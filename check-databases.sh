#!/bin/bash

# EmbedAI 数据库服务状态检查脚本
# 用于检查本地 Docker 环境中数据库服务的运行状态

set -e  # 遇到错误时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行"
        return 1
    fi
    
    return 0
}

# 检查容器状态
check_container_status() {
    local container_name=$1
    local service_name=$2
    
    if ! docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name"; then
        echo -e "${RED}❌ $service_name${NC} - 容器未运行"
        return 1
    fi
    
    local status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$container_name" | awk '{print $2}')
    
    if [[ $status == *"healthy"* ]]; then
        echo -e "${GREEN}✅ $service_name${NC} - 运行正常 (健康检查通过)"
        return 0
    elif [[ $status == *"unhealthy"* ]]; then
        echo -e "${RED}❌ $service_name${NC} - 运行异常 (健康检查失败)"
        return 1
    elif [[ $status == *"Up"* ]]; then
        echo -e "${YELLOW}⚠️  $service_name${NC} - 运行中 (健康检查中...)"
        return 0
    else
        echo -e "${RED}❌ $service_name${NC} - 状态异常: $status"
        return 1
    fi
}

# 检查端口连通性
check_port_connectivity() {
    local host=$1
    local port=$2
    local service_name=$3
    
    if nc -z "$host" "$port" 2>/dev/null; then
        echo -e "${GREEN}✅ $service_name 端口${NC} - $host:$port 可访问"
        return 0
    else
        echo -e "${RED}❌ $service_name 端口${NC} - $host:$port 不可访问"
        return 1
    fi
}

# 检查 Milvus 服务
check_milvus() {
    local container="embedai_milvus"
    local service="Milvus (向量数据库)"
    
    echo -e "${CYAN}检查 $service...${NC}"
    
    if check_container_status "$container" "$service"; then
        check_port_connectivity "localhost" "10103" "Milvus gRPC"
        
        # 检查 Milvus 是否可以响应
        if command -v curl &> /dev/null; then
            if docker exec "$container" curl -f http://localhost:9091/healthz &>/dev/null; then
                echo -e "${GREEN}✅ Milvus 健康检查${NC} - 服务响应正常"
            else
                echo -e "${YELLOW}⚠️  Milvus 健康检查${NC} - 服务可能还在启动中"
            fi
        fi
    fi
    echo ""
}

# 检查 etcd 服务
check_etcd() {
    local container="embedai_etcd"
    local service="etcd (协调服务)"
    
    echo -e "${CYAN}检查 $service...${NC}"
    
    if check_container_status "$container" "$service"; then
        # etcd 不对外暴露端口，只检查容器内部健康状态
        if docker exec "$container" etcdctl endpoint health &>/dev/null; then
            echo -e "${GREEN}✅ etcd 健康检查${NC} - 服务响应正常"
        else
            echo -e "${YELLOW}⚠️  etcd 健康检查${NC} - 服务可能还在启动中"
        fi
    fi
    echo ""
}

# 检查 Neo4j 服务
check_neo4j() {
    local container="embedai_neo4j"
    local service="Neo4j (图数据库)"
    
    echo -e "${CYAN}检查 $service...${NC}"
    
    if check_container_status "$container" "$service"; then
        check_port_connectivity "localhost" "10104" "Neo4j HTTP"
        check_port_connectivity "localhost" "10105" "Neo4j Bolt"
        
        # 检查 Neo4j 数据库连接
        if command -v curl &> /dev/null; then
            if curl -f http://localhost:10104 &>/dev/null; then
                echo -e "${GREEN}✅ Neo4j Web界面${NC} - http://localhost:10104 可访问"
            else
                echo -e "${YELLOW}⚠️  Neo4j Web界面${NC} - 服务可能还在启动中"
            fi
        fi
    fi
    echo ""
}

# 检查 MinIO 服务
check_minio() {
    local container="embedai_minio"
    local service="MinIO (对象存储)"
    
    echo -e "${CYAN}检查 $service...${NC}"
    
    if check_container_status "$container" "$service"; then
        check_port_connectivity "localhost" "10106" "MinIO API"
        check_port_connectivity "localhost" "10107" "MinIO Console"
        
        # 检查 MinIO 健康状态
        if command -v curl &> /dev/null; then
            if curl -f http://localhost:10106/minio/health/live &>/dev/null; then
                echo -e "${GREEN}✅ MinIO 健康检查${NC} - 服务响应正常"
                echo -e "${GREEN}✅ MinIO 管理界面${NC} - http://localhost:10107 可访问"
            else
                echo -e "${YELLOW}⚠️  MinIO 健康检查${NC} - 服务可能还在启动中"
            fi
        fi
    fi
    echo ""
}

# 显示服务摘要
show_summary() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}           服务状态摘要                 ${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    local total_services=4
    local running_services=0
    
    # 计算运行中的服务数量
    containers=("embedai_milvus" "embedai_etcd" "embedai_neo4j" "embedai_minio")
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            ((running_services++))
        fi
    done
    
    echo -e "运行中服务: ${GREEN}$running_services${NC}/$total_services"
    
    if [ $running_services -eq $total_services ]; then
        echo -e "整体状态: ${GREEN}全部运行正常${NC}"
    elif [ $running_services -gt 0 ]; then
        echo -e "整体状态: ${YELLOW}部分服务运行${NC}"
    else
        echo -e "整体状态: ${RED}所有服务已停止${NC}"
    fi
    
    echo ""
    
    # 显示快速操作提示
    if [ $running_services -eq 0 ]; then
        echo -e "${YELLOW}💡 提示:${NC} 使用 './start-databases.sh' 启动数据库服务"
    elif [ $running_services -lt $total_services ]; then
        echo -e "${YELLOW}💡 提示:${NC} 部分服务未运行，建议重启所有服务"
        echo -e "   使用 './stop-databases.sh && ./start-databases.sh'"
    else
        echo -e "${GREEN}💡 提示:${NC} 所有服务运行正常"
        echo -e "   • Neo4j Web界面: http://localhost:10104 (neo4j/embedai123)"
        echo -e "   • MinIO 管理界面: http://localhost:10107 (minioadmin/minioadmin123)"
    fi
}

# 显示详细日志（可选）
show_logs() {
    if [ "$1" = "--logs" ] || [ "$1" = "-l" ]; then
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}           容器日志 (最近20行)          ${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        containers=("embedai_milvus" "embedai_etcd" "embedai_neo4j" "embedai_minio")
        for container in "${containers[@]}"; do
            if docker ps --format "table {{.Names}}" | grep -q "$container"; then
                echo -e "${CYAN}$container 日志:${NC}"
                docker logs --tail 20 "$container" 2>/dev/null || echo "无法获取日志"
                echo ""
            fi
        done
    fi
}

# 主函数
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}      EmbedAI 数据库服务状态检查        ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    if ! check_docker; then
        exit 1
    fi
    
    log_info "开始检查数据库服务状态..."
    echo ""
    
    # 检查各个服务
    check_etcd
    check_minio
    check_neo4j
    check_milvus
    
    # 显示摘要
    show_summary
    
    # 显示日志（如果请求）
    show_logs "$1"
}

# 显示帮助信息
show_help() {
    echo "EmbedAI 数据库服务状态检查脚本"
    echo ""
    echo "用法:"
    echo "  $0          # 检查服务状态"
    echo "  $0 --logs   # 检查状态并显示容器日志"
    echo "  $0 -l       # 检查状态并显示容器日志"
    echo "  $0 --help   # 显示帮助信息"
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
