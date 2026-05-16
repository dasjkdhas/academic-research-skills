# Methodology Framework — 方法論創新總藍圖
## Daily-Weather Coupled Risk-Oriented SDR System
## 日級用電 × 氣象耦合風險導向 Soft DR 系統

**Phase**: 4 — Pre-execution Methodology Design
**Date**: 2026-05-16
**Status**: 待用戶確認後執行
**Target Journal**: *Energies* (MDPI Q2)

---

## 0. 您的核心思路整理

> 1. **機器學習對每一天的用電數據進行學習**
> 2. **同時使用當時的天氣狀況學習**
> 3. **找出預報系統**
> 4. **制定預警計劃**

→ 翻譯為學術命題：

> 構建一個**日級用電 × 天氣耦合**的機器學習預測引擎，輸出層接到**容量風險判別器**，再連結到**柔性響應動作規劃器**—形成「預測 → 預警 → 響應」三層閉環。

---

## 1. 方法論定位（一句話 Punch Line）

> 本研究將高校用電管理從「**月度賬單事後分析**」升級為「**日級風險事前判別 + 動作級柔性響應**」之**三層閉環方法**，並通過合同容量導向的風險指數，使僅 4–5% 之高風險時段即可覆蓋 80%+ 真實高負荷事件。

---

## 2. 整體框架：**FRR-Loop**
### **F**orecasting → **R**isk → **R**esponse Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   [Input Data Sources]                                          │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │  小時級負荷  │  │  AMeDAS 氣象 │  │  校歷+樓宇   │         │
│   │  (校園歷史) │  │  (氣溫/濕度  │  │  (學期/考試  │         │
│   │              │  │   /降水/風)  │  │   /假期/類型)│         │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│          └─────────────────┼─────────────────┘                  │
│                            ▼                                    │
│   ┌──────────────────────────────────────────────────┐         │
│   │  ★ L0: Feature Engineering & Day-Embedding        │         │
│   │   • 時序滯後特徵 (lag 1h/24h/168h)                │         │
│   │   • 體感溫度 / WBGT / 熱浪累積指標                 │         │
│   │   • Day-Type Embedding (學/暑/考試/假/週末)        │         │
│   │   • 樓宇異質性特徵 (教學/實驗/宿舍 share)         │         │
│   └─────────────────┬────────────────────────────────┘         │
│                     ▼                                           │
│   ┌──────────────────────────────────────────────────┐         │
│   │  ★ L1: Dual-Head Forecasting Layer                │         │
│   │                                                  │         │
│   │   ┌────────────────┐    ┌─────────────────────┐  │         │
│   │   │  Head A:       │    │  Head B:            │  │         │
│   │   │  LightGBM      │    │  GRU (Sequential)   │  │         │
│   │   │  ─ 連續負載迴歸│    │  ─ 峰值事件分類     │  │         │
│   │   │  ─ Loss: MSE   │    │  ─ Loss: Focal Loss │  │         │
│   │   │  ─ 輸出: ŷ(t)  │    │  ─ 輸出: P(peak|t)  │  │         │
│   │   └────────┬───────┘    └──────────┬──────────┘  │         │
│   │            └───────────┬───────────┘             │         │
│   │                        ▼                         │         │
│   │              聯合損失 + Cross-validation         │         │
│   └────────────────────────┬─────────────────────────┘         │
│                            ▼                                    │
│   ┌──────────────────────────────────────────────────┐         │
│   │  ★ L2: Capacity-Aware Risk Index (CCRI)           │         │
│   │                                                  │         │
│   │   CCRI(t) = f( ŷ(t), σ(t), P(peak|t), C, history )│         │
│   │                                                  │         │
│   │   ┌─────────┬─────────┬─────────┐                │         │
│   │   │ Normal  │  High   │Critical │                │         │
│   │   │ ŷ<0.85C │0.85≤<0.95│ ≥0.95C │                │         │
│   │   └─────────┴─────────┴─────────┘                │         │
│   │                                                  │         │
│   │   觀察: 4.17% 高風險時段 → 81.25% 事件覆蓋        │         │
│   └────────────────────────┬─────────────────────────┘         │
│                            ▼                                    │
│   ┌──────────────────────────────────────────────────┐         │
│   │  ★ L3: Soft DR Action Recommender                 │         │
│   │                                                  │         │
│   │   IF CCRI = High:                                │         │
│   │     a1: 空調設定 +1 ℃ (全樓)                     │         │
│   │     a2: 非關鍵設備錯峰 15 min                    │         │
│   │   IF CCRI = Critical:                            │         │
│   │     a3: 空調 +2 ℃ + 樓宇差異化                   │         │
│   │     a4: 教學樓優先豁免、實驗樓豁免、宿舍 +1.5 ℃   │         │
│   │                                                  │         │
│   │   輸出: 動作-時段-樓宇 三維推薦矩陣              │         │
│   │   驗證: 109 kW 削峰 / 60% 高風險時長壓縮         │         │
│   └────────────────────────┬─────────────────────────┘         │
│                            ▼                                    │
│   ┌──────────────────────────────────────────────────┐         │
│   │  ★ L4: SHAP-based Explanation Layer               │         │
│   │   • Tree SHAP (對 LightGBM)                       │         │
│   │   • DeepSHAP (對 GRU)                             │         │
│   │   • Summary / Dependence / Force Plot 三類圖     │         │
│   └────────────────────────┬─────────────────────────┘         │
│                            ▼                                    │
│   ┌──────────────────────────────────────────────────┐         │
│   │  (Optional) L5: Online Feedback Loop              │         │
│   │   • 觀測實際削峰量                                │         │
│   │   • 月度模型 fine-tune                            │         │
│   │   • Conformal Prediction 區間更新                 │         │
│   └──────────────────────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. **七大方法論創新點**（Novel Contributions）

