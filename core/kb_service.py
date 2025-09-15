"""
知识库服务核心逻辑
"""
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from knowledge.kb_manager import KnowledgeBaseManager as KBManager
from knowledge.lightrag_kb import LightRagKB
from core.config import settings, get_openai_config, get_embedding_config, get_reranker_config
from core.exceptions import KnowledgeBaseError, RAGError
from schemas.requests import ChatRecommendationRequest, ProductFilter
from schemas.responses import ProductRecommendation, Evidence, ChatRecommendationResponse
from utils.logging_config import logger


class KBService:
    """知识库服务"""
    
    def __init__(self):
        """初始化知识库服务"""
        self.work_dir = settings.WORK_DIR
        os.makedirs(self.work_dir, exist_ok=True)
        
        # 初始化知识库管理器
        self.kb_manager = KBManager(self.work_dir)
        
        # 默认知识库ID
        self.default_db_id = "default"
        
        logger.info("知识库服务初始化完成")
    
    async def get_or_create_default_db(self) -> str:
        """获取或创建默认知识库"""
        try:
            # 检查数据库是否存在
            databases = self.kb_manager.get_databases()
            if self.default_db_id not in databases:
                # 创建新数据库
                await self._create_default_database()
            
            return self.default_db_id
            
        except Exception as e:
            logger.error(f"获取/创建默认数据库失败: {e}")
            raise KnowledgeBaseError(f"默认数据库初始化失败: {str(e)}")
    
    async def _create_default_database(self):
        """创建默认数据库"""
        try:
            # 获取配置
            openai_config = get_openai_config()
            embedding_config = get_embedding_config()
            
            # 创建 LightRAG 知识库
            kb = self.kb_manager.create_kb(
                db_id=self.default_db_id,
                kb_type="lightrag",
                embedding_config=embedding_config,
                llm_config=openai_config
            )
            
            logger.info(f"创建默认数据库 {self.default_db_id}")
            
        except Exception as e:
            logger.error(f"创建默认数据库失败: {e}")
            raise KnowledgeBaseError(f"创建默认数据库失败: {str(e)}")
    
    async def chat_recommendation(self, request: ChatRecommendationRequest) -> ChatRecommendationResponse:
        """聊天商品推荐"""
        trace_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = int(datetime.now().timestamp())
        
        try:
            # 获取默认数据库
            db_id = await self.get_or_create_default_db()
            
            # 构建查询上下文
            query_context = self._build_query_context(request)
            
            # 执行RAG查询
            rag_result = await self._execute_rag_query(db_id, query_context, request.top_k)
            
            # 解析结果为商品推荐
            products, evidence = self._parse_rag_result(rag_result, request.filters)
            
            # 生成回复
            reply = self._generate_reply(products, request.message)
            
            logger.info(f"推荐查询完成: {trace_id}, 返回 {len(products)} 个商品")
            
            return ChatRecommendationResponse(
                reply=reply,
                products=products[:request.top_k],
                evidence=evidence,
                trace_id=trace_id,
                session_id=request.session_id,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"推荐查询失败: {e}")
            return ChatRecommendationResponse(
                success=False,
                reply=f"抱歉，查询时遇到了问题：{str(e)}",
                products=[],
                evidence=[],
                trace_id=trace_id,
                session_id=request.session_id,
                timestamp=timestamp
            )
    
    def _build_query_context(self, request: ChatRecommendationRequest) -> str:
        """构建查询上下文"""
        context_parts = []
        
        # 添加历史对话上下文
        if request.history:
            context_parts.append("对话历史：")
            for msg in request.history[-5:]:  # 只保留最近5轮对话
                context_parts.append(f"{msg.role}: {msg.content}")
        
        # 添加当前查询
        context_parts.append(f"用户查询: {request.message}")
        
        # 添加筛选条件
        if request.filters:
            filter_parts = []
            if request.filters.price:
                filter_parts.append(f"价格区间: {request.filters.price[0]}-{request.filters.price[1]}元")
            if request.filters.brand:
                filter_parts.append(f"品牌: {', '.join(request.filters.brand)}")
            if request.filters.category:
                filter_parts.append(f"类目: {', '.join(request.filters.category)}")
            if request.filters.tags:
                filter_parts.append(f"标签: {', '.join(request.filters.tags)}")
            
            if filter_parts:
                context_parts.append("筛选条件: " + "; ".join(filter_parts))
        
        return "\n".join(context_parts)
    
    async def _execute_rag_query(self, db_id: str, query: str, top_k: int) -> Dict[str, Any]:
        """执行RAG查询"""
        try:
            # 获取知识库实例
            kb = self.kb_manager.get_kb(db_id)
            if not isinstance(kb, LightRagKB):
                raise RAGError("不支持的知识库类型")
            
            # 执行查询
            result = await kb.aquery(
                query=query,
                param={"mode": "mix", "top_k": top_k}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            raise RAGError(f"RAG查询失败: {str(e)}")
    
    def _parse_rag_result(self, rag_result: Dict[str, Any], filters: Optional[ProductFilter]) -> tuple[List[ProductRecommendation], List[Evidence]]:
        """解析RAG结果为商品推荐"""
        products = []
        evidence = []
        
        try:
            # 从RAG结果中提取商品信息（这里需要根据实际数据格式调整）
            if "context" in rag_result:
                contexts = rag_result["context"]
                if isinstance(contexts, list):
                    for i, ctx in enumerate(contexts):
                        # 尝试解析商品信息
                        product = self._extract_product_from_context(ctx, i)
                        if product and self._filter_product(product, filters):
                            products.append(product)
                        
                        # 添加证据
                        if isinstance(ctx, dict):
                            evidence.append(Evidence(
                                type="doc",
                                file_id=ctx.get("file_id", f"ctx_{i}"),
                                snippet=str(ctx)[:200] + "..." if len(str(ctx)) > 200 else str(ctx)
                            ))
            
            # 按分数排序
            products.sort(key=lambda x: x.score, reverse=True)
            
        except Exception as e:
            logger.error(f"解析RAG结果失败: {e}")
        
        return products, evidence
    
    def _extract_product_from_context(self, context: Any, index: int) -> Optional[ProductRecommendation]:
        """从上下文中提取商品信息"""
        try:
            # 这里是简化的解析逻辑，实际需要根据数据格式调整
            if isinstance(context, dict):
                return ProductRecommendation(
                    sku=context.get("sku", f"product_{index}"),
                    title=context.get("title", "商品标题"),
                    price=float(context.get("price", 0)),
                    currency=context.get("currency", "CNY"),
                    image_url=context.get("image_url"),
                    product_url=context.get("product_url"),
                    brand=context.get("brand"),
                    category=context.get("category"),
                    rating=float(context.get("rating", 0)) if context.get("rating") else None,
                    stock=int(context.get("stock", 0)) if context.get("stock") else None,
                    reasons=context.get("reasons", []),
                    score=float(context.get("score", 0.5)),
                    tags=context.get("tags", [])
                )
            elif isinstance(context, str):
                # 简单的文本解析示例
                return ProductRecommendation(
                    sku=f"product_{index}",
                    title=context[:50] if len(context) > 50 else context,
                    price=99.0,  # 默认价格
                    score=0.5,
                    reasons=[context[:100] if len(context) > 100 else context]
                )
        except Exception as e:
            logger.error(f"提取商品信息失败: {e}")
        
        return None
    
    def _filter_product(self, product: ProductRecommendation, filters: Optional[ProductFilter]) -> bool:
        """根据筛选条件过滤商品"""
        if not filters:
            return True
        
        # 价格筛选
        if filters.price and len(filters.price) == 2:
            if not (filters.price[0] <= product.price <= filters.price[1]):
                return False
        
        # 品牌筛选
        if filters.brand and product.brand:
            if product.brand not in filters.brand:
                return False
        
        # 类目筛选
        if filters.category and product.category:
            if product.category not in filters.category:
                return False
        
        # 标签筛选
        if filters.tags:
            if not any(tag in product.tags for tag in filters.tags):
                return False
        
        return True
    
    def _generate_reply(self, products: List[ProductRecommendation], query: str) -> str:
        """生成回复文本"""
        if not products:
            return "抱歉，没有找到符合您要求的商品。请尝试调整搜索条件或咨询客服。"
        
        if len(products) == 1:
            return f"为您推荐这款商品：{products[0].title}，价格 ¥{products[0].price}"
        else:
            return f"为您找到 {len(products)} 款相关商品，按相关度排序展示："
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 清理知识库管理器
            if hasattr(self, 'kb_manager'):
                # 这里可以添加具体的清理逻辑
                pass
            logger.info("知识库服务清理完成")
        except Exception as e:
            logger.error(f"知识库服务清理失败: {e}")
    
    def get_database_info(self, db_id: str) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            return self.kb_manager.get_database_info(db_id)
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            raise KnowledgeBaseError(f"获取数据库信息失败: {str(e)}")
    
    def list_databases(self) -> List[Dict[str, Any]]:
        """列出数据库"""
        try:
            databases = self.kb_manager.get_databases()
            result = []
            
            for db_id, db_info in databases.items():
                result.append({
                    "id": db_id,
                    "name": db_info.get("name", db_id),
                    "status": "active",  # 简化状态
                    "created_at": int(datetime.now().timestamp()),
                    "updated_at": int(datetime.now().timestamp())
                })
            
            return result
            
        except Exception as e:
            logger.error(f"列出数据库失败: {e}")
            raise KnowledgeBaseError(f"列出数据库失败: {str(e)}")
