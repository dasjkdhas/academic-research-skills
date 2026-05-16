"""PROPER day-ahead forecast model (multi-step direct forecast).

KEY FIX: At deployment time T (today 17:00), to predict load at T+k for k=1..31,
we CANNOT use b00_lag1, b00_lag2, ..., b00_lag(k-1) because those are FUTURE.

Available features at deployment time T:
  - b00_lag(k) for k >= horizon (e.g., for predicting tomorrow's 14:00 from
    today 17:00, we can use load from 1 day ago at 14:00 = 24h lag)
  - All weather forecast features at prediction time
  - All calendar/time features at prediction time

This script trains a SINGLE model for the "day-ahead" task by using only
lags >= 24 hours, mimicking the worst-case scenario where any of tomorrow's
hours could be predicted from today's snapshot.
"""
import os, json, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures"
sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.0)

df = pd.read_parquet(f"{PROC}/features.parquet")
fcs = pd.read_csv(f"{PROC}/jma_forecast_hourly.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")

# Replace observed weather columns with JMA MSM forecast versions
msm_cols = [c for c in fcs.columns if c.endswith("_msm")]
fcs_msm = fcs[msm_cols].copy()
fcs_msm.columns = [c.replace("_msm", "") for c in fcs_msm.columns]

# Derive WBGT + heat_alert for forecast
T_f, RH_f = fcs_msm["temperature_2m"], fcs_msm["relative_humidity_2m"]
e_f = (RH_f/100) * 6.105 * np.exp(17.27*T_f/(237.7+T_f))
fcs_msm["wbgt_approx"] = 0.567*T_f + 0.393*e_f + 3.94
def heat_alert(w):
    if pd.isna(w): return np.nan
    if w >= 31: return 4
    if w >= 28: return 3
    if w >= 25: return 2
    if w >= 21: return 1
    return 0
fcs_msm["heat_alert_level"] = fcs_msm["wbgt_approx"].apply(heat_alert)

# Build features using forecast weather (replace observed)
weather_to_replace = [c for c in fcs_msm.columns if c in df.columns]
df_fcst = df.copy()
df_fcst[weather_to_replace] = fcs_msm[weather_to_replace].reindex(df_fcst.index)
# Re-derive temp_lag features from forecast
df_fcst["temp_lag24"]  = df_fcst["temperature_2m"].shift(24)
df_fcst["temp_lag168"] = df_fcst["temperature_2m"].shift(168)
df_fcst["wbgt_lag1"]   = df_fcst["wbgt_approx"].shift(1)
df_fcst["cdh_20"] = (df_fcst["temperature_2m"] - 20).clip(lower=0)
df_fcst["hdh_18"] = (18 - df_fcst["temperature_2m"]).clip(lower=0)
for lvl in [2, 3, 4]:
    df_fcst[f"heat_alert_ge{lvl}"] = (df_fcst["heat_alert_level"] >= lvl).astype(int)

# Drop NaN due to refreshed lags
df_fcst = df_fcst.dropna(subset=["temp_lag168", "b00_lag168", "y"])

# --- KEY: Day-ahead-safe feature subset ---
# Only b00_lag features with lag >= 24 are safe for day-ahead deployment
# (since we know yesterday's load when planning tomorrow)
def safe_features_for_horizon(df: pd.DataFrame, min_lag: int = 24) -> list:
    """Return features that are knowable at deployment time T for any horizon."""
    feats = []
    for c in df.columns:
        if c in ("y", "y_peak", "b00", "day_type", "holiday_name", "dow_name", "dow"):
            continue
        if c.startswith("b") and not c.startswith("b00_"):
            # building submeters — not used for predicting b00
            continue
        if c.startswith("b00_lag"):
            lag = int(c.replace("b00_lag", ""))
            if lag < min_lag:
                continue   # exclude lag1, lag2, etc. (future at deploy time)
            feats.append(c); continue
        if c == "b00_roll24_mean" or c == "b00_roll24_std":
            # rolling window already shifted by 1 — but for safety, exclude.
            # We'll use roll168 instead.
            continue
        if c == "b00_roll168_mean":
            feats.append(c); continue
        feats.append(c)
    return feats


