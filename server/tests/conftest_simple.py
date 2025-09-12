"""
简化的测试配置文件
专注于基本的测试功能，避免复杂的依赖问题
"""
import os
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# 设置测试环境变量
os.environ["TESTING"] = "1"


@pytest.fixture
def app():
    """创建简单的测试应用"""
    app = FastAPI(title="EmbedAI Test API")
    
    # 添加基本路由用于测试
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    db = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    db.query = Mock()
    db.add = Mock()
    db.delete = Mock()
    db.merge = Mock()
    return db


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


# 数据库连接测试夹具（仅在数据库可用时使用）
@pytest.fixture
def milvus_connection():
    """Milvus连接测试夹具"""
    try:
        from pymilvus import connections
        connections.connect(
            alias="test_connection",
            host="localhost", 
            port=10103
        )
        yield connections
        connections.disconnect("test_connection")
    except Exception as e:
        pytest.skip(f"Milvus不可用: {e}")


@pytest.fixture
def neo4j_driver():
    """Neo4j连接测试夹具"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            "bolt://localhost:10105",
            auth=("neo4j", "embedai123")
        )
        with driver.session() as session:
            session.run("RETURN 1")
        yield driver
        driver.close()
    except Exception as e:
        pytest.skip(f"Neo4j不可用: {e}")


@pytest.fixture  
def minio_client():
    """MinIO连接测试夹具"""
    try:
        from minio import Minio
        client = Minio(
            "localhost:10106",
            access_key="minioadmin",
            secret_key="minioadmin123", 
            secure=False
        )
        client.list_buckets()
        yield client
    except Exception as e:
        pytest.skip(f"MinIO不可用: {e}")
