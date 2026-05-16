# INSIGHT Collection
## 校園高溫季 ML+SDR 研究 — 關鍵洞察庫

**Phase**: 3 — Synthesis
**Date**: 2026-05-16
**用途**: 論文寫作之 punch-line 倉庫；供 Introduction、Discussion、Abstract 直接取用

---

## INSIGHT 1: 「校園 ≠ 商辦」的硬約束

> 大學校園的需量管理面對的是**多建築耦合 + 強時間異質性 + 顯著管理約束**三重交織—學期制度、考試安排、假期狀態、作息規律—使其既非單體建築也非完全市場化園區，現有 ML 模型若直接遷移自商辦案例必然失準。

**支撐文獻**: Amber 2017; Jasim 2025 (Energy Nexus); Lim 2014 (Energy & Buildings)
**論文位置**: Introduction §3 (中段)

---

## INSIGHT 2: 「峰值是少數時段的故事，不是全天都熱」

> 高溫季工作日的平均日峰值比普通工作日高 21.2%，但真正的管理壓力集中於 12:00–16:00，尤其 15:00 前後—這意味著任何有效的削峰策略必須**精準瞄準少數臨界時段**，而非對全日作均勻干預。

**支撐文獻**: Spandagos & Ng (Applied Energy); 用戶實證數字
**論文位置**: Introduction §1; Results §4 (峰值時間分佈分析)

---

## INSIGHT 3: 「LightGBM 為何能贏在小時級電力預測」

> LightGBM 在小時級校園總負載預測上達 MAE 18.53 kWh、MAPE 1.89%、R²=0.9908—其優勢源自三點：(1) GOSS 對高梯度樣本的聚焦保留了氣溫尖峰時段的學習權重；(2) EFB 對 dummy 變量 (時段、星期、節假日) 的高效束打捆減少過擬合風險；(3) 樹模型對非線性與交互效應的天然適配性匹配「氣溫 × 時段 × 樓宇」之複雜耦合。

**支撐文獻**: Ke et al. 2017 NeurIPS; JJSAI 35(3) 電力需要予測コンテスト
**論文位置**: Discussion §1 (模型選擇之機制解釋)

---

## INSIGHT 4: 「GRU 在峰值識別上反超 LightGBM 的原因」

> 在峰值識別任務上 GRU 達 F1=0.907，超越 LightGBM。這非意外—峰值識別本質上是**時序事件偵測 (temporal event detection)** 而非點值回歸，GRU 的隱狀態能累積「過去 6–12 小時的氣溫上升軌跡 + 負載累積動量」這類無法被靜態特徵充分表達的訊號，且 update gate 對峰值上升期的選擇性記憶優於樹模型的固定深度。

**支撐文獻**: Cho et al. 2014 EMNLP; Lin et al. 2017 Focal Loss; arxiv:2311.15654 Event Detection
**論文位置**: Discussion §1 (Dual-head architecture rationale)

---

## INSIGHT 5: 「合同容量是被學界忽視的設計變量」

> DR 文獻多以價格信號或系統頻率為觸發，但對大學等以合同容量 (contract demand) 計費的用戶而言，**真實的財務驅動是「不超約」而非「電價套利」**。本研究以 C=2,000 kW 構建的風險指數實現了「4.17% 時段覆蓋 81.25% 真實高負荷事件」的高精度比，證明合同容量導向的風險判別是**被既有 DR 文獻忽視的高效設計範式**。

**支撐文獻**: Energies 18(19) 5217 (DR Potential Review); FERC 2025; 用戶實證
**論文位置**: Introduction §2 (gap 段); Methods §3.5 (風險指數設計); Conclusion

---

## INSIGHT 6: 「Soft DR 在校園的不可替代性」

> 工業與商辦可承受短時 Hard DR (強制中斷)，但大學校園的教學連續性、實驗設備保護、學生人身舒適三重約束使硬性中斷的隱性成本極高。**Soft DR—空調設定 +1–2 ℃、設備錯峰、樓宇差異控制—是唯一可在校園落地的範式**。本研究展示其 109 kW 削峰、60% 高風險時長壓縮的可行性，且不涉及任何強制中斷。

**支撐文獻**: Energies 18(18) 4960; ACM e-Energy 2024; azbil tems™; DAIKIN i-touchmanager
**論文位置**: Introduction §4 (校園特殊性); Discussion §3

---

## INSIGHT 7: 「持續時長壓縮 > 削峰量」的指標革新

> 多數 DR 文獻以「峰值削減量」為唯一指標，但對運維而言**「高風險狀態維持多久」**才是真實壓力—因為合同容量超約罰款依超約小時計算，而非瞬時尖峰高度。本研究提出**高風險持續時長壓縮 60%** 作為輔助指標，更貼近運維決策邏輯。

