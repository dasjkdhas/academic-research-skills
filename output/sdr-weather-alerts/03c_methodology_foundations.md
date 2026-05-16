# Wave 4 Supplement — 方法學基礎文獻 (For *Energies* Submission)
## Methodological Foundations for ML/DL Load Forecasting + Risk-Oriented SDR

**Phase**: 2 — Investigation (Wave 4)
**檢索日**: 2026-05-16
**目的**: 補強方法論文獻，不止應用案例；對標 *Energies* (MDPI Q2, IF~3.0) 投稿風格
**新增**: 27 筆；總書目 **90 筆** (63 + 27)

> *Energies* 期刊偏好「理論動機 + 嚴謹比較 + 實證驗證 + 不確定性量化」的方法論論述。本檔提供以上四個面向的基底文獻。

---

## L. 機器學習方法原始論文（Foundational Methods）

### L1. ⭐⭐ Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*. **NeurIPS 30**, 3146–3154.
- **Tier**: 1 (NeurIPS 頂會)
- **核心貢獻**: GOSS (Gradient-based One-Side Sampling) + EFB (Exclusive Feature Bundling)；訓練速度較傳統 GBDT 快 20×，精度相當
- **與本研究關聯**: **本研究主模型原始論文**；必引於 Section 3 Methodology
- 來源: https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree
- BibTeX 引用: Ke et al., 2017

### L2. ⭐⭐ Chen, T., & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. **KDD '16**, 785–794.
- **Tier**: 1 (KDD 頂會)
- **核心貢獻**: 二階泰勒展開 + sparsity-aware 算法 + weighted quantile sketch
- **與本研究關聯**: **本研究比較模型原始論文**；必引
- 來源: https://www.kdd.org/kdd2016/papers/files/rfp0697-chenAemb.pdf | https://arxiv.org/abs/1603.02754

### L3. ⭐⭐ Lundberg, S. M., & Lee, S.-I. (2017). *A Unified Approach to Interpreting Model Predictions*. **NeurIPS 30**, 4766–4777.
- **Tier**: 1 (NeurIPS 頂會 Oral)
- **核心貢獻**: Shapley value 公理化基礎 + Tree SHAP 多項式時間算法
- **與本研究關聯**: **本研究解釋性方法原始論文**；必引
- 來源: https://papers.nips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions | https://arxiv.org/abs/1705.07874

### L4. ⭐⭐ Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). *Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation*. **EMNLP 2014**.
- **Tier**: 1
- **核心貢獻**: 提出 GRU 架構 (update gate + reset gate)；序列建模計算效率優於 LSTM
- **與本研究關聯**: **本研究 GRU 模型原始論文**；必引
- 來源: https://arxiv.org/abs/1406.1078 | https://aclanthology.org/D14-1179/

### L5. ⭐⭐ Hochreiter, S., & Schmidhuber, J. (1997). *Long Short-Term Memory*. **Neural Computation**, 9(8), 1735–1780.
- **Tier**: 1 (20 世紀最高被引神經網路論文)
- **核心貢獻**: Constant Error Carousel；解決 RNN 梯度消失問題
- **與本研究關聯**: 本研究 LSTM 比較模型原始論文；必引
- 來源: https://direct.mit.edu/neco/article/9/8/1735/6109/Long-Short-Term-Memory

### L6. ⭐ Breiman, L. (2001). *Random Forests*. **Machine Learning**, 45(1), 5–32.
- **Tier**: 1
- **與本研究關聯**: 本研究 RF 比較模型原始論文；必引
- DOI: https://doi.org/10.1023/A:1010933404324

### L7. ⭐⭐ Akiba, T., Sano, S., Yanase, T., Ohta, T., & Koyama, M. (2019). *Optuna: A Next-Generation Hyperparameter Optimization Framework*. **KDD '19**.
- **Tier**: 1
- **核心貢獻**: TPE (Tree-structured Parzen Estimator) + Pruning；GP-Sampler
- **與本研究關聯**: 本研究若使用 Optuna 調參，須引此並描述 search space 與 trials
- 來源: https://arxiv.org/abs/1907.10902

### L8. ⭐ Vaswani, A., et al. (2017). *Attention Is All You Need*. **NeurIPS 30**.
- **Tier**: 1
- **與本研究關聯**: Transformer 基礎；若加入 Informer/Transformer 比較須引
- 來源: https://arxiv.org/abs/1706.03762

---

## M. 時序交叉驗證與評估方法

