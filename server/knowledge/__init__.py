
import os
from .graphbase import GraphDatabase
from dotenv import load_dotenv

load_dotenv("src/.env", override=True)

from concurrent.futures import ThreadPoolExecutor  # noqa: E402
executor = ThreadPoolExecutor()

from core.config import settings  # noqa: E402
config = settings

# 导入知识库相关模块
from .kb_factory import KnowledgeBaseFactory  # noqa: E402
from .kb_manager import KnowledgeBaseManager  # noqa: E402
from .lightrag_kb import LightRagKB  # noqa: E402

# 注册知识库类型
KnowledgeBaseFactory.register("lightrag", LightRagKB, {"description": "基于图检索的知识库，支持实体关系构建和复杂查询"})

# 创建知识库管理器
work_dir = os.path.join(config.save_dir, "knowledge_base_data")
knowledge_base = KnowledgeBaseManager(work_dir)

__all__ = ["GraphDatabase"]

graph_base = GraphDatabase()
