"""
管理后台API测试
"""
import pytest
import uuid
import random
import string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 标记所有测试为数据库测试
pytestmark = pytest.mark.database

# 生成唯一用户名后缀
def unique_suffix():
    return uuid.uuid4().hex[:8]
    
# 生成完全随机的用户名
def random_username(prefix="user"):
    random_str = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    return f"{prefix}_{random_str}_{unique_suffix()}"


class TestAdminAPI:
    """测试管理后台API"""

    def test_get_users(self, db_client: TestClient):
        """测试获取用户列表接口"""
        # 1. 初始化管理员
        admin_username = random_username("admin_list")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 创建多个测试用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        created_usernames = []
        for i in range(3):
            username = random_username(f"testuser_{i}")
            created_usernames.append(username)
            new_user_data = {
                "username": username, 
                "password": "testpass", 
                "role": "user"
            }
            response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
            assert response.status_code == 200
        
        # 3. 使用管理员API获取用户列表
        response = db_client.get("/api/admin/users", headers=headers)
        assert response.status_code == 200
        users = response.json()
        
        # 4. 验证返回的数据
        assert isinstance(users, list)
        assert len(users) >= 4  # 至少应该有管理员和3个创建的用户
        
        # 5. 验证用户列表中包含我们创建的用户
        usernames = [user["username"] for user in users]
        for username in created_usernames:
            assert username in usernames
        
        # 6. 验证用户数据结构
        for user in users:
            assert "id" in user
            assert "username" in user
            assert "role" in user
            assert "created_at" in user

    def test_get_users_pagination(self, db_client: TestClient):
        """测试获取用户列表接口的分页功能"""
        # 1. 初始化管理员并创建多个用户
        admin_username = random_username("admin_pagination")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        for i in range(5):
            new_user_data = {"username": random_username(f"page_user_{i}"), "password": "testpass", "role": "user"}
            db_client.post("/api/auth/users", json=new_user_data, headers=headers)

        # 2. 测试分页参数 limit
        response = db_client.get("/api/admin/users?limit=2", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

        # 3. 测试分页参数 skip 和 limit
        response = db_client.get("/api/admin/users?skip=1&limit=3", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 3

    def test_get_system_stats(self, db_client: TestClient):
        """测试获取系统统计信息接口"""
        # 1. 初始化管理员
        admin_username = random_username("admin_stats")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        
        # 2. 创建测试用户
        headers = {"Authorization": f"Bearer {admin_token}"}
        for i in range(2):
            username = random_username(f"testuser_{i}")
            new_user_data = {
                "username": username, 
                "password": "testpass", 
                "role": "user"
            }
            response = db_client.post("/api/auth/users", json=new_user_data, headers=headers)
            assert response.status_code == 200
        
        # 3. 获取系统统计信息
        response = db_client.get("/api/admin/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()
        
        # 4. 验证返回的数据结构
        assert "success" in stats
        assert stats["success"] == True
        assert "data" in stats
        
        data = stats["data"]
        assert "users" in data
        assert "databases" in data
        assert "activity" in data
        
        # 5. 验证用户统计数据
        users_stats = data["users"]
        assert users_stats["total"] >= 3  # 至少有1个管理员和2个普通用户
        assert users_stats["admins"] >= 1  # 至少有1个管理员
        assert users_stats["regular"] >= 2  # 至少有2个普通用户
        
    def test_create_and_delete_database(self, db_client: TestClient):
        """测试创建和删除知识库数据库接口"""
        # 1. 初始化管理员
        admin_username = random_username("admin_db")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 2. 创建数据库
        db_name = f"test_db_{unique_suffix()}"
        db_data = {
            "name": db_name,
            "description": "测试数据库",
            "embed_model": "test-embedding-model"
        }
        response = db_client.post("/api/admin/databases", json=db_data, headers=headers)
        assert response.status_code == 200
        result = response.json()
        
        # 3. 验证创建结果
        assert "success" in result
        assert result["success"] == True
        assert "data" in result
        assert "db_id" in result["data"]
        db_id = result["data"]["db_id"]
        
        # 4. 获取数据库列表，验证新创建的数据库存在
        response = db_client.get("/api/admin/databases", headers=headers)
        assert response.status_code == 200
        databases = response.json()
        db_names = [db["name"] for db in databases]
        assert db_name in db_names
        
        # 5. 获取数据库详情
        response = db_client.get(f"/api/admin/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        db_detail = response.json()
        assert db_detail["success"] == True
        assert "data" in db_detail
        assert "database" in db_detail["data"]
        assert db_detail["data"]["database"]["name"] == db_name
        assert "files" in db_detail["data"]
        
        # 6. 删除数据库
        response = db_client.delete(f"/api/admin/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        delete_result = response.json()
        assert delete_result["success"] == True
        
        # 7. 验证数据库已被删除
        response = db_client.get(f"/api/admin/databases/{db_id}", headers=headers)
        assert response.status_code == 404  # 应该返回404 Not Found

    def test_get_operation_logs(self, db_client: TestClient):
        """测试获取操作日志接口"""
        # 1. 初始化管理员并获取其ID和令牌
        admin_username = random_username("admin_logs")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_id = response.json()["user_id"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. 创建一个普通用户以生成更多日志
        user_username = random_username("log_user")
        user_data = {"username": user_username, "password": "testpass", "role": "user"}
        response = db_client.post("/api/auth/users", json=user_data, headers=headers)
        assert response.status_code == 200
        user_id = response.json()["id"]

        # 3. 获取所有操作日志，验证有初始化、创建用户等操作
        response = db_client.get("/api/admin/logs", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) >= 2
        operations = [log['operation'] for log in logs]
        assert "系统初始化" in operations
        assert "创建用户" in operations

        # 4. 按 user_id 筛选日志
        response = db_client.get(f"/api/admin/logs?user_id={admin_id}", headers=headers)
        assert response.status_code == 200
        admin_logs = response.json()
        assert len(admin_logs) > 0
        for log in admin_logs:
            assert log['user_id'] == admin_id

        # 5. 按 operation 筛选日志
        response = db_client.get('/api/admin/logs?operation=创建用户', headers=headers)
        assert response.status_code == 200
        create_user_logs = response.json()
        assert len(create_user_logs) >= 1
        assert create_user_logs[0]['operation'] == "创建用户"

        # 6. 测试分页
        response = db_client.get('/api/admin/logs?limit=1', headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_admin_api_insufficient_permissions(self, db_client: TestClient):
        """测试普通用户无法访问管理后台API"""
        # 1. 初始化管理员并创建普通用户
        admin_username = random_username("admin_perm_api")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        user_username = random_username("normal_user_api_perm")
        new_user_data = {"username": user_username, "password": "testpass", "role": "user"}
        response = db_client.post("/api/auth/users", json=new_user_data, headers=admin_headers)
        assert response.status_code == 200

        # 2. 普通用户登录获取令牌
        login_data = {"username": user_username, "password": "testpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 3. 尝试使用普通用户令牌访问所有管理后台端点
        admin_endpoints = [
            "/api/admin/users",
            "/api/admin/stats",
            "/api/admin/logs",
            "/api/admin/databases"
        ]

        for endpoint in admin_endpoints:
            response = db_client.get(endpoint, headers=user_headers)
            assert response.status_code == 403
