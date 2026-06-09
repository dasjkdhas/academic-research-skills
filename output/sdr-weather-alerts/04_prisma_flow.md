# PRISMA 2020 Flow Diagram
## 校園夏季天氣驅動 DR 預警系統研究

**Phase**: 2 — Investigation
**Version**: v1 (post Wave 2)
**Date**: 2026-05-16

---

## 檢索字串（最終版）

### Boolean Query (English)
```
TS = (("demand response" OR "demand-side management" OR "negawatt" OR
       "load curtailment" OR "peak shaving")
  AND ("university" OR "universities" OR "college" OR "campus" OR
       "higher education" OR "academic building" OR "K-12 school")
  AND ("weather" OR "meteorological" OR "temperature" OR "heat wave" OR
       "heatwave" OR "thermal comfort" OR "outdoor air")
  AND ("machine learning" OR "deep learning" OR "neural network" OR
       "LSTM" OR "transformer" OR "attention" OR "reinforcement learning" OR
       "XGBoost" OR "ensemble learning")
  AND ("alert" OR "warning" OR "early warning" OR "threshold" OR
       "trigger" OR "notification"))
```

### Boolean Query (Traditional Chinese)
```
("需量反應" OR "需求側管理" OR "削峰") AND
("校園" OR "大學" OR "高等教育") AND
("天氣" OR "氣象" OR "熱浪" OR "體感溫度") AND
("機器學習" OR "深度學習" OR "LSTM" OR "Transformer" OR "強化學習") AND
("預警" OR "警示" OR "閾值" OR "觸發")
```

### Boolean Query (日本語)
```
(「デマンドレスポンス」 OR 「需要応答」 OR 「ネガワット」) AND
(「大学」 OR 「キャンパス」 OR 「学校」) AND
(「天気」 OR 「気象」 OR 「熱波」 OR 「外気温」) AND
(「機械学習」 OR 「深層学習」 OR 「LSTM」 OR 「強化学習」)
```

### Boolean Query (한국어)
```
("수요반응" OR "디맨드리스폰스") AND ("대학" OR "캠퍼스") AND
("날씨" OR "기상" OR "폭염") AND ("기계학습" OR "딥러닝" OR "LSTM" OR "강화학습")
```

---

## 資料庫覆蓋

| 資料庫 | 領域 | 語言 |
|--------|------|------|
| Scopus | 跨領域 | 英 |
| Web of Science | 跨領域 | 英 |
| IEEE Xplore | 電機/能源/AI | 英 |
| ScienceDirect (Elsevier) | 多領域 | 英 |
| MDPI | OA 跨領域 | 英 |
| arXiv | preprint | 英 |
| CNKI (中國知網) | 中文 | 中 |
| J-STAGE | 日本科技論文 | 日 |
| KCI (Korea Citation Index) | 韓國 | 韓 |
| NDLTD Taiwan | 台灣博碩士論文 | 中 |
| Korea Science | 韓國 OA | 韓/英 |
| Google Scholar | 補充檢索 | 多語 |

---

## PRISMA 2020 Flow (ASCII Diagram)

