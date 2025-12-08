#!/bin/bash
# 使用 Docker 在 Linux 容器中打包后端，生成 Linux 可运行的包

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKERFILE="$ROOT_DIR/Dockerfile.build"
IMAGE_NAME="predictflow-builder"
OUTPUT_DIR="$ROOT_DIR/dist"
OUTPUT_FILE="$OUTPUT_DIR/predictflow-api.shiv"

echo "=========================================="
echo "PredictFlow Docker 构建脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未找到 Docker"
    echo "   请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker 已安装: $(docker --version)"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 清理旧的打包文件
if [ -f "$OUTPUT_FILE" ]; then
    echo "==> 清理旧的打包文件"
    rm -f "$OUTPUT_FILE"
    echo "   已删除: $OUTPUT_FILE"
    echo ""
fi

# 检查 Dockerfile 是否存在
if [ ! -f "$DOCKERFILE" ]; then
    echo "❌ 错误: 未找到 Dockerfile: $DOCKERFILE"
    exit 1
fi

echo "==> 构建 Docker 镜像"
echo "   镜像名称: $IMAGE_NAME"
echo ""

# 检测并处理镜像源问题
echo "   正在尝试拉取基础镜像..."
echo "   如果遇到 403 Forbidden 错误，请运行: ./fix_docker_registry.sh"
echo ""

# 尝试使用多个镜像源，如果官方源失败则尝试其他源
BUILD_ARGS=""
USE_PLATFORM="linux/amd64"

# 检测是否需要使用平台参数（在 Apple Silicon Mac 上）
if [[ "$(uname -m)" == "arm64" ]] || [[ "$(uname -m)" == "aarch64" ]]; then
    # Apple Silicon Mac 需要指定平台来构建 x86_64 镜像
    USE_PLATFORM="linux/amd64"
    BUILD_ARGS="--platform $USE_PLATFORM"
    echo "   检测到 ARM 架构，将构建 Linux/AMD64 镜像"
fi

# 尝试构建，如果失败则提供解决方案
if ! docker build $BUILD_ARGS -f "$DOCKERFILE" -t "$IMAGE_NAME" "$ROOT_DIR" 2>&1 | tee /tmp/docker_build.log; then
    echo ""
    echo "❌ Docker 镜像构建失败"
    echo ""
    
    # 检查是否是镜像源问题
    if grep -q "403 Forbidden\|unauthorized\|pull access denied" /tmp/docker_build.log 2>/dev/null; then
        echo "⚠️  检测到镜像源访问问题（可能是 Docker 镜像源配置问题）"
        echo ""
        echo "解决方案："
        echo "1. 检查 Docker Desktop 设置中的镜像源配置"
        echo "2. 或者临时禁用镜像源，使用官方 Docker Hub："
        echo ""
        echo "   方法 A: 修改 Docker Desktop 设置"
        echo "   - 打开 Docker Desktop"
        echo "   - Settings -> Docker Engine"
        echo "   - 临时注释掉 registry-mirrors 配置"
        echo ""
        echo "   方法 B: 手动拉取镜像后重试"
        echo "   docker pull python:3.11-slim"
        echo "   # 然后重新运行此脚本"
        echo ""
        echo "   方法 C: 使用其他镜像源（修改 Docker Desktop 配置）"
        echo "   推荐镜像源："
        echo "   - 腾讯云: https://mirror.ccs.tencentyun.com"
        echo "   - 网易: https://hub-mirror.c.163.com"
        echo "   - 中科大: https://docker.mirrors.ustc.edu.cn"
    fi
    
    rm -f /tmp/docker_build.log
    exit 1
fi

rm -f /tmp/docker_build.log

echo ""
echo "✅ Docker 镜像构建成功"
echo ""

echo "==> 在容器中执行打包"
echo "   这将生成 Linux 兼容的 shiv 包"

# 运行容器并执行打包
# 如果指定了平台，运行时也需要指定
RUN_ARGS=""
if [[ -n "$BUILD_ARGS" ]]; then
    RUN_ARGS="--platform $USE_PLATFORM"
fi

docker run --rm $RUN_ARGS \
    -v "$OUTPUT_DIR:/output" \
    "$IMAGE_NAME"

if [ $? -ne 0 ]; then
    echo "❌ 打包过程失败"
    exit 1
fi

echo ""
if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "=========================================="
    echo "✅ 打包成功！"
    echo "=========================================="
    echo "   文件位置: $OUTPUT_FILE"
    echo "   文件大小: $FILE_SIZE"
    echo "   平台: Linux (x86_64)"
    echo ""
    echo "💡 使用说明:"
    echo "   在 Linux 系统上运行:"
    echo "   chmod +x $OUTPUT_FILE"
    echo "   $OUTPUT_FILE"
    echo ""
    echo "   或使用 Python 解释器:"
    echo "   python3 $OUTPUT_FILE"
    echo ""
    
    # 验证文件
    echo "==> 验证打包文件"
    if file "$OUTPUT_FILE" | grep -q "executable"; then
        echo "   ✅ 文件是可执行的"
    fi
    
    # 检查是否是 Python zip 文件
    if head -c 2 "$OUTPUT_FILE" | grep -q "PK"; then
        echo "   ✅ 文件格式正确（ZIP/Python）"
    fi
    
    echo ""
    echo "✨ 打包完成！文件已准备好部署到 Linux 系统。"
else
    echo "❌ 打包失败: 未找到生成的文件"
    exit 1
fi

echo ""
echo "==> 清理 Docker 镜像（可选）"
read -p "   是否删除构建镜像？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    echo "   ✅ 已清理构建镜像"
fi
