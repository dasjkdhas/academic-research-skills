"""Refined Track-B paper analysis with the precise Yamaguchi U academic calendar
and contract capacity = 2000 kW.

Inputs:
  campus_power_hourly_JFY2025.csv     (hourly load, kWh)
  jma_weather_embedded_JFY2025.csv    (AMeDAS Ube)
  academic_calendar_JFY2025.csv       (6-level day_type)
Settings:
  CONTRACT_KW = 2000

Outputs (figures_paper/, results/):
  RQ1: load_by_daytype.png             — boxplots by 6 calendar states
  RQ2: signature_overall.png           — refined daily energy signature
  RQ3: signature_by_daytype.png        — KEY: signature per day_type
       sensitivity_table.csv           — per-daytype thresholds & slopes
  RQ4: rho_timeseries.png              — load-to-capacity ratio time series
       risk_concentration.png          — risk in (temperature, day_type) space
       risk_concentration_hour.png     — risk in (hour, day_type) space
       capacity_risk_summary.json
"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pwlf

plt.rcParams["font.family"] = ["IPAGothic", "DejaVu Sans"]
plt.rcParams.update({"axes.grid":True,"grid.alpha":0.3,"axes.unicode_minus":False,
                     "axes.spines.top":False,"axes.spines.right":False})
NAVY="#003B71"; RED="#C8102E"; GRN="#2D9C5A"; ORG="#E78A00"; GREY="#5A5A5A"; PURP="#8E44AD"

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_paper"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"

CONTRACT_KW = 2000

# ---------- merge data + calendar ----------
pw = pd.read_csv(f"{PROC}/campus_power_hourly_JFY2025.csv",
                 parse_dates=["timestamp"]).set_index("timestamp")
wx = pd.read_csv(f"{PROC}/jma_weather_embedded_JFY2025.csv",
                 parse_dates=["timestamp"]).set_index("timestamp")
cal = pd.read_csv(f"{PROC}/academic_calendar_JFY2025.csv", parse_dates=["date"])

df = pw.join(wx, how="inner").rename(columns={"kwh":"load"})
df = df.dropna(subset=["load", "temperature_2m"])
df["date"] = df.index.normalize()
df = df.merge(cal[["date","day_type","term","event_name"]], on="date", how="left")
df.index = df.index if df.index.name else pd.DatetimeIndex(df.index)
df = df.set_index(pw.index.name or "timestamp", drop=False) if "timestamp" in df.columns else df

# Rebuild a clean DatetimeIndex
df = pw.join(wx, how="inner").rename(columns={"kwh":"load"}).dropna(subset=["load","temperature_2m"])
df["date"] = df.index.normalize()
df = df.reset_index().merge(cal[["date","day_type","term","event_name"]], on="date", how="left").set_index("timestamp")
df["hour"] = df.index.hour; df["month"] = df.index.month
df["rho"] = df["load"] / CONTRACT_KW

print(f"Merged: {len(df)} valid hours, {df.index.min()} → {df.index.max()}")
print("\nday_type hour-counts:")
print(df["day_type"].value_counts())

# ==========================================================================
# RQ1: Load by day_type (boxplots + hourly profile)
# ==========================================================================
order = ["上課日","試験期","活動日","週末","節假日","休業"]
colors_dt = {"上課日":RED,"試験期":PURP,"活動日":ORG,"週末":NAVY,"節假日":GREY,"休業":GRN}

fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
sns.boxplot(data=df, x="day_type", y="load", order=order,
            palette=[colors_dt[d] for d in order], ax=axes[0], showfliers=False)
axes[0].set_xlabel("校歴状態"); axes[0].set_ylabel("時間負荷 (kWh/h)")
axes[0].set_title("校歴状態別 負荷分布", fontweight="bold", color=NAVY)
axes[0].axhline(CONTRACT_KW, ls="--", color=RED, alpha=0.6, label=f"契約容量 {CONTRACT_KW} kW")
axes[0].legend()
for dt in order:
    g = df[df["day_type"]==dt].groupby("hour")["load"].mean()
    axes[1].plot(g.index, g.values, marker="o", ms=3, lw=2, color=colors_dt[dt], label=dt)
axes[1].set_xlabel("時刻"); axes[1].set_ylabel("平均負荷 (kWh/h)")
axes[1].set_title("校歴状態別 日内プロファイル", fontweight="bold", color=NAVY)
axes[1].legend(fontsize=9, ncol=2)
plt.tight_layout(); plt.savefig(f"{FIG}/paperI_load_by_daytype.png", dpi=150); plt.close()
print("✓ paperI_load_by_daytype.png")

# ==========================================================================
# RQ2 + RQ3: Daily energy signature per day_type
# ==========================================================================
daily = df.groupby("date").agg(load=("load","mean"), temp=("temperature_2m","mean"),
                                day_type=("day_type", lambda s: s.iloc[0])).dropna()

def fit_sig(sub, n=3):
    if len(sub) < 30: return None
    s = sub.sort_values("temp")
    m = pwlf.PiecewiseLinFit(s["temp"].values, s["load"].values); m.fit(n)
    xx = np.linspace(s["temp"].min(), s["temp"].max(), 150)
    return {"x":s["temp"].values,"y":s["load"].values,"xx":xx,"yy":m.predict(xx),
            "breaks":m.fit_breaks.tolist(),"slopes":m.slopes.tolist(),
            "r2":float(m.r_squared()),"n":int(len(s))}

# Overall
overall = fit_sig(daily, 3)
print(f"\nOverall daily signature: n={overall['n']}, R²={overall['r2']:.3f}")
print(f"  breaks: {[round(b,1) for b in overall['breaks']]}")
print(f"  slopes: {[round(s,2) for s in overall['slopes']]} kWh/h/°C")

# Per day_type
sig = {}
for dt in order:
    r = fit_sig(daily[daily["day_type"]==dt], 3)
    if r is not None: sig[dt] = r

# Build summary table
rows = [{"day_type":"全体","n_days":overall['n'],
         "heating_thr":round(overall['breaks'][1],1),
         "cooling_thr":round(overall['breaks'][2],1),
         "heating_slope":round(overall['slopes'][0],2),
         "comfort_slope":round(overall['slopes'][1],2),
         "cooling_slope":round(overall['slopes'][2],2),
         "R2":round(overall['r2'],3)}]
for dt, r in sig.items():
    rows.append({"day_type":dt,"n_days":r['n'],
                 "heating_thr":round(r['breaks'][1],1),
                 "cooling_thr":round(r['breaks'][2],1),
                 "heating_slope":round(r['slopes'][0],2),
                 "comfort_slope":round(r['slopes'][1],2),
                 "cooling_slope":round(r['slopes'][2],2),
                 "R2":round(r['r2'],3)})
tab = pd.DataFrame(rows)
tab.to_csv(f"{RES}/sensitivity_table.csv", index=False)
print("\n=== Sensitivity table ===")
print(tab.to_string(index=False))

# Plot signatures together
fig, ax = plt.subplots(figsize=(11, 7))
for dt, r in sig.items():
    if r["n"] < 50: continue
    c = colors_dt[dt]
    ax.scatter(r["x"], r["y"], s=18, alpha=0.35, color=c)
    ax.plot(r["xx"], r["yy"], color=c, lw=2.8,
            label=f"{dt}: 冷房閾値 {r['breaks'][2]:.1f}°C, 感度 {r['slopes'][2]:.1f}, R²={r['r2']:.2f}, n={r['n']}")
ax.set_xlabel("日平均気温 (°C)"); ax.set_ylabel("日平均負荷 (kWh/h)")
ax.set_title("校歴状態別 エネルギー署名 — 制度日历が温度感度を調節 (RQ3)",
             fontweight="bold", color=NAVY, fontsize=12)
ax.legend(loc="upper center", fontsize=9, framealpha=0.95)
plt.tight_layout(); plt.savefig(f"{FIG}/paperJ_signature_refined.png", dpi=150); plt.close()
print("✓ paperJ_signature_refined.png")

# ==========================================================================
# RQ4: Capacity risk — ρ = load / 2000 kW
# ==========================================================================
def risk_tier(r):
    if r >= 0.85: return "Critical"
    if r >= 0.70: return "High"
    if r >= 0.50: return "Watch"
    return "Normal"
df["risk_tier"] = df["rho"].apply(risk_tier)
tier_order = ["Normal","Watch","High","Critical"]
tier_colors = {"Normal":GRN,"Watch":"#FFC107","High":ORG,"Critical":RED}

print(f"\nrho stats: max={df['rho'].max():.3f}, mean={df['rho'].mean():.3f}, P95={df['rho'].quantile(0.95):.3f}")
print(df["risk_tier"].value_counts().reindex(tier_order).to_string())

# 4.1 Time-series of rho with tier shading
fig, ax = plt.subplots(figsize=(15, 4.5))
ax.plot(df.index, df["rho"], color=NAVY, lw=0.4, alpha=0.7)
ax.axhline(0.50, ls="--", color="#FFC107", lw=1, label="Watch (0.50)")
ax.axhline(0.70, ls="--", color=ORG, lw=1, label="High (0.70)")
ax.axhline(0.85, ls="--", color=RED, lw=1, label="Critical (0.85)")
ax.set_ylabel("ρ = 負荷 / 契約容量 (2000 kW)"); ax.set_xlabel("日付")
ax.set_title(f"容量リスク比 ρ の時系列 — 最大 {df['rho'].max():.3f}, P95 {df['rho'].quantile(0.95):.3f}",
             fontweight="bold", color=NAVY)
ax.legend(loc="upper right")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
plt.tight_layout(); plt.savefig(f"{FIG}/paperK_rho_timeseries.png", dpi=150); plt.close()
print("✓ paperK_rho_timeseries.png")

# 4.2 Risk concentration in (temperature_bin, day_type) space
df["tbin"] = pd.cut(df["temperature_2m"], bins=np.arange(-4, 38, 3))
risk_mat = df.pivot_table(values="rho", index="day_type", columns="tbin", aggfunc="mean")
risk_mat = risk_mat.reindex(order)
fig, ax = plt.subplots(figsize=(13, 5))
sns.heatmap(risk_mat, annot=True, fmt=".2f", cmap="YlOrRd", vmin=0, vmax=0.9,
            cbar_kws={"label":"平均 ρ"}, ax=ax, linewidths=0.3)
ax.set_xlabel("気温ビン (°C)"); ax.set_ylabel("校歴状態")
ax.set_title("容量リスク ρ の集中度 — (気温 × 校歴) 空間 (RQ4)",
             fontweight="bold", color=NAVY, fontsize=12)
plt.tight_layout(); plt.savefig(f"{FIG}/paperL_risk_concentration.png", dpi=150); plt.close()
print("✓ paperL_risk_concentration.png")

# 4.3 Hour × day_type concentration
risk_hour = df.pivot_table(values="rho", index="day_type", columns="hour", aggfunc="mean")
risk_hour = risk_hour.reindex(order)
fig, ax = plt.subplots(figsize=(15, 5))
sns.heatmap(risk_hour, cmap="YlOrRd", vmin=0, vmax=0.9,
            cbar_kws={"label":"平均 ρ"}, ax=ax, linewidths=0.2)
ax.set_xlabel("時刻"); ax.set_ylabel("校歴状態")
ax.set_title("ρ の (時刻 × 校歴) 集中度 — 管理窓口の特定 (RQ4)",
             fontweight="bold", color=NAVY)
plt.tight_layout(); plt.savefig(f"{FIG}/paperM_risk_by_hour.png", dpi=150); plt.close()
print("✓ paperM_risk_by_hour.png")

# Summary
summary = {
    "contract_kw": CONTRACT_KW,
    "rho_stats": {"max": float(df["rho"].max()),
                  "mean": float(df["rho"].mean()),
                  "P80": float(df["rho"].quantile(0.80)),
                  "P95": float(df["rho"].quantile(0.95)),
                  "P99": float(df["rho"].quantile(0.99))},
    "tier_hours": {t: int((df["risk_tier"]==t).sum()) for t in tier_order},
    "tier_pct":   {t: float((df["risk_tier"]==t).mean()*100) for t in tier_order},
    "critical_concentration": df[df["risk_tier"]=="Critical"]["day_type"].value_counts().to_dict(),
    "high_or_above": df[df["rho"]>=0.70]["day_type"].value_counts().to_dict(),
    "max_rho_event": {
        "timestamp": str(df["rho"].idxmax()),
        "load": float(df["load"].max()),
        "temp": float(df.loc[df["rho"].idxmax(), "temperature_2m"]),
        "day_type": str(df.loc[df["rho"].idxmax(), "day_type"]),
    }
}
with open(f"{RES}/capacity_risk_summary.json", "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print("\n=== CAPACITY RISK SUMMARY ===")
print(json.dumps(summary, ensure_ascii=False, indent=2))

# Persist refined merged for future steps
df.to_parquet(f"{PROC}/analysis_merged_v2_JFY2025.parquet")
