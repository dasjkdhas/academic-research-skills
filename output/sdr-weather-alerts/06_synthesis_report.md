# Synthesis Report
## 大學校園高溫季電力負荷預測與風險導向 SDR 研究

**Phase**: 3 — Synthesis
**Date**: 2026-05-16
**Target**: *Energies* (MDPI, Q2, IF ~3.0)
**輸入**: 90 篇文獻 + 用戶實證結果 (LightGBM MAE 18.53, GRU F1=0.907, 組合 SDR 削峰 109 kW)

---

## 1. 領域地形 (Landscape)

### 1.1 三大研究軸線之收斂

文獻顯示三條獨立軸線正在 2020 年後收斂：

```
   ML/DL 負載預測          需量反應 (DR)            校園能源管理
   ────────────────       ──────────────           ───────────────
   Ke 2017 LightGBM       Albadi 2008 DR review     Lim 2014 KR campus
   Chen 2016 XGBoost      ACM e-Energy 2024 RL+DR   Jasim 2025 review
   Cho 2014 GRU           OpenADR 2.0               UH Manoa 2025 (Energies)
   Lundberg 2017 SHAP     FERC 2025 DR Assessment   SGEMS Smart Cities 2025
            ↓                       ↓                       ↓
            └────────── 三角交集（research gap）───────────┘
                                    │
                          ⭐ 本研究定位於此
```

### 1.2 文獻熱度分佈 (Wave 1–4, 90 篇)
- **2024–2026 占 41%** (37 篇)：表明此為**活躍前沿**
- **Energies 期刊近期占 10 篇**：投稿可行性確認
- **日本場域占 17%** (15 篇)：與用戶實證設定貼合

---

## 2. 既有研究的五項共識 (Established Consensus)

| # | 共識 | 證據 | 對本研究意涵 |
|---|------|------|------------|
| C1 | LightGBM/XGBoost 在小時級負載預測上**通常優於**單一 DL 模型，特別在資料量 < 10K 樣本時 | JJSAI 35(3) 競賽; arxiv:2501.05000; P1, P2, P4 | 本研究 LightGBM 最優 (MAPE 1.89%) **符合**且強化此共識 |
| C2 | **冷氣負載與外氣溫之非線性、時延、湿度交互**為主導特徵 | C2 SSA-Bi-LSTM SHAP; SHASE 46(293); K2 改进贝叶斯+集成 | 本研究 SHAP 應再現此一發現，作為「方法可信」之 sanity check |
| C3 | **時序 CV 必須使用 walk-forward**，標準 k-fold 對自回歸 ML 模型偏樂觀 | Bergmeir 2012, 2018; Cerqueira 2020 | 本研究須於 Section 3 明確說明 CV 設計 |
| C4 | **HVAC 設定溫度微調 (+1–2 ℃)** 為 DR 中最低擾動高效益手段，可削峰 10–30% | Energies 18(18) 4960; azbil tems™; DAIKIN i-touchmanager | 本研究 SDR (109 kW 約 5.5% 削峰於 2,000 kW) **保守且可信** |
| C5 | **高溫導致峰值集中於 14:00–16:00 之窄窗口**，非全日均勻提升 | Equivalent FLH Asian cities (Spandagos & Ng); Lim 2014 | 本研究「12:00–16:00 風險窗口、15:00 前後最高」**與文獻一致** |

---

## 3. 文獻矛盾與本研究立場 (Contradictions & Positioning)

### 矛盾 1: Transformer vs GBM/RNN 之孰優

- **支持 Transformer**: Park 2023 NRF Transformer 三維最佳；Energies P3 LSTM-XGBoost 混合
- **反對 Transformer (小資料情境)**: arxiv:2501.05000 (DL 是否值得？)；JJSAI 35(3) GBM 競賽奪冠
- **本研究立場**: 在**小時級、單校園**情境下，LightGBM 為**正當選擇**；若資料擴大至跨校 + 多年，Transformer 才顯優勢。**此一立場可在 Discussion 段以「資料規模 - 模型複雜度權衡」框架呈現。**

