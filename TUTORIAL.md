# PredictFlow 详细教程

本教程将带你逐步了解如何使用 PredictFlow 进行数据探索、模型训练和预测。

## 目录

1. [环境准备](#1-环境准备)
2. [快速体验](#2-快速体验)
3. [使用自己的数据](#3-使用自己的数据)
4. [理解输出结果](#4-理解输出结果)
5. [模型预测](#5-模型预测)
6. [高级用法](#6-高级用法)
7. [常见场景](#7-常见场景)

---

## 1. 环境准备

### 1.1 安装依赖

```bash
cd /path/to/PredictFlow
pip install -r requirements.txt
```

### 1.2 验证安装

```bash
python -c "import pandas, sklearn, joblib; print('所有依赖已安装成功！')"
```

---

## 2. 快速体验

### 2.1 使用示例数据训练

项目自带了一个示例数据文件 `example_data.csv`，包含：
- **输入列**: `frequency_multiple`（频率倍数）, `load_multiple`（载荷倍数）
- **输出列**: `stress`（应力）, `strain`（应变）, `temperature`（温度）, `life`（寿命）

运行自动训练：

```bash
python inspect_and_train.py example_data.csv --auto
```

你会看到：
```
已加载数据，行数=50, 列数=6

=== 列信息 ===
  0. frequency_multiple    类型=float64    缺失值=0
  1. load_multiple         类型=float64    缺失值=0
  2. stress                类型=float64    缺失值=0
  ...

最终选定的输入列： ['frequency_multiple', 'load_multiple']
最终选定的输出列： ['stress', 'strain', 'temperature', 'life']

开始训练模型...
训练完成！

=== 模型评估结果 ===
stress               -> R2: 0.9998  MAE: 0.9876
strain               -> R2: 0.9998  MAE: 0.0001
temperature          -> R2: 0.9997  MAE: 0.1234
life                 -> R2: 0.9989  MAE: 34.5678

模型已保存到: model.joblib
```

### 2.2 使用模型预测

现在使用训练好的模型对新数据进行预测：

```bash
python predict.py --model model.joblib --input new_data_for_prediction.csv --output predictions.csv
```

查看预测结果：

```bash
cat predictions.csv
```

---

## 3. 使用自己的数据

### 3.1 准备数据

确保你的数据文件（CSV 或 Excel）包含：
- **输入列**：影响因素（如频率、载荷、压力等）
- **输出列**：你想预测的目标（如应力、温度、寿命等）

示例数据格式：

| freq | load | output1 | output2 |
|------|------|---------|---------|
| 1.0  | 1.5  | 100.5   | 0.023   |
| 1.2  | 2.0  | 125.8   | 0.031   |
| ...  | ...  | ...     | ...     |

### 3.2 交互式训练（推荐新手）

```bash
python inspect_and_train.py your_data.csv
```

脚本会：
1. 展示所有列名和类型
2. 自动识别可能的输入输出列
3. 显示相关性分析
4. 等待你确认

你可以：
- **直接按回车**：接受自动识别的列
- **输入列名**：例如 `freq,load`（逗号分隔）
- **输入索引**：例如 `0,1`（从列信息中查看索引号）

### 3.3 自动训练（适合确定列名时）

如果你知道哪些是输入列、哪些是输出列：

```bash
python inspect_and_train.py your_data.csv \
    --inputs freq,load,pressure \
    --outputs stress,temperature,life \
    --out-model my_model.joblib
```

### 3.4 纯自动模式（无需人工干预）

完全依赖自动识别：

```bash
python inspect_and_train.py your_data.csv --auto
```

---

## 4. 理解输出结果

### 4.1 列信息

```
=== 列信息 ===
  0. frequency_multiple    类型=float64    缺失值=0
  1. load_multiple         类型=float64    缺失值=0
```

- **索引**：用于快速选择列
- **类型**：数据类型（float64、int64、object等）
- **缺失值**：该列中缺失数据的数量

### 4.2 相关性分析

```
=== 输入-输出相关性分析 ===
-- frequency_multiple 与输出列的相关性 --
stress    0.8523    # 强正相关
strain    0.7891    # 较强正相关
life     -0.6234    # 较强负相关（频率越高，寿命越短）
```

相关系数范围：`-1` 到 `+1`
- **接近 +1**：强正相关（一起增大）
- **接近 -1**：强负相关（一个增大另一个减小）
- **接近 0**：无线性关系

### 4.3 评估指标

**R² 分数 (R-squared)**
- 范围：0 到 1（可能为负）
- **> 0.9**：非常好
- **0.7 - 0.9**：良好
- **0.5 - 0.7**：中等
- **< 0.5**：较差，可能需要重新考虑特征选择

**MAE (Mean Absolute Error，平均绝对误差)**
- 越小越好
- 表示预测值与真实值的平均差距
- 单位与输出变量相同

---

## 5. 模型预测

### 5.1 从文件预测

准备包含输入列的新数据文件：

```csv
frequency_multiple,load_multiple
1.3,1.8
2.1,2.3
```

运行预测：

```bash
python predict.py --model model.joblib --input new_data.csv --output results.csv
```

### 5.2 交互式预测

逐个输入数据，实时获取预测：

```bash
python predict.py --model model.joblib --interactive
```

示例交互：
```
请输入 frequency_multiple: 1.5
请输入 load_multiple: 2.0

预测结果:
  stress: 241.5234
  strain: 0.0362
  temperature: 91.7345
  life: 9567.2341
```

### 5.3 只查看结果不保存

```bash
python predict.py --model model.joblib --input new_data.csv
```

结果会显示在终端，但不保存文件。

---

## 6. 高级用法

### 6.1 修改模型参数

编辑 `inspect_and_train.py` 中的模型配置：

```python
base = RandomForestRegressor(
    n_estimators=500,        # 增加树的数量（更准确但更慢）
    max_depth=20,            # 限制树的深度（防止过拟合）
    min_samples_split=5,     # 节点分裂所需的最小样本数
    n_jobs=-1,               # 使用所有CPU核心
    random_state=42
)
```

### 6.2 使用配置文件

项目提供了 `config.py` 配置文件，可以集中管理所有参数：

```python
# config.py
RF_N_ESTIMATORS = 300
TEST_SIZE = 0.25
FUZZY_INPUT_KEYS = ["freq", "load", "custom_keyword"]
```

### 6.3 添加自定义识别规则

如果你的数据列名不符合默认规则，编辑 `inspect_and_train.py`：

```python
FUZZY_INPUT_KEYS = [
    # 默认规则
    "freq", "frequency", "频率",
    # 添加你的规则
    "rpm", "转速", "cycles", "周期"
]
```

### 6.4 更换机器学习算法

替换为 XGBoost：

```python
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor

base = XGBRegressor(n_estimators=200, learning_rate=0.1)
model = MultiOutputRegressor(base)
```

### 6.5 批量训练多个模型

创建脚本 `batch_train.sh`：

```bash
#!/bin/bash
for file in data/*.csv; do
    echo "训练: $file"
    python inspect_and_train.py "$file" --auto --out-model "models/$(basename $file .csv).joblib"
done
```

---

## 7. 常见场景

### 场景1：列名不确定，需要人工判断

```bash
# 1. 先查看数据结构
python inspect_and_train.py mystery_data.csv
# 2. 根据输出的列信息，手动输入列名或索引
# 3. 完成训练
```

### 场景2：自动化批处理（CI/CD）

```bash
python inspect_and_train.py data.csv \
    --inputs col1,col2,col3 \
    --outputs target1,target2 \
    --auto
```

### 场景3：模型评估分数低

可能原因及解决方案：

**1. 输入特征选择不合理**
```bash
# 重新查看相关性分析，选择相关性高的列
python inspect_and_train.py data.csv
```

**2. 数据质量问题**
- 检查缺失值是否过多
- 检查是否有异常值
- 考虑数据清洗

**3. 需要特征工程**
- 添加交互特征：`freq * load`
- 添加多项式特征：`freq^2`, `load^2`
- 对数变换、标准化等

**4. 模型不适合**
- 尝试 XGBoost、LightGBM
- 尝试神经网络
- 调整超参数

### 场景4：数据量很大（>100万行）

```python
# 修改 inspect_and_train.py，使用采样
df = load_data(args.path)
if len(df) > 100000:
    df = df.sample(n=100000, random_state=42)
    print("数据量过大，已采样10万条数据用于训练")
```

### 场景5：需要实时API预测

创建 Flask API（示例）：

```python
# app.py
from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)
model_data = joblib.load('model.joblib')
model = model_data['model']
inputs = model_data['inputs']
outputs = model_data['outputs']

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    X = pd.DataFrame([data])[inputs]
    pred = model.predict(X)
    result = {outputs[i]: float(pred[0][i]) for i in range(len(outputs))}
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

运行：
```bash
pip install flask
python app.py
```

测试：
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"frequency_multiple": 1.5, "load_multiple": 2.0}'
```

---

## 小结

PredictFlow 提供了：
- ✅ 自动化的数据探索
- ✅ 智能的列识别
- ✅ 灵活的训练模式
- ✅ 便捷的预测功能

无论你是机器学习新手还是经验丰富的数据科学家，都可以快速上手并根据需求定制。

**祝你使用愉快！有问题随时查阅文档或提 Issue。** 🚀

