# Thematic Synthesis Matrix
## 校園夏季天氣驅動 DR 預警系統研究

**Phase**: 2-3 橋接 — Literature × Theme cross-tabulation
**Date**: 2026-05-16

---

## 主題編碼 (Theme Codes)

| Code | 主題 | 描述 |
|------|------|------|
| **T1** | 天氣特徵整合 | NWP / 體感 / AI 氣象 → 負載特徵工程 |
| **T2** | 模型架構 | LSTM / Transformer / Attention / RL |
| **T3** | 預警觸發機制 | 閾值設計、分級警示、override |
| **T4** | 校園特殊性 | 學期/暑假切換、實驗室、宿舍 |
| **T5** | 跨地比較 | 台日韓中政策與技術差異 |
| **T6** | 公平性 / 舒適性 | 學生族群、室內熱環境 |
| **T7** | 可解釋性 | SHAP / Attention 可視化 |
| **T8** | 標準化通訊 | OpenADR / OASIS EI |
| **T9** | 經濟誘因 / 政策 | 計減型、誘因型、tariff |
| **T10** | 系統整合 | BEMS / VPP / Microgrid / DT |

---

## Source × Theme Matrix

凡例：⭐ = 核心貢獻；● = 涵蓋；○ = 部分提及；空白 = 未涵蓋

| 編號 | 來源 (簡稱) | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 |
|------|------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|
| A1 | Nature Comms 2023 (PMC10550920) IDR 熱浪 | ⭐ | | ● | | | ⭐ | | | ⭐ | |
| A2 | Chen 2022 China DR 政策 | | | ○ | | ⭐ | | | | ⭐ | ● |
| A3 | 台電 2024 需量反應措施 | | | ● | | ⭐ | | | ● | ⭐ | ● |
| A4 | METI Negawatt 2019 | | | ● | | ⭐ | | | ⭐ | ⭐ | ● |
| A5 | J-STAGE SHASE 47(300) MPC-DR | ○ | ● | ⭐ | | ● | | | | | ⭐ |
| A6 | FERC 2025 DR Assessment | | | ● | | | | | ● | ⭐ | |
| A7 | OpenADR 2.0 Guide | | | ● | | | | | ⭐ | ● | ⭐ |
| B1 | NextDrive 文欣國小 VPP | ● | ● | ● | ● | ⭐ | | | | ● | ⭐ |
| B2 | Yokohama Smart City | ● | ○ | ⭐ | | ⭐ | | | ● | ● | ⭐ |
| B3 | Chiang Mai Digital Twin | ● | ● | ○ | ⭐ | ● | | | | | ⭐ |
| B4 | Spain Smart Campus IoT | ● | ● | ○ | ● | | | | | | ⭐ |
| B5 | Jasim 2025 Campus EMS Review (anchor) | ● | ● | ● | ⭐ | ● | ○ | ○ | ○ | ● | ⭐ |
| B6 | Smart Cities 8(1):30 SGEMS | ● | ⭐ | ● | ⭐ | | | | | | ⭐ |
| B7 | Smart Cities 9(1):18 Campus Microgrid | ● | ⭐ | ● | ⭐ | | | | | ● | ⭐ |
| B8 | Lim 2014 韓國校園調查 | ● | | | ⭐ | ⭐ | ● | | | | |
| B9 | SNU 2023 碳中和路徑 | ○ | | | ⭐ | ⭐ | | | | ● | |
| B10 | Korea Univ Low-Carbon 2025 | ● | | | ⭐ | ⭐ | | | | | ● |
| B11 | H 大學能耗結構 2021 | ○ | | | ⭐ | ⭐ | | | | | |
| B12 | 成功大學節能指標 | ● | | | ⭐ | ⭐ | | | | | ● |
| B13 | 台大能源管理經驗 | | | | ⭐ | ⭐ | | | | ● | ● |
| B14 | PMC9737343 智慧校園 IoT | ● | ● | ○ | ● | | | | | | ⭐ |
| B15 | arxiv:2403.15395 Smart Campus IoT | ● | ● | ○ | ⭐ | | | | | | ⭐ |
| C1 | Kitakyushu A-LSTM 2021 | ⭐ | ⭐ | | ● | ● | | ● | | | |
| C2 | SSA-Bi-LSTM + SHAP 2026 | ⭐ | ⭐ | | | | | ⭐ | | | |
| C3 | CRG-Informer Hangzhou | ⭐ | ⭐ | | ○ | ● | | ○ | | | |
| C4 | Transfer Learning Transformers 2025 | ⭐ | ⭐ | | ● | | | | | | |
| C5 | arxiv:2503.05813 Regional GRU | ⭐ | ⭐ | | | | | | | | |
| C6 | Cheongju DH (Nature Sci Rep) | ⭐ | ● | | | ⭐ | | ⭐ | | | |
| C7 | Yeungnam ensemble | ● | ● | | ● | ● | | | | | |
| C8 | arxiv:2501.05000 DL 是否值得 | ● | ⭐ | | | | | | | | |
| C9 | Auto-DL+IoT Univ case 2025 | ● | ⭐ | ○ | ⭐ | | | | | | ⭐ |
| C10 | Short-term LF Survey 2025 | ● | ⭐ | | | | | | | | |
| C11 | J-STAGE SHASE 46(293) Hybrid PHY+ML | ⭐ | ⭐ | | | ⭐ | | | | | |
| C12 | J-STAGE 2020.9 DL HVAC for RL | ● | ⭐ | | | ⭐ | | | | | ● |
| C13 | Park 2023 NRF Transformer 韓 | ⭐ | ⭐ | | | ⭐ | | | | | |
| C14 | Tropical Campus ML 2025 | ⭐ | ⭐ | | ⭐ | ● | ○ | | | | |
| C15 | Asian cities EFLH | ⭐ | | | ● | ⭐ | | | | | |
| D1 | ACM e-Energy 2024 RL Override | ● | ⭐ | ⭐ | | | ⭐ | | ● | | |
| D2 | Vázquez-Canteli RL Review 2019 | ● | ⭐ | ● | | | | | | ● | |
| D3 | DRL Commercial Cluster 2021 | ● | ⭐ | ⭐ | | | | | | ● | ● |
| D4 | RL Commercial 2025 | ● | ⭐ | ● | | | | | | | ● |
| D5 | DRL Multi-Energy 2025 | | ⭐ | | | | | | | ● | ⭐ |
| E1 | npj Clim Atmos 2024 AI NWP | ⭐ | | | | ⭐ | | | | | |
| E2 | DCS NWP 預測 | ⭐ | ⭐ | | | | | | | | ● |
| F1 | Energies 18(19) DR Forecast Review | ⭐ | ● | ● | | | | | | ● | ● |
| F2 | ESJ 2025 PRISMA Residential | ● | ⭐ | | | | | | | | |
| F3 | JIMESE 2025 ML/DL Review | ⭐ | ⭐ | | | | | | | | |
| G1 | NERC EEA / CAISO Flex Alert | ○ | | ⭐ | | | | | ● | ⭐ | |
| G2 | WHO Heatwave EWS | ⭐ | | ⭐ | | | ⭐ | | | | |

