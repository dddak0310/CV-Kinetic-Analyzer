import pandas as pd
import numpy as np
from scipy.stats import linregress

def calculate_k1_k2(df):
    # 根據你的手寫圖定義：10組交錯的欄位位置 (acegikmoqs 是電壓，其他是電流)
    volt_col_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18] 
    curr_col_indices = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19] 
    
    # 變數 v 在這裡代表公式中的掃描速率，直接對應 10 個標準回歸點
    v = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
    x_val = np.sqrt(v)
    
    result = []
    
    # 逐行（電壓每 0.01V）重複計算
    for idx, row in df.iterrows():
        # 使用 iloc 依位置精準抓取第一組的電壓數值
        target_voltage = row.iloc[volt_col_indices[0]]
        
        # 排除空白行
        if pd.isna(target_voltage):
            continue
            
        # 依位置抓取這 10 個欄位在目前電壓下對應的電流值
        currents = []
        for c_idx in curr_col_indices:
            currents.append(row.iloc[c_idx])
        currents = np.array(currents, dtype=float)
        
        # 帶入第二條公式的 Y 軸： i / sqrt(v)
        y_val = currents / np.sqrt(v)
        
        # 進行線性回歸，得到該電壓下的 k1 (斜率) 與 k2 (截距)
        slope, intercept, r_value, p_value, std_err = linregress(x_val, y_val)
        
        k1 = slope
        k2 = intercept
        r_squared = r_value ** 2
        
        # 將 k1, k2 帶入第一條公式，得到特定電壓下「電流和掃描速率」的公式
        formula_str = f"i = ({k1:.4f})*v + ({k2:.4f})*v^0.5"
        
        # 【修改】這裡不再將系統內部的行編號 idx 塞進結果
        result.append([target_voltage, k1, k2, r_squared, formula_str])
        
    result_df = pd.DataFrame(
        result, 
        columns=["Voltage (V)", "k1 (斜率)", "k2 (截距)", "R2 (擬合度)", "特定電壓下的電流和掃描速率公式"]
    )
    return result_df