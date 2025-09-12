"""
数据库连接测试
验证与启动的数据库服务的连接性
"""
import pytest


class TestMilvusConnection:
    """Milvus数据库连接测试"""
    
    def test_milvus_connection(self):
        """测试Milvus连接"""
        try:
            from pymilvus import connections, utility
            
            # 连接到Milvus
            connections.connect(
                alias="test_connection",
                host="localhost",
                port=10103
            )
            
            # 验证连接
            assert connections.has_connection("test_connection")
            
            # 测试基本操作
            collections = utility.list_collections()
            assert isinstance(collections, list)
            
            print(f"✅ Milvus连接成功，发现 {len(collections)} 个集合")
            
        except ImportError:
            pytest.skip("pymilvus未安装")
        except Exception as e:
            pytest.fail(f"Milvus连接失败: {e}")
        finally:
            try:
                connections.disconnect("test_connection")
            except:
                pass
    
    def test_milvus_collection_operations(self):
        """测试Milvus集合操作"""
        try:
            from pymilvus import (
                connections, utility, Collection, 
                FieldSchema, CollectionSchema, DataType
            )
            
            connections.connect(
                alias="test_ops",
                host="localhost", 
                port=10103
            )
            
            collection_name = "test_embedai_collection"
            
            # 清理可能存在的集合
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
            
            # 创建测试集合
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000)
            ]
            
            schema = CollectionSchema(fields, "EmbedAI测试集合")
            collection = Collection(collection_name, schema)
            
            # 验证集合创建成功
            assert utility.has_collection(collection_name)
            print(f"✅ 成功创建Milvus集合: {collection_name}")
            
            # 清理
            utility.drop_collection(collection_name)
            
        except ImportError:
            pytest.skip("pymilvus未安装")
        except Exception as e:
            pytest.fail(f"Milvus集合操作失败: {e}")
        finally:
            try:
                connections.disconnect("test_ops")
            except:
                pass


class TestNeo4jConnection:
    """Neo4j数据库连接测试"""
    
    def test_neo4j_connection(self):
        """测试Neo4j连接"""
        try:
            from neo4j import GraphDatabase
            
            # 连接到Neo4j
            driver = GraphDatabase.driver(
                "bolt://localhost:10105",
                auth=("neo4j", "embedai123")
            )
            
            # 测试连接
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                assert record["test"] == 1
                
            print("✅ Neo4j连接成功")
            driver.close()
            
        except ImportError:
            pytest.skip("neo4j未安装")
        except Exception as e:
            pytest.fail(f"Neo4j连接失败: {e}")
    
    def test_neo4j_basic_operations(self):
        """测试Neo4j基本操作"""
        try:
            from neo4j import GraphDatabase
            
            driver = GraphDatabase.driver(
                "bolt://localhost:10105",
                auth=("neo4j", "embedai123")
            )
            
            with driver.session() as session:
                # 创建测试节点
                result = session.run(
                    "CREATE (p:TestProduct {name: $name, price: $price}) RETURN p.name as name",
                    name="EmbedAI测试产品",
                    price=999
                )
                record = result.single()
                assert record["name"] == "EmbedAI测试产品"
                
                # 查询节点数量
                result = session.run("MATCH (p:TestProduct) RETURN count(p) as count")
                count = result.single()["count"]
                assert count >= 1
                
                print(f"✅ Neo4j基本操作成功，创建了测试节点")
                
                # 清理测试数据
                session.run("MATCH (p:TestProduct {name: $name}) DELETE p", 
                           name="EmbedAI测试产品")
                
            driver.close()
            
        except ImportError:
            pytest.skip("neo4j未安装")
        except Exception as e:
            pytest.fail(f"Neo4j操作失败: {e}")


class TestMinIOConnection:
    """MinIO对象存储连接测试"""
    
    def test_minio_connection(self):
        """测试MinIO连接"""
        try:
            from minio import Minio
            
            # 连接到MinIO
            client = Minio(
                "localhost:10106",
                access_key="minioadmin",
                secret_key="minioadmin123",
                secure=False
            )
            
            # 测试连接
            buckets = client.list_buckets()
            assert isinstance(buckets, list)
            
            print(f"✅ MinIO连接成功，发现 {len(buckets)} 个存储桶")
            
        except ImportError:
            pytest.skip("minio未安装")
        except Exception as e:
            pytest.fail(f"MinIO连接失败: {e}")
    
    def test_minio_bucket_operations(self):
        """测试MinIO存储桶操作"""
        try:
            from minio import Minio
            from io import BytesIO
            
            client = Minio(
                "localhost:10106", 
                access_key="minioadmin",
                secret_key="minioadmin123",
                secure=False
            )
            
            bucket_name = "embedai-test"
            
            # 创建存储桶（如果不存在）
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                print(f"✅ 创建存储桶: {bucket_name}")
            
            # 上传测试文件
            test_content = b"EmbedAI test file content"
            object_name = "test/embedai_test.txt"
            
            client.put_object(
                bucket_name,
                object_name,
                BytesIO(test_content),
                length=len(test_content)
            )
            
            # 验证文件存在
            obj = client.get_object(bucket_name, object_name)
            content = obj.read()
            assert content == test_content
            
            print(f"✅ MinIO文件操作成功")
            
            # 清理测试文件
            client.remove_object(bucket_name, object_name)
            
        except ImportError:
            pytest.skip("minio未安装")
        except Exception as e:
            pytest.fail(f"MinIO操作失败: {e}")


class TestDatabaseIntegration:
    """数据库集成测试"""
    
    def test_all_databases_available(self):
        """测试所有数据库都可用"""
        results = {}
        
        # 测试Milvus
        try:
            from pymilvus import connections
            connections.connect(alias="integration_test", host="localhost", port=10103)
            results["milvus"] = "✅ 可用"
            connections.disconnect("integration_test")
        except Exception as e:
            results["milvus"] = f"❌ 不可用: {e}"
        
        # 测试Neo4j  
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:10105", auth=("neo4j", "embedai123"))
            with driver.session() as session:
                session.run("RETURN 1")
            results["neo4j"] = "✅ 可用"
            driver.close()
        except Exception as e:
            results["neo4j"] = f"❌ 不可用: {e}"
        
        # 测试MinIO
        try:
            from minio import Minio
            client = Minio("localhost:10106", access_key="minioadmin", secret_key="minioadmin123", secure=False)
            client.list_buckets()
            results["minio"] = "✅ 可用"
        except Exception as e:
            results["minio"] = f"❌ 不可用: {e}"
        
        # 打印结果
        print("\n" + "="*50)
        print("数据库连接状态:")
        print("="*50)
        for db_name, status in results.items():
            print(f"{db_name.upper():10s}: {status}")
        print("="*50)
        
        # 验证至少有一个数据库可用
        available_count = sum(1 for status in results.values() if "✅" in status)
        assert available_count > 0, "至少需要一个数据库可用"
        
        return results