---

## 主題覆蓋密度分析

| 主題 | ⭐ 核心 | ● 涵蓋 | ○ 部分 | 總密度 |
|------|---------|---------|---------|---------|
| T1 天氣特徵整合 | 17 | 9 | 4 | 30 |
| T2 模型架構 | 21 | 7 | 1 | 29 |
| T3 預警觸發機制 | 6 | 13 | 5 | 24 |
| T4 校園特殊性 | 13 | 10 | 0 | 23 |
| T5 跨地比較 | 16 | 6 | 0 | 22 |
| T6 公平性/舒適性 | 3 | 3 | 2 | 8 |
| T7 可解釋性 | 2 | 1 | 3 | 6 |
| T8 標準化通訊 | 2 | 4 | 0 | 6 |
| T9 經濟誘因/政策 | 6 | 11 | 0 | 17 |
| T10 系統整合 | 12 | 9 | 0 | 21 |

---

## 關鍵觀察 (Synthesis Findings)

### 1. 高密度主題（充分既有研究）
- **T1 天氣特徵整合** + **T2 模型架構** + **T4 校園特殊性** + **T5 跨地比較**
- 暗示：基礎技術成熟；本研究可站在巨人肩膀上

### 2. 低密度主題（研究缺口 / 機會）⭐
- **T6 公平性/舒適性** — 僅 8 (Nature Comms 2023 唯一突出)
- **T7 可解釋性** — 僅 6 (SSA-Bi-LSTM SHAP 2026 為主)
- **T8 標準化通訊** — 僅 6，且多為灰色文獻 → 學術論文整合 OpenADR + ML 預警有研究機會

### 3. 中密度主題（可作為對比/驗證）
- **T3 預警觸發機制** — 24，但深度多在工業/商辦；校園預警仍空白
- **T9 政策誘因** — 17，多單一國家分析；跨東亞 4 地比較稀少
- **T10 系統整合** — 21，本研究可貢獻 ML-DR-OpenADR 整合架構

### 4. 矛盾與爭議 (Contradictions)
| 議題 | A 立場 (代表文獻) | B 立場 (代表文獻) |
|------|-------------------|-------------------|
| Transformer 是否優於 LSTM | Park 2023 (Transformer 三維最佳) | arxiv:2501.05000 (DL 對小規模未必值得) |
| 自動 vs 人在迴圈 DR | OpenADR / NERC EEA (自動化) | ACM e-Energy 2024 (override + RL) |
| 校園夏季峰值在學期/暑假 | 多數研究 (學期末) | NextDrive 案例 (暑期 VPP 仍價值) |

### 5. Methodological Insights for Phase 3
- **資料受限校園**: 採 transfer learning (C4) 或 hybrid physics-ML (C11) 是合理路徑
- **解釋性**: SSA-Bi-LSTM+SHAP (C2) 為當前 SOTA，本研究宜對標
- **預警分級**: 沿用 NERC EEA 三層 (Advisory/Warning/Emergency)，閾值用分位數 (D3) 而非絕對值
- **PRISMA + LLM 篩選**: ESJ 2025 (F2) 提供方法論可複製
