# 1. 核心功能规划 (Core Feature Plan)

本规划书面向智荐 AI（IntelliRecs AI）项目组的产品与研发同学，聚焦于“可通过 JS 脚本轻松集成的 RAG 商品推荐聊天机器人”。在撰写前，我已通读现有服务端样例代码，重点参考了以下模块，以确保技术方案具备可行性并与当前代码基础一致：

- 知识库与 RAG 编排相关：
  - [server/knowledge/lightrag_kb.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/lightrag_kb.py:0:0-0:0)（集成 LightRAG，Milvus/Neo4j 存储，OpenAI 兼容适配）
  - [server/knowledge/indexing.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/indexing.py:0:0-0:0)（基于 LangChain 的文档解析与切片）
  - [server/knowledge/kb_utils.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_utils.py:0:0-0:0)（默认 embedding 配置装配）
  - [server/knowledge/graphbase.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/graphbase.py:0:0-0:0)（Neo4j 向量索引、实体查询）
  - [server/knowledge/kb_manager.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_manager.py:0:0-0:0)（多知识库类型统一管理）
- 模型相关：
  - [server/models/chat_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/chat_model.py:0:0-0:0)（OpenAI 兼容 API 客户端封装）
  - [server/models/embedding.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/embedding.py:0:0-0:0)（多种 embedding 适配，包括 OpenAI 兼容/其他）
  - [server/models/rerank_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/rerank_model.py:0:0-0:0)（在线重排适配器，面向 reranker API）
- 工具与基础能力：
  - [server/utils/minio_utils.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/utils/minio_utils.py:0:0-0:0)（MinIO 文件服务封装）
  - [server/utils/logging_config.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/utils/logging_config.py:0:0-0:0)（统一日志）
  - [server/pyproject.toml](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/pyproject.toml:0:0-0:0)（FastAPI、Uvicorn、Prometheus、httpx 等依赖已具备）

以上现有能力为我们实现“RAG 驱动的电商推荐聊天机器人”提供了扎实基础：RAG 流程由 LightRAG 编排（[lightrag_kb.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/lightrag_kb.py:0:0-0:0)），文档/CSV 解析与分块由 LangChain 完成（[indexing.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/indexing.py:0:0-0:0)），OpenAI 兼容模型调用（面向硅基流动 SiliconFlow）能力已具备（[chat_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/chat_model.py:0:0-0:0) 与 LightRAG 的 openai 适配）。下面进入详细规划。

---

## 1.1. AI 聊天窗 SDK (AI Chat Widget SDK)

- 集成方式

  - 最终以一个托管于 CDN 的单文件 JS 链接供客户网站直接引入，完成“零后端/零打包”的快速集成：
    - 客户只需在任意电商网站页面 `<head>` 或 `</body>` 前插入：
      ```
      <script src="https://cdn.intellirecs.ai/sdk/latest/intellirecs-ai.js" defer></script>
      <script>
        window.IntelliRecsAI.init({
          tenantId: "YOUR_TENANT_ID",
          apiBase: "https://api.intellirecs.ai",
          theme: { primary: "#2563eb", corner: "16px" },
          welcome: "你好，我是你的智能导购助手。想找点什么？",
          lang: "zh-CN",
          productLinkMode: "new_tab",
          enableHistory: true
        });
      </script>
      ```
  - SDK 打包建议
    - 使用 Vite lib 模式或 Rollup，输出 UMD + ESM 两种格式，默认挂载 `window.IntelliRecsAI`。
    - 内部以 React + Tailwind CSS 构建 UI（`frontend_sdk/` 目录已有前端脚手架，可复用）。
    - 通过 Shadow DOM 或样式前缀防止污染宿主站点样式。
    - 提供 TypeScript 类型定义，便于 B 端工程师二次开发。

