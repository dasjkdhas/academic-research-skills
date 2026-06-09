# Methodology Framework — Final Lock-In
## 校園 FRR-Loop 方法論最終定案

**Date**: 2026-05-16
**狀態**: 已與用戶確認，鎖定執行
**Target Journal**: *Energies* (MDPI Q2)

---

## ✅ 用戶確認決策

| 維度 | 決策 | 影響 |
|------|------|------|
| 創新點範圍 | **核心 1–5 為論文主體 + 創新點 6,7 為 Future Work** | 論文預估 18–22 頁 |
| Day-Type 來源 | **人工標籤 + 自動 clustering 並行對比** | 創新點 2 升級為「**雙路徑驗證式 Day Embedding**」 |
| 樓宇分項負荷 | **部分（少數樓宇有分計量）** | 創新點 4 採「分層分析」策略：有分計量樓宇做完整 SDR 動作-效益拆解；其他樓宇做總體削峰評估 |
| Conformal Prediction | **Future Work** | 論文 Section 7 留專段；不執行 |

---

## 鎖定的五項核心方法論創新

### ★ 創新 1: Dual-Head Joint Learning
- Head A: **LightGBM** (回歸, MSE loss)
- Head B: **GRU** (二元分類, Focal Loss)
- 共享 Day-Embedding + 氣象特徵層
- 整合輸出 → CCRI

### ★ 創新 2: Dual-Path Day-Type Embedding (升級版)
- **Path A (人工標籤)**：使用您提供的 day_type (5–7 類)，學 d=8 嵌入
- **Path B (自動 clustering)**：對歷史小時負載曲線做 K-Means + DTW，自動識別 K=5–8 個原型日
- **對比實驗**：
  - 比較 Path A vs Path B 在預測精度與峰值識別 F1 上的差異
  - 報告兩者之**標籤重疊度** (Adjusted Rand Index, NMI)
  - **若 Path B ≈ Path A**：證明資料中已包含足夠校歷信號 → 模型可於資料不足時無監督運行
  - **若 Path B 揭露新模式**（例如冷氣設備老化期、實驗高峰期）：作為**意外發現**寫入 Discussion

### ★ 創新 3: Contract-Capacity Risk Index (CCRI)
- 公式: `CCRI(t) = w₁·ŷ(t)/C + w₂·P(peak|t) + w₃·Ê[duration|t]`
- 三層: Normal / High / Critical
- 權重 wᵢ 從訓練集校準（最大化 F1 on critical events）
- C = 2,000 kW (鎖定)

### ★ 創新 4: Tiered Counterfactual SDR Decomposition (升級版)
- **Tier 1 (有分計量樓宇)**:
  完整「動作 × 時段 × 樓宇」三維貢獻矩陣
  反事實: `Δ(aᵢ, t, b) = ŷ_base(t,b) − ŷ_cf(t,b|aᵢ)`
- **Tier 2 (僅總體)**:
  「動作 × 時段」二維貢獻矩陣
  反事實基於總負載 baseline
- **整合論述**: 用 Tier 1 細粒度結果**校準** Tier 2 之系統性偏差，提出「分計量擴展邊際效益」討論

### ★ 創新 5: Risk Duration Compression Ratio (RDCR)
- `RDCR = 1 − T_risk_with_SDR / T_risk_baseline`
- 您實證: 60%
- 配合峰值削減量 (109 kW) 形成**雙指標體系**
- 補表報告 Capacity Excursion Hours (CEH)

---

## Future Work (Section 7 — 不執行但寫入論文)

### Future 6: SHAP-Verified Physical Consistency
- **論文寫法**: 列出 4–5 條物理 prior，論述未來如何用 dependence plot 驗證
- **不執行原因**: 屬延伸驗證；主體 SHAP summary plot 已足

### Future 7: Conformal Risk Calibration
- **論文寫法**: 引 Romano 2019 CQR，說明如何將 CCRI 升級為有覆蓋率保證的概率風險
- **不執行原因**: 需額外驗證集 + 計算成本

---

## 數據需求清單 (Data Drop Checklist)

請依以下格式準備並傳給我。**所有資料皆為 CSV 或 Parquet 格式**，UTF-8 編碼。

### 📁 必要資料（無法執行 Step 1 之前必要）

#### 1. `campus_load_hourly.csv` — 校園小時級總負荷
```
timestamp           ,total_load_kW
2024-04-01 00:00:00 ,852.3
2024-04-01 01:00:00 ,810.6
...
```
- 期間: 建議 ≥ 1 年（2 年以上更佳，可做 seasonal generalization）
- 時區: 標明 JST (UTC+9)
- 缺失值: 用 NaN 表示，**不要**填零

#### 2. `amedas_hourly.csv` — AMeDAS 小時級氣象
```
timestamp           ,temperature_C ,humidity_pct ,precipitation_mm ,wind_speed_mps
2024-04-01 00:00:00 ,12.4          ,65           ,0.0              ,2.3
...
```
- 站點: 距校園最近一站；請標明站名
- 期間: 與負荷資料對齊
- (可選) global_solar_radiation_MJ 欄位—若有則模型可加入太陽輻射特徵

