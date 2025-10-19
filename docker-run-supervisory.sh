#!/bin/bash

# 主管架构系统便捷运行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  主管架构研究系统${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查 Docker 是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker 未运行，请先启动 Docker"
        exit 1
    fi
}

# 检查 Ollama 服务
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_warning "Ollama 服务未运行，将使用 Docker 启动"
        return 1
    fi
    return 0
}

# 启动 Ollama 服务
start_ollama() {
    print_message "启动 Ollama 服务..."
    docker-compose -f docker-compose-supervisory.yml up -d ollama
    
    # 等待 Ollama 启动
    print_message "等待 Ollama 服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_message "Ollama 服务已启动"
            return 0
        fi
        sleep 2
    done
    
    print_error "Ollama 服务启动超时"
    return 1
}

# 下载模型
download_model() {
    local model=${1:-"llama3"}
    print_message "检查模型 $model 是否已下载..."
    
    if curl -s http://localhost:11434/api/tags | grep -q "\"name\":\"$model\""; then
        print_message "模型 $model 已存在"
        return 0
    fi
    
    print_message "下载模型 $model..."
    docker exec ollama-supervisory ollama pull $model
    
    if [ $? -eq 0 ]; then
        print_message "模型 $model 下载完成"
    else
        print_error "模型 $model 下载失败"
        return 1
    fi
}

# 运行主管架构研究
run_supervisory_research() {
    local topic="$1"
    local output_file="${2:-supervisory_research_report.md}"
    local provider="${3:-ollama}"
    local model="${4:-llama3}"
    local search_api="${5:-duckduckgo}"
    local max_loops="${6:-3}"
    
    print_message "开始主管架构研究..."
    print_message "主题: $topic"
    print_message "输出文件: $output_file"
    print_message "LLM 提供商: $provider"
    print_message "模型: $model"
    print_message "搜索引擎: $search_api"
    print_message "最大循环次数: $max_loops"
    
    # 构建命令
    local cmd="python -m Langgraph_deep_researcher.supervisory_cli"
    cmd="$cmd \"$topic\""
    cmd="$cmd --out /app/output/$output_file"
    cmd="$cmd --provider $provider"
    cmd="$cmd --model $model"
    cmd="$cmd --search-api $search_api"
    cmd="$cmd --max-loops $max_loops"
    cmd="$cmd --verbose"
    
    # 运行研究
    docker-compose -f docker-compose-supervisory.yml run --rm \
        -e RESEARCH_TOPIC="$topic" \
        supervisory-researcher \
        sh -c "$cmd"
    
    if [ $? -eq 0 ]; then
        print_message "研究完成！报告已保存到: output/$output_file"
    else
        print_error "研究失败"
        return 1
    fi
}

# 清理资源
cleanup() {
    print_message "清理 Docker 资源..."
    docker-compose -f docker-compose-supervisory.yml down
}

# 显示帮助信息
show_help() {
    echo "主管架构研究系统便捷脚本"
    echo ""
    echo "用法:"
    echo "  $0 \"研究主题\" [输出文件] [LLM提供商] [模型] [搜索引擎] [最大循环次数]"
    echo ""
    echo "参数:"
    echo "  研究主题        必需，要研究的主题"
    echo "  输出文件        可选，输出文件名 (默认: supervisory_research_report.md)"
    echo "  LLM提供商       可选，ollama 或 openai (默认: ollama)"
    echo "  模型           可选，模型名称 (默认: llama3)"
    echo "  搜索引擎       可选，duckduckgo/tavily/perplexity/searxng (默认: duckduckgo)"
    echo "  最大循环次数    可选，1-5 (默认: 3)"
    echo ""
    echo "示例:"
    echo "  $0 \"人工智能发展趋势\""
    echo "  $0 \"量子计算应用\" ai_report.md ollama llama3 duckduckgo 2"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  --cleanup      清理 Docker 资源"
    echo "  --check        检查服务状态"
}

# 检查服务状态
check_status() {
    print_message "检查服务状态..."
    
    if check_docker; then
        print_message "✅ Docker 运行正常"
    else
        print_error "❌ Docker 未运行"
    fi
    
    if check_ollama; then
        print_message "✅ Ollama 服务运行正常"
    else
        print_warning "⚠️  Ollama 服务未运行"
    fi
}

# 主函数
main() {
    print_header
    
    # 处理命令行参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        --cleanup)
            cleanup
            exit 0
            ;;
        --check)
            check_status
            exit 0
            ;;
        "")
            print_error "请提供研究主题"
            show_help
            exit 1
            ;;
    esac
    
    # 检查 Docker
    check_docker
    
    # 检查并启动 Ollama
    if ! check_ollama; then
        if ! start_ollama; then
            print_error "无法启动 Ollama 服务"
            exit 1
        fi
    fi
    
    # 下载模型
    download_model "${4:-llama3}"
    
    # 创建输出目录
    mkdir -p output
    
    # 运行研究
    run_supervisory_research "$@"
    
    print_message "主管架构研究完成！"
}

# 捕获中断信号
trap cleanup INT TERM

# 运行主函数
main "$@"
