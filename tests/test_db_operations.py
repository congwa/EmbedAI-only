"""
数据库操作相关的API集成测试
"""
import pytest
from fastapi.testclient import TestClient

# 标记所有测试为数据库测试
pytestmark = pytest.mark.database


class TestAuthDBOperations:
    """测试认证相关的数据库操作"""

    def test_check_first_run(self, db_client: TestClient):
        """测试系统在初始状态下是否被正确识别为首次运行"""
        response = db_client.get("/api/auth/check-first-run")
        assert response.status_code == 200
        assert response.json() == {"first_run": True}

    def test_initialize_admin_and_login(self, db_client: TestClient):
        """测试初始化管理员账户，然后使用该账户登录"""
        # 1. 初始化管理员
        admin_data = {"username": "superadmin", "password": "superpassword"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["username"] == "superadmin"
        assert token_data["role"] == "superadmin"

        # 2. 检查首次运行状态是否变为False
        response = db_client.get("/api/auth/check-first-run")
        assert response.status_code == 200
        assert response.json() == {"first_run": False}

        # 3. 尝试再次初始化，应该失败
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 403

        # 4. 使用新创建的管理员账户登录
        login_data = {"username": "superadmin", "password": "superpassword"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        login_token_data = response.json()
        assert "access_token" in login_token_data
        assert login_token_data["username"] == "superadmin"
