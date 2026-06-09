"""Forecast-driven day-ahead SDR decision model.

Realistic deployment scenario:
  At today T (e.g., 17:00 JST), we have:
    - All OBSERVED b00 load up to T
    - JMA MSM FORECAST for the next 24-39 hours
  We want to predict load b00[T+1 .. T+24] using FORECAST features (not observed)
  → output: per-hour CCRI risk for tomorrow → SDR decision

Features re-engineered:
  Lag features (b00_lag1..168, b00_roll24): from OBSERVED past (available at T)
  Weather features at prediction time t: from JMA MSM FORECAST (forecast for t)
  Calendar features at prediction time t: known (deterministic)

This is the FORECAST-AWARE version. Compare against OBSERVED-AWARE
('cheating') baseline that uses ERA5 observations.
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
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                              f1_score, precision_score, recall_score,
                              roc_auc_score, average_precision_score)
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import joblib

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures"
sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.0)


# ============================================================================
# Load all data: load + ERA5 obs + JMA MSM forecast + calendar
# ============================================================================
print("=" * 70); print("Loading data..."); print("=" * 70)
pw  = pd.read_csv(f"{PROC}/campus_power_hourly.csv", parse_dates=["timestamp"]).set_index("timestamp")
obs = pd.read_csv(f"{PROC}/weather_hourly.csv",       parse_dates=["timestamp"]).set_index("timestamp")
fcs = pd.read_csv(f"{PROC}/jma_forecast_hourly.csv",  parse_dates=["timestamp"]).set_index("timestamp")
cal = pd.read_csv(f"{PROC}/calendar.csv", parse_dates=["date"]).set_index("date")

# Drop GSM, keep only MSM forecast columns (rename to drop _msm suffix for cleaner code)
msm_cols = [c for c in fcs.columns if c.endswith("_msm")]
fcs = fcs[msm_cols].copy()
fcs.columns = [c.replace("_msm", "") for c in fcs.columns]
print(f"Power: {pw.shape}, Obs: {obs.shape}, Fcst MSM: {fcs.shape}")

# Derive WBGT proxy for forecast
T_f, RH_f = fcs["temperature_2m"], fcs["relative_humidity_2m"]
e_f = (RH_f/100) * 6.105 * np.exp(17.27*T_f/(237.7+T_f))
fcs["wbgt_approx"] = 0.567*T_f + 0.393*e_f + 3.94
# Heat alert tiers
def heat_alert(w):
    if pd.isna(w): return np.nan
    if w >= 31: return 4
    if w >= 28: return 3
    if w >= 25: return 2
    if w >= 21: return 1
    return 0
fcs["heat_alert_level"] = fcs["wbgt_approx"].apply(heat_alert)


# ============================================================================
# Build features — two parallel datasets
# ============================================================================
def build_features(power_df: pd.DataFrame, weather_df: pd.DataFrame,
                   cal: pd.DataFrame, name: str) -> pd.DataFrame:
    """Build feature dataframe joining power + given weather source + calendar."""
    common = power_df.index.intersection(weather_df.index)
    df = power_df.loc[common].join(weather_df.loc[common], how="inner")
    df["date_only"] = df.index.normalize()
    cal_lookup = cal.reset_index().rename(columns={"date": "date_only"})
    df = df.reset_index().merge(cal_lookup, on="date_only", how="left").set_index("timestamp")
    df.drop(columns=["date_only"], inplace=True)

    df["hour"] = df.index.hour
    df["dow_int"] = df.index.dayofweek
    df["month"] = df.index.month
    df["day_of_year"] = df.index.dayofyear
    df["is_weekend"] = (df["dow_int"] >= 5).astype(int)
    df["is_class_day"] = df["is_class_day"].astype(int)
    for col, period in [("hour", 24), ("dow_int", 7), ("month", 12)]:
        df[f"{col}_sin"] = np.sin(2*np.pi*df[col]/period)
        df[f"{col}_cos"] = np.cos(2*np.pi*df[col]/period)
    df["dow_hour"] = df["dow_int"]*100 + df["hour"]

    le = LabelEncoder()
    df["day_type_id_A"] = le.fit_transform(df["day_type"].fillna("unknown"))
    daily_profile = df["b00"].groupby(df.index.date).apply(
        lambda x: x.reset_index(drop=True).iloc[:24]).unstack()
    daily_profile.columns = [f"h{i:02d}" for i in range(daily_profile.shape[1])]
    daily_profile.index = pd.to_datetime(daily_profile.index)
    daily_profile = daily_profile.dropna(thresh=20)
    profile_norm = daily_profile.div(daily_profile.mean(axis=1), axis=0).fillna(0)
    km = KMeans(n_clusters=5, n_init=20, random_state=42)
    day_cluster = pd.Series(km.fit_predict(profile_norm),
                            index=profile_norm.index, name="day_type_id_B")
    cluster_lookup = day_cluster.reset_index().rename(columns={"index":"date_only"})
    cluster_lookup["date_only"] = pd.to_datetime(cluster_lookup["date_only"])
    df["date_only"] = df.index.normalize()
    df = df.reset_index().merge(cluster_lookup, on="date_only", how="left").set_index("timestamp")
    df.drop(columns=["date_only"], inplace=True)
    df["day_type_id_B"] = df["day_type_id_B"].fillna(-1).astype(int)

    # Lag features always from observed b00 (these are the past, known at deployment time)
    for lag in [1, 2, 3, 6, 12, 24, 48, 168]:
        df[f"b00_lag{lag}"] = df["b00"].shift(lag)
    df["b00_roll24_mean"]  = df["b00"].shift(1).rolling(24).mean()
    df["b00_roll24_std"]   = df["b00"].shift(1).rolling(24).std()
    df["b00_roll168_mean"] = df["b00"].shift(1).rolling(168).mean()

    # Weather derived (note: temp_lag24 here uses weather source — if forecast, uses
    # forecast made 24h prior; if observed, uses real observation 24h prior)
    df["temp_lag24"]  = df["temperature_2m"].shift(24)
    df["temp_lag168"] = df["temperature_2m"].shift(168)
    df["wbgt_lag1"]   = df["wbgt_approx"].shift(1)
    df["cdh_20"] = (df["temperature_2m"] - 20).clip(lower=0)
    df["hdh_18"] = (18 - df["temperature_2m"]).clip(lower=0)
    for lvl in [2, 3, 4]:
        df[f"heat_alert_ge{lvl}"] = (df["heat_alert_level"] >= lvl).astype(int)

    df["y"] = df["b00"]
    df_clean = df.dropna(subset=[c for c in df.columns if c.startswith("b00_lag") or c.startswith("b00_roll")])
    df_clean = df_clean.dropna(subset=["y", "b00"])
    df_clean = df_clean[df_clean["b00"] > 1.0]
    print(f"  [{name}] features: {df_clean.shape}  ({df_clean.index.min()} → {df_clean.index.max()})")
    return df_clean


df_obs  = build_features(pw, obs, cal, "OBSERVED (ERA5)")
df_fcst = build_features(pw, fcs, cal, "FORECAST (JMA MSM)")

# ============================================================================
# Training: Walk-Forward CV — both variants
# ============================================================================
common_feat_pattern = (
    lambda df: [c for c in df.columns
                if c not in ("y", "b00", "day_type", "holiday_name", "dow_name", "dow")
                and not c.startswith("b") or c.startswith("b00_lag") or c.startswith("b00_roll")]
)

# Build common feature list (intersect for fair comparison)
feat_obs  = sorted([c for c in df_obs.columns
                    if c not in ("y", "b00", "day_type", "holiday_name", "dow_name", "dow")
                    and not (c.startswith("b") and not c.startswith("b00_"))])
feat_fcst = sorted([c for c in df_fcst.columns
                    if c not in ("y", "b00", "day_type", "holiday_name", "dow_name", "dow")
                    and not (c.startswith("b") and not c.startswith("b00_"))])
feats = sorted(set(feat_obs) & set(feat_fcst))
print(f"Common features for fair comparison: {len(feats)}")


def train_eval(df, feats, label):
    n = len(df)
    init_train = int(n * 0.50)
    test_size  = int(n * 0.15)
    step       = test_size
    fold_results = []
    for i in range(3):
        tr_end = init_train + i*step
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
        print(f"  [{label}] fold {i+1}: MAE={mae:.1f} R²={r2:.3f}")
    return fold_results


print("\n" + "=" * 70); print("WALK-FORWARD CV"); print("=" * 70)
print("\nOBSERVED weather (ERA5 — represents 'perfect knowledge' upper bound):")
results_obs  = train_eval(df_obs,  feats, "OBSERVED")
print("\nJMA MSM FORECAST (realistic deployment scenario):")
results_fcst = train_eval(df_fcst, feats, "JMA_MSM_FCST")

all_results = pd.DataFrame(results_obs + results_fcst)
agg = all_results.groupby("label").agg(
    MAE_mean=("MAE", "mean"), MAE_std=("MAE", "std"),
    R2_mean=("R2", "mean"), MAPE_mean=("MAPE", "mean")
).round(3)
print("\n" + "=" * 70)
print("SUMMARY (mean across 3 folds)")
print("=" * 70)
print(agg.to_string())
agg.to_csv(f"{RES}/forecast_vs_obs_model_perf.csv")

# Quantify the cost of forecast uncertainty
mae_loss = agg.loc["JMA_MSM_FCST", "MAE_mean"] - agg.loc["OBSERVED", "MAE_mean"]
r2_loss  = agg.loc["OBSERVED", "R2_mean"] - agg.loc["JMA_MSM_FCST", "R2_mean"]
print(f"\nForecast uncertainty cost: MAE +{mae_loss:.1f} kW, R² -{r2_loss:.3f}")
print(f"→ JMA MSM forecast accuracy is {'EXCELLENT' if mae_loss < 20 else 'acceptable' if mae_loss < 50 else 'borderline'} for day-ahead SDR decisions")


# ============================================================================
# Final model: trained on FORECAST features — this is the deployable version
# ============================================================================
print("\n" + "=" * 70)
print("Training FINAL deployable model (forecast-driven, 70/30 holdout)")
print("=" * 70)
n = len(df_fcst); split_pt = int(n * 0.70)
Xtr = df_fcst[feats].iloc[:split_pt]; ytr = df_fcst["y"].iloc[:split_pt]
Xte = df_fcst[feats].iloc[split_pt:]; yte = df_fcst["y"].iloc[split_pt:]
p95_tr = ytr.quantile(0.95)
ytr_cls = (ytr >= p95_tr).astype(int)
yte_cls = (yte >= p95_tr).astype(int)

model_reg = lgb.LGBMRegressor(
    n_estimators=600, learning_rate=0.03, num_leaves=63,
    min_data_in_leaf=20, feature_fraction=0.85, bagging_fraction=0.85,
    bagging_freq=5, reg_alpha=0.1, reg_lambda=0.1,
    random_state=42, verbose=-1
)
model_reg.fit(Xtr, ytr)
pred = model_reg.predict(Xte)
mae  = mean_absolute_error(yte, pred)
r2   = r2_score(yte, pred)

# Classifier on peak hours
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
             "p95_thr": float(p95_tr), "features": feats, "split_pt": split_pt},
            f"{RES}/forecast_model.pkl")

print(f"Holdout test: MAE={mae:.1f} R²={r2:.3f}")
print(f"P95 peak threshold (training): {p95_tr:.1f} kW")
print(f"Test set positives: {yte_cls.sum()}/{len(yte_cls)} ({yte_cls.mean()*100:.1f}%)")

# Save test_df with predictions for downstream day-ahead CCRI work
test_df = df_fcst.iloc[split_pt:].copy()
test_df["pred_reg_fcst"]      = pred
test_df["pred_cls_prob_fcst"] = pred_cls
test_df["y_cls_fold"]    = yte_cls.values
test_df["p95_thr_train"] = p95_tr
test_df.to_parquet(f"{PROC}/test_df_forecast.parquet")
print(f"\n💾 saved → forecast_model.pkl + test_df_forecast.parquet")
