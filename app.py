import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import numpy as np
from dunn_analysis import calculate_k1_k2

# 1. 網頁標題與寬版排版設定
st.set_page_config(
    page_title="CV Kinetic Analyzer",
    page_icon="⚡",
    layout="wide"
)

# 2. 注入自訂 CSS 樣式，打造現代感 UI
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .hero-banner h1 {
        color: white !important;
        margin: 0;
        font-weight: 700;
        font-size: 2.2rem;
    }
    .hero-banner p {
        color: #e0e0e0;
        margin-top: 5px;
        font-size: 1rem;
    }
    .step-card {
        background-color: #ffffff;
        border-left: 5px solid #2a5298;
        padding: 15px;
        border-radius: 4px 8px 8px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        height: 100%;
    }
    .step-number {
        font-size: 0.85rem;
        font-weight: bold;
        color: #2a5298;
        text-transform: uppercase;
        margin-bottom: 3px;
    }
    .step-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #333333;
    }
    .report-box {
        background-color: #f0f4f8;
        border: 1px solid #d0e1fd;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
    }
    [data-testid="stFileUploader"] {
        border: 2px dashed #2a5298 !important;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(56, 239, 125, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(56, 239, 125, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# 頂部 Tech Banner
st.markdown("""
    <div class="hero-banner">
        <h1>⚡ CV Kinetic Analyzer</h1>
        <p>基於 Dunn's Method 的電化學循環伏安法動力學自動化分析系統</p>
    </div>
""", unsafe_allow_html=True)

# 四大步驟卡片排版
st.subheader("📋 數據分析核心架構")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.markdown("""
        <div class="step-card" style="border-left-color: #1e3c72;">
            <div class="step-number">Step 01</div>
            <div class="step-title">橫向行讀取</div>
            <p style="font-size:0.9rem; color:#666;">鎖定單一橫行（如 3V），精準抽取該電壓下橫向排開的 10 組電流數據值。</p>
        </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown("""
        <div class="step-card" style="border-left-color: #00b4db;">
            <div class="step-number">Step 02</div>
            <div class="step-title">變數 v 線性回歸</div>
            <p style="font-size:0.9rem; color:#666;">將電流帶入第二條公式 <span style="font-family:monospace;">i/v^0.5 = k1*v^0.5 + k2</span> 進行擬合，求得斜率 k1 與截距 k2。</p>
        </div>
    """, unsafe_allow_html=True)

with col_s3:
    st.markdown("""
        <div class="step-card" style="border-left-color: #a8ff78;">
            <div class="step-number">Step 03</div>
            <div class="step-title">重構電流公式</div>
            <p style="font-size:0.9rem; color:#666;">將求解出的 k1, k2 帶回第一條公式，成功導出該特定電壓下電流與掃描速率的物理函數。</p>
        </div>
    """, unsafe_allow_html=True)

with col_s4:
    st.markdown("""
        <div class="step-card" style="border-left-color: #f45c43;">
            <div class="step-number">Step 04</div>
            <div class="step-title">0.01V 循環疊代</div>
            <p style="font-size:0.9rem; color:#666;">自動向下推移至下一橫行數據，每隔 0.01V 完美重複計算，最終產出完整趨勢圖表。</p>
        </div>
    """, unsafe_allow_html=True)

st.write(" ")
st.write("---")

# 檔案上傳區
uploaded_file = st.file_uploader(
    "請上傳您的電化學原始數據檔案 (支援 Excel 或 CSV 格式)",
    type=["xlsx", "csv"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)
        
        top_labels = []
        for i in range(len(df.columns)):
            if i < 20:
                group_num = (i // 2) + 1
                if i % 2 == 0:
                    top_labels.append(f"⚡ 固定電壓 {group_num}")
                else:
                    top_labels.append(f"📉 對應電流 {group_num}")
            else:
                top_labels.append("其他資料")
        
        sub_labels = [f"欄位 {i}" for i in range(len(df.columns))]
        
        display_df = df.copy()
        display_df.columns = pd.MultiIndex.from_arrays([top_labels, sub_labels])

        st.subheader("📂 原始數據預覽")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.write(" ")
        if st.button("🚀 開始自動化動力學分析"):
            with st.spinner("正在逐行進行線性擬合與物理公式建構..."):
                result_df = calculate_k1_k2(df)
                
            st.success("✨ 分析成功！數據、圖表與實驗報告已全數建構完畢。")
            
            # --- 數據表格展示 ---
            st.subheader("📊 分析結果矩陣")
            st.dataframe(result_df, use_container_width=True, hide_index=True)
            
            # 提供數據 CSV 下載
            csv_output = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下載分析結果 CSV 數據表",
                data=csv_output,
                file_name="cv_kinetic_analysis_results.csv",
                mime="text/csv"
            )
            
            st.write("---")
            
            # --- 圖表區塊 ---
            st.subheader("📈 趨勢圖表可視化")
            
            col1, col2 = st.columns(2)
            sns.set_theme(style="whitegrid")
            
            with col1:
                st.write("### 1. k1 與 k2 隨電壓變化趨勢")
                fig1, plt_ax1 = plt.subplots(figsize=(6, 4.2))
                
                color = '#1f77b4'
                plt_ax1.set_xlabel('Voltage (V)', fontweight='bold')
                plt_ax1.set_ylabel('k1 (Slope)', color=color, fontweight='bold')
                plt_ax1.plot(result_df['Voltage (V)'], result_df['k1 (斜率)'], color=color, linewidth=2, label='k1')
                plt_ax1.tick_params(axis='y', labelcolor=color)
                
                plt_ax2 = plt_ax1.twinx()
                color = '#ff7f0e'
                plt_ax2.set_ylabel('k2 (Intercept)', color=color, fontweight='bold')
                plt_ax2.plot(result_df['Voltage (V)'], result_df['k2 (截距)'], color=color, linewidth=2, linestyle='--', label='k2')
                plt_ax2.tick_params(axis='y', labelcolor=color)
                
                fig1.tight_layout()
                st.pyplot(fig1)
                
                buf1 = io.BytesIO()
                fig1.savefig(buf1, format="png", dpi=300)
                buf1.seek(0)
                st.download_button(
                    label="🖼️ 下載 k1 & k2 趨勢圖 (PNG)",
                    data=buf1,
                    file_name="k1_k2_trend.png",
                    mime="image/png"
                )
                
            with col2:
                st.write("### 2. 線性擬合度 R² 分佈")
                fig2, plt_ax3 = plt.subplots(figsize=(6, 4.2))
                
                plt_ax3.plot(result_df['Voltage (V)'], result_df['R2 (擬合度)'], color='#2ca02c', linewidth=2)
                plt_ax3.set_xlabel('Voltage (V)', fontweight='bold')
                plt_ax3.set_ylabel('R² (Fitting Quality)', fontweight='bold')
                plt_ax3.set_ylim(0, 1.05)
                
                fig2.tight_layout()
                st.pyplot(fig2)
                
                buf2 = io.BytesIO()
                fig2.savefig(buf2, format="png", dpi=300)
                buf2.seek(0)
                st.download_button(
                    label="🖼️ 下載 R² 擬合度圖 (PNG)",
                    data=buf2,
                    file_name="r2_distribution.png",
                    mime="image/png"
                )
            
            st.write("---")
            
            # ==================== 全新加載：自動化結果分析診斷報告 ====================
            st.subheader("📝 自動化實驗數據診斷報告")
            
            # 計算統計數值
            avg_k1 = result_df['k1 (斜率)'].mean()
            avg_k2 = result_df['k2 (截距)'].mean()
            avg_r2 = result_df['R2 (擬合度)'].mean()
            min_r2 = result_df['R2 (擬合度)'].min()
            
            # 動態判斷儲能行為主導機制
            if abs(avg_k1) > abs(avg_k2):
                mechanism_status = "表面電容行為（Capacitive-controlled process）主導"
                mechanism_desc = "這代表材料具有優異的表面積利用率與快速的游離離子吸脫附能力，適合用於高功率輸出的儲能元件（如超級電容器或虛擬電容材料）。"
            else:
                mechanism_status = "溶液離子擴散行為（Diffusion-controlled process）主導"
                mechanism_desc = "這代表材料的電荷儲存非常依賴離子嵌入脫出晶格的擴散過程，符合典型的電池型（Battery-like）儲能特徵，通常能提供較高的能量密度。"
            
            # 擬合可信度評級
            if avg_r2 >= 0.95:
                r2_rating = "🌟 優秀（Highly Reliable）"
                r2_advice = "平均擬合度極高，說明該體系的動力學行為完美符合 Dunn's Method 的物理模型，所得之 $k_1, k_2$ 公式極具學術參考價值。"
            elif avg_r2 >= 0.85:
                r2_rating = "✅ 良好（Acceptable）"
                r2_advice = "擬合度表現良好，數據大致符合理論模型，但局部電位可能伴隨輕微的極化副反應或量測干擾雜訊。"
            else:
                r2_rating = "⚠️ 需注意（Weak Correlation）"
                r2_advice = "擬合度偏低，建議檢查原始實驗數據是否存在顯著的儀器雜訊，或者該體系在測試電位下存在更為複雜的非線性多步電化學反應。"

            # 渲染美觀的報告區塊
            st.markdown(f"""
            <div class="report-box">
                <h4 style="color:#1e3c72; margin-top:0;">📊 數據統計與儲能機制診斷</h4>
                <ul style="font-size:0.95rem; line-height:1.6; color:#333;">
                    <li><b>平均擬合品質 (Average R²)</b>： <span style="font-family:monospace; font-weight:bold; color:#2ca02c;">{avg_r2:.4f}</span> ➔ 評級：<b>{r2_rating}</b></li>
                    <li><b>最低擬合點 (Minimum R²)</b>： <span style="font-family:monospace;">{min_r2:.4f}</span></li>
                    <li><b>平均電容控制項常數 (Average k1)</b>： <span style="font-family:monospace;">{avg_k1:.4e}</span></li>
                    <li><b>平均擴散控制項常數 (Average k2)</b>： <span style="font-family:monospace;">{avg_k2:.4e}</span></li>
                </ul>
                <hr style="border:0; border-top:1px solid #d0e1fd; margin:15px 0;">
                <h4 style="color:#1e3c72;">🧪 科學結論與物理意義分析</h4>
                <p style="font-size:0.95rem; line-height:1.6; color:#333; text-align:justify;">
                    1. <b>主導儲能機制</b>：本實驗體系在整體量測電位區間內，呈現由 <b>{mechanism_status}</b>。{mechanism_desc}
                </p>
                <p style="font-size:0.95rem; line-height:1.6; color:#333; text-align:justify;">
                    2. <b>模型適用性檢驗</b>：{r2_advice}
                </p>
                <p style="font-size:0.85rem; color:#666; margin-top:20px; font-style:italic;">
                    * 註：此診斷報告由系統根據回歸矩陣自適應生成，可直接複製作為實驗結案報告之文字基礎。
                </p>
            </div>
            """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"讀取或計算檔案時出錯，錯誤訊息: {e}")