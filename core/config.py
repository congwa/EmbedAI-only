"""
应用配置设置
"""
import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础设置
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    # CORS设置
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # 数据库设置
    WORK_DIR: str = Field(default="./data", env="WORK_DIR")
    
    # SiliconFlow API设置
    SILICONFLOW_API_KEY: str = Field(default="", env="SILICONFLOW_API_KEY")
    SILICONFLOW_BASE_URL: str = Field(
        default="https://api.siliconflow.cn/v1", 
        env="SILICONFLOW_BASE_URL"
    )
    
    # LightRAG设置
    LIGHTRAG_LLM_PROVIDER: str = Field(default="siliconflow", env="LIGHTRAG_LLM_PROVIDER")
    LIGHTRAG_LLM_NAME: str = Field(default="zai-org/GLM-4.5-Air", env="LIGHTRAG_LLM_NAME")
    LIGHTRAG_EMBEDDING_MODEL: str = Field(default="BAAI/bge-m3", env="LIGHTRAG_EMBEDDING_MODEL")
    LIGHTRAG_RERANKER_MODEL: str = Field(default="BAAI/bge-reranker-large", env="LIGHTRAG_RERANKER_MODEL")
    
    # Milvus设置
    MILVUS_HOST: str = Field(default="localhost", env="MILVUS_HOST")
    MILVUS_PORT: int = Field(default=19530, env="MILVUS_PORT")
    MILVUS_USER: str = Field(default="", env="MILVUS_USER")
    MILVUS_PASSWORD: str = Field(default="", env="MILVUS_PASSWORD")
    
    # Neo4j设置
    NEO4J_URI: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # MinIO设置
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    MINIO_BUCKET: str = Field(default="embedai", env="MINIO_BUCKET")
    
    # 限流设置
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1小时
    
    # 推荐设置
    DEFAULT_TOP_K: int = Field(default=10, env="DEFAULT_TOP_K")
    MAX_TOP_K: int = Field(default=50, env="MAX_TOP_K")
    MAX_HISTORY_LENGTH: int = Field(default=20, env="MAX_HISTORY_LENGTH")
    
    # 安全设置
    DOMAIN_WHITELIST: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="DOMAIN_WHITELIST"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建配置实例
settings = Settings()


def get_openai_config() -> dict:
    """获取OpenAI兼容配置"""
    return {
        "api_key": settings.SILICONFLOW_API_KEY,
        "base_url": settings.SILICONFLOW_BASE_URL,
        "model": settings.LIGHTRAG_LLM_NAME,
    }


def get_embedding_config() -> dict:
    """获取Embedding配置"""
    return {
        "api_key": settings.SILICONFLOW_API_KEY,
        "base_url": settings.SILICONFLOW_BASE_URL,
        "model": settings.LIGHTRAG_EMBEDDING_MODEL,
        "dimension": 1024,  # bge-m3的维度
    }


def get_reranker_config() -> dict:
    """获取Reranker配置"""
    return {
        "api_key": settings.SILICONFLOW_API_KEY,
        "base_url": settings.SILICONFLOW_BASE_URL,
        "model": settings.LIGHTRAG_RERANKER_MODEL,
    }
