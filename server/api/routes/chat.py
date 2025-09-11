"""
聊天推荐API路由 - 集成知识库数据库
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import time
import uuid

from api.models.user_model import User
from api.models.kb_models import KnowledgeDatabase, KnowledgeFile, KnowledgeNode
from api.models.thread_model import Thread
from api.utils.auth_middleware import get_current_user, get_db
from api.utils.common_utils import log_operation
from src.utils import logger

router = APIRouter(prefix="/chat", tags=["chat"])


# =============================================================================
# === 请求和响应模型 ===
# =============================================================================

class ChatRequest(BaseModel):
    message: str
    db_id: Optional[str] = None
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool = True
    reply: str
    thread_id: str
    sources: List[dict] = []
    timestamp: int


class ThreadCreateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# =============================================================================
# === 聊天API ===
# =============================================================================

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送聊天消息并获取基于知识库的回复
    """
    start_time = time.time()
    
    try:
        # 获取或创建线程
        thread_id = chat_request.thread_id
        if not thread_id:
            thread_id = str(uuid.uuid4())
            # 创建新的对话线程
            thread = Thread(
                id=thread_id,
                user_id=str(current_user.id),
                agent_id="kb_agent",
                title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
            )
            db.add(thread)
            db.commit()
        
        # 如果指定了数据库ID，从该数据库查询相关信息
        sources = []
        if chat_request.db_id:
            knowledge_db = db.query(KnowledgeDatabase).filter(
                KnowledgeDatabase.db_id == chat_request.db_id
            ).first()
            
            if knowledge_db:
                # 简单的关键词匹配查询（实际项目中应该使用向量搜索）
                nodes = db.query(KnowledgeNode).join(KnowledgeFile).filter(
                    KnowledgeFile.database_id == chat_request.db_id,
                    KnowledgeNode.text.ilike(f"%{chat_request.message[:20]}%")
                ).limit(3).all()
                
                sources = [
                    {
                        "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                        "file_id": node.file_id,
                        "metadata": node.meta_info or {}
                    }
                    for node in nodes
                ]
        
        # 生成回复（这里是简化版，实际应该调用LLM）
        if sources:
            reply = f"基于知识库内容，我找到了以下相关信息：\n\n"
            for i, source in enumerate(sources, 1):
                reply += f"{i}. {source['text']}\n\n"
            reply += "希望这些信息对您有帮助！"
        else:
            reply = "很抱歉，我在知识库中没有找到相关信息。您可以尝试换个问法或联系管理员添加更多知识内容。"
        
        # 记录操作日志
        log_operation(db, current_user.id, "发送聊天消息", f"消息: {chat_request.message[:50]}, 线程: {thread_id}", request)
        
        duration = time.time() - start_time
        logger.info(f"聊天消息处理完成: user_id={current_user.id}, thread_id={thread_id}, 耗时={duration:.3f}s")
        
        return ChatResponse(
            reply=reply,
            thread_id=thread_id,
            sources=sources,
            timestamp=int(time.time())
        )
        
    except Exception as e:
        logger.error(f"聊天消息处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理聊天消息失败: {str(e)}"
        )


async def log_recommendation_details(
    tenant_id: str, 
    session_id: str, 
    trace_id: str, 
    product_count: int, 
    duration: float
):
    """异步记录推荐详情日志"""
    try:
        logger.info(
            f"推荐详情 - 租户: {tenant_id}, 会话: {session_id}, "
            f"追踪: {trace_id}, 商品数: {product_count}, 耗时: {duration:.3f}s"
        )
    except Exception as e:
        logger.error(f"记录推荐详情失败: {e}")


@router.get("/sessions/{session_id}/history")
@limiter.limit("60/minute")
async def get_session_history(
    request: Request,
    session_id: str,
    tenant_id: str,
    limit: int = 50
):
    """
    获取会话历史记录
    
    Args:
        session_id: 会话ID
        tenant_id: 租户ID
        limit: 返回条数限制
    """
    try:
        # 这里可以实现会话历史记录的获取逻辑
        # 目前返回空列表，后续可以接入数据库或缓存
        
        logger.info(f"获取会话历史: session_id={session_id}, tenant_id={tenant_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "history": [],  # 暂时返回空历史
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"获取会话历史失败: {e}")
        return {
            "success": False,
            "error": {
                "code": "HISTORY_ERROR",
                "message": "获取会话历史失败"
            }
        }


@router.delete("/sessions/{session_id}")
@limiter.limit("10/minute")
async def clear_session(
    request: Request,
    session_id: str,
    tenant_id: str
):
    """
    清空会话历史
    
    Args:
        session_id: 会话ID
        tenant_id: 租户ID
    """
    try:
        # 这里可以实现会话清空逻辑
        
        logger.info(f"清空会话: session_id={session_id}, tenant_id={tenant_id}")
        
        return {
            "success": True,
            "message": "会话已清空"
        }
        
    except Exception as e:
        logger.error(f"清空会话失败: {e}")
        return {
            "success": False,
            "error": {
                "code": "CLEAR_SESSION_ERROR", 
                "message": "清空会话失败"
            }
        }


@router.get("/threads", response_model=List[dict])
async def get_user_threads(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    获取用户的对话线程列表
    """
    try:
        threads = db.query(Thread).filter(
            Thread.user_id == str(current_user.id)
        ).order_by(Thread.created_at.desc()).offset(skip).limit(limit).all()
        
        result = [
            {
                "id": thread.id,
                "title": thread.title,
                "description": thread.description,
                "status": thread.status,
                "created_at": thread.created_at.isoformat() if thread.created_at else None,
                "updated_at": thread.updated_at.isoformat() if thread.updated_at else None
            }
            for thread in threads
        ]
        
        log_operation(db, current_user.id, "获取对话线程", f"获取 {len(result)} 个线程", request)
        
        return result
        
    except Exception as e:
        logger.error(f"获取对话线程失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话线程失败: {str(e)}"
        )


@router.post("/threads", response_model=dict)
async def create_thread(
    request: Request,
    thread_request: ThreadCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的对话线程
    """
    try:
        thread_id = str(uuid.uuid4())
        thread = Thread(
            id=thread_id,
            user_id=str(current_user.id),
            agent_id="kb_agent",
            title=thread_request.title or "新对话",
            description=thread_request.description
        )
        
        db.add(thread)
        db.commit()
        
        log_operation(db, current_user.id, "创建对话线程", f"线程ID: {thread_id}", request)
        
        return {
            "id": thread.id,
            "title": thread.title,
            "description": thread.description,
            "status": thread.status,
            "created_at": thread.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"创建对话线程失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建对话线程失败: {str(e)}"
        )


@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除对话线程
    """
    try:
        thread = db.query(Thread).filter(
            Thread.id == thread_id,
            Thread.user_id == str(current_user.id)
        ).first()
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话线程未找到"
            )
        
        db.delete(thread)
        db.commit()
        
        log_operation(db, current_user.id, "删除对话线程", f"线程ID: {thread_id}", request)
        
        return {"success": True, "message": "对话线程已删除"}
        
    except Exception as e:
        logger.error(f"删除对话线程失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除对话线程失败: {str(e)}"
        )
