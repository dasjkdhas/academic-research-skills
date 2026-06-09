"""Methodology comparison: AMeDAS-style observation vs JMA forecast as model input.

Three architectures, all using day-ahead-safe feature subset (lags >= 24h):

  A. Obs-only       : weather features = observation (ERA5/AMeDAS proxy)
                      → POST-HOC upper bound; NOT deployable for true day-ahead
                      because tomorrow's observation doesn't exist at time T.

  B. Forecast-only  : weather features = JMA MSM forecast
                      → Realistic day-ahead deployment, current production setup.

  C. Hybrid         : lag-window weather (>=24h ago) from OBSERVATION,
                      prediction-window weather (current time t) from FORECAST.
                      → Most defensible: clean training signal for past + realistic
                      forecast for the prediction time.

The model, hyperparameters, CV scheme, holdout split are identical across A/B/C.
Only the weather feature source differs.
"""
import os, json, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures"
sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.0)

# ============================================================================
# Load base features (which were originally built with OBSERVATION weather)
# ============================================================================
df_obs = pd.read_parquet(f"{PROC}/features.parquet")
fcs    = pd.read_csv(f"{PROC}/jma_forecast_hourly.csv",
                     parse_dates=["timestamp"]).set_index("timestamp")

# Strip "_msm" suffix to align with observation column names
msm_cols = [c for c in fcs.columns if c.endswith("_msm")]
fcs_msm  = fcs[msm_cols].copy()
fcs_msm.columns = [c.replace("_msm", "") for c in fcs_msm.columns]

# Re-derive WBGT + heat_alert for forecast
T_f, RH_f = fcs_msm["temperature_2m"], fcs_msm["relative_humidity_2m"]
e_f = (RH_f / 100) * 6.105 * np.exp(17.27*T_f / (237.7+T_f))
fcs_msm["wbgt_approx"] = 0.567*T_f + 0.393*e_f + 3.94
def heat_alert(w):
    if pd.isna(w): return np.nan
    if w >= 31: return 4
    if w >= 28: return 3
    if w >= 25: return 2
    if w >= 21: return 1
    return 0
fcs_msm["heat_alert_level"] = fcs_msm["wbgt_approx"].apply(heat_alert)

WX_VARS = [c for c in fcs_msm.columns if c in df_obs.columns]
print(f"Aligned weather variables ({len(WX_VARS)}): {WX_VARS}")

# ============================================================================
# Build three feature DataFrames
# ============================================================================
def build_archA_obs(base: pd.DataFrame) -> pd.DataFrame:
    """Architecture A: observation everywhere (already the base)."""
    df = base.copy()
    df["temp_lag24"]  = df["temperature_2m"].shift(24)
    df["temp_lag168"] = df["temperature_2m"].shift(168)
    df["wbgt_lag1"]   = df["wbgt_approx"].shift(1)
    df["cdh_20"] = (df["temperature_2m"] - 20).clip(lower=0)
    df["hdh_18"] = (18 - df["temperature_2m"]).clip(lower=0)
    for lvl in [2, 3, 4]:
        df[f"heat_alert_ge{lvl}"] = (df["heat_alert_level"] >= lvl).astype(int)
    return df.dropna(subset=["temp_lag168", "b00_lag168", "y"])


def build_archB_forecast(base: pd.DataFrame, fcs: pd.DataFrame) -> pd.DataFrame:
    """Architecture B: forecast everywhere."""
    df = base.copy()
    df[WX_VARS] = fcs[WX_VARS].reindex(df.index)
    df["temp_lag24"]  = df["temperature_2m"].shift(24)
    df["temp_lag168"] = df["temperature_2m"].shift(168)
    df["wbgt_lag1"]   = df["wbgt_approx"].shift(1)
    df["cdh_20"] = (df["temperature_2m"] - 20).clip(lower=0)
    df["hdh_18"] = (18 - df["temperature_2m"]).clip(lower=0)
    for lvl in [2, 3, 4]:
        df[f"heat_alert_ge{lvl}"] = (df["heat_alert_level"] >= lvl).astype(int)
    return df.dropna(subset=["temp_lag168", "b00_lag168", "y"])


