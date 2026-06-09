"""Climate × Energy correlation + PCA analysis.

Outputs presentation-ready figures showing:
  1. Pearson correlation heatmap (weather vs electricity, hourly + daily)
  2. Scatter grid of weather vars vs b00 load
  3. Hour-of-day stratified correlation (controls for diurnal confound)
  4. PCA on standardized weather variables — loadings biplot + variance
  5. Standardized regression coefficients (relative weather impact on b00)
  6. Energy decomposition framework (electricity + gas placeholder)

Uses cleaned data only (b00 > 0). Gas data is not yet available — a
placeholder/framework diagram is generated and the script is structured so
that adding a gas CSV later only requires changing one variable.
"""
import os, json, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr, spearmanr

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_pres"
os.makedirs(FIG, exist_ok=True)

# Yamaguchi style
YU_NAVY   = "#003B71"
YU_NAVY_LT= "#2A5A8E"
YU_ORANGE = "#E78A00"
YU_GREEN  = "#2D9C5A"
YU_RED    = "#C8102E"
YU_GREY   = "#5A5A5A"
LIGHT_BG  = "#F4F6FA"

plt.rcParams.update({
    "font.family": ["IPAGothic", "DejaVu Sans"],
    "axes.titlesize": 12, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 9, "axes.grid": True,
    "grid.alpha": 0.3, "grid.linewidth": 0.5,
    "axes.edgecolor": "#333333",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False,
})

# ============================================================================
# Load + merge electricity & weather
# ============================================================================
power = pd.read_csv(f"{PROC}/campus_power_hourly.csv",
                    parse_dates=["timestamp"]).set_index("timestamp")
weather = pd.read_csv(f"{PROC}/weather_hourly.csv",
                      parse_dates=["timestamp"]).set_index("timestamp")

# Clean: drop sensor-offline rows
power = power[power["b00"] > 0]
df = power.join(weather, how="inner")
df = df.dropna(subset=["b00", "temperature_2m"])
print(f"Joined dataset: {len(df)} hours, "
      f"{df.index.min()} → {df.index.max()}")

# Weather variables with Japanese labels
WEATHER_VARS = {
    "temperature_2m":     "気温 (°C)",
    "relative_humidity_2m":"湿度 (%)",
    "dew_point_2m":       "露点温度 (°C)",
    "apparent_temperature":"体感気温 (°C)",
    "shortwave_radiation":"日射量 (W/m²)",
    "cloud_cover":        "雲量 (%)",
    "surface_pressure":   "気圧 (hPa)",
    "wind_speed_10m":     "風速 (m/s)",
    "precipitation":      "降水量 (mm)",
    "wbgt_approx":        "WBGT (°C)",
}
WX_COLS = list(WEATHER_VARS.keys())

# Add hour-of-day feature
df["hour"] = df.index.hour

# ============================================================================
# FIGURE 1: Pearson + Spearman correlation heatmap (hourly)
# ============================================================================
corr_pearson = {}
corr_spearman = {}
for v in WX_COLS:
    p, _ = pearsonr(df[v], df["b00"])
    s, _ = spearmanr(df[v], df["b00"])
    corr_pearson[v] = p
    corr_spearman[v] = s

cdf = pd.DataFrame({
    "Pearson 線形": [corr_pearson[v] for v in WX_COLS],
    "Spearman 順位": [corr_spearman[v] for v in WX_COLS],
}, index=[WEATHER_VARS[v] for v in WX_COLS])

fig, ax = plt.subplots(figsize=(7.5, 5))
sns.heatmap(cdf, annot=True, fmt=".3f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, cbar_kws={"label": "相関係数"},
            ax=ax, linewidths=0.5, linecolor="white",
            annot_kws={"size": 11, "weight": "bold"})
ax.set_title("気象変数 × 電力消費 b00 の相関係数 (時間別データ)", fontsize=12, pad=10)
ax.set_xlabel("")
plt.tight_layout()
plt.savefig(f"{FIG}/corr_01_pearson_heatmap.png", dpi=150)
plt.close()
print("✓ corr_01_pearson_heatmap.png")

# ============================================================================
# FIGURE 2: Daily aggregated correlation (cleaner climate signal)
# ============================================================================
daily = df.resample("D").agg({
    "b00": "mean",
    **{v: "mean" for v in WX_COLS}
}).dropna()
daily["b00_peak"] = df["b00"].resample("D").max()

