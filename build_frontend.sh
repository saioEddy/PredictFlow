#!/bin/bash
# 前端打包：npm install（修正 lock 与 package.json）并构建静态资源

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "==> 检查 Node 与 npm"
command -v node >/dev/null 2>&1 || { echo "需要安装 node"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "需要安装 npm"; exit 1; }

echo "==> 安装依赖（npm install，修正 lock 与 package.json 不一致）"
cd "$FRONTEND_DIR"
npm install

echo "==> 清理旧构建"
rm -rf build

echo "==> 构建前端"
npm run build

echo "==> 前端构建完成: $FRONTEND_DIR/build"

