"""
聊天功能相关的API集成测试
"""
import pytest
import uuid
import random
import string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest import mock

# 标记所有测试为聊天和数据库测试
pytestmark = [pytest.mark.chat, pytest.mark.database]

# 生成唯一用户名后缀
def unique_suffix():
    return uuid.uuid4().hex[:8]
    
# 生成完全随机的用户名
def random_username(prefix="user"):
    random_str = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    return f"{prefix}_{random_str}_{unique_suffix()}"


class TestChatAPI:
    """测试聊天相关的API"""

    def test_create_thread(self, db_client: TestClient):
        """测试创建新的对话线程"""
        # 1. 初始化用户以获取令牌
        username = random_username("chat_user")
        user_data = {"username": username, "password": "testpass", "role": "user"}
        
        # 需要先创建管理员来创建普通用户
        admin_username = random_username("chat_admin")
        admin_init_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_init_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = db_client.post("/api/auth/users", json=user_data, headers=admin_headers)
        assert response.status_code == 200

        # 2. 用户登录
        login_data = {"username": username, "password": "testpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {user_token}"}

        # 3. 创建对话线程
        thread_title = f"测试线程_{unique_suffix()}"
        thread_data = {"title": thread_title, "description": "这是一个测试线程"}
        response = db_client.post("/api/chat/threads", json=thread_data, headers=headers)
        assert response.status_code == 200
        result = response.json()

        # 4. 验证响应
        assert "id" in result
        assert result["title"] == thread_title
        assert result["description"] == "这是一个测试线程"
        assert result["status"] == 1

    def test_get_user_threads(self, db_client: TestClient):
        """测试获取用户的对话线程列表和分页"""
        # 1. 初始化用户
        username = random_username("chat_user_list")
        user_data = {"username": username, "password": "testpass", "role": "user"}
        admin_username = random_username("chat_admin_list")
        admin_init_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_init_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = db_client.post("/api/auth/users", json=user_data, headers=admin_headers)
        assert response.status_code == 200

        # 2. 用户登录
        login_data = {"username": username, "password": "testpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {user_token}"}

        # 3. 为用户创建多个对话线程
        thread_titles = []
        for i in range(5):
            thread_title = f"线程_{i}_{unique_suffix()}"
            thread_titles.append(thread_title)
            thread_data = {"title": thread_title}
            response = db_client.post("/api/chat/threads", json=thread_data, headers=headers)
            assert response.status_code == 200

        # 4. 获取所有线程
        response = db_client.get("/api/chat/threads", headers=headers)
        assert response.status_code == 200
        threads = response.json()
        assert len(threads) == 5

        # 5. 测试分页 limit
        response = db_client.get("/api/chat/threads?limit=2", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

        # 6. 测试分页 skip 和 limit
        response = db_client.get("/api/chat/threads?skip=2&limit=3", headers=headers)
        assert response.status_code == 200
        paginated_threads = response.json()
        assert len(paginated_threads) == 3

    def test_send_message(self, db_client: TestClient):
        """测试发送聊天消息并从知识库获取回复"""
        from api.models.kb_models import KnowledgeDatabase, KnowledgeFile, KnowledgeNode

        # 1. 初始化用户和知识库
        admin_username = random_username("chat_admin_msg")
        admin_init_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_init_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"消息测试知识库_{unique_suffix()}"
        kb_data = {"name": kb_name}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 手动在数据库中创建文件和知识节点以供查询
        # 这是因为目前没有API直接创建节点，而send_message依赖于节点查询
        from api.db_manager import db_manager
        with db_manager.get_session() as db:
            file_id = f"file_{unique_suffix()}"
            new_file = KnowledgeFile(file_id=file_id, database_id=db_id, filename="test_file.txt", path="/tmp/test_file.txt", file_type="text/plain", status="completed")
            db.add(new_file)
            
            node_text = "关于苹果公司的信息"
            new_node = KnowledgeNode(file_id=file_id, text=node_text)
            db.add(new_node)
            db.commit()

        # 3. 发送包含关键词的消息
        chat_data = {"message": "苹果公司", "db_id": db_id}
        response = db_client.post("/api/chat/message", json=chat_data, headers=headers)
        assert response.status_code == 200
        result = response.json()

        # 4. 验证回复和来源
        assert "基于知识库内容" in result["reply"]
        assert len(result["sources"]) > 0
        assert result["sources"][0]["text"] == node_text

        # 5. 测试不带db_id的通用回复
        chat_data_no_db = {"message": "你好"}
        response = db_client.post("/api/chat/message", json=chat_data_no_db, headers=headers)
        assert response.status_code == 200
        result_no_db = response.json()
        assert "没有找到相关信息" in result_no_db["reply"]
        assert len(result_no_db["sources"]) == 0

    def test_delete_thread(self, db_client: TestClient):
        """测试删除对话线程"""
        # 1. 初始化用户
        username = random_username("chat_user_delete")
        user_data = {"username": username, "password": "testpass", "role": "user"}
        admin_username = random_username("chat_admin_delete")
        admin_init_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_init_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = db_client.post("/api/auth/users", json=user_data, headers=admin_headers)
        assert response.status_code == 200

        # 2. 用户登录
        login_data = {"username": username, "password": "testpass"}
        response = db_client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {user_token}"}

        # 3. 创建一个对话线程
        thread_data = {"title": "待删除线程"}
        response = db_client.post("/api/chat/threads", json=thread_data, headers=headers)
        assert response.status_code == 200
        thread_id = response.json()["id"]

        # 4. 删除该线程
        response = db_client.delete(f"/api/chat/threads/{thread_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True

        # 5. 验证线程已被删除
        response = db_client.get("/api/chat/threads", headers=headers)
        assert response.status_code == 200
        threads = response.json()
        assert all(t["id"] != thread_id for t in threads)
