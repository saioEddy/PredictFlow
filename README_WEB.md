# 预测平台 Web 应用

基于 React + FastAPI 的简单预测平台，用于调用训练好的Python预测模型。

## 功能特性

- ✅ 用户登录（简单认证，无需数据库）
- ✅ 预测界面（输入载荷和频率）
- ✅ 实时预测结果展示
- ✅ 响应式设计，界面简洁美观

## 技术栈

- **前端**: React 18 + React Router
- **后端**: FastAPI + Python
- **认证**: JWT Token

## 快速开始

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 3. 启动服务

#### 方式一：使用启动脚本（推荐）

**终端1 - 启动后端：**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**终端2 - 启动前端：**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

#### 方式二：手动启动

**启动后端：**
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端：**
```bash
cd frontend
npm start
```

### 4. 访问应用

- **前端地址**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 使用说明

### 登录

默认测试账号：
- 用户名: `admin`，密码: `admin123`
- 用户名: `user`，密码: `user123`

### 预测

1. 登录成功后进入预测页面
2. 输入**载荷**和**频率**值
3. 点击"开始预测"按钮
4. 查看预测结果

## 项目结构

```
PredictFlow/
├── api/                    # FastAPI后端
│   ├── __init__.py
│   └── main.py            # 主API文件
├── frontend/              # React前端
│   ├── public/
│   ├── src/
│   │   ├── components/    # React组件
│   │   │   ├── Login.js   # 登录页面
│   │   │   └── Predict.js # 预测页面
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── models/                # 模型文件目录
│   └── model.joblib      # 训练好的模型（需要存在）
├── start_backend.sh      # 后端启动脚本
├── start_frontend.sh     # 前端启动脚本
└── requirements.txt      # Python依赖
```

## API接口说明

### 登录接口

**POST** `/api/login`

请求体：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

响应：
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "登录成功"
}
```

### 预测接口

**POST** `/api/predict`

请求头：
```
Authorization: Bearer <token>
```

请求体：
```json
{
  "load": 0.2,
  "frequency": 1.5
}
```

响应：
```json
{
  "predictions": {
    "stress": 123.4567,
    "strain": 0.0123
  },
  "input_data": {
    "load": 0.2,
    "frequency": 1.5
  }
}
```

### 获取模型信息

**GET** `/api/model-info`

请求头：
```
Authorization: Bearer <token>
```

响应：
```json
{
  "inputs": ["载荷", "频率"],
  "outputs": ["应力", "应变"]
}
```

## 注意事项

1. **模型文件**: 确保 `models/model.joblib` 文件存在，否则后端无法启动
2. **端口冲突**: 如果8000或3000端口被占用，请修改启动命令中的端口号
3. **CORS配置**: 如果前端运行在不同端口，需要修改 `api/main.py` 中的CORS配置

## 修改登录账号

编辑 `api/main.py` 文件中的 `USERS` 字典：

```python
USERS = {
    "your_username": "your_password",
    # 添加更多用户...
}
```

## 修改模型路径

编辑 `api/main.py` 文件中的 `MODEL_PATH` 变量：

```python
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "your_model.joblib")
```

## 故障排除

### 后端启动失败

1. 检查模型文件是否存在
2. 检查Python依赖是否安装完整
3. 查看终端错误信息

### 前端无法连接后端

1. 确认后端服务已启动（访问 http://localhost:8000/docs 测试）
2. 检查 `frontend/src/components/` 中的 `API_BASE_URL` 是否正确
3. 检查CORS配置

### 预测失败

1. 检查输入的载荷和频率是否为有效数字
2. 查看浏览器控制台的错误信息
3. 查看后端终端的错误日志

## 开发建议

- 生产环境应使用环境变量管理敏感信息（如JWT密钥）
- 建议添加数据库存储用户信息
- 可以添加更多的输入验证和错误处理
- 可以添加预测历史记录功能