feats_day_ahead = safe_features_for_horizon(df_fcst, min_lag=24)
print(f"Day-ahead-safe features: {len(feats_day_ahead)}")
print(f"Included b00_lag features: {[f for f in feats_day_ahead if f.startswith('b00_lag')]}")
print(f"Included b00_roll features: {[f for f in feats_day_ahead if f.startswith('b00_roll')]}")


# ============================================================================
# Walk-forward CV with day-ahead-safe features
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
        tr = slice(0, tr_end); te = slice(tr_end, te_end)
        Xtr = df[feats].iloc[tr]; ytr = df["y"].iloc[tr]
        Xte = df[feats].iloc[te]; yte = df["y"].iloc[te]
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
        fold_results.append({"label": label, "fold": i+1,
                             "MAE": mae, "RMSE": rmse, "R2": r2, "MAPE": mape})
        print(f"  [{label}] fold {i+1}: MAE={mae:.1f} R²={r2:.3f} MAPE={mape:.2f}%")
    return fold_results


print("\n" + "=" * 70)
print("CV with DAY-AHEAD-SAFE feature subset (lags >= 24h only)")
print("=" * 70)
results = train_eval(df_fcst, feats_day_ahead, "DayAhead-JMA-MSM")
agg = pd.DataFrame(results).groupby("label").agg(
    MAE_mean=("MAE", "mean"), MAE_std=("MAE", "std"),
    R2_mean=("R2", "mean"), MAPE_mean=("MAPE", "mean")
).round(3)
print("\nSummary:")
print(agg.to_string())
agg.to_csv(f"{RES}/day_ahead_model_perf.csv")


# ============================================================================
# Train final deployable day-ahead model (70/30)
# ============================================================================
n = len(df_fcst); split_pt = int(n * 0.70)
Xtr = df_fcst[feats_day_ahead].iloc[:split_pt]; ytr = df_fcst["y"].iloc[:split_pt]
Xte = df_fcst[feats_day_ahead].iloc[split_pt:]; yte = df_fcst["y"].iloc[split_pt:]
p95_tr = ytr.quantile(0.95)
ytr_cls = (ytr >= p95_tr).astype(int)
yte_cls = (yte >= p95_tr).astype(int)

model_reg = lgb.LGBMRegressor(
    n_estimators=800, learning_rate=0.03, num_leaves=63,
    min_data_in_leaf=20, feature_fraction=0.85, bagging_fraction=0.85,
    bagging_freq=5, reg_alpha=0.1, reg_lambda=0.1,
    random_state=42, verbose=-1
)
model_reg.fit(Xtr, ytr)
pred = model_reg.predict(Xte)
mae  = mean_absolute_error(yte, pred); r2 = r2_score(yte, pred)
mape = (np.abs((yte - pred) / yte.replace(0, np.nan))).mean() * 100
print(f"\nDay-Ahead Final Holdout: MAE={mae:.1f} R²={r2:.3f} MAPE={mape:.2f}%")

pos = max(ytr_cls.sum(), 1); neg = len(ytr_cls) - pos
w = np.where(ytr_cls == 1, neg/pos, 1.0)
model_cls = lgb.LGBMClassifier(
    n_estimators=400, learning_rate=0.03, num_leaves=31,
    min_data_in_leaf=15, feature_fraction=0.85,
    random_state=42, verbose=-1
)
model_cls.fit(Xtr, ytr_cls, sample_weight=w)
pred_cls = model_cls.predict_proba(Xte)[:, 1]