def build_archC_hybrid(base: pd.DataFrame, fcs: pd.DataFrame) -> pd.DataFrame:
    """Architecture C: hybrid.

    - Current-time weather (temperature_2m at row t)         : FORECAST
      (this is the prediction-window value, future at time T)
    - Lag features computed from OBSERVATION
      (past values, already realized at time T → use higher-fidelity obs)
    - WBGT/CDH/HDH/heat_alert derived from current-time forecast
      (because they're functions of current-time weather)
    """
    df = base.copy()
    # Current-time weather features ← forecast
    df[WX_VARS] = fcs[WX_VARS].reindex(df.index)
    # Lag features ← OBSERVATION (use base values, not the replaced ones)
    df["temp_lag24"]  = base["temperature_2m"].shift(24).reindex(df.index)
    df["temp_lag168"] = base["temperature_2m"].shift(168).reindex(df.index)
    df["wbgt_lag1"]   = base["wbgt_approx"].shift(1).reindex(df.index)
    # CDH/HDH/heat_alert ← derived from current-time weather (= forecast)
    df["cdh_20"] = (df["temperature_2m"] - 20).clip(lower=0)
    df["hdh_18"] = (18 - df["temperature_2m"]).clip(lower=0)
    for lvl in [2, 3, 4]:
        df[f"heat_alert_ge{lvl}"] = (df["heat_alert_level"] >= lvl).astype(int)
    return df.dropna(subset=["temp_lag168", "b00_lag168", "y"])


dfA = build_archA_obs(df_obs)
dfB = build_archB_forecast(df_obs, fcs_msm)
dfC = build_archC_hybrid(df_obs, fcs_msm)

# Align rows (intersect indices) so test set is identical across architectures
common_idx = dfA.index.intersection(dfB.index).intersection(dfC.index)
dfA = dfA.loc[common_idx]; dfB = dfB.loc[common_idx]; dfC = dfC.loc[common_idx]
print(f"Common samples: {len(common_idx)}  ({common_idx.min()} → {common_idx.max()})")


# ============================================================================
# Day-ahead-safe feature subset (same definition as 10_proper_day_ahead.py)
# ============================================================================
def safe_features(df: pd.DataFrame, min_lag: int = 24) -> list:
    feats = []
    for c in df.columns:
        if c in ("y", "y_peak", "b00", "day_type", "holiday_name", "dow_name", "dow"):
            continue
        if c.startswith("b") and not c.startswith("b00_"):
            continue
        if c.startswith("b00_lag"):
            lag = int(c.replace("b00_lag", ""))
            if lag < min_lag: continue
            feats.append(c); continue
        if c == "b00_roll24_mean" or c == "b00_roll24_std":
            continue
        if c == "b00_roll168_mean":
            feats.append(c); continue
        feats.append(c)
    return feats


feats = safe_features(dfA, min_lag=24)
# Ensure all three DataFrames have the same feature set
feats = [f for f in feats if f in dfA.columns and f in dfB.columns and f in dfC.columns]
print(f"Day-ahead-safe features: {len(feats)}")


# ============================================================================
# Train + evaluate each architecture (identical splits, model, seed)
# ============================================================================
def train_eval(df: pd.DataFrame, feats: list, label: str):
    n = len(df)
    init_train = int(n * 0.50)
    test_size  = int(n * 0.15)
    fold_results = []
    for i in range(3):
        tr_end = init_train + i*test_size
        te_end = tr_end + test_size
        if te_end > n: break
        Xtr = df[feats].iloc[:tr_end]; ytr = df["y"].iloc[:tr_end]
        Xte = df[feats].iloc[tr_end:te_end]; yte = df["y"].iloc[tr_end:te_end]
        model = lgb.LGBMRegressor(
            n_estimators=600, learning_rate=0.03, num_leaves=63,
            min_data_in_leaf=20, feature_fraction=0.85, bagging_fraction=0.85,
            bagging_freq=5, reg_alpha=0.1, reg_lambda=0.1,
            random_state=42, verbose=-1
        )
        model.fit(Xtr, ytr)
        pred = model.predict(Xte)
        mae  = mean_absolute_error(yte, pred)
        rmse = np.sqrt(mean_squared_error(yte, pred))
        r2   = r2_score(yte, pred)
        mape = (np.abs((yte - pred) / yte.replace(0, np.nan))).mean() * 100
        fold_results.append({"arch": label, "fold": i+1,
                             "MAE": mae, "RMSE": rmse, "R2": r2, "MAPE": mape})
    return fold_results


