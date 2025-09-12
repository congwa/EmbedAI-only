"""
图谱管理API测试用例
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from main import app
from api.models.user_model import User


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_admin_user():
    """模拟管理员用户"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "admin"
    user.role = "admin"
    return user


@pytest.fixture
def mock_knowledge_graph():
    """模拟知识图谱数据"""
    class MockNode:
        def __init__(self, node_id, labels, properties):
            self.id = node_id
            self.labels = labels
            self.properties = properties
    
    class MockEdge:
        def __init__(self, edge_id, source, target, edge_type, properties):
            self.id = edge_id
            self.source = source
            self.target = target
            self.type = edge_type
            self.properties = properties
    
    class MockKnowledgeGraph:
        def __init__(self):
            self.nodes = [
                MockNode("node1", ["Entity"], {"entity_type": "Person", "name": "张三"}),
                MockNode("node2", ["Entity"], {"entity_type": "Company", "name": "ABC公司"})
            ]
            self.edges = [
                MockEdge("edge1", "node1", "node2", "WORKS_AT", {"since": "2020"})
            ]
            self.is_truncated = False
    
    return MockKnowledgeGraph()


class TestLightRAGSubgraph:
    """LightRAG子图查询测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.is_lightrag_database")
    @patch("knowledge.knowledge_base._get_lightrag_instance")
    def test_get_lightrag_subgraph_success(self, mock_get_instance, mock_is_lightrag, mock_get_admin, 
                                           client, mock_admin_user, mock_knowledge_graph):
        """测试获取LightRAG子图成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_lightrag.return_value = True
        
        # 模拟LightRAG实例
        mock_rag_instance = Mock()
        mock_rag_instance.get_knowledge_graph = AsyncMock(return_value=mock_knowledge_graph)
        mock_get_instance.return_value = mock_rag_instance
        
        response = client.get("/api/graph/lightrag/subgraph", params={
            "db_id": "lightrag_test_db",
            "node_label": "Entity",
            "max_depth": 2,
            "max_nodes": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["nodes"]) == 2
        assert len(data["data"]["edges"]) == 1
        assert data["data"]["total_nodes"] == 2
        assert data["data"]["total_edges"] == 1
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.is_lightrag_database")
    def test_get_lightrag_subgraph_not_lightrag_db(self, mock_is_lightrag, mock_get_admin, client, mock_admin_user):
        """测试非LightRAG数据库获取子图失败"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_lightrag.return_value = False
        
        response = client.get("/api/graph/lightrag/subgraph", params={
            "db_id": "regular_db",
            "node_label": "Entity",
            "max_depth": 2,
            "max_nodes": 100
        })
        
        assert response.status_code == 400
        assert "不是 LightRAG 类型" in response.json()["detail"]
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.is_lightrag_database")
    @patch("knowledge.knowledge_base._get_lightrag_instance")
    def test_get_lightrag_subgraph_instance_not_found(self, mock_get_instance, mock_is_lightrag, 
                                                      mock_get_admin, client, mock_admin_user):
        """测试LightRAG实例不存在"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_lightrag.return_value = True
        mock_get_instance.return_value = None
        
        response = client.get("/api/graph/lightrag/subgraph", params={
            "db_id": "nonexistent_db",
            "node_label": "Entity",
            "max_depth": 2,
            "max_nodes": 100
        })
        
        assert response.status_code == 404
        assert "不存在或无法访问" in response.json()["detail"]


class TestLightRAGDatabases:
    """LightRAG数据库管理测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.get_lightrag_databases")
    def test_get_lightrag_databases_success(self, mock_get_databases, mock_get_admin, client, mock_admin_user):
        """测试获取LightRAG数据库列表成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_get_databases.return_value = [
            {"db_id": "lightrag_db1", "name": "测试图谱1"},
            {"db_id": "lightrag_db2", "name": "测试图谱2"}
        ]
        
        response = client.get("/api/graph/lightrag/databases")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["databases"]) == 2
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.get_lightrag_databases")
    def test_get_lightrag_databases_error(self, mock_get_databases, mock_get_admin, client, mock_admin_user):
        """测试获取LightRAG数据库列表出错"""
        mock_get_admin.return_value = mock_admin_user
        mock_get_databases.side_effect = Exception("数据库连接失败")
        
        response = client.get("/api/graph/lightrag/databases")
        assert response.status_code == 500
        assert "获取 LightRAG 数据库列表失败" in response.json()["detail"]