### 創新點 1 (核心): Dual-Head Joint Learning Architecture 雙頭聯合學習架構

**問題**:
既有研究多用單一模型 (LightGBM **或** GRU) 同時做負載預測與峰值識別。但**這兩個任務的損失函數本質不同**—回歸任務求最小化 MSE (平等對待所有點)、分類任務求最大化 F1 (聚焦少數類)。單一模型必有取捨。

**創新**:
- Head A (LightGBM): 連續負載回歸，捕捉「平均行為」
- Head B (GRU): 峰值事件分類 (focal loss)，捕捉「臨界行為」
- 二者共享 Day-Embedding 與氣象特徵層，但獨立輸出
- 整合層融合 ŷ(t) 與 P(peak|t) 得到 CCRI

**文獻新意**:
- *Energies* 期刊近期 (P3 LSTM-XGBoost Hybrid 2025) 雖有混合，但目的是**精度疊加**而非**任務分工**
- 本研究的「任務分工式雙頭」屬**新組合**

**支撐**:
Ke 2017 LightGBM (L1); Cho 2014 GRU (L4); Lin 2017 Focal Loss (N2)

---

### 創新點 2 (核心): Day-Type Embedding for Campus Calendar 校歷感知日類嵌入

**問題**:
既有研究多將「星期幾」「節假日」作為 one-hot 特徵。但校園日歷有遠超週度週期的結構—**學期/暑假/考試週/迎新週/校慶**，且不同類型日的「氣象-負載」響應曲線**根本不同**（暑期高溫日只有部分樓宇開機、學期高溫日所有教學樓全開）。

**創新**:
- 定義 5–7 種 day-type 標籤
- 學習 d 維 day-type embedding (e.g., d=8)
- 將 embedding 與小時級特徵 concat 後送入下游模型
- **進階版**: 不依賴人工標籤，用 K-Means / DTW clustering 從歷史曲線自動學出 day-type

**文獻新意**:
- Amber 2017 識別了校歷的影響但未量化嵌入
- Jasim 2025 (Energy Nexus) 指出此一缺口

**支撐**:
Amber et al. 2017; Jasim et al. 2025

---

### 創新點 3 (核心): Contract-Capacity Risk Index (CCRI) 合同容量風險指數

**問題**:
既有 DR 文獻多以**電價信號**或**系統頻率**為觸發。但大學等以**合同容量計費**的用戶，真正的財務驅動是**「不超約」而非電價套利**。

**創新**:
定義
```
CCRI(t) = w₁·ŷ(t)/C + w₂·P(peak|t) + w₃·E[duration|t]
```
其中：
- ŷ(t)/C: 預測負載對合同容量的相對比
- P(peak|t): GRU 給出的峰值概率
- E[duration|t]: 預期高負荷持續時長

三層分類：
- Normal: CCRI < θ₁ (e.g. 0.75)
- High: θ₁ ≤ CCRI < θ₂ (e.g. 0.90)
- Critical: CCRI ≥ θ₂

**文獻新意**:
- *Energies* 18(19) 5217 (P6) 提出 DR 潛力預測但未基於合同容量
- ACM e-Energy 2024 用分位數但未連結合同容量

**支撐**:
P6 Energies DR Review; FERC 2025; D3 DRL Commercial Cluster