corr_daily = {}
for v in WX_COLS:
    p, _ = pearsonr(daily[v], daily["b00"])
    corr_daily[v] = p

corr_daily_peak = {}
for v in WX_COLS:
    p, _ = pearsonr(daily[v], daily["b00_peak"])
    corr_daily_peak[v] = p

ddf = pd.DataFrame({
    "日平均負荷": [corr_daily[v] for v in WX_COLS],
    "日最大負荷": [corr_daily_peak[v] for v in WX_COLS],
}, index=[WEATHER_VARS[v] for v in WX_COLS])

fig, ax = plt.subplots(figsize=(7.5, 5))
sns.heatmap(ddf, annot=True, fmt=".3f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, cbar_kws={"label": "Pearson 相関係数"},
            ax=ax, linewidths=0.5, linecolor="white",
            annot_kws={"size": 11, "weight": "bold"})
ax.set_title("日単位集計後の気象 × 電力 相関係数", fontsize=12, pad=10)
ax.set_xlabel("")
plt.tight_layout()
plt.savefig(f"{FIG}/corr_02_daily_heatmap.png", dpi=150)
plt.close()
print("✓ corr_02_daily_heatmap.png")

# ============================================================================
# FIGURE 3: Scatter grid — 6 representative weather vars vs b00
# ============================================================================
key_vars = ["temperature_2m", "relative_humidity_2m", "shortwave_radiation",
            "wbgt_approx", "cloud_cover", "apparent_temperature"]
fig, axes = plt.subplots(2, 3, figsize=(11, 6.5))
for i, v in enumerate(key_vars):
    ax = axes[i // 3, i % 3]
    sample = df.sample(min(2000, len(df)), random_state=42)
    sc = ax.scatter(sample[v], sample["b00"], c=sample["hour"],
                    cmap="viridis", s=6, alpha=0.45)
    # Trend line (LOWESS-style: simple 2nd-order poly)
    coef = np.polyfit(df[v], df["b00"], 2)
    xs = np.linspace(df[v].min(), df[v].max(), 100)
    ys = np.polyval(coef, xs)
    ax.plot(xs, ys, color=YU_RED, lw=1.8, alpha=0.85, label="二次回帰")
    r = corr_pearson[v]
    ax.set_xlabel(WEATHER_VARS[v]); ax.set_ylabel("b00 (kW)")
    ax.set_title(f"{WEATHER_VARS[v].split(' ')[0]}  (r = {r:+.3f})",
                 fontweight="bold", color=YU_NAVY if abs(r) > 0.3 else YU_GREY)
    ax.legend(loc="upper left", fontsize=8)
fig.suptitle("気象変数 × 電力消費 b00 散布図 (色: 時刻)",
             fontsize=13, fontweight="bold", color=YU_NAVY, y=1.0)
plt.tight_layout()
plt.savefig(f"{FIG}/corr_03_scatter_grid.png", dpi=150)
plt.close()
print("✓ corr_03_scatter_grid.png")

# ============================================================================
# FIGURE 4: Correlation stratified by hour-of-day
# (Controls for diurnal confound: solar correlates with load partly because
#  both peak at noon. Stratifying by hour reveals true climate effect.)
# ============================================================================
hourly_corr = pd.DataFrame(index=range(24), columns=WX_COLS)
for h in range(24):
    sub = df[df["hour"] == h]
    if len(sub) < 10: continue
    for v in WX_COLS:
        r, _ = pearsonr(sub[v], sub["b00"])
        hourly_corr.loc[h, v] = r
hourly_corr = hourly_corr.astype(float).T
hourly_corr.index = [WEATHER_VARS[v] for v in WX_COLS]

fig, ax = plt.subplots(figsize=(11, 5))
sns.heatmap(hourly_corr, annot=False, cmap="RdBu_r", center=0,
            vmin=-0.8, vmax=0.8, cbar_kws={"label": "Pearson 相関係数"},
            ax=ax, linewidths=0.3, linecolor="white")
ax.set_xlabel("時刻 (hour)")
ax.set_ylabel("")
ax.set_title("時刻別に層別化した気象 × b00 相関 (日内変動を除去)",
             fontsize=12, pad=10, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG}/corr_04_hourly_stratified.png", dpi=150)
plt.close()
print("✓ corr_04_hourly_stratified.png")

# ============================================================================
# FIGURE 5: PCA on weather variables — variance explained
# ============================================================================
X = df[WX_COLS].values
scaler = StandardScaler()
Xs = scaler.fit_transform(X)
pca = PCA(n_components=min(6, len(WX_COLS)))
scores = pca.fit_transform(Xs)
explained = pca.explained_variance_ratio_ * 100
cumulative = np.cumsum(explained)

fig, ax = plt.subplots(figsize=(8, 4.5))
xs = np.arange(1, len(explained) + 1)
bars = ax.bar(xs, explained, color=YU_NAVY, alpha=0.85, label="各主成分")
ax2 = ax.twinx()
ax2.plot(xs, cumulative, color=YU_ORANGE, marker="o", lw=2,
         label="累積寄与率")
ax2.axhline(80, ls="--", color=YU_RED, lw=1, alpha=0.7)
ax2.text(len(explained), 82, "80%", color=YU_RED, fontsize=9)
for b, v in zip(bars, explained):
    ax.text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.1f}%",
            ha="center", fontsize=9.5, fontweight="bold")
