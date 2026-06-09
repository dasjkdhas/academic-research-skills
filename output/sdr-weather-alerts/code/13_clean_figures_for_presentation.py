"""Regenerate clean figures for conference presentation.

Removes invalid data (b00 == 0 sensor-offline periods) before plotting:
  - 2025-09-24: 14 zero hours (partial-day maintenance)
  - 2025-10-27 to 10-31: 5 full zero days (sensor offline)

Produces presentation-ready clean figures (PNG, 150 dpi) under figures_pres/.
"""
import os, json, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import seaborn as sns
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_pres"
os.makedirs(FIG, exist_ok=True)

# Yamaguchi University style
YU_NAVY   = "#003B71"   # ヤマグチブルー
YU_ORANGE = "#E78A00"
YU_GREEN  = "#2D9C5A"
YU_RED    = "#C8102E"
YU_GREY   = "#5A5A5A"

plt.rcParams.update({
    "font.family": ["IPAGothic", "DejaVu Sans"],
    "axes.titlesize": 12, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 8.5, "axes.grid": True,
    "grid.alpha": 0.3, "grid.linewidth": 0.5,
    "axes.edgecolor": "#333333",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False,
})

def reindex_continuous(s, full_idx):
    """Reindex series to continuous hourly range; gaps become NaN so plotted lines break."""
    return s.reindex(full_idx)

# ============================================================================
# Load + clean data
# ============================================================================
df_obs = pd.read_parquet(f"{PROC}/features.parquet")
fcs    = pd.read_csv(f"{PROC}/jma_forecast_hourly.csv",
                     parse_dates=["timestamp"]).set_index("timestamp")
msm_cols = [c for c in fcs.columns if c.endswith("_msm")]
fcs_msm  = fcs[msm_cols].copy()
fcs_msm.columns = [c.replace("_msm", "") for c in fcs_msm.columns]
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

# Build Architecture C dataset (lag obs + current forecast)
df = df_obs.copy()
df[WX_VARS] = fcs_msm[WX_VARS].reindex(df.index)
df["temp_lag24"]  = df_obs["temperature_2m"].shift(24).reindex(df.index)
df["temp_lag168"] = df_obs["temperature_2m"].shift(168).reindex(df.index)
df["wbgt_lag1"]   = df_obs["wbgt_approx"].shift(1).reindex(df.index)
df["cdh_20"] = (df["temperature_2m"] - 20).clip(lower=0)
df["hdh_18"] = (18 - df["temperature_2m"]).clip(lower=0)
for lvl in [2, 3, 4]:
    df[f"heat_alert_ge{lvl}"] = (df["heat_alert_level"] >= lvl).astype(int)
df = df.dropna(subset=["temp_lag168", "b00_lag168", "y"])

# DROP invalid rows (sensor offline → b00 = 0)
n_before = len(df)
df = df[df["b00"] > 0]
df = df[df["y"] > 0]
n_after = len(df)
print(f"Cleaned: dropped {n_before - n_after} invalid rows "
      f"({(n_before - n_after) / n_before * 100:.1f}%)")
print(f"Valid range: {df.index.min()} → {df.index.max()}, n={n_after} hours")


# Feature subset
def safe_features(df, min_lag=24):
    feats = []
    for c in df.columns:
        if c in ("y","y_peak","b00","day_type","holiday_name","dow_name","dow"): continue
        if c.startswith("b") and not c.startswith("b00_"): continue
        if c.startswith("b00_lag"):
            lag = int(c.replace("b00_lag",""))
            if lag < min_lag: continue
            feats.append(c); continue
        if c == "b00_roll24_mean" or c == "b00_roll24_std": continue
        if c == "b00_roll168_mean": feats.append(c); continue
        feats.append(c)
    return feats

feats = safe_features(df, 24)
print(f"Features: {len(feats)}")

# Train on cleaned data
n = len(df); split_pt = int(n * 0.70)
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
mape = (np.abs((yte - pred) / yte)).mean() * 100
print(f"\nHybrid (cleaned) holdout: MAE={mae:.1f} RMSE={rmse:.1f} R²={r2:.3f} MAPE={mape:.2f}%")

