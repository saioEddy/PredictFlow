# main.py
# FastAPI 后端主文件
# 提供登录和预测接口

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
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

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