for x, y in zip(xs, cumulative):
    ax2.text(x, y + 2, f"{y:.0f}%", ha="center",
             fontsize=8.5, color=YU_ORANGE, fontweight="bold")
ax.set_xlabel("主成分 (Principal Component)")
ax.set_ylabel("寄与率 (%)", color=YU_NAVY)
ax2.set_ylabel("累積寄与率 (%)", color=YU_ORANGE)
ax.set_xticks(xs); ax.set_xticklabels([f"PC{i}" for i in xs])
ax.set_title("主成分分析: 各成分の分散説明力", fontsize=12, fontweight="bold")
ax.tick_params(axis="y", labelcolor=YU_NAVY)
ax2.tick_params(axis="y", labelcolor=YU_ORANGE)
ax2.set_ylim(0, 110); ax2.grid(False)
plt.tight_layout()
plt.savefig(f"{FIG}/corr_05_pca_variance.png", dpi=150)
plt.close()
print("✓ corr_05_pca_variance.png")

# ============================================================================
# FIGURE 6: PCA loadings heatmap (PC1-PC3) + correlation with b00
# ============================================================================
loadings = pd.DataFrame(pca.components_[:3].T,
                        index=[WEATHER_VARS[v] for v in WX_COLS],
                        columns=[f"PC{i+1} ({explained[i]:.1f}%)" for i in range(3)])

# Correlation of each PC with b00 (signed)
pc_b00_corr = []
for i in range(3):
    r, _ = pearsonr(scores[:, i], df["b00"].values)
    pc_b00_corr.append(r)

fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2),
                         gridspec_kw={"width_ratios": [2.0, 1.0]})
ax = axes[0]
sns.heatmap(loadings, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, cbar_kws={"label": "loading (係数)"},
            ax=ax, linewidths=0.4, linecolor="white",
            annot_kws={"size": 10})
ax.set_title("主成分の構成 (どの気象変数が各PCを作るか)",
             fontsize=11, fontweight="bold")
ax.set_xlabel("")

ax = axes[1]
pc_labels = [f"PC{i+1}\n({explained[i]:.1f}%)" for i in range(3)]
colors = [YU_NAVY if abs(c) > 0.3 else YU_GREY for c in pc_b00_corr]
bars = ax.bar(pc_labels, pc_b00_corr, color=colors, alpha=0.9,
              edgecolor="black", linewidth=0.6)
for b, v in zip(bars, pc_b00_corr):
    ax.text(b.get_x() + b.get_width()/2,
            v + (0.02 if v >= 0 else -0.04),
            f"{v:+.3f}", ha="center", fontsize=10, fontweight="bold")
ax.axhline(0, color="black", lw=0.6)
ax.set_ylabel("Pearson r (PC vs b00)")
ax.set_title("各主成分と電力 b00 の相関", fontsize=11, fontweight="bold")
ax.set_ylim(-1, 1)
plt.tight_layout()
plt.savefig(f"{FIG}/corr_06_pca_loadings.png", dpi=150)
plt.close()
print("✓ corr_06_pca_loadings.png")

