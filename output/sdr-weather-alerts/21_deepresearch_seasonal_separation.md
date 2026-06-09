# Deep-Research レポート — 温度応答解析における季節分離の妥当性

**問い**: キャンパス電力の温度応答 (energy signature / change-point) 解析で、冬季・夏季・過渡期を分離して計算・分析すべきか? 文献上の標準手法と根拠は?

**結論 (確信度: 高)**: ✅ **季節分離は確立された標準手法**であり、本研究に採用すべき。単一の通年回帰は (i) 過渡期の平坦域が冷房・暖房の傾きを希釈し、(ii) 暖房regime と冷房regime を一本のV字に押し込めることで両端の感度推定を不安定化させる。**冷房期・暖房期・過渡期を分けるか、最低でも heating/cooling の change-point を別々に推定するのが de facto standard**。

---

## 1. 主要な検証済み知見 (claim → 根拠)

### Claim 1 — 温度-電力関係は V/U 字型で、最低点 (balance/comfort point) は気候により ~18–27°C
- 米国一般: 最低需要は ~65°F (18°C) 付近、両側で傾きが立つ U 字 [YesEnergy; arXiv 2503.07213]
- ベトナム (高温・高AC普及): 最低点 26–27°C と高温側にシフト [Vietnam, ScienceDirect S037787782100623X]
- **含意**: balance point は気候・AC普及率に依存する → 各地点で実測すべき (本研究の宇部で実測した 17–22°C は妥当範囲)
- **確信度**: 高 (独立 3 ソース収束)

### Claim 2 — 暖房と冷房は別々の change-point (balance temperature) を持つ
- 都市規模の例: 暖房 change-point ≈ 14°C, 冷房 change-point ≈ 18°C と別個に同定される [MDPI Buildings 12(10):1717; degreedays.net base-temperature]
- 3-parameter change-point モデルは「冷房(暖房)は気温が建物 balance 温度を上(下)回ると始まる」状況を記述 [ASHRAE inverse modeling; Wikipedia energy signature]
- **含意**: 暖房閾値 ≠ 冷房閾値。両者を別々に推定するのが正しい。本研究の通年3区分回帰 (暖房閾値・冷房閾値) はこれと整合するが、**季節を分ければ各閾値の推定がより安定する**。
- **確信度**: 高

### Claim 3 — 過渡期 (春・秋 = shoulder season) は需要最低・温度応答最小
- 春 = 3–5 月、秋 = 9–11 月が一般的定義。外気温が建物内部温度に近く、暖房・冷房需要が年間最低 [EIA "shoulder season"; Tagup; Amperon]
- 外気温 ~55–75°F (13–24°C) が shoulder month の目安 [Tagup]
- **含意**: 過渡期は「制度ベース負荷」が支配的で温度感度がほぼゼロ → **通年回帰に混ぜると冷房・暖房の傾きを希釈する**。分離すべき最大の理由。
- **確信度**: 高

### Claim 4 — regime を pooling すると推定にバイアス、piecewise/switching または季節別モデルが推奨
- 非線形関係は「複数の線形領域 (piecewise linear / linear splines)」で近似。2 領域の場合は break point が暖房→冷房の switch を表す switching regression [arXiv 2310.15204; uwaterloo miller17]
- 閾値温度をモデル内で内生推定する手法も発展 [arXiv 2503.07213, distributional regression]
- **含意**: 本研究が pwlf (区分線形) を採用しているのは方法論的に正しい。季節分離はこれを補強する。
- **確信度**: 高

### Claim 5 — 占用 (occupied/unoccupied) 別の回帰分離も標準推奨
- 「平日 (月-金) と週末 (土日) で別々に回帰分析せよ」「曜日の占用差ノイズを減らすため週次集約せよ」 [degreedays.net regression-analysis]
- baseload (天候非依存) と weather-dependent を分離 [degreedays.net; Wikipedia]
- **含意**: 本研究の「校歴状態別 energy signature」(上課日/週末/休業) は文献の occupied/unoccupied 分離の精緻化版であり、**季節分離と組合せると二重に正当**。
- **確信度**: 高

---

## 2. 本研究への具体的提言