#### 3. `calendar.csv` — 校歷
```
date       ,day_type        ,is_class_day
2024-04-01 ,regular_term    ,True
2024-04-05 ,weekend         ,False
2024-04-29 ,national_holiday,False
2024-07-15 ,exam_week       ,True
2024-08-05 ,summer_break    ,False
...
```
- day_type 建議使用以下標籤之一：
  - `regular_term` (正常上課日)
  - `exam_week` (考試週)
  - `summer_break` (暑假)
  - `winter_break` (寒假/春假)
  - `national_holiday` (國定假日)
  - `weekend` (一般週末)
  - `special_event` (校慶/迎新等)
- 若您的分類不同，**直接用您的標籤即可**，我會接受任意離散值

#### 4. 合同容量值
- **C = 2,000 kW** (已知)
- 若有歷史變更紀錄，告知變更日期即可

### 📁 推薦資料（升級創新點 4 必要）

#### 5. `building_load_hourly.csv` — 樓宇分項負荷（**部分樓宇有即可**）
```
timestamp           ,building_id ,building_type ,load_kW
2024-04-01 00:00:00 ,B01         ,teaching      ,120.5
2024-04-01 00:00:00 ,B02         ,lab           ,180.3
2024-04-01 00:00:00 ,B03         ,dorm          ,95.2
...
```
- `building_type` 建議: teaching / lab / dorm / admin / library / cafeteria / sport
- 即使只有 2–3 棟樓有資料，Tier 1 分析仍可進行
- 若無此資料：執行降級為 Tier 2 路線

### 📁 可選資料（強化分析深度）

#### 6. `building_metadata.csv` — 樓宇基本資訊
```
building_id ,building_type ,floor_area_m2 ,n_floors ,year_built ,has_lab
B01         ,teaching      ,5200          ,5        ,2008       ,False
...
```

#### 7. `hvac_setpoint_history.csv` — 空調設定歷史（如有 BEMS 紀錄）
- 用於驗證 SDR 動作模擬之合理性

---

## 接收資料後的執行流程（Step 0–10）

```
您傳資料
   ↓
Step 0  資料診斷                     [~10 min]
   • 缺失值 / outlier / 時區一致性
   • 季節性 / 平穩性 / ACF / PACF
   • 產出: data_diagnostic.md + diagnostic_plots/

Step 1  特徵工程                      [~30 min]
   • 時序滯後 (lag 1h/3h/24h/168h)
   • 體感溫度 / WBGT 計算
   • Day-Type Embedding (Path A 人工 + Path B 自動)
   • 樓宇聚合
   • 產出: features.parquet + feature_dict.md

Step 2  Walk-Forward CV 設計          [~10 min]
   • 訓練/驗證/測試 切分
   • 引 Bergmeir 2012
   • 產出: cv_splits.json + cv_design.md

Step 3  Head A LightGBM 訓練          [~20 min]
   • Optuna 100 trials
   • Path A vs Path B 對比
   • 產出: model_lightgbm_*.pkl + metrics

Step 4  Head B GRU 訓練               [~30 min]
   • Focal Loss + 早停
   • Path A vs Path B 對比
   • 產出: model_gru_*.pt + metrics

Step 5  基準對照                      [~20 min]
   • RF / XGBoost / LSTM
   • 產出: baseline_comparison.csv

Step 6  統計顯著性                    [~10 min]
   • Diebold-Mariano + Friedman + Nemenyi
   • 產出: significance_tests.md

Step 7  CCRI 風險指數                 [~20 min]
   • 三層分類校準
   • 混淆矩陣 / 風險覆蓋率
   • 產出: ccri_results.csv

Step 8  SDR 動作反事實                [~40 min]
   • Tier 1 (有分計量): 三維矩陣
   • Tier 2 (其他): 二維矩陣
   • RDCR / CEH 計算
   • 產出: sdr_action_matrix.csv

Step 9  SHAP 解釋                     [~30 min]
   • Tree SHAP / DeepSHAP
   • Summary + Dependence + Force
   • 產出: shap_plots/

Step 10 整合報告                      [~30 min]
   • 對應論文 Section 3-5
   • 產出: final_results.md (可直接套入論文模板)
```

**總時間**: 約 4 小時連續執行；含 review 與調整約 6–8 小時。

---

## 結果套入論文章節對應

| Step 產出 | 論文章節 |
|----------|---------|
| Step 0 | Section 3.1 Data Description |
| Step 1 | Section 3.2 Feature Engineering |
| Step 2 | Section 3.3 Cross-Validation Design |
| Step 3,4 | Section 3.4 Model Architecture; Section 4.1 Single-Model Performance |
| Step 5 | Section 4.2 Baseline Comparison |
| Step 6 | Section 4.3 Statistical Significance |
| Step 7 | Section 3.5 CCRI Design; Section 4.4 Risk Identification |
| Step 8 | Section 3.6 SDR Action Set; Section 4.5 Action-Benefit Decomposition |
| Step 9 | Section 4.6 Interpretability Analysis |
| Step 10 | Section 4.7 Summary Tables; Section 5 Discussion Preparation |

---

## 等待您傳資料中 ⏳

請依「數據需求清單」準備並上傳。即使只有部分項目（如只有 #1–#4），也可立即啟動 Step 0–7（樓宇分項相關 Step 8 採 Tier 2 路線）。

收到資料後我會：
1. **先回傳 Step 0 資料診斷報告**（含資料品質摘要 + 任何疑慮）
2. **等您確認**後再進入 Step 1
3. 之後每完成 2–3 步上傳一次中間結果，您可隨時 review 調整方向
