#!/bin/bash
# 修复 Docker 镜像源问题

echo "=========================================="
echo "Docker 镜像源修复工具"
echo "=========================================="
echo ""

# 检查 Docker 是否运行
if ! docker ps &> /dev/null; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

echo "✅ Docker 正在运行"
echo ""

# 尝试直接拉取镜像
echo "==> 测试拉取 python:3.11-slim 镜像"
echo ""

if docker pull python:3.11-slim; then
    echo ""
    echo "✅ 镜像拉取成功！可以正常使用 Docker 构建了"
    echo "   现在可以运行: ./build_backend_docker.sh"
    exit 0
else
    echo ""
    echo "❌ 镜像拉取失败"
    echo ""
    echo "可能的原因："
    echo "1. Docker 镜像源配置有问题（403 Forbidden）"
    echo "2. 网络连接问题"
    echo ""
    echo "解决方案："
    echo ""
    echo "方案 1: 修改 Docker Desktop 镜像源配置"
    echo "----------------------------------------"
    echo "1. 打开 Docker Desktop"
    echo "2. 点击 Settings (设置)"
    echo "3. 选择 Docker Engine"
    echo "4. 修改或删除 registry-mirrors 配置"
    echo ""
    echo "推荐的配置（选择其中一个）："
    echo ""
    echo "选项 A: 使用官方 Docker Hub（推荐，如果网络允许）"
    echo "{"
    echo "  \"registry-mirrors\": []"
    echo "}"
    echo ""
    echo "选项 B: 使用腾讯云镜像源"
    echo "{"
    echo "  \"registry-mirrors\": ["
    echo "    \"https://mirror.ccs.tencentyun.com\""
    echo "  ]"
    echo "}"
    echo ""
    echo "选项 C: 使用网易镜像源"
    echo "{"
    echo "  \"registry-mirrors\": ["
    echo "    \"https://hub-mirror.c.163.com\""
    echo "  ]"
    echo "}"
    echo ""
    echo "选项 D: 使用中科大镜像源"
    echo "{"
    echo "  \"registry-mirrors\": ["
    echo "    \"https://docker.mirrors.ustc.edu.cn\""
    echo "  ]"
    echo "}"
    echo ""
    echo "修改后，点击 'Apply & Restart' 重启 Docker"
    echo ""
    echo "方案 2: 手动拉取镜像"
    echo "----------------------------------------"
    echo "如果配置了正确的镜像源，可以尝试："
    echo "  docker pull python:3.11-slim"
    echo ""
    echo "方案 3: 使用代理"
    echo "----------------------------------------"
    echo "如果有代理，可以在 Docker Desktop 中配置代理"
    echo ""
    exit 1
fi
