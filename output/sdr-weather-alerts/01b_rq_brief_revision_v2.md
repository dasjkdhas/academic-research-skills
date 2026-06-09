# Research Question Brief — Revision v2 (Aligned with实证设定)
## 大學校園高溫季電力負荷預測與風險導向 Soft Demand Response (SDR) 研究

**Revised**: 2026-05-16 (Wave 3)
**取代**: 01_rq_brief.md
**對齊**: 用戶確認的实证设定 — 日本校园 + AMeDAS + LightGBM/GRU/SHAP + 风险导向 SDR

---

## 0. 重要修正說明

第一版 (01_rq_brief.md) 將研究定位為跨東亞四地比較性研究。經用戶確認後**重新定位**：

| 維度 | v1 (原定) | v2 (對齊后) |
|------|----------|------------|
| 地理範圍 | 東亞四地 (台日韓中) 比較 | 日本單一大學校園實證 + 跨區文獻對照 |
| 氣象源 | NWP / 體感 / AI 氣象 | **AMeDAS 觀測小時資料 + 校歷** |
| 主模型 | LSTM / Transformer / Attention | **LightGBM / XGBoost / GRU + RF** (對標) |
| DR 設計 | 預警分級 + RL 觸發 | **风险导向 Soft DR (空调微调、设备错峰、楼宇差异)** |
| 解釋性 | SHAP / Attention 視覺化 | **SHAP 已为核心方法** (非可選) |
| 容量基準 | 動態閾值 | **合同容量 C = 2,000 kW 之风险指数** |

---

## 1. 主要研究問題 (Primary RQ — v2)

**中文**:
> **如何以小时级历史负荷、AMeDAS 气象资料与校园运行日历构建机器学习与深度学习模型，对大学校园高温季总体负荷与峰值风险进行精准识别与解释，并以风险导向 Soft Demand Response 实现低扰动削峰？**

**英文**:
> Machine Learning and Deep Learning for High-Temperature Campus Load Forecasting and Risk-Oriented Soft Demand Response in University Energy Management.

---

## 2. 次研究問題 (Sub-RQs — v2)

| # | Sub-RQ | 性質 | 已得結果 |
|---|--------|------|---------|
| **SQ1** | LightGBM、XGBoost、RF、LSTM、GRU 在小时级校园总体负荷预测上的相对表现？ | 比较性 | **LightGBM 最优**：MAE 18.53 kWh, RMSE 27.01 kWh, MAPE 1.89%, R²=0.9908 |
| **SQ2** | 哪种模型更适合识别峰值/高风险时段？ | 比较性 | **GRU 最优**：F1 = 0.907 (峰值识别任务) |
| **SQ3** | 在合同容量 C=2,000 kW 下，风险指数如何识别 High/Critical 风险窗口？ | 设计性 | 高风险时段占测试样本 4.17%，但覆盖 81.25% 真实高负荷事件 |
| **SQ4** | 不同 Soft DR 情境 (空调微调 / 设备错峰 / 楼宇差异) 之削峰潜力？ | 评估性 | **组合 SDR 可削峰约 109 kW**，使高风险持续时长缩短 60% |
| **SQ5** | SHAP 如何揭示气温、时段、历史负荷与建筑运行的相对贡献？ | 解释性 | (待完整呈现) — 用 SHAP 解釋風險來源 |

---

## 3. FINER 評分 (v2 修正)

| 維度 | v1 評分 | v2 評分 | v2 說明 |
|------|--------|--------|---------|
| **F**easible | 4 | **5** | 資料已採集；模型已訓練；結果已驗證 |
| **I**nteresting | 5 | **5** | 21.2% 峰值差 + 81.25% 風險覆蓋 + 60% 持續時長壓縮，三項實證數字夠力 |
| **N**ovel | 4 | **4** | 校園 × AMeDAS × LightGBM/GRU × SHAP × 風險導向 SDR 的組合屬研究空白 |
| **E**thical | 5 | **5** | 觀測級資料；SDR 設計優先考慮低擾動、不影響教學 |
| **R**elevant | 5 | **5** | 日本 2050 淨零、校園 contract demand 管理之熱點 |

**總分**: 23/25 → **24/25** ✅ Strong Pass

---

## 4. 範圍界定 (v2)

### In-Scope
- **地理**: 日本大學校園 1 個 (具體案例)
- **氣象源**: JMA AMeDAS 小時資料 (氣溫、相對濕度、降水、風速等)
- **負載資料**: 校園小時級電力負載 + 主要樓宇分項 (教學/實驗/宿舍/行政)
- **模型族**:
  - 樹模型 / GBM: Random Forest, XGBoost, **LightGBM**
  - 序列模型: LSTM, **GRU**
  - 解釋方法: **SHAP** (Tree SHAP 對 LightGBM, Deep SHAP 對 GRU)
- **預測時域**: 小時級 (1–24h day-ahead)
- **DR 類型**: **Soft DR (柔性響應)** — 不中斷供電、僅微調設定
- **風險判別**: 三層 (Normal / High / Critical) 基於合同容量 C 之分位數
- **SDR 動作集**:
  1. 空調設定溫度微調 (e.g. +1–2 ℃ during 12:00–16:00)
  2. 非關鍵設備錯峰啟動
  3. 樓宇差異化控制 (依使用率、熱舒適容忍度)

### Out-of-Scope
- 多校跨國比較 (留作 future work)
- 硬性 DR (強制斷電) / 工業計減型
- 儲能 / V2G 整合 (留作 extension)
- 電價優化問題 (本研究關注物理可行性，不涉及電價博弈)

---

## 5. 核心貢獻聲明 (Contribution Statement — v2)

本研究的學術貢獻**不在於單純比較預測精度**，而在於：

1. **方法論貢獻**: 將校園負荷預測**進一步推進到風險判斷與柔性響應支持層面**
2. **實證貢獻**: 提供**合同容量約束下**的風險指數設計範例 (4.17% 高風險時段 → 81.25% 事件覆蓋)
3. **應用貢獻**: 證明**組合 Soft DR 策略**可使高風險持續時長縮短 60%，為高校高溫季削峰、合同容量優化和運行管理**提供更具操作性的分析路徑**

---

## 6. 與 v1 範圍之差異對 Phase 3–6 的影響

| 階段 | v1 規劃 | v2 修正 |
|------|---------|---------|
| Phase 2 文獻 | 跨東亞四地全面回顧 | **日本錨點 + 跨區對照** (中重比例調整) |
| Phase 3 綜合 | 比較式表格 | **單一案例深描 + 跨區放置 (positioning)** |
| Phase 4 撰寫 | 多案例對照論文 | **單一案例 + 嚴謹 ML 比較 + 風險-SDR 閉環** |
| Phase 5 審稿模擬 | 三地 reviewer | **能源工程 + ML 方法 + 校園能源管理三位 reviewer** |
| Phase 6 終稿 | 國際英文期刊 | **中文期刊 + 英文 Energy & Buildings / Applied Energy 雙投考量** |