### M1. ⭐⭐ Bergmeir, C., & Benítez, J. M. (2012). *On the use of cross-validation for time series predictor evaluation*. **Information Sciences**, 191, 192–213.
- **Tier**: 1
- **核心貢獻**: 證明 forward-chaining CV 之 MSE 估計具一致性；普通 k-fold CV 對時序資料無效
- **與本研究關聯**: 本研究時序資料切分之**理論依據**；Section 3.4 必引
- 來源: https://www.sciencedirect.com/science/article/abs/pii/S0020025511006773

### M2. ⭐ Bergmeir, C., Hyndman, R. J., & Koo, B. (2018). *A note on the validity of cross-validation for evaluating autoregressive time series prediction*. **Computational Statistics & Data Analysis**, 120, 70–83.
- **Tier**: 1
- **核心貢獻**: 對純自回歸模型，若殘差無相關，標準 k-fold CV 可用
- **與本研究關聯**: 本研究 LightGBM 含 lag features 之 CV 設計需引
- 來源: https://robjhyndman.com/papers/cv-wp.pdf

### M3. ⭐ Cerqueira, V., Torgo, L., & Mozetič, I. (2020). *Evaluating time series forecasting models: an empirical study on performance estimation methods*. **Machine Learning**.
- **Tier**: 1
- **與本研究關聯**: 經驗比較多種時序 CV 策略
- 來源: https://arxiv.org/pdf/1905.11744

---

## N. 不平衡分類與罕見事件偵測 (Peak/Risk Detection)

### N1. ⭐⭐ Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). *SMOTE: Synthetic Minority Over-sampling Technique*. **JAIR**, 16, 321–357.
- **Tier**: 1
- **核心貢獻**: 合成少數類樣本之 k-NN 內插
- **與本研究關聯**: 本研究 High/Critical 風險窗口 (4.17% 比例) 屬不平衡分類；GRU 訓練可考量 SMOTE
- DOI: https://doi.org/10.1613/jair.953

### N2. ⭐⭐ Lin, T.-Y., Goyal, P., Girshick, R., He, K., & Dollár, P. (2017). *Focal Loss for Dense Object Detection*. **ICCV 2017**.
- **Tier**: 1
- **核心貢獻**: 焦點損失—下調 well-classified 樣本的權重，聚焦難分類樣本
- **與本研究關聯**: GRU 峰值識別 (F1=0.907) 可採 focal loss 替代 BCE 進一步提升
- 來源: https://arxiv.org/abs/1708.02002

### N3. ⭐ MDPI Symmetry (2021). *Effectiveness of Focal Loss for Minority Classification in Network Intrusion Detection Systems*. 13(1), 4.
- **Tier**: 1
- **與本研究關聯**: focal loss 在不平衡偵測任務的應用範例
- 來源: https://www.mdpi.com/2073-8994/13/1/4

### N4. (NEW) *Event Detection in Time Series: Universal Deep Learning Approach* (2024). **arxiv:2311.15654v3**.
- **Tier**: 2 (preprint, 後刊出)
- **與本研究關聯**: 時序罕見事件偵測之最新框架
- 來源: https://arxiv.org/html/2311.15654v3

### N5. (NEW) Scientific Reports (2025). *Modified resampling strategy for extreme values in imbalanced air pollution data using moving block bootstrapping with relevance weighting (MBB-RW)*.
- **Tier**: 1
- **與本研究關聯**: 極值/尾端事件之 resampling 新方法；對電力峰值有方法論啟示
- 來源: https://www.nature.com/articles/s41598-025-28416-5

---

## O. 不確定性量化與機率預測 (Probabilistic Load Forecasting)

### O1. ⭐⭐ Romano, Y., Patterson, E., & Candès, E. J. (2019). *Conformalized Quantile Regression*. **NeurIPS 32**.
- **Tier**: 1
- **核心貢獻**: 結合 conformal prediction 與分位數迴歸；提供有限樣本下的覆蓋率保證
- **與本研究關聯**: 本研究可作 extension—點預測升級為**機率預測 + 風險指數信賴區間**
- 來源: https://arxiv.org/abs/1905.03222

### O2. ⭐ Hong, T., & Fan, S. (2016). *Probabilistic electric load forecasting: A tutorial review*. **International Journal of Forecasting**, 32(3), 914–938.
- **Tier**: 1
- **核心貢獻**: 機率電力負載預測權威 tutorial
- **與本研究關聯**: 機率預測脈絡之必引
- DOI: https://doi.org/10.1016/j.ijforecast.2015.11.011

### O3. (NEW) *Short-Term Probabilistic Load Forecasting Based on Conformalized Quantile Regression*. **Energy Proceedings, ICAE 2023**.
- **Tier**: 2
- **與本研究關聯**: CQR + RF 應用於 STLF；可作為本研究 extension 路徑
- 來源: https://www.energy-proceedings.org/wp-content/uploads/icae2023/1703111755.pdf

