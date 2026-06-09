# Data Acquisition & Paper Submission Roadmap (v2)

**Target**: Energy & Buildings (IF ~7) — primary; Applied Energy as stretch goal
**Timeline**: 3 months
**Date drafted**: 2026-05-17 (revised: data plan changed from 3-year to 2025 full-year)

---

## 1. Paper Re-framing (Strategic)

### From → To

| Original | Revised |
|---------|---------|
| "Forecast-driven Setpoint DR deployment system" | **"Hybrid-source weather inputs for day-ahead peak load forecasting: methodology + Soft DR impact assessment"** |

### Terminology Update (Important)
- **"SDR" now means "Soft Demand Response"** (broader, modern term)
  - Not "Setpoint DR" (which only refers to HVAC setpoint adjustment)
  - Soft DR encompasses setpoint + lighting + non-critical loads, matching the
    Japanese ERAB (METI) terminology "ソフトデマンドレスポンス"

### Why
- No historical SDR logs → cannot validate real SDR effectiveness
- Re-framing: contribution = **methodology + influence assessment**, not deployment

### Revised Working Title
- **EN**: "Day-ahead university campus peak load forecasting using hybrid-source weather inputs: a methodology and Soft DR impact study"
- **JP**: 「ハイブリッド気象入力による大学キャンパスの翌日ピーク電力予測 ― 手法と Soft DR 影響分析」

---

## 2. Data Inventory

### Currently Available (✅)
- 2025-07 to 2025-10 (89 valid days, hourly)
- Building b00–b15 hourly load
- **ERA5 hourly observations (Open-Meteo Historical API)**
  - Note: AMeDAS Ube station has only 4-element measurement (temp/wind/rain/sunshine), no humidity
  - ERA5 is used because of its complete variable coverage and global grid
- JMA MSM (5km, +39h) + JMA GSM (20km, +264h) hourly forecasts
- Japanese calendar (holidays, business days)

### Revised Data Plan: 2025 full year (single year, complete cycle)

**Strategy change**: Instead of 3-year cross-temporal validation, use **2025 full-year**
with internal temporal hold-out. Rationale:
- 12-month cycle covers winter heating + spring shoulder + summer cooling + autumn shoulder
- Simpler narrative ("we model one full year") vs. complex cross-year story
- Easier to obtain (one year of BEMS export)
- Matches journal expectation: at least one full annual cycle

### Required Data for Paper

#### 🔴 Tier 0 — Must obtain in Week 1-2

| Data | Source | Format |
|------|--------|--------|
| **2025 full-year hourly load (b00–b15)** | BEMS / 設施課 | CSV, hourly, kWh |
| Electricity tariff contract structure | 経理課 / 電力契約書 | Markdown summary + monthly billing CSV |
| Academic calendar 2025 | 教務課 / 大学官網 | CSV with `date, term_type, is_exam, is_intensive` |

#### 🟧 Tier 1 — Strongly recommended (Week 3-4)

| Data | Source | Format |
|------|--------|--------|
| Indoor temperature, representative rooms | BEMS or installed loggers | 1-2 points × hourly |
| Building b00 specs | 設施圖面 | Floor area, HVAC equipment, COP, construction year |

#### 🟨 Tier 2 — Bonus
- AMeDAS station observation (Yamaguchi / Ube — note humidity unavailable for Ube)
- HVAC vs lighting vs equipment submetering
- Past power-supply-tight period records (電力ひっ迫 alerts)

---

## 3. File Organization Standard

### Directory Structure
```
raw_data_v2/
├── power_hourly/
│   ├── b00_2025.csv      # timestamp, kWh — full year
│   ├── b01_2025.csv ...
│   └── README.md         # units, missing-value policy, meter notes
├── weather_observed/     # use ERA5 (Open-Meteo) for analysis
│   └── era5_yamaguchi_2025.csv
├── weather_forecast/
│   └── jma_msm_yamaguchi_2025.csv
├── tariff/
│   ├── contract_summary.md      # 契約電力, peak hours, tariff structure
│   └── billing_monthly_2025.csv
├── building_specs/
│   └── b00_specs.csv            # floor area, HVAC, COP, construction year
├── academic_calendar/
│   └── academic_calendar_2025.csv
└── indoor_temp/                  # if available
    └── b00_room_*.csv
```

