"""
API接口测试用例
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app
from schemas.requests import ChatRecommendationRequest, ProductFilter
from schemas.responses import ChatRecommendationResponse


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_kb_service():
    """模拟知识库服务"""
    with patch("main.app_state") as mock_state:
        mock_service = Mock()
        mock_state.__getitem__.return_value = mock_service
        yield mock_service


class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check_success(self, client):
        """测试健康检查成功"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "checks" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_readiness_check(self, client):
        """测试就绪检查"""
        response = client.get("/api/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data
    
    def test_liveness_check(self, client):
        """测试存活检查"""
        response = client.get("/api/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data


class TestChatAPI:
    """聊天推荐API测试"""
    
    def test_chat_recommendations_success(self, client, mock_kb_service):
        """测试聊天推荐成功"""
        # 模拟服务响应
        mock_response = ChatRecommendationResponse(
            reply="为您推荐以下商品：",
            products=[],
            evidence=[],
            trace_id="test_trace_id",
            session_id="test_session",
            timestamp=1234567890
        )
        mock_kb_service.chat_recommendation.return_value = mock_response
        
        # 发送请求
        request_data = {
            "sessionId": "test_session",
            "message": "推荐一款手机",
            "history": [],
            "topK": 5,
            "lang": "zh-CN"
        }
        
        response = client.post("/api/chat/recommendations", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["reply"] == "为您推荐以下商品："
        assert data["trace_id"] == "test_trace_id"
        assert data["session_id"] == "test_session"
    
    def test_chat_recommendations_with_filters(self, client, mock_kb_service):
        """测试带筛选条件的聊天推荐"""
        mock_response = ChatRecommendationResponse(
            reply="找到符合条件的商品：",
            products=[],
            evidence=[],
            trace_id="test_trace_id_2",
            session_id="test_session_2",
            timestamp=1234567890
        )
        mock_kb_service.chat_recommendation.return_value = mock_response
        
        request_data = {
            "sessionId": "test_session_2",
            "message": "推荐iPhone",
            "history": [
                {"role": "user", "content": "我想买手机"},
                {"role": "assistant", "content": "您有什么要求吗？"}
            ],
            "filters": {
                "price": [1000, 8000],
                "brand": ["Apple", "华为"],
                "tags": ["5G", "拍照"]
            },
            "topK": 10,
            "lang": "zh-CN"
        }
        
        response = client.post("/api/chat/recommendations", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["reply"] == "找到符合条件的商品："
    
    def test_chat_recommendations_validation_error(self, client):
        """测试请求参数验证错误"""
        # 缺少必需参数
        request_data = {
            "sessionId": "test_session",
            "message": "推荐商品"
        }
        
        response = client.post("/api/chat/recommendations", json=request_data)
        assert response.status_code == 422
    
    def test_chat_recommendations_invalid_top_k(self, client):
        """测试无效的topK参数"""
        request_data = {
            "sessionId": "test_session",
            "message": "推荐商品",
            "topK": 100  # 超出最大值
        }
        
        response = client.post("/api/chat/recommendations", json=request_data)
        assert response.status_code == 422
    
    def test_get_session_history(self, client):
        """测试获取会话历史"""
        response = client.get(
            "/api/chat/sessions/test_session/history?limit=10"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test_session"
        assert "history" in data
        assert "total" in data
    
    def test_clear_session(self, client):
        """测试清空会话"""
        response = client.delete(
            "/api/chat/sessions/test_session"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data


class TestAdminAPI:
    """管理后台API测试"""
    
    def test_list_databases(self, client, mock_kb_service):
        """测试获取数据库列表"""
        mock_kb_service.list_databases.return_value = [
            {
                "id": "test_db_1",
                "name": "测试数据库1",
                "status": "active",
                "created_at": 1234567890,
                "updated_at": 1234567890
            }
        ]
        
        response = client.get("/api/admin/kb/databases")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["databases"]) == 1
        assert data["total"] == 1
    
    def test_create_database(self, client, mock_kb_service):
        """测试创建数据库"""
        mock_kb_service.get_or_create_default_db.return_value = "new_db_id"
        
        request_data = {
            "name": "新数据库",
            "description": "测试数据库",
            "embeddingModel": "BAAI/bge-m3"
        }
        
        response = client.post("/api/admin/kb/databases", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "database_id" in data["data"]
    
    def test_get_database_detail(self, client, mock_kb_service):
        """测试获取数据库详情"""
        mock_kb_service.get_database_info.return_value = {
            "name": "测试数据库",
            "status": "active",
            "file_count": 5,
            "chunk_count": 100
        }
        
        response = client.get("/api/admin/kb/databases/test_db")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["database"]["id"] == "test_db"
        assert data["database"]["status"] == "active"
    
    def test_upload_file(self, client):
        """测试文件上传"""
        # 创建测试文件
        test_file = ("test.csv", b"sku,title,price\nA001,test_product,99.0", "text/csv")
        
        response = client.post(
            "/api/admin/kb/upload?database_id=test_db",
            files={"file": test_file}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "file_id" in data
    
    def test_build_index(self, client):
        """测试构建索引"""
        request_data = {
            "databaseId": "test_db",
            "forceRebuild": False
        }
        
        response = client.post("/api/admin/kb/index", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data
    
    def test_get_analytics(self, client):
        """测试获取分析数据"""
        response = client.get("/api/admin/analytics/conversations")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data


class TestRootAPI:
    """根路径API测试"""
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
