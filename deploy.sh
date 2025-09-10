#!/bin/bash

# EmbedAI Docker 部署脚本
# 用途：简化 Docker Compose 部署流程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖项..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 使用新版本的 docker compose 命令
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    print_success "依赖检查通过"
}

# 检查环境配置
check_environment() {
    print_info "检查环境配置..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env 文件不存在，正在从 .env.example 创建..."
            cp .env.example .env
            print_warning "请编辑 .env 文件，填入 SILICONFLOW_API_KEY 等必要配置"
            echo
            echo "主要需要配置的项目："
            echo "- SILICONFLOW_API_KEY: SiliconFlow API 密钥 (必须)"
            echo "- http_proxy, https_proxy: 代理设置 (可选)"
            echo
            read -p "是否现在打开 .env 文件进行编辑？ (y/N): " edit_env
            if [[ $edit_env =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env
            fi
        else
            print_error ".env.example 文件不存在，无法创建环境配置"
            exit 1
        fi
    fi
    
    # 检查必要的环境变量
    source .env
    if [ -z "$SILICONFLOW_API_KEY" ] || [ "$SILICONFLOW_API_KEY" = "your_siliconflow_api_key_here" ]; then
        print_error "请在 .env 文件中配置 SILICONFLOW_API_KEY"
        exit 1
    fi
    
    print_success "环境配置检查通过"
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用情况..."
    
    PORTS=(10100 10101 10102 10103 10104 10105 10106 10107)
    OCCUPIED_PORTS=()
    
    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            OCCUPIED_PORTS+=($port)
        fi
    done
    
    if [ ${#OCCUPIED_PORTS[@]} -gt 0 ]; then
        print_warning "以下端口已被占用: ${OCCUPIED_PORTS[*]}"
        print_warning "请确保这些端口可用，或修改 docker-compose.yml 中的端口配置"
        read -p "是否继续部署？ (y/N): " continue_deploy
        if [[ ! $continue_deploy =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "端口检查通过"
    fi
}

# 构建镜像
build_images() {
    print_info "构建 Docker 镜像..."
    
    # 构建后端镜像
    print_info "构建后端镜像..."
    $COMPOSE_CMD build backend
    
    # 构建前端管理镜像
    print_info "构建前端管理镜像..."
    $COMPOSE_CMD build frontend_admin
    
    # 构建前端SDK镜像
    print_info "构建前端SDK镜像..."
    $COMPOSE_CMD build frontend_sdk
    
    print_success "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    
    # 启动数据库服务
    print_info "启动数据库服务..."
    $COMPOSE_CMD up -d etcd minio neo4j
    
    # 等待数据库启动
    print_info "等待数据库服务启动..."
    sleep 30
    
    # 启动 Milvus
    print_info "启动 Milvus..."
    $COMPOSE_CMD up -d milvus
    
    # 等待 Milvus 启动
    print_info "等待 Milvus 启动..."
    sleep 60
    
    # 启动应用服务
    print_info "启动应用服务..."
    $COMPOSE_CMD up -d backend frontend_admin frontend_sdk
    
    print_success "所有服务启动完成"
}

# 检查服务状态
check_services() {
    print_info "检查服务状态..."
    
    echo
    print_info "服务状态："
    $COMPOSE_CMD ps
    
    echo
    print_info "健康检查状态："
    sleep 10  # 等待健康检查
    
    # 检查各服务的健康状态
    SERVICES=("embedai_backend:10100" "embedai_admin:10101" "embedai_sdk:10102")
    
    for service in "${SERVICES[@]}"; do
        name="${service%%:*}"
        port="${service##*:}"
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "$name (端口 $port) - 健康"
        else
            print_warning "$name (端口 $port) - 检查失败"
        fi
    done
}

# 显示访问信息
show_access_info() {
    echo
    print_success "==================================="
    print_success "EmbedAI 部署完成！"
    print_success "==================================="
    echo
    echo "服务访问地址："
    echo "📊 管理后台:    http://localhost:10101"  
    echo "🛠️  SDK 演示:    http://localhost:10102"
    echo "🔧 后端 API:    http://localhost:10100"
    echo "💾 MinIO 控制台: http://localhost:10107 (minioadmin/minioadmin123)"
    echo "🕸️  Neo4j 浏览器: http://localhost:10104 (neo4j/embedai123)"
    echo
    echo "实用命令："
    echo "🔍 查看日志:    $COMPOSE_CMD logs -f [service_name]"
    echo "⏸️  停止服务:    $COMPOSE_CMD down"
    echo "🗑️  清理数据:    $COMPOSE_CMD down -v"
    echo "🔄 重启服务:    $COMPOSE_CMD restart [service_name]"
    echo
    print_info "享受使用 EmbedAI！"
}

# 主函数
main() {
    print_info "开始部署 EmbedAI..."
    echo
    
    check_dependencies
    check_environment
    check_ports
    build_images
    start_services
    check_services
    show_access_info
}

# 处理参数
case "${1:-}" in
    "build")
        check_dependencies
        build_images
        ;;
    "start")
        check_dependencies
        start_services
        ;;
    "stop")
        print_info "停止所有服务..."
        $COMPOSE_CMD down
        print_success "服务已停止"
        ;;
    "restart")
        print_info "重启所有服务..."
        $COMPOSE_CMD restart
        print_success "服务已重启"
        ;;
    "logs")
        $COMPOSE_CMD logs -f ${2:-}
        ;;
    "status")
        check_services
        ;;
    "clean")
        print_warning "这将删除所有容器和数据卷！"
        read -p "确定要继续吗？ (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            $COMPOSE_CMD down -v --remove-orphans
            docker system prune -f
            print_success "清理完成"
        else
            print_info "取消清理"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "EmbedAI Docker 部署脚本"
        echo
        echo "用法:"
        echo "  ./deploy.sh [命令]"
        echo
        echo "命令:"
        echo "  (无参数)   完整部署流程"
        echo "  build      仅构建镜像"
        echo "  start      仅启动服务"
        echo "  stop       停止所有服务"
        echo "  restart    重启所有服务"
        echo "  logs       查看日志 (可指定服务名)"
        echo "  status     检查服务状态"
        echo "  clean      清理所有容器和数据卷"
        echo "  help       显示此帮助信息"
        ;;
    *)
        main
        ;;
esac
