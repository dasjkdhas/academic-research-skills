# Step 0: Data Diagnostic Report

**Site**: Yamaguchi University, Engineering Faculty — Central Electric Room
**Period**: 2025-07-06 00:00:00 → 2025-10-31 23:00:00  (2771 hours, ~115.5 days)

## 1. Headline numbers

| Statistic | Value |
|---|---|
| Hours observed         | 2771 |
| Missing hours (interp) | 0 |
| Mean load              | 809.5 kW |
| Median load            | 736.0 kW |
| Std deviation          | 327.6 kW |
| Max load               | **1786.0 kW** |
| P95 load               | 1450.0 kW |
| P99 load               | 1625.9 kW |
| Hours > 80% capacity   | 35 (1.3%) |
| Hours > 90% capacity   | **0** (0.0%) |
| Hours > 95% capacity   | 0 (0.0%) |
| Hours > 100% capacity  | **0** (0.00%) |

## 2. Per-building load summary (hourly kW)

| col | building | mean | min | max | share% |
|---|---|---|---|---|---|
| b00 | HV_main_total | 809.50 | 0.00 | 1786.00 | 100.0% |
| b01 | engineering_main | 202.62 | 0.00 | 476.00 | 25.0% |
| b02 | research_2 | 18.82 | 0.00 | 56.00 | 2.3% |
| b04 | env_coexist_dept | 25.25 | 0.00 | 80.00 | 3.1% |
| b05 | civil_practice | 57.85 | 0.00 | 143.20 | 7.1% |
| b06 | lecture_hall_D | 22.23 | 0.00 | 211.00 | 2.7% |
| b07 | elec_electronics | 264.24 | 0.00 | 550.00 | 32.6% |
| b08 | substation_internal | 8.96 | 0.00 | 45.00 | 1.1% |
| b09 | library | 3.87 | 0.00 | 23.30 | 0.5% |
| b10 | info_sci | 28.47 | 0.00 | 109.60 | 3.5% |
| b11 | advanced_research | 39.96 | 0.00 | 89.00 | 4.9% |
| b12 | media_center | 48.62 | 0.00 | 60.90 | 6.0% |
| b13 | welfare | 32.06 | 0.00 | 89.70 | 4.0% |
| b14 | civil_practice_T148_1 | 3.28 | 0.00 | 17.00 | 0.4% |
| b15 | civil_practice_T148_2 | 5.11 | 0.00 | 26.00 | 0.6% |

## 3. Stationarity (ADF test)

- ADF statistic = -3.1647
- p-value       = 0.022121
- Critical 5%   = -2.8626
- **Verdict**: stationary at 5% — direct differencing not strictly required.

## 4. Submetering coverage (Tier 1 feasibility check)

- Total b00 = sum(submeters) + residual
- Mean sum-of-submeters: 761.3 kW
- Mean residual (unmetered): 48.2 kW
- **Submetering coverage: 94.1%**  → Tier 1 SDR decomposition feasible.

## 5. Day-of-week pattern (mean load by day)

- Mon: 839.7 kW
- Tue: 850.1 kW
- Wed: 857.4 kW
- Thu: 874.8 kW
- Fri: 849.3 kW
- Sat: 704.4 kW
- Sun: 686.4 kW

- Weekday vs Weekend ratio: 854.3 / 695.4 = **1.23**

## 6. Peak hour analysis
- Peak hour-of-day (average across all weeks): **15:00** (1107.9 kW)
- Min hour-of-day: 5:00 (600.7 kW)

## 7. Data health flags

- ⚠ 134 zero-load hours (likely meter outage)
- ⚠ 133 duplicate rows