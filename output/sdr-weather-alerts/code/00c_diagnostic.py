"""Step 0c: Diagnostic plots and stats for campus_power_hourly data."""
import os, json, warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import seaborn as sns

DATA = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed/campus_power_hourly.csv"
META = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed/campus_power_hourly.meta.json"
FIGD = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures"
os.makedirs(FIGD, exist_ok=True)

CONTRACT = 2000.0
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.05)

df = pd.read_csv(DATA, parse_dates=["timestamp"]).set_index("timestamp")
with open(META) as f:
    meta = json.load(f)
schema_names = meta["columns"]

# Fill small gaps with linear interpolation (≤ 3 hrs)
df = df.interpolate(method="time", limit=3)

y = df["b00"]
print(f"Final shape: {df.shape}, complete fraction: {(1-df.isna().mean().mean())*100:.2f}%")
print(f"y(b00) stats:  mean={y.mean():.1f}  std={y.std():.1f}  p50={y.median():.1f}  p95={y.quantile(.95):.1f}  p99={y.quantile(.99):.1f}  max={y.max():.1f} kW")

# ============================================================================
# Figure 1: Time series with contract capacity line + peak markers
# ============================================================================
fig, ax = plt.subplots(figsize=(15, 4.5))
ax.plot(y.index, y.values, lw=0.4, color="#1f4e79", alpha=0.85)
ax.axhline(CONTRACT, color="red", ls="--", lw=1.2, label=f"Contract capacity ({CONTRACT:.0f} kW)")
ax.axhline(0.9*CONTRACT, color="orange", ls=":", lw=1.0, label="90% threshold")
peak = y[y > 0.9*CONTRACT]
ax.scatter(peak.index, peak.values, color="red", s=8, label=f"Hours > 90% cap (n={len(peak)})", zorder=5)
ax.set_title("Yamaguchi U. Engineering Faculty — HV Main Total Load (2025-07-06 → 2025-10-31)")
ax.set_xlabel("Date"); ax.set_ylabel("Hourly load (kW)")
ax.legend(loc="upper right", framealpha=0.95)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
plt.tight_layout()
plt.savefig(f"{FIGD}/fig01_timeseries_total.png", dpi=130)
plt.close()
print(f"✓ fig01: time series → {peak.shape[0]} hours > 90% capacity, {(y > CONTRACT).sum()} hours > 100%")

# ============================================================================
# Figure 2: Hour-of-day × Day-of-week heatmap (mean load)
# ============================================================================
df2 = pd.DataFrame({"y": y})
df2["hour"] = df2.index.hour
df2["dow"]  = df2.index.dayofweek  # 0=Mon
pivot = df2.groupby(["dow", "hour"])["y"].mean().unstack("hour")
pivot.index = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
fig, ax = plt.subplots(figsize=(12, 3.5))
sns.heatmap(pivot, cmap="rocket_r", ax=ax, cbar_kws={"label":"Mean kW"}, linewidths=0.4)
ax.set_title("Mean hourly load by hour × day-of-week")
ax.set_xlabel("Hour of day"); ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{FIGD}/fig02_heatmap_hour_dow.png", dpi=130)
plt.close()
print(f"✓ fig02: heatmap — peak hour/dow = ({pivot.stack().idxmax()})")

# ============================================================================
# Figure 3: Daily mean + 95% percentile, with weekend shading
# ============================================================================
daily = y.resample("D").agg(["mean","max","min","quantile"])  # quantile defaults to 0.5
daily.columns = ["mean","max","min","median"]
daily["p95_hourly"] = y.resample("D").quantile(0.95)
fig, ax = plt.subplots(figsize=(15, 4))
ax.fill_between(daily.index, daily["min"], daily["max"], alpha=0.25, color="#1f4e79", label="Daily min-max range")
ax.plot(daily.index, daily["mean"], lw=1.5, color="#1f4e79", label="Daily mean")
ax.plot(daily.index, daily["p95_hourly"], lw=1.0, color="#d62728", ls="--", label="Daily P95 (hourly)")
# Highlight weekends
for d in daily.index:
    if d.dayofweek >= 5:
        ax.axvspan(d, d + pd.Timedelta(days=1), alpha=0.07, color="grey", zorder=0)
ax.axhline(CONTRACT, color="red", ls="--", lw=1, alpha=0.6)
ax.set_title("Daily load profile (range, mean, P95)  — grey bands = weekends")
ax.set_xlabel("Date"); ax.set_ylabel("kW"); ax.legend(loc="upper left")
plt.tight_layout()
plt.savefig(f"{FIGD}/fig03_daily_profile.png", dpi=130)
plt.close()
print("✓ fig03: daily profile")