```
                    ┌───────────────────────────────────────┐
                    │     IDENTIFICATION (識別)             │
                    └───────────────────────────────────────┘

Records identified from databases (n = TBD):
  Scopus              ~280
  Web of Science      ~220
  IEEE Xplore         ~150
  ScienceDirect       ~310
  MDPI                ~95
  arXiv               ~110
  CNKI (中國知網)     ~180
  J-STAGE             ~85
  KCI                 ~62
  NDLTD Taiwan        ~40
  Korea Science       ~30
  Google Scholar      ~200 (top hits, 補漏)
  ────────────────────────
  Total              ~1,762  (估計值，待 Phase 2 完整檢索確認)

Records from other sources:
  Citation chasing (snowball)    ~40
  Hand-search of key journals    ~25  (Energy & Buildings, Applied
                                       Energy, IEEE TSG, Smart Cities)
  ────────────────────────
  Total non-DB                   ~65

                                ▼
                    ┌───────────────────────────────────────┐
                    │     SCREENING (篩選)                  │
                    └───────────────────────────────────────┘

Records after duplicate removal           ~1,420
                                ▼
Records screened by title/abstract        ~1,420
                                ▼
Records excluded                          ~1,180
  Reasons:
    - Not on DR or load forecasting:        ~480
    - Not on campus/university setting:     ~320
    - Pre-2015 (outside DL era):            ~95
    - Not in target languages (EN/ZH/JA/KO):~70
    - Non-research (op-ed, editorial):      ~60
    - Off-topic (e.g. cybersecurity-only):  ~155

                                ▼
                    ┌───────────────────────────────────────┐
                    │     ELIGIBILITY (合資格性)             │
                    └───────────────────────────────────────┘

Reports sought for retrieval              ~240
Reports not retrieved (paywall/lost)      ~25
                                ▼
Reports assessed for eligibility          ~215
Reports excluded:
  - No weather feature integration:        ~40
  - No ML/DL model:                        ~35
  - No DR alert/trigger mechanism:         ~50
  - Insufficient data/methods reporting:   ~25
                                ▼

                    ┌───────────────────────────────────────┐
                    │     INCLUDED (納入)                   │
                    └───────────────────────────────────────┘

Studies included in qualitative synthesis  ~65–80 (預計)
  - Empirical ML model studies:          ~35
  - Policy / DR programme analyses:      ~12
  - Case studies (campus/building):      ~15
  - Reviews / Meta-analyses:             ~5
  - Standards / Technical guidelines:     ~5

Studies included in narrative synthesis    ~65–80
(Meta-analysis 不適用—模型架構與資料異質性過高)

                                ▼
              ⭐ Current Wave-2 manual collection: 45 verified
                 (Phase 2 完整化目標: 補齊至 ~75)
```

---

## 納入/排除準則

### 納入準則 (Inclusion)
1. **時間**: 2015-01-01 至 2026-05-16 (DL 主流時代)
2. **設定**: 高等教育校園 / 學校 / 教育性建築為主；商辦/住宅僅作對照
3. **方法**: 至少含一種 ML/DL 模型 (含 RL)
4. **議題**: 直接涉及 DR、預警機制、負載預測、能源管理至少一項
5. **天氣整合**: 須以天氣資料為輸入特徵 (T, RH, GHI, WBGT 等任一)
6. **語言**: 英文、繁/簡中文、日文、韓文
7. **同儕審查**: 期刊論文、會議論文、博碩士論文；灰色文獻僅納權威機構 (政府、IEA、IEEE 標準)

### 排除準則 (Exclusion)
1. 純供應側/發電端調度研究
2. 純儲能控制最適化 (除非作為 DR 對照)
3. 純物理模擬 (EnergyPlus etc.) 無資料驅動成分
4. 純政策研究無實證或方法論
5. 重複出版 (採後續更完整版本)
6. 通訊資料/摘要不足以判斷方法

---

## 風險偏誤評估 (Risk of Bias)

由於本研究擬納入之文獻為非隨機化 ML 模型驗證研究，採 ROBINS-I 框架評估：

| 維度 | 評估面向 |
|------|---------|
| Confounding | 資料分割是否考量季節性/年度循環？ |
| Selection | 案例校園是否代表性？ (規模、氣候帶、運轉模式) |
| Classification | 預警分級之 ground truth 如何定義？ |
| Deviations | 模型訓練/部署是否一致？ |
| Missing data | 智慧電表/氣象資料缺失處理 |
| Measurement | 標籤泄漏 (label leakage) 風險 |
| Reporting | 是否完整揭露超參數、種子、運行時間？ |

---

## Phase 2 完整化工作量估計

| 工作項 | 預估時間 |
|--------|---------|
| CNKI 完整檢索 + 翻譯篩選 | 8 小時 |
| J-STAGE 補強 (15+ 篇) | 5 小時 |
| KCI 補強 (10+ 篇) | 4 小時 |
| NDLTD 台灣論文 | 3 小時 |
| Snowballing (前向+後向) | 6 小時 |
| 全文取得與品質評分 | 10 小時 |
| Semantic Scholar API 驗證 | 2 小時 |
| **總計** | **~38 小時** |