### 矛盾 2: Hard DR vs Soft DR

- **支持 Hard DR**: 工業計減型 (FERC 2025)、台電強制中斷
- **支持 Soft DR**: ACM e-Energy 2024 (允許用戶 override + RL 學習)；本研究設計
- **本研究立場**: 校園情境**不容許 Hard DR** (教學/實驗中斷成本極高)；Soft DR 是**唯一可落地**選項。此一論述可在 Introduction 與 Discussion 拉開差異。

### 矛盾 3: 預警閾值之絕對 vs 相對

- **絕對閾值**: NERC EEA 三級警報；CAISO Flex Alert 度數
- **相對 / 容量導向**: Energies 18(19) DR Potential Review; ACM e-Energy 2024 分位數
- **本研究立場**: 採**合同容量 C=2,000 kW 之風險指數**—屬相對 / 容量導向，理由：(a) 校園峰值絕對值因季節變化大；(b) 容量超約罰款是真實財務驅動；(c) 與 contract demand management 文獻相通。

---

## 4. 研究缺口 (Research Gaps) — 本研究填補之處

| Gap | 既有研究現況 | 本研究填補 |
|-----|------------|-----------|
| **G1: 校園高溫季 ML × 風險識別 × Soft DR 閉環** | 三個元素獨立研究多，**整合到單一閉環極少** | 本研究提供完整 pipeline |
| **G2: 合同容量導向風險指數** | DR 文獻多以價格信號或系統頻率為觸發 | 本研究以 **C = 2,000 kW + 分層 (High/Critical)** 為設計變量 |
| **G3: 日本大學 + AMeDAS + LightGBM/GRU 組合** | J-STAGE 有 HVAC + ML 案例 (SHASE 46(293)); 但**校園 + AMeDAS + GBM + SHAP** 組合稀缺 | 本研究提供日本校園實證 |
| **G4: Soft DR 動作量化效益拆解** | 多數研究只報告**總削峰量**，不拆解各動作貢獻 | 本研究分解空調微調 / 設備錯峰 / 樓宇差異三類動作 |
| **G5: 風險時長壓縮指標** | 文獻多用「峰值削減量」為單一指標 | 本研究新增 **「高風險持續時長壓縮 60%」**—更貼近運維決策 |

---

## 5. 研究貢獻聲明 (For Introduction & Conclusion)

### Three-fold contribution

1. **方法層面**: 提出整合 GBM + RNN + SHAP 的**雙頭預測架構**—LightGBM 負責總體負載精度，GRU 負責峰值風險識別，二者透過共享特徵空間互補。在大學校園小時級資料上驗證此架構之有效性 (MAE 18.53 kWh、F1=0.907)。

2. **設計層面**: 提出**合同容量導向風險指數** (Risk Index based on C=2,000 kW)，將點預測轉化為三層風險判別 (Normal / High / Critical)，使僅 4.17% 高風險時段即可覆蓋 81.25% 真實高負荷事件—**為運維提供高精度低成本的注意力分配機制**。

3. **應用層面**: 提出**風險導向 Soft DR 動作集** (空調設定微調 + 設備錯峰 + 樓宇差異控制)，量化各動作貢獻；組合策略可達削峰 109 kW、高風險持續時長壓縮 60%。此為高校在**不影響教學科研前提下**之可落地解。

---

## 6. 對 Introduction 五段式骨架的建議

