"""
知识库管理API测试用例
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from main import app
from api.models.user_model import User
from api.models.kb_models import KnowledgeDatabase, KnowledgeFile, KnowledgeNode


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    with patch("api.utils.auth_middleware.get_db") as mock_get_db:
        mock_session = Mock(spec=Session)
        mock_get_db.return_value = mock_session
        yield mock_session


@pytest.fixture
def mock_user():
    """模拟用户对象"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.role = "user"
    return user


@pytest.fixture
def mock_knowledge_db():
    """模拟知识库对象"""
    kb = Mock(spec=KnowledgeDatabase)
    kb.id = 1
    kb.db_id = "kb_12345678"
    kb.name = "测试知识库"
    kb.description = "这是一个测试知识库"
    kb.embed_model = "text-embedding-ada-002"
    kb.dimension = 1536
    kb.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    return kb


@pytest.fixture
def mock_knowledge_file():
    """模拟知识库文件对象"""
    file = Mock(spec=KnowledgeFile)
    file.file_id = "file_12345"
    file.database_id = "kb_12345678"
    file.filename = "test_doc.txt"
    file.file_type = "text/plain"
    file.status = "completed"
    file.created_at.isoformat.return_value = "2024-01-01T10:00:00"
    file.nodes = []
    return file


class TestKnowledgeDatabaseManagement:
    """知识库数据库管理测试"""
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_databases_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试获取知识库列表成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟数据库查询返回结果
        mock_db_session.query.return_value.outerjoin.return_value.group_by.return_value.all.return_value = [
            (mock_knowledge_db, 3)  # (database, file_count)
        ]
        
        response = client.get("/api/knowledge/databases")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["db_id"] == "kb_12345678"
        assert data[0]["name"] == "测试知识库"
        assert data[0]["file_count"] == 3
    
    @patch("api.utils.auth_middleware.get_current_user")
    @patch("knowledge.knowledge_base.create_knowledge_base")
    def test_create_database_success(self, mock_create_kb, mock_get_user, client, mock_db_session, mock_user):
        """测试创建知识库成功"""
        mock_get_user.return_value = mock_user
        mock_create_kb.return_value = AsyncMock()
        
        # 模拟数据库操作
        mock_new_db = Mock()
        mock_new_db.id = 1
        mock_new_db.db_id = "kb_87654321"
        mock_new_db.name = "新知识库"
        
        with patch("api.routes.knowledge_router.KnowledgeDatabase", return_value=mock_new_db):
            with patch("uuid.uuid4") as mock_uuid:
                mock_uuid.return_value.hex = "87654321abcdef12"
                
                response = client.post("/api/knowledge/databases", json={
                    "name": "新知识库",
                    "description": "新建的测试知识库",
                    "embed_model": "text-embedding-ada-002",
                    "dimension": 1536
                })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "新知识库"
        assert "kb_" in data["data"]["db_id"]
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_database_info_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db, mock_knowledge_file):
        """测试获取知识库详情成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟数据库查询
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_knowledge_file]
        
        response = client.get("/api/knowledge/databases/kb_12345678")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["database"]["db_id"] == "kb_12345678"
        assert len(data["data"]["files"]) == 1
        assert data["data"]["files"][0]["filename"] == "test_doc.txt"
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_database_info_not_found(self, mock_get_user, client, mock_db_session, mock_user):
        """测试获取不存在的知识库详情"""
        mock_get_user.return_value = mock_user
        
        # 模拟知识库不存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        response = client.get("/api/knowledge/databases/nonexistent")
        assert response.status_code == 404
        assert "知识库不存在" in response.json()["detail"]
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_update_database_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试更新知识库成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟找到知识库
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        response = client.put("/api/knowledge/databases/kb_12345678", json={
            "name": "更新后的知识库",
            "description": "更新后的描述"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "更新成功" in data["message"]
    
    @patch("api.utils.auth_middleware.get_current_user")
    @patch("knowledge.knowledge_base.delete_knowledge_base")
    def test_delete_database_success(self, mock_delete_kb, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试删除知识库成功"""
        mock_get_user.return_value = mock_user
        mock_delete_kb.return_value = AsyncMock()
        
        # 模拟找到知识库
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        response = client.delete("/api/knowledge/databases/kb_12345678")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]