# ============================================================================
# Figure 4: Building contribution stacked area (weekly mean)
# ============================================================================
sub_cols = [c for c in df.columns if c != "b00" and c != "b03"]
weekly = df[sub_cols].resample("W").mean()
fig, ax = plt.subplots(figsize=(15, 5))
ax.stackplot(weekly.index, weekly[sub_cols].T.values,
             labels=[schema_names.get(c, c) for c in sub_cols],
             alpha=0.85)
ax.plot(df["b00"].resample("W").mean().index, df["b00"].resample("W").mean().values,
        color="black", lw=1.6, label="b00 HV total")
ax.set_title("Weekly mean — building contribution stack")
ax.set_xlabel("Date"); ax.set_ylabel("kW")
ax.legend(loc="upper left", ncol=2, fontsize=8, framealpha=0.95)
plt.tight_layout()
plt.savefig(f"{FIGD}/fig04_building_stack.png", dpi=130)
plt.close()
print("✓ fig04: building stack")

# ============================================================================
# Figure 5: Building share of total (boxplot of hourly share)
# ============================================================================
share = df[sub_cols].div(df["b00"].replace(0, np.nan), axis=0).clip(0, 1)
share_means = share.mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(11, 4))
order = share_means.index.tolist()
sns.boxplot(data=share[order]*100, ax=ax, fliersize=2, color="#5a9bd4",
            order=order)
ax.set_xticklabels([schema_names.get(c, c) for c in order], rotation=30, ha="right")
ax.set_ylabel("Share of HV total (%)"); ax.set_title("Per-building share of total load (hourly)")
plt.tight_layout()
plt.savefig(f"{FIGD}/fig05_building_share.png", dpi=130)
plt.close()
print(f"✓ fig05: top-3 buildings by share: {[(schema_names.get(c,c), f'{share[c].mean()*100:.1f}%') for c in share_means.index[:3]]}")

# ============================================================================
# Figure 6: Distribution of hourly load
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].hist(y.dropna(), bins=60, color="#1f4e79", edgecolor="white")
axes[0].axvline(CONTRACT, color="red", ls="--", label=f"Contract {CONTRACT:.0f} kW")
axes[0].axvline(0.9*CONTRACT, color="orange", ls=":", label="90% threshold")
axes[0].set_xlabel("Hourly load (kW)"); axes[0].set_ylabel("Count")
axes[0].set_title("Distribution of hourly load"); axes[0].legend()
# Q-Q vs normal
from scipy import stats
stats.probplot(y.dropna(), dist="norm", plot=axes[1])
axes[1].set_title("Q-Q plot vs normal")
plt.tight_layout()
plt.savefig(f"{FIGD}/fig06_distribution.png", dpi=130)
plt.close()

# ============================================================================
# Figure 7: ACF / PACF
# ============================================================================
try:
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    fig, axes = plt.subplots(2, 1, figsize=(11, 6))
    plot_acf(y.dropna(), lags=168, ax=axes[0])
    axes[0].set_title("ACF (168h = 1 week)")
    plot_pacf(y.dropna(), lags=72, ax=axes[1], method="ywm")
    axes[1].set_title("PACF (72h = 3 days)")
    plt.tight_layout()
    plt.savefig(f"{FIGD}/fig07_acf_pacf.png", dpi=130)
    plt.close()
    print("✓ fig07: ACF/PACF")
except Exception as e:
    print(f"  acf/pacf skipped: {e}")

# ============================================================================
# Stats summary report (markdown)
# ============================================================================
report = []
report.append(f"# Step 0: Data Diagnostic Report\n")
report.append(f"**Site**: Yamaguchi University, Engineering Faculty — Central Electric Room")
report.append(f"**Period**: {df.index.min()} → {df.index.max()}  ({len(df)} hours, ~{len(df)/24:.1f} days)\n")

