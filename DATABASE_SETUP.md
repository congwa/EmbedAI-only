# EmbedAI 数据库本地部署指南

本项目提供了一套完整的脚本来在本地 Docker 环境中部署所有需要的数据库服务。

## 📋 包含的数据库服务

- **Milvus** (v2.4.15) - 向量数据库，用于存储和查询文档向量
- **Neo4j** (v5.26.0) - 图数据库，用于存储知识图谱
- **MinIO** (RELEASE.2024-12-18T13-15-44Z) - 对象存储，用于存储文件
- **etcd** (v3.5.15) - 协调服务，Milvus 的依赖服务

## 🚀 快速开始

### 1. 启动数据库服务

```bash
./start-databases.sh
```

该脚本会：
- 检查 Docker 环境
- 启动所有数据库服务
- 等待服务健康检查完成
- 显示服务访问信息

### 2. 检查服务状态

```bash
./check-databases.sh
```

查看详细日志：
```bash
./check-databases.sh --logs
```

### 3. 停止数据库服务

```bash
./stop-databases.sh
```

停止服务并清理资源：
```bash
./stop-databases.sh --cleanup
```

## 🔌 服务访问信息

| 服务 | 访问地址 | 用户名/密码 | 用途 |
|------|----------|-------------|------|
| Milvus | localhost:10103 | - | 向量数据库 gRPC 端点 |
| Neo4j (HTTP) | http://localhost:10104 | neo4j/embedai123 | 图数据库 Web 界面 |
| Neo4j (Bolt) | bolt://localhost:10105 | neo4j/embedai123 | 图数据库连接端点 |
| MinIO (API) | http://localhost:10106 | minioadmin/minioadmin123 | 对象存储 API |
| MinIO (Console) | http://localhost:10107 | minioadmin/minioadmin123 | 对象存储管理界面 |

## 📁 文件说明

- `docker-compose-db.yml` - 数据库服务的 Docker Compose 配置
- `start-databases.sh` - 启动数据库服务的脚本
- `stop-databases.sh` - 停止数据库服务的脚本
- `check-databases.sh` - 检查数据库服务状态的脚本

## 🔧 前置要求

- Docker 已安装并运行
- Docker Compose 已安装
- 端口 10103-10107 未被其他服务占用

## 💾 数据持久化

所有数据库数据都通过 Docker 卷进行持久化存储：

- `milvus_data` - Milvus 数据
- `etcd_data` - etcd 数据
- `neo4j_data` - Neo4j 数据库文件
- `neo4j_logs` - Neo4j 日志
- `minio_data` - MinIO 对象存储数据

## 🛠️ 常见操作

### 重启所有服务
```bash
./stop-databases.sh && ./start-databases.sh
```

### 查看服务日志
```bash
# 查看所有服务状态和最近日志
./check-databases.sh --logs

# 查看特定服务日志
docker logs embedai_milvus
docker logs embedai_neo4j
docker logs embedai_minio
```

### 清理数据（谨慎操作）
```bash
# 停止服务并清理所有数据
./stop-databases.sh --cleanup
```

## 🔍 故障排除

### 服务启动失败
1. 检查 Docker 是否正常运行：`docker info`
2. 检查端口是否被占用：`lsof -i :10103-10107`
3. 查看服务日志：`./check-databases.sh --logs`

### 健康检查超时
- Milvus 启动需要较长时间，请耐心等待
- 可以通过 `./check-databases.sh` 持续监控服务状态

### 连接问题
- 确保防火墙没有阻止相关端口
- 检查服务是否完全启动：`./check-databases.sh`

## 📝 注意事项

1. **首次启动**：首次启动可能需要下载镜像，耗时较长
2. **资源要求**：确保系统有足够的内存和磁盘空间
3. **端口冲突**：如果端口被占用，可以修改 `docker-compose-db.yml` 中的端口映射
4. **数据备份**：重要数据请定期备份 Docker 卷

## 🔗 相关链接

- [Milvus 官方文档](https://milvus.io/docs)
- [Neo4j 官方文档](https://neo4j.com/docs/)
- [MinIO 官方文档](https://min.io/docs/minio/linux/index.html)

---

如果遇到问题，请检查日志并参考相关文档，或联系项目维护者。
