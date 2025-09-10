"""
请求数据模型
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class ProductFilter(BaseModel):
    """商品筛选条件"""
    price: Optional[List[float]] = Field(None, description="价格区间 [最低价, 最高价]")
    brand: Optional[List[str]] = Field(None, description="品牌列表")
    category: Optional[List[str]] = Field(None, description="类目列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    
    @validator('price')
    def validate_price_range(cls, v):
        if v is not None and len(v) == 2:
            if v[0] > v[1]:
                raise ValueError("最低价不能高于最高价")
        return v


class ChatRecommendationRequest(BaseModel):
    """聊天推荐请求模型"""
    tenant_id: str = Field(..., description="租户ID", alias="tenantId")
    session_id: str = Field(..., description="会话ID", alias="sessionId")
    message: str = Field(..., description="用户消息", min_length=1, max_length=1000)
    history: Optional[List[ChatMessage]] = Field(default=[], description="历史对话")
    filters: Optional[ProductFilter] = Field(None, description="筛选条件")
    top_k: Optional[int] = Field(default=10, description="返回商品数量", alias="topK")
    lang: Optional[str] = Field(default="zh-CN", description="语言")
    
    @validator('history')
    def validate_history_length(cls, v):
        if len(v) > 20:  # 最大历史长度
            return v[-20:]  # 只保留最后20条
        return v
    
    @validator('top_k')
    def validate_top_k(cls, v):
        if v <= 0 or v > 50:
            raise ValueError("topK必须在1-50之间")
        return v


class DatabaseCreateRequest(BaseModel):
    """创建数据库请求模型"""
    name: str = Field(..., description="数据库名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="数据库描述", max_length=500)
    tenant_id: str = Field(..., description="租户ID", alias="tenantId")
    embedding_model: Optional[str] = Field(None, description="Embedding模型", alias="embeddingModel")
    chunk_size: Optional[int] = Field(default=1000, description="文档分块大小", alias="chunkSize")
    chunk_overlap: Optional[int] = Field(default=200, description="分块重叠大小", alias="chunkOverlap")


class FileUploadRequest(BaseModel):
    """文件上传请求模型"""
    database_id: str = Field(..., description="数据库ID", alias="databaseId")
    file_type: str = Field(..., description="文件类型", alias="fileType")
    file_name: str = Field(..., description="文件名", alias="fileName")
    source_url: Optional[str] = Field(None, description="源URL", alias="sourceUrl")


class IndexBuildRequest(BaseModel):
    """索引构建请求模型"""
    database_id: str = Field(..., description="数据库ID", alias="databaseId")
    force_rebuild: Optional[bool] = Field(default=False, description="强制重建", alias="forceRebuild")