---

### 創新點 4: Counterfactual SDR Action-Benefit Decomposition 反事實 SDR 動作效益拆解

**問題**:
多數研究只報告**總削峰量**，但運維者問的是「**每個動作貢獻多少？**」、「**取捨哪個成本最低？**」

**創新**:
對每個 SDR 動作 aᵢ 做反事實評估：
```
Δ_load(aᵢ, t, b) = ŷ_baseline(t, b) − ŷ_counterfactual(t, b | aᵢ applied)
```
其中 b = 樓宇 (building)。

形成「**動作 × 時段 × 樓宇**」三維貢獻矩陣，可：
- 推薦最低擾動組合
- 解釋為何選 a₁+a₃ 而非 a₂+a₄

**文獻新意**:
- ACM e-Energy 2024 有 override 機制但未做動作拆解
- Energies P5 列出多種 KPI 但無細粒度動作量化

**支撐**:
Energies P5 (Grid-Interactive Buildings Review); Counterfactual reasoning literature

---

### 創新點 5: Duration-Aware Risk Metric 風險持續時長指標

**問題**:
DR 文獻幾乎都用「削峰量 (kW)」為指標。但合同容量超約罰款多按**超約小時**累計，**「高風險狀態維持多久」才是真實壓力**。

**創新**:
引入兩個指標：
- **Risk Duration Compression Ratio (RDCR)** = 1 − (T_risk_with_SDR / T_risk_baseline)
- **Capacity Excursion Hours (CEH)** = ∑ I(ŷ(t) > 0.95·C)

您實證: 組合 SDR 使 RDCR = 60%

**文獻新意**:
- 目前無 DR 論文以此為主指標
- 與 Energies P5 (1%–65% 峰削) 互補但維度不同

**支撐**: 原創觀察

---

### 創新點 6: SHAP-Verified Physical Consistency 物理一致性驗證

**問題**:
ML 模型在能源工程的接受度受限於「黑箱」疑慮。即使 SHAP 是常用工具，**多數研究只展示 SHAP 圖而不論其是否符合物理規律**。

**創新**:
- 預先列出 4–5 條物理 prior（如「氣溫上升 1℃ → 冷負荷增 X%」、「15:00 為日峰」、「週末負載 < 工作日」）
- 用 SHAP dependence plot 驗證模型是否學到這些 prior
- 形成「**物理一致性檢核表**」作為模型可信度的第三方證據

**文獻新意**:
- SSA-Bi-LSTM 2026 用 SHAP 但未做 prior 對齊
- Lundberg 2017 原始論文未論能源領域應用

**支撐**:
Lundberg & Lee 2017 (L3); SSA-Bi-LSTM 2026 (C2)

---

### 創新點 7 (Future Extension): Conformal Risk Calibration 共形風險校準

**問題**:
CCRI 給出三層分類但無**統計覆蓋率保證**—模型說 Critical，實際發生概率多少？

**創新**（**作為論文 Future Work 章節 + 強化 Discussion**）:
- 套用 Conformalized Quantile Regression (Romano 2019)
- 為每個風險級別給出 finite-sample coverage guarantee
- 例：「Critical 預警，95% 概率超約 ≥ 10 分鐘」

**支撐**:
Romano et al. 2019 NeurIPS (O1); Hong & Fan 2016 (O2)

---

## 4. 對標 Energies 的方法論差異化

| 維度 | Energies 近期 (P1–P10) 典型 | 本研究 |
|------|----------------------------|--------|
| 模型 | 單模型 OR 混合疊加 | **雙頭任務分工** |
| 風險定義 | 閾值或分位數 | **合同容量導向 CCRI** |
| DR 評估 | 總削峰量 | **動作拆解 + 持續時長壓縮** |
| 可解釋性 | SHAP 圖 | **物理 prior 對齊驗證** |
| 不確定性 | 點預測 | (Future) **CQR 校準** |
| 校歷處理 | one-hot | **Day-Type Embedding** |

**這六項組合中**：
- 任 1 項提升一個版本即可達 Q2 投稿
- 任 3 項組合則具 Q1 期刊潛力（如 Applied Energy / Energy and Buildings）

---

## 5. 整體執行流程 (Step-by-Step Pipeline)

**待您傳資料後**，按以下步驟執行。每步**自成一個產出**，可獨立 review：

