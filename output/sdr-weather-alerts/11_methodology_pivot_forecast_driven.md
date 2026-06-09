# 方法論大調整 — 由「歷史分析」轉為「氣象預報驅動之隔日 SDR 預警系統」

**Pivot Date**: 2026-05-16
**Confirmed Contract Capacity**: 2,000 kW（資料驗證：Max 1786 kW = 89.3%）

---

## 🎯 核心情境重新定義

### 舊框架 (歷史分析導向)
```
今天的負荷 ← 今天的觀測氣象 ← 我們事後分析它
```

### 新框架 (預報驅動隔日預警) ⭐
```
今天 17:00 (JMA 預報發布)
   ↓
讀取 JMA 隔日氣象預報 (T+0 ~ T+39 小時)
   ↓
模型預測「明天」每小時負荷
   ↓
計算「明天」每小時 CCRI 風險指數
   ↓
如果有任何小時 CCRI ≥ High → 發布隔日 SDR 呼籲
   ↓
今晚通知各樓宇管理員：明天 14:00-17:00 高風險，請：
   ・冷氣設定點 +2°C
   ・推遲非必要實驗
   ・限制電梯使用
   ↓
明天執行 SDR → 削峰 → 避免 FRR 觸發 + 避免罰款
```

---

## ☀ 日本氣象預報資料源（JMA 官方產品）

### 主要候選資料

| JMA 產品 | 發布頻率 | 預報範圍 | 變數 | 適用性 |
|---------|---------|---------|------|--------|
| **MSM** (Meso-Scale Model 局地数値予報) | 3 hr | 39 hr | T, RH, P, 風, 降水, 雲量, 短波輻射 | ⭐ 最佳 |
| **GSM** (Global Spectral Model) | 6 hr | 264 hr | 同上但較粗 | 長期 |
| **暑さ指数 WBGT 予報** | 1 日 2 次 | 3 日 | WBGT 預測 | ⭐ 直接對應 |
| **高温注意情報** | 即時 | 隔日 | 是否發布警報 | ⭐ 直接觸發訊號 |
| **天気予報** (一般天氣預報) | 1 日 3 次 | 7 日 | 天氣文字 + 概要 | 輔助 |
| **アメダス予報** | 1 hr | 24 hr | 每個 AMeDAS 站點 | 在地校準 |

### 我們可用的程式化介面

1. **Open-Meteo Forecast API** (推薦)
   - 內部使用 JMA MSM/GSM 模型
   - 提供小時級預報，含短波輻射、體感溫度、WBGT 等衍生量
   - 開放免費
   - 同一個 API 也支援取得「歷史的『當天預報』」用於模型訓練 ⭐⭐⭐

2. **JMA 官方 XML/JSON Feed**
   - https://www.jma.go.jp/bosai/forecast/data/forecast/
   - 純文字預報 + 機械可讀格式
   - 結合 https://www.jma.go.jp/bosai/wbgt/ (WBGT 預測)

3. **氣象庁 過去の予報** (歷史預報重建)
   - 困難：JMA 不開放歷史 raw forecast；要靠 GPV 開發者 API（如 Pythie、grib2）
   - **替代**：用 ERA5 reanalysis 作為「完美預報」上界估計

---

## 🏗️ 方法論結構大調整

### Section 1: 系統定位 (Repositioned)

**舊**：「Campus FRR-Loop 後驗分析」
**新**：「Forecast-Driven Day-Ahead SDR Advisory System for Campus FRR」

### Section 3 (Methodology) 重整

#### 3.1 資料 (Data)
- 校園負荷：保持
- **氣象資料 (重大調整)**：
  - 訓練用：**JMA reanalysis (相當於完美觀測)** + 同期間的**「當天 JMA 預報」**
  - 推論用：**JMA 隔日預報** (真實使用情境)
- 校歷：保持

#### 3.2 兩個關鍵特徵集 (NEW)
這是新方法論最重要的概念差異：

| 特徵集 | 用途 | 來源 |
|--------|------|------|
| **F_obs** (觀測特徵) | 模型訓練的 "ground truth" | ERA5 / AMeDAS 觀測 |
| **F_fcst** (預報特徵) | **線上推論 + 訓練評估** | JMA MSM 預報（過往的 day-ahead 預報） |

**論文創新點 (NEW Innovation 8)**: 「**Forecast-Aware Training**」
- 不只用觀測訓練、再期望它在預報下表現
- 而是**直接在訓練時就模擬預報誤差**：將觀測加 noise（依 JMA MSM 已知誤差統計）後訓練
- 或更乾淨：用 JMA reforecast（歷史預報）資料直接訓練

#### 3.3 預報誤差校準 (NEW)
JMA MSM 已知的預報誤差 (1-day ahead):
- 氣溫：MAE ≈ 1.2-1.5 °C
- 短波輻射：MAE ≈ 80-120 W/m² (cloud cover 是主誤差源)
- 相對濕度：MAE ≈ 6-8 %
- 降水：F1 ≈ 0.6-0.7 (binary rain/no-rain)

模型訓練時可注入這些誤差統計 → 評估更貼近真實線上表現。

#### 3.4 雙時間軸的模型 (Time-Aware Model Architecture)