def holdout_eval(df: pd.DataFrame, feats: list, label: str, split_frac=0.70):
    n = len(df); split_pt = int(n * split_frac)
    Xtr = df[feats].iloc[:split_pt]; ytr = df["y"].iloc[:split_pt]
    Xte = df[feats].iloc[split_pt:]; yte = df["y"].iloc[split_pt:]
    model = lgb.LGBMRegressor(
        n_estimators=800, learning_rate=0.03, num_leaves=63,
        min_data_in_leaf=20, feature_fraction=0.85, bagging_fraction=0.85,
        bagging_freq=5, reg_alpha=0.1, reg_lambda=0.1,
        random_state=42, verbose=-1
    )
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    mae  = mean_absolute_error(yte, pred); rmse = np.sqrt(mean_squared_error(yte, pred))
    r2   = r2_score(yte, pred)
    mape = (np.abs((yte - pred) / yte.replace(0, np.nan))).mean() * 100
    # Day-level peak hit-rate for SDR call
    test_df = df.iloc[split_pt:].copy(); test_df["pred"] = pred
    test_df["date"] = test_df.index.date
    return {"arch": label, "MAE": mae, "RMSE": rmse, "R2": r2, "MAPE": mape,
            "split_pt": split_pt, "test_df": test_df, "model": model}


print("\n" + "=" * 70)
print("3-fold walk-forward CV  (identical splits, model, seed)")
print("=" * 70)
cv_rows = []
for label, df in [("A_Obs", dfA), ("B_Forecast", dfB), ("C_Hybrid", dfC)]:
    cv_rows += train_eval(df, feats, label)
    print(f"  {label:12s} done")
cv = pd.DataFrame(cv_rows)
cv_summary = cv.groupby("arch").agg(
    MAE_mean=("MAE", "mean"), MAE_std=("MAE", "std"),
    RMSE_mean=("RMSE", "mean"),
    R2_mean=("R2", "mean"), R2_std=("R2", "std"),
    MAPE_mean=("MAPE", "mean")
).round(3)
print("\nCV summary:")
print(cv_summary.to_string())

print("\n" + "=" * 70)
print("70/30 holdout final evaluation")
print("=" * 70)
holdouts = {}
for label, df in [("A_Obs", dfA), ("B_Forecast", dfB), ("C_Hybrid", dfC)]:
    h = holdout_eval(df, feats, label)
    holdouts[label] = h
    print(f"  {label:12s}  MAE={h['MAE']:.1f}  RMSE={h['RMSE']:.1f}  "
          f"R²={h['R2']:.3f}  MAPE={h['MAPE']:.2f}%")

# ============================================================================
# SDR call accuracy (day-level)
# ============================================================================
y_train_full = df_obs["b00"].dropna().iloc[:holdouts["A_Obs"]["split_pt"] + 168]
p80 = y_train_full.quantile(0.80)
p95 = y_train_full.quantile(0.95)
print(f"\nThresholds: P80={p80:.1f}, P95={p95:.1f} kW")

day_metrics = []
for label, h in holdouts.items():
    td = h["test_df"]
    # Predict day-level peak
    daily = td.groupby("date").agg(
        max_pred=("pred", "max"),
        max_actual=("b00", "max"),
    )
    daily["pred_call"] = daily["max_pred"] >= p80
    daily["true_peak"] = daily["max_actual"] >= p80
    tp = (daily["pred_call"] & daily["true_peak"]).sum()
    fp = (daily["pred_call"] & ~daily["true_peak"]).sum()
    fn = (~daily["pred_call"] & daily["true_peak"]).sum()
    tn = (~daily["pred_call"] & ~daily["true_peak"]).sum()
    prec = tp / max(tp+fp, 1); rec = tp / max(tp+fn, 1)
    f1 = 2*prec*rec/max(prec+rec, 1e-6)
    day_metrics.append({"arch": label, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
                        "precision": prec, "recall": rec, "F1": f1,
                        "peak_MAE_kW": float((daily["max_actual"] - daily["max_pred"]).abs().mean())})

day_df = pd.DataFrame(day_metrics).round(3)
print("\nDay-level SDR-call accuracy (P80 threshold):")
print(day_df.to_string(index=False))

