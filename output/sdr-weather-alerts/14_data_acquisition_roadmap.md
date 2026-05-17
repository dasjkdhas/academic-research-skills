# Data Acquisition & Paper Submission Roadmap

**Target**: Energy & Buildings (IF ~7) — primary; Applied Energy as stretch goal
**Timeline**: 3 months
**Date drafted**: 2026-05-17

---

## 1. Paper Re-framing (Strategic)

### From → To

| Original | Revised |
|---------|---------|
| "Forecast-driven SDR deployment system" | **"Hybrid-source weather inputs for day-ahead peak load forecasting: methodology + counterfactual SDR impact assessment"** |

### Why
- No historical SDR logs → cannot validate real SDR effectiveness
- Re-framing: contribution = **methodology + influence assessment**, not deployment
- Energy & Buildings is more receptive to methodology papers than Applied Energy

### Revised Working Title (English / Japanese)
- **EN**: "Day-ahead university campus peak load forecasting using hybrid-source weather inputs: a methodology and counterfactual SDR impact study"
- **JP**: 「ハイブリッド気象入力による大学キャンパスの翌日ピーク電力予測 ― 手法と反事実SDR影響分析」

---

## 2. Data Inventory

### Currently Available (✅)
- 2025-07 to 2025-10 (89 valid days, hourly)
- Building b00–b15 hourly load
- ERA5 hourly observations
- JMA MSM (5km, +39h) + JMA GSM (20km, +264h) hourly forecasts
- Japanese calendar (holidays, business days)

### Required for Paper

#### 🔴 Tier 0 — Must obtain in Week 1-2 (paper cannot proceed without)
| Data | Source | Format |
|------|--------|--------|
| 2023+2024 hourly load (b00–b15), July–Oct | BEMS / 設施課 | CSV, hourly, kWh |
| Electricity tariff contract structure | 経理課 / 電力契約書 | Markdown summary + monthly billing CSV |
| Academic calendar 2023–2025 | 教務課 / 大学官網 | CSV with `date, term_type, is_exam, is_intensive` |

#### 🟧 Tier 1 — Strongly recommended (Week 3-4)
| Data | Source | Format |
|------|--------|--------|
| Winter (Dec–Feb) hourly load 2023–2024 | Same as above | If pursuing all-year SDR; otherwise scope to summer |
| Indoor temperature, representative rooms | BEMS or installed loggers | 1-2 points × hourly |
| Building b00 specs | 設施圖面 | Floor area, HVAC equipment, COP, construction year |

#### 🟨 Tier 2 — Bonus
- AMeDAS station observation (Yamaguchi / Ube / Hofu)
- HVAC vs lighting vs equipment submetering
- Past power-supply-tight period records (電力ひっ迫 alerts)

---

## 3. File Organization Standard

### Directory Structure
```
raw_data_v2/
├── power_hourly/
│   ├── b00_2023.csv      # timestamp, kWh
│   ├── b00_2024.csv
│   ├── b00_2025.csv
│   ├── b01-15_*.csv ...
│   └── README.md         # units, missing-value policy, meter notes
├── weather_amedas/
│   └── yamaguchi_amedas_hourly_2023-2025.csv
├── tariff/
│   ├── contract_summary.md      # 契約電力, peak hours, tariff structure
│   └── billing_monthly_2023-2025.csv
├── building_specs/
│   └── b00_specs.csv            # floor area, HVAC, COP, construction year
├── academic_calendar/
│   └── academic_calendar_2023-2025.csv
└── indoor_temp/                  # if available
    └── b00_room_*.csv
```

### File Format Rules (Hard Requirements)
- **First column**: `timestamp` in ISO 8601 with JST offset (`2024-08-15 14:00:00+09:00`)
- **Missing values**: blank or `NaN` — **never use 0 or -999** (see 2025-10-27 incident)
- **Encoding**: UTF-8 (Shift-JIS will be converted, costs time)
- **One variable per column** — no wide-format hourly tables
- **One year per file** (or one month if data source is monthly-natural)

---

