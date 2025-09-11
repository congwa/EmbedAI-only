"""
知识库管理API路由 - 知识库CRUD、文档管理、查询等
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Query, UploadFile, File, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.models.user_model import User
from api.models.kb_models import KnowledgeDatabase, KnowledgeFile, KnowledgeNode
from api.utils.auth_middleware import get_current_user, get_db
from api.utils.common_utils import log_operation
from knowledge import knowledge_base
from src.utils import logger

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# =============================================================================
# === 请求/响应模型 ===
# =============================================================================

class DatabaseCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    embed_model: Optional[str] = "text-embedding-ada-002"
    dimension: Optional[int] = 1536


class DatabaseUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    embed_model: Optional[str] = None
    dimension: Optional[int] = None


class DatabaseResponse(BaseModel):
    id: int
    db_id: str
    name: str
    description: Optional[str] = None
    embed_model: Optional[str] = None
    dimension: Optional[int] = None
    created_at: str
    file_count: int = 0


class DocumentAddRequest(BaseModel):
    items: List[Dict[str, Any]]
    params: Optional[Dict[str, Any]] = {}


class QueryRequest(BaseModel):
    query: str
    meta: Optional[Dict[str, Any]] = {}


# =============================================================================
# === 数据库管理接口 ===
# =============================================================================

@router.get("/databases", response_model=List[DatabaseResponse])
async def get_databases(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有知识库"""
    try:
        # 查询数据库列表，同时统计文件数量
        databases_query = db.query(
            KnowledgeDatabase,
            func.count(KnowledgeFile.id).label('file_count')
        ).outerjoin(KnowledgeFile).group_by(KnowledgeDatabase.id)
        
        databases_with_count = databases_query.all()
        
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
        
        log_operation(db, current_user.id, "查看知识库列表", f"获取知识库列表，数量: {len(result)}", request)
        
        logger.info(f"用户 {current_user.username} 获取知识库列表，数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取知识库列表失败"
        )


