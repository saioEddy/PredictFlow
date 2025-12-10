#!/bin/bash
# PredictFlow 启动脚本
# 启动前端（Tomcat）和后端服务

set -euo pipefail

# 获取脚本所在目录（部署目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置
TOMCAT_DIR="$SCRIPT_DIR/apache-tomcat-9.0.113"
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
TOMCAT_PID_FILE="$SCRIPT_DIR/.tomcat.pid"
LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
BACKEND_ERROR_LOG="$LOG_DIR/backend_error.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查后端是否已运行
check_backend_running() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$BACKEND_PID_FILE"
            return 1
        fi
    fi
    return 1
}

# 检查 Tomcat 是否已运行
check_tomcat_running() {
    if [ -f "$TOMCAT_PID_FILE" ]; then
        local pid=$(cat "$TOMCAT_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$TOMCAT_PID_FILE"
            return 1
        fi
    fi
    # 也检查 Tomcat 进程
    if pgrep -f "catalina" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 启动后端服务
start_backend() {
    if check_backend_running; then
        echo_warn "后端服务已在运行中（PID: $(cat "$BACKEND_PID_FILE")）"
        return 0
    fi

    echo_info "正在启动后端服务..."
    
    # 检查后端文件是否存在
    if [ ! -f "$SCRIPT_DIR/backend/predictflow-api.shiv" ]; then
        echo_error "后端文件不存在: $SCRIPT_DIR/backend/predictflow-api.shiv"
        return 1
    fi
    
    # 检查 Python 是否存在
    if [ ! -f "$SCRIPT_DIR/python-portable/bin/python3" ]; then
        echo_error "Python 可执行文件不存在: $SCRIPT_DIR/python-portable/bin/python3"
        return 1
    fi
    
    # 启动后端（后台运行，保存 PID）
    cd "$SCRIPT_DIR"
    nohup "$SCRIPT_DIR/python-portable/bin/python3" "$SCRIPT_DIR/backend/predictflow-api.shiv" \
        > "$BACKEND_LOG" 2> "$BACKEND_ERROR_LOG" &
    
    local backend_pid=$!
    echo $backend_pid > "$BACKEND_PID_FILE"
    
    # 等待一下，检查进程是否还在运行
    sleep 2
    if ps -p "$backend_pid" > /dev/null 2>&1; then
        echo_info "✓ 后端服务启动成功（PID: $backend_pid）"
        echo_info "  日志文件: $BACKEND_LOG"
        echo_info "  错误日志: $BACKEND_ERROR_LOG"
        return 0
    else
        echo_error "后端服务启动失败，请查看日志: $BACKEND_ERROR_LOG"
        rm -f "$BACKEND_PID_FILE"
        return 1
    fi
}

# 启动 Tomcat
start_tomcat() {
    if check_tomcat_running; then
        echo_warn "Tomcat 已在运行中"
        return 0
    fi

    echo_info "正在启动 Tomcat..."
    
    # 检查 Tomcat 目录是否存在
    if [ ! -d "$TOMCAT_DIR" ]; then
        echo_error "Tomcat 目录不存在: $TOMCAT_DIR"
        return 1
    fi
    
    # 检查 startup.sh 是否存在
    if [ ! -f "$TOMCAT_DIR/bin/startup.sh" ]; then
        echo_error "Tomcat startup.sh 不存在: $TOMCAT_DIR/bin/startup.sh"
        return 1
    fi
    
    # 设置 CATALINA_HOME
    export CATALINA_HOME="$TOMCAT_DIR"
    export CATALINA_BASE="$TOMCAT_DIR"
    
    # 启动 Tomcat
    cd "$TOMCAT_DIR/bin"
    bash startup.sh
    
    # 等待一下，获取 Tomcat 进程 PID
    sleep 3
    local tomcat_pid=$(pgrep -f "catalina" | head -n 1)
    
    if [ -n "$tomcat_pid" ]; then
        echo $tomcat_pid > "$TOMCAT_PID_FILE"
        echo_info "✓ Tomcat 启动成功（PID: $tomcat_pid）"
        return 0
    else
        echo_warn "Tomcat 可能未正常启动，请检查日志: $TOMCAT_DIR/logs/catalina.out"
        return 1
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "PredictFlow 服务启动脚本"
    echo "=========================================="
    echo ""
    echo "部署目录: $SCRIPT_DIR"
    echo "Tomcat 目录: $TOMCAT_DIR"
    echo "后端文件: $SCRIPT_DIR/backend/predictflow-api.shiv"
    echo ""
    
    # 启动后端
    if ! start_backend; then
        echo_error "后端启动失败，退出"
        exit 1
    fi
    
    echo ""
    
    # 启动 Tomcat
    if ! start_tomcat; then
        echo_warn "Tomcat 启动可能失败，但后端已启动"
    fi
    
    echo ""
    echo "=========================================="
    echo "✓ 服务启动完成"
    echo "=========================================="
    echo ""
    echo "前端地址: http://localhost:8080"
    echo "后端 API: http://localhost:8000"
    echo "API 文档: http://localhost:8000/docs"
    echo ""
    echo "查看后端日志: tail -f $BACKEND_LOG"
    echo "查看后端错误: tail -f $BACKEND_ERROR_LOG"
    echo "查看 Tomcat 日志: tail -f $TOMCAT_DIR/logs/catalina.out"
    echo ""
    echo "停止服务: ./stop_predictflow.sh"
    echo ""
}

# 执行主函数
main "$@"