### O4. (NEW) Preprints.org (2026). *Enhancing Short-Term Wind Energy Forecasting with XGBoost and Conformal Prediction for Robust Uncertainty Quantification*.
- **Tier**: 2
- **與本研究關聯**: XGBoost + Conformal 在能源預測之最新探索
- 來源: https://www.preprints.org/manuscript/202601.1804/v1/download

---

## P. *Energies* 期刊近期同主題 (對標投稿風格)

### P1. ⭐⭐ MDPI **Energies** 18(6), 1518 (2025-03). *Day-Ahead Net Load Forecasting for Renewable Integrated Buildings Using XGBoost*.
- **Tier**: 1 (target 期刊近期文章)
- **核心發現**: 多年校園負載 + PV 資料 (University of Hawaii Manoa)
- **與本研究關聯**: **直接對標**—校園 + XGBoost + Energies；確認投稿可行性與表達風格
- 來源: https://www.mdpi.com/1996-1073/18/6/1518

### P2. ⭐⭐ MDPI **Energies** 18(19), 5144 (2025). *Short-Term Electrical Load Forecasting Based on XGBoost Model*.
- **Tier**: 1
- **與本研究關聯**: 直接對標—小時電力 + XGBoost + 2013–2025 資料；Section 4 比較模型必引
- 來源: https://www.mdpi.com/1996-1073/18/19/5144

### P3. ⭐⭐ MDPI **Energies** 18(11), 2842 (2025-05). *Optimizing Smart Grid Load Forecasting via a Hybrid LSTM-XGBoost Framework*.
- **Tier**: 1
- **與本研究關聯**: LSTM + XGBoost 混合架構—對標本研究 GRU + LightGBM 取捨論述
- 來源: https://www.mdpi.com/1996-1073/18/11/2842

### P4. ⭐ MDPI **Energies** 18(20), 5526 (2025-10). *LightGBM Medium-Term Photovoltaic Power Prediction Integrating Meteorological Features and Historical Data*.
- **Tier**: 1
- **與本研究關聯**: **同期刊 + 同模型 (LightGBM) + 同特徵類別 (氣象 + 歷史)**；本研究行文與引用結構之 template
- 來源: https://www.mdpi.com/1996-1073/18/20/5526

### P5. ⭐ MDPI **Energies** 18(18), 4960 (2025-09). *Energy Flexibility Realization in Grid-Interactive Buildings for Demand Response: State-of-the-Art Review on Strategies, Resources, Control, and KPIs*.
- **Tier**: 1
- **核心發現**: load shifting 4–6 hr 削峰；HVAC 為 DR 首選；峰值削減 1%–65%、能耗節省至 60%
- **與本研究關聯**: 本研究 SDR 結果 (109 kW、60% 高風險時長壓縮) **在文獻範圍內** 的論述支撐
- 來源: https://www.mdpi.com/1996-1073/18/18/4960

### P6. ⭐ MDPI **Energies** 18(19), 5217 (2025). *Demand Response Potential Forecasting: A Systematic Review of Methods, Challenges, and Future Directions*.
- **Tier**: 1
- **與本研究關聯**: DR 潛力預測系統性回顧—本研究歸位之 anchor
- 來源: https://www.mdpi.com/1996-1073/18/19/5217

### P7. (NEW) MDPI **Energies** 19(3), 705 (2026). *Enhancing Short-Term Load Forecasting Using Hyperparameter-Optimized Deep Learning Approaches*.
- **Tier**: 1
- **與本研究關聯**: 本研究 LightGBM/GRU 超參優化部分對標
- 來源: https://www.mdpi.com/1996-1073/19/3/705

### P8. (NEW) MDPI **Energies** 18(5), 1048 (2025). *Collaborative Forecasting of Multiple Energy Loads in Integrated Energy Systems Based on Feature Extraction and Deep Learning*.
- **Tier**: 1
- 來源: https://www.mdpi.com/1996-1073/18/5/1048

### P9. (NEW) MDPI **Energies** 18(16), 4285 (2025). *Hybrid Forecasting for Energy Consumption in South Africa: LSTM and XGBoost Approach*.
- **Tier**: 1
- 來源: https://www.mdpi.com/1996-1073/18/16/4285

### P10. (NEW) MDPI **Energies** 18(22), 5932 (2025). *Research on Monthly Energy Consumption Intensity Prediction and Climate Correlation of Public Institutions Based on Machine Learning*.
- **Tier**: 1
- **與本研究關聯**: 公共機構月度能耗 + 氣候相關；對校園研究近親
- 來源: https://www.mdpi.com/1996-1073/18/22/5932