# ============================================================================
# FIGURE 7: Standardized regression coefficients (relative importance)
# Uses CORE meteorological inputs only (drops derived vars apparent_temp,
# dew_point, WBGT) to avoid multicollinearity that destabilizes β values.
# ============================================================================
CORE_VARS = ["temperature_2m", "relative_humidity_2m", "shortwave_radiation",
             "cloud_cover", "surface_pressure", "wind_speed_10m", "precipitation"]
X_core = df[CORE_VARS].values
Xc_s = StandardScaler().fit_transform(X_core)
y = df["b00"].values
y_s = (y - y.mean()) / y.std()
reg = LinearRegression()
reg.fit(Xc_s, y_s)
betas = reg.coef_
order = np.argsort(np.abs(betas))[::-1]
beta_labels = [WEATHER_VARS[CORE_VARS[i]] for i in order]
beta_vals   = [betas[i] for i in order]

fig, ax = plt.subplots(figsize=(8, 5))
colors = [YU_RED if v < 0 else YU_NAVY for v in beta_vals]
bars = ax.barh(np.arange(len(beta_vals))[::-1], beta_vals,
               color=colors, alpha=0.88,
               edgecolor="black", linewidth=0.5)
for b, v in zip(bars, beta_vals):
    # Always place label outside the bar, on the side away from zero
    offset = 0.015 if v >= 0 else -0.015
    ax.text(v + offset, b.get_y() + b.get_height()/2,
            f"{v:+.3f}", va="center",
            ha="left" if v >= 0 else "right",
            fontsize=10, fontweight="bold")
ax.set_yticks(np.arange(len(beta_vals))[::-1]); ax.set_yticklabels(beta_labels)
ax.axvline(0, color="black", lw=0.6)
# Add margin to avoid overlap with y-tick labels
xlo = min(beta_vals) - 0.07
xhi = max(beta_vals) + 0.07
ax.set_xlim(xlo, xhi)
ax.set_xlabel("標準化回帰係数 β  (正: 増, 負: 減)")
ax.set_title("各気象変数の電力 b00 への寄与度 (重回帰の標準化β)\n"
             "  ※ 7変数のみ — 派生変数(体感気温・WBGT等)は除外し多重共線性を回避",
             fontsize=11.5, fontweight="bold", color=YU_NAVY)
legend_elements = [
    mpatches.Patch(color=YU_NAVY, label="正の影響 (↑値→電力↑)"),
    mpatches.Patch(color=YU_RED,  label="負の影響 (↑値→電力↓)"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)
r2_full = reg.score(Xc_s, y_s)
ax.text(0.02, 0.02, f"R² = {r2_full:.3f}\n(7変数のみで電力分散の{r2_full*100:.0f}%を説明)",
        transform=ax.transAxes, fontsize=9.5,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=LIGHT_BG,
                  edgecolor=YU_NAVY, alpha=0.9))
plt.tight_layout()
plt.savefig(f"{FIG}/corr_07_standardized_beta.png", dpi=150)
plt.close()
print("✓ corr_07_standardized_beta.png  (core vars, no multicollinearity)")


# ============================================================================
# FIGURE 8: Energy framework — electricity (have) + gas (placeholder)
# ============================================================================
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")

def fbox(x, y, w, h, label, sub, fc, ec, tc="white"):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                         linewidth=1.5, edgecolor=ec, facecolor=fc, alpha=0.92)
    ax.add_patch(box)
    ax.text(x + w/2, y + h*0.65, label, ha="center", va="center",
            fontsize=12, fontweight="bold", color=tc)
    ax.text(x + w/2, y + h*0.28, sub, ha="center", va="center",
            fontsize=9, color=tc, style="italic")

# Climate sources
fbox(0.3, 4.3, 1.9, 1.2, "気象観測\n(ERA5)", "気温/湿度/日射", YU_NAVY, YU_NAVY)
fbox(0.3, 2.7, 1.9, 1.2, "気象予報\n(JMA MSM)", "5km, +39h", YU_NAVY_LT, YU_NAVY_LT)
fbox(0.3, 1.1, 1.9, 1.2, "AMeDAS 観測", "(将来追加)", YU_GREY, YU_GREY,
     tc="white")

# Center: correlation analysis box
fbox(3.0, 2.5, 2.5, 1.6, "相関分析\n+ PCA", "本スライド\nの内容", YU_ORANGE, YU_ORANGE)

