#!/bin/bash
# 一键打包前后端：调用分脚本，生成后端 shiv 包 + 前端静态资源，并汇总到 dist/full-release

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$ROOT_DIR/dist"
RELEASE_DIR="$DIST_DIR/full-release"
FRONTEND_BUILD_DIR="$ROOT_DIR/frontend/build"
BACKEND_SHIV="$DIST_DIR/predictflow-api.shiv"

echo "==> 清理旧产物"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# 保留旧流程（已用分脚本替代）
# python3 -m shiv -e bootstrap:main -o "$BACKEND_SHIV" -r requirements.txt .
# npm ci && npm run build

# 检查是否使用 Docker 构建
USE_DOCKER=${USE_DOCKER:-"false"}
if [[ "$USE_DOCKER" == "true" ]] || [[ "$1" == "--docker" ]]; then
    echo "==> 使用 Docker 打包后端（Linux 兼容）"
    "$ROOT_DIR/build_backend_docker.sh"
else
    echo "==> 打包后端（本地环境）"
"$ROOT_DIR/build_backend.sh"
fi

echo "==> 打包前端"
"$ROOT_DIR/build_frontend.sh"

echo "==> 汇总发布文件"
cp "$BACKEND_SHIV" "$RELEASE_DIR/"
cp -r "$FRONTEND_BUILD_DIR" "$RELEASE_DIR/frontend-build"

echo "==> 完成"
echo "后端包: $BACKEND_SHIV"
echo "前端静态: $RELEASE_DIR/frontend-build"
echo "发布目录: $RELEASE_DIR"

