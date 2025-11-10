
# EmbedAI 商品推荐 RAG 系统

## 归档说明

本项目已经集成了 LightRAG 知识库系统，支持配置管理知识库，支持通过 sdk 嵌入页面。 由于工作比较忙，抽不出时间维护的原因，不计划向后扩展。

## 项目简介

EmbedAI 是一个面向电商场景的 RAG（Retrieval-Augmented Generation）商品推荐聊天机器人。系统整合了知识库管理、推荐服务、管理后台以及 SDK 等多个子系统，方便团队快速构建基于企业知识库的智能推荐应用。

## 技术栈

- **后端框架**：FastAPI
- **数据库**：PostgreSQL（通过 SQLAlchemy 管理）
- **向量数据库**：Milvus / LightRAG（支持向量检索与重排）
- **模型服务**：SiliconFlow API、Ollama（可扩展至自定义 Embedding）
- **前端**：React (Admin)、SDK（待集成）
- **容器化**：Docker、docker-compose

## 已完成功能

### 1. 知识库管理
- 支持创建、查看、更新、删除知识库数据库 @api/routes/knowledge_router.py#66-321
- 提供文档上传、检索、删除等接口 @api/routes/knowledge_router.py#328-642
- 集成 LightRAG，支持默认知识库自动初始化 @core/kb_service.py#18-112

### 2. 聊天与推荐服务
- 提供登录态聊天接口，支持线程建立与上下文管理 @api/routes/chat.py#99-377
- 支持基于知识库的推荐结果生成与证据返回 @core/kb_service.py#70-112
- 暴露无认证推荐接口供 SDK 使用 @api/routes/chat.py#52-94

### 3. 管理后台
- 用户列表、操作日志查询接口 @api/routes/admin.py#63-149
- 知识库数据库 CRUD 及统计接口 @api/routes/admin.py#152-415
- 操作审计日志记录（log_operation）支撑 @api/utils/common_utils.py

### 4. 健康监控与限流
- 健康检查、就绪、存活探针接口 @api/routes/health.py#19-71
- 全局限流器 SlowAPI 集成及异常处理 @main.py#20-117
- Prometheus ASGI 中间件用于指标暴露 @main.py#78-80

### 5. 配置与异常处理
- 集中化配置管理，支持多模型配置（Embedding、Reranker） @core/config.py#94-110
- 自定义异常体系与全局异常捕获 @core/exceptions.py#13-96
- 统一日志记录配置 @utils/logging_config.py

## 快速开始

1. 克隆仓库并安装依赖
   ```bash
   poetry install
   ```
2. 配置环境变量，参考 `.env.example`
3. 启动服务
   ```bash
   poetry run uvicorn main:app --reload
   ```
4. 访问接口文档（开启 DEBUG 时）：`http://localhost:8000/api/docs`

## 目录结构

```
.
├── api/                # FastAPI 路由、模型、工具
├── core/               # 核心服务、配置、异常
├── models/             # Embedding 模型封装
├── knowledge/          # 知识库管理与工具
├── frontend_admin/     # 管理后台前端
├── frontend_sdk/       # SDK 相关代码
├── tests/              # 测试用例
├── Dockerfile
├── docker-compose.yml
└── main.py             # 应用入口
```