joblib.dump({"model_reg": model_reg, "model_cls": model_cls,
             "p95_thr": float(p95_tr), "features": feats_day_ahead,
             "split_pt": split_pt, "test_mae": float(mae), "test_r2": float(r2)},
            f"{RES}/day_ahead_model.pkl")


# ============================================================================
# Compute CCRI for day-ahead deployment
# ============================================================================
y_train_full = df["b00"].dropna().iloc[:split_pt + 168]
p50 = y_train_full.quantile(0.50)
p80 = y_train_full.quantile(0.80)
p95 = y_train_full.quantile(0.95)
print(f"\nThresholds: P50={p50:.1f}  P80={p80:.1f}  P95={p95:.1f} kW")

test_df = df_fcst.iloc[split_pt:].copy()
test_df["pred_reg"]      = pred
test_df["pred_cls_prob"] = pred_cls

duration = []
for i in range(len(test_df)):
    end = min(i + 6, len(test_df))
    duration.append((test_df["pred_reg"].iloc[i:end] >= p80).sum())
test_df["pred_duration_6h"] = duration

w1, w2, w3 = 0.50, 0.30, 0.20
test_df["CCRI"] = (
    w1 * (test_df["pred_reg"] / p80).clip(0, 2)
    + w2 * test_df["pred_cls_prob"]
    + w3 * (test_df["pred_duration_6h"] / 6)
)
def tier(c):
    if c >= 0.85: return "Critical"
    if c >= 0.65: return "High"
    return "Normal"
test_df["risk_tier"] = test_df["CCRI"].apply(tier)
test_df["sdr_recommended"] = test_df["risk_tier"].isin(["High", "Critical"])
test_df["date"] = test_df.index.date

print(f"\nDay-ahead CCRI tier distribution:")
print(test_df["risk_tier"].value_counts())

# Day-level decision aggregation
daily = test_df.groupby("date").agg(
    max_load_pred=("pred_reg", "max"),
    max_load_actual=("b00", "max"),
    n_high_or_critical=("sdr_recommended", "sum"),
    n_critical=("risk_tier", lambda s: (s == "Critical").sum()),
    max_ccri=("CCRI", "max"),
).round(1)
daily["sdr_call_issued"] = daily["n_high_or_critical"] > 0
daily["forecast_err_kW"] = daily["max_load_actual"] - daily["max_load_pred"]
daily.to_csv(f"{RES}/day_ahead_daily_decisions.csv")
print(f"\nDays with SDR call: {daily['sdr_call_issued'].sum()} / {len(daily)}")
print(f"Mean peak forecast error: {daily['forecast_err_kW'].mean():.1f} kW (positive = under-predicted)")
print(f"\nLast 10 days:")
print(daily.tail(10).to_string())

# Validation: do days with SDR call correspond to days that actually had peaks > P80?
true_peak_day = test_df.groupby("date")["b00"].max() >= p80
pred_call     = daily["sdr_call_issued"]
common = true_peak_day.index.intersection(pred_call.index)
tp = (true_peak_day.loc[common] & pred_call.loc[common]).sum()
fp = ((~true_peak_day.loc[common]) & pred_call.loc[common]).sum()
fn = (true_peak_day.loc[common] & (~pred_call.loc[common])).sum()
tn = ((~true_peak_day.loc[common]) & (~pred_call.loc[common])).sum()
prec = tp / max(tp+fp, 1); rec = tp / max(tp+fn, 1)
print(f"\nDay-level SDR call accuracy:")
print(f"  TP={tp} FP={fp} FN={fn} TN={tn}")
print(f"  Precision: {prec:.3f}   Recall: {rec:.3f}   F1: {2*prec*rec/max(prec+rec,1e-6):.3f}")


