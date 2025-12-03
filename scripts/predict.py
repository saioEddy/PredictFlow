# predict.py
# 模型预测脚本
# 功能：加载训练好的模型，对新数据进行预测

import argparse
import sys
import os
import pandas as pd
import numpy as np
import joblib

def load_model(model_path):
    """
    加载训练好的模型
    
    参数:
        model_path: 模型文件路径
    
    返回:
        包含模型、输入列名、输出列名的字典
    """
    if not os.path.exists(model_path):
        print(f"错误：模型文件不存在: {model_path}")
        sys.exit(1)
    
    model_data = joblib.load(model_path)
    print(f"已加载模型: {model_path}")
    print(f"输入列: {model_data['inputs']}")
    print(f"输出列: {model_data['outputs']}")
    
    return model_data

def prepare_input_data(data, expected_inputs):
    """
    准备输入数据，确保列顺序和名称正确
    
    参数:
        data: 输入数据 (DataFrame 或 dict 或 list)
        expected_inputs: 期望的输入列名列表
    
    返回:
        准备好的输入DataFrame
    """
    # 如果是字典或列表，转换为DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], dict):
            df = pd.DataFrame(data)
        else:
            # 假设是单行数据
            df = pd.DataFrame([data], columns=expected_inputs)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("不支持的数据类型")
    
    # 检查是否包含所有必需的列
    missing_cols = set(expected_inputs) - set(df.columns)
    if missing_cols:
        print(f"警告：缺少输入列: {missing_cols}")
        print(f"可用的列: {df.columns.tolist()}")
        raise ValueError(f"输入数据缺少必需的列: {missing_cols}")
    
    # 选择并排序列
    df = df[expected_inputs]
    
    # 确保数值类型
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 检查缺失值
    if df.isna().any().any():
        print("警告：输入数据包含缺失值，将用0填充")
        df = df.fillna(0)
    
    return df

def predict_from_file(model_path, input_file, output_file=None):
    """
    从文件读取数据并预测
    
    参数:
        model_path: 模型文件路径
        input_file: 输入数据文件路径 (CSV/Excel)
        output_file: 输出结果文件路径（可选）
    
    返回:
        预测结果DataFrame
    """
    # 加载模型
    model_data = load_model(model_path)
    model = model_data['model']
    inputs = model_data['inputs']
    outputs = model_data['outputs']
    
    # 读取输入数据
    print(f"\n正在读取输入文件: {input_file}")
    if input_file.lower().endswith('.csv'):
        input_df = pd.read_csv(input_file)
    elif input_file.lower().endswith(('.xls', '.xlsx')):
        input_df = pd.read_excel(input_file)
    else:
        try:
            input_df = pd.read_csv(input_file)
        except:
            input_df = pd.read_excel(input_file)
    
    print(f"读取到 {len(input_df)} 条数据")
    
    # 准备输入数据
    X = prepare_input_data(input_df, inputs)
    
    print("\n输入数据预览:")
    print(X.head())
    
    # 预测
    print("\n正在进行预测...")
    predictions = model.predict(X)
    
    # 构建结果DataFrame
    result_df = pd.DataFrame(predictions, columns=outputs, index=X.index)
    
    # 合并原始输入和预测结果
    full_result = pd.concat([X, result_df], axis=1)
    
    print("\n预测结果预览:")
    print(full_result.head())
    
    # 保存结果
    if output_file:
        if output_file.lower().endswith('.csv'):
            full_result.to_csv(output_file, index=False)
        elif output_file.lower().endswith(('.xls', '.xlsx')):
            full_result.to_excel(output_file, index=False)
        else:
            full_result.to_csv(output_file, index=False)
        print(f"\n预测结果已保存到: {output_file}")
    
    return full_result

def predict_interactive(model_path):
    """
    交互式预测模式
    
    参数:
        model_path: 模型文件路径
    """
    # 加载模型
    model_data = load_model(model_path)
    model = model_data['model']
    inputs = model_data['inputs']
    outputs = model_data['outputs']
    
    print("\n=== 交互式预测模式 ===")
    print("请按提示输入数据，输入 'q' 退出\n")
    
    while True:
        print("-" * 60)
        input_data = {}
        
        # 逐个输入特征值
        for inp in inputs:
            value = input(f"请输入 {inp}: ").strip()
            if value.lower() == 'q':
                print("退出预测")
                return
            
            try:
                input_data[inp] = float(value)
            except ValueError:
                print(f"错误：'{value}' 不是有效的数值，请重新输入")
                break
        
        if len(input_data) != len(inputs):
            continue
        
        # 准备数据并预测
        X = pd.DataFrame([input_data])
        predictions = model.predict(X)
        
        print("\n预测结果:")
        for i, output_name in enumerate(outputs):
            print(f"  {output_name}: {predictions[0][i]:.4f}")
        print()

def main():
    """主函数"""
    ap = argparse.ArgumentParser(
        description="使用训练好的模型进行预测",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  1. 从文件预测：
     python predict.py --model model.joblib --input new_data.csv --output predictions.csv
  
  2. 交互式预测：
     python predict.py --model model.joblib --interactive
  
  3. 从文件预测（不保存结果）：
     python predict.py --model model.joblib --input new_data.csv
        """
    )
    
    ap.add_argument("--model", required=True, help="模型文件路径 (.joblib)")
    ap.add_argument("--input", help="输入数据文件路径 (csv/xlsx)")
    ap.add_argument("--output", help="输出预测结果文件路径 (csv/xlsx)")
    ap.add_argument("--interactive", action="store_true", help="交互式预测模式")
    
    args = ap.parse_args()
    
    if args.interactive:
        # 交互式预测
        predict_interactive(args.model)
    elif args.input:
        # 从文件预测
        predict_from_file(args.model, args.input, args.output)
    else:
        print("错误：请指定 --input 文件或使用 --interactive 模式")
        sys.exit(1)

if __name__ == "__main__":
    main()