# ============================================================================
# Save everything
# ============================================================================
cv_summary.to_csv(f"{RES}/arch_compare_cv.csv")
day_df.to_csv(f"{RES}/arch_compare_dayLevel.csv", index=False)

holdout_summary = {label: {"MAE": float(h["MAE"]), "RMSE": float(h["RMSE"]),
                            "R2": float(h["R2"]), "MAPE": float(h["MAPE"])}
                   for label, h in holdouts.items()}
with open(f"{RES}/arch_compare_summary.json", "w") as f:
    json.dump({
        "cv_summary": cv_summary.reset_index().to_dict(orient="records"),
        "holdout_summary": holdout_summary,
        "day_level": day_df.to_dict(orient="records"),
        "thresholds_kW": {"P80": float(p80), "P95": float(p95)},
        "n_features": len(feats),
        "n_samples": len(common_idx),
    }, f, indent=2)

# ============================================================================
# Visual comparison
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

ax = axes[0]
labels_order = ["A_Obs", "B_Forecast", "C_Hybrid"]
colors = {"A_Obs": "#1f4e79", "B_Forecast": "#d62728", "C_Hybrid": "#2ca02c"}
mae_means = [cv_summary.loc[l, "MAE_mean"] for l in labels_order]
mae_stds  = [cv_summary.loc[l, "MAE_std"]  for l in labels_order]
bars = ax.bar(labels_order, mae_means, yerr=mae_stds,
              color=[colors[l] for l in labels_order], alpha=0.85, capsize=4)
ax.set_ylabel("MAE (kW)")
ax.set_title("CV MAE  (lower = better)")
for b, v in zip(bars, mae_means):
    ax.text(b.get_x() + b.get_width()/2, v + 1, f"{v:.1f}",
            ha="center", fontsize=9, fontweight="bold")

ax = axes[1]
r2_means = [cv_summary.loc[l, "R2_mean"] for l in labels_order]
r2_stds  = [cv_summary.loc[l, "R2_std"]  for l in labels_order]
bars = ax.bar(labels_order, r2_means, yerr=r2_stds,
              color=[colors[l] for l in labels_order], alpha=0.85, capsize=4)
ax.set_ylabel("R²")
ax.set_ylim(0, 1)
ax.set_title("CV R²  (higher = better)")
for b, v in zip(bars, r2_means):
    ax.text(b.get_x() + b.get_width()/2, v + 0.01, f"{v:.3f}",
            ha="center", fontsize=9, fontweight="bold")

ax = axes[2]
f1_vals = day_df.set_index("arch").loc[labels_order, "F1"]
bars = ax.bar(labels_order, f1_vals,
              color=[colors[l] for l in labels_order], alpha=0.85)
ax.set_ylabel("F1 (day-level SDR call)")
ax.set_ylim(0, 1)
ax.set_title("Day-level SDR-call F1")
for b, v in zip(bars, f1_vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.01, f"{v:.2f}",
            ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.savefig(f"{FIG}/fig17_arch_compare.png", dpi=140)
plt.close()

# Time-series overlay on holdout
fig, ax = plt.subplots(figsize=(15, 5))
test_idx = holdouts["A_Obs"]["test_df"].index
ax.plot(test_idx, holdouts["A_Obs"]["test_df"]["b00"],
        lw=0.9, color="black", alpha=0.7, label="Actual b00")
for l in labels_order:
    ax.plot(holdouts[l]["test_df"].index, holdouts[l]["test_df"]["pred"],
            lw=0.7, color=colors[l], alpha=0.8,
            label=f"{l}  (MAE={holdouts[l]['MAE']:.1f}, R²={holdouts[l]['R2']:.3f})")
ax.axhline(p80, ls="--", color="orange", lw=0.9, label=f"P80={p80:.0f} kW")
ax.set_title("Holdout predictions: Observation vs Forecast vs Hybrid input")
ax.set_ylabel("Hourly load b00 (kW)")
ax.legend(loc="upper right", fontsize=8)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=20, ha="right")
plt.tight_layout()
plt.savefig(f"{FIG}/fig18_arch_compare_timeseries.png", dpi=130)
plt.close()

print(f"\n💾 saved → arch_compare_cv.csv, arch_compare_dayLevel.csv, "
      f"arch_compare_summary.json")
print(f"💾 figures → fig17_arch_compare.png, fig18_arch_compare_timeseries.png")