# Build other architectures' baselines on the SAME cleaned data
def build_archA():
    d = df_obs.copy()
    d["temp_lag24"]  = d["temperature_2m"].shift(24)
    d["temp_lag168"] = d["temperature_2m"].shift(168)
    d["wbgt_lag1"]   = d["wbgt_approx"].shift(1)
    d["cdh_20"] = (d["temperature_2m"] - 20).clip(lower=0)
    d["hdh_18"] = (18 - d["temperature_2m"]).clip(lower=0)
    for lvl in [2,3,4]: d[f"heat_alert_ge{lvl}"] = (d["heat_alert_level"] >= lvl).astype(int)
    return d.dropna(subset=["temp_lag168","b00_lag168","y"])

def build_archB():
    d = df_obs.copy()
    d[WX_VARS] = fcs_msm[WX_VARS].reindex(d.index)
    d["temp_lag24"]  = d["temperature_2m"].shift(24)
    d["temp_lag168"] = d["temperature_2m"].shift(168)
    d["wbgt_lag1"]   = d["wbgt_approx"].shift(1)
    d["cdh_20"] = (d["temperature_2m"] - 20).clip(lower=0)
    d["hdh_18"] = (18 - d["temperature_2m"]).clip(lower=0)
    for lvl in [2,3,4]: d[f"heat_alert_ge{lvl}"] = (d["heat_alert_level"] >= lvl).astype(int)
    return d.dropna(subset=["temp_lag168","b00_lag168","y"])

dfA = build_archA(); dfA = dfA[dfA["b00"]>0]; dfA = dfA[dfA["y"]>0]
dfB = build_archB(); dfB = dfB[dfB["b00"]>0]; dfB = dfB[dfB["y"]>0]
common_idx = dfA.index.intersection(dfB.index).intersection(df.index)
dfA = dfA.loc[common_idx]; dfB = dfB.loc[common_idx]; dfC = df.loc[common_idx]

def train_holdout(d, label):
    n = len(d); sp = int(n*0.70)
    f = [x for x in feats if x in d.columns]
    Xtr, ytr = d[f].iloc[:sp], d["y"].iloc[:sp]
    Xte, yte = d[f].iloc[sp:], d["y"].iloc[sp:]
    m = lgb.LGBMRegressor(n_estimators=800, learning_rate=0.03, num_leaves=63,
                          min_data_in_leaf=20, feature_fraction=0.85, bagging_fraction=0.85,
                          bagging_freq=5, reg_alpha=0.1, reg_lambda=0.1, random_state=42, verbose=-1)
    m.fit(Xtr, ytr); p = m.predict(Xte)
    return {"arch": label, "MAE": mean_absolute_error(yte, p),
            "RMSE": np.sqrt(mean_squared_error(yte, p)),
            "R2": r2_score(yte, p),
            "MAPE": (np.abs((yte - p) / yte)).mean() * 100,
            "test_idx": Xte.index, "y_true": yte.values, "y_pred": p, "model": m}

print("\nRe-training all architectures on cleaned data...")
hA = train_holdout(dfA, "A_Obs")
hB = train_holdout(dfB, "B_Forecast")
hC = train_holdout(dfC, "C_Hybrid")
for h in [hA, hB, hC]:
    print(f"  {h['arch']:12s}  MAE={h['MAE']:.1f}  RMSE={h['RMSE']:.1f}  "
          f"R²={h['R2']:.3f}  MAPE={h['MAPE']:.2f}%")

# Determine P80/P95 from CLEAN training portion
y_tr_full = df["b00"].iloc[:split_pt + 168]
p50 = y_tr_full.quantile(0.50)
p80 = y_tr_full.quantile(0.80)
p95 = y_tr_full.quantile(0.95)
print(f"\nThresholds: P50={p50:.0f} P80={p80:.0f} P95={p95:.0f} kW")

# ============================================================================
# FIGURE 1 (pres_01_overview): Daily load profile by month — clean
# ============================================================================
df_clean_raw = pd.read_csv(f"{PROC}/campus_power_hourly.csv",
                           parse_dates=["timestamp"]).set_index("timestamp")
df_clean_raw = df_clean_raw[df_clean_raw["b00"] > 0]
df_clean_raw["hour"] = df_clean_raw.index.hour
df_clean_raw["month"] = df_clean_raw.index.month
monthly = df_clean_raw.groupby(["month", "hour"])["b00"].mean().unstack(0)

