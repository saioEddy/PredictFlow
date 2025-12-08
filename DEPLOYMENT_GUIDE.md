# PredictFlow 部署指南

## 部署方式

项目支持两种部署方式：

### 方案 1: FastAPI 集成部署（推荐）

FastAPI 同时提供前端静态文件和后端 API 服务，单端口部署。

**优势：**
- ✅ 单端口，部署简单
- ✅ 无需处理跨域问题
- ✅ 适合生产环境

**启动方式：**

```bash
# 方式1: 使用启动脚本（推荐）
./start_server.sh

# 方式2: 直接运行后端（会自动检测并服务前端）
python3 dist/predictflow-api.shiv

# 或使用 Python 直接运行
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**访问地址：**
- 前端界面: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

### 方案 2: 前后端分离部署

使用 Python HTTP Server 提供前端，FastAPI 提供后端 API。

**优势：**
- ✅ 前后端完全分离
- ✅ 前端可以使用任何 HTTP 服务器（nginx, Apache 等）

**启动方式：**

**步骤 1: 启动后端服务**

```bash
# 使用 shiv 包
python3 dist/predictflow-api.shiv

# 或使用 Python 直接运行
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**步骤 2: 启动前端服务**

```bash
# 方式1: 使用脚本（默认端口 80）
./start_frontend_http.sh

# 方式2: 使用脚本指定端口
./start_frontend_http.sh 8080

# 方式3: 手动启动
cd frontend/build
python3 -m http.server 80
```

**或使用一键启动脚本：**

```bash
# 使用分离模式启动
./start_server.sh --separate
```

**访问地址：**
- 前端界面: http://localhost:80
- 后端 API: http://localhost:8000

**注意：** 使用端口 80 需要 root 权限，可以使用其他端口（如 8080）。

---

## 打包部署

### 完整打包

```bash
# 打包前后端
./build_all.sh

# 或使用 Docker 打包后端（Linux 兼容）
USE_DOCKER=true ./build_all.sh
```

打包后的文件在 `dist/full-release/` 目录：
- `predictflow-api.shiv` - 后端服务包
- `frontend-build/` - 前端静态文件

### 部署到 Linux 服务器

**步骤 1: 传输文件**

```bash
# 将 dist/full-release/ 目录传输到服务器
scp -r dist/full-release/ user@server:/opt/predictflow/
```

**步骤 2: 在服务器上部署**

```bash
# 登录服务器
ssh user@server

# 进入部署目录
cd /opt/predictflow

# 使用方案1（推荐）：单服务部署
python3 predictflow-api.shiv

# 或使用方案2：前后端分离
# 终端1: 启动后端
python3 predictflow-api.shiv

# 终端2: 启动前端
cd frontend-build
python3 -m http.server 80
```

---

## 环境变量配置

### 前端 API 地址配置

如果使用方案2（前后端分离），需要配置前端 API 地址：

**方法1: 构建时配置**

```bash
export REACT_APP_API_URL=http://your-api-server:8000
npm run build
```

**方法2: 修改前端代码**

前端代码已经支持相对路径，如果不设置 `REACT_APP_API_URL`，会使用相对路径调用 API（适用于方案1）。

---

## 使用 systemd 管理服务（Linux）

### 创建后端服务

创建文件 `/etc/systemd/system/predictflow-api.service`:

```ini
[Unit]
Description=PredictFlow API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/predictflow
ExecStart=/usr/bin/python3 /opt/predictflow/predictflow-api.shiv
Restart=always
RestartSec=10
Environment="HOST=0.0.0.0"
Environment="PORT=8000"

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable predictflow-api
sudo systemctl start predictflow-api
sudo systemctl status predictflow-api
```

### 创建前端服务（方案2）

创建文件 `/etc/systemd/system/predictflow-frontend.service`:

```ini
[Unit]
Description=PredictFlow Frontend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/predictflow/frontend-build
ExecStart=/usr/bin/python3 -m http.server 80
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable predictflow-frontend
sudo systemctl start predictflow-frontend
sudo systemctl status predictflow-frontend
```

---

## 端口配置

### 修改后端端口

```bash
# 使用环境变量
export PORT=8000
python3 predictflow-api.shiv

# 或直接修改 bootstrap.py
```

### 修改前端端口（方案2）

```bash
# 使用脚本
./start_frontend_http.sh 8080

# 或手动启动
python3 -m http.server 8080
```

---

## 常见问题

### 问题1: 前端无法访问后端 API

**方案1 部署：** 确保后端服务正常启动，前端会通过相对路径访问 API。

**方案2 部署：** 
- 检查后端是否运行在正确的端口
- 检查前端代码中的 API 地址配置
- 检查 CORS 配置

### 问题2: 端口 80 需要 root 权限

使用其他端口（如 8080），或使用 nginx 反向代理。

### 问题3: React Router 路由不工作

确保服务器配置正确：
- **方案1**: FastAPI 已自动配置支持 React Router
- **方案2**: 需要配置服务器支持 SPA（单页应用），所有路径返回 `index.html`

---

## 推荐配置

**生产环境推荐：**
- ✅ 使用方案1（FastAPI 集成部署）
- ✅ 使用 nginx 作为反向代理（可选）
- ✅ 使用 systemd 管理服务
- ✅ 配置防火墙规则

**开发环境：**
- ✅ 使用方案1，方便调试
- ✅ 或使用 `npm start` 启动前端开发服务器