---

## Q. 機器學習 × 建築能源 綜述 (For Introduction & Discussion)

### Q1. ⭐ MDPI **Buildings** 15(4), 648 (2025). *Machine Learning Applications in Building Energy Systems: Review and Prospects*.
- **Tier**: 1
- **與本研究關聯**: 引言段建築能源 ML 主流方法地圖
- 來源: https://www.mdpi.com/2075-5309/15/4/648

### Q2. ⭐ MDPI **Buildings** 15(18), 3298 (2025). *Model Predictive Control for Smart Buildings: Applications and Innovations in Energy Management*.
- **Tier**: 1
- **與本研究關聯**: MPC vs ML predictive 路線對照
- 來源: https://www.mdpi.com/2075-5309/15/18/3298

---

## 投稿風格對齊筆記 (Energies-Specific Writing Notes)

### 結構特徵 (從 P1–P10 觀察)
1. **Abstract**: 5–7 句結構式 (Background → Methods → Results → Implications)；通常 200–300 字
2. **Introduction**: 3–5 段；含 (a) DR/能源管理脈絡 (b) ML/DL 既有進展 (c) 校園特殊性 (d) 本研究貢獻三點明列
3. **Methodology**: 含完整模型方程式 + 超參表 + 資料分割 + 評估指標 + 計算環境
4. **Results**: 比較表為主軸；含 ablation；風險指數設計需有公式
5. **Discussion**: 與既有研究 (引 P1–P10) 之數值比較；限制段落必備
6. **Conclusion**: 4–6 句；含 future work

### Methodological Rigor 要點
- ✅ 模型原始論文引用 (L1–L8)
- ✅ 時序 CV 引用 Bergmeir (M1)
- ✅ Hyperparameter 搜索協議（若用 Optuna 引 L7）
- ✅ 統計顯著性檢定（Diebold-Mariano、Friedman、Wilcoxon）
- ✅ Reproducibility: 隨機種子、軟體版本、計算硬體
- ⚠️ 不確定性量化（本研究若加入 O1 conformal 將顯著提升審稿評分）

### 與您現有結果的差距檢視
| 項目 | 現狀 | Energies 期待 | 行動 |
|------|------|-------------|------|
| 模型比較 | LightGBM/GRU/RF/XGBoost/LSTM 五模型 | 5+ 模型 | ✅ 已達 |
| 超參調校描述 | 待補 | Optuna/Bayesian + 搜索空間表 | 補章節 |
| 時序 CV 設計 | 待補 | walk-forward + 不重疊 | 補章節 |
| 統計檢定 | 待補 | DM 或 Friedman 檢定 | 補表 |
| 不確定性區間 | 點預測 | 區間 + 覆蓋率 | （建議補） |
| SHAP 視覺化 | 已有 | summary + dependence + force plot | 補圖 |
| 風險指數公式 | 已用 C=2000 kW | 完整 risk_score(t) 公式 | 補方程 |
| SDR 動作量化 | 109 kW、60% | 對每個 action 拆解 | 補表 |

---

## 累計總書目 (Wave 1–4)

| Wave | 主題 | 新增 | 累計 |
|------|------|------|------|
| Wave 1 | 初次廣域搜尋 | 28 | 28 |
| Wave 2 | PRISMA + 東亞補強 | 17 | 45 |
| Wave 3 | AMeDAS 日本聚焦 | 18 | 63 |
| **Wave 4** | **方法學基礎 + Energies 對標** | **27** | **90** |

### Tier 分佈
| Tier | 數量 | 比率 |
|------|------|------|
| 1 | 56 | 62% |
| 2 | 18 | 20% |
| 3 | 16 | 18% |

### 方法學文獻補齊狀況
| 方法 | 原始論文 | 應用範例 | 評估方法論 |
|------|---------|---------|-----------|
| LightGBM | ✅ L1 | ✅ P4 | ✅ K2 |
| XGBoost | ✅ L2 | ✅ P1,P2 | — |
| GRU | ✅ L4 | ✅ Energies P3 | — |
| LSTM | ✅ L5 | ✅ P3 | — |
| RF | ✅ L6 | — | — |
| SHAP | ✅ L3 | ✅ K1, K2 | — |
| 時序 CV | — | — | ✅ M1, M2, M3 |
| 超參優化 | ✅ L7 | ✅ P7 | — |
| Conformal | ✅ O1 | ✅ O3, O4 | — |
| 不平衡分類 | ✅ N1, N2 | ✅ N3, N5 | — |
