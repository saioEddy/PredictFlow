# excel_to_csv.py
# Excel转CSV工具
# 功能：将Excel文件转换为CSV格式，支持多工作表、自动清理数据

import argparse
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

def is_empty_sheet(df):
    """
    检查工作表是否为空
    
    参数:
        df: pandas DataFrame
    
    返回:
        True如果工作表为空，False否则
    """
    # 移除完全为空的行和列后检查
    df_cleaned = df.dropna(how='all').dropna(axis=1, how='all')
    return df_cleaned.empty or (len(df_cleaned) == 0 and len(df_cleaned.columns) == 0)

def clean_dataframe(df):
    """
    清理DataFrame：移除空行、空列，处理合并单元格等
    
    参数:
        df: pandas DataFrame
    
    返回:
        清理后的DataFrame
    """
    # 移除完全为空的行和列
    df = df.dropna(how='all').dropna(axis=1, how='all')
    
    # 重置索引
    df = df.reset_index(drop=True)
    
    return df

def extract_structured_data(df):
    """
    从非标准格式的Excel中提取结构化数据
    适用于类似"载荷0.2倍.xlsx"这种格式的数据
    将块状数据重组为标准表格格式
    
    数据块结构：
    - 载荷行：载荷, 0.2, NaN, 应力强度最大值, 15.15MPA, NaN
    - 频率行：频率, 0.1, NaN, 定向弹性应变, 4.92e-05, -3.9647e-05
    - 线性化薄膜应力行：NaN, NaN, NaN, 线性化薄膜应力, 2.78MPA, NaN
    - 膜加弯应力行：NaN, NaN, NaN, 膜加弯应力, 6.3691MPA, NaN
    
    输出格式：
    载荷,频率,应力强度最大值,定向弹性应变1,定向弹性应变2,线性化薄膜应力,膜加弯应力
    
    参数:
        df: 原始DataFrame
    
    返回:
        结构化后的DataFrame，如果无法提取则返回None
    """
    records = []
    i = 0
    
    while i < len(df):
        row = df.iloc[i]
        
        # 查找载荷行（第0列包含"载荷"）
        if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() == '载荷':
            # 提取载荷值（第1列）
            load_value = None
            if pd.notna(row.iloc[1]):
                try:
                    load_value = float(row.iloc[1])
                except (ValueError, TypeError):
                    pass
            
            # 查找对应的频率行（下一行，第0列包含"频率"）
            if i + 1 < len(df):
                freq_row = df.iloc[i + 1]
                
                if pd.notna(freq_row.iloc[0]) and str(freq_row.iloc[0]).strip() == '频率':
                    # 提取频率值（第1列）
                    freq_value = None
                    if pd.notna(freq_row.iloc[1]):
                        try:
                            freq_value = float(freq_row.iloc[1])
                        except (ValueError, TypeError):
                            pass
                    
                    # 初始化记录，使用固定的列名
                    record = {
                        '载荷': load_value,
                        '频率': freq_value,
                        '应力强度最大值': None,
                        '定向弹性应变1': None,
                        '定向弹性应变2': None,
                        '线性化薄膜应力': None,
                        '膜加弯应力': None
                    }
                    
                    # 从载荷行提取应力强度最大值（第3列是标签，第4列是值）
                    if len(row) > 4 and pd.notna(row.iloc[3]) and pd.notna(row.iloc[4]):
                        stress_label = str(row.iloc[3]).strip()
                        stress_val = row.iloc[4]
                        
                        # 检查是否是应力强度最大值
                        if '应力强度最大值' in stress_label or '应力强度' in stress_label:
                            # 保留MPA单位（按用户示例格式）
                            record['应力强度最大值'] = str(stress_val)
                    
                    # 从频率行提取定向弹性应变（第3列是标签，第4列是值，第5列是负值）
                    if len(freq_row) > 4 and pd.notna(freq_row.iloc[3]) and pd.notna(freq_row.iloc[4]):
                        strain_label = str(freq_row.iloc[3]).strip()
                        strain_val = freq_row.iloc[4]
                        
                        # 检查是否是定向弹性应变
                        if '定向弹性应变' in strain_label or '应变' in strain_label:
                            # 第4列是正值，格式化为固定小数位数（不使用科学计数法）
                            try:
                                strain_val_float = float(strain_val)
                                # 格式化为固定小数位数，保留足够的精度
                                record['定向弹性应变1'] = f"{strain_val_float:.10f}".rstrip('0').rstrip('.')
                            except (ValueError, TypeError):
                                record['定向弹性应变1'] = str(strain_val)
                            
                            # 第5列是负值，格式化为固定小数位数
                            if len(freq_row) > 5 and pd.notna(freq_row.iloc[5]):
                                try:
                                    neg_val_float = float(freq_row.iloc[5])
                                    # 格式化为固定小数位数，保留足够的精度
                                    record['定向弹性应变2'] = f"{neg_val_float:.10f}".rstrip('0').rstrip('.')
                                except (ValueError, TypeError):
                                    record['定向弹性应变2'] = str(freq_row.iloc[5])
                    
                    # 查找后续行的其他参数（线性化薄膜应力、膜加弯应力等）
                    # 这些行的第0列是NaN，第3列是参数标签，第4列是参数值
                    j = i + 2
                    while j < len(df) and j < i + 6:  # 最多查找4行（通常只有2-3个参数行）
                        next_row = df.iloc[j]
                        
                        # 如果遇到下一个载荷行，停止
                        if pd.notna(next_row.iloc[0]) and str(next_row.iloc[0]).strip() == '载荷':
                            break
                        
                        # 查找参数标签（第3列是标签，第4列是值）
                        if len(next_row) > 4 and pd.notna(next_row.iloc[3]) and pd.notna(next_row.iloc[4]):
                            param_label = str(next_row.iloc[3]).strip()
                            param_val = next_row.iloc[4]
                            
                            if param_label:
                                # 根据标签名称匹配到对应的列
                                if '线性化薄膜应力' in param_label:
                                    # 保留MPA单位
                                    record['线性化薄膜应力'] = str(param_val)
                                elif '膜加弯应力' in param_label:
                                    # 保留MPA单位
                                    record['膜加弯应力'] = str(param_val)
                        
                        j += 1
                    
                    # 确保至少有一些有效数据
                    if record['载荷'] is not None and record['频率'] is not None:
                        records.append(record)
                    
                    i = j - 1  # 跳到下一个数据块
        
        i += 1
    
    if len(records) > 0:
        # 转换为DataFrame，使用固定的列顺序
        column_order = ['载荷', '频率', '应力强度最大值', '定向弹性应变1', '定向弹性应变2', '线性化薄膜应力', '膜加弯应力']
        result_df = pd.DataFrame(records, columns=column_order)
        return result_df
    
    return None

