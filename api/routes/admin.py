"""
管理后台API路由 - 权限管理和数据库管理
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.models.user_model import User, OperationLog
from api.models.kb_models import KnowledgeDatabase, KnowledgeFile
from api.utils.auth_middleware import get_admin_user, get_current_user, get_db
from api.utils.common_utils import log_operation
from utils.logging_config import logger

router = APIRouter(tags=["admin"])


# =============================================================================
# === 响应模型 ===
# =============================================================================

class UserListResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: str
    last_login: str | None = None


class DatabaseResponse(BaseModel):
    id: int
    db_id: str
    name: str
    description: str | None = None
    embed_model: str | None = None
    dimension: int | None = None
    created_at: str
    file_count: int = 0


class OperationLogResponse(BaseModel):
    id: int
    user_id: int
    username: str
    operation: str
    details: str | None = None
    ip_address: str | None = None
    timestamp: str


class CreateDatabaseRequest(BaseModel):
    name: str
    description: str | None = None
    embed_model: str | None = None


# =============================================================================
# === 用户管理API ===
# =============================================================================

@router.get("/users", response_model=List[UserListResponse])
async def get_users(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过的用户数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的用户数"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（管理员权限）
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        
        result = []
        for user in users:
            result.append(UserListResponse(
                id=user.id,
                username=user.username,
                role=user.role,
                created_at=user.created_at.isoformat() if user.created_at else "",
                last_login=user.last_login.isoformat() if user.last_login else None
            ))
        
        log_operation(db, current_user.id, "查看用户列表", f"获取用户列表，跳过 {skip}，限制 {limit}", request)
        
        logger.info(f"管理员 {current_user.username} 获取用户列表，数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


# =============================================================================
# === 操作日志API ===
# =============================================================================

@router.get("/logs", response_model=List[OperationLogResponse])
async def get_operation_logs(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过的日志数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的日志数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    operation: Optional[str] = Query(None, description="操作类型筛选"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取操作日志（管理员权限）
    """
    try:
        query = db.query(OperationLog).join(User)
        
        if user_id:
            query = query.filter(OperationLog.user_id == user_id)
        if operation:
            query = query.filter(OperationLog.operation.ilike(f"%{operation}%"))
        
        logs = query.order_by(OperationLog.timestamp.desc()).offset(skip).limit(limit).all()
        
        result = []
        for log in logs:
            result.append(OperationLogResponse(
                id=log.id,
                user_id=log.user_id,
                username=log.user.username,
                operation=log.operation,
                details=log.details,
                ip_address=log.ip_address,
                timestamp=log.timestamp.isoformat() if log.timestamp else ""
            ))
        
        log_operation(db, current_user.id, "查看操作日志", f"获取操作日志，筛选条件: user_id={user_id}, operation={operation}", request)
        
        logger.info(f"管理员 {current_user.username} 获取操作日志，数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取操作日志失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取操作日志失败"
        )


# =============================================================================
# === 数据库管理API ===
# =============================================================================

