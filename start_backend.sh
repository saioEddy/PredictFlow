#!/bin/bash
# 启动FastAPI后端服务

echo "正在启动FastAPI后端服务..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""

cd "$(dirname "$0")"
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