class TestLightRAGLabels:
    """LightRAG标签管理测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.is_lightrag_database")
    @patch("knowledge.knowledge_base._get_lightrag_instance")
    def test_get_lightrag_labels_success(self, mock_get_instance, mock_is_lightrag, mock_get_admin, 
                                         client, mock_admin_user):
        """测试获取LightRAG标签成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_lightrag.return_value = True
        
        # 模拟LightRAG实例
        mock_rag_instance = Mock()
        mock_rag_instance.get_graph_labels = AsyncMock(return_value=["Entity", "Relationship", "Document"])
        mock_get_instance.return_value = mock_rag_instance
        
        response = client.get("/api/graph/lightrag/labels", params={"db_id": "lightrag_test_db"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Entity" in data["data"]["labels"]
        assert "Relationship" in data["data"]["labels"]


class TestNeo4jNodes:
    """Neo4j节点管理测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.is_running")
    @patch("knowledge.graph_base.get_sample_nodes")
    def test_get_neo4j_nodes_success(self, mock_get_nodes, mock_is_running, mock_get_admin, 
                                     client, mock_admin_user):
        """测试获取Neo4j节点成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_running.return_value = True
        mock_get_nodes.return_value = {
            "nodes": [
                {"id": "1", "labels": ["Person"], "properties": {"name": "张三"}},
                {"id": "2", "labels": ["Company"], "properties": {"name": "ABC公司"}}
            ],
            "total": 2
        }
        
        response = client.get("/api/graph/neo4j/nodes", params={
            "kgdb_name": "neo4j",
            "num": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["result"]["nodes"]) == 2
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.is_running")
    def test_get_neo4j_nodes_db_not_running(self, mock_is_running, mock_get_admin, client, mock_admin_user):
        """测试Neo4j数据库未运行"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_running.return_value = False
        
        response = client.get("/api/graph/neo4j/nodes", params={
            "kgdb_name": "neo4j",
            "num": 100
        })
        
        assert response.status_code == 400
        assert "图数据库未启动" in response.json()["detail"]
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.is_running")
    @patch("knowledge.graph_base.query_node")
    def test_get_neo4j_node_by_entity(self, mock_query_node, mock_is_running, mock_get_admin, 
                                      client, mock_admin_user):
        """测试根据实体名查询Neo4j节点"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_running.return_value = True
        mock_query_node.return_value = {
            "node": {"id": "1", "labels": ["Person"], "properties": {"name": "张三"}},
            "relationships": []
        }
        
        response = client.get("/api/graph/neo4j/node", params={"entity_name": "张三"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["node"]["properties"]["name"] == "张三"


class TestLightRAGStats:
    """LightRAG统计信息测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.knowledge_base.is_lightrag_database")
    @patch("knowledge.knowledge_base._get_lightrag_instance")
    def test_get_lightrag_stats_success(self, mock_get_instance, mock_is_lightrag, mock_get_admin, 
                                        client, mock_admin_user, mock_knowledge_graph):
        """测试获取LightRAG统计信息成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_lightrag.return_value = True
        
        # 模拟LightRAG实例
        mock_rag_instance = Mock()
        mock_rag_instance.get_knowledge_graph = AsyncMock(return_value=mock_knowledge_graph)
        mock_get_instance.return_value = mock_rag_instance
        
        response = client.get("/api/graph/lightrag/stats", params={"db_id": "lightrag_test_db"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_nodes"] == 2
        assert data["data"]["total_edges"] == 1
        assert len(data["data"]["entity_types"]) > 0


class TestNeo4jInfo:
    """Neo4j信息测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.get_graph_info")
    def test_get_neo4j_info_success(self, mock_get_info, mock_get_admin, client, mock_admin_user):
        """测试获取Neo4j信息成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_get_info.return_value = {
            "version": "5.0.0",
            "database": "neo4j",
            "status": "online",
            "node_count": 1000,
            "relationship_count": 2500
        }
        
        response = client.get("/api/graph/neo4j/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["version"] == "5.0.0"
        assert data["data"]["node_count"] == 1000
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.get_graph_info")
    def test_get_neo4j_info_error(self, mock_get_info, mock_get_admin, client, mock_admin_user):
        """测试获取Neo4j信息失败"""
        mock_get_admin.return_value = mock_admin_user
        mock_get_info.return_value = None
        
        response = client.get("/api/graph/neo4j/info")
        assert response.status_code == 400
        assert "图数据库获取出错" in response.json()["detail"]


class TestNeo4jEntityIndexing:
    """Neo4j实体索引测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.is_running")
    @patch("knowledge.graph_base.add_embedding_to_nodes")
    def test_index_neo4j_entities_success(self, mock_add_embedding, mock_is_running, mock_get_admin, 
                                          client, mock_admin_user):
        """测试Neo4j实体索引成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_running.return_value = True
        mock_add_embedding.return_value = 150  # 索引了150个节点
        
        response = client.post("/api/graph/neo4j/index-entities", json={
            "kgdb_name": "neo4j"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["indexed_count"] == 150
        assert "已成功为150个节点添加嵌入向量" in data["message"]
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.is_running")
    def test_index_neo4j_entities_db_not_running(self, mock_is_running, mock_get_admin, 
                                                  client, mock_admin_user):
        """测试Neo4j数据库未运行时索引失败"""
        mock_get_admin.return_value = mock_admin_user
        mock_is_running.return_value = False
        
        response = client.post("/api/graph/neo4j/index-entities", json={
            "kgdb_name": "neo4j"
        })
        
        assert response.status_code == 400
        assert "图数据库未启动" in response.json()["detail"]


class TestNeo4jEntityAddition:
    """Neo4j实体添加测试"""
    
    @patch("api.utils.auth_middleware.get_admin_user")
    @patch("knowledge.graph_base.jsonl_file_add_entity")
    def test_add_neo4j_entities_success(self, mock_add_entity, mock_get_admin, client, mock_admin_user):
        """测试添加Neo4j实体成功"""
        mock_get_admin.return_value = mock_admin_user
        mock_add_entity.return_value = AsyncMock()
        
        response = client.post("/api/graph/neo4j/add-entities", json={
            "file_path": "/path/to/entities.jsonl",
            "kgdb_name": "neo4j"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "实体添加成功" in data["message"]
    
    def test_add_neo4j_entities_invalid_file(self, client):
        """测试添加Neo4j实体时文件格式错误"""
        with patch("api.utils.auth_middleware.get_admin_user"):
            response = client.post("/api/graph/neo4j/add-entities", json={
                "file_path": "/path/to/entities.txt",  # 错误的文件格式
                "kgdb_name": "neo4j"
            })
        
        assert response.status_code == 200  # 这个接口返回200但success为False
        data = response.json()
        assert data["success"] is False
        assert "文件格式错误" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