```
                  Forecast Issue Time T
                          |
   ┌──────── Past (Observed) ──────┐ ┌──── Future (Forecast) ────┐
   |                                |  |                          |
   t-168h  ...   t-24h ... t-1h    [T]  T+1 ... T+24h ... T+48h
   └─── b00, weather observed ────┘ └──── weather forecast ─────┘
              用於特徵生成              用於預測 y(T+1)..y(T+24)
```

模型輸入分兩段：
- **歷史段**：b00 lags、過去 7 天的負荷模式、過去觀測氣象
- **預報段**：未來 24h 的 JMA 預報氣象、未來 24h 的校歷標籤

模型輸出：未來 24h 每小時的 b00 預測 + 峰值機率 + CCRI

---

### Section 4 (Results) 新章節結構

| 4.1 | 隔日預測精度 (MAE/MAPE/R² for next-24h) |
| 4.2 | 不同預報前置時間的精度衰減 (1h → 24h → 48h ahead) |
| 4.3 | CCRI 隔日預警準確率 (Precision/Recall/Lead-time) |
| 4.4 | 對標 JMA 高温注意情報 (是否一致) ⭐ |
| 4.5 | SDR 動作效益 (Tier 1 分解, 同前) |
| 4.6 | SHAP 解釋（預報特徵 vs 觀測特徵的重要性對比） |
| 4.7 | 模擬部署 - 假設某日 17:00 接收預報 → 觸發 SDR 全流程示意 |

---

## 🔑 與 JMA 既有預警產品的關係

JMA 已經發布以下預警產品，本系統的價值定位需明確：

| JMA 既有 | 本系統 | 差異 |
|---------|--------|------|
| **高温注意情報** | CCRI Critical 預警 | JMA 看人體健康；本系統看校園電力負荷風險 |
| **WBGT 暑さ予報** | 整合進 CCRI 計算 | JMA 是單變量；本系統整合多變量 + 模型預測 |
| **電力需給 ひっ迫警報** (経済産業省) | 校園級替代 | 経産省看全國級；本系統看單一校園級 |

**論文定位**：「Bridging the gap between national-scale grid warnings and building-scale demand response — a forecast-driven decision support system」

---

## ⚙ 即時可執行的下一步

### 立即做 (60 min)：取得歷史 JMA 預報資料 + 重訓
我會做：
1. 用 Open-Meteo Forecast API 的 `archive-api` 模式（內含 ECMWF/JMA 預報歷史回放）
   - 取 2025-07-06 → 2025-10-31 每天 17:00 JST 對「隔天」的預報
2. 將「預報」與「觀測」並列存檔，計算預報誤差
3. **重訓 LightGBM**：輸入特徵全部換成「24 小時前的預報」
4. 預期：R² 從 0.881 降至 0.80-0.85 範圍（仍可用）
5. 重算 CCRI 隔日預警的 Precision/Recall

### 短期 (本週)：對標 JMA 高温注意情報
- 取 2025 年夏季山口縣高温注意情報發布紀錄
- 看本系統的 CCRI Critical 預警與 JMA 是否同步
- 寫進論文 §4.4

### 中期 (上傳更多資料後)：完整 day-ahead 系統 prototype
- 部署一個小程式：每天 17:00 拉 JMA 預報、產生報告、模擬 SDR 觸發決策

---

## 📊 預期論文升級

| 維度 | 舊方法 | 新方法 |
|------|--------|--------|
| 學術定位 | 後驗負荷分析 | **隔日決策支援系統** |
| 工程價值 | 中（量化過去） | **高**（指導未來行動） |
| 創新點 | 5 個 (1-5) | **7 個** (新增 §4.2/§4.4 預報感知 + JMA 對標) |
| 期刊適配 | *Energies* Q2 | **可投** *Applied Energy* Q1 / *Energy & Buildings* Q1 / *IEEE TSG* |
| Reviewer 質疑 | 「事後諸葛亮意義有限」 | 「實際可部署的系統」 |
| 與 JMA 既有預警的關係 | 無對標 | **明確 bridging value** |

---

## 🚨 風險與限制 (誠實)

1. **Open-Meteo 雖然使用 JMA 模型輸出，但介面有 1-2 天延遲**：實際線上部署仍需直接從 JMA 拉資料 → 工程實作議題
2. **JMA 歷史 reforecast 不開放**：精確的「該日 17:00 對隔日的預報」很難取得；目前只能用 ECMWF/Open-Meteo 替代並聲明
3. **預報精度地理變異**：宇部相對於山口市區，預報精度可能略低 (內陸 vs 海岸效應)
4. **SDR 動作執行延遲**：通知到動作生效有時間差，論文需討論

---

## ✅ 是否啟動

請確認以下三點，我就立即開始重訓：

1. ☐ 鎖定 **2,000 kW** 為合約電力（與資料 89.3% 利用率吻合）
2. ☐ 同意採用 **Forecast-Driven Day-Ahead** 為新主軸
3. ☐ 同意先用 **Open-Meteo Forecast API**（內含 JMA MSM/GSM 模型） 作為預報資料源（後續視可行性切換 JMA 直接 API）

確認後我會：
- (a) 取 4 個月期間的「歷史隔日預報」資料
- (b) 重訓模型以預報為輸入
- (c) 重算 CCRI 隔日預警準確率
- (d) 對標 JMA 高温注意情報資料（2025-07/08 山口縣）
- (e) 產出新版完整論文 §3-§4 草稿
