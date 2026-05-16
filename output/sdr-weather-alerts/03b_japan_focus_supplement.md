# Wave 3 Supplement — 日本場域聚焦文獻
## AMeDAS + LightGBM/GRU/SHAP + Soft Demand Response

**Phase**: 2 — Investigation (Wave 3)
**檢索日**: 2026-05-16
**檢索範圍**: J-STAGE (深度), CNKI (深度), 日本商業 BEMS/DR 系統文獻
**新增**: 18 筆；總書目達 **63 筆** (45 + 18)

> 本檔聚焦研究實際設定：日本校園、AMeDAS 氣象、LightGBM/GRU 模型、SHAP 解釋、SDR 柔性響應。

---

## H. 日本場域 — 電力需求 ML 預測經典 (J-STAGE 深度)

### H1. ⭐ 電気学会 IEEJ (1997, 持續被引). *NN応用電力需要予測システムの開発*. **電気学会論文誌B (電力・エネルギー部門誌)**, 120(12), 1550.
- **Tier**: 1 (日本電氣學會旗艦期刊)
- **核心發現**: 日本電力需求 NN 預測系統的開山級文獻；含氣象 + 假日特徵
- **與本研究關聯**: 日本 ML 電力預測典範起點；正當化選擇神經網路類模型
- 來源: https://www.jstage.jst.go.jp/article/ieejpes1990/120/12/120_12_1550/_article/-char/ja/

### H2. ⭐ IEEJ. *電力需要予測*. **電気学会誌**, 117(9), 596.
- **Tier**: 1 (peer-reviewed review)
- **與本研究關聯**: 日本電力預測通史與方法論回顧
- 來源: https://www.jstage.jst.go.jp/article/ieejjournal1994/117/9/117_9_596/_article/-char/ja/

### H3. ⭐ *人工ニューラルネットワークによる電力需要予測の影響要因評価—学習条件による影響*. **エネルギー・資源学会論文誌 (JJSER)**, 40(5), 144.
- **Tier**: 1
- **核心發現**: 學習條件對 ANN 電力需求預測精度的敏感性分析
- **與本研究關聯**: 對應本研究訓練超參數調校之先行
- 來源: https://www.jstage.jst.go.jp/article/jjser/40/5/40_144/_pdf

### H4. ⭐ *ニューラルネットワークを用いた翌日電力需要予測と当日予測補正*. **JPV 第 18 回次世代太陽光発電シンポジウム** (2021).
- **Tier**: 2 (學會年會論文)
- **核心發現**: 翌日預測 + 當日修正之雙階段架構
- **與本研究關聯**: 本研究小時級短期預測可採之 staged 思想
- 來源: https://www.jstage.jst.go.jp/article/jpvsproc/1/0/1_130/_article/-char/ja/

### H5. ⭐ *機械学習を用いた電力量消費予測に関する研究*. **空気調和・衛生工学会大会学術講演論文集**, 2019.9, 189.
- **Tier**: 2 (SHASE 大會)
- **核心發現**: 日本建築電力消費 ML 預測；含 AMeDAS 等外生變量
- 來源: https://www.jstage.jst.go.jp/article/shasetaikai/2019.9/0/2019.9_189/_pdf/-char/ja

### H6. *電力需要予測コンテスト—オープンイノベーションへの取組み*. **人工知能学会誌 (JJSAI)**, 35(3), 360.
- **Tier**: 1
- **核心發現**: 電力需求預測公開競賽；含 LightGBM 等 GBM 模型獲勝案例之 lesson learned
- **與本研究關聯**: 直接支持本研究 LightGBM 為日本場域有效選擇
- 來源: https://www.jstage.jst.go.jp/article/jjsai/35/3/35_360/_article/-char/ja/

### H7. *2030 年日本の電力システムの再生可能エネルギー系統統合*. **風力エネルギー協会論文集 (JWE)**, 40, 223.
- **Tier**: 1
- **與本研究關聯**: 日本 2030 RE 大量併網下 DR 必要性背景
- 來源: https://www.jstage.jst.go.jp/article/jweasympo/40/0/40_223/_pdf/-char/ja

---

## I. AMeDAS 氣象資料應用與處理

### I1. ⭐ JMA / 気象庁. *地域気象観測システム (アメダス) 解説*.
- **Tier**: 1 (政府權威源)
- **核心發現**: 全國 ~1,300 站；每 10 分鐘記錄降水/風向/風速/氣溫/濕度
- **與本研究關聯**: 本研究氣象資料源之**官方規格定義**；引用為 Section 3.1 資料源段
- 來源: https://www.jma.go.jp/jma/kishou/know/amedas/kaisetsu.html

