"""
健康检查API测试
"""
import pytest
from fastapi.testclient import TestClient

# 标记所有测试为API测试
pytestmark = pytest.mark.integration


class TestHealthAPI:
    """测试健康检查API"""

    def test_health_check(self, client: TestClient):
        """测试健康检查接口"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        
        # 验证返回的数据结构
        assert "status" in data
        assert "checks" in data
        assert "timestamp" in data
        assert "version" in data
        
        # 验证状态
        assert data["status"] == "healthy"
        assert "api" in data["checks"]
        assert data["checks"]["api"] == "ok"
        
    def test_readiness_check(self, client: TestClient):
        """测试就绪检查接口"""
        response = client.get("/api/ready")
        assert response.status_code == 200
        data = response.json()
        
        # 验证返回的数据结构
        assert "status" in data
        assert "timestamp" in data
        
        # 验证状态
        assert data["status"] == "ready"
        
    def test_liveness_check(self, client: TestClient):
        """测试存活检查接口"""
        response = client.get("/api/live")
        assert response.status_code == 200
        data = response.json()
        
        # 验证返回的数据结构
        assert "status" in data
        assert "timestamp" in data
        
        # 验证状态
        assert data["status"] == "alive"