**支撐文獻**: 本研究原創觀察；類比 Energies 18(18) 4960 KPI 框架
**論文位置**: Discussion §4 (Indicator Innovation); Conclusion

---

## INSIGHT 8: 「AMeDAS 距離 — 校園微氣象之必要性」

> AMeDAS 全國 ~1,300 站、平均站距 17 km，但校園熱島效應使站點實測氣溫與校內實際工況可能存在 1–3 ℃ 差異。本研究雖以 AMeDAS 為主要外生輸入仍達 R²=0.9908，但這暗示**未來精度天花板的提升需在校內部署微氣象站**。

**支撐文獻**: JMA AMeDAS 規格; SHASE 46(293) Hybrid PHY+ML
**論文位置**: Limitations / Future Work

---

## INSIGHT 9: 「SHAP 揭示之物理一致性即方法可信度」

> 一個 ML 模型對能源工程的價值不僅在於精度數字，更在於**其特徵歸因是否符合熱力學直覺**。本研究 SHAP 預期排序為「氣溫 > 氣溫滯後 1–3h > 時段 dummy > 歷史負荷 lag > 濕度」，與既有建築熱負荷物理理解一致—這一致性本身就是模型可信度的**第三方驗證**。

**支撐文獻**: Lundberg & Lee 2017 NeurIPS; SSA-Bi-LSTM 2026; K2 改进贝叶斯+集成
**論文位置**: Results §4.3 (SHAP analysis); Discussion §2

---

## INSIGHT 10: 「方法論層面對 Energies 期刊投稿的差異化」

> 在 Energies 期刊近期 (2025) 同主題十篇文章 (P1–P10) 中，多數聚焦於**模型精度比較**或**單一動作削峰**，**少有研究將預測—風險識別—Soft DR 動作三層整合為閉環**並提供日本場域 (AMeDAS + 大學) 實證。本研究的差異化在於此一閉環設計與場域實證的雙重稀缺性。

**支撐文獻**: P1–P10 對比
**論文位置**: Introduction §5 (Contribution Statement); Cover Letter

---

## INSIGHT 11: 「公平性是被忽視的 Soft DR 倫理問題」

> 空調設定 +2 ℃ 對健康青年不構成顯著影響，但**對熱敏感族群 (孕婦、慢病學生、夜間長時實驗者) 可能造成累積熱暴露風險**。本研究 SDR 動作集應內建 opt-out 與分樓宇異質化邏輯—樓宇差異控制策略恰好為此提供天然介面。

**支撐文獻**: Nature Comms 2023 (PMC10550920) Heatwave IDR Equity
**論文位置**: Discussion §5 (Ethical Considerations)

---

## INSIGHT 12: 「機率預測為下一步研究高槓桿擴展」

> 本研究以點預測 + 三層風險指數構建運維邏輯，但 Conformalized Quantile Regression (Romano 2019) 可在不修改主模型架構的前提下，將點預測升級為**有覆蓋率保證的區間預測**，使風險指數轉化為「以 95% 置信區間覆蓋的風險概率」—這是論文 Future Work 段最高 ROI 的延伸方向。

**支撐文獻**: Romano et al. 2019 NeurIPS; Hong & Fan 2016 (Int J Forecasting Tutorial)
**論文位置**: Future Work / Conclusion

---

## 12 個 INSIGHT 的論文配置建議

| INSIGHT | Abstract | Intro §1 | Intro §2 | Intro §3 | Intro §4 | Intro §5 | Methods | Results | Disc §1 | Disc §2 | Disc §3 | Disc §4 | Disc §5 | Future | Conclusion |
|---------|----------|----------|----------|----------|----------|----------|---------|---------|---------|---------|---------|---------|---------|--------|-----------|
| 1 校園≠商辦 | | | | ⭐ | | | | | | | | | | | |
| 2 峰值窄窗 | ⭐ | ⭐ | | | | | | ⭐ | | | | | | | |
| 3 LightGBM 機制 | | | | | | | | | ⭐ | | | | | | |
| 4 GRU 機制 | | | | | | | | | ⭐ | | | | | | |
| 5 合同容量 | ⭐ | | ⭐ | | | ⭐ | ⭐ | | | | | | | | ⭐ |
| 6 Soft DR 校園必要 | | | | | ⭐ | | | | | | ⭐ | | | | |
| 7 持續時長指標 | ⭐ | | | | | | | ⭐ | | | | ⭐ | | | ⭐ |
| 8 AMeDAS 距離 | | | | | | | | | | | | | | ⭐ | |
| 9 SHAP 物理一致 | | | | | | | | ⭐ | | ⭐ | | | | | |
| 10 期刊差異化 | | | | | | ⭐ | | | | | | | | | |
| 11 公平性 | | | | | | | | | | | | | ⭐ | | |
| 12 機率預測 | | | | | | | | | | | | | | ⭐ | |
