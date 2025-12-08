"""PredictFlow 打包配置，便于 shiv 安装本地代码与模型文件。"""

from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent
# model_files = [
#     str(path)
#     for path in (BASE_DIR / "models").glob("*.joblib")
#     if path.is_file()
# ]
# 使用固定的相对路径，避免打包时被认为是绝对路径
model_files = [
    "models/model.joblib",
    "models/load_model.joblib",
    "models/weather_model.joblib",
]

setup(
    name="predictflow",
    version="0.1.0",
    description="PredictFlow FastAPI backend",
    packages=find_packages(include=["api", "api.*", "scripts", "scripts.*", "models", "models.*"]),
    py_modules=["bootstrap", "config"],
    include_package_data=True,
    package_data={"models": ["*.joblib"]},
    # data_files=[("models", model_files)],
    install_requires=[],
)

