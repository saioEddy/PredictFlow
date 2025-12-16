// 运行时环境配置文件
// 此文件会在构建时被复制到 build 目录
// 部署到 Tomcat 后，可以修改此文件来配置 API 地址，无需重新构建

window.env = {
  // API 基础URL配置说明：
  // 1. 如果后端在同一服务器，可以通过 Tomcat 配置反向代理，使用相对路径（空字符串或 '/api'）
  // 2. 如果后端在不同服务器，填写完整的后端地址，例如：'http://your-backend-server:8000'
  // 3. 如果使用相对路径，确保 Tomcat 已配置反向代理，将 /api/* 请求转发到后端服务器
  // 4. 本地开发时，如果后端运行在 localhost:8000，设置为 'http://localhost:8000'
  // 5. 生产环境部署时，可以设置为空字符串 '' 使用相对路径（需要配置反向代理）
  REACT_APP_API_URL: 'http://localhost:8000'  // 本地开发时建议改为: 'http://localhost:8000'
};

