"""Nature-style figure generation: all 10 figures rebuilt to Nature submission spec.

Specifications enforced:
- White background, no chart frame (only left + bottom spines, 0.5 pt)
- No grid (or extremely subtle alpha=0.06 for heatmaps only)
- Sans-serif Liberation Sans / Helvetica / Arial
- Tol's muted color-blind-safe palette (low saturation)
- Tick marks pointing outward, short (length=2.5, width=0.5)
- Legends: frameon=False, small, placed to avoid data overlap
- Panel labels: bold italic 'a', 'b' top-left
- Figure widths: 89 mm (single col) = 3.5", 120 mm (1.5 col) = 4.72",
                 183 mm (double col) = 7.20"
- Export: PNG 600 dpi + SVG with svg.fonttype='none' (text remains editable)
"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
import seaborn as sns
from sklearn.linear_model import LinearRegression
import pwlf

# ---------- NATURE STYLE ----------
plt.rcParams.update({
    "font.family": ["Liberation Sans", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 7,
    "axes.titlesize": 7.5,
    "axes.labelsize": 7,
    "axes.labelweight": "regular",
    "axes.linewidth": 0.5,
    "axes.edgecolor": "#222222",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.grid": False,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.pad": 2, "ytick.major.pad": 2,
    "xtick.direction": "out", "ytick.direction": "out",
    "legend.fontsize": 6, "legend.frameon": False,
    "legend.handlelength": 1.4, "legend.handletextpad": 0.5,
    "legend.columnspacing": 0.8, "legend.borderaxespad": 0.3,
    "lines.linewidth": 1.0, "lines.markersize": 3,
    "savefig.dpi": 600, "savefig.bbox": "tight",
    "savefig.facecolor": "white", "figure.facecolor": "white",
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "axes.unicode_minus": False,
})

# Tol's muted color-blind-safe palette
T = {
    "blue":  "#4477AA", "cyan":   "#66CCEE", "green": "#228833",
    "yellow":"#CCBB44", "red":    "#EE6677", "purple":"#AA3377",
    "grey":  "#BBBBBB", "darkgrey":"#555555",
}
DT_COLOR = {"Class day":T["red"], "Weekend":T["blue"], "Vacation":T["green"],
            "Exam closure":T["purple"], "Special event":T["yellow"],
            "Public holiday":T["grey"]}
SE_COLOR = {"Cooling (Jun–Sep)":T["red"],
            "Transition (Apr–May, Oct–Nov)":T["green"],
            "Heating (Dec–Mar)":T["blue"]}

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_nature"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
os.makedirs(FIG, exist_ok=True)
CONTRACT = 2000
W_SINGLE, W_DOUBLE, W_1_5 = 3.5, 7.2, 4.72  # inches

def panel(ax, label, x=-0.18, y=1.03):
    ax.text(x, y, label, transform=ax.transAxes, fontsize=8.5, fontweight="bold",
            fontstyle="italic", va="bottom", ha="left")

def style(ax):
    """Apply Nature style to a single axes."""
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"):
        ax.spines[s].set_linewidth(0.5); ax.spines[s].set_color("#222222")
    ax.tick_params(direction="out", length=2.5, width=0.5, pad=2)

def save(name):
    plt.savefig(f"{FIG}/{name}.png", dpi=600)
    plt.savefig(f"{FIG}/{name}.svg")
    plt.close()
    print(f"  ✓ {name}")

def linfit(x, y):
    X = np.asarray(x).reshape(-1,1); y = np.asarray(y)
    m = LinearRegression().fit(X, y); yhat = m.predict(X)
    r2 = 1 - ((y - yhat)**2).sum() / ((y - y.mean())**2).sum()
    return float(m.coef_[0]), float(m.intercept_), float(r2)

# ============================================================================
# Load
# ============================================================================
pw  = pd.read_csv(f"{PROC}/campus_power_hourly_JFY2025.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
ame = pd.read_csv(f"{PROC}/jma_weather_embedded_JFY2025.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
era = pd.read_csv(f"{PROC}/era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
cal = pd.read_csv(f"{PROC}/academic_calendar_JFY2025.csv",
                  parse_dates=["date"])
EN_DT = {"上課日":"Class day","週末":"Weekend","祝日":"Public holiday",
         "節假日":"Public holiday","休業":"Vacation",
         "活動日":"Special event","試験期":"Exam closure"}
cal["day_type_en"] = cal["day_type"].map(EN_DT).fillna(cal["day_type"])

df = (pw.join(ame[["temperature_2m","precipitation","wind_speed_10m",
                    "wind_direction_10m"]], how="inner")
        .rename(columns={"kwh":"load"})
        .join(era[["relative_humidity_2m","apparent_temperature"]], how="inner")
        .dropna(subset=["load","temperature_2m"]))
df["date"] = df.index.normalize()
df = df.reset_index().merge(cal[["date","day_type_en"]], on="date", how="left").set_index("timestamp")
df = df.rename(columns={"day_type_en":"day_type"})
df["hour"]=df.index.hour; df["month"]=df.index.month
def season_en(m):
    if m in (6,7,8,9): return "Cooling (Jun–Sep)"
    if m in (12,1,2,3): return "Heating (Dec–Mar)"
    return "Transition (Apr–May, Oct–Nov)"
df["season"] = df["month"].map(season_en)
df["rho"] = df["load"]/CONTRACT

# Comfort indices
T_arr = df["temperature_2m"].values; RH = df["relative_humidity_2m"].values
es = 6.105*np.exp(17.27*T_arr/(237.7+T_arr)); e = (RH/100.0)*es
df["WBGT"] = 0.567*T_arr + 0.393*e + 3.94
df["T_apparent"] = T_arr + 0.33*e - 0.70*1.5 - 4.0
Tf = T_arr*9/5 + 32
HIf = (-42.379+2.04901523*Tf+10.14333127*RH-0.22475541*Tf*RH
       -0.00683783*Tf**2-0.05481717*RH**2+0.00122874*Tf**2*RH
       +0.00085282*Tf*RH**2-0.00000199*Tf**2*RH**2)
HIf = np.where(T_arr<27, Tf, HIf); df["HI"] = (HIf-32)*5/9

# Daily aggregate
daily = (df.groupby("date").agg(load=("load","mean"),
                temp=("temperature_2m","mean"),
                T_app=("T_apparent","mean"), WBGT=("WBGT","mean"), HI=("HI","mean"),
                season=("season", lambda s: s.iloc[0]),
                day_type=("day_type", lambda s: s.iloc[0])).dropna())
print(f"Loaded {len(df):,} hours / {len(daily)} days")

DT_ORDER = ["Class day","Exam closure","Special event","Weekend",
            "Public holiday","Vacation"]
SE_ORDER = ["Heating (Dec–Mar)","Transition (Apr–May, Oct–Nov)","Cooling (Jun–Sep)"]

# ============================================================================
# Figure 1: Data availability matrix (double column)
# ============================================================================
hours_mat = (df.pivot_table("load", index="season", columns="day_type",
              aggfunc="count").reindex(SE_ORDER).reindex(DT_ORDER, axis=1).fillna(0).astype(int))
days_mat = (df.groupby([df.index.normalize(),"season","day_type"]).size()
              .reset_index().groupby(["season","day_type"]).size()
              .unstack(fill_value=0).reindex(SE_ORDER).reindex(DT_ORDER, axis=1).fillna(0).astype(int))

fig, axes = plt.subplots(1, 2, figsize=(W_DOUBLE, 2.4))
for ax, mat, cmap, lbl, ttl in zip(axes,
        [hours_mat, days_mat], ["Blues","Greens"],
        ["Hours","Days"], ["a","b"]):
    sns.heatmap(mat, annot=True, fmt="d", cmap=cmap, ax=ax,
                cbar_kws={"label":lbl,"shrink":0.7,"pad":0.02},
                annot_kws={"size":6, "color":"#222222"},
                linewidths=0.4, linecolor="white", vmin=0)
    ax.set_xlabel("Day type"); ax.set_ylabel("Season" if ttl=="a" else "")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=6)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=6)
    panel(ax, ttl, x=-0.20, y=1.06)
    ax.collections[0].colorbar.ax.tick_params(labelsize=6, length=2, width=0.4)
    ax.collections[0].colorbar.set_label(lbl, fontsize=7)
plt.tight_layout(w_pad=2.0)
save("Figure_1_data_availability")

# ============================================================================
# Figure 2: Annual time series (double column)
# ============================================================================
fig, axes = plt.subplots(2, 1, figsize=(W_DOUBLE, 3.0), sharex=True,
                         gridspec_kw={"hspace":0.25})
ax=axes[0]; style(ax)
ax.plot(df.index, df["load"], color=T["blue"], lw=0.25, alpha=0.85, rasterized=True)
ax.axhline(CONTRACT, ls="--", color=T["red"], lw=0.7,
           label=f"Contract capacity ({CONTRACT} kW)")
ax.set_ylabel("Load (kWh h$^{-1}$)")
ax.legend(loc="upper right", fontsize=6)
ax.yaxis.set_major_locator(MultipleLocator(500))
panel(ax, "a", x=-0.06, y=1.02)

ax=axes[1]; style(ax)
ax.plot(df.index, df["temperature_2m"], color=T["yellow"], lw=0.35,
        alpha=0.95, rasterized=True)
ax.axhline(0, ls=":", color="#222222", lw=0.4, alpha=0.6)
ax.set_ylabel("Air temperature (°C)"); ax.set_xlabel("Date")
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
plt.setp(ax.xaxis.get_majorticklabels(), fontsize=6)
panel(ax, "b", x=-0.06, y=1.02)
save("Figure_2_annual_timeseries")

# ============================================================================
# Figure 3: day_type distribution + diurnal profile (double column)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(W_DOUBLE, 2.6))
ax = axes[0]; style(ax)
bp = ax.boxplot([df[df["day_type"]==d]["load"].values for d in DT_ORDER],
                labels=DT_ORDER, widths=0.55, showfliers=False,
                patch_artist=True,
                medianprops=dict(color="#222222", lw=0.7),
                boxprops=dict(linewidth=0.5, edgecolor="#222222"),
                whiskerprops=dict(linewidth=0.5, color="#222222"),
                capprops=dict(linewidth=0.5, color="#222222"))
for patch, dt in zip(bp["boxes"], DT_ORDER):
    patch.set_facecolor(DT_COLOR[dt]); patch.set_alpha(0.7)
ax.axhline(CONTRACT, ls="--", color=T["red"], lw=0.6, alpha=0.6,
           label=f"Capacity ({CONTRACT} kW)")
ax.set_xlabel("Day type"); ax.set_ylabel("Load (kWh h$^{-1}$)")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=6)
ax.legend(loc="upper right", fontsize=6)
panel(ax, "a")

ax = axes[1]; style(ax)
for dt in DT_ORDER:
    g = df[df["day_type"]==dt].groupby("hour")["load"].mean()
    if len(g): ax.plot(g.index, g.values, "o-", ms=2, lw=1.0,
                       color=DT_COLOR[dt], label=dt)
ax.set_xlabel("Hour of day"); ax.set_ylabel("Mean load (kWh h$^{-1}$)")
ax.set_xticks(range(0,24,4))
ax.legend(loc="upper left", fontsize=5.5, ncol=2, columnspacing=0.6)
panel(ax, "b")
plt.tight_layout(w_pad=2.0)
save("Figure_3_daytype_profiles")

# ============================================================================
# Figure 4: Seasonal signatures (double column)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(W_DOUBLE, 2.8))
seas_res = {}
ax = axes[0]; style(ax)
for s in SE_ORDER:
    sub = df[df["season"]==s]
    if not len(sub): continue
    sl, ic, r2 = linfit(sub["temperature_2m"].values, sub["load"].values)
    seas_res[s] = {"hourly":{"slope":round(sl,2),"r2":round(r2,3),"n":int(len(sub))}}
    ax.scatter(sub["temperature_2m"], sub["load"], s=0.8, alpha=0.10,
               color=SE_COLOR[s], rasterized=True, linewidth=0)
    xx = np.linspace(sub["temperature_2m"].min(), sub["temperature_2m"].max(), 50)
    ax.plot(xx, sl*xx+ic, color=SE_COLOR[s], lw=1.4,
            label=f"{s}\nβ={sl:+.1f}, R²={r2:.2f}")
ax.set_xlabel("Air temperature (°C)"); ax.set_ylabel("Hourly load (kWh h$^{-1}$)")
ax.legend(loc="upper left", fontsize=5.5, handlelength=1.0)
panel(ax, "a")

ax = axes[1]; style(ax)
for s in SE_ORDER:
    sub = daily[daily["season"]==s]
    if len(sub) < 5: continue
    sl, ic, r2 = linfit(sub["temp"].values, sub["load"].values)
    seas_res[s]["daily"] = {"slope":round(sl,2),"r2":round(r2,3),"n":int(len(sub))}
    ax.scatter(sub["temp"], sub["load"], s=10, alpha=0.65, color=SE_COLOR[s],
               edgecolor="white", linewidth=0.3)
    xx = np.linspace(sub["temp"].min(), sub["temp"].max(), 50)
    ax.plot(xx, sl*xx+ic, color=SE_COLOR[s], lw=1.4,
            label=f"{s}\nβ={sl:+.1f}, R²={r2:.2f}")
ax.set_xlabel("Daily mean temperature (°C)"); ax.set_ylabel("Daily load (kWh h$^{-1}$)")
ax.legend(loc="upper left", fontsize=5.5, handlelength=1.0)
panel(ax, "b")
plt.tight_layout(w_pad=2.0)
save("Figure_4_seasonal_signatures")

# ============================================================================
# Figure 5: Cooling x day_type signatures (double column)
# ============================================================================
cool_h = df[df["season"]=="Cooling (Jun–Sep)"]
cool_d = daily[daily["season"]=="Cooling (Jun–Sep)"]
KEY = ["Class day","Weekend","Vacation"]
fig, axes = plt.subplots(1, 2, figsize=(W_DOUBLE, 2.9))
rq3 = {}
ax = axes[0]; style(ax)
for dt in KEY:
    sub = cool_h[cool_h["day_type"]==dt]
    if len(sub) < 30: continue
    c = DT_COLOR[dt]
    sl, ic, r2 = linfit(sub["temperature_2m"].values, sub["load"].values)
    rq3[dt] = {"hourly":{"slope":round(sl,2),"r2":round(r2,3),"n":int(len(sub))}}
    ax.scatter(sub["temperature_2m"], sub["load"], s=0.8, alpha=0.12, color=c,
               rasterized=True, linewidth=0)
    xx = np.linspace(sub["temperature_2m"].min(), sub["temperature_2m"].max(), 40)
    ax.plot(xx, sl*xx+ic, color=c, lw=1.4,
            label=f"{dt}: β={sl:+.1f}, R²={r2:.2f}")
ax.set_xlabel("Air temperature (°C)"); ax.set_ylabel("Hourly load (kWh h$^{-1}$)")
ax.legend(loc="upper left", fontsize=5.5)
panel(ax, "a")

ax = axes[1]; style(ax)
for dt in KEY:
    sub = cool_d[cool_d["day_type"]==dt]
    if len(sub) < 10: continue
    c = DT_COLOR[dt]
    sl, ic, r2 = linfit(sub["temp"].values, sub["load"].values)
    rq3[dt]["daily"] = {"slope":round(sl,2),"r2":round(r2,3),"n":int(len(sub))}
    ax.scatter(sub["temp"], sub["load"], s=14, alpha=0.7, color=c,
               edgecolor="white", linewidth=0.3)
    xx = np.linspace(sub["temp"].min(), sub["temp"].max(), 40)
    ax.plot(xx, sl*xx+ic, color=c, lw=1.4,
            label=f"{dt}: β={sl:+.1f}, R²={r2:.2f}, n={len(sub)}")
ax.set_xlabel("Daily mean temperature (°C)"); ax.set_ylabel("Daily load (kWh h$^{-1}$)")
ax.legend(loc="upper left", fontsize=5.5)
panel(ax, "b")
plt.tight_layout(w_pad=2.0)
save("Figure_5_cooling_by_daytype")

# ============================================================================
# Figure 6: Thermal-comfort index comparison (2x2, double column)
# ============================================================================
indices = [("temp","Dry-bulb T",T["blue"]),
           ("T_app","Apparent T",T["yellow"]),
           ("WBGT","WBGT",T["red"]),
           ("HI","Heat Index",T["purple"])]
fig, axes = plt.subplots(2, 2, figsize=(W_DOUBLE, 4.6))
res_idx = {}
for ax, (col, lbl, c), p in zip(axes.flat, indices, ["a","b","c","d"]):
    style(ax)
    x = cool_d[col].values; y = cool_d["load"].values
    sl, ic, r2 = linfit(x, y)
    res_idx[col] = {"slope":round(sl,2),"r2":round(r2,3),"n":int(len(x))}
    ax.scatter(x, y, s=10, alpha=0.6, color=c, edgecolor="white", linewidth=0.3)
    xx = np.linspace(x.min(), x.max(), 50)
    ax.plot(xx, sl*xx+ic, color=c, lw=1.4)
    ax.set_xlabel(f"Daily mean {lbl} (°C)")
    ax.set_ylabel("Daily load (kWh h$^{-1}$)")
    ax.text(0.04, 0.96, f"β = {sl:+.1f} kWh h$^{{-1}}$ °C$^{{-1}}$\n"
                          f"R² = {r2:.3f}\nn = {len(x)} days",
            transform=ax.transAxes, va="top", ha="left", fontsize=6,
            color="#222222")
    panel(ax, p, x=-0.16)
plt.tight_layout(w_pad=2.0, h_pad=2.0)
save("Figure_6_comfort_indices")

# ============================================================================
# Figure 7: Balance-point (double column, 2 panels)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(W_DOUBLE, 3.0))
ax = axes[0]; style(ax)
balance_pts = {}
for dt in KEY:
    sub = daily[(daily["day_type"]==dt) &
                (daily["season"].isin(["Cooling (Jun–Sep)",
                                        "Transition (Apr–May, Oct–Nov)"]))]
    if len(sub) < 25: continue
    s = sub.sort_values("temp")
    m = pwlf.PiecewiseLinFit(s["temp"].values, s["load"].values); m.fit(2)
    bp = float(m.fit_breaks[1])
    bload = float(m.predict([bp])[0])
    balance_pts[dt] = {"T_balance_C":round(bp,1),
                       "cooling_slope":round(float(m.slopes[1]),2),
                       "base_load":round(bload,0),
                       "n_days":int(len(sub))}
    c = DT_COLOR[dt]
    ax.scatter(sub["temp"], sub["load"], s=10, alpha=0.45, color=c,
               edgecolor="white", linewidth=0.3)
    xx = np.linspace(s["temp"].min(), s["temp"].max(), 100)
    ax.plot(xx, m.predict(xx), color=c, lw=1.4,
            label=f"{dt} (T$_{{bal}}$ = {bp:.1f} °C)")
    ax.axvline(bp, color=c, lw=0.4, ls=":", alpha=0.6)
ax.set_xlabel("Daily mean temperature (°C)"); ax.set_ylabel("Daily load (kWh h$^{-1}$)")
ax.legend(loc="upper left", fontsize=6)
panel(ax, "a")

ax = axes[1]; style(ax)
ax.axis("off")
bp_list = [v["T_balance_C"] for v in balance_pts.values()]
dbp = max(bp_list)-min(bp_list)
txt = ("$\\bf{Building\\!-\\!physics\\ interpretation}$\n"
       "\n"
       "$\\mathit{T}_{bal} = \\mathit{T}_{set} - (\\mathit{Q}_{int}+\\mathit{Q}_{sol}) / \\mathit{UA}$\n"
       "\n"
       "$\\mathit{T}_{set}$ : indoor setpoint (≈ 28 °C, Cool Biz)\n"
       "$\\mathit{Q}_{int}$ : internal heat gains (occupants,\n"
       "       equipment, lighting)\n"
       "$\\mathit{Q}_{sol}$ : solar gains through envelope\n"
       "$\\mathit{UA}$ : building heat-loss coefficient\n"
       "\n"
       "$\\bf{Observed\\ balance\\ points}$\n")
for dt, v in balance_pts.items():
    txt += f"  {dt:<10s}: {v['T_balance_C']:.1f} °C  ({v['n_days']} d)\n"
txt += f"\n  $\\Delta\\mathit{{T}}_{{bal}}$ = {dbp:.1f} °C\n"
txt += "  → quantifies occupant-driven\n     internal heat-gain contrast"
ax.text(0.02, 0.98, txt, transform=ax.transAxes, va="top", ha="left",
        fontsize=7, linespacing=1.4,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white",
                  edgecolor="#222222", linewidth=0.5))
panel(ax, "b", x=-0.02, y=1.02)
plt.tight_layout(w_pad=2.0)
save("Figure_7_balance_point")

# ============================================================================
# Figure 8: Internal heat gains at matched WBGT (single column wide)
# ============================================================================
cool_act = cool_h[cool_h["WBGT"]>=22].copy()
bins = np.arange(22, 31, 1.0)
cool_act["wbin"] = pd.cut(cool_act["WBGT"], bins=bins)
piv = (cool_act.groupby(["wbin","day_type"], observed=False)["load"].mean()
                .unstack().reindex(KEY, axis=1))
centers = [iv.mid for iv in piv.index if isinstance(iv, pd.Interval)]

fig, ax = plt.subplots(figsize=(W_DOUBLE, 2.8))
style(ax)
for dt in KEY:
    if dt in piv.columns:
        v = piv[dt].values
        ax.plot(centers, v, "o-", ms=3.5, lw=1.2, color=DT_COLOR[dt], label=dt)
if "Class day" in piv.columns and "Weekend" in piv.columns:
    for x, c_l, w_l in zip(centers, piv["Class day"].values, piv["Weekend"].values):
        if not (np.isnan(c_l) or np.isnan(w_l)) and (c_l - w_l) > 80:
            mid = (c_l + w_l)/2
            ax.annotate("", xy=(x, c_l), xytext=(x, w_l),
                        arrowprops=dict(arrowstyle="<->", color="#555555", lw=0.5))
            ax.text(x+0.06, mid, f"+{c_l - w_l:.0f}", fontsize=5.5,
                    color="#555555", ha="left", va="center")
ax.set_xlabel("WBGT bin (°C)"); ax.set_ylabel("Mean hourly load (kWh h$^{-1}$)")
ax.legend(loc="upper left", fontsize=6)
save("Figure_8_internal_heat_gains")

# ============================================================================
# Figure 9: Risk concentration heatmap (double column)
# ============================================================================
df["tbin"] = pd.cut(df["temperature_2m"], bins=np.arange(-4, 38, 3))
rmat = (df.pivot_table("rho", index="day_type", columns="tbin",
                        aggfunc="mean", observed=False).reindex(DT_ORDER))
# Format x-tick labels
xlabels = [f"{int(iv.left)}–{int(iv.right)}" if isinstance(iv, pd.Interval) else ""
           for iv in rmat.columns]
fig, ax = plt.subplots(figsize=(W_DOUBLE, 2.3))
sns.heatmap(rmat, annot=True, fmt=".2f", cmap="YlOrRd", vmin=0, vmax=0.9,
            cbar_kws={"label":"ρ = L / C","shrink":0.7,"pad":0.02},
            ax=ax, linewidths=0.4, linecolor="white",
            annot_kws={"size":5.5, "color":"#222222"}, xticklabels=xlabels)
ax.set_xlabel("Air-temperature bin (°C)"); ax.set_ylabel("Day type")
plt.setp(ax.get_xticklabels(), rotation=0, fontsize=5.5)
plt.setp(ax.get_yticklabels(), rotation=0, fontsize=6)
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=6, length=2, width=0.4)
cbar.set_label("ρ = L / C", fontsize=7)
save("Figure_9_risk_concentration")

# ============================================================================
# Figure 10: rho time series (double column)
# ============================================================================
fig, ax = plt.subplots(figsize=(W_DOUBLE, 2.2))
style(ax)
ax.plot(df.index, df["rho"], color=T["blue"], lw=0.22, alpha=0.75,
        rasterized=True)
tier_lines = [(0.50, T["yellow"], "Watch (ρ ≥ 0.50)"),
              (0.70, T["yellow"], "High (ρ ≥ 0.70)"),
              (0.85, T["red"], "Critical (ρ ≥ 0.85)")]
for thr, col, lbl in tier_lines:
    ax.axhline(thr, ls="--", color=col, lw=0.6, label=lbl)
ax.set_ylabel("ρ = Load / Capacity"); ax.set_xlabel("Date")
ax.set_ylim(0, 1.0)
ax.legend(loc="upper right", fontsize=6, ncol=3, columnspacing=1.0)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
plt.setp(ax.xaxis.get_majorticklabels(), fontsize=6)
save("Figure_10_rho_timeseries")

# ============================================================================
# Save results
# ============================================================================
out = {
    "style": "Nature submission spec: white BG, Liberation Sans, "
             "Tol muted palette, no grid/box, left+bottom spines only, "
             "panel labels italic bold, PNG 600 dpi + editable SVG",
    "valid_hours": int(len(df)), "valid_days": int(len(daily)),
    "season_signature": seas_res,
    "cooling_by_daytype": rq3,
    "cooling_by_index": res_idx,
    "balance_points": balance_pts,
    "risk": {
        "max_rho": float(df["rho"].max()),
        "critical_hours": int((df["rho"]>=0.85).sum()),
        "high_hours": int((df["rho"]>=0.70).sum()),
        "critical_by_daytype": df[df["rho"]>=0.85]["day_type"].value_counts().to_dict(),
    }
}
with open(f"{RES}/nature_figures_results.json","w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n💾 results/nature_figures_results.json")
print(f"💾 figures_nature/ — 10 figures × 2 formats (PNG 600 dpi + editable SVG)")
