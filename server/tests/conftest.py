"""
测试配置文件
配置测试夹具和环境设置
"""
import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
# 数据库导入（仅在需要时导入以避免依赖问题）
try:
    from pymilvus import connections, utility
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    from minio import Minio
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

# 设置测试环境变量
os.environ["TESTING"] = "1"
os.environ["MILVUS_PORT"] = "10103"
os.environ["NEO4J_URI"] = "bolt://localhost:10105"
os.environ["NEO4J_PASSWORD"] = "embedai123"
os.environ["MINIO_ENDPOINT"] = "localhost:10106"
os.environ["MINIO_SECRET_KEY"] = "minioadmin123"

# 延迟导入以避免循环依赖
def create_test_app():
    """创建测试应用"""
    from fastapi import FastAPI
    app = FastAPI(title="EmbedAI Test API")
    return app


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_db() -> Generator[Mock, None, None]:
    """模拟数据库会话"""
    db = Mock(spec=Session)
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    db.query = Mock()
    db.add = Mock()
    db.delete = Mock()
    db.merge = Mock()
    yield db


@pytest.fixture
def mock_user():
    """创建模拟用户"""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_admin = False
    user.is_active = True
    return user


@pytest.fixture
def mock_admin_user():
    """创建模拟管理员用户"""
    user = Mock()
    user.id = 1
    user.username = "admin"
    user.email = "admin@example.com"
    user.is_admin = True
    user.is_active = True
    return user


@pytest.fixture
def override_get_db(mock_db):
    """重写数据库依赖"""
    def _override_get_db():
        return mock_db
    return _override_get_db


@pytest.fixture
def override_get_current_user(mock_user):
    """重写当前用户依赖"""
    def _override_get_current_user():
        return mock_user
    return _override_get_current_user


@pytest.fixture
def override_get_admin_user(mock_admin_user):
    """重写管理员用户依赖"""
    def _override_get_admin_user():
        return mock_admin_user
    return _override_get_admin_user


# =============================================================================
# === 真实数据库连接测试夹具 ===
# =============================================================================

@pytest.fixture(scope="session")
def real_milvus_connection():
    """真实Milvus连接"""
    try:
        connections.connect(
            alias="default",
            host="localhost",
            port=10103
        )
        yield connections
        connections.disconnect("default")
    except Exception as e:
        pytest.skip(f"无法连接到Milvus: {e}")


@pytest.fixture(scope="session") 
def real_neo4j_driver():
    """真实Neo4j连接"""
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:10105",
            auth=("neo4j", "embedai123")
        )
        # 测试连接
        with driver.session() as session:
            session.run("RETURN 1")
        yield driver
        driver.close()
    except Exception as e:
        pytest.skip(f"无法连接到Neo4j: {e}")


@pytest.fixture(scope="session")
def real_minio_client():
    """真实MinIO连接"""
    try:
        client = Minio(
            "localhost:10106",
            access_key="minioadmin",
            secret_key="minioadmin123",
            secure=False
        )
        # 测试连接
        client.list_buckets()
        yield client
    except Exception as e:
        pytest.skip(f"无法连接到MinIO: {e}")


# =============================================================================
# === 集成测试夹具 ===
# =============================================================================

@pytest.fixture
def integration_client(real_milvus_connection, real_neo4j_driver, real_minio_client):
    """集成测试客户端 - 使用真实数据库"""
    
    # 创建测试数据库引擎
    engine = create_engine("sqlite:///./test_embedai.db", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 清理
    app.dependency_overrides.clear()
    if os.path.exists("./test_embedai.db"):
        os.remove("./test_embedai.db")


@pytest.fixture
def test_knowledge_data():
    """测试知识库数据"""
    return {
        "databases": [
            {
                "name": "test_kb",
                "description": "测试知识库",
                "type": "lightrag"
            }
        ],
        "documents": [
            {
                "title": "测试文档1",
                "content": "这是一个测试文档的内容",
                "metadata": {"category": "test"}
            }
        ]
    }


@pytest.fixture
def test_graph_data():
    """测试图谱数据"""
    return {
        "nodes": [
            {"id": "node1", "label": "Product", "properties": {"name": "iPhone"}},
            {"id": "node2", "label": "Category", "properties": {"name": "手机"}}
        ],
        "relationships": [
            {"from": "node1", "to": "node2", "type": "BELONGS_TO"}
        ]
    }


# =============================================================================
# === Mock装饰器 ===
# =============================================================================

def mock_knowledge_base():
    """Mock knowledge_base模块"""
    return patch.multiple(
        'knowledge.knowledge_base',
        create_database=Mock(return_value={"success": True, "id": "test_db_id"}),
        get_databases=Mock(return_value=[{"id": "1", "name": "test_kb"}]),
        add_document=Mock(return_value={"success": True}),
        query_database=Mock(return_value={"success": True, "results": []}),
        delete_database=Mock(return_value={"success": True})
    )


def mock_graph_base():
    """Mock graph_base模块"""
    return patch.multiple(
        'knowledge.graph_base',
        get_subgraph=Mock(return_value={"nodes": [], "edges": []}),
        get_databases=Mock(return_value=["test_graph_db"]),
        query_nodes=Mock(return_value=[]),
        add_entities=Mock(return_value={"success": True})
    )


# =============================================================================
# === 测试数据清理 ===
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """测试后自动清理数据"""
    yield
    
    # 清理测试创建的文件
    test_files = [
        "./test_embedai.db",
        "./test_data/",
        "./logs/test_*.log"
    ]
    
    for file_pattern in test_files:
        import glob
        for file_path in glob.glob(file_pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
            except Exception:
                pass


# =============================================================================
# === 测试标记 ===
# =============================================================================

# 定义测试标记
pytest_markers = [
    "unit: 单元测试",
    "integration: 集成测试", 
    "slow: 慢速测试",
    "database: 需要数据库的测试",
    "auth: 认证相关测试",
    "knowledge: 知识库相关测试",
    "graph: 图谱相关测试"
]