```
Step 0: 資料診斷 (Data Diagnostic)         [10 min]
   • 接收您的負荷 + AMeDAS + 校歷資料
   • 缺失值 / outlier / 時區一致性檢查
   • 季節性 / 平穩性 / 自相關分析
   • 產出: data_diagnostic_report.md

Step 1: 特徵工程 (Feature Engineering)     [30 min]
   • 時序滯後特徵 (1h, 24h, 168h)
   • 體感溫度 / WBGT 計算
   • Day-Type 標籤 / Embedding
   • 樓宇分項聚合
   • 產出: features.parquet + feature_dict.md

Step 2: Walk-Forward CV 分割              [10 min]
   • 訓練 / 驗證 / 測試切分
   • 不重疊滑動窗
   • 引用 Bergmeir 2012 為理論依據
   • 產出: cv_splits.json + cv_design.md

Step 3: 模型訓練 - Head A (LightGBM)       [20 min]
   • Optuna 貝葉斯超參搜索 (100 trials)
   • 早停 + 正則化
   • 報告 MAE / RMSE / MAPE / R²
   • 產出: model_lightgbm.pkl + metrics_lightgbm.json

Step 4: 模型訓練 - Head B (GRU)            [30 min]
   • 隱層維度 / 序列長度搜索
   • Focal Loss 訓練
   • 報告 F1 / PR-AUC / Recall@P
   • 產出: model_gru.pt + metrics_gru.json

Step 5: 基準對照模型                       [20 min]
   • Random Forest, XGBoost, LSTM (對照組)
   • 統一評估
   • 產出: baseline_comparison.csv

Step 6: 統計顯著性檢定                     [10 min]
   • Diebold-Mariano test
   • Friedman + Nemenyi post-hoc
   • 產出: significance_tests.md

Step 7: CCRI 風險指數計算                  [20 min]
   • 三層分類 (閾值校準)
   • 混淆矩陣 / 風險覆蓋率
   • 產出: ccri_results.csv + ccri_plot.png

Step 8: SDR 動作反事實評估                 [40 min]
   • 三種動作組合的削峰量
   • 樓宇分項拆解
   • RDCR 計算
   • 產出: sdr_action_matrix.csv + benefit_decomp.png

Step 9: SHAP 解釋性分析                    [30 min]
   • Tree SHAP / DeepSHAP
   • Summary / Dependence / Force plots
   • 物理 prior 對齊檢核表
   • 產出: shap_plots/ + physical_consistency.md

Step 10: 統一報告                          [30 min]
   • 整合 Step 1–9 結果
   • 對應論文 Section 3–5
   • 產出: final_results.md
```

**總預估時間**: 4–5 小時（純執行）；含您 review 與修正可能 1–2 天。

---

## 6. 需要您提供的資料規格

### 6.1 校園電力負荷
- **粒度**: 小時級 (建議 ≥ 1 年；2 年以上更佳)
- **欄位**:
  - timestamp (yyyy-mm-dd HH:00)
  - total_load_kW
  - (可選) building-level load: teaching_kW, lab_kW, dorm_kW, admin_kW
- **格式**: CSV / Parquet / Excel 皆可

### 6.2 AMeDAS 氣象資料
- **站點**: 距校園最近一站
- **粒度**: 小時級
- **欄位**:
  - timestamp
  - temperature_C (氣溫)
  - humidity_pct (相對濕度)
  - precipitation_mm (降水)
  - wind_speed_mps (風速)
  - (可選) global_solar_radiation_MJ (日射量)

### 6.3 校歷資訊
- **粒度**: 日級
- **欄位**:
  - date
  - day_type (其一: regular_term / exam_week / summer_break / national_holiday / weekend / special_event)
  - is_class_day (boolean)

### 6.4 合同容量
- **單值**: C = 2,000 kW (已確認)
- **(可選)**: 歷史變更紀錄

### 6.5 樓宇基本資訊（可選但推薦）
- 各樓宇面積、樓層數、主要用途
- 用於樓宇差異化動作設計

---

## 7. 框架調整選項（請您選擇）

請就以下 4 個方向確認您的偏好；之後我即可開始資料診斷與框架代碼搭建。

| 選項 | 子問題 |
|------|--------|
| 創新點優先序 | 7 個創新點是否全採？或聚焦其中 3–4 個？ |
| Day-Type 標籤 | 人工標籤 OR 自動 clustering？ |
| 樓宇分項 | 您是否有樓宇分項資料？若無，創新點 4 (動作拆解) 需簡化 |
| Conformal Prediction | 納入論文主體 OR 留作 Future Work？ |

---

## 8. 框架完備後的下一步預告

確認方案 → 您傳資料 → 我執行 Step 0–10 → 產出**完整 Results 章節材料** → 自動套入論文模板 → 投稿準備
