#!/bin/bash

# EmbedAI 数据库服务启动脚本
# 用于在本地 Docker 环境中启动所有需要的数据库服务

set -e  # 遇到错误时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否已安装并运行
check_docker() {
    log_info "检查 Docker 环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请先启动 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 检查必要文件
check_files() {
    log_info "检查必要文件..."
    
    if [ ! -f "docker-compose-db.yml" ]; then
        log_error "找不到 docker-compose-db.yml 文件"
        exit 1
    fi
    
    if [ ! -f "milvus/milvus.yaml" ]; then
        log_warning "找不到 milvus/milvus.yaml 配置文件，将使用默认配置"
    fi
    
    log_success "文件检查完成"
}

# 清理旧容器（可选）
cleanup_old_containers() {
    log_info "清理可能存在的旧容器..."
    
    # 停止并删除相关容器
    containers=("embedai_milvus" "embedai_etcd" "embedai_neo4j" "embedai_minio")
    
    for container in "${containers[@]}"; do
        if docker ps -a --format "table {{.Names}}" | grep -q "^${container}$"; then
            log_info "停止并删除容器: $container"
            docker stop "$container" 2>/dev/null || true
            docker rm "$container" 2>/dev/null || true
        fi
    done
}

# 启动数据库服务
start_databases() {
    log_info "启动数据库服务..."
    
    # 使用 docker-compose 或 docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    log_info "使用命令: $COMPOSE_CMD -f docker-compose-db.yml up -d"
    
    # 启动服务
    $COMPOSE_CMD -f docker-compose-db.yml up -d
    
    if [ $? -eq 0 ]; then
        log_success "数据库服务启动命令执行完成"
    else
        log_error "数据库服务启动失败"
        exit 1
    fi
}

# 等待服务健康检查
wait_for_services() {
    log_info "等待服务启动并通过健康检查..."
    
    services=("embedai_etcd" "embedai_minio" "embedai_neo4j" "embedai_milvus")
    max_wait=300  # 最大等待5分钟
    elapsed=0
    
    for service in "${services[@]}"; do
        log_info "等待 $service 服务启动..."
        
        while [ $elapsed -lt $max_wait ]; do
            if docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$service" | grep -q "healthy\|Up"; then
                log_success "$service 服务已启动"
                break
            fi
            
            sleep 5
            elapsed=$((elapsed + 5))
            echo -n "."
        done
        
        if [ $elapsed -ge $max_wait ]; then
            log_warning "$service 服务启动超时，请检查服务状态"
        fi
        
        elapsed=0
    done
}

# 显示服务信息
show_service_info() {
    echo ""
    log_success "数据库服务启动完成！"
    echo ""
    echo -e "${BLUE}服务访问信息:${NC}"
    echo "┌─────────────────────────────────────────────────────────────────┐"
    echo "│ 服务名称      │ 访问地址                │ 用户名/密码            │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│ Milvus       │ localhost:10103         │ -                     │"
    echo "│ Neo4j (HTTP) │ http://localhost:10104  │ neo4j/embedai123      │"
    echo "│ Neo4j (Bolt) │ bolt://localhost:10105  │ neo4j/embedai123      │"
    echo "│ MinIO (API)  │ http://localhost:10106  │ minioadmin/minioadmin123 │"
    echo "│ MinIO (Web)  │ http://localhost:10107  │ minioadmin/minioadmin123 │"
    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""
    echo -e "${YELLOW}使用提示:${NC}"
    echo "• 使用 './stop-databases.sh' 停止数据库服务"
    echo "• 使用 './check-databases.sh' 检查服务状态"
    echo "• 使用 'docker logs <容器名>' 查看服务日志"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}      EmbedAI 数据库服务启动脚本        ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    check_docker
    check_files
    
    # 询问是否清理旧容器
    read -p "是否清理旧容器? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup_old_containers
    fi
    
    start_databases
    wait_for_services
    show_service_info
}

# 执行主函数
main "$@"
