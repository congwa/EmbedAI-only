"""
用户认证API测试用例
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from main import app
from api.models.user_model import User
from api.utils.auth_utils import AuthUtils


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
    user.password_hash = AuthUtils.hash_password("testpassword")
    user.role = "user"
    user.to_dict.return_value = {
        "id": 1,
        "username": "testuser", 
        "role": "user",
        "created_at": "2024-01-01T00:00:00",
        "last_login": None
    }
    return user


@pytest.fixture
def mock_admin_user():
    """模拟管理员用户"""
    user = Mock(spec=User)
    user.id = 2
    user.username = "admin"
    user.password_hash = AuthUtils.hash_password("adminpass")
    user.role = "admin"
    user.to_dict.return_value = {
        "id": 2,
        "username": "admin",
        "role": "admin", 
        "created_at": "2024-01-01T00:00:00",
        "last_login": "2024-01-02T10:00:00"
    }
    return user


class TestAuthLogin:
    """登录认证测试"""
    
    def test_login_success(self, client, mock_db_session, mock_user):
        """测试登录成功"""
        # 模拟数据库查询
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # 发送登录请求
        response = client.post("/api/auth/token", data={
            "username": "testuser",
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"
        assert data["role"] == "user"
    
    def test_login_invalid_username(self, client, mock_db_session):
        """测试无效用户名登录"""
        # 模拟用户不存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        response = client.post("/api/auth/token", data={
            "username": "nonexistent", 
            "password": "testpassword"
        })
        
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]
    
    def test_login_invalid_password(self, client, mock_db_session, mock_user):
        """测试无效密码登录"""
        # 模拟用户存在但密码错误
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        response = client.post("/api/auth/token", data={
            "username": "testuser",
            "password": "wrongpassword"  
        })
        
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]


class TestAuthInitialization:
    """系统初始化测试"""
    
    @patch("api.db_manager.db_manager.check_first_run")
    def test_check_first_run_true(self, mock_check, client):
        """测试首次运行检查 - 是首次运行"""
        mock_check.return_value = True
        
        response = client.get("/api/auth/check-first-run")
        assert response.status_code == 200
        assert response.json()["first_run"] is True
    
    @patch("api.db_manager.db_manager.check_first_run")  
    def test_check_first_run_false(self, mock_check, client):
        """测试首次运行检查 - 非首次运行"""
        mock_check.return_value = False
        
        response = client.get("/api/auth/check-first-run")
        assert response.status_code == 200
        assert response.json()["first_run"] is False
    
    @patch("api.db_manager.db_manager.check_first_run")
    def test_initialize_admin_success(self, mock_check, client, mock_db_session):
        """测试初始化管理员成功"""
        mock_check.return_value = True
        
        # 模拟数据库操作
        mock_admin = Mock()
        mock_admin.id = 1
        mock_admin.username = "admin"
        mock_admin.role = "superadmin"
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        with patch("api.routes.auth_router.User", return_value=mock_admin):
            response = client.post("/api/auth/initialize", json={
                "username": "admin",
                "password": "adminpass123"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "admin"
        assert data["role"] == "superadmin"
    
    @patch("api.db_manager.db_manager.check_first_run")
    def test_initialize_admin_not_first_run(self, mock_check, client):
        """测试非首次运行时无法初始化管理员"""
        mock_check.return_value = False
        
        response = client.post("/api/auth/initialize", json={
            "username": "admin", 
            "password": "adminpass123"
        })
        
        assert response.status_code == 403
        assert "系统已经初始化" in response.json()["detail"]


class TestUserManagement:
    """用户管理测试"""
    
    @patch("api.utils.auth_middleware.get_current_user")
    def test_get_current_user_info(self, mock_get_user, client, mock_user):
        """测试获取当前用户信息"""
        mock_get_user.return_value = mock_user
        
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["role"] == "user"
    
    @patch("api.utils.auth_middleware.get_admin_user")
    def test_create_user_success(self, mock_get_admin, client, mock_db_session, mock_admin_user):
        """测试管理员创建用户成功"""
        mock_get_admin.return_value = mock_admin_user
        
        # 模拟用户不存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # 模拟创建新用户
        mock_new_user = Mock()
        mock_new_user.to_dict.return_value = {
            "id": 3,
            "username": "newuser",
            "role": "user",
            "created_at": "2024-01-03T00:00:00",
            "last_login": None
        }
        
        with patch("api.routes.auth_router.User", return_value=mock_new_user):
            response = client.post("/api/auth/users", json={
                "username": "newuser",
                "password": "newpass123",
                "role": "user"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "user"
    
    @patch("api.utils.auth_middleware.get_admin_user")
    def test_create_user_duplicate_username(self, mock_get_admin, client, mock_db_session, mock_admin_user, mock_user):
        """测试创建重复用户名的用户"""
        mock_get_admin.return_value = mock_admin_user
        
        # 模拟用户已存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        response = client.post("/api/auth/users", json={
            "username": "testuser",  # 已存在的用户名
            "password": "newpass123",
            "role": "user" 
        })
        
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]
    
    @patch("api.utils.auth_middleware.get_admin_user") 
    def test_get_users_list(self, mock_get_admin, client, mock_db_session, mock_admin_user):
        """测试获取用户列表"""
        mock_get_admin.return_value = mock_admin_user
        
        # 模拟用户列表
        mock_users = [Mock(), Mock()]
        for i, user in enumerate(mock_users):
            user.to_dict.return_value = {
                "id": i + 1,
                "username": f"user{i + 1}",
                "role": "user",
                "created_at": "2024-01-01T00:00:00",
                "last_login": None
            }
        
        mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_users
        
        response = client.get("/api/auth/users")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "user1"
    
    @patch("api.utils.auth_middleware.get_admin_user")
    def test_delete_user_success(self, mock_get_admin, client, mock_db_session, mock_admin_user, mock_user):
        """测试删除用户成功"""
        mock_get_admin.return_value = mock_admin_user
        
        # 模拟找到要删除的用户
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        response = client.delete("/api/auth/users/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "用户已删除" in data["message"]
    
    @patch("api.utils.auth_middleware.get_admin_user")
    def test_delete_user_not_found(self, mock_get_admin, client, mock_db_session, mock_admin_user):
        """测试删除不存在的用户"""
        mock_get_admin.return_value = mock_admin_user
        
        # 模拟用户不存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        response = client.delete("/api/auth/users/999")
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
