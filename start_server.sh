#!/bin/bash
# 启动脚本：提供两种启动方式
# 方案1: FastAPI 同时提供前后端（推荐，单端口）
# 方案2: Python HTTP Server 提供前端 + FastAPI 提供后端（双端口）

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-80}
MODE=${MODE:-"integrated"}

echo "=========================================="
echo "PredictFlow 服务启动脚本"
echo "=========================================="
echo ""

# 检查模式
if [[ "$1" == "--separate" ]] || [[ "$MODE" == "separate" ]]; then
    MODE="separate"
    echo "使用方案2: 前后端分离部署"
    echo "  前端: Python HTTP Server (端口 $FRONTEND_PORT)"
    echo "  后端: FastAPI (端口 $PORT)"
    echo ""
    
    # 检查前端构建文件
    FRONTEND_BUILD_DIR="$ROOT_DIR/frontend/build"
    if [ ! -d "$FRONTEND_BUILD_DIR" ]; then
        echo "❌ 前端构建目录不存在: $FRONTEND_BUILD_DIR"
        echo "   请先运行: ./build_frontend.sh"
        exit 1
    fi
    
    # 检查后端
    BACKEND_SHIV="$ROOT_DIR/dist/predictflow-api.shiv"
    if [ ! -f "$BACKEND_SHIV" ]; then
        echo "⚠️  后端 shiv 包不存在: $BACKEND_SHIV"
        echo "   将使用 Python 直接运行后端..."
        BACKEND_CMD="python3 -m uvicorn api.main:app --host 0.0.0.0 --port $PORT"
    else
        echo "✅ 找到后端包: $BACKEND_SHIV"
        BACKEND_CMD="python3 $BACKEND_SHIV"
    fi
    
    echo ""
    echo "==> 启动后端服务 (端口 $PORT)"
    echo "   命令: $BACKEND_CMD"
    $BACKEND_CMD &
    BACKEND_PID=$!
    echo "   后端进程 ID: $BACKEND_PID"
    
    # 等待后端启动
    sleep 2
    
    echo ""
    echo "==> 启动前端服务 (端口 $FRONTEND_PORT)"
    echo "   目录: $FRONTEND_BUILD_DIR"
    cd "$FRONTEND_BUILD_DIR"
    python3 -m http.server $FRONTEND_PORT &
    FRONTEND_PID=$!
    echo "   前端进程 ID: $FRONTEND_PID"
    
    echo ""
    echo "=========================================="
    echo "✅ 服务已启动！"
    echo "=========================================="
    echo "   前端地址: http://localhost:$FRONTEND_PORT"
    echo "   后端 API: http://localhost:$PORT"
    echo ""
    echo "   按 Ctrl+C 停止所有服务"
    echo ""
    
    # 捕获中断信号，清理进程
    trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    
    # 等待进程
    wait
    
else
    MODE="integrated"
    echo "使用方案1: FastAPI 集成部署（推荐）"
    echo "  前端 + 后端: FastAPI (端口 $PORT)"
    echo "  访问地址: http://localhost:$PORT"
    echo ""
    
    # 检查前端构建文件
    FRONTEND_BUILD_DIR="$ROOT_DIR/frontend/build"
    FRONTEND_DIST_DIR="$ROOT_DIR/dist/full-release/frontend-build"
    
    if [ ! -d "$FRONTEND_BUILD_DIR" ] && [ ! -d "$FRONTEND_DIST_DIR" ]; then
        echo "⚠️  前端构建目录不存在"
        echo "   将只启动后端 API 服务"
        echo "   前端功能将不可用"
        echo ""
    else
        if [ -d "$FRONTEND_DIST_DIR" ]; then
            echo "✅ 找到前端文件: $FRONTEND_DIST_DIR"
        else
            echo "✅ 找到前端文件: $FRONTEND_BUILD_DIR"
        fi
        echo ""
    fi
    
    # 检查后端
    BACKEND_SHIV="$ROOT_DIR/dist/predictflow-api.shiv"
    if [ ! -f "$BACKEND_SHIV" ]; then
        echo "⚠️  后端 shiv 包不存在: $BACKEND_SHIV"
        echo "   将使用 Python 直接运行后端..."
        BACKEND_CMD="python3 -m uvicorn api.main:app --host 0.0.0.0 --port $PORT"
    else
        echo "✅ 找到后端包: $BACKEND_SHIV"
        BACKEND_CMD="python3 $BACKEND_SHIV"
    fi
    
    echo "==> 启动服务 (端口 $PORT)"
    echo "   命令: $BACKEND_CMD"
    echo ""
    echo "=========================================="
    echo "✅ 服务已启动！"
    echo "=========================================="
    echo "   访问地址: http://localhost:$PORT"
    echo "   API 文档: http://localhost:$PORT/docs"
    echo ""
    echo "   按 Ctrl+C 停止服务"
    echo ""
    
    # 启动服务
    $BACKEND_CMD
fi
