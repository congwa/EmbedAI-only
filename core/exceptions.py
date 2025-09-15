"""
自定义异常和异常处理器
"""
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from utils.logging_config import logger


class EmbedAIException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class KnowledgeBaseError(EmbedAIException):
    """知识库相关异常"""
    def __init__(self, message: str, code: str = "KB_ERROR"):
        super().__init__(message, code)


class RAGError(EmbedAIException):
    """RAG检索相关异常"""
    def __init__(self, message: str, code: str = "RAG_ERROR"):
        super().__init__(message, code)


class ModelError(EmbedAIException):
    """模型相关异常"""
    def __init__(self, message: str, code: str = "MODEL_ERROR"):
        super().__init__(message, code)




class RateLimitError(EmbedAIException):
    """限流异常"""
    def __init__(self, message: str = "请求过于频繁，请稍后再试", code: str = "RATE_LIMIT_ERROR"):
        super().__init__(message, code)


def setup_exception_handlers(app: FastAPI):
    """设置异常处理器"""
    
    @app.exception_handler(EmbedAIException)
    async def embedai_exception_handler(request: Request, exc: EmbedAIException):
        """自定义异常处理器"""
        logger.error(f"EmbedAI异常: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "type": exc.__class__.__name__
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证异常处理器"""
        logger.error(f"请求验证失败: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求参数验证失败",
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        logger.error(f"未处理异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                    "type": exc.__class__.__name__
                }
            }
        )
