#!/bin/bash
# 后端打包：使用 shiv 生成可执行包 dist/predictflow-api.shiv

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_SHIV="$ROOT_DIR/dist/predictflow-api.shiv"

echo "==> 检查 Python 与 pip"
command -v python3 >/dev/null 2>&1 || { echo "需要安装 python3"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "需要安装 pip3"; exit 1; }

echo "==> 安装 shiv（如未安装）"
python3 -m pip show shiv >/dev/null 2>&1 || python3 -m pip install -U shiv

echo "==> 打包后端（shiv）"
cd "$ROOT_DIR"
python3 -m shiv -e bootstrap:main -o "$BACKEND_SHIV" -r requirements.txt .

echo "==> 后端打包完成: $BACKEND_SHIV"