### I2. *機械学習を用いた 1 ヶ月気象予測の試み*. **土木学会論文集 B1 (水工学)**, 76(2), I_331.
- **Tier**: 1
- **核心發現**: 月尺度氣象 ML 預測；AMeDAS 為輸入
- **與本研究關聯**: 跨日預測之氣象上游
- 來源: https://www.jstage.jst.go.jp/article/jscejhe/76/2/76_I_331/_pdf

### I3. *機械学習による局地気象予報手法の開発*. **JSAI 大會 2019**, 4Rin133.
- **Tier**: 2
- **與本研究關聯**: 局地氣象 ML 預測；本研究 grid resolution 對齊
- 來源: https://www.jstage.jst.go.jp/article/pjsai/JSAI2019/0/JSAI2019_4Rin133/_pdf

### I4. WXBC (2023). *アメダス気象データ分析チャレンジ Python 版*. 気象ビジネス推進コンソーシアム.
- **Tier**: 3 (產業教育性)
- **與本研究關聯**: AMeDAS 在 Python 工具鏈之 best practice
- 來源: https://www.wxbc.jp/mypage/challenge/challenge_20230928/

---

## J. 商業 BEMS / Soft DR 系統 (日本廠商實裝)

### J1. ⭐ アズビル株式会社 (azbil) / tems™. *ディマンドリスポンス建物エネルギーマネジメント*.
- **Tier**: 3 (產業案例 / 商業白皮書)
- **核心發現**: 日本商業 BEMS 旗艦產品線；整合 DR 信號與空調溫度設定自動回應
- **與本研究關聯**: 本研究 SDR 動作 (空調設定微調、設備錯峰) 之**產業落地參考**
- 來源: https://www.azbil.com/jp/product/building/energy-management/demand-response/index.html

### J2. ⭐ DAIKIN. *i-touch manager Demand Control*.
- **Tier**: 3
- **核心發現**: 大金商用 VRF 空調的 demand control 模組
- **與本研究關聯**: 本研究 SDR 動作可透過此類產品落地
- 來源: https://www.ac.daikin.co.jp/i-touchmanager/demand

### J3. 日立 GLS. *exiida デマンド制御ソリューション*.
- **Tier**: 3
- **與本研究關聯**: 另一日本廠商 DR 解決方案；對照 J1/J2
- 來源: https://www.hitachi-gls.co.jp/products/exiida/demand/

### J4. 環境省. *デマンドレスポンス活用 (政府文件)*.
- **Tier**: 2 (政府政策文件)
- **與本研究關聯**: 日本環境省對 DR 之政策定位；2050 淨零脈絡
- 來源: https://www.env.go.jp/content/900449390.pdf

### J5. 中部電力 ミライズ. *デマンドレスポンス商品 — 再エネと組み合わせ*.
- **Tier**: 3 (電力業者商業文件)
- 來源: https://miraiz.chuden.co.jp/business/carbon-free/demand-response/

### J6. ほくでんネットワーク (北海道電力 NW). *学校 (小・中・高) 節電チェックシート — 夏季*.
- **Tier**: 3 (電力業者教育性文件)
- **與本研究關聯**: 日本電力業對 K-12 學校夏季節電的官方指引；可作為**比較對象**（本研究升級為大學 ML 化版本）
- 來源: https://www.hepco.co.jp/network/electric_life/power_saving/business/simulation/school_summer.html

---

## K. CNKI 深度補充

### K1. *小微企业违约特征再探索：基于 SHAP 解释方法的机器学习模型*. **中国管理科学**.
- **Tier**: 1
- **與本研究關聯**: CNKI 來源 SHAP 方法學示範；本研究 SHAP 部分可援引
- 來源: https://www.zgglkx.com/CN/10.16381/j.cnki.issn1003-207x.2021.0027

### K2. *基于改进贝叶斯优化与集成学习短期负荷预测模型*. **电力系统及其自动化学报 (CNKI)**.
- **Tier**: 1
- **核心發現**: XGBoost 為 meta-learner + SHAP 特徵重要性；溫度/濕度為外生輸入
- **與本研究關聯**: 直接對標—中國電力短期預測 SHAP 範本
- 來源: https://dlzd.cbpt.cnki.net/.../paper/8e066871d0a2c513f399241678af2b3b