| 段 | 主題 | 必引文獻 (Wave 1–4) |
|----|------|-------------------|
| §1 | 氣候變暖 → 校園冷氣峰值問題 | Spandagos & Ng (Applied Energy); Lim 2014; PMC10550920 Nature Comms |
| §2 | DR 之既有手段與限制 | Albadi 2008; FERC 2025; Energies P5 P6; 環境省政策 |
| §3 | ML/DL 負載預測之既有進展 | Ke 2017; Chen 2016; Cho 2014; Energies P1 P2 P3 P4 |
| §4 | 校園特殊性與既有研究缺口 | Jasim 2025; UH Manoa P1; SGEMS Smart Cities; Lim 2014 |
| §5 | 本研究貢獻三點 | (上方第 5 節三點) |

---

## 7. 對 Discussion 段的關鍵論點預備

### 論點 7.1: 模型選擇的「資料規模—複雜度」權衡
- 本研究 LightGBM 勝出 → 與 JJSAI 35(3) 競賽、arxiv:2501.05000 觀察一致
- Discussion 引: P1 (XGBoost on UH Manoa)、P3 (LSTM-XGBoost 混合)
- 留白: 未來若擴展至多校年度資料，Transformer 可能反超

### 論點 7.2: SHAP 揭示之特徵重要性與物理直覺一致
- 預期排序: 氣溫 (現值) > 氣溫滯後 1–3h > 時段 dummy > 歷史負荷 lag > 濕度 > 風速
- 與 SSA-Bi-LSTM 2026、K2 改进贝叶斯一致 → 強化方法可信

### 論點 7.3: 風險指數 4.17% / 81.25% 之高精度比
- 對標: Energies 18(19) 5217 DR Potential Forecasting Review 提出之 KPI 範式
- 解讀: 本指數實現了「**少量高精度注意力**」—運維只需處理 4.17% 時段即可預防 81.25% 風險

### 論點 7.4: Soft DR 109 kW (5.5%) 削峰之合理性
- 對標: Energies 18(18) 4960 報告載荷彈性峰削 1%–65%、能耗節省至 60%
- 5.5% 落在保守端，但**不犧牲舒適**為本研究設計前提
- 60% 持續時長壓縮**才是真實業務價值**

### 論點 7.5: 局限與 future work
- 單校單年度 → 跨校驗證
- AMeDAS 站距離校園可能 > 1 km → 校園微氣象站之未來必要
- 點預測 → 機率預測 + Conformal Prediction (Romano 2019, O1)
- 線下分析 → 線上部署 (含 OpenADR 通訊層)
- Hard DR 整合 (儲能、V2G)

---

## 8. 結構性風險揭露 (Risks to Surface)

| 風險類型 | 風險 | 緩解 |
|---------|------|------|
| 內部效度 | LightGBM 過擬合於某季 | walk-forward CV + 留出測試 + 跨季驗證 |
| 外部效度 | 單校樣本，難推廣 | 在 Limitations 明示；提供 transfer learning 路徑 (K4) |
| 構念效度 | 風險指數設計依賴 C=2,000 kW，C 變動則指數失效 | sensitivity analysis 對 C 敏感度 |
| 結論效度 | F1=0.907 與 81.25% 風險覆蓋率屬同一統計信號 | 報告 PR-AUC、Recall@P、混淆矩陣補強 |
| 倫理 / 公平 | Soft DR 空調微調可能對熱敏感族群 (孕婦、慢病) 不公平 | 引 PMC10550920 並設計 opt-out 機制 |

---

## 9. 投稿準備檢核 (For Energies)

| 項 | 狀態 |
|----|------|
| 模型原始論文引用 (L1–L7) | ✅ 文獻已蒐集 |
| 時序 CV 方法論 (M1) | ✅ |
| 不平衡分類論述 (N1, N2) | ✅ |
| Energies 期刊近期類似主題 (P1–P10) | ✅ |
| 統計檢定設計 (DM/Friedman) | ⚠️ 須補章節 |
| 不確定性量化 (O1 conformal) | ⚠️ 建議補 (extension) |
| 倫理與公平性段落 | ⚠️ 須補 |
| Reproducibility 聲明 | ⚠️ 須補 (種子、套件版本) |
| GitHub repo / code availability | ⚠️ 須準備 |
