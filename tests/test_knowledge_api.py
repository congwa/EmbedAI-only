"""
知识库相关的API集成测试
"""
import pytest
import uuid
import random
import string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest import mock

# 标记所有测试为知识库和数据库测试
pytestmark = [pytest.mark.knowledge, pytest.mark.database]

# 生成唯一用户名后缀
def unique_suffix():
    return uuid.uuid4().hex[:8]
    
# 生成完全随机的用户名
def random_username(prefix="user"):
    random_str = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    return f"{prefix}_{random_str}_{unique_suffix()}"


class TestKnowledgeAPI:
    """测试知识库相关的API"""

    def test_create_knowledge_base(self, db_client: TestClient):
        """测试创建知识库"""
        # 1. 初始化管理员以获取令牌
        admin_username = random_username("kb_admin")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. 创建知识库
        kb_name = f"测试知识库_{unique_suffix()}"
        kb_data = {
            "name": kb_name,
            "description": "这是一个测试知识库",
            "embed_model": "test-embedding-model"
        }
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        result = response.json()

        # 3. 验证响应
        assert result["success"] is True
        assert "db_id" in result["data"]
        assert result["data"]["name"] == kb_name

    def test_get_knowledge_bases(self, db_client: TestClient):
        """测试获取知识库列表"""
        # 1. 初始化管理员以获取令牌
        admin_username = random_username("kb_admin_list")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. 创建多个知识库
        kb_names = []
        for i in range(3):
            kb_name = f"列表测试知识库_{i}_{unique_suffix()}"
            kb_names.append(kb_name)
            kb_data = {"name": kb_name, "description": "列表测试"}
            response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
            assert response.status_code == 200

        # 3. 获取知识库列表
        response = db_client.get("/api/knowledge/databases", headers=headers)
        assert response.status_code == 200
        databases = response.json()

        # 4. 验证响应
        assert isinstance(databases, list)
        assert len(databases) >= 3
        
        # 5. 验证创建的知识库都在列表中
        response_kb_names = [db['name'] for db in databases]
        for name in kb_names:
            assert name in response_kb_names

    def test_get_knowledge_base_detail(self, db_client: TestClient):
        """测试获取单个知识库的详细信息"""
        # 1. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_detail")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"详情测试知识库_{unique_suffix()}"
        kb_desc = "这是一个用于测试获取详情的知识库"
        kb_data = {"name": kb_name, "description": kb_desc}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 获取该知识库的详情
        response = db_client.get(f"/api/knowledge/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        detail_data = response.json()

        # 3. 验证详情数据
        assert detail_data["success"] is True
        database_info = detail_data["data"]["database"]
        assert database_info["db_id"] == db_id
        assert database_info["name"] == kb_name
        assert database_info["description"] == kb_desc
        assert database_info["file_count"] == 0
        assert "files" in detail_data["data"]
        assert isinstance(detail_data["data"]["files"], list)

        # 4. 测试获取不存在的知识库
        non_existent_db_id = "kb_nonexistent"
        response = db_client.get(f"/api/knowledge/databases/{non_existent_db_id}", headers=headers)
        assert response.status_code == 404

    def test_update_knowledge_base(self, db_client: TestClient):
        """测试更新知识库信息"""
        # 1. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_update")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"更新前知识库_{unique_suffix()}"
        kb_data = {"name": kb_name, "description": "更新前"}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 更新知识库信息
        updated_kb_name = f"更新后知识库_{unique_suffix()}"
        updated_kb_desc = "更新后描述"
        update_data = {"name": updated_kb_name, "description": updated_kb_desc}
        response = db_client.put(f"/api/knowledge/databases/{db_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        update_result = response.json()
        assert update_result["success"] is True
        assert update_result["data"]["name"] == updated_kb_name

        # 3. 获取详情以验证更新
        response = db_client.get(f"/api/knowledge/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        detail_data = response.json()["data"]["database"]
        assert detail_data["name"] == updated_kb_name
        assert detail_data["description"] == updated_kb_desc

    def test_delete_knowledge_base(self, db_client: TestClient):
        """测试删除知识库"""
        # 1. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_delete")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"待删除知识库_{unique_suffix()}"
        kb_data = {"name": kb_name}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 删除知识库
        response = db_client.delete(f"/api/knowledge/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        delete_result = response.json()
        assert delete_result["success"] is True
        assert delete_result["message"] == "知识库删除成功"

        # 3. 验证知识库已被删除
        response = db_client.get(f"/api/knowledge/databases/{db_id}", headers=headers)
        assert response.status_code == 404

    def test_upload_file_to_kb(self, db_client: TestClient):
        """测试向知识库上传文件"""
        # 1. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_upload")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"文件上传测试知识库_{unique_suffix()}"
        kb_data = {"name": kb_name}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 上传文件
        file_content = "这是一个测试文件。".encode("utf-8")
        files = {"file": ("test.txt", file_content, "text/plain")}
        response = db_client.post(f"/api/knowledge/files/upload?db_id={db_id}", files=files, headers=headers)
        assert response.status_code == 200
        upload_result = response.json()

        # 3. 验证上传结果
        assert upload_result["success"] is True
        assert "file_id" in upload_result["data"]
        assert upload_result["data"]["filename"] == "test.txt"

        # 4. 验证知识库文件数量已更新
        response = db_client.get(f"/api/knowledge/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        detail_data = response.json()["data"]["database"]
        assert detail_data["file_count"] == 1

    def test_get_document_detail(self, db_client: TestClient):
        """测试获取文档详细信息"""
        # 1. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_doc_detail")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"文档详情测试知识库_{unique_suffix()}"
        kb_data = {"name": kb_name}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 上传文件
        file_content = "这是一个用于测试获取文档详情的文件。".encode("utf-8")
        files = {"file": ("detail_test.txt", file_content, "text/plain")}
        response = db_client.post(f"/api/knowledge/files/upload?db_id={db_id}", files=files, headers=headers)
        assert response.status_code == 200
        file_id = response.json()["data"]["file_id"]

        # 3. 获取文档详情
        response = db_client.get(f"/api/knowledge/databases/{db_id}/documents/{file_id}", headers=headers)
        assert response.status_code == 200
        doc_detail = response.json()

        # 4. 验证文档详情
        assert doc_detail["success"] is True
        assert doc_detail["data"]["file_id"] == file_id
        assert doc_detail["data"]["filename"] == "detail_test.txt"
        assert doc_detail["data"]["status"] == "uploaded"

        # 5. 测试获取不存在的文档
        non_existent_doc_id = "doc_nonexistent"
        response = db_client.get(f"/api/knowledge/databases/{db_id}/documents/{non_existent_doc_id}", headers=headers)
        assert response.status_code == 404

    def test_delete_document(self, db_client: TestClient):
        """测试删除知识库中的文档"""
        # 1. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_doc_delete")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"文档删除测试知识库_{unique_suffix()}"
        kb_data = {"name": kb_name}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 2. 上传文件
        file_content = "这是一个待删除的文件。".encode("utf-8")
        files = {"file": ("delete_test.txt", file_content, "text/plain")}
        response = db_client.post(f"/api/knowledge/files/upload?db_id={db_id}", files=files, headers=headers)
        assert response.status_code == 200
        file_id = response.json()["data"]["file_id"]

        # 3. 删除文档
        response = db_client.delete(f"/api/knowledge/databases/{db_id}/documents/{file_id}", headers=headers)
        assert response.status_code == 200
        delete_result = response.json()
        assert delete_result["success"] is True

        # 4. 验证文档已被删除
        response = db_client.get(f"/api/knowledge/databases/{db_id}/documents/{file_id}", headers=headers)
        assert response.status_code == 404

        # 5. 验证知识库文件数量已更新为0
        response = db_client.get(f"/api/knowledge/databases/{db_id}", headers=headers)
        assert response.status_code == 200
        detail_data = response.json()["data"]["database"]
        assert detail_data["file_count"] == 0

    @mock.patch('api.routes.knowledge_router.knowledge_base.aquery')
    def test_query_knowledge_base(self, mock_aquery, db_client: TestClient):
        """测试查询知识库"""
        # 1. 设置 mock 返回值
        mock_aquery.return_value = {"results": [{"text": "这是模拟的查询结果"}]}

        # 2. 初始化管理员并创建知识库
        admin_username = random_username("kb_admin_query")
        admin_data = {"username": admin_username, "password": "adminpass"}
        response = db_client.post("/api/auth/initialize", json=admin_data)
        assert response.status_code == 200
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        kb_name = f"查询测试知识库_{unique_suffix()}"
        kb_data = {"name": kb_name}
        response = db_client.post("/api/knowledge/databases", json=kb_data, headers=headers)
        assert response.status_code == 200
        db_id = response.json()["data"]["db_id"]

        # 3. 查询知识库
        query_data = {"query": "测试查询"}
        response = db_client.post(f"/api/knowledge/databases/{db_id}/query", json=query_data, headers=headers)
        assert response.status_code == 200
        query_result = response.json()

        # 4. 验证查询结果
        assert query_result["success"] is True
        assert query_result["data"]["results"][0]["text"] == "这是模拟的查询结果"
        mock_aquery.assert_called_once_with(query_text="测试查询", db_id=db_id)

        # 5. 测试查询不存在的知识库
        response = db_client.post("/api/knowledge/databases/kb_nonexistent/query", json=query_data, headers=headers)
        assert response.status_code == 404