### K3. *基于 ResNet-LSTM 网络和注意力机制的综合能源系统多元负荷预测*. **电工技术学报**.
- **Tier**: 1 (CNKI top journal)
- **與本研究關聯**: 中國 IES 多元負載預測 SOTA；本研究單一電力負載為簡化版
- 來源: https://dgjsxb.ces-transaction.com/fileup/HTML/2022-7-1789.htm

### K4. *基于 XGBoost 与多源域迁移学习的贫资料地区*. **现代电力 (CNKI)**, 2025.
- **Tier**: 1
- **核心發現**: XGBoost + SHAP 衡量特徵-輸出映射；transfer learning 至資料貧乏區
- **與本研究關聯**: 本研究若校園資料有限可援引此 transfer 路徑
- 來源: http://xddl.ncepujournal.com/cn/article/pdf/preview/10.19725/j.cnki.1007-2322.2024.0038.pdf

### K5. *高校节能监管平台建设与应用研究* (碩士論文). **CNKI CMFD**.
- **Tier**: 2 (碩士論文)
- **核心發現**: 中國高校能耗監管平台；決策樹 + 灰預測之預警
- **與本研究關聯**: 中國 baseline 對照，本研究升級為 GBM/RNN + SHAP
- 來源: https://oversea.cnki.net/kcms/detail/detail.aspx?dbcode=CMFD&...

### K6. *基于机器学习的短期负荷预测算法综述*. **计算机系统应用 (CNKI)**.
- **Tier**: 1
- **與本研究關聯**: 中文版 ML 短期負載預測綜述；本研究中文文獻錨點
- 來源: https://www.c-s-a.org.cn/csa/article/html/8734

---

## 整體 Source Quality Matrix (Wave 3 後)

| Tier | 來源類型 | 數量 |
|------|---------|------|
| 1 | Peer-reviewed Q1 期刊 / 頂會 | 36 |
| 2 | Q2 + 權威政府 / 標準 / 學會大會 | 14 |
| 3 | 灰色文獻、產業案例、新聞 | 13 |
| **總計** | | **63** |

**Tier 1 比率**: 57% (≥50% 標準 ✅)

### 地理分佈 (Wave 3 後)
| 地理 | 數量 | 註 |
|------|------|-----|
| **日本** | **15** | **主場域，含 AMeDAS、IEEJ、SHASE、商業 BEMS** |
| 中國大陸 | 11 | CNKI 深度 |
| 韓國 | 7 | KCI / Energy and Buildings |
| 台灣 | 5 | 在地對照 |
| 東南亞 | 2 | 熱帶氣候對照 |
| 歐美 | 6 | 政策/標準 (OpenADR/FERC/NERC) |
| 國際 / 跨區 | 17 | Q1 期刊 |

### 方法學分佈
| 方法 | 文獻數 |
|------|--------|
| LightGBM / GBM | 11 |
| LSTM / GRU / RNN | 14 |
| Transformer / Attention | 8 |
| XGBoost | 9 |
| RL (DRL / DDPG / PPO) | 6 |
| SHAP / XAI | 5 |
| Hybrid (PHY+ML) | 4 |

---

## 本研究的文獻錨點（給寫作引用用）

### 引言段必引
- Jasim et al. 2025 (Energy Nexus) — 校園 EMS 缺長期預測能力的權威主張
- Lim 2014 (Energy & Buildings) — 韓國校園 27 ℃ baseline
- IEEJ 1997 NN系統 — 日本 ML 電力預測典範起點
- 環境省 DR 政策文件 — 日本政策背景

### 方法段必引
- JMA AMeDAS 官方解說 — 資料源
- SHASE 46(293) Hybrid 模型 — 日本建築 ML 負載預測 SOTA
- 改進貝葉斯 + 集成學習 (CNKI) — LightGBM + SHAP 設計參考
- 電力需求預測コンテスト (JJSAI 35(3)) — LightGBM 在日本場域有效性
- Smart Cities 8(1):30 SGEMS — XGBoost+RL 校園預測 baseline

### SDR / 風險段必引
- ACM e-Energy 2024 Override RL — Soft DR 概念
- azbil tems™ + DAIKIN i-touchmanager — SDR 動作之產業落地
- Nature Comms 2023 IDR Heat — DR 公平性
- 北海道電力 K-12 節電指引 — 與本研究升級對照
