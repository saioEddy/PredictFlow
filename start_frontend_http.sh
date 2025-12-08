#!/bin/bash
# 使用 Python HTTP Server 启动前端（方案2）
# 需要先启动后端服务（端口 8000）

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${1:-80}
FRONTEND_BUILD_DIR="$ROOT_DIR/frontend/build"
FRONTEND_DIST_DIR="$ROOT_DIR/dist/full-release/frontend-build"

echo "=========================================="
echo "启动前端 HTTP Server"
echo "=========================================="
echo ""

# 查找前端构建目录
if [ -d "$FRONTEND_DIST_DIR" ]; then
    FRONTEND_DIR="$FRONTEND_DIST_DIR"
    echo "✅ 使用前端目录: $FRONTEND_DIR"
elif [ -d "$FRONTEND_BUILD_DIR" ]; then
    FRONTEND_DIR="$FRONTEND_BUILD_DIR"
    echo "✅ 使用前端目录: $FRONTEND_DIR"
else
    echo "❌ 前端构建目录不存在"
    echo "   请先运行: ./build_frontend.sh"
    exit 1
fi

echo ""
echo "==> 启动 Python HTTP Server"
echo "   端口: $PORT"
echo "   目录: $FRONTEND_DIR"
echo ""
echo "   访问地址: http://localhost:$PORT"
echo "   确保后端服务运行在: http://localhost:8000"
echo ""
echo "   按 Ctrl+C 停止服务"
echo ""

cd "$FRONTEND_DIR"
python3 -m http.server $PORT