class TestDocumentManagement:
    """文档管理测试"""
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_add_documents_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试添加文档成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟知识库存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "doc12345678"
            
            response = client.post("/api/knowledge/databases/kb_12345678/documents", json={
                "items": [
                    {
                        "filename": "document1.txt",
                        "path": "/path/to/doc1.txt",
                        "type": "text"
                    },
                    {
                        "filename": "document2.pdf", 
                        "path": "/path/to/doc2.pdf",
                        "type": "pdf"
                    }
                ],
                "params": {}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "成功添加" in data["message"]
        assert len(data["data"]["added_documents"]) > 0
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_document_info_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_file):
        """测试获取文档信息成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟找到文档
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_file
        
        response = client.get("/api/knowledge/databases/kb_12345678/documents/file_12345")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["filename"] == "test_doc.txt"
        assert data["data"]["status"] == "completed"
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_delete_document_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_file):
        """测试删除文档成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟找到文档
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_file
        
        response = client.delete("/api/knowledge/databases/kb_12345678/documents/file_12345")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]


class TestKnowledgeQuery:
    """知识库查询测试"""
    
    @patch("api.utils.auth_middleware.get_current_user")
    @patch("knowledge.knowledge_base.query_knowledge_base")
    def test_query_knowledge_base_success(self, mock_query_kb, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试查询知识库成功"""
        mock_get_user.return_value = mock_user
        mock_query_kb.return_value = AsyncMock(return_value={
            "results": [
                {
                    "content": "这是搜索结果1",
                    "score": 0.95
                },
                {
                    "content": "这是搜索结果2", 
                    "score": 0.88
                }
            ],
            "total": 2
        })
        
        # 模拟知识库存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        response = client.post("/api/knowledge/databases/kb_12345678/query", json={
            "query": "什么是人工智能？",
            "meta": {
                "top_k": 5,
                "score_threshold": 0.7
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data["data"]
    
    @patch("api.utils.auth_middleware.get_current_user")
    @patch("knowledge.knowledge_base.test_query_knowledge_base")
    def test_query_test_success(self, mock_test_query, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试查询测试成功"""
        mock_get_user.return_value = mock_user
        mock_test_query.return_value = AsyncMock(return_value={
            "results": [],
            "debug_info": "测试查询执行成功"
        })
        
        # 模拟知识库存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        response = client.post("/api/knowledge/databases/kb_12345678/query-test", json={
            "query": "测试查询",
            "meta": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_query_params_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试获取查询参数成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟知识库存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        response = client.get("/api/knowledge/databases/kb_12345678/query-params")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "top_k" in data["data"]
        assert "embed_model" in data["data"]


class TestFileUpload:
    """文件上传测试"""
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_upload_file_success(self, mock_get_user, client, mock_db_session, mock_user, mock_knowledge_db):
        """测试文件上传成功"""
        mock_get_user.return_value = mock_user
        
        # 模拟知识库存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_knowledge_db
        
        # 创建测试文件
        test_file_content = b"This is test content"
        
        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "file123456"
            
            response = client.post(
                "/api/knowledge/files/upload?db_id=kb_12345678",
                files={"file": ("test.txt", test_file_content, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "上传成功" in data["message"]
        assert data["data"]["filename"] == "test.txt"
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_upload_file_no_filename(self, mock_get_user, client, mock_user):
        """测试文件上传无文件名"""
        mock_get_user.return_value = mock_user
        
        response = client.post(
            "/api/knowledge/files/upload",
            files={"file": ("", b"content", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "文件名不能为空" in response.json()["detail"]


class TestKnowledgeStats:
    """知识库统计测试"""
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_knowledge_base_types(self, mock_get_user, client, mock_user):
        """测试获取知识库类型"""
        mock_get_user.return_value = mock_user
        
        response = client.get("/api/knowledge/types")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        
        # 检查返回的类型包含向量和图谱
        type_names = [t["type"] for t in data["data"]]
        assert "vector" in type_names
        assert "graph" in type_names
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_statistics(self, mock_get_user, client, mock_db_session, mock_user):
        """测试获取统计信息"""
        mock_get_user.return_value = mock_user
        
        # 模拟统计查询
        mock_db_session.query.return_value.count.return_value = 5  # 数据库数量
        mock_db_session.query.return_value.group_by.return_value.all.return_value = [
            ("completed", 10),
            ("processing", 2),
            ("failed", 1)
        ]
        
        response = client.get("/api/knowledge/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "databases" in data["data"]
        assert "files" in data["data"]
        assert "nodes" in data["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
