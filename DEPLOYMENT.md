# EmbedAI Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署完整的 EmbedAI 系统。

## 🏗️ 系统架构

EmbedAI 系统包含以下组件：

### 应用服务
- **后端 API** (端口 10100): FastAPI 后端服务，提供 RAG 推荐 API
- **前端管理后台** (端口 10101): React 管理界面，用于系统管理和配置
- **前端 SDK 演示** (端口 10102): React SDK 演示页面，展示聊天窗组件

### 数据存储服务
- **Milvus** (端口 10103): 向量数据库，存储文档 embedding
- **Neo4j** (端口 10104/10105): 图数据库，存储实体关系
- **MinIO** (端口 10106/10107): 对象存储，存储文件和模型数据
- **etcd**: Milvus 的元数据存储

## 📋 部署前准备

### 系统要求
- Docker 20.10+ 
- Docker Compose 2.0+ (或 docker-compose 1.27+)
- 8GB+ 内存推荐
- 50GB+ 磁盘空间

### 端口要求
确保以下端口未被占用：
- 10100-10107 (应用和数据库服务)

## 🚀 快速部署

### 1. 获取代码
```bash
git clone <repository-url>
cd EmbedAI-only
```

### 2. 配置环境变量
```bash
# 复制环境变量模版
cp .env.example .env

# 编辑配置文件，必须填入 SiliconFlow API Key
nano .env
```

**重要配置项：**
```bash
# 必填：SiliconFlow API 密钥
SILICONFLOW_API_KEY=your_api_key_here

# 可选：用户ID对齐（Linux/Mac）
APP_UID=1000
APP_GID=1000
```

### 3. 一键部署
```bash
# 使用部署脚本（推荐）
./deploy.sh

# 或手动执行
docker-compose up -d --build
```

### 4. 验证部署
部署完成后，访问以下地址验证：

- 📊 **管理后台**: http://localhost:10101
- 🛠️ **SDK 演示**: http://localhost:10102  
- 🔧 **后端 API**: http://localhost:10100/docs
- 💾 **MinIO 控制台**: http://localhost:10107 (minioadmin/minioadmin123)
- 🕸️ **Neo4j 浏览器**: http://localhost:10104 (neo4j/embedai123)

## 📝 部署脚本使用说明

部署脚本 `deploy.sh` 提供了便捷的管理命令：

```bash
# 完整部署流程
./deploy.sh

# 仅构建镜像
./deploy.sh build

# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs [service_name]

# 检查服务状态
./deploy.sh status

# 清理所有数据（谨慎使用）
./deploy.sh clean

# 显示帮助
./deploy.sh help
```

## 🔧 手动部署步骤

如果不使用部署脚本，可以按以下步骤手动部署：

### 1. 构建镜像
```bash
# 构建所有服务镜像
docker-compose build

# 或分别构建
docker-compose build backend
docker-compose build frontend_admin  
docker-compose build frontend_sdk
```

### 2. 启动数据库服务
```bash
# 启动基础服务
docker-compose up -d etcd minio neo4j

# 等待服务启动
sleep 30

# 启动 Milvus
docker-compose up -d milvus

# 等待 Milvus 启动
sleep 60
```

### 3. 启动应用服务
```bash
# 启动应用服务
docker-compose up -d backend frontend_admin frontend_sdk
```

### 4. 检查服务状态
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🔍 故障排除

### 常见问题

#### 1. 端口冲突
**错误**: `bind: address already in use`

**解决**:
```bash
# 检查端口占用
lsof -i :10100-10107

# 停止占用进程或修改 docker-compose.yml 中的端口映射
```

#### 2. 内存不足
**错误**: `cannot allocate memory`

**解决**:
- 增加 Docker 内存限制 (Docker Desktop)
- 关闭不必要的应用释放内存
- 考虑减少并发服务数量

#### 3. Milvus 启动失败
**错误**: `milvus etcd connection failed`

**解决**:
```bash
# 重启 etcd 服务
docker-compose restart etcd

# 等待后重启 Milvus
sleep 10
docker-compose restart milvus
```

#### 4. 构建镜像失败
**错误**: `failed to solve: process "/bin/sh -c pip install..."`

**解决**:
```bash
docker-compose build --no-cache

# 或编辑 .env 文件添加代理配置
```

#### 5. 权限问题
**错误**: `permission denied`

**解决**:
```bash
# 检查文件权限
ls -la deploy.sh

# 添加执行权限
chmod +x deploy.sh

# 对于数据卷权限问题，设置正确的 UID/GID
echo "APP_UID=$(id -u)" >> .env
echo "APP_GID=$(id -g)" >> .env
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend_admin
docker-compose logs -f milvus
docker-compose logs -f neo4j

# 查看最近50行日志
docker-compose logs --tail=50 backend
```

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:10100/health  # 后端
curl http://localhost:10101/health  # 管理前端
curl http://localhost:10102/health  # SDK前端

# 检查数据库连接
docker-compose exec backend python -c "
from core.database import test_connections
test_connections()
"
```

## 🔄 更新和维护

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署  
./deploy.sh stop
./deploy.sh build
./deploy.sh start
```

### 数据备份
```bash
# 导出数据卷
docker run --rm -v embedai-only_neo4j_data:/data -v $(pwd):/backup alpine tar czf /backup/neo4j_backup.tar.gz -C /data .
docker run --rm -v embedai-only_milvus_data:/data -v $(pwd):/backup alpine tar czf /backup/milvus_backup.tar.gz -C /data .

# 恢复数据
docker run --rm -v embedai-only_neo4j_data:/data -v $(pwd):/backup alpine tar xzf /backup/neo4j_backup.tar.gz -C /data
```

### 清理和重置
```bash
# ⚠️ 警告：这将删除所有数据！
./deploy.sh clean

# 或手动清理
docker-compose down -v --remove-orphans
docker system prune -f
```

## 🛡️ 安全配置

### 生产环境建议

1. **更改默认密码**:
   ```bash
   # Neo4j 密码
   NEO4J_AUTH=neo4j/your_secure_password
   
   # MinIO 密码  
   MINIO_ROOT_PASSWORD=your_secure_password
   ```

2. **配置 HTTPS**:
   - 使用 Nginx 反向代理
   - 配置 SSL 证书
   - 更新 CORS 配置

3. **网络隔离**:
   - 只暴露必要端口
   - 使用防火墙规则
   - 考虑 VPN 访问

4. **资源限制**:
   ```yaml
   # 在 docker-compose.yml 中添加
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 4G
   ```

## 📞 支持和帮助

### 获取帮助
- 查看日志了解错误详情
- 检查 GitHub Issues
- 参考官方文档

### 性能调优
- 调整 Milvus 配置 (`milvus/milvus.yaml`)
- 优化 Neo4j 内存设置
- 配置适当的资源限制

---

*最后更新: 2024年12月*
