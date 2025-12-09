# main.py
# FastAPI 后端主文件
# 提供登录和预测接口

from fastapi import FastAPI, HTTPException, Depends, status, Request
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
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from predict import load_model, prepare_input_data

app = FastAPI(title="预测平台API", version="1.0.0")

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求的详细信息"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"[请求] {request.method} {request.url.path}")
    logger.info(f"      客户端: {request.client.host if request.client else 'unknown'}:{request.client.port if request.client else 'unknown'}")
    logger.info(f"      查询参数: {dict(request.query_params)}")
    
    # 处理请求
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"[响应] {request.method} {request.url.path} - 状态码: {response.status_code} - 耗时: {process_time:.3f}秒")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[错误] {request.method} {request.url.path} - 异常: {str(e)} - 耗时: {process_time:.3f}秒")
        raise

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
    logger.info("=" * 60)
    logger.info("FastAPI 应用启动中...")
    logger.info("=" * 60)
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"Python 路径: {sys.path}")
    logger.info(f"模型文件路径: {MODEL_PATH}")
    logger.info(f"模型文件是否存在: {os.path.exists(MODEL_PATH)}")
    
    try:
        if os.path.exists(MODEL_PATH):
            logger.info(f"开始加载模型: {MODEL_PATH}")
            model_data = load_model(MODEL_PATH)
            logger.info(f"✓ 模型加载成功: {MODEL_PATH}")
            logger.info(f"  输入列: {model_data['inputs']}")
            logger.info(f"  输出列: {model_data['outputs']}")
            logger.info(f"  模型类型: {type(model_data['model'])}")
        else:
            logger.warning(f"⚠ 警告: 模型文件不存在: {MODEL_PATH}")
            logger.warning(f"  请确保模型文件存在于 models/ 目录下")
            logger.warning(f"  当前目录内容: {os.listdir(os.path.dirname(MODEL_PATH) if os.path.dirname(MODEL_PATH) else '.')}")
    except Exception as e:
        logger.error(f"✗ 模型加载失败: {str(e)}")
        logger.exception(e)  # 打印完整的异常堆栈
    
    logger.info("=" * 60)
    logger.info("FastAPI 应用启动完成，准备接收请求")
    logger.info("=" * 60)

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
    logger.info(f"[登录] 收到登录请求，用户名: {login_data.username}")
    username = login_data.username
    password = login_data.password
    
    if username in USERS and USERS[username] == password:
        token = create_access_token(username)
        logger.info(f"[登录] 登录成功: {username}")
        return {
            "success": True,
            "token": token,
            "message": "登录成功"
        }
    else:
        logger.warning(f"[登录] 登录失败: 用户名或密码错误 - {username}")
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
    """健康检查端点，用于验证服务是否正常运行"""
    logger.info("[健康检查] 收到健康检查请求")
    result = {
        "status": "ok",
        "model_loaded": model_data is not None,
        "timestamp": datetime.now().isoformat()
    }
    if model_data is not None:
        result["model_info"] = {
            "inputs": model_data['inputs'],
            "outputs": model_data['outputs']
        }
    logger.info(f"[健康检查] 返回结果: {result}")
    return result

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
    logger.info("=" * 60)
    logger.info("直接运行 main.py，启动服务...")
    logger.info("=" * 60)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        use_colors=True
    )

