"""
外部数据库与存储服务的集成测试。
要求本地通过 `docker-compose-db.yml` 启动 Milvus、Neo4j、MinIO。
"""
import uuid

import pytest
from pymilvus import utility

pytestmark = [pytest.mark.integration, pytest.mark.database]


def test_milvus_list_collections(real_milvus_connection):
    """验证 Milvus 服务可用，能够列出集合并执行基础操作。"""
    collections = utility.list_collections(timeout=5)
    assert isinstance(collections, list)


def test_neo4j_create_and_cleanup_node(real_neo4j_driver):
    """验证 Neo4j 服务可执行基本的 Cypher 写入与清理。"""
    label = f"TestNode_{uuid.uuid4().hex[:8]}"
    property_value = "embedai"

    with real_neo4j_driver.session() as session:
        # 创建节点
        created = session.run(
            f"CREATE (n:{label} {{value: $value}}) RETURN n.value",
            value=property_value,
        ).single()
        assert created is not None
        assert created[0] == property_value

        # 验证节点存在
        exists_count = session.run(
            f"MATCH (n:{label}) RETURN count(n)",
        ).single()[0]
        assert exists_count == 1

        # 删除节点
        deleted_count = session.run(
            f"MATCH (n:{label}) DELETE n RETURN count(n)",
        ).single()[0]
        assert deleted_count == 1  # 应该删除了1个节点

        # 验证节点已被删除
        final_count = session.run(
            f"MATCH (n:{label}) RETURN count(n)",
        ).single()[0]
        assert final_count == 0  # 确认节点已被删除


def test_minio_bucket_lifecycle(real_minio_client):
    """验证 MinIO 服务可以创建与删除 bucket。"""
    bucket_name = f"test-bucket-{uuid.uuid4().hex[:8]}"

    try:
        if not real_minio_client.bucket_exists(bucket_name):
            real_minio_client.make_bucket(bucket_name)

        buckets = [bucket.name for bucket in real_minio_client.list_buckets()]
        assert bucket_name in buckets
    finally:
        if real_minio_client.bucket_exists(bucket_name):
            real_minio_client.remove_bucket(bucket_name)
