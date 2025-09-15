#!/usr/bin/env python3
"""
EmbedAI 服务启动脚本
"""
import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import settings
from utils.logging_config import logger


def main():
    """启动服务"""
    try:
        # 确保数据目录存在
        os.makedirs(settings.WORK_DIR, exist_ok=True)
        os.makedirs(f"{settings.WORK_DIR}/logs", exist_ok=True)
        os.makedirs(f"{settings.WORK_DIR}/uploads", exist_ok=True)
        
        logger.info("启动 EmbedAI RAG推荐服务")
        logger.info(f"配置信息:")
        logger.info(f"  - 主机: {settings.HOST}:{settings.PORT}")
        logger.info(f"  - 调试模式: {settings.DEBUG}")
        logger.info(f"  - 工作目录: {settings.WORK_DIR}")
        logger.info(f"  - LLM模型: {settings.LIGHTRAG_LLM_NAME}")
        logger.info(f"  - Embedding模型: {settings.LIGHTRAG_EMBEDDING_MODEL}")
        
        # 启动服务
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if not settings.DEBUG else "debug",
            access_log=True,
        )
        
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
