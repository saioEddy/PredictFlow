#!/bin/bash
# PredictFlow 停止脚本
# 停止前端（Tomcat）和后端服务

set -euo pipefail

# 获取脚本所在目录（部署目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置
TOMCAT_DIR="$SCRIPT_DIR/apache-tomcat-9.0.113"
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
TOMCAT_PID_FILE="$SCRIPT_DIR/.tomcat.pid"

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

# 停止后端服务
stop_backend() {
    if [ ! -f "$BACKEND_PID_FILE" ]; then
        # 尝试通过进程名查找
        local pid=$(pgrep -f "predictflow-api.shiv" | head -n 1)
        if [ -n "$pid" ]; then
            echo_info "找到后端进程（PID: $pid），正在停止..."
            kill "$pid" 2>/dev/null || true
            sleep 2
            if ps -p "$pid" > /dev/null 2>&1; then
                echo_warn "进程未响应，强制停止..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo_info "✓ 后端服务已停止"
            return 0
        else
            echo_warn "后端服务未运行"
            return 0
        fi
    fi
    
    local pid=$(cat "$BACKEND_PID_FILE")
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo_info "正在停止后端服务（PID: $pid）..."
        kill "$pid" 2>/dev/null || true
        
        # 等待进程结束
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # 如果还在运行，强制停止
        if ps -p "$pid" > /dev/null 2>&1; then
            echo_warn "进程未响应，强制停止..."
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        fi
        
        if ps -p "$pid" > /dev/null 2>&1; then
            echo_error "无法停止后端服务（PID: $pid）"
            return 1
        else
            echo_info "✓ 后端服务已停止"
            rm -f "$BACKEND_PID_FILE"
            return 0
        fi
    else
        echo_warn "后端服务未运行（PID 文件存在但进程不存在）"
        rm -f "$BACKEND_PID_FILE"
        return 0
    fi
}

# 停止 Tomcat
stop_tomcat() {
    if [ ! -d "$TOMCAT_DIR" ]; then
        echo_warn "Tomcat 目录不存在: $TOMCAT_DIR"
        return 0
    fi
    
    if [ ! -f "$TOMCAT_DIR/bin/shutdown.sh" ]; then
        echo_warn "Tomcat shutdown.sh 不存在，尝试通过进程停止..."
        local pid=$(pgrep -f "catalina" | head -n 1)
        if [ -n "$pid" ]; then
            echo_info "找到 Tomcat 进程（PID: $pid），正在停止..."
            kill "$pid" 2>/dev/null || true
            sleep 3
            if ps -p "$pid" > /dev/null 2>&1; then
                echo_warn "进程未响应，强制停止..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo_info "✓ Tomcat 已停止"
            rm -f "$TOMCAT_PID_FILE"
            return 0
        else
            echo_warn "Tomcat 未运行"
            rm -f "$TOMCAT_PID_FILE"
            return 0
        fi
    fi
    
    # 使用 shutdown.sh 停止
    echo_info "正在停止 Tomcat..."
    
    export CATALINA_HOME="$TOMCAT_DIR"
    export CATALINA_BASE="$TOMCAT_DIR"
    
    cd "$TOMCAT_DIR/bin"
    bash shutdown.sh
    
    # 等待进程结束
    sleep 5
    
    # 检查是否还有 Tomcat 进程
    local pid=$(pgrep -f "catalina" | head -n 1)
    if [ -n "$pid" ]; then
        echo_warn "Tomcat 未正常停止，强制停止（PID: $pid）..."
        kill "$pid" 2>/dev/null || true
        sleep 2
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi
    
    # 再次检查
    if pgrep -f "catalina" > /dev/null 2>&1; then
        echo_error "无法完全停止 Tomcat，可能还有其他进程"
        return 1
    else
        echo_info "✓ Tomcat 已停止"
        rm -f "$TOMCAT_PID_FILE"
        return 0
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "PredictFlow 服务停止脚本"
    echo "=========================================="
    echo ""
    
    # 停止后端
    stop_backend
    
    echo ""
    
    # 停止 Tomcat
    stop_tomcat
    
    echo ""
    echo "=========================================="
    echo "✓ 服务停止完成"
    echo "=========================================="
    echo ""
}

# 执行主函数
main "$@"

