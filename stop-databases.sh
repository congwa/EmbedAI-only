#!/bin/bash

# EmbedAI 数据库服务停止脚本
# 用于停止本地 Docker 环境中的所有数据库服务

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

# 检查 Docker 是否可用
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行"
        exit 1
    fi
}

# 停止数据库服务
stop_databases() {
    log_info "停止数据库服务..."
    
    # 检查 docker-compose 文件是否存在
    if [ ! -f "docker-compose-db.yml" ]; then
        log_error "找不到 docker-compose-db.yml 文件"
        exit 1
    fi
    
    # 使用 docker-compose 或 docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    log_info "使用命令: $COMPOSE_CMD -f docker-compose-db.yml down"
    
    # 停止服务
    $COMPOSE_CMD -f docker-compose-db.yml down
    
    if [ $? -eq 0 ]; then
        log_success "数据库服务已停止"
    else
        log_error "数据库服务停止失败"
        exit 1
    fi
}

# 清理容器和网络（可选）
cleanup_resources() {
    if [ "$1" = "--cleanup" ] || [ "$1" = "-c" ]; then
        log_info "清理相关资源..."
        
        # 删除网络
        if docker network ls | grep -q "embedai_network"; then
            log_info "删除网络: embedai_network"
            docker network rm embedai_network 2>/dev/null || true
        fi
        
        # 清理未使用的卷（谨慎操作）
        read -p "是否删除数据卷？这将永久删除所有数据库数据！(y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_warning "删除数据卷..."
            docker volume prune -f
            log_warning "数据卷已删除"
        fi
        
        log_success "资源清理完成"
    fi
}

# 显示容器状态
show_status() {
    log_info "检查容器状态..."
    
    containers=("embedai_milvus" "embedai_etcd" "embedai_neo4j" "embedai_minio")
    all_stopped=true
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "^${container}$"; then
            log_warning "$container 仍在运行"
            all_stopped=false
        fi
    done
    
    if [ "$all_stopped" = true ]; then
        log_success "所有数据库容器已停止"
    else
        log_warning "部分容器可能仍在运行，请检查"
    fi
}

# 主函数
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}      EmbedAI 数据库服务停止脚本        ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    check_docker
    stop_databases
    show_status
    cleanup_resources "$1"
    
    echo ""
    log_success "数据库服务停止完成！"
    echo ""
    echo -e "${YELLOW}使用提示:${NC}"
    echo "• 使用 './start-databases.sh' 重新启动数据库服务"
    echo "• 使用 './stop-databases.sh --cleanup' 停止服务并清理资源"
    echo "• 使用 './check-databases.sh' 检查服务状态"
    echo ""
}

# 显示帮助信息
show_help() {
    echo "EmbedAI 数据库服务停止脚本"
    echo ""
    echo "用法:"
    echo "  $0              # 停止数据库服务"
    echo "  $0 --cleanup    # 停止服务并清理资源"
    echo "  $0 -c           # 停止服务并清理资源"
    echo "  $0 --help       # 显示帮助信息"
    echo ""
}

# 处理命令行参数
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        main "$1"
        ;;
esac
