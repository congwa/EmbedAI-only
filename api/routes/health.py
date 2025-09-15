"""
健康检查API路由
"""
from fastapi import APIRouter, Depends
from prometheus_client import Counter, Histogram
import time

from core.config import settings
from schemas.responses import HealthResponse
from utils.logging_config import logger

# Prometheus指标
health_check_counter = Counter("health_checks_total", "健康检查总次数")
health_check_duration = Histogram("health_check_duration_seconds", "健康检查耗时")

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """系统健康检查"""
    start_time = time.time()
    
    try:
        # 记录指标
        health_check_counter.inc()
        
        # 简单的健康状态检查
        status = "healthy"
        checks = {
            "api": "ok",
            "config": "ok" if settings.SILICONFLOW_API_KEY else "warning",
        }
        
        # 计算耗时
        duration = time.time() - start_time
        health_check_duration.observe(duration)
        
        logger.info(f"健康检查完成，耗时: {duration:.3f}s")
        
        return HealthResponse(
            status=status,
            checks=checks,
            timestamp=int(time.time()),
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        duration = time.time() - start_time
        health_check_duration.observe(duration)
        
        return HealthResponse(
            status="unhealthy",
            checks={"api": "error"},
            timestamp=int(time.time()),
            version="1.0.0",
            error=str(e)
        )


@router.get("/ready")
async def readiness_check():
    """就绪检查"""
    return {"status": "ready", "timestamp": int(time.time())}


@router.get("/live")
async def liveness_check():  
    """存活检查"""
    return {"status": "alive", "timestamp": int(time.time())}