# Right: energy targets
fbox(6.3, 4.3, 2.0, 1.2, "電力消費", "(✓ 取得済)", YU_GREEN, YU_GREEN)
fbox(6.3, 2.7, 2.0, 1.2, "都市ガス消費", "(将来追加)", YU_GREY, YU_GREY)
fbox(6.3, 1.1, 2.0, 1.2, "総エネルギー", "= 電力 + ガス×換算", YU_NAVY, YU_NAVY)

# Outputs
fbox(8.6, 2.5, 1.3, 1.6, "翌日\n予測モデル", "+ SDR判断", YU_RED, YU_RED)

# Arrows
arrow_kw = dict(arrowstyle="->", color="#555555", lw=1.5,
                connectionstyle="arc3,rad=0")
ax.annotate("", xy=(3.0, 3.3), xytext=(2.2, 4.9), arrowprops=arrow_kw)
ax.annotate("", xy=(3.0, 3.3), xytext=(2.2, 3.3), arrowprops=arrow_kw)
ax.annotate("", xy=(3.0, 3.3), xytext=(2.2, 1.7), arrowprops=arrow_kw)
ax.annotate("", xy=(6.3, 3.3), xytext=(5.5, 3.3), arrowprops=arrow_kw)
ax.annotate("", xy=(8.6, 3.3), xytext=(7.5, 3.3), arrowprops=arrow_kw)

# Title + note
ax.text(5, 5.75, "気象 × エネルギー 解析フレームワーク",
        ha="center", fontsize=14, fontweight="bold", color=YU_NAVY)
ax.text(5, 0.25,
        "※ 都市ガス・AMeDAS データは取得待ち。データ受領後、同じパイプラインで再分析可能。",
        ha="center", fontsize=9, color=YU_GREY, style="italic")
plt.tight_layout()
plt.savefig(f"{FIG}/corr_08_framework.png", dpi=150)
plt.close()
print("✓ corr_08_framework.png")


# ============================================================================
# Save summary stats for PPT / discussion
# ============================================================================
summary = {
    "n_hours_analyzed": len(df),
    "data_range": f"{df.index.min().date()} → {df.index.max().date()}",
    "hourly_correlation": {WEATHER_VARS[v]: {
        "pearson":  round(corr_pearson[v], 4),
        "spearman": round(corr_spearman[v], 4),
    } for v in WX_COLS},
    "daily_correlation": {WEATHER_VARS[v]: {
        "mean_load": round(corr_daily[v], 4),
        "peak_load": round(corr_daily_peak[v], 4),
    } for v in WX_COLS},
    "pca": {
        "explained_variance_ratio_pct": [round(e, 2) for e in explained],
        "cumulative_pct": [round(c, 2) for c in cumulative],
        "PC1_top3_loadings": loadings["PC1 ({:.1f}%)".format(explained[0])]
                                .abs().sort_values(ascending=False).head(3).round(3).to_dict(),
        "PC2_top3_loadings": loadings["PC2 ({:.1f}%)".format(explained[1])]
                                .abs().sort_values(ascending=False).head(3).round(3).to_dict(),
        "PC_b00_correlation": {f"PC{i+1}": round(pc_b00_corr[i], 4) for i in range(3)},
    },
    "standardized_beta_top3": {beta_labels[i]: round(beta_vals[i], 4) for i in range(3)},
    "multivariate_R2": round(r2_full, 4),
    "gas_data_status": "not_yet_available — placeholder framework figure generated",
}
with open(f"{RES}/correlation_pca_summary.json", "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"\n💾 saved → results/correlation_pca_summary.json")
print(f"💾 figures saved to {FIG}/  (corr_01 … corr_08)")
print("\n=== Key findings ===")
print(f"Strongest hourly correlation: "
      f"{max(corr_pearson, key=lambda k: abs(corr_pearson[k]))} "
      f"r={corr_pearson[max(corr_pearson, key=lambda k: abs(corr_pearson[k]))]:+.3f}")
print(f"PC1 explains {explained[0]:.1f}% of weather variance; "
      f"PC1-b00 correlation r={pc_b00_corr[0]:+.3f}")
print(f"PC1+PC2+PC3 cumulative: {cumulative[2]:.1f}%")
print(f"Multivariate R² (linear): {r2_full:.3f}")
