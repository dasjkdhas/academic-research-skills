# Methodology Blueprint
## 校園夏季天氣驅動 DR 預警系統研究

**Phase**: 1 — Scoping
**Linked**: 01_rq_brief.md

---

## 1. 研究典範 (Research Paradigm)

**Pragmatist 實用主義**：兼採量化預測模型評估 (positivist) 與系統設計可用性訪談 (interpretivist)。

理由：本題既需嚴謹的 ML 模型誤差量測 (RMSE/MAPE/CRPS)，又需理解校園能源管理人員的決策慣性與信任邊界。

---

## 2. 研究方法選擇

### 主方法：Mixed-Methods Sequential Explanatory Design
- **Phase A (量化)**: ML 模型比較 + 預警機制模擬
- **Phase B (質性)**: 校園能管員半結構訪談 (8–12 位，台日韓各 2-4)
- **Phase C (整合)**: 設計研究 (Design Science Research, Hevner 2004) — 預警系統雛形 + 評估

### 對應 EQUATOR 報告準則
- ML 模型比較段：CONSORT-AI / TRIPOD-AI
- 質性訪談段：COREQ
- 系統設計段：DSR Hevner 七準則

---

## 3. 資料策略

### 一手資料 (Primary)
| 資料源 | 性質 | 時間範圍 | 取得方式 |
|--------|------|----------|----------|
| 案例校園 (1–2 所) 智慧電表 | 15 min 粒度負載 | 2022–2025 暑期前後 | 與校方合作 IRB |
| 案例校園 BAS/BEMS 紀錄 | 冷氣機運轉、室內溫濕度 | 同上 | 同上 |
| 校園能管員訪談 | 半結構錄音 | 2026 春夏 | IRB 通過後 |

### 二手資料 (Secondary)
| 資料源 | 內容 |
|--------|------|
| CWA (台灣中央氣象署) | 觀測 + 短期預報 (含 WRF) |
| JMA / KMA / CMA | 日韓中對照觀測資料 |
| FengWu / FuXi (releases) | AI 氣象預報基線 |
| 台電公開資料平台 | 區域系統負載、DR 公告紀錄 |
| Yokohama Smart City 公開報告 | 22.8% 削峰實證資料 |

### 資料治理
- IRB 申請 (準免審：觀測級資料、訪談取得 informed consent)
- 學生身分資料不蒐集；負載僅彙整至樓棟層
- GDPR-equivalent 處理 (PDPA 台灣個資法)

---

## 4. 分析框架

### 4.1 預測模型層 (RQ1, RQ2)

```
Baselines (對照組)           |  Deep Learning (實驗組)
─────────────────────────────┼──────────────────────────────
Persistence (naïve)          |  LSTM (vanilla)
SARIMAX (+ exogenous T, RH)  |  Bi-LSTM
SVR (RBF kernel)             |  Attention-LSTM
XGBoost / LightGBM           |  Informer (long-seq transformer)
                             |  Temporal Fusion Transformer (TFT)
                             |  CNN-BiLSTM-Attention (Frontiers 2026)
```

**評估指標**:
- 點預測：RMSE、MAPE、nRMSE、R²
- 機率預測：CRPS、Pinball Loss、PICP/PINAW
- 預警時序：lead time、precision-recall@threshold
- 公平性：跨樓棟誤差分佈 (Gini)

**可解釋性**: SHAP (對標 Frontiers 2026 SSA-Bi-LSTM)、Attention weights 視覺化

### 4.2 預警觸發機制層 (RQ3)

三層警示設計 (對標 NERC EEA / 台電 DR Levels)：
| 層級 | 觸發條件 | 行動 |
|------|---------|------|
| **Advisory** | 預測負載 P95 接近 contracted capacity 90% | 通知 + 提供節能建議 |
| **Warning** | P95 ≥ 95% 且持續 ≥30 min | 自動上調空調設定溫度 +1°C |
| **Emergency** | P50 ≥ 100% 或氣象警特報 | 非關鍵負載卸載；通報能管員 |

**決策時序評估**:
- Lead time vs accuracy trade-off curve
- ROC for alert classification
- Override signal 強化學習迴圈 (對標 ACM e-Energy 2024)

### 4.3 質性訪談分析
- 主題分析 (Braun & Clarke 2006)
- NVivo / MAXQDA 編碼
- 三角驗證 (researcher triangulation)

---

## 5. 效度與信度準則

| 維度 | 措施 |
|------|------|
| Internal validity | 留 hold-out 測試集 (2025 暑期)；交叉驗證 walk-forward |
| External validity | 跨校驗證 (1 所主要校園 + 至少 1 所跨地區外推) |
| Construct validity | 預警閾值由能管員/台電 DR 條款共同確認 |
| Reliability | 隨機種子固定 ≥5 次；TRIPOD-AI 報告所有超參數 |
| 可重現性 | OSF 預註冊 + GitHub 程式碼公開 |

---

## 6. 預期限制 (Known Limitations)

1. 校園資料規模較工業/全網小，可能限制 transformer 表現 (引 arxiv:2501.05000)
2. 訪談以中文/英文進行，跨日韓需翻譯—回譯
3. 真實 DR 事件樣本稀疏；倚賴歷史模擬與 cross-domain transfer
4. AI 氣象預報模型 (FengWu) 之解析度 (~25 km) 對校園尺度仍粗略

---

## 7. 預註冊與報告準則

- **OSF 預註冊**: 21-item template (見 deep-research/templates)
- **PRISMA 2020**: 文獻回顧階段
- **TRIPOD-AI** + **CONSORT-AI**: 預測模型與介入評估
- **COREQ**: 質性訪談

---

## 8. 時程預估 (參考)

| 階段 | 月份 | 產出 |
|------|------|------|
| Phase 2 文獻搜尋 | M1–M2 | Annotated Bibliography (PRISMA flow) |
| Phase 3 資料整理 | M3 | 校園 + 氣象資料表 |
| Phase A ML 訓練 | M4–M6 | 模型評估報告 |
| Phase B 訪談 | M5–M7 | 編碼後質性結果 |
| Phase C 雛形與評估 | M8–M10 | DR 預警雛形 + 使用者測試 |
| 撰寫 + 投稿 | M11–M12 | Q1 期刊投稿 |

---

## 9. 候選期刊 (依範圍排序)

1. *Applied Energy* (IF 11.2) — ML + 建築能源
2. *Energy and Buildings* (IF 6.7) — 建築 + DR
3. *Sustainable Cities and Society* (IF 10.5) — 智慧校園
4. *IEEE Transactions on Smart Grid* — DR + ML
5. *Energy Policy* — 若強化政策面向
