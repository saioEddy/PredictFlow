# Docker 构建说明

## 概述

使用 Docker 在 Linux 容器中打包 PredictFlow 后端，可以确保生成的 `predictflow-api.shiv` 包在 Linux 系统上正常运行，即使在 macOS 或 Windows 上构建也是如此。

## 前置要求

1. **安装 Docker**
   - macOS: https://docs.docker.com/desktop/install/mac-install/
   - Linux: `sudo apt-get install docker.io` 或 `sudo yum install docker`
   - Windows: https://docs.docker.com/desktop/install/windows-install/

2. **验证 Docker 安装**
   ```bash
   docker --version
   docker ps  # 测试 Docker 是否正常运行
   ```

## 使用方法

### 方法 1: 使用 Docker 构建脚本（推荐）

```bash
# 直接运行 Docker 构建脚本
./build_backend_docker.sh
```

这个脚本会：
1. 检查 Docker 是否安装
2. 构建 Docker 镜像
3. 在容器中执行打包
4. 将打包好的文件输出到 `dist/predictflow-api.shiv`
5. 验证打包结果

### 方法 2: 使用一键打包脚本

```bash
# 使用 Docker 模式打包前后端
USE_DOCKER=true ./build_all.sh

# 或
./build_all.sh --docker
```

### 方法 3: 手动使用 Docker

```bash
# 1. 构建镜像
docker build -f Dockerfile.build -t predictflow-builder .

# 2. 运行容器进行打包
docker run --rm \
    -v "$(pwd)/dist:/output" \
    predictflow-builder

# 3. 打包完成后，文件会在 dist/predictflow-api.shiv
```

## 输出文件

打包完成后，Linux 兼容的 shiv 包会生成在：
```
dist/predictflow-api.shiv
```

## 在 Linux 系统上运行

将 `predictflow-api.shiv` 传输到目标 Linux 系统后：

```bash
# 方法 1: 直接运行（需要执行权限）
chmod +x predictflow-api.shiv
./predictflow-api.shiv

# 方法 2: 使用 Python 解释器
python3 predictflow-api.shiv

# 方法 3: 使用便携式 Python
./python-portable/bin/python3 predictflow-api.shiv
```

## 优势

✅ **跨平台构建**: 在 macOS/Windows 上也能生成 Linux 包  
✅ **环境一致**: 使用官方 Python 镜像，确保依赖版本一致  
✅ **隔离构建**: 不影响本地 Python 环境  
✅ **可重复**: 每次构建环境完全相同  

## 故障排查

### 问题 1: 镜像拉取失败 (403 Forbidden)

**错误信息**: `ERROR: failed to solve: python:3.11-slim: unexpected status from HEAD request... 403 Forbidden`

**原因**: Docker 配置的镜像源（如阿里云）返回 403 错误，无法访问。

**解决方案**:

**方法 1: 使用修复脚本（推荐）**
```bash
./fix_docker_registry.sh
```

**方法 2: 修改 Docker Desktop 镜像源配置**

1. 打开 Docker Desktop
2. 点击 **Settings** (设置) 图标
3. 选择 **Docker Engine**
4. 修改配置，删除或替换有问题的镜像源

**推荐配置（选择其一）:**

- **使用官方 Docker Hub**（如果网络允许）:
```json
{
  "registry-mirrors": []
}
```

- **使用腾讯云镜像源**:
```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

- **使用网易镜像源**:
```json
{
  "registry-mirrors": [
    "https://hub-mirror.c.163.com"
  ]
}
```

- **使用中科大镜像源**:
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```

5. 点击 **Apply & Restart** 重启 Docker
6. 重新运行构建脚本

**方法 3: 手动拉取镜像**
```bash
# 先拉取基础镜像
docker pull python:3.11-slim

# 然后运行构建脚本
./build_backend_docker.sh
```

### 问题 2: Docker 未启动

```bash
# macOS: 启动 Docker Desktop
# Linux: 启动 Docker 服务
sudo systemctl start docker
```

### 问题 2: 权限问题

```bash
# Linux 上可能需要添加用户到 docker 组
sudo usermod -aG docker $USER
# 然后重新登录
```

### 问题 3: 构建失败

```bash
# 查看详细构建日志
docker build -f Dockerfile.build -t predictflow-builder . --progress=plain --no-cache

# 进入容器调试
docker run -it --rm predictflow-builder /bin/bash
```

### 问题 4: 文件未生成

确保输出目录存在且有写入权限：
```bash
mkdir -p dist
chmod 755 dist
```

### 问题 5: Apple Silicon Mac 构建问题

如果你使用的是 Apple Silicon Mac (M1/M2/M3)，Docker 可能需要使用 `--platform` 参数来构建 Linux/x86_64 镜像。

构建脚本已自动处理此问题，但如果有问题，可以手动指定：

```bash
docker build --platform linux/amd64 -f Dockerfile.build -t predictflow-builder .
docker run --rm --platform linux/amd64 -v "$(pwd)/dist:/output" predictflow-builder
```

## 清理

```bash
# 删除构建镜像
docker rmi predictflow-builder

# 清理所有未使用的 Docker 资源
docker system prune
```