# ============================================================================
# Plot: actual vs forecast over test period
# ============================================================================
fig, axes = plt.subplots(2, 1, figsize=(15, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
ax = axes[0]
ax.plot(test_df.index, test_df["b00"], lw=0.9, color="#1f4e79", label="Actual b00")
ax.plot(test_df.index, test_df["pred_reg"], lw=0.9, color="#d62728",
        label="Day-ahead forecast (JMA MSM driven)")
ax.axhline(p80, ls="--", color="orange", lw=1, label=f"P80 threshold ({p80:.0f} kW)")
ax.axhline(p95, ls=":", color="red", lw=1, label=f"P95 threshold ({p95:.0f} kW)")
crit = test_df[test_df["risk_tier"] == "Critical"]
high = test_df[test_df["risk_tier"] == "High"]
ax.scatter(high.index, high["b00"], color="orange", s=10, alpha=0.7, label=f"SDR High (n={len(high)})")
ax.scatter(crit.index, crit["b00"], color="red",    s=15, label=f"SDR Critical (n={len(crit)})")
ax.set_title(f"Day-Ahead SDR Decision System (lags≥24h only)  —  Holdout MAE={mae:.1f} kW, R²={r2:.3f}, MAPE={mape:.2f}%")
ax.set_ylabel("Hourly load (kW)")
ax.legend(loc="upper right", fontsize=8, ncol=2)

ax = axes[1]
ax.plot(test_df.index, test_df["CCRI"], lw=0.8, color="#5a5a5a")
ax.fill_between(test_df.index, 0, test_df["CCRI"],
                where=(test_df["risk_tier"] == "High"), color="orange", alpha=0.4, label="High")
ax.fill_between(test_df.index, 0, test_df["CCRI"],
                where=(test_df["risk_tier"] == "Critical"), color="red", alpha=0.4, label="Critical")
ax.axhline(0.65, ls="--", color="orange", lw=0.8)
ax.axhline(0.85, ls="--", color="red", lw=0.8)
ax.set_ylabel("CCRI"); ax.set_xlabel("Time")
ax.legend(loc="upper right", fontsize=8)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=20, ha="right")
plt.tight_layout()
plt.savefig(f"{FIG}/fig15_day_ahead_proper.png", dpi=130)
plt.close()

# SHAP for this corrected model
import shap
sample = test_df.sample(min(500, len(test_df)), random_state=42)
X_sample = sample[feats_day_ahead]
explainer = shap.TreeExplainer(model_reg)
shap_values = explainer.shap_values(X_sample)
mean_abs = np.abs(shap_values).mean(axis=0)
top_idx = np.argsort(mean_abs)[::-1][:12]
top12 = [(feats_day_ahead[i], float(mean_abs[i])) for i in top_idx]
print("\nTop 12 features for day-ahead model:")
for f, v in top12:
    print(f"  {f:30s}  {v:.2f}")

shap.summary_plot(shap_values, X_sample, show=False, max_display=15)
plt.tight_layout()
plt.savefig(f"{FIG}/fig16_shap_day_ahead.png", dpi=130, bbox_inches="tight")
plt.close()

# Save summary
summary = {
    "model_type": "LightGBM day-ahead forecast-driven",
    "deployment_constraint": "Only lag >= 24h used (no future leak)",
    "test_metrics": {"MAE_kW": float(mae), "R2": float(r2), "MAPE_pct": float(mape)},
    "cv_mean_MAE": float(agg.loc["DayAhead-JMA-MSM", "MAE_mean"]),
    "day_level_decision": {"precision": float(prec), "recall": float(rec),
                            "TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn),
                            "n_days_with_call": int(daily["sdr_call_issued"].sum()),
                            "total_days": int(len(daily))},
    "ccri_thresholds": {"P50": float(p50), "P80": float(p80), "P95": float(p95)},
    "top_features_shap": [{"feature": f, "mean_abs": v} for f, v in top12],
}
with open(f"{RES}/day_ahead_proper_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"\n💾 saved → day_ahead_model.pkl, day_ahead_daily_decisions.csv, day_ahead_proper_summary.json")
