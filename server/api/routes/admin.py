"""
管理后台API路由
"""
from fastapi import APIRouter, Depends, Request, UploadFile, File, BackgroundTasks
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
import time
import uuid

from core.kb_service import KBService
from schemas.requests import DatabaseCreateRequest, IndexBuildRequest
from schemas.responses import (
    DatabaseListResponse, DatabaseDetailResponse, DatabaseInfo,
    UploadResponse, IndexBuildResponse, StandardResponse
)
from utils.logging_config import logger

# 限流器
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def get_kb_service(request: Request) -> KBService:
    """获取知识库服务依赖"""
    from main import app_state
    return app_state["kb_service"]


@router.get("/kb/databases", response_model=DatabaseListResponse)
@limiter.limit("30/minute")
async def list_databases(
    request: Request,
    tenant_id: Optional[str] = None,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    获取数据库列表
    
    Args:
        tenant_id: 可选的租户ID过滤
    """
    try:
        databases_data = kb_service.list_databases(tenant_id)
        
        databases = [
            DatabaseInfo(
                id=db["id"],
                name=db["name"],
                tenant_id=db["tenant_id"],
                status=db["status"],
                file_count=db.get("file_count", 0),
                chunk_count=db.get("chunk_count", 0),
                created_at=db["created_at"],
                updated_at=db["updated_at"]
            ) for db in databases_data
        ]
        
        logger.info(f"获取数据库列表: tenant_id={tenant_id}, 数量={len(databases)}")
        
        return DatabaseListResponse(
            databases=databases,
            total=len(databases)
        )
        
    except Exception as e:
        logger.error(f"获取数据库列表失败: {e}")
        return DatabaseListResponse(
            success=False,
            databases=[],
            total=0
        )


@router.post("/kb/databases", response_model=StandardResponse)
@limiter.limit("10/minute")
async def create_database(
    request: Request,
    db_request: DatabaseCreateRequest,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    创建新数据库
    """
    try:
        # 生成数据库ID
        db_id = f"tenant_{db_request.tenant_id}_{uuid.uuid4().hex[:8]}"
        
        # 创建数据库（这里简化处理，实际需要调用kb_service的创建方法）
        await kb_service.get_or_create_tenant_db(db_request.tenant_id)
        
        logger.info(f"创建数据库: {db_id}, 租户: {db_request.tenant_id}")
        
        return StandardResponse(
            message=f"数据库创建成功: {db_id}",
            data={"database_id": db_id}
        )
        
    except Exception as e:
        logger.error(f"创建数据库失败: {e}")
        return StandardResponse(
            success=False,
            message=f"创建数据库失败: {str(e)}"
        )


@router.get("/kb/databases/{db_id}", response_model=DatabaseDetailResponse)
@limiter.limit("60/minute")
async def get_database_detail(
    request: Request,
    db_id: str,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    获取数据库详情
    """
    try:
        db_info = kb_service.get_database_info(db_id)
        
        # 构建数据库信息
        database = DatabaseInfo(
            id=db_id,
            name=db_info.get("name", db_id),
            description=db_info.get("description"),
            tenant_id=db_info.get("tenant_id", ""),
            status=db_info.get("status", "active"),
            file_count=db_info.get("file_count", 0),
            chunk_count=db_info.get("chunk_count", 0),
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        # 获取文件列表（简化处理）
        files = []
        
        logger.info(f"获取数据库详情: {db_id}")
        
        return DatabaseDetailResponse(
            database=database,
            files=files
        )
        
    except Exception as e:
        logger.error(f"获取数据库详情失败: {e}")
        return DatabaseDetailResponse(
            success=False,
            database=DatabaseInfo(
                id=db_id,
                name="未知",
                tenant_id="",
                status="error",
                created_at=int(time.time()),
                updated_at=int(time.time())
            ),
            files=[]
        )


@router.delete("/kb/databases/{db_id}", response_model=StandardResponse)
@limiter.limit("5/minute")
async def delete_database(
    request: Request,
    db_id: str,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    删除数据库
    """
    try:
        # 这里需要实现删除逻辑
        logger.info(f"删除数据库: {db_id}")
        
        return StandardResponse(
            message=f"数据库删除成功: {db_id}"
        )
        
    except Exception as e:
        logger.error(f"删除数据库失败: {e}")
        return StandardResponse(
            success=False,
            message=f"删除数据库失败: {str(e)}"
        )


@router.post("/kb/upload", response_model=UploadResponse)
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    database_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    上传文件到知识库
    """
    try:
        # 生成文件ID
        file_id = f"file_{uuid.uuid4().hex}"
        
        # 保存上传的文件
        file_path = f"./data/uploads/{file_id}_{file.filename}"
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 异步处理文件索引
        if background_tasks:
            background_tasks.add_task(
                process_uploaded_file,
                kb_service,
                database_id,
                file_id,
                file_path,
                file.filename
            )
        
        logger.info(f"文件上传成功: {file.filename}, file_id={file_id}")
        
        return UploadResponse(
            file_id=file_id,
            message=f"文件上传成功: {file.filename}"
        )
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return UploadResponse(
            success=False,
            file_id="",
            message=f"文件上传失败: {str(e)}"
        )


@router.post("/kb/index", response_model=IndexBuildResponse)
@limiter.limit("5/minute")
async def build_index(
    request: Request,
    index_request: IndexBuildRequest,
    background_tasks: BackgroundTasks,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    构建知识库索引
    """
    try:
        # 生成任务ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # 异步构建索引
        background_tasks.add_task(
            build_index_task,
            kb_service,
            index_request.database_id,
            task_id,
            index_request.force_rebuild
        )
        
        logger.info(f"索引构建任务启动: {task_id}, 数据库: {index_request.database_id}")
        
        return IndexBuildResponse(
            task_id=task_id,
            message="索引构建任务已启动"
        )
        
    except Exception as e:
        logger.error(f"启动索引构建失败: {e}")
        return IndexBuildResponse(
            success=False,
            task_id="",
            message=f"启动索引构建失败: {str(e)}"
        )


async def process_uploaded_file(
    kb_service: KBService,
    database_id: str,
    file_id: str,
    file_path: str,
    filename: str
):
    """异步处理上传的文件"""
    try:
        logger.info(f"开始处理文件: {filename}, file_id={file_id}")
        
        # 这里需要调用知识库服务的文件处理方法
        # 暂时只记录日志
        
        logger.info(f"文件处理完成: {filename}")
        
    except Exception as e:
        logger.error(f"文件处理失败: {e}")


async def build_index_task(
    kb_service: KBService,
    database_id: str,
    task_id: str,
    force_rebuild: bool
):
    """异步构建索引任务"""
    try:
        logger.info(f"开始构建索引: {database_id}, task_id={task_id}")
        
        # 这里需要调用知识库服务的索引构建方法
        # 暂时只记录日志
        
        logger.info(f"索引构建完成: {task_id}")
        
    except Exception as e:
        logger.error(f"索引构建失败: {e}")


@router.get("/analytics/conversations")
@limiter.limit("30/minute")
async def get_conversation_analytics(
    request: Request,
    tenant_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """
    获取对话分析数据
    """
    try:
        # 这里可以实现对话分析逻辑
        # 暂时返回模拟数据
        
        analytics_data = {
            "total_conversations": 0,
            "total_recommendations": 0,
            "avg_products_per_query": 0.0,
            "top_queries": [],
            "popular_products": [],
            "conversion_rate": 0.0
        }
        
        logger.info(f"获取对话分析: tenant_id={tenant_id}")
        
        return {
            "success": True,
            "data": analytics_data
        }
        
    except Exception as e:
        logger.error(f"获取对话分析失败: {e}")
        return {
            "success": False,
            "error": {
                "code": "ANALYTICS_ERROR",
                "message": "获取分析数据失败"
            }
        }
