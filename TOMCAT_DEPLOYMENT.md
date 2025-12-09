# Tomcat 部署指南

## 概述

本指南说明如何将 PredictFlow 前端部署到 Tomcat 服务器。

## 部署步骤

### 1. 构建前端

```bash
cd frontend
npm install
npm run build
```

构建完成后，`frontend/build` 目录包含所有静态资源文件。

### 2. 配置 API 地址

部署到 Tomcat 前，需要配置后端 API 地址。有两种方式：

#### 方式 1：使用相对路径（推荐，适用于后端在同一服务器）

如果后端也在同一服务器，可以通过 Tomcat 配置反向代理。

1. 修改 `frontend/build/env-config.js`：

```javascript
window.env = {
  REACT_APP_API_URL: ''  // 使用相对路径
};
```

2. 配置 Tomcat 反向代理（见下方配置说明）

#### 方式 2：使用绝对路径（适用于后端在不同服务器）

如果后端在不同服务器，直接配置后端地址：

```javascript
window.env = {
  REACT_APP_API_URL: 'http://your-backend-server:8000'
};
```

### 3. 部署到 Tomcat

#### 方法 A：部署为 ROOT 应用（推荐）

1. 将 `frontend/build` 目录下的所有文件复制到 Tomcat 的 `webapps/ROOT` 目录：

```bash
# 清空 ROOT 目录（注意备份）
rm -rf $CATALINA_HOME/webapps/ROOT/*

# 复制构建文件
cp -r frontend/build/* $CATALINA_HOME/webapps/ROOT/
```

2. 访问地址：`http://your-server:8080`

#### 方法 B：部署为独立应用

1. 将 `frontend/build` 目录重命名为应用名（如 `predictflow`）

```bash
cp -r frontend/build $CATALINA_HOME/webapps/predictflow
```

2. 访问地址：`http://your-server:8080/predictflow`

### 4. 配置 Tomcat 反向代理（如果使用相对路径）

如果使用相对路径，需要配置 Tomcat 将 `/api/*` 请求转发到后端服务器。

#### 方式 1：使用 AJP 连接器（推荐）

在 `server.xml` 中添加 AJP 连接器配置，然后使用 Apache HTTP Server 或 Nginx 作为反向代理。

#### 方式 2：使用 Nginx 作为前端代理

在 Nginx 配置中添加：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/tomcat/webapps/ROOT;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 方式 3：使用 Tomcat 的 RewriteValve

在 `server.xml` 的 `<Host>` 标签中添加：

```xml
<Valve className="org.apache.catalina.valves.rewrite.RewriteValve" />
```

在 `META-INF/context.xml` 或 `conf/Catalina/localhost/ROOT.xml` 中添加重写规则（需要安装 rewrite 模块）。

### 5. 配置 React Router 支持

由于使用了 React Router，需要确保所有路由都返回 `index.html`。

#### 方法 1：使用 Tomcat 的 ErrorPage（简单但不完美）

在 `web.xml` 中添加：

```xml
<error-page>
    <error-code>404</error-code>
    <location>/index.html</location>
</error-page>
```

#### 方法 2：使用 Nginx（推荐）

在 Nginx 配置中使用 `try_files`：

```nginx
location / {
    root /path/to/tomcat/webapps/ROOT;
    try_files $uri $uri/ /index.html;
}
```

## 配置说明

### API_BASE_URL 配置优先级

代码中的 API 地址配置按以下优先级：

1. **运行时配置**（`window.env.REACT_APP_API_URL`）- 最高优先级
   - 适用于生产环境，无需重新构建即可修改
   - 修改 `build/env-config.js` 文件即可

2. **构建时环境变量**（`process.env.REACT_APP_API_URL`）
   - 构建时设置：`REACT_APP_API_URL=http://api.example.com npm run build`
   - 适用于 CI/CD 自动化构建

3. **相对路径**（空字符串）- 默认值
   - 适用于后端在同一域名下
   - 需要配置反向代理

### 修改 API 地址

部署后如需修改 API 地址，只需编辑 `webapps/ROOT/env-config.js`（或对应应用目录下的文件）：

```javascript
window.env = {
  REACT_APP_API_URL: 'http://new-api-server:8000'
};
```

修改后重启 Tomcat 或清除浏览器缓存即可生效。

## 常见问题

### 1. 前端无法访问后端 API

**问题**：使用相对路径时，前端请求 `/api/login` 返回 404。

**解决方案**：
- 检查是否配置了反向代理
- 检查 `env-config.js` 中的配置是否正确
- 检查后端服务是否正常运行

### 2. React Router 路由不工作

**问题**：刷新页面或直接访问路由时返回 404。

**解决方案**：
- 确保配置了所有路由返回 `index.html`（见上方配置说明）
- 使用 Nginx 的 `try_files` 是最可靠的方案

### 3. 跨域问题

**问题**：浏览器控制台显示 CORS 错误。

**解决方案**：
- 如果使用相对路径，不会有跨域问题
- 如果使用绝对路径，确保后端配置了 CORS 允许前端域名

### 4. 静态资源 404

**问题**：CSS、JS 文件加载失败。

**解决方案**：
- 检查文件路径是否正确
- 如果部署在子路径（如 `/predictflow`），需要配置 `package.json` 中的 `homepage` 字段：
  ```json
  {
    "homepage": "/predictflow"
  }
  ```
  然后重新构建。

## 推荐配置

**生产环境推荐**：
- ✅ 使用 Nginx 作为反向代理
- ✅ 使用相对路径配置 API 地址
- ✅ 部署为 ROOT 应用（简化 URL）
- ✅ 配置 HTTPS
- ✅ 使用 systemd 管理 Tomcat 服务

## 验证部署

部署完成后，访问应用并检查：

1. 前端页面正常加载
2. 登录功能正常
3. API 请求成功（检查浏览器开发者工具的 Network 标签）
4. React Router 路由正常工作（刷新页面测试）