### File Format Rules (Hard Requirements)
- **First column**: `timestamp` in ISO 8601 with JST offset (`2025-08-15 14:00:00+09:00`)
- **Missing values**: blank or `NaN` — **never use 0 or -999** (see 2025-10-27 incident)
- **Encoding**: UTF-8 (Shift-JIS will be converted, costs time)
- **One variable per column** — no wide-format hourly tables
- **One year per file**

---

## 4. Data Splitting Design (Updated for Single-Year)

### Temporal Hold-out within 2025
```
Train  : 2025-01 to 2025-09  (~9 months, all seasons covered)
Test   : 2025-10 to 2025-12  (~3 months, autumn + winter)
```

This is the **gold-standard temporal generalization test** that journal reviewers expect, with the benefit of covering both heating and cooling regimes.

### Internal Validation
Within train set, use walk-forward CV with 3-month folds to tune hyperparameters.

### Why this is acceptable for a journal
- Full annual cycle (12 months) is the minimum data scale E&B expects
- Walk-forward CV demonstrates temporal robustness
- Including winter heating + autumn shoulder season strengthens the methodology
- Discuss limitations of single-year data in Section 5; mention multi-year as future work

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

## 6. Counterfactual Soft DR Impact (Replaces Missing SDR Log)

### Method
On predicted Critical days (CCRI ≥ 0.85):
1. Identify hours where forecast b00 ≥ P95
2. Apply assumed Soft DR response: setpoint +2°C → AC load × 0.85 (literature: Park 2024)
3. Recompute b00_counterfactual = b00 - ΔAC_load
4. Sum peak reduction × tariff = economic savings

### Required Inputs
- Tariff structure (Tier 0)
- HVAC fraction of total b00 (Tier 1, from sub-metering or literature default ≈40%)
- Setpoint response coefficient (literature: 5–10% per °C)

---

## 7. Twelve-Week Timeline (Revised)

| Week | Owner | Action |
|------|------|--------|
| **W1** | User | Send formal data request: 2025 full-year hourly load (b00-b15), tariff, academic calendar |
| **W2** | User | Follow up; collect tariff PDF + academic schedule |
| **W2-3** | Me | Ingest 2025 full year; merge with existing 7-10月 data |
| **W3-4** | User | Obtain Tier 1: indoor temperature, building specs |
| **W4-5** | Me | Retrain Architecture C on Jan-Sep train, Oct-Dec test; add 5 baselines |
| **W6** | Me | Annual cycle analysis: winter heating vs summer cooling correlation differences |
| **W7** | Me | Counterfactual Soft DR + economic analysis; sensitivity studies |
| **W8** | Me | Finalize all figures/tables; statistical significance tests |
| **W9** | Me | Draft Sections 1-3 (Intro, Related Work, Methodology) |
| **W10** | Me | Draft Sections 4-6 (Results, Discussion, Conclusion) |
| **W11** | User + Me | Internal review; revision |
| **W12** | User | Submit + cover letter |

---

## 8. Risk Register

| Risk | Impact | Mitigation |
|------|-------|------------|
| 2025 Jan-Jun data unavailable | Cannot do full-year analysis | Fallback: extend existing 4-month dataset only; downgrade to conference paper |
| Tariff data sensitive | No economic analysis | Use generic Japanese university tariff template + sensitivity range |
| BEMS data format inconsistent across months | Pipeline rework | Build ingest with reconciliation script |
| Indoor temperature not available | Weak comfort argument | Use literature defaults + simulation-based comfort proxy |
| Winter behavior very different from summer | Single model insufficient | Train season-conditional models or use season-dummy features |

---

## 9. User Action Items (This Week)

1. ✉ **Email 設施課**: request **2025-01-01 to 2025-12-31** hourly meter data for b00-b15 (raw or BEMS export)
2. ✉ **Email 経理課**: request electricity contract structure and 2025 monthly billing summary
3. 📄 **Download** academic calendar 2025 from university website; convert to CSV
4. 🗣 **Internal discussion**: confirm authorization to publish anonymized building-level data (or use codenames)

---

## 10. Long-term Roadmap (Beyond This Paper)

If this paper is accepted, follow-up papers (with more data over time):
- **Year +1**: Multi-year analysis (2024 + 2025 + 2026)
- **Year +1.5**: Multi-campus extension (collaboration with another university)
- **Year +2**: Real Soft DR field trial (with operator feedback)
- **Year +2.5**: Transfer learning across campuses

These should be mentioned in the Conclusions / Future Work section.
