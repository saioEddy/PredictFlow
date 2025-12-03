# inspect_and_train.py
# 数据探索与模型训练脚本
# 功能：自动识别数据列、训练多输出回归模型、保存模型

import argparse
import sys
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

# 模糊匹配关键词：用于自动识别输入列
FUZZY_INPUT_KEYS = [
    "freq", "frequency", "频率", "倍数", "mult", "multiple",
    "load", "载荷", "载重", "payload"
]

def load_data(path):
    """
    加载数据文件（支持CSV和Excel格式）
    
    参数:
        path: 文件路径
    
    返回:
        pandas DataFrame
    """
    p = str(path).lower()
    if p.endswith(".csv"):
        return pd.read_csv(path)
    elif p.endswith((".xls", ".xlsx")):
        return pd.read_excel(path)
    else:
        # 尝试先按CSV读取，失败则按Excel读取
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.read_excel(path)

def summarize_df(df, n_head=5):
    """
    展示数据框的基本信息
    
    参数:
        df: pandas DataFrame
        n_head: 显示前n行数据
    """
    print("\n=== 列信息 ===")
    for i, c in enumerate(df.columns):
        print(f"{i:3d}. {c} \t 类型={df[c].dtype} \t 缺失值={df[c].isna().sum()}")
    
    print("\n=== 前几行数据 ===")
    print(df.head(n_head))
    
    print("\n=== 数值列统计信息 ===")
    print(df.describe().T)

def fuzzy_candidates(df):
    """
    使用模糊匹配自动识别候选输入列和输出列
    
    参数:
        df: pandas DataFrame
    
    返回:
        (cand_inputs, cand_outputs): 候选输入列和候选输出列
    """
    cols = list(df.columns)
    lower = [c.lower() for c in cols]
    cand_inputs = []
    
    # 根据模糊匹配规则识别输入列
    for i, c in enumerate(cols):
        for k in FUZZY_INPUT_KEYS:
            if k in c.lower():
                cand_inputs.append(c)
                break
    
    # 去重并保持顺序
    cand_inputs = list(dict.fromkeys(cand_inputs))
    
    # 将所有数值列作为候选输出列（排除已识别的输入列）
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cand_outputs = [c for c in numeric_cols if c not in cand_inputs]
    
    return cand_inputs, cand_outputs

def show_correlations(df, inputs, outputs):
    """
    显示输入列与输出列之间的相关性矩阵
    
    参数:
        df: pandas DataFrame
        inputs: 输入列名列表
        outputs: 输出列名列表
    """
    if not inputs or not outputs:
        return
    
    sub = df[inputs + outputs].dropna()
    if sub.shape[0] < 3:
        print("\n（数据太少，无法计算相关性）")
        return
    
    corr = sub.corr()
    print("\n=== 输入-输出相关性分析 ===")
    for inp in inputs:
        row = corr.loc[inp, outputs].sort_values(ascending=False)
        print(f"\n-- {inp} 与输出列的相关性 --")
        print(row)

def pick_columns_interactive(df, cand_inputs, cand_outputs):
    """
    交互式选择输入列和输出列
    
    参数:
        df: pandas DataFrame
        cand_inputs: 自动识别的候选输入列
        cand_outputs: 自动识别的候选输出列
    
    返回:
        (inputs, outputs): 最终选定的输入列和输出列
    """
    print("\n自动识别到的候选输入列：", cand_inputs)
    print("自动识别到的候选输出列（数值型）：", cand_outputs)
    print("\n如果自动识别正确，直接回车接受。否则输入列名或索引（逗号分隔）。")
    
    inp = input("选择输入列 (name1,name2 或 索引0,1) [回车接受自动识别]: ").strip()
    if inp == "":
        inputs = cand_inputs.copy()
    else:
        inputs = parse_choice_input(inp, df.columns)
    
    outp = input("选择输出列 (name1,name2 或 索引0,1) [回车接受自动识别]: ").strip()
    if outp == "":
        outputs = cand_outputs.copy()
    else:
        outputs = parse_choice_input(outp, df.columns)
    
    # 验证选择
    if not inputs:
        print("错误：至少需要1个输入列。")
        sys.exit(1)
    if not outputs:
        print("错误：至少需要1个数值输出列。")
        sys.exit(1)
    
    return inputs, outputs

def parse_choice_input(text, all_columns):
    """
    解析用户输入的列选择（支持列名或索引）
    
    参数:
        text: 用户输入的文本
        all_columns: 所有列名
    
    返回:
        选中的列名列表
    """
    text = text.strip()
    parts = [p.strip() for p in text.split(",") if p.strip()]
    chosen = []
    
    for p in parts:
        if p.isdigit():
            idx = int(p)
            if 0 <= idx < len(all_columns):
                chosen.append(all_columns[idx])
        else:
            # 精确匹配
            if p in all_columns:
                chosen.append(p)
            else:
                # 不区分大小写匹配
                for c in all_columns:
                    if c.lower() == p.lower():
                        chosen.append(c)
                        break
    
    return chosen

def clean_numeric_value(value):
    """
    清理数值字符串，去除单位（如MPA、MPA等）
    
    参数:
        value: 待清理的值（可能是字符串或数值）
    
    返回:
        清理后的数值
    """
    if pd.isna(value):
        return value
    
    # 如果是数值类型，直接返回
    if isinstance(value, (int, float)):
        return value
    
    # 转换为字符串并清理
    import re
    str_value = str(value).strip()
    
    # 使用正则表达式提取数值部分（包括负号、小数点）
    # 匹配模式：可选负号 + 数字 + 可选小数点 + 更多数字
    match = re.search(r'-?\d+\.?\d*', str_value)
    if match:
        try:
            return float(match.group())
        except (ValueError, TypeError):
            return np.nan
    
    # 如果正则匹配失败，尝试直接转换
    try:
        return float(str_value)
    except (ValueError, TypeError):
        return np.nan