- 用户界面（UI/UX）

  - 形态：右下角悬浮按钮 + 展开后侧滑/弹层聊天窗。
  - 技术栈：React + Tailwind CSS。注重轻量、响应式、无障碍（a11y）。
  - 结构与组件
    - 浮动入口按钮（显示品牌/自定义图标，未读气泡数）
    - 聊天窗头部（品牌 Logo、欢迎语、主题色、在线状态）
    - 对话区（支持多轮对话、流式生成、Markdown 渲染）
    - 商品卡片列表（卡片包含图片、名称、价格、评分、促销标签、到手价/优惠、库存状态、跳转链接）
    - 底部输入区（多行输入、快捷问题 Suggestion、发送/重试、清空会话）
  - 可定制项
    - 主题色、圆角、字体、Logo、欢迎语、默认推荐提示、默认入口问候气泡
    - 商品卡片样式（密度/尺寸）、打开方式（当前页/新开页）、链接打点
    - 国际化：内置 `zh-CN/en-US`，支持注入自定义文案包

- 核心交互

  - 用户自然语言输入需求（如“帮我找一款适合户外运动的防水蓝牙音箱”）
  - SDK 通过 HTTPS 调用后端 FastAPI `/chat/recommendations` 接口
  - 后端执行 RAG 检索 + 重排 + 生成，返回结构化推荐结果 + 参考依据
  - SDK 将回复以“文本 + 商品卡片”的形式展示；点击卡片跳转商品页；可持续多轮追问与筛选
  - 历史记录：可选择仅在本地 `localStorage` 保存，或启用云端会话同步（需鉴权）

- 功能点清单
  - 多轮对话与上下文保持（会话 ID，SDK 本地缓存，可选云端会话恢复）
  - 商品卡片展示（图片、标题、副标题、价格、库存/配送、评分、促销、跳转链接）
  - 商品筛选交互（价格区间、品牌、类目、颜色/尺寸等属性提取与追问）
  - 引用与透明度：可展开“来自资料/索引来源”（RAG 参考证据）以提升可解释性
  - 错误提示与重试机制、网络断线提示
  - 键入建议（热门搜索/示例问题）
  - 事件回调与数据打点
    - `onOpen/onClose/onSend/onReceive/onProductClick/onError`
    - 埋点字段包含 tenantId、sessionId、queryId、商品 SKU、点击来源等
  - 安全与合规
    - 域名白名单，origin 校验；CSP 建议；接口签名或短期 token 注入
    - 隐私遮蔽开关（如不回传 PII）；GDPR/CCPA 选项说明

---

## 2.2. 服务端 (Server-side)

- 核心逻辑

  - 作为系统“大脑”，接收 SDK 请求，完成“查询理解 → RAG 检索 → 重排/生成 → 结构化推荐输出”全链路。
  - 技术栈
    - 框架：FastAPI（[server/pyproject.toml](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/pyproject.toml:0:0-0:0) 中已包含 `fastapi`/`uvicorn`）
    - 存储与组件：LightRAG（Milvus 向量库 + Neo4j 图谱）、MinIO（图片/CDN 文件）
    - 日志与指标：`loguru` 统一日志（[utils/logging_config.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/utils/logging_config.py:0:0-0:0)），`prometheus-client` 暴露指标
    - 安全与限流：`slowapi` 支持限流；Pydantic 校验与签名鉴权结合

