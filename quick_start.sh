#!/bin/bash
# PredictFlow 快速开始脚本

echo "================================"
echo "PredictFlow 快速开始向导"
echo "================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

echo "✓ Python3 已安装"
python3 --version
echo ""

# 安装依赖
echo "正在安装依赖包..."
pip3 install -r requirements.txt
echo ""
echo "✓ 依赖包安装完成"
echo ""

# 使用示例数据训练模型
echo "================================"
echo "使用示例数据训练模型"
echo "================================"
echo ""

python3 inspect_and_train.py example_data.csv --auto --out-model example_model.joblib

echo ""
echo "================================"
echo "✓ 训练完成！"
echo "================================"
echo ""

# 交互式预测示例
echo "现在可以进行预测了！"
echo ""
echo "1. 交互式预测："
echo "   python3 predict.py --model example_model.joblib --interactive"
echo ""
echo "2. 从文件预测："
echo "   python3 predict.py --model example_model.joblib --input your_data.csv --output predictions.csv"
echo ""
echo "3. 使用你自己的数据训练："
echo "   python3 inspect_and_train.py your_data.csv"
echo ""

