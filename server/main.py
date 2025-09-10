"""
EmbedAI RAG商品推荐聊天机器人 - 主应用入口
"""
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.routes import chat, admin, health
from core.config import settings
from core.exceptions import setup_exception_handlers
from utils.logging_config import setup_logging


# 设置限流器
limiter = Limiter(key_func=get_remote_address)

# 全局状态管理
app_state: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    setup_logging()
    
    # 初始化知识库管理器
    from core.kb_service import KBService
    kb_service = KBService()
    app_state["kb_service"] = kb_service
    
    yield
    
    # 关闭时清理资源
    if "kb_service" in app_state:
        await app_state["kb_service"].cleanup()


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title="EmbedAI RAG推荐API",
        description="基于RAG的智能商品推荐聊天机器人API服务",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )
    
    # 添加限流中间件
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health.router, prefix="/api", tags=["健康检查"])
    app.include_router(chat.router, prefix="/api/chat", tags=["聊天推荐"])
    app.include_router(admin.router, prefix="/api/admin", tags=["管理后台"])
    
    # 添加Prometheus指标端点
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # 设置异常处理器
    setup_exception_handlers(app)
    
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """添加处理时间头部"""
        import time
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    return app


# 创建应用实例
app = create_app()


@app.get("/")
async def root():
    """根路径"""
    return {"message": "EmbedAI RAG推荐API服务运行中", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
