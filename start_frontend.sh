#!/bin/bash
# 启动React前端服务

echo "正在启动React前端服务..."
echo "前端地址: http://localhost:3000"
echo ""

cd "$(dirname "$0")/frontend"

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "检测到未安装依赖，正在安装..."
    npm install
fi

npm start