fig, ax = plt.subplots(figsize=(8, 4.5))
month_colors = {7: YU_RED, 8: YU_ORANGE, 9: YU_GREEN, 10: YU_NAVY}
month_labels = {7: "7月 (盛夏)", 8: "8月 (盛夏)", 9: "9月 (晩夏)", 10: "10月 (秋)"}
for m in [7, 8, 9, 10]:
    if m in monthly.columns:
        ax.plot(monthly.index, monthly[m], lw=2.2, color=month_colors[m],
                label=month_labels[m], marker="o", markersize=4)
ax.set_xlabel("時刻"); ax.set_ylabel("平均負荷 b00 (kW)")
ax.set_title("月別 時刻別 平均消費電力 (b00)")
ax.set_xticks(range(0, 24, 3))
ax.legend(loc="upper right")
plt.tight_layout()
plt.savefig(f"{FIG}/pres_01_overview_daily_profile.png", dpi=150)
plt.close()
print("✓ pres_01_overview_daily_profile.png")


# ============================================================================
# FIGURE 2 (pres_02_load_temp_scatter): Temperature vs Load scatter
# ============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.5))
sc = ax.scatter(df_clean_raw["b00"].index.map(
        lambda t: df_obs["temperature_2m"].get(t, np.nan)),
    df_clean_raw["b00"], c=df_clean_raw["hour"], cmap="viridis",
    s=8, alpha=0.5)
ax.axhline(p80, ls="--", color=YU_ORANGE, lw=1.3, label=f"P80閾値 ({p80:.0f} kW)")
ax.axhline(p95, ls=":",  color=YU_RED,    lw=1.3, label=f"P95閾値 ({p95:.0f} kW)")
ax.set_xlabel("外気温 (°C)"); ax.set_ylabel("時間負荷 b00 (kW)")
ax.set_title("外気温と消費電力の関係")
cbar = plt.colorbar(sc, ax=ax, label="時刻")
ax.legend(loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{FIG}/pres_02_temp_load_scatter.png", dpi=150)
plt.close()
print("✓ pres_02_temp_load_scatter.png")


# ============================================================================
# FIGURE 3 (pres_03_arch_compare): Architecture comparison bar chart
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(9, 4))
arch_labels = ["A: 観測のみ\n(理論上限)", "B: 予報のみ\n(実運用時)", "C: ハイブリッド\n(本研究)"]
mae_vals    = [hA["MAE"], hB["MAE"], hC["MAE"]]
r2_vals     = [hA["R2"],  hB["R2"],  hC["R2"]]
colors      = [YU_GREY, YU_RED, YU_NAVY]

ax = axes[0]
bars = ax.bar(arch_labels, mae_vals, color=colors, alpha=0.9, edgecolor="black", linewidth=0.6)
for b, v in zip(bars, mae_vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.7, f"{v:.1f}",
            ha="center", fontsize=10, fontweight="bold")
ax.set_ylabel("MAE (kW) ↓ 低いほど良い")
ax.set_title("予測誤差 MAE の比較")
ax.set_ylim(0, max(mae_vals) * 1.18)

ax = axes[1]
bars = ax.bar(arch_labels, r2_vals, color=colors, alpha=0.9, edgecolor="black", linewidth=0.6)
for b, v in zip(bars, r2_vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.01, f"{v:.3f}",
            ha="center", fontsize=10, fontweight="bold")
ax.set_ylabel("R² ↑ 高いほど良い")
ax.set_title("決定係数 R² の比較")
ax.set_ylim(0.8, 1.0)
plt.tight_layout()
plt.savefig(f"{FIG}/pres_03_arch_compare.png", dpi=150)
plt.close()
print("✓ pres_03_arch_compare.png")


# ============================================================================
# FIGURE 4 (pres_04_holdout_timeseries): Holdout time-series (CLEAN)
# ============================================================================
# Use Architecture C predictions
test_idx = hC["test_idx"]
y_true = pd.Series(hC["y_true"], index=test_idx)
y_pred = pd.Series(hC["y_pred"], index=test_idx)

# Reindex to continuous hourly range so gaps from invalid data break the lines
full_idx = pd.date_range(test_idx.min(), test_idx.max(), freq="h")
y_true_c = reindex_continuous(y_true, full_idx)
y_pred_c = reindex_continuous(y_pred, full_idx)

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(full_idx, y_true_c, lw=1.1, color=YU_NAVY, label="実測 (Actual)", alpha=0.85)
ax.plot(full_idx, y_pred_c, lw=1.1, color=YU_ORANGE,
        label=f"予測 (Predicted, MAE={hC['MAE']:.1f} kW, R²={hC['R2']:.3f})", alpha=0.85)
