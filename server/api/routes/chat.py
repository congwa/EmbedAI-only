"""
聊天推荐API路由
"""
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_client import Counter, Histogram
import time

from core.kb_service import KBService
from schemas.requests import ChatRecommendationRequest
from schemas.responses import ChatRecommendationResponse
from utils.logging_config import logger

# Prometheus指标
chat_requests_counter = Counter("chat_requests_total", "聊天请求总数", ["tenant_id", "status"])
chat_request_duration = Histogram("chat_request_duration_seconds", "聊天请求耗时")
recommendation_counter = Counter("recommendations_total", "推荐商品总数", ["tenant_id"])

# 限流器
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def get_kb_service(request: Request) -> KBService:
    """获取知识库服务依赖"""
    from main import app_state
    return app_state["kb_service"]


@router.post("/recommendations", response_model=ChatRecommendationResponse)
@limiter.limit("30/minute")  # 每分钟30次请求限制
async def chat_recommendations(
    request: Request,
    chat_request: ChatRecommendationRequest,
    background_tasks: BackgroundTasks,
    kb_service: KBService = Depends(get_kb_service)
):
    """
    聊天商品推荐API
    
    接收用户的自然语言查询，返回相关商品推荐和AI回复
    """
    start_time = time.time()
    
    try:
        logger.info(f"收到推荐请求: tenant_id={chat_request.tenant_id}, session_id={chat_request.session_id}")
        
        # 执行推荐查询
        response = await kb_service.chat_recommendation(chat_request)
        
        # 记录指标
        duration = time.time() - start_time
        chat_request_duration.observe(duration)
        chat_requests_counter.labels(
            tenant_id=chat_request.tenant_id, 
            status="success" if response.success else "error"
        ).inc()
        recommendation_counter.labels(tenant_id=chat_request.tenant_id).inc(len(response.products))
        
        # 异步记录详细日志
        background_tasks.add_task(
            log_recommendation_details,
            chat_request.tenant_id,
            chat_request.session_id,
            response.trace_id,
            len(response.products),
            duration
        )
        
        logger.info(f"推荐完成: trace_id={response.trace_id}, 耗时={duration:.3f}s, 商品数={len(response.products)}")
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        chat_request_duration.observe(duration)
        chat_requests_counter.labels(tenant_id=chat_request.tenant_id, status="error").inc()
        
        logger.error(f"推荐请求处理失败: {e}", exc_info=True)
        
        # 返回错误响应
        return ChatRecommendationResponse(
            success=False,
            reply="抱歉，系统暂时无法处理您的请求，请稍后再试。",
            products=[],
            evidence=[],
            trace_id=f"error_{int(time.time())}",
            session_id=chat_request.session_id,
            timestamp=int(time.time())
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