# Hours over thresholds
n80 = int((y > 0.8*CONTRACT).sum())
n90 = int((y > 0.9*CONTRACT).sum())
n95 = int((y > 0.95*CONTRACT).sum())
n100 = int((y > CONTRACT).sum())
report.append("## 1. Headline numbers\n")
report.append(f"| Statistic | Value |")
report.append(f"|---|---|")
report.append(f"| Hours observed         | {len(y)} |")
report.append(f"| Missing hours (interp) | {int(y.isna().sum())} |")
report.append(f"| Mean load              | {y.mean():.1f} kW |")
report.append(f"| Median load            | {y.median():.1f} kW |")
report.append(f"| Std deviation          | {y.std():.1f} kW |")
report.append(f"| Max load               | **{y.max():.1f} kW** |")
report.append(f"| P95 load               | {y.quantile(.95):.1f} kW |")
report.append(f"| P99 load               | {y.quantile(.99):.1f} kW |")
report.append(f"| Hours > 80% capacity   | {n80} ({n80/len(y)*100:.1f}%) |")
report.append(f"| Hours > 90% capacity   | **{n90}** ({n90/len(y)*100:.1f}%) |")
report.append(f"| Hours > 95% capacity   | {n95} ({n95/len(y)*100:.1f}%) |")
report.append(f"| Hours > 100% capacity  | **{n100}** ({n100/len(y)*100:.2f}%) |\n")

report.append("## 2. Per-building load summary (hourly kW)\n")
report.append("| col | building | mean | min | max | share% |")
report.append("|---|---|---|---|---|---|")
for c in df.columns:
    s = df[c]
    bn = schema_names.get(c, "")
    sh = (s.mean()/y.mean()*100) if c != "b00" else 100
    report.append(f"| {c} | {bn} | {s.mean():.2f} | {s.min():.2f} | {s.max():.2f} | {sh:.1f}% |")
report.append("")

# Stationarity
try:
    from statsmodels.tsa.stattools import adfuller
    adf = adfuller(y.dropna(), autolag="AIC", maxlag=48)
    report.append("## 3. Stationarity (ADF test)\n")
    report.append(f"- ADF statistic = {adf[0]:.4f}")
    report.append(f"- p-value       = {adf[1]:.6f}")
    report.append(f"- Critical 5%   = {adf[4]['5%']:.4f}")
    if adf[1] < 0.05:
        report.append("- **Verdict**: stationary at 5% — direct differencing not strictly required.")
    else:
        report.append("- **Verdict**: non-stationary — consider differencing or detrending.")
    report.append("")
except Exception as e:
    report.append(f"## 3. Stationarity\nADF skipped: {e}\n")

# Sanity
sub_cols = [c for c in df.columns if c not in ("b00", "b03")]
sum_subs = df[sub_cols].sum(axis=1)
diff = df["b00"] - sum_subs
report.append("## 4. Submetering coverage (Tier 1 feasibility check)\n")
report.append(f"- Total b00 = sum(submeters) + residual")
report.append(f"- Mean sum-of-submeters: {sum_subs.mean():.1f} kW")
report.append(f"- Mean residual (unmetered): {diff.mean():.1f} kW")
report.append(f"- **Submetering coverage: {sum_subs.mean()/y.mean()*100:.1f}%**  → Tier 1 SDR decomposition feasible.\n")

# Day-of-week pattern
dow_mean = pivot.mean(axis=1).round(1).to_dict()
report.append("## 5. Day-of-week pattern (mean load by day)\n")
for d, v in dow_mean.items():
    report.append(f"- {d}: {v} kW")
report.append("")
weekday_mean = pivot.iloc[:5].values.mean()
weekend_mean = pivot.iloc[5:].values.mean()
report.append(f"- Weekday vs Weekend ratio: {weekday_mean:.1f} / {weekend_mean:.1f} = **{weekday_mean/weekend_mean:.2f}**\n")

# Peak hours by hour
hour_mean = pivot.mean(axis=0)
peak_hour = int(hour_mean.idxmax())
report.append(f"## 6. Peak hour analysis\n- Peak hour-of-day (average across all weeks): **{peak_hour}:00** ({hour_mean.max():.1f} kW)\n- Min hour-of-day: {hour_mean.idxmin()}:00 ({hour_mean.min():.1f} kW)\n")

# Health flags
report.append("## 7. Data health flags\n")
flags = []
if (y == 0).sum() > 0:
    flags.append(f"⚠ {(y==0).sum()} zero-load hours (likely meter outage)")
if y.isna().sum() > 0:
    flags.append(f"⚠ {int(y.isna().sum())} NaN hours")
if df.duplicated().sum() > 0:
    flags.append(f"⚠ {df.duplicated().sum()} duplicate rows")
if not flags:
    flags.append("✓ No major data-health flags")
for f in flags:
    report.append(f"- {f}")

OUT_MD = "/home/user/academic-research-skills/output/sdr-weather-alerts/results/step0_diagnostic.md"
os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
with open(OUT_MD, "w") as f:
    f.write("\n".join(report))
print(f"\n💾 report → {OUT_MD}")
print(f"💾 figures → {FIGD}/  (fig01..fig07)")