def convert_excel_to_csv(excel_path, output_path=None, sheet_name=None, 
                        clean_data=True, encoding='utf-8-sig', user_specified_output=False):
    """
    将Excel文件转换为CSV格式
    
    参数:
        excel_path: Excel文件路径
        output_path: 输出CSV文件路径（如果为None，则自动生成）
        sheet_name: 要转换的工作表名称（如果为None，转换所有工作表）
        clean_data: 是否清理数据（移除空行空列）
        encoding: CSV文件编码（默认utf-8-sig，支持Excel打开）
        user_specified_output: 用户是否明确指定了输出文件名
    
    返回:
        生成的CSV文件路径列表
    """
    excel_path = Path(excel_path)
    
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel文件不存在: {excel_path}")
    
    # 如果没有指定输出路径，自动生成
    if output_path is None:
        output_path = excel_path.parent / f"{excel_path.stem}.csv"
        user_specified_output = False
    else:
        output_path = Path(output_path)
        user_specified_output = True
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"正在读取Excel文件: {excel_path}")
    
    # 读取Excel文件
    try:
        # 如果指定了工作表名称
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # 检查是否为空工作表
            if is_empty_sheet(df):
                print(f"⚠ 工作表 '{sheet_name}' 为空，已跳过")
                return []
            
            # 先尝试从原始DataFrame提取结构化数据（不清理，保持列索引）
            structured_df = extract_structured_data(df)
            if structured_df is not None:
                df = structured_df
            elif clean_data:
                # 如果无法提取结构化数据，清理后使用原始格式
                df = clean_dataframe(df)
            
            # 保存为CSV
            df.to_csv(output_path, index=False, encoding=encoding)
            print(f"✓ 已转换: {output_path}")
            return [str(output_path)]
        else:
            # 读取所有工作表
            excel_file = pd.ExcelFile(excel_path)
            sheet_names = excel_file.sheet_names
            output_paths = []
            non_empty_sheets = []
            
            # 先过滤出非空的工作表
            for sheet in sheet_names:
                df_test = pd.read_excel(excel_path, sheet_name=sheet)
                if not is_empty_sheet(df_test):
                    non_empty_sheets.append(sheet)
                else:
                    print(f"⚠ 工作表 '{sheet}' 为空，已跳过")
            
            if len(non_empty_sheets) == 0:
                print("错误：所有工作表都为空，无法转换")
                return []
            
            if len(non_empty_sheets) == 1:
                # 只有一个非空工作表，直接转换
                df = pd.read_excel(excel_path, sheet_name=non_empty_sheets[0])
                
                # 先尝试从原始DataFrame提取结构化数据
                structured_df = extract_structured_data(df)
                if structured_df is not None:
                    df = structured_df
                elif clean_data:
                    # 如果无法提取结构化数据，清理后使用原始格式
                    df = clean_dataframe(df)
                
                df.to_csv(output_path, index=False, encoding=encoding)
                print(f"✓ 已转换: {output_path}")
                output_paths.append(str(output_path))
            else:
                # 多个非空工作表，为每个工作表生成一个CSV文件
                print(f"检测到 {len(non_empty_sheets)} 个非空工作表，将分别转换...")
                # 如果用户指定了输出文件名，第一个工作表使用该文件名，其他的添加工作表名称后缀
                for idx, sheet in enumerate(non_empty_sheets):
                    df = pd.read_excel(excel_path, sheet_name=sheet)
                    
                    # 先尝试从原始DataFrame提取结构化数据
                    structured_df = extract_structured_data(df)
                    if structured_df is not None:
                        df = structured_df
                    elif clean_data:
                        # 如果无法提取结构化数据，清理后使用原始格式
                        df = clean_dataframe(df)
                    
                    # 第一个工作表使用用户指定的文件名（如果用户明确指定了），其他的添加工作表名称后缀
                    if idx == 0 and user_specified_output:
                        # 用户指定了输出文件名，第一个工作表使用该文件名
                        sheet_output = output_path
                    else:
                        # 其他工作表添加工作表名称后缀
                        sheet_output = output_path.parent / f"{output_path.stem}_{sheet}.csv"
                    
                    df.to_csv(sheet_output, index=False, encoding=encoding)
                    print(f"✓ 已转换工作表 '{sheet}': {sheet_output}")
                    output_paths.append(str(sheet_output))
            
            return output_paths
    except Exception as e:
        print(f"错误：转换失败 - {str(e)}")
        raise

