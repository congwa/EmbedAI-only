"""
数据库操作相关的API集成测试
"""
import pytest
import uuid
from fastapi.testclient import TestClient

# 标记所有测试为数据库测试
pytestmark = pytest.mark.database

# 生成唯一用户名后缀
def unique_suffix():
    return uuid.uuid4().hex[:8]


class TestAuthDBOperations:
    """测试认证相关的数据库操作"""

    def test_first_run_check(self, db_client: TestClient):
        """测试首次运行检查"""
        # 检查系统是否处于首次运行状态
        response = db_client.get("/api/auth/check-first-run")
        assert response.status_code == 200
        # 注意：由于每个测试用例都会创建新的数据库，所以这里总是首次运行
        assert response.json() == {"first_run": True}
        
    def test_initialize_admin(self, db_client: TestClient):
        """测试初始化管理员账户"""
        # 1. 初始化管理员
        username = f"admin_init_{unique_suffix()}"
        admin_data = {"username": username, "password": "superpassword"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["username"] == username
        assert token_data["role"] == "superadmin"

        # 2. 尝试再次初始化，应该失败
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 403

    def test_admin_login(self, db_client: TestClient):
        """测试管理员登录"""
        # 1. 初始化管理员
        username = f"admin_login_{unique_suffix()}"
        admin_data = {"username": username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        
        # 2. 使用管理员账户登录
        login_data = {"username": username, "password": "adminpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        login_token_data = response.json()
        assert "access_token" in login_token_data
        assert login_token_data["username"] == username

    def test_create_user(self, db_client: TestClient):
        """测试管理员创建新用户"""
        # 1. 初始化管理员
        admin_data = {"username": "admin_creator", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 使用管理员权限创建新用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_user_data = {
            "username": "testuser", 
            "password": "testpass", 
            "role": "user"
        }
        response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "testuser"
        assert user_data["role"] == "user"
        assert "id" in user_data
        
        # 3. 验证新用户可以登录
        login_data = {"username": "testuser", "password": "testpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["username"] == "testuser"
        
    def test_get_users(self, db_client: TestClient):
        """测试获取用户列表"""
        # 1. 初始化管理员
        admin_data = {"username": "admin_list", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 创建多个测试用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        for i in range(3):
            new_user_data = {
                "username": f"testuser{i}", 
                "password": "testpass", 
                "role": "user"
            }
            response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
            assert response.status_code == 200
        
        # 3. 获取用户列表
        response = db_client.get("/api/auth/users", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 3  # 至少应该有我们创建的三个用户
        
        # 4. 验证用户列表中包含我们创建的用户
        usernames = [user["username"] for user in users]
        for i in range(3):
            assert f"testuser{i}" in usernames
            
    def test_get_user_by_id(self, db_client: TestClient):
        """测试根据ID获取特定用户"""
        # 1. 初始化管理员
        admin_data = {"username": "admin_getuser", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 创建测试用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_user_data = {
            "username": "specific_user", 
            "password": "testpass", 
            "role": "user"
        }
        response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        user_id = user_data["id"]
        
        # 3. 根据ID获取用户
        response = db_client.get(f"/api/auth/users/{user_id}", headers=headers)
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["username"] == "specific_user"
        assert retrieved_user["role"] == "user"
        
        # 4. 测试获取不存在的用户
        response = db_client.get("/api/auth/users/9999", headers=headers)
        assert response.status_code == 404
        
    def test_update_user(self, db_client: TestClient):
        """测试更新用户信息"""
        # 1. 初始化管理员
        admin_data = {"username": "admin_update", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 创建测试用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_user_data = {
            "username": "update_user", 
            "password": "oldpass", 
            "role": "user"
        }
        response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        user_id = user_data["id"]
        
        # 3. 更新用户信息
        update_data = {
            "username": "updated_user",
            "password": "newpass"
        }
        response = db_client.put(f"/api/auth/users/{user_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["username"] == "updated_user"
        
        # 4. 验证更新后的用户信息
        response = db_client.get(f"/api/auth/users/{user_id}", headers=headers)
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["username"] == "updated_user"
        
        # 5. 验证新密码可以登录
        login_data = {"username": "updated_user", "password": "newpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        # 6. 验证旧密码无法登录
        login_data = {"username": "updated_user", "password": "oldpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 401
        
    def test_delete_user(self, db_client: TestClient):
        """测试删除用户"""
        # 1. 初始化管理员
        admin_data = {"username": "admin_delete", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 创建测试用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_user_data = {
            "username": "delete_user", 
            "password": "testpass", 
            "role": "user"
        }
        response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        user_id = user_data["id"]
        
        # 3. 删除用户
        response = db_client.delete(f"/api/auth/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # 4. 验证用户已被删除
        response = db_client.get(f"/api/auth/users/{user_id}", headers=headers)
        assert response.status_code == 404
        
        # 5. 验证已删除用户无法登录
        login_data = {"username": "delete_user", "password": "testpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 401
        
    def test_cannot_delete_self(self, db_client: TestClient):
        """测试管理员不能删除自己的账户"""
        # 1. 初始化管理员
        admin_data = {"username": "admin_self", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_id = response.json()["user_id"]
        
        # 2. 尝试删除自己
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = db_client.delete(f"/api/auth/users/{admin_id}", headers=headers)
        assert response.status_code == 400  # 应该返回错误
        
    def test_cannot_delete_last_superadmin(self, db_client: TestClient):
        """测试不能删除最后一个超级管理员"""
        # 1. 初始化超级管理员
        admin_data = {"username": "super_admin", "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_id = response.json()["user_id"]
        
        # 2. 创建普通管理员
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_admin_data = {
            "username": "normal_admin", 
            "password": "adminpass", 
            "role": "admin"
        }
        response = db_client.post("/api/auth/users", json=new_admin_data, headers=headers)
        assert response.status_code == 200
        normal_admin_id = response.json()["id"]
        
        # 3. 使用普通管理员登录
        login_data = {"username": "normal_admin", "password": "adminpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        normal_admin_token = response.json()["access_token"]
        
        # 4. 尝试使用普通管理员删除超级管理员
        headers = {"Authorization": f"Bearer {normal_admin_token}"}
        response = db_client.delete(f"/api/auth/users/{admin_id}", headers=headers)
        assert response.status_code == 403  # 应该返回权限不足错误