ax.axhline(p80, ls="--", color=YU_RED, lw=1, alpha=0.7, label=f"P80 ({p80:.0f} kW)")
ax.set_xlabel("日付"); ax.set_ylabel("時間負荷 b00 (kW)")
ax.set_title(f"テスト期間の予測結果 — Architecture C (ハイブリッド)\n"
             f"テスト範囲: {test_idx.min().strftime('%Y-%m-%d')} 〜 {test_idx.max().strftime('%Y-%m-%d')}")
ax.legend(loc="upper right", fontsize=9)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha="center")
plt.tight_layout()
plt.savefig(f"{FIG}/pres_04_holdout_timeseries.png", dpi=150)
plt.close()
print("✓ pres_04_holdout_timeseries.png")


# ============================================================================
# FIGURE 5 (pres_05_scatter_pred_actual): Predicted vs Actual scatter
# ============================================================================
fig, ax = plt.subplots(figsize=(6, 5.5))
ax.scatter(y_true, y_pred, s=12, alpha=0.5, color=YU_NAVY, edgecolor="white", linewidth=0.3)
lo = min(y_true.min(), y_pred.min()) * 0.95
hi = max(y_true.max(), y_pred.max()) * 1.05
ax.plot([lo, hi], [lo, hi], ls="--", color="black", lw=1, alpha=0.6, label="完全予測線 y=x")
ax.axhline(p80, ls=":", color=YU_RED, lw=0.9, alpha=0.7)
ax.axvline(p80, ls=":", color=YU_RED, lw=0.9, alpha=0.7)
ax.text(p80 + 5, lo + 30, f"P80={p80:.0f}", fontsize=8, color=YU_RED)
ax.set_xlabel("実測値 (kW)"); ax.set_ylabel("予測値 (kW)")
ax.set_title(f"予測 vs 実測の散布図 \nMAE={hC['MAE']:.1f} kW, R²={hC['R2']:.3f}, MAPE={hC['MAPE']:.2f}%")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_aspect("equal")
ax.legend(loc="upper left", fontsize=9)
plt.tight_layout()
plt.savefig(f"{FIG}/pres_05_pred_vs_actual.png", dpi=150)
plt.close()
print("✓ pres_05_pred_vs_actual.png")


# ============================================================================
# FIGURE 6 (pres_06_shap): Top features SHAP
# ============================================================================
import shap
explainer = shap.TreeExplainer(hC["model"])
X_sample = dfC[hC["model"].booster_.feature_name()].iloc[split_pt:].sample(
    min(500, len(dfC) - split_pt), random_state=42)
shap_values = explainer.shap_values(X_sample)
mean_abs = np.abs(shap_values).mean(axis=0)
top_n = 10
top_idx = np.argsort(mean_abs)[::-1][:top_n]
feat_names = hC["model"].booster_.feature_name()
top_feats = [feat_names[i] for i in top_idx]
top_vals  = [mean_abs[i] for i in top_idx]

# Translate to Japanese-friendly labels
jp_map = {
    "b00_lag168": "前週同時刻負荷 (lag168h)",
    "b00_lag24":  "前日同時刻負荷 (lag24h)",
    "b00_lag48":  "2日前同時刻負荷",
    "day_type_id_B": "営業日フラグ",
    "temp_lag24": "前日同時刻気温",
    "day_of_year": "年内日付",
    "shortwave_radiation": "日射量 (予報)",
    "hour": "時刻",
    "wbgt_lag1": "前時刻WBGT",
    "dow_hour": "曜日×時刻",
    "hour_cos": "時刻 cos周期",
    "hour_sin": "時刻 sin周期",
    "apparent_temperature": "体感気温 (予報)",
    "temperature_2m": "気温 (予報)",
    "wbgt_approx": "WBGT (予報)",
    "relative_humidity_2m": "湿度 (予報)",
    "cdh_20": "冷房度時 CDH20",
    "hdh_18": "暖房度時 HDH18",
    "month": "月",
    "dow": "曜日",
}
labels = [jp_map.get(f, f) for f in top_feats][::-1]
vals = top_vals[::-1]