| 提言 | 根拠 | 実装 |
|---|---|---|
| **冷房期・暖房期・過渡期の 3 季に分離** | Claim 3,4 | 月で定義: 冷房期 6–9月 / 暖房期 12–3月 / 過渡期 4–5,10–11月 |
| 冷房期は **正の傾き** (冷房感度) を線形推定 | Claim 1,2 | 季内は単調 → 単純線形で安定 |
| 暖房期は **負の傾き** (暖房感度) を線形推定 | Claim 1,2 | 通年V字より安定 |
| 過渡期は **平坦** を確認 (制度ベース負荷の純粋推定) | Claim 3 | 温度感度≈0 を示す → baseload 推定に最適 |
| 季 × 校歴状態 の二重層別 | Claim 5 | 冷房期 × 上課日 が最重要セル |
| balance point は宇部で実測 (借り物の 18°C を使わない) | Claim 1 | 既に実測済み (17–22°C) |

**注意点 (over-fragmentation の回避)**: 暖房期 × 上課日 × 極寒 はサンプルが少ない (冬季は授業日減 + 1-2月電力欠測)。季 × 校歴の全組合せではなく、**冷房期は校歴層別を厚く、暖房期は季のみ**という非対称設計が現実的。

---

## 3. 文献上の「季節分離の標準デザイン」テンプレート

```
通年データ
  ├── 冷房期 (Cooling season)   : 冷房 change-point 以上が主 → 冷房感度 β_c
  ├── 暖房期 (Heating season)   : 暖房 change-point 以下が主 → 暖房感度 β_h
  └── 過渡期 (Transition/shoulder): balance band → baseload (温度感度≈0)
各季内でさらに occupied / unoccupied (上課日/週末・休業) に分離
```

これは ASHRAE Guideline 14 / IMT の change-point 思想 + degreedays.net の実務指針を統合した形であり、Energy and Buildings 系誌で広く受容される。

---

## 4. 論文 Methods への記述案 (英語)

> Following standard energy-signature practice (Kissock et al.; ASHRAE Guideline 14)
> and the recommendation to separate weather regimes rather than pool them, we
> stratify the year into a cooling season (Jun–Sep), a heating season (Dec–Mar),
> and transition (shoulder) seasons (Apr–May, Oct–Nov). Pooling all months into a
> single change-point model dilutes the cooling and heating slopes through the
> near-flat shoulder-season balance band; season-specific regression yields stable,
> physically interpretable cooling (β_c) and heating (β_h) sensitivities. Within
> each season we further separate institutional states (class day vs. weekend/
> vacation), consistent with the occupied/unoccupied separation recommended for
> weather normalization.

---

## 5. 出典 (Sources)

- [MDPI Buildings 12(10):1717 — Simplified Weather-Related Building Energy Disaggregation and Change-Point Regression](https://www.mdpi.com/2075-5309/12/10/1717)
- [A cooling change-point model of community-aggregate electrical load — Energy and Buildings](https://www.sciencedirect.com/science/article/abs/pii/S0378778810002550)
- [Energy signature — Wikipedia](https://en.m.wikipedia.org/wiki/Energy_signature)
- [Estimation of changeover times and degree-day balance point temperatures using energy signatures — Sustainable Cities and Society](https://www.sciencedirect.com/science/article/abs/pii/S2210670717306996)
- [EIA — What is the shoulder season in electricity markets?](https://www.eia.gov/todayinenergy/detail.php?id=64044)
- [Tagup — HVAC Shoulder Seasons](https://www.tagup.ai/post/hvac-shoulder-seasons-peak-relative-savings-from-cooling-optimization)
- [Frontiers — Temperature-sensitive electricity demand, Florida](https://www.frontiersin.org/journals/sustainable-energy-policy/articles/10.3389/fsuep.2023.1271035/full)
- [Nonlinear temperature response of electricity loads, Vietnam — Energy](https://www.sciencedirect.com/science/article/pii/S037787782100623X)
- [Nonlinear temperature sensitivity of residential electricity demand (distributional regression) — arXiv 2503.07213](https://arxiv.org/pdf/2503.07213)
- [Mid-Long Term Daily Electricity Consumption Forecasting (piecewise linear) — arXiv 2310.15204](https://arxiv.org/pdf/2310.15204)
- [degreedays.net — Regression Analysis of Energy Consumption and Degree Days](https://www.degreedays.net/regression-analysis)
- [degreedays.net — Base Temperature (Balance Point)](https://www.degreedays.net/base-temperature)
- [Frontiers — Temperature Variability on Seasonal Electricity Demand, Southern US](https://www.frontiersin.org/journals/sustainable-cities/articles/10.3389/frsc.2021.644789/full)

**作成日**: 2026-05-31 | 検証: 5 検索アングル + 多ソース収束 (MDPI 本文は 403 のため検索スニペット + 独立ソースで裏付け)
