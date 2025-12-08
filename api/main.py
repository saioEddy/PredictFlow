# main.py
# FastAPI 后端主文件
# 提供登录和预测接口

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import sys
import pandas as pd
import joblib
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from predict import load_model, prepare_input_data

app = FastAPI(title="预测平台API", version="1.0.0")

# 配置CORS，允许前端访问（如果前后端分离部署）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应限制）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务配置
# 尝试挂载前端构建目录（如果存在）
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
FRONTEND_DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "dist", "full-release", "frontend-build")

# 优先使用 full-release 中的前端文件，其次使用 frontend/build
static_dir = None
if os.path.exists(FRONTEND_DIST_DIR):
    static_dir = FRONTEND_DIST_DIR
elif os.path.exists(FRONTEND_BUILD_DIR):
    static_dir = FRONTEND_BUILD_DIR

if static_dir:
    # 挂载静态资源目录（CSS, JS 等）
    static_resources_dir = os.path.join(static_dir, "static")
    if os.path.exists(static_resources_dir):
        static_files = StaticFiles(directory=static_resources_dir)
        app.mount("/static", static_files, name="static")
    
    # 为 React Router 提供支持：所有非 API 路径返回 index.html
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # 排除 API 路径和 static 路径
        if full_path.startswith("api/") or full_path.startswith("static/"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # 如果请求的是文件（有扩展名），尝试返回该文件
        if "." in full_path.split("/")[-1]:
            file_path = os.path.join(static_dir, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
        
        # 其他情况返回 index.html（支持 React Router）
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")

# 简单的用户认证（不需要数据库）
# 实际项目中应该使用数据库和密码哈希
USERS = {
    "admin": "admin123",  # 用户名: 密码
    "user": "user123"
}

# JWT密钥（简单示例，生产环境应使用环境变量）
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# 模型路径
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.joblib")

# 全局变量存储加载的模型
model_data = None

# 请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

class PredictRequest(BaseModel):
    load: float  # 载荷
    frequency: float  # 频率

class PredictResponse(BaseModel):
    predictions: dict  # 预测结果字典
    input_data: dict  # 输入的载荷和频率

# 加载模型（启动时加载一次）
@app.on_event("startup")
async def load_model_on_startup():
    global model_data
    try:
        if os.path.exists(MODEL_PATH):
            model_data = load_model(MODEL_PATH)
            print(f"✓ 模型加载成功: {MODEL_PATH}")
            print(f"  输入列: {model_data['inputs']}")
            print(f"  输出列: {model_data['outputs']}")
        else:
            print(f"⚠ 警告: 模型文件不存在: {MODEL_PATH}")
            print(f"  请确保模型文件存在于 models/ 目录下")
    except Exception as e:
        print(f"✗ 模型加载失败: {str(e)}")

# 生成JWT token
def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": username,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# 验证JWT token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的token")

# 登录接口
@app.post("/api/login")
async def login(login_data: LoginRequest):
    username = login_data.username
    password = login_data.password
    
    if username in USERS and USERS[username] == password:
        token = create_access_token(username)
        return {
            "success": True,
            "token": token,
            "message": "登录成功"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

# 预测接口
@app.post("/api/predict", response_model=PredictResponse)
async def predict(predict_data: PredictRequest, username: str = Depends(verify_token)):
    global model_data
    
    if model_data is None:
        raise HTTPException(status_code=500, detail="模型未加载，请检查模型文件")
    
    try:
        model = model_data['model']
        inputs = model_data['inputs']
        outputs = model_data['outputs']
        
        # 构建输入数据字典
        # 需要匹配模型的输入列名（可能是"载荷"、"频率"或英文列名）
        input_dict = {}
        
        # 尝试匹配输入列名（支持中英文）
        for col in inputs:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['load', '载荷', '载重', 'payload']):
                input_dict[col] = predict_data.load
            elif any(keyword in col_lower for keyword in ['freq', 'frequency', '频率', '倍数']):
                input_dict[col] = predict_data.frequency
            else:
                # 如果无法匹配，使用第一个输入列作为载荷，第二个作为频率
                # 这是一个fallback策略
                pass
        
        # 如果匹配失败，按顺序分配（假设第一个是载荷，第二个是频率）
        if len(input_dict) < len(inputs):
            for i, col in enumerate(inputs):
                if col not in input_dict:
                    if i == 0:
                        input_dict[col] = predict_data.load
                    elif i == 1:
                        input_dict[col] = predict_data.frequency
                    else:
                        input_dict[col] = 0  # 默认值
        
        # 准备输入数据
        X = prepare_input_data(input_dict, inputs)
        
        # 进行预测
        predictions = model.predict(X)
        
        # 构建结果字典
        result_dict = {}
        for i, output_name in enumerate(outputs):
            result_dict[output_name] = float(predictions[0][i])
        
        return PredictResponse(
            predictions=result_dict,
            input_data={
                "load": predict_data.load,
                "frequency": predict_data.frequency
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

# 健康检查接口
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": model_data is not None
    }

# 获取模型信息接口
@app.get("/api/model-info")
async def get_model_info(username: str = Depends(verify_token)):
    if model_data is None:
        raise HTTPException(status_code=500, detail="模型未加载")
    
    return {
        "inputs": model_data['inputs'],
        "outputs": model_data['outputs']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