fig, ax = plt.subplots(figsize=(8, 4.5))
y_pos = np.arange(len(labels))
bars = ax.barh(y_pos, vals, color=YU_NAVY, alpha=0.85, edgecolor="black", linewidth=0.4)
ax.set_yticks(y_pos); ax.set_yticklabels(labels)
ax.set_xlabel("平均 |SHAP値|  (kW)")
ax.set_title("予測寄与の大きい特徴量 Top 10 (SHAP)")
for b, v in zip(bars, vals):
    ax.text(v + 0.5, b.get_y() + b.get_height()/2, f"{v:.1f}",
            va="center", fontsize=8)
plt.tight_layout()
plt.savefig(f"{FIG}/pres_06_shap_top10.png", dpi=150)
plt.close()
print("✓ pres_06_shap_top10.png")


# ============================================================================
# FIGURE 7 (pres_07_split): Train/Test split visualization
# ============================================================================
fig, ax = plt.subplots(figsize=(11, 3))
all_idx = df.index
tr_idx = all_idx[:split_pt]
te_idx = all_idx[split_pt:]
# Continuous index for gap-aware plotting
full_idx = pd.date_range(all_idx.min(), all_idx.max(), freq="h")
load_clean = df["b00"].reindex(full_idx)
# Build masked series per split
tr_mask = pd.Series(False, index=full_idx); tr_mask.loc[tr_idx] = True
te_mask = pd.Series(False, index=full_idx); te_mask.loc[te_idx] = True
load_tr = load_clean.where(tr_mask); load_te = load_clean.where(te_mask)
ax.plot(full_idx, load_tr, lw=0.5, color=YU_NAVY, alpha=0.7,
        label=f"学習データ {tr_idx.min().strftime('%m/%d')}–{tr_idx.max().strftime('%m/%d')} (n={len(tr_idx)}h)")
ax.plot(full_idx, load_te, lw=0.5, color=YU_ORANGE, alpha=0.85,
        label=f"テストデータ {te_idx.min().strftime('%m/%d')}–{te_idx.max().strftime('%m/%d')} (n={len(te_idx)}h)")
ax.axvline(tr_idx.max(), ls="--", color="black", lw=1.2, alpha=0.6)
ax.text(tr_idx.max(), ax.get_ylim()[1] * 0.95, "  分割点",
        fontsize=9, color="black", va="top")
ax.set_xlabel("日付"); ax.set_ylabel("b00 (kW)")
ax.set_title(f"学習/テスト分割 (時系列 70:30)  —  有効データ: 2025-07-20 〜 2025-10-26")
ax.legend(loc="upper right", fontsize=9)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
plt.tight_layout()
plt.savefig(f"{FIG}/pres_07_train_test_split.png", dpi=150)
plt.close()
print("✓ pres_07_train_test_split.png")


# ============================================================================
# Save cleaned summary for PPT
# ============================================================================
summary = {
    "data_range": f"{df.index.min().date()} → {df.index.max().date()}",
    "n_hours_valid": len(df),
    "n_hours_invalid_dropped": n_before - n_after,
    "train_range": f"{tr_idx.min().date()} → {tr_idx.max().date()}",
    "test_range":  f"{te_idx.min().date()} → {te_idx.max().date()}",
    "n_train": len(tr_idx), "n_test": len(te_idx),
    "thresholds_kW": {"P50": float(p50), "P80": float(p80), "P95": float(p95)},
    "results": {
        "A_Obs":      {"MAE": round(hA["MAE"],1), "RMSE": round(hA["RMSE"],1),
                       "R2": round(hA["R2"],3),  "MAPE": round(hA["MAPE"],2)},
        "B_Forecast": {"MAE": round(hB["MAE"],1), "RMSE": round(hB["RMSE"],1),
                       "R2": round(hB["R2"],3),  "MAPE": round(hB["MAPE"],2)},
        "C_Hybrid":   {"MAE": round(hC["MAE"],1), "RMSE": round(hC["RMSE"],1),
                       "R2": round(hC["R2"],3),  "MAPE": round(hC["MAPE"],2)},
    },
    "top_features": [{"feature": top_feats[i], "label_jp": jp_map.get(top_feats[i], top_feats[i]),
                      "mean_abs_shap": float(top_vals[i])} for i in range(top_n)],
}
with open(f"{RES}/pres_summary.json", "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"\n💾 saved → results/pres_summary.json")
print(f"💾 figures saved to {FIG}/")