@router.post("/databases", response_model=dict)
async def create_database(
    request: Request,
    db_request: DatabaseCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建知识库"""
    try:
        # 生成数据库ID
        db_id = f"kb_{uuid.uuid4().hex[:8]}"
        
        # 创建数据库记录
        new_database = KnowledgeDatabase(
            db_id=db_id,
            name=db_request.name,
            description=db_request.description,
            embed_model=db_request.embed_model,
            dimension=db_request.dimension
        )
        
        db.add(new_database)
        db.commit()
        db.refresh(new_database)
        
        # 初始化知识库（如果需要）
        try:
            await knowledge_base.create_knowledge_base(db_id, {
                "name": db_request.name,
                "description": db_request.description,
                "embed_model": db_request.embed_model,
                "dimension": db_request.dimension
            })
        except Exception as kb_error:
            logger.warning(f"知识库后端初始化失败: {kb_error}")
        
        log_operation(db, current_user.id, "创建知识库", f"创建知识库: {db_request.name}, ID: {db_id}", request)
        
        logger.info(f"用户 {current_user.username} 创建知识库: {db_request.name}")
        
        return {
            "success": True,
            "message": "知识库创建成功",
            "data": {
                "id": new_database.id,
                "db_id": db_id,
                "name": new_database.name
            }
        }
        
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库失败: {str(e)}"
        )


@router.get("/databases/{db_id}", response_model=dict)
async def get_database_info(
    request: Request,
    db_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库详细信息"""
    try:
        # 查找数据库
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 获取文件列表
        files = db.query(KnowledgeFile).filter(KnowledgeFile.database_id == db_id).all()
        
        log_operation(db, current_user.id, "查看知识库详情", f"查看知识库: {database.name}, ID: {db_id}", request)
        
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
        logger.error(f"获取知识库详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库详情失败: {str(e)}"
        )


@router.put("/databases/{db_id}", response_model=dict)
async def update_database(
    request: Request,
    db_id: str,
    update_request: DatabaseUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新知识库信息"""
    try:
        # 查找数据库
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 更新字段
        if update_request.name is not None:
            database.name = update_request.name
        if update_request.description is not None:
            database.description = update_request.description
        if update_request.embed_model is not None:
            database.embed_model = update_request.embed_model
        if update_request.dimension is not None:
            database.dimension = update_request.dimension
        
        db.commit()
        db.refresh(database)
        
        log_operation(db, current_user.id, "更新知识库", f"更新知识库: {database.name}, ID: {db_id}", request)
        
        logger.info(f"用户 {current_user.username} 更新知识库: {database.name}")
        
        return {
            "success": True,
            "message": "知识库更新成功",
            "data": {
                "id": database.id,
                "db_id": database.db_id,
                "name": database.name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知识库失败: {str(e)}"
        )


@router.delete("/databases/{db_id}", response_model=dict)
async def delete_database(
    request: Request,
    db_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除知识库"""
    try:
        # 查找数据库
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 删除知识库后端数据（如果存在）
        try:
            await knowledge_base.delete_knowledge_base(db_id)
        except Exception as kb_error:
            logger.warning(f"知识库后端删除失败: {kb_error}")
        
        # 删除数据库记录（级联删除相关文件和节点）
        db.delete(database)
        db.commit()
        
        log_operation(db, current_user.id, "删除知识库", f"删除知识库: {database.name}, ID: {db_id}", request)
        
        logger.info(f"用户 {current_user.username} 删除知识库: {database.name}")
        
        return {
            "success": True,
            "message": "知识库删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识库失败: {str(e)}"
        )


# =============================================================================
# === 文档管理接口 ===
# =============================================================================

@router.post("/databases/{db_id}/documents", response_model=dict)
async def add_documents(
    request: Request,
    db_id: str,
    doc_request: DocumentAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加文档到知识库"""
    try:
        # 检查数据库是否存在
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 处理文档添加（这里需要根据实际的知识库实现来调整）
        added_docs = []
        for item in doc_request.items:
            try:
                # 生成文件ID
                file_id = f"doc_{uuid.uuid4().hex[:8]}"
                
                # 创建文件记录
                new_file = KnowledgeFile(
                    file_id=file_id,
                    database_id=db_id,
                    filename=item.get("filename", "unknown"),
                    path=item.get("path", ""),
                    file_type=item.get("type", "text"),
                    status="processing"
                )
                
                db.add(new_file)
                added_docs.append(file_id)
                
            except Exception as doc_error:
                logger.error(f"添加文档失败: {doc_error}")
                continue
        
        db.commit()
        
        log_operation(db, current_user.id, "添加文档", f"向知识库 {db_id} 添加 {len(added_docs)} 个文档", request)
        
        return {
            "success": True,
            "message": f"成功添加 {len(added_docs)} 个文档",
            "data": {
                "added_documents": added_docs
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加文档失败: {str(e)}"
        )


@router.get("/databases/{db_id}/documents/{doc_id}", response_model=dict)
async def get_document_info(
    request: Request,
    db_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档信息"""
    try:
        # 查找文档
        document = db.query(KnowledgeFile).filter(
            KnowledgeFile.database_id == db_id,
            KnowledgeFile.file_id == doc_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )
        
        return {
            "success": True,
            "data": {
                "file_id": document.file_id,
                "filename": document.filename,
                "file_type": document.file_type,
                "status": document.status,
                "created_at": document.created_at.isoformat() if document.created_at else "",
                "node_count": len(document.nodes) if document.nodes else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档信息失败: {str(e)}"
        )


@router.delete("/databases/{db_id}/documents/{doc_id}", response_model=dict)
async def delete_document(
    request: Request,
    db_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文档"""
    try:
        # 查找文档
        document = db.query(KnowledgeFile).filter(
            KnowledgeFile.database_id == db_id,
            KnowledgeFile.file_id == doc_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )
        
        # 删除文档记录（级联删除相关节点）
        db.delete(document)
        db.commit()
        
        log_operation(db, current_user.id, "删除文档", f"删除文档: {document.filename}, ID: {doc_id}", request)
        
        return {
            "success": True,
            "message": "文档删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )


# =============================================================================
# === 查询接口 ===
# =============================================================================

@router.post("/databases/{db_id}/query", response_model=dict)
async def query_knowledge_base(
    request: Request,
    db_id: str,
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询知识库"""
    try:
        # 检查数据库是否存在
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 执行查询（这里需要根据实际的知识库实现来调整）
        try:
            results = await knowledge_base.query_knowledge_base(
                db_id, query_request.query, query_request.meta
            )
        except Exception as query_error:
            logger.error(f"知识库查询失败: {query_error}")
            results = {"results": [], "message": "查询执行失败"}
        
        log_operation(db, current_user.id, "查询知识库", f"查询知识库 {db_id}: {query_request.query[:50]}...", request)
        
        return {
            "success": True,
            "data": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询知识库失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询知识库失败: {str(e)}"
        )


@router.post("/databases/{db_id}/query-test", response_model=dict)
async def query_test(
    request: Request,
    db_id: str,
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """测试查询知识库"""
    try:
        # 检查数据库是否存在
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 执行测试查询
        try:
            results = await knowledge_base.test_query_knowledge_base(
                db_id, query_request.query, query_request.meta
            )
        except Exception as query_error:
            logger.error(f"测试查询失败: {query_error}")
            results = {"results": [], "message": "测试查询执行失败", "debug_info": str(query_error)}
        
        return {
            "success": True,
            "data": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试查询失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试查询失败: {str(e)}"
        )


@router.get("/databases/{db_id}/query-params", response_model=dict)
async def get_knowledge_base_query_params(
    request: Request,
    db_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库查询参数"""
    try:
        # 检查数据库是否存在
        database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        # 获取查询参数配置
        params = {
            "top_k": 5,
            "score_threshold": 0.7,
            "search_type": "similarity",
            "embed_model": database.embed_model or "text-embedding-ada-002",
            "dimension": database.dimension or 1536
        }
        
        return {
            "success": True,
            "data": params
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取查询参数失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取查询参数失败: {str(e)}"
        )


# =============================================================================
# === 文件上传接口 ===
# =============================================================================

@router.post("/files/upload", response_model=dict)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db_id: Optional[str] = Query(None, description="知识库ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件"""
    try:
        # 检查文件类型
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )
        
        # 如果指定了db_id，检查数据库是否存在
        if db_id:
            database = db.query(KnowledgeDatabase).filter(KnowledgeDatabase.db_id == db_id).first()
            if not database:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="知识库不存在"
                )
        
        # 生成文件ID和路径
        file_id = f"file_{uuid.uuid4().hex[:10]}"
        
        # 读取文件内容
        content = await file.read()
        
        # 这里应该保存文件到磁盘或云存储，现在先模拟
        file_path = f"/tmp/uploads/{file_id}_{file.filename}"
        
        # 如果指定了db_id，创建文件记录
        if db_id:
            new_file = KnowledgeFile(
                file_id=file_id,
                database_id=db_id,
                filename=file.filename,
                path=file_path,
                file_type=file.content_type or "application/octet-stream",
                status="uploaded"
            )
            db.add(new_file)
            db.commit()
        
        log_operation(db, current_user.id, "上传文件", f"上传文件: {file.filename}, ID: {file_id}", request)
        
        return {
            "success": True,
            "message": "文件上传成功",
            "data": {
                "file_id": file_id,
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


# =============================================================================
# === 知识库类型和统计接口 ===
# =============================================================================

@router.get("/types", response_model=dict)
async def get_knowledge_base_types(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """获取支持的知识库类型"""
    try:
        types = [
            {
                "type": "vector",
                "name": "向量数据库",
                "description": "基于向量相似度的知识检索",
                "supported": True
            },
            {
                "type": "graph",
                "name": "知识图谱",
                "description": "基于实体关系的知识表示",
                "supported": True
            },
            {
                "type": "hybrid",
                "name": "混合模式",
                "description": "结合向量和图谱的混合检索",
                "supported": False
            }
        ]
        
        return {
            "success": True,
            "data": types
        }
        
    except Exception as e:
        logger.error(f"获取知识库类型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库类型失败: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_statistics(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库统计信息"""
    try:
        # 统计知识库数量
        total_databases = db.query(KnowledgeDatabase).count()
        
        # 统计文件数量
        total_files = db.query(KnowledgeFile).count()
        
        # 统计节点数量
        total_nodes = db.query(KnowledgeNode).count()
        
        # 按状态统计文件
        file_status_stats = db.query(
            KnowledgeFile.status,
            func.count(KnowledgeFile.id).label('count')
        ).group_by(KnowledgeFile.status).all()
        
        status_stats = {status: count for status, count in file_status_stats}
        
        stats = {
            "databases": {
                "total": total_databases
            },
            "files": {
                "total": total_files,
                "by_status": status_stats
            },
            "nodes": {
                "total": total_nodes
            }
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