@router.get("/databases", response_model=List[DatabaseResponse])
async def get_databases(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过的数据库数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的数据库数"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取知识库数据库列表（管理员权限）
    """
    try:
        # 查询数据库列表，同时统计文件数量
        databases_query = db.query(
            KnowledgeDatabase,
            func.count(KnowledgeFile.id).label('file_count')
        ).outerjoin(KnowledgeFile).group_by(KnowledgeDatabase.id)
        
        databases_with_count = databases_query.offset(skip).limit(limit).all()
        
        result = []
        for database, file_count in databases_with_count:
            result.append(DatabaseResponse(
                id=database.id,
                db_id=database.db_id,
                name=database.name,
                description=database.description,
                embed_model=database.embed_model,
                dimension=database.dimension,
                created_at=database.created_at.isoformat() if database.created_at else "",
                file_count=file_count
            ))
        
        log_operation(db, current_user.id, "查看数据库列表", f"获取数据库列表，跳过 {skip}，限制 {limit}", request)
        
        logger.info(f"管理员 {current_user.username} 获取数据库列表，数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取数据库列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据库列表失败"
        )


@router.post("/databases", response_model=dict)
async def create_database(
    request: Request,
    db_request: CreateDatabaseRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建新的知识库数据库（管理员权限）
    """
    try:
        # 生成数据库ID
        import uuid
        db_id = f"kb_{uuid.uuid4().hex[:8]}"
        
        # 创建数据库记录
        new_database = KnowledgeDatabase(
            db_id=db_id,
            name=db_request.name,
            description=db_request.description,
            embed_model=db_request.embed_model
        )
        
        db.add(new_database)
        db.commit()
        db.refresh(new_database)
        
        log_operation(db, current_user.id, "创建数据库", f"创建知识库数据库: {db_request.name}, ID: {db_id}", request)
        
        logger.info(f"管理员 {current_user.username} 创建数据库: {db_request.name}")
        
        return {
            "success": True,
            "message": "数据库创建成功",
            "data": {
                "id": new_database.id,
                "db_id": db_id,
                "name": new_database.name
            }
        }
        
    except Exception as e:
        logger.error(f"创建数据库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建数据库失败: {str(e)}"
        )


@router.delete("/databases/{db_id}", response_model=dict)
async def delete_database(
    request: Request,
    db_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除知识库数据库（管理员权限）
    """
    try:
        # 查找数据库
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据库不存在"
            )
        
        # 删除数据库（级联删除相关文件和节点）
        db.delete(database)
        db.commit()
        
        log_operation(db, current_user.id, "删除数据库", f"删除知识库数据库: {database.name}, ID: {db_id}", request)
        
        logger.info(f"管理员 {current_user.username} 删除数据库: {database.name}")
        
        return {
            "success": True,
            "message": "数据库删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除数据库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除数据库失败: {str(e)}"
        )


# =============================================================================
# === 系统统计API ===
# =============================================================================

@router.get("/stats", response_model=dict)
async def get_system_stats(
    request: Request,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取系统统计信息（管理员权限）
    """
    try:
        # 统计用户数量
        total_users = db.query(User).count()
        admin_users = db.query(User).filter(User.role.in_(["admin", "superadmin"])).count()
        
        # 统计数据库数量
        total_databases = db.query(KnowledgeDatabase).count()
        total_files = db.query(KnowledgeFile).count()
        
        # 最近操作日志
        recent_logs_count = db.query(OperationLog).filter(
            OperationLog.timestamp >= datetime.now().replace(hour=0, minute=0, second=0)
        ).count()
        
        stats = {
            "users": {
                "total": total_users,
                "admins": admin_users,
                "regular": total_users - admin_users
            },
            "databases": {
                "total": total_databases,
                "total_files": total_files
            },
            "activity": {
                "today_operations": recent_logs_count
            }
        }
        
        log_operation(db, current_user.id, "查看系统统计", "获取系统统计信息", request)
        
        logger.info(f"管理员 {current_user.username} 获取系统统计信息")
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统统计失败"
        )


# =============================================================================
# === 数据库详情API ===
# =============================================================================

@router.get("/databases/{db_id}", response_model=dict)
async def get_database_detail(
    request: Request,
    db_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取知识库数据库详情（管理员权限）
    """
    try:
        # 查找数据库及其文件
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据库不存在"
            )
        
        # 获取文件列表
        files = db.query(KnowledgeFile).filter(KnowledgeFile.database_id == db_id).all()
        
        log_operation(db, current_user.id, "查看数据库详情", f"查看数据库详情: {database.name}, ID: {db_id}", request)
        
        logger.info(f"管理员 {current_user.username} 查看数据库详情: {database.name}")
        
        return {
            "success": True,
            "data": {
                "database": DatabaseResponse(
                    id=database.id,
                    db_id=database.db_id,
                    name=database.name,
                    description=database.description,
                    embed_model=database.embed_model,
                    dimension=database.dimension,
                    created_at=database.created_at.isoformat() if database.created_at else "",
                    file_count=len(files)
                ),
                "files": [
                    {
                        "file_id": file.file_id,
                        "filename": file.filename,
                        "file_type": file.file_type,
                        "status": file.status,
                        "created_at": file.created_at.isoformat() if file.created_at else ""
                    } for file in files
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取数据库详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库详情失败: {str(e)}"
        )