def main():
    """主函数"""
    ap = argparse.ArgumentParser(
        description="Excel转CSV工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  1. 基本转换（自动生成输出文件名）：
     python excel_to_csv.py data/train/载荷0.2倍.xlsx
  
  2. 指定输出文件：
     python excel_to_csv.py input.xlsx -o output.csv
  
  3. 转换指定工作表：
     python excel_to_csv.py input.xlsx -s "Sheet1" -o output.csv
  
  4. 转换所有工作表（多文件输出）：
     python excel_to_csv.py input.xlsx -o output.csv
  
  5. 不清理数据（保留空行空列）：
     python excel_to_csv.py input.xlsx --no-clean
        """
    )
    
    ap.add_argument("excel_file", help="Excel文件路径 (.xlsx 或 .xls)")
    ap.add_argument("-o", "--output", help="输出CSV文件路径（默认：与Excel文件同目录同名）", default=None)
    ap.add_argument("-s", "--sheet", help="要转换的工作表名称（默认：转换所有工作表）", default=None)
    ap.add_argument("--no-clean", action="store_true", help="不清理数据（保留空行空列）")
    ap.add_argument("--encoding", help="CSV文件编码（默认：utf-8-sig）", default="utf-8-sig")
    
    args = ap.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.excel_file):
        print(f"错误：文件不存在: {args.excel_file}")
        sys.exit(1)
    
    # 检查文件格式
    if not args.excel_file.lower().endswith(('.xlsx', '.xls')):
        print(f"警告：文件扩展名不是 .xlsx 或 .xls，将尝试读取...")
    
    try:
        # 执行转换
        output_paths = convert_excel_to_csv(
            excel_path=args.excel_file,
            output_path=args.output,
            sheet_name=args.sheet,
            clean_data=not args.no_clean,
            encoding=args.encoding,
            user_specified_output=(args.output is not None)
        )
        
        print(f"\n✓ 转换完成！共生成 {len(output_paths)} 个CSV文件")
        for path in output_paths:
            print(f"  - {path}")
        
    except Exception as e:
        print(f"\n✗ 转换失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