def simple_preprocess(df, inputs, outputs):
    """
    简单数据预处理：数值化和缺失值填充
    
    参数:
        df: pandas DataFrame
        inputs: 输入列名列表
        outputs: 输出列名列表
    
    返回:
        预处理后的DataFrame
    """
    sub = df[inputs + outputs].copy()
    
    # 数值化转换（增强版：清理单位）
    for c in sub.columns:
        if sub[c].dtype == object:
            # 先尝试清理单位，再转换为数值
            sub[c] = sub[c].apply(clean_numeric_value)
        else:
            # 对于已经是数值类型的列，也尝试清理（以防万一）
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
    
    # 缺失值处理：用中位数填充
    for c in sub.columns:
        if sub[c].isna().any():
            med = sub[c].median()
            if pd.isna(med):
                # 如果中位数也是NaN，用0填充
                med = 0
            sub[c] = sub[c].fillna(med)
            print(f"列 '{c}' 有缺失值，已用中位数 {med:.4f} 填充")
    
    return sub

def train_and_save(X, y, out_model_path="model.joblib"):
    """
    训练多输出回归模型并保存
    
    参数:
        X: 输入特征DataFrame
        y: 输出目标DataFrame
        out_model_path: 模型保存路径
    
    返回:
        训练好的模型
    """
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 创建随机森林多输出回归模型
    base = RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=42)
    model = MultiOutputRegressor(base)
    
    print(f"\n开始训练模型...")
    print(f"训练集样本数：{len(X_train)}")
    print(f"测试集样本数：{len(X_test)}")
    print(f"输入特征数：{X.shape[1]}")
    print(f"输出目标数：{y.shape[1]}")
    
    model.fit(X_train, y_train)
    print("训练完成！\n")
    
    # 评估模型
    print("=== 模型评估结果 ===")
    y_pred = model.predict(X_test)
    
    if y.shape[1] == 1:
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        print(f"R2 分数: {r2:.4f}")
        print(f"平均绝对误差 (MAE): {mae:.4f}")
    else:
        for i, col in enumerate(y.columns):
            r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
            mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
            print(f"{col:20s} -> R2: {r2:.4f}  MAE: {mae:.4f}")
    
    # 保存模型
    joblib.dump({
        "model": model,
        "inputs": X.columns.tolist(),
        "outputs": y.columns.tolist()
    }, out_model_path)
    print(f"\n模型已保存到: {out_model_path}")
    
    return model

def main():
    """主函数"""
    ap = argparse.ArgumentParser(
        description="数据探索与多输出模型训练工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  1. 交互式模式（推荐）：
     python inspect_and_train.py data.csv
  
  2. 自动模式：
     python inspect_and_train.py data.csv --auto
  
  3. 指定输入输出列：
     python inspect_and_train.py data.csv --inputs freq,load --outputs stress,strain
        """
    )
    
    ap.add_argument("path", help="数据文件路径 (csv/xlsx)")
    ap.add_argument("--inputs", help="逗号分隔的输入列名（优先于自动识别）", default=None)
    ap.add_argument("--outputs", help="逗号分隔的输出列名（优先于自动识别）", default=None)
    ap.add_argument("--out-model", help="保存模型路径", default="models/model.joblib")
    ap.add_argument("--auto", action="store_true", help="自动接受脚本识别的候选输入/输出（非交互）")
    
    args = ap.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.path):
        print(f"错误：文件不存在: {args.path}")
        sys.exit(1)
    
    # 加载数据
    print(f"正在加载数据文件: {args.path}")
    df = load_data(args.path)
    print(f"已加载数据，行数={len(df)}, 列数={len(df.columns)}")
    
    # 展示数据概况
    summarize_df(df)
    
    # 自动识别候选列
    cand_inputs, cand_outputs = fuzzy_candidates(df)
    
    # 显示相关性分析
    show_correlations(df, cand_inputs, cand_outputs)
    
    # 确定最终使用的输入输出列
    if args.inputs:
        inputs = [s.strip() for s in args.inputs.split(",") if s.strip()]
    else:
        inputs = cand_inputs
    
    if args.outputs:
        outputs = [s.strip() for s in args.outputs.split(",") if s.strip()]
    else:
        outputs = cand_outputs
    
    if args.auto:
        # 自动模式：直接使用识别结果
        if not inputs:
            print("错误：自动模式但没有识别到输入列，请使用 --inputs 指定。")
            sys.exit(1)
        if not outputs:
            print("错误：自动模式但没有识别到输出列（数值型），无法训练。")
            sys.exit(1)
    else:
        # 交互模式：让用户确认或修改
        inputs, outputs = pick_columns_interactive(df, inputs, outputs)
    
    print("\n" + "="*60)
    print("最终选定的输入列：", inputs)
    print("最终选定的输出列：", outputs)
    print("="*60)
    
    # 数据预处理
    print("\n正在进行数据预处理...")
    sub = simple_preprocess(df, inputs, outputs)
    X = sub[inputs]
    y = sub[outputs]
    
    # 训练模型
    model = train_and_save(X, y, args.out_model)
    
    # 示例预测
    print("\n=== 示例预测（使用最后3条输入数据） ===")
    sample = X.tail(3)
    print("\n输入数据：")
    print(sample)
    
    pred = model.predict(sample)
    out_df = pd.DataFrame(pred, columns=y.columns, index=sample.index)
    print("\n预测结果：")
    print(out_df)
    
    print("\n✓ 训练完成！")

if __name__ == "__main__":
    main()

