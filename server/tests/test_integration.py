"""
集成测试 - 使用真实数据库连接
测试完整的API流程和数据库交互
"""
import pytest
import time
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseConnections:
    """数据库连接集成测试"""
    
    def test_milvus_connection(self, real_milvus_connection):
        """测试Milvus连接"""
        from pymilvus import connections, utility
        
        # 验证连接
        assert connections.has_connection("default")
        
        # 测试基本操作
        collections = utility.list_collections()
        assert isinstance(collections, list)
        
    def test_neo4j_connection(self, real_neo4j_driver):
        """测试Neo4j连接"""
        with real_neo4j_driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            assert record["test"] == 1
            
    def test_minio_connection(self, real_minio_client):
        """测试MinIO连接"""
        buckets = real_minio_client.list_buckets()
        assert isinstance(buckets, list)


@pytest.mark.integration
@pytest.mark.slow
class TestKnowledgeIntegration:
    """知识库集成测试"""
    
    @patch('knowledge.knowledge_base.create_database')
    def test_create_knowledge_database_flow(self, mock_create, integration_client, test_knowledge_data):
        """测试创建知识库完整流程"""
        mock_create.return_value = {"success": True, "database_id": "test_db_123"}
        
        # 模拟登录获取token
        login_data = {"username": "admin", "password": "admin123"}
        
        with patch('api.utils.auth_middleware.get_current_user') as mock_user:
            mock_user.return_value.is_admin = True
            mock_user.return_value.id = 1
            
            # 创建知识库
            kb_data = test_knowledge_data["databases"][0]
            response = integration_client.post("/knowledge/databases", json=kb_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "database_id" in data
            
    @patch('knowledge.knowledge_base.add_document')
    def test_add_document_flow(self, mock_add_doc, integration_client, test_knowledge_data):
        """测试添加文档完整流程"""
        mock_add_doc.return_value = {"success": True, "document_id": "doc_123"}
        
        with patch('api.utils.auth_middleware.get_current_user') as mock_user:
            mock_user.return_value.id = 1
            
            doc_data = {
                "title": "集成测试文档",
                "content": "这是集成测试的文档内容",
                "metadata": {"source": "integration_test"}
            }
            
            response = integration_client.post("/knowledge/databases/test_db/documents", json=doc_data)
            
            assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
class TestGraphIntegration:
    """图谱集成测试"""
    
    @patch('knowledge.graph_base.get_subgraph')
    def test_lightrag_subgraph_integration(self, mock_subgraph, integration_client):
        """测试LightRAG子图查询集成"""
        mock_subgraph.return_value = {
            "nodes": [{"id": "node1", "label": "Product"}],
            "edges": [{"source": "node1", "target": "node2", "relation": "belongs_to"}]
        }
        
        with patch('api.utils.auth_middleware.get_admin_user') as mock_admin:
            mock_admin.return_value.id = 1
            mock_admin.return_value.is_admin = True
            
            response = integration_client.get("/graph/subgraph/lightrag/test_db")
            
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data
            
    @patch('knowledge.graph_base.query_nodes')
    def test_neo4j_nodes_integration(self, mock_query, integration_client):
        """测试Neo4j节点查询集成"""
        mock_query.return_value = [
            {"id": "1", "label": "Product", "properties": {"name": "iPhone"}}
        ]
        
        with patch('api.utils.auth_middleware.get_admin_user') as mock_admin:
            mock_admin.return_value.id = 1
            mock_admin.return_value.is_admin = True
            
            response = integration_client.get("/graph/neo4j/nodes", params={"limit": 10})
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


@pytest.mark.integration
@pytest.mark.auth
class TestAuthIntegration:
    """认证集成测试"""
    
    def test_full_auth_flow(self, integration_client):
        """测试完整认证流程"""
        # 1. 检查系统初始化
        response = integration_client.get("/auth/init-check")
        assert response.status_code == 200
        
        # 2. 模拟首次初始化（如果需要）
        with patch('api.models.user_model.User') as mock_user_model:
            mock_user_model.query.first.return_value = None  # 无用户存在
            
            init_data = {
                "username": "admin",
                "password": "admin123",
                "email": "admin@test.com"
            }
            
            response = integration_client.post("/auth/init", json=init_data)
            # 可能返回200（已初始化）或201（新创建）
            assert response.status_code in [200, 201]


@pytest.mark.integration 
@pytest.mark.slow
class TestChatIntegration:
    """聊天推荐集成测试"""
    
    @patch('models.chat_model.ChatService')
    def test_chat_recommendation_flow(self, mock_chat_service, integration_client):
        """测试聊天推荐完整流程"""
        mock_chat_service.return_value.get_recommendation.return_value = {
            "recommendations": [
                {"product_id": "1", "name": "iPhone 15", "score": 0.95}
            ],
            "explanation": "基于您的历史偏好推荐"
        }
        
        with patch('api.utils.auth_middleware.get_current_user') as mock_user:
            mock_user.return_value.id = 1
            
            chat_data = {
                "message": "我想买一个手机",
                "context": {"budget": "5000-8000"}
            }
            
            response = integration_client.post("/chat/recommend", json=chat_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "recommendations" in data


@pytest.mark.integration
@pytest.mark.database  
class TestDatabaseOperations:
    """数据库操作集成测试"""
    
    def test_milvus_vector_operations(self, real_milvus_connection):
        """测试Milvus向量操作"""
        from pymilvus import Collection, utility, FieldSchema, CollectionSchema, DataType
        
        # 创建测试集合
        collection_name = "test_integration_collection"
        
        # 清理可能存在的集合
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)
        ]
        
        schema = CollectionSchema(fields, "Integration test collection")
        collection = Collection(collection_name, schema)
        
        # 验证集合创建成功
        assert utility.has_collection(collection_name)
        
        # 清理
        utility.drop_collection(collection_name)
        
    def test_neo4j_graph_operations(self, real_neo4j_driver):
        """测试Neo4j图操作"""
        with real_neo4j_driver.session() as session:
            # 创建测试节点
            result = session.run(
                "CREATE (p:TestProduct {name: $name, price: $price}) RETURN p",
                name="Integration Test Product",
                price=999
            )
            
            record = result.single()
            assert record is not None
            
            # 查询并验证
            result = session.run(
                "MATCH (p:TestProduct {name: $name}) RETURN p.price as price",
                name="Integration Test Product"
            )
            record = result.single()
            assert record["price"] == 999
            
            # 清理测试数据
            session.run("MATCH (p:TestProduct {name: $name}) DELETE p", 
                       name="Integration Test Product")
                       
    def test_minio_file_operations(self, real_minio_client):
        """测试MinIO文件操作"""
        bucket_name = "test-integration"
        
        # 确保存储桶存在
        if not real_minio_client.bucket_exists(bucket_name):
            real_minio_client.make_bucket(bucket_name)
        
        # 上传测试文件
        test_content = b"Integration test file content"
        object_name = "test/integration_test.txt"
        
        from io import BytesIO
        real_minio_client.put_object(
            bucket_name, 
            object_name, 
            BytesIO(test_content), 
            length=len(test_content)
        )
        
        # 验证文件存在
        try:
            obj = real_minio_client.get_object(bucket_name, object_name)
            content = obj.read()
            assert content == test_content
        finally:
            # 清理
            real_minio_client.remove_object(bucket_name, object_name)


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndScenarios:
    """端到端场景测试"""
    
    @patch('knowledge.knowledge_base.create_database')
    @patch('knowledge.knowledge_base.add_document') 
    @patch('knowledge.knowledge_base.query_database')
    def test_complete_knowledge_workflow(self, mock_query, mock_add_doc, mock_create, integration_client):
        """测试完整知识库工作流程"""
        # Mock返回值
        mock_create.return_value = {"success": True, "database_id": "workflow_test_db"}
        mock_add_doc.return_value = {"success": True, "document_id": "doc_123"}
        mock_query.return_value = {
            "success": True,
            "results": [{"content": "相关内容", "score": 0.85}]
        }
        
        with patch('api.utils.auth_middleware.get_current_user') as mock_user:
            mock_user.return_value.id = 1
            mock_user.return_value.is_admin = True
            
            # 1. 创建知识库
            kb_data = {"name": "工作流测试库", "description": "端到端测试", "type": "lightrag"}
            response = integration_client.post("/knowledge/databases", json=kb_data)
            assert response.status_code == 200
            
            # 2. 添加文档
            doc_data = {
                "title": "测试文档",
                "content": "这是测试文档内容",
                "metadata": {"category": "test"}
            }
            response = integration_client.post("/knowledge/databases/workflow_test_db/documents", json=doc_data)
            assert response.status_code == 200
            
            # 3. 查询知识库
            query_data = {"query": "测试查询", "top_k": 5}
            response = integration_client.post("/knowledge/databases/workflow_test_db/query", json=query_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "results" in data


@pytest.mark.integration
@pytest.mark.performance
class TestPerformance:
    """性能集成测试"""
    
    def test_api_response_times(self, integration_client):
        """测试API响应时间"""
        with patch('api.utils.auth_middleware.get_current_user') as mock_user:
            mock_user.return_value.id = 1
            
            # 测试健康检查响应时间
            start_time = time.time()
            response = integration_client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 1.0  # 响应时间应小于1秒
            
    @pytest.mark.slow
    def test_concurrent_requests(self, integration_client):
        """测试并发请求"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = integration_client.get("/health")
            results.put(response.status_code)
        
        # 创建10个并发请求
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都成功
        success_count = 0
        while not results.empty():
            status_code = results.get()
            if status_code == 200:
                success_count += 1
        
        assert success_count == 10