- RAG 流程（基于 LightRAG）

  - 编排说明
    - [server/knowledge/lightrag_kb.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/lightrag_kb.py:0:0-0:0) 使用 `LightRAG` 管理工作区与检索流程，存储后端为 Milvus（向量）与 Neo4j（图谱）。
    - 支持“mix 模式”查询（向量 + 图谱融合），并可选只返回 context 供生成模型参考。
    - 内置 [aquery](cci:1://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_manager.py:195:4-198:68) 接口采用 `QueryParam` 控制检索参数（top_k、mode 等）。
  - 文档/商品数据接入与切片
    - [server/knowledge/indexing.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/indexing.py:0:0-0:0) 基于 LangChain 的多格式加载器：CSV、Markdown、HTML、PDF（可选 OCR）、DOCX 等。
    - CSV 文件适配：将每行商品记录转为 Markdown 片段（或结构化 JSON 再序列化），字段建议：
      - `sku`, `title`, `brand`, `category`, `attrs`（键值属性）、`price`, `currency`, `image_url`, `product_url`, `stock`, `rating`, `tags`
    - 切片策略：`RecursiveCharacterTextSplitter` 或 `MarkdownTextSplitter`（[server/knowledge/kb_utils.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_utils.py:0:0-0:0)）智能分段，保留 `chunk_idx` 与 `file_id`/`source` 作为元数据。
  - 向量化与索引
    - Embedding：默认使用 SiliconFlow 提供的 OpenAI 兼容 embedding 服务（如 `BAAI/bge-m3`），由 [get_embedding_config()](cci:1://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_utils.py:106:0-138:22) 提供参数（模型名、base_url、api_key、维度）。
      - 参考 [server/knowledge/kb_utils.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_utils.py:0:0-0:0) 与 [server/models/embedding.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/embedding.py:0:0-0:0)
    - 存储：Milvus 作为向量存储，Neo4j 存图谱与向量索引（[server/knowledge/graphbase.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/graphbase.py:0:0-0:0) 中也提供 Neo4j 向量索引能力与图谱查询）
  - 候选召回与重排
    - 先由 LightRAG 进行候选召回（向量/图谱融合）。
    - 结合在线 Reranker 提升相关性（参考 [server/models/rerank_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/rerank_model.py:0:0-0:0)，支持对接 SiliconFlow 的 reranker API，如 `BAAI/bge-reranker-large` 或同类）。
  - 生成与结构化推荐
    - 生成调用：通过 OpenAI 兼容模式（见“模型与 API”）进行自然语言生成，合成最终回答与商品推荐语。
    - 输出结构化 JSON（推荐商品列表 + 推荐理由 + 参考证据），便于 SDK 渲染商品卡片与“参考资料”折叠面板。

- 无 Redis/Celery 的文档嵌入状态管理与触发机制

  - 状态模型
    - 基于 `KnowledgeBase.files_meta` 记录每个文件的处理状态与元信息，关键状态：`processing`、`done`、`failed`，以及用于异常自愈的 `error`。
    - 使用类级队列 `KnowledgeBase._processing_files` 与互斥锁 `_processing_lock` 跟踪当前进行中的任务，防止并发竞态。
    - 持久化通过 `KnowledgeBase._save_metadata()` 将 `{"databases", "files", "kb_type", "updated_at"}` 写入 `work_dir/metadata_{kb_type}.json`，重启后状态可恢复。

  - 触发流程（以 `LightRagKB.add_content()` 为例）
    - 准备元数据：`prepare_item_metadata()` 生成 `file_id`、路径、来源等；写入 `self.files_meta` 后立即 `_save_metadata()`。
    - 入队：调用 `KnowledgeBase._add_to_processing_queue(file_id)` 将任务标记为进行中。
    - 处理：文件走 `process_file_to_markdown()`，URL 走 `process_url_to_markdown()`；随后调用 `rag.ainsert(input=markdown, ids=file_id, file_paths=item_path)` 完成嵌入与索引。
    - 完成/失败：成功时将 `status=done`；异常时将 `status=failed` 并写入 `error`；二者均 `_save_metadata()` 并最终 `_remove_from_processing_queue(file_id)`。

  - 状态修复与查询
    - 读取数据库信息时，`KnowledgeBase.get_database_info()` 会调用 `_check_and_fix_processing_status(db_id)`：若某文件 `status=processing` 但不在队列中，则标记为 `error` 并记录错误原因。
    - 管理端可通过 `get_database_info()` 查看文件列表与状态；`LightRagKB.get_file_info()` 用于查看该文件切片（chunks）详情。

  - 触发方式（无外部队列）
    - API 层采用 FastAPI `BackgroundTasks` 或 `asyncio.create_task` 将 `add_content()` 放入进程内后台执行；通过信号量/协程池限制并发，避免压垮外部依赖（Milvus/Neo4j/Embedding API）。
    - 失败重试由管理端提供“重新索引”操作触发，利用幂等键 `file_id` 避免重复入库。

  - 优势与注意事项
    - 无需部署 Redis/Celery，显著减少运维复杂度；重启后通过自愈逻辑避免“无限进行中”。
    - 横向扩容时建议按租户或 DB 进行请求分片；同一 `file_id` 在上层保持幂等，避免并发双写。

- 模型与 API

  - 语言模型（LLM）
    - 通过 LangChain 的 OpenAI 兼容模式接入硅基流动（SiliconFlow）API，使用其 API Key 认证。
    - 在现有代码中，LightRAG 路径使用其内置 OpenAI 适配器（`lightrag.llm.openai.openai_complete_if_cache` 与 `openai_embed`），而自研通道可使用 [server/models/chat_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/chat_model.py:0:0-0:0) 的 [OpenAIBase](cci:2://file:///Users/cong/code/my/EmbedAI-only/server/models/chat_model.py:7:0-58:21) 对接 SiliconFlow。
    - 环境变量建议：
      - `LIGHTRAG_LLM_PROVIDER=siliconflow`
      - `LIGHTRAG_LLM_NAME=zai-org/GLM-4.5-Air`（可替换）
      - `OPENAI_API_KEY=...`（SiliconFlow 的 Key）
      - `OPENAI_BASE_URL=https://api.siliconflow.cn/v1`
  - Embedding 模型
    - 默认 `BAAI/bge-m3`（或业务评估后选择更适合商品场景的中文/多语 embedding）。
    - 通过 [server/models/embedding.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/embedding.py:0:0-0:0) 的 [OtherEmbedding](cci:2://file:///Users/cong/code/my/EmbedAI-only/server/models/embedding.py:142:0-175:78) 以 OpenAI 兼容格式调用 SiliconFlow embeddings 接口。
  - Reranker 模型
    - 接入 SiliconFlow 提供的 reranker（见 [rerank_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/rerank_model.py:0:0-0:0) 负载协议），作为精排以提高商品 Top-N 命中率与一致性。

- API 设计（建议）

  - Chat 推荐
    - `POST /api/chat/recommendations`
    - 请求：
      ```json
      {
        "tenantId": "t_xxx",
        "sessionId": "s_xxx",
        "message": "帮我找一款适合户外运动的防水蓝牙音箱",
        "history": [
          { "role": "user", "content": "预算 500 左右" },
          { "role": "assistant", "content": "好的，还有颜色偏好吗？" }
        ],
        "filters": { "price": [199, 599], "brand": ["JBL", "索尼"] },
        "topK": 10,
        "lang": "zh-CN"
      }
      ```
    - 响应（示例）：
      ```json
      {
        "reply": "为你挑选了 3 款适合户外且支持防水的音箱：",
        "products": [
          {
            "sku": "A123",
            "title": "JBL Clip 4",
            "price": 399,
            "currency": "CNY",
            "image_url": "https://cdn.xxx/jbl-clip4.jpg",
            "product_url": "https://shop.example.com/p/A123",
            "reasons": ["IP67 防尘防水", "便携挂扣", "续航 10h"],
            "score": 0.92
          }
        ],
        "evidence": [
          { "type": "doc", "file_id": "file_abc", "snippet": "..." },
          {
            "type": "url",
            "href": "https://brand.com/jbl-clip4",
            "snippet": "..."
          }
        ],
        "trace_id": "q_20250910_xxx"
      }
      ```
  - 管理端/知识库
    - `POST /api/admin/kb/databases` 创建/配置数据库（含 embedding/LLM 选择、语言、chunk 策略）
    - `POST /api/admin/kb/upload` 上传 CSV/文档
    - `POST /api/admin/kb/index` 触发构建（进程内异步执行，无需 Redis/Celery）
    - `GET /api/admin/kb/databases/:id` 查看 KB 状态、文档列表、chunk 数量
    - `DELETE /api/admin/kb/databases/:id` 删除（清理 Milvus + Neo4j，参考 [lightrag_kb.py::delete_database](cci:1://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_manager.py:174:4-188:46)）
  - 分析与日志
    - `GET /api/admin/analytics/conversations` 会话与热门问题
    - `GET /metrics` Prometheus 指标（QPS、P95、召回/重排统计、命中率等）

- 性能与稳定性

  - 限流与缓存：`slowapi` 配额控制；对热问题结果进行 TTL 缓存；
  - 观测性：`loguru` 统一日志，`prometheus-client` 指标 + Grafana 看板。
  - 多租户隔离：每个 `tenantId` 映射到独立 LightRAG 工作区与索引前缀（`db_id` 级别隔离，参考 [kb_manager.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_manager.py:0:0-0:0) 的多知识库管理）。

- 安全
  - SDK → API：短期签名（HMAC）或 JWT，服务端校验域名（Origin/CORS 白名单、Referer 检查）。
  - API Key/密钥保管：仅服务端持有；在容器/Secret Manager 中注入。
  - PII/行为数据：最小化采集，可配置匿名化与脱敏。

---

## 2.3. 管理端 (Admin Panel)

- 目标用户

  - 电商网站运营/商品经理/站点管理员，用于知识库与对话运营。

- 核心功能

  - 知识库管理
    - 创建/删除数据库（每个站点/类目一个 DB，独立检索域）
    - 上传/同步商品数据（CSV/Excel），可配置字段映射（列名 → 标准字段）
    - 触发索引构建与状态跟踪（进行中/完成/失败），失败可查看日志
  - 对话分析
    - 用户与 AI 的交互日志检索、导出
    - 热门问题、无解问题、推荐点击率、SKU 曝光/点击漏斗
    - 版本与 A/B 实验对比（召回/重排效果）
  - 配置与定制
    - 聊天窗主题（色彩、圆角、Logo）、欢迎语、默认建议问题
    - 推荐策略开关（是否启用 reranker、topK、语言等）
    - 白名单域名、限流策略、埋点配置

- 技术栈
  - 前端：Vite + React + TypeScript
  - UI 组件库：shadcn/ui（按需安装组件，命令：`pnpm dlx shadcn@latest add <component-name>`）
  - 路由：`@tanstack/react-router`
  - 表格与上传：推荐 `@tanstack/react-table` + 表单校验 + 大文件分片上传
  - 后端：复用 FastAPI 服务端 API

---

# 3. 技术架构与部署策略 (Technical Architecture & Deployment Strategy)

- 参考架构图（Mermaid，建议用于后续 README/设计评审）

```mermaid
flowchart LR
  subgraph Client Site
    A[JS SDK - React Widget] -- HTTPS --> B(API Gateway/FastAPI)
  end

  subgraph Backend
    B -- Chat/Recommend --> Svc[FastAPI App]
    Svc -- RAG Query --> L[LightRAG]
    L -- Vectors --> M[(Milvus)]
    L -- Graph --> N[(Neo4j)]
    Svc -- Embeddings/Reranker/LLM --> SF[SiliconFlow OpenAI-Compat API]
    Svc -- Files/Images --> O[(MinIO)]
    Svc -. background tasks .-> BG[In-Process Worker Pool]
    Svc -- Metrics --> P[Prometheus]
  end

  subgraph Admin
    UI[Admin Panel (Vite+React+shadcn/ui)]
    UI -- HTTPS --> B
  end
```

- 部署
  - 全面容器化（Docker）
    - 服务端 FastAPI：独立容器，暴露 `/api/*` 与 `/metrics`
    - 管理端 React：构建静态产物，Nginx/静态服务容器托管
    - SDK：构建并上传至 CDN（版本化），或由静态服务容器提供 `/sdk/*` 路径
    - Milvus、Neo4j、MinIO、FastAPI（内置 In-Process Worker Pool）：分容器编排
  - 编排建议
    - 单机 PoC：Docker Compose（端口映射与卷挂载）
    - 生产：Kubernetes（HPA 横向扩缩、节点级 SSD、Readiness/Liveness 探针）
  - 配置与密钥
    - `.env` 注入 SiliconFlow API Key、Milvus/Neo4j/MinIO 连接、域名白名单
    - 按租户/环境（dev/stg/prod）进行 ConfigMap/Secret 分离
  - 监控与告警
    - Prometheus + Grafana；日志接入 ELK/Opensearch；慢查询与错误报警

---

# 4. 项目里程碑 (Project Milestones)

- 第一阶段：完成服务端 RAG 核心流程开发

  - 基于 FastAPI 搭建最小可用 API：`/api/chat/recommendations`
  - 整合 LightRAG、Milvus、Neo4j；打通 CSV → 切片 → 索引 → 检索链路
  - 接入 SiliconFlow（LLM/Embedding/Reranker），完成多租户 DB 隔离
  - 指标埋点与基础观测性（Prometheus、统一日志），限流与鉴权

- 第二阶段：开发聊天窗 SDK 并完成端到端联调

  - React + Tailwind 的 Widget 组件，构建/打包为单文件 JS（兼容 UMD/ESM）
  - 多轮对话与商品卡片渲染、回调与埋点、i18n
  - 与后端联调（RAG 响应结构 → UI 渲染），灰度到 1-2 个电商站点

- 第三阶段：开发管理端

  - Vite + React + shadcn/ui + @tanstack/react-router
  - 知识库管理（DB 创建、CSV 上传、索引状态与日志）、对话分析、主题与策略配置
  - 运营功能完善与体验优化（批量导入、字段映射模板、失败重试）

---

# 附：与现有代码的适配要点

- RAG 与知识库
  - 直接复用 [server/knowledge/lightrag_kb.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/lightrag_kb.py:0:0-0:0) 及 [kb_manager.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_manager.py:0:0-0:0) 的多 DB 管理能力，将每个 `tenantId` 映射到一个 `db_id` 工作区。
  - CSV/文档解析与切片沿用 [server/knowledge/indexing.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/indexing.py:0:0-0:0) 与 [server/knowledge/kb_utils.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/kb_utils.py:0:0-0:0)，对电商字段做轻量适配。
- 模型与 API
  - OpenAI 兼容接入硅基流动：LightRAG 内部 `openai_complete_if_cache/openai_embed` 已支持；自研链路可用 [server/models/chat_model.py::OpenAIBase](cci:2://file:///Users/cong/code/my/EmbedAI-only/server/models/chat_model.py:7:0-58:21) 与 [server/models/embedding.py::OtherEmbedding](cci:2://file:///Users/cong/code/my/EmbedAI-only/server/models/embedding.py:142:0-175:78)。
  - Reranker 接口按 [server/models/rerank_model.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/models/rerank_model.py:0:0-0:0) 的负载规范对接 SiliconFlow 的 reranker 服务。
- 图谱与向量索引
  - Neo4j 与 Milvus 协同：LightRAG 原生支持；同时保留 [server/knowledge/graphbase.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/knowledge/graphbase.py:0:0-0:0) 中 Neo4j 向量索引能力以备扩展（如实体级问答/关系可视化）。
- 文件与图片
  - MinIO 统一文件服务（[server/utils/minio_utils.py](cci:7://file:///Users/cong/code/my/EmbedAI-only/server/utils/minio_utils.py:0:0-0:0)），可用于图片上传/中转或生成内容托管。
