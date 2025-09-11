"""
响应数据模型
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ProductRecommendation(BaseModel):
    """商品推荐模型"""
    sku: str = Field(..., description="商品SKU")
    title: str = Field(..., description="商品标题")
    price: float = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币")
    image_url: Optional[str] = Field(None, description="商品图片URL", alias="imageUrl")
    product_url: Optional[str] = Field(None, description="商品详情页URL", alias="productUrl")
    brand: Optional[str] = Field(None, description="品牌")
    category: Optional[str] = Field(None, description="类目")
    rating: Optional[float] = Field(None, description="评分")
    stock: Optional[int] = Field(None, description="库存")
    reasons: List[str] = Field(default=[], description="推荐理由")
    score: float = Field(..., description="推荐分数")
    tags: List[str] = Field(default=[], description="商品标签")


class Evidence(BaseModel):
    """参考证据模型"""
    type: str = Field(..., description="证据类型：doc/url")
    file_id: Optional[str] = Field(None, description="文件ID", alias="fileId")
    snippet: str = Field(..., description="相关片段")
    href: Optional[str] = Field(None, description="链接地址")
    title: Optional[str] = Field(None, description="标题")


class ChatRecommendationResponse(BaseModel):
    """聊天推荐响应模型"""
    success: bool = Field(default=True, description="是否成功")
    reply: str = Field(..., description="AI回复内容")
    products: List[ProductRecommendation] = Field(default=[], description="推荐商品列表")
    evidence: List[Evidence] = Field(default=[], description="参考证据")
    trace_id: str = Field(..., description="追踪ID", alias="traceId")
    session_id: str = Field(..., description="会话ID", alias="sessionId")
    timestamp: int = Field(..., description="时间戳")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="健康状态：healthy/unhealthy")
    checks: Dict[str, str] = Field(..., description="各组件检查状态")
    timestamp: int = Field(..., description="检查时间戳")
    version: str = Field(..., description="版本号")
    error: Optional[str] = Field(None, description="错误信息")


class DatabaseInfo(BaseModel):
    """数据库信息模型"""
    id: str = Field(..., description="数据库ID")
    name: str = Field(..., description="数据库名称")
    description: Optional[str] = Field(None, description="描述")
    status: str = Field(..., description="状态：active/building/error")
    file_count: int = Field(default=0, description="文件数量", alias="fileCount")
    chunk_count: int = Field(default=0, description="文档块数量", alias="chunkCount")
    created_at: int = Field(..., description="创建时间", alias="createdAt")
    updated_at: int = Field(..., description="更新时间", alias="updatedAt")


class FileInfo(BaseModel):
    """文件信息模型"""
    id: str = Field(..., description="文件ID")
    name: str = Field(..., description="文件名")
    type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小")
    status: str = Field(..., description="处理状态：processing/done/failed")
    chunk_count: int = Field(default=0, description="文档块数量", alias="chunkCount")
    error: Optional[str] = Field(None, description="错误信息")
    created_at: int = Field(..., description="创建时间", alias="createdAt")
    updated_at: int = Field(..., description="更新时间", alias="updatedAt")


class DatabaseListResponse(BaseModel):
    """数据库列表响应模型"""
    success: bool = Field(default=True, description="是否成功")
    databases: List[DatabaseInfo] = Field(..., description="数据库列表")
    total: int = Field(..., description="总数")


class DatabaseDetailResponse(BaseModel):
    """数据库详情响应模型"""
    success: bool = Field(default=True, description="是否成功")
    database: DatabaseInfo = Field(..., description="数据库信息")
    files: List[FileInfo] = Field(default=[], description="文件列表")


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool = Field(default=True, description="是否成功")
    file_id: str = Field(..., description="文件ID", alias="fileId")
    message: str = Field(..., description="响应消息")


class IndexBuildResponse(BaseModel):
    """索引构建响应模型"""
    success: bool = Field(default=True, description="是否成功")
    task_id: str = Field(..., description="任务ID", alias="taskId")
    message: str = Field(..., description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="是否成功")
    error: Dict[str, Any] = Field(..., description="错误信息")


class StandardResponse(BaseModel):
    """标准响应模型"""
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