## 4. Data Splitting Design

### Cross-year Hold-out
```
Train  : 2023-07 to 2024-10  (~4 months × 2 years = ~5,800 hours)
Test   : 2025-07 to 2025-10  (~3 months  ← already secured)
```

This is the **gold-standard temporal generalization test** that journal reviewers expect.

### Internal Validation
Within train set, use walk-forward CV with 3-month folds to tune hyperparameters.

---

## 5. Required Baselines (Reviewer Expectation)

For E&B / AE, the model comparison must include:

| Baseline | Why |
|---------|-----|
| Persistence (today = yesterday) | Sanity check; reviewers always ask |
| Seasonal naive (today = same DOW last week) | Captures weekly periodicity |
| Linear regression with weather | Linear baseline |
| XGBoost (standard ML baseline) | Comparable tree-based |
| **LightGBM-Hybrid (this work)** | Proposed |
| LSTM or simple Transformer | Deep learning baseline |

All on the same train/test split, same features set.

---

## 6. Counterfactual SDR Impact (Replaces Missing SDR Log)

### Method
On predicted Critical days (CCRI ≥ 0.85):
1. Identify hours where forecast b00 ≥ P95
2. Apply assumed SDR response: setpoint +2°C → AC load × 0.85 (literature: Park 2024)
3. Recompute b00_counterfactual = b00 - ΔAC_load
4. Sum peak reduction × tariff = economic savings

### Required Inputs
- Tariff structure (Tier 0)
- HVAC fraction of total b00 (Tier 1, from sub-metering or literature default ≈40%)
- Setpoint response coefficient (literature: 5–10% per °C)

---

## 7. Twelve-Week Timeline

| Week | Owner | Action |
|------|------|--------|
| **W1** | User | Send formal data request: 2023-2024 hourly load (b00-b15), tariff structure, academic calendar |
| **W2** | User | Follow up; collect tariff PDF + academic schedule |
| **W2-3** | Me | Build multi-year ingest pipeline; harmonize 2023-2025 |
| **W3-4** | User | Obtain Tier 1: indoor temperature, building specs |
| **W4-5** | Me | Retrain Architecture C on 2023-24 train, 2025 test; add 5 baselines |
| **W6-7** | Me | Counterfactual SDR + economic analysis; sensitivity studies |
| **W8** | Me | Finalize all figures/tables; cross-year SHAP; statistical significance tests |
| **W9** | Me | Draft Sections 1-3 (Intro, Related Work, Methodology) |
| **W10** | Me | Draft Sections 4-6 (Results, Discussion, Conclusion) |
| **W11** | User + Me | Internal review; revision |
| **W12** | User | Submit + cover letter |

---

## 8. Risk Register

| Risk | Impact | Mitigation |
|------|-------|------------|
| 2023-2024 data unavailable | Cannot do cross-year hold-out | Fallback: walk-forward CV within 2025; downgrade target to conference paper |
| Tariff data sensitive | No economic analysis | Use generic Japanese university tariff template + sensitivity range |
| BEMS data format inconsistent across years | Pipeline rework | Build year-by-year ingest with reconciliation script |
| Indoor temperature not available | Weak comfort argument | Use literature defaults + simulation-based comfort proxy |

---

## 9. User Action Items (This Week)

1. ✉ **Email 設施課**: request 2023-07 to 2024-10 hourly meter data for b00-b15 (raw or BEMS export)
2. ✉ **Email 経理課**: request electricity contract structure and 2023-2025 monthly billing summary
3. 📄 **Download** academic calendar 2023-2025 from university website; convert to CSV
4. 🗣 **Internal discussion**: confirm authorization to publish anonymized building-level data (or use codenames)

---

## 10. Long-term Roadmap (Beyond This Paper)

If this paper is accepted, follow-up papers (with more data over time):
- **Year +1**: Multi-campus extension (collaboration with another university)
- **Year +1.5**: Real SDR field trial (with operator feedback)
- **Year +2**: Transfer learning across campuses

These should be mentioned in the Conclusions / Future Work section.
