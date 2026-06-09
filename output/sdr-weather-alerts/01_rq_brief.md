# Research Question Brief
## 校園夏季天氣驅動需量反應 (DR) 預警系統研究

**Generated**: 2026-05-16
**Phase**: 1 — Scoping
**Mode**: deep-research full → academic-pipeline

---

## 1. 主要研究問題 (Primary RQ)

> **如何運用機器學習模型整合多源天氣預報資料，建構面向東亞校園夏季供電緊張情境的需量反應預警機制，使預測精度與預警觸發時序兼顧能源削峰效益、空調舒適性與決策可解釋性？**

**英文版**:
> How can machine-learning models that fuse multi-source weather forecasts be designed to deliver weather-triggered demand-response (DR) alerts for East-Asian university campuses during summer peak periods, optimizing peak-shaving effectiveness, thermal comfort, and decision interpretability?

---

## 2. 次研究問題 (Sub-RQs)

| # | Sub-RQ | 性質 |
|---|--------|------|
| SQ1 | 在東亞氣候條件下 (台灣/日韓中)，哪些天氣特徵 (溫度、體感溫度、輻射量、濕度) 對校園夏季冷氣負載最具預測力？ | 描述性 + 預測性 |
| SQ2 | LSTM、Transformer、Attention-based 模型在中短期 (1–24h) 校園冷氣負載預測上的相對表現與資料效率為何？ | 比較性 |
| SQ3 | 預警觸發機制 (固定閾值 vs 自適應分位數 vs 強化學習) 在「漏報率—誤報率—使用者疲勞」三角下的最適設計為何？ | 規範性 |

---

## 3. FINER 評分

| 維度 | 評分 (1–5) | 說明 |
|------|------------|------|
| **F**easible (可行性) | 4 | 公開氣象資料 (CWA/JMA/KMA/CMA)、台電/Yokohama/Cheongju 公開負載資料、開源 ML 框架皆可取得；硬體 (Raspberry Pi + Modbus) 入門門檻低 |
| **I**nteresting (重要性) | 5 | 2022 Yokohama 案例 22.8% 削峰、Nature Comms 2023 熱浪 IDR 研究、台灣 2021 桃園文欣國小校園 VPP 30% 削減，三大區位均有實證需求 |
| **N**ovel (新穎性) | 4 | 多數既有研究集中於商辦/工業；**校園情境** (學期/暑假切換、無人化暑期、學生宿舍) 與**天氣驅動預警機制**之交集仍屬研究缺口 |
| **E**thical (倫理性) | 5 | 觀測級資料、無生物實驗；唯需關注學生宿舍熱舒適與弱勢族群保護 (cf. PMC10550920) |
| **R**elevant (時效性) | 5 | 中國 NDRC 規定各省 2025 年起 DR 容量達年度最大負載 3%；台電 113 年 1 月最新修訂《需量反應負載管理措施》；契合 2026 年 ICAP/COP 議程 |

**總分**: 23/25 ✅ Pass

---

## 4. 範圍界定

### In-Scope (包含)
- **地理**: 台灣、日本、韓國、中國大陸的高等教育機構 (大學校園主體；K-12 案例僅作對照)
- **時間窗**: 2015–2026 文獻 (深度學習興起後)，重點為 2020 後
- **能源類別**: 夏季制冷空調負載 (HVAC cooling)、總電力負載中與天氣相關之部分
- **預測時域**: 短期 (15 min–1 h) 與 中短期 (3–24 h day-ahead) 預警
- **天氣資料源**: 數值天氣預報 (NWP)、氣象 AI 模型 (FengWu/FuXi/Pangu)、體感溫度指標 (WBGT、Heat Index)
- **ML 模型族**: LSTM/Bi-LSTM、Attention-LSTM、Transformer (Informer/TFT)、CNN-BiLSTM-Attention、強化學習 (RL/DRL)
- **預警機制**: 閾值設計、人因介面、觸發時序、誤/漏報權衡、用戶疲勞

### Out-of-Scope (排除)
- 純供應端調度 (發電端 unit commitment)
- 微電網/儲能控制最適化 (除非作為 DR 對照機制)
- 工業/商辦/住宅大樓 (僅作背景/對照引用)
- 冬季供暖負載 (台灣語境主要關注夏季)
- 非東亞地區案例 (歐美僅作政策對照)

---

## 5. 核心關鍵詞 (Boolean 檢索字串)

```
(("demand response" OR "需量反應" OR "negawatt" OR "load curtailment")
  AND ("university" OR "campus" OR "校園" OR "high school" OR "school")
  AND ("weather" OR "temperature" OR "heatwave" OR "氣象" OR "熱浪")
  AND ("machine learning" OR "deep learning" OR "LSTM" OR "Transformer"
       OR "attention" OR "reinforcement learning" OR "機器學習" OR "深度學習")
  AND ("alert" OR "warning" OR "early warning" OR "threshold" OR "trigger"
       OR "預警" OR "警示" OR "閾值"))
```

**目標資料庫**: Scopus, Web of Science, IEEE Xplore, ScienceDirect, arXiv, CNKI (中國知網), J-STAGE (日), NDLTD (台灣博碩士論文)

---

## 6. 預期貢獻

1. **理論**: 提出整合 NWP + 體感指標 + 校園作息模式的 hybrid 特徵工程框架
2. **方法**: 比較 Attention-LSTM / Informer / TFT 於資料受限校園情境的相對表現 (含 transfer learning 評估)
3. **實務**: 設計三層預警機制 (advisory / warning / emergency) 對應台電/Taipower 與東亞各國 DR 計畫
4. **政策**: 提出校園作為虛擬電廠 (Campus-as-VPP) 的可複製方案

---

## 7. Devil's Advocate Checkpoint 1 (自評)

| 質疑 | 回應 |
|------|------|
| **「校園夏季用電其實主要在暑假前 6 月，6-8 月暑假反而低，這個 RQ 是否錯置？」** | ✅ 已收斂為「學期末峰值 + 暑期實驗室/伺服器/補習班負載」雙情境，並引 NextDrive 案例證實暑期仍有 VPP 餘電價值 |
| **「LSTM/Transformer 在小規模校園資料上是否過擬合？傳統 SARIMAX 是否更合適？」** | ⚠️ 須在 Methodology 中明列 baseline 比較 (含 ARIMAX、SVR、XGBoost)，並引 arxiv:2501.05000 對 deep-learning 在小規模社群是否值得的辯論 |
| **「Nature Comms 2023 已證明 IDR 削峰效果，那再做這題的邊際貢獻為何？」** | ✅ 該研究聚焦住宅且未涉及天氣預測整合與預警時序設計；本研究填補「校園 + 預警 + 模型可解釋性」三維交集 |
| **「預警機制本身是 HCI 議題，ML 研究做這個是否越界？」** | 部分成立，須加入「決策觸發時序」與「使用者疲勞」量化指標，並引用 RL override signal 文獻 |

**裁決**: ✅ PASS with revisions to Methodology (見 02_methodology_blueprint.md)
