"""Energies-ready figure regeneration (English, Arial, 600 dpi RGB, PNG + SVG).

Strict compliance with MDPI Energies Instructions for Authors:
- English labels throughout (no JP/CN); professional academic phrasing
- Sans-serif font (Arial/Helvetica/Liberation Sans)
- PNG at 600 dpi, RGB; editable SVG with svg.fonttype='none'
- File naming: Figure_N_<descriptor>.png/svg per MDPI convention
- Color-blind safe palette (Wong, Nat Methods 2011 inspired)
- Single & double-column friendly sizing
"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sklearn.linear_model import LinearRegression
import pwlf
from scipy.stats import pearsonr

# ---- MDPI Energies-compliant style ----
plt.rcParams.update({
    "font.family": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "axes.linewidth": 0.8,
    "axes.grid": True, "grid.alpha": 0.3, "grid.linewidth": 0.4,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False,
    "svg.fonttype": "none",      # editable text in SVG
    "pdf.fonttype": 42,
    "savefig.dpi": 600,           # MDPI minimum
    "savefig.bbox": "tight",
    "axes.edgecolor": "#222222",
})

# Color-blind safe palette (Wong 2011)
C = {
    "navy":    "#0072B2",   # blue
    "orange":  "#E69F00",
    "vermillion":"#D55E00",
    "green":   "#009E73",
    "purple":  "#CC79A7",
    "yellow":  "#F0E442",
    "skyblue": "#56B4E9",
    "grey":    "#555555",
}

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_energies_en"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
os.makedirs(FIG, exist_ok=True)
CONTRACT_KW = 2000

# ---- helper: dual-save PNG (600 dpi) + SVG (editable) ----
def save(name):
    plt.savefig(f"{FIG}/{name}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{FIG}/{name}.svg", bbox_inches="tight")
    plt.close()
    print(f"  ✓ {name}.png (600 dpi) + .svg")

def linfit(x, y):
    X = np.asarray(x).reshape(-1,1); y = np.asarray(y)
    m = LinearRegression().fit(X, y); yhat = m.predict(X)
    ss = 1 - ((y - yhat)**2).sum() / ((y - y.mean())**2).sum()
    return float(m.coef_[0]), float(m.intercept_), float(ss)

# ============================================================================
# Load + merge data
# ============================================================================
pw  = pd.read_csv(f"{PROC}/campus_power_hourly_JFY2025.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
ame = pd.read_csv(f"{PROC}/jma_weather_embedded_JFY2025.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
era = pd.read_csv(f"{PROC}/era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
cal = pd.read_csv(f"{PROC}/academic_calendar_JFY2025.csv",
                  parse_dates=["date"])

# English day_type labels
EN_DT = {"上課日":"Class day","週末":"Weekend","祝日":"Public holiday",
         "節假日":"Public holiday","休業":"Vacation",
         "活動日":"Special event","試験期":"Exam closure"}
cal["day_type_en"] = cal["day_type"].map(EN_DT).fillna(cal["day_type"])

df = pw.join(ame[["temperature_2m","precipitation","wind_speed_10m",
                   "wind_direction_10m"]], how="inner").rename(columns={"kwh":"load"})
df = df.join(era[["relative_humidity_2m","apparent_temperature"]], how="inner")
df = df.dropna(subset=["load","temperature_2m"])
df["date"] = df.index.normalize()
df = df.reset_index().merge(cal[["date","day_type_en"]], on="date", how="left").set_index("timestamp")
df = df.rename(columns={"day_type_en":"day_type"})
df["hour"] = df.index.hour; df["month"] = df.index.month
# English season labels
def season_en(m):
    if m in (6,7,8,9): return "Cooling (Jun–Sep)"
    if m in (12,1,2,3): return "Heating (Dec–Mar)"
    return "Transition (Apr–May, Oct–Nov)"
df["season"] = df["month"].map(season_en)
df["rho"] = df["load"] / CONTRACT_KW

# Thermal-comfort indices (ERA5-derived; humidity verified vs AMeDAS at r≈0.99 for T)
T  = df["temperature_2m"].values
RH = df["relative_humidity_2m"].values
es = 6.105 * np.exp(17.27*T / (237.7+T))
e  = (RH/100.0) * es
df["vapor_pressure"] = e
df["WBGT"] = 0.567*T + 0.393*e + 3.94                          # Stull/Bernard
df["T_apparent"] = T + 0.33*e - 0.70*1.5 - 4.0                 # Steadman 1984
def heat_index(Tc, RHv):
    Tf = Tc*9/5 + 32
    HIf = (-42.379 + 2.04901523*Tf + 10.14333127*RHv
           - 0.22475541*Tf*RHv - 0.00683783*Tf**2 - 0.05481717*RHv**2
           + 0.00122874*Tf**2*RHv + 0.00085282*Tf*RHv**2
           - 0.00000199*Tf**2*RHv**2)
    HIf = np.where(Tc<27, Tf, HIf)
    return (HIf - 32)*5/9
df["HI"] = heat_index(T, RH)

print(f"Merged: {len(df):,} valid hours, {df.index.normalize().nunique()} days")

# ============================================================================
# Figure 1: Data availability matrix (Energies-ready, English)
# ============================================================================
DT_ORDER = ["Class day","Exam closure","Special event","Weekend",
            "Public holiday","Vacation"]
SE_ORDER = ["Heating (Dec–Mar)","Transition (Apr–May, Oct–Nov)","Cooling (Jun–Sep)"]
hours_mat = df.pivot_table("load", index="season", columns="day_type",
                            aggfunc="count").reindex(SE_ORDER).reindex(DT_ORDER, axis=1).fillna(0).astype(int)
days_mat = (df.groupby([df.index.normalize(),"season","day_type"]).size()
              .reset_index().groupby(["season","day_type"]).size()
              .unstack(fill_value=0).reindex(SE_ORDER).reindex(DT_ORDER, axis=1).fillna(0).astype(int))

fig, axes = plt.subplots(1, 2, figsize=(7.48, 2.6))   # MDPI double-column = 7.48"
sns.heatmap(hours_mat, annot=True, fmt="d", cmap="Blues", ax=axes[0],
            cbar_kws={"label":"Hours","shrink":0.9}, annot_kws={"size":7})
axes[0].set_title("(a) Hourly samples", fontsize=9, fontweight="bold")
axes[0].set_xlabel("Day type", fontsize=9); axes[0].set_ylabel("Season", fontsize=9)
sns.heatmap(days_mat, annot=True, fmt="d", cmap="Greens", ax=axes[1],
            cbar_kws={"label":"Days","shrink":0.9}, annot_kws={"size":7})
axes[1].set_title("(b) Daily samples", fontsize=9, fontweight="bold")
axes[1].set_xlabel("Day type", fontsize=9); axes[1].set_ylabel("")
for ax in axes:
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=7.5)
    plt.setp(ax.get_yticklabels(), fontsize=7.5)
plt.suptitle(f"Data availability: {len(df):,} hours / {df.index.normalize().nunique()} days "
             f"(of 8,760 annual hours)", fontsize=9.5, y=1.04)
plt.tight_layout(); save("Figure_1_data_availability")

# ============================================================================
# Figure 2: Annual time series (load + temperature)
# ============================================================================
fig, axes = plt.subplots(2, 1, figsize=(7.48, 4.2), sharex=True)
axes[0].plot(df.index, df["load"], color=C["navy"], lw=0.25, alpha=0.85)
axes[0].axhline(CONTRACT_KW, ls="--", color=C["vermillion"], lw=0.8,
                label=f"Contract capacity ({CONTRACT_KW} kW)")
axes[0].set_ylabel("Electricity load (kWh/h)", fontsize=9)
axes[0].legend(loc="upper right", fontsize=8)
axes[0].set_title("(a) Hourly campus electricity load",
                  fontsize=9.5, fontweight="bold", loc="left")
axes[1].plot(df.index, df["temperature_2m"], color=C["orange"], lw=0.35, alpha=0.9)
axes[1].axhline(0, ls=":", color="black", lw=0.4, alpha=0.5)
axes[1].set_ylabel("Air temperature (°C)", fontsize=9)
axes[1].set_xlabel("Date", fontsize=9)
axes[1].set_title("(b) AMeDAS Ube observation",
                  fontsize=9.5, fontweight="bold", loc="left")
axes[1].xaxis.set_major_locator(mdates.MonthLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7.5)
plt.tight_layout(); save("Figure_2_annual_timeseries")

# ============================================================================
# Figure 3: Day-type distribution + diurnal profiles
# ============================================================================
dtcol = {"Class day":C["vermillion"],"Exam closure":C["purple"],
         "Special event":C["orange"],"Weekend":C["navy"],
         "Public holiday":C["grey"],"Vacation":C["green"]}
fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.2))
sns.boxplot(data=df, x="day_type", y="load", order=DT_ORDER,
            palette=[dtcol[d] for d in DT_ORDER], ax=axes[0], showfliers=False,
            linewidth=0.7)
axes[0].axhline(CONTRACT_KW, ls="--", color=C["vermillion"], lw=0.7, alpha=0.6,
                label=f"Capacity {CONTRACT_KW} kW")
axes[0].set_xlabel("Day type", fontsize=9); axes[0].set_ylabel("Load (kWh/h)", fontsize=9)
axes[0].set_title("(a) Load distribution by day type", fontsize=9.5,
                  fontweight="bold", loc="left")
axes[0].legend(fontsize=8)
plt.setp(axes[0].get_xticklabels(), rotation=30, ha="right", fontsize=7.5)

for dt in DT_ORDER:
    g = df[df["day_type"]==dt].groupby("hour")["load"].mean()
    if len(g): axes[1].plot(g.index, g.values, "o-", ms=3, lw=1.5,
                            color=dtcol[dt], label=dt)
axes[1].set_xlabel("Hour of day", fontsize=9); axes[1].set_ylabel("Mean load (kWh/h)", fontsize=9)
axes[1].set_title("(b) Mean diurnal profile by day type", fontsize=9.5,
                  fontweight="bold", loc="left")
axes[1].legend(fontsize=7, ncol=2, loc="upper left")
axes[1].set_xticks(range(0,24,3))
plt.tight_layout(); save("Figure_3_daytype_profiles")

# ============================================================================
# Figure 4: Season-separated energy signatures (hourly + daily)
# ============================================================================
scol = {"Cooling (Jun–Sep)":C["vermillion"],
        "Transition (Apr–May, Oct–Nov)":C["green"],
        "Heating (Dec–Mar)":C["navy"]}
daily = (df.groupby("date")
           .agg(load=("load","mean"), temp=("temperature_2m","mean"),
                T_app=("T_apparent","mean"), WBGT=("WBGT","mean"),
                HI=("HI","mean"),
                season=("season", lambda s: s.iloc[0]),
                day_type=("day_type", lambda s: s.iloc[0]))
           .dropna())

fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.6))
seas_res = {}
for s in SE_ORDER:
    sub = df[df["season"]==s]
    if not len(sub): continue
    sl, ic, r2 = linfit(sub["temperature_2m"].values, sub["load"].values)
    seas_res[s] = {"hourly":{"slope":round(sl,2),"r2":round(r2,3),"n_hours":int(len(sub))}}
    axes[0].scatter(sub["temperature_2m"], sub["load"], s=1.5, alpha=0.12, color=scol[s])
    xx = np.linspace(sub["temperature_2m"].min(), sub["temperature_2m"].max(), 50)
    axes[0].plot(xx, sl*xx+ic, color=scol[s], lw=2,
                 label=f"{s}: β={sl:+.1f}, R²={r2:.2f}, n={len(sub):,}")
axes[0].set_xlabel("Air temperature (°C)", fontsize=9)
axes[0].set_ylabel("Hourly load (kWh/h)", fontsize=9)
axes[0].set_title("(a) Hourly resolution", fontsize=9.5, fontweight="bold", loc="left")
axes[0].legend(loc="upper left", fontsize=7)

for s in SE_ORDER:
    sub = daily[daily["season"]==s]
    if len(sub) < 5: continue
    sl, ic, r2 = linfit(sub["temp"].values, sub["load"].values)
    seas_res[s]["daily"] = {"slope":round(sl,2),"r2":round(r2,3),"n_days":int(len(sub))}
    axes[1].scatter(sub["temp"], sub["load"], s=15, alpha=0.55, color=scol[s],
                    edgecolor="white", lw=0.3)
    xx = np.linspace(sub["temp"].min(), sub["temp"].max(), 50)
    axes[1].plot(xx, sl*xx+ic, color=scol[s], lw=2,
                 label=f"{s}: β={sl:+.1f}, R²={r2:.2f}, n={len(sub)} d")
axes[1].set_xlabel("Daily mean air temperature (°C)", fontsize=9)
axes[1].set_ylabel("Daily mean load (kWh/h)", fontsize=9)
axes[1].set_title("(b) Daily resolution (ASHRAE convention)",
                  fontsize=9.5, fontweight="bold", loc="left")
axes[1].legend(loc="upper left", fontsize=7)
plt.suptitle("Season-stratified energy signatures", fontsize=10, y=1.03)
plt.tight_layout(); save("Figure_4_seasonal_signatures")

# ============================================================================
# Figure 5: Cooling season × day_type signatures (the key RQ3 result)
# ============================================================================
cool_h = df[df["season"]=="Cooling (Jun–Sep)"]
cool_d = daily[daily["season"]=="Cooling (Jun–Sep)"]
key_dt = ["Class day","Weekend","Vacation"]
fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.6))
rq3 = {}
for dt in key_dt:
    sub_h = cool_h[cool_h["day_type"]==dt]
    sub_d = cool_d[cool_d["day_type"]==dt]
    if len(sub_h) < 30: continue
    c = dtcol[dt]
    sl_h, ic_h, r2_h = linfit(sub_h["temperature_2m"].values, sub_h["load"].values)
    sl_d, ic_d, r2_d = linfit(sub_d["temp"].values, sub_d["load"].values)
    rq3[dt] = {"hourly":{"slope":round(sl_h,2),"r2":round(r2_h,3),"n":int(len(sub_h))},
               "daily" :{"slope":round(sl_d,2),"r2":round(r2_d,3),"n":int(len(sub_d))}}
    axes[0].scatter(sub_h["temperature_2m"], sub_h["load"], s=1.5, alpha=0.15, color=c)
    xx = np.linspace(sub_h["temperature_2m"].min(), sub_h["temperature_2m"].max(), 40)
    axes[0].plot(xx, sl_h*xx+ic_h, color=c, lw=2,
                 label=f"{dt}: β={sl_h:+.1f}, R²={r2_h:.2f}, n={len(sub_h):,}")
    axes[1].scatter(sub_d["temp"], sub_d["load"], s=20, alpha=0.6, color=c,
                    edgecolor="white", lw=0.3)
    xx = np.linspace(sub_d["temp"].min(), sub_d["temp"].max(), 40)
    axes[1].plot(xx, sl_d*xx+ic_d, color=c, lw=2,
                 label=f"{dt}: β={sl_d:+.1f}, R²={r2_d:.2f}, n={len(sub_d)} d")
for ax in axes:
    ax.set_xlabel("Air temperature (°C)", fontsize=9)
    ax.set_ylabel("Load (kWh/h)", fontsize=9)
axes[0].set_title("(a) Hourly resolution", fontsize=9.5, fontweight="bold", loc="left")
axes[1].set_title("(b) Daily resolution", fontsize=9.5, fontweight="bold", loc="left")
axes[0].legend(loc="upper left", fontsize=7); axes[1].legend(loc="upper left", fontsize=7)
plt.suptitle("Calendar modulation of cooling-season temperature sensitivity",
             fontsize=10, y=1.03)
plt.tight_layout(); save("Figure_5_cooling_by_daytype")

# ============================================================================
# Figure 6: Cooling-season signatures using thermal-comfort indices
# ============================================================================
indices = [("temp","Dry-bulb T",C["navy"]),
           ("T_app","Apparent T (Steadman 1984)",C["orange"]),
           ("WBGT","WBGT (Stull/Bernard)",C["vermillion"]),
           ("HI","Heat Index (Rothfusz 1990)",C["purple"])]
fig, axes = plt.subplots(2, 2, figsize=(7.48, 5.5))
res_idx = {}
for ax, (col, lbl, c) in zip(axes.flat, indices):
    x = cool_d[col].values; y = cool_d["load"].values
    sl, ic, r2 = linfit(x, y)
    res_idx[col] = {"slope":round(sl,2),"r2":round(r2,3),"n":int(len(x))}
    ax.scatter(x, y, s=15, alpha=0.55, color=c, edgecolor="white", lw=0.3)
    xx = np.linspace(x.min(), x.max(), 50)
    ax.plot(xx, sl*xx+ic, color=c, lw=2.2)
    ax.set_xlabel(f"Daily mean {lbl} (°C)", fontsize=8.5)
    ax.set_ylabel("Daily load (kWh/h)", fontsize=8.5)
    ax.set_title(f"{lbl}: β={sl:+.1f} kWh/h/°C, R²={r2:.3f}, n={len(x)}",
                 fontsize=9, color=c, fontweight="bold")
plt.suptitle("Cooling-season signature using thermal-comfort indices",
             fontsize=10, y=1.02)
plt.tight_layout(); save("Figure_6_comfort_indices")

# ============================================================================
# Figure 7: Balance-point temperature as building-physics quantity
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.6))
ax = axes[0]
balance_pts = {}
for dt in key_dt:
    sub = daily[(daily["day_type"]==dt) &
                (daily["season"].isin(["Cooling (Jun–Sep)","Transition (Apr–May, Oct–Nov)"]))]
    if len(sub) < 25: continue
    s = sub.sort_values("temp")
    m = pwlf.PiecewiseLinFit(s["temp"].values, s["load"].values); m.fit(2)
    bp = float(m.fit_breaks[1])
    bload = float(m.predict([bp])[0])
    balance_pts[dt] = {"T_balance_C":round(bp,1),
                       "cooling_slope":round(float(m.slopes[1]),2),
                       "base_load_kWh_h":round(bload,0),
                       "n_days":int(len(sub))}
    c = dtcol[dt]
    ax.scatter(sub["temp"], sub["load"], s=14, alpha=0.4, color=c)
    xx = np.linspace(s["temp"].min(), s["temp"].max(), 100)
    ax.plot(xx, m.predict(xx), color=c, lw=2.2,
            label=f"{dt}: T_bal = {bp:.1f} °C, baseload = {bload:.0f} kWh/h")
ax.set_xlabel("Daily mean air temperature (°C)", fontsize=9)
ax.set_ylabel("Daily mean load (kWh/h)", fontsize=9)
ax.set_title("(a) Balance-point identification", fontsize=9.5,
             fontweight="bold", loc="left")
ax.legend(loc="upper left", fontsize=7)

ax = axes[1]; ax.axis("off")
bp_list = [v["T_balance_C"] for v in balance_pts.values()]
delta_bp = max(bp_list) - min(bp_list)
explanation = (
"Building-physics interpretation\n"
"\n"
"  T_balance = T_set − (Q_int + Q_sol) / UA\n"
"\n"
"  T_set : indoor setpoint (≈ 28 °C, Cool Biz)\n"
"  Q_int : internal heat gains (occupants,\n"
"          equipment, lighting)\n"
"  Q_sol : solar gains through envelope\n"
"  UA    : building heat-loss coefficient\n"
"\n"
"Observed balance points\n"
)
for dt, v in balance_pts.items():
    explanation += f"  {dt:<10s} : {v['T_balance_C']} °C  (n={v['n_days']} d)\n"
explanation += (
f"\nΔT_balance = {delta_bp:.1f} °C (max − min)\n"
"→ Quantifies occupant-driven internal-gain\n"
"  contribution at constant building UA.\n"
)
ax.text(0.02, 0.98, explanation, transform=ax.transAxes, va="top",
        family="monospace", fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#F4F6FA",
                  edgecolor=C["navy"], linewidth=1.0))
plt.suptitle("Balance-point temperature as a building-physics quantity",
             fontsize=10, y=1.02)
plt.tight_layout(); save("Figure_7_balance_point")

# ============================================================================
# Figure 8: Same-WBGT load excess (internal-heat-gain evidence)
# ============================================================================
cool_act = cool_h[cool_h["WBGT"] >= 22].copy()
bins = np.arange(22, 31, 1.0)
cool_act["wbin"] = pd.cut(cool_act["WBGT"], bins=bins)
piv = (cool_act.groupby(["wbin","day_type"], observed=False)["load"].mean()
              .unstack().reindex(["Class day","Weekend","Vacation"], axis=1))
centers = [iv.mid for iv in piv.index if isinstance(iv, pd.Interval)]
fig, ax = plt.subplots(figsize=(7.48, 3.4))
for dt in ["Class day","Weekend","Vacation"]:
    if dt in piv.columns:
        ax.plot(centers, piv[dt].values, "o-", ms=6, lw=2, color=dtcol[dt],
                label=f"{dt}")
# annotate gap at the central bin
if "Class day" in piv.columns and "Weekend" in piv.columns:
    for x, c_load, w_load in zip(centers, piv["Class day"].values, piv["Weekend"].values):
        if not (np.isnan(c_load) or np.isnan(w_load)):
            gap = c_load - w_load
            if abs(gap) > 80:
                ax.annotate(f"+{gap:.0f}", xy=(x, (c_load+w_load)/2), fontsize=7,
                            color=C["grey"], ha="left", va="center")
                ax.annotate("", xy=(x, c_load), xytext=(x, w_load),
                            arrowprops=dict(arrowstyle="<->", color=C["grey"], lw=0.6))
ax.set_xlabel("WBGT bin (°C)", fontsize=9)
ax.set_ylabel("Mean hourly load (kWh/h)", fontsize=9)
ax.set_title("Excess load under matched WBGT (proxy for occupant internal heat gains)",
             fontsize=9.5, fontweight="bold")
ax.legend(loc="upper left", fontsize=8)
plt.tight_layout(); save("Figure_8_internal_heat_gains")

# ============================================================================
# Figure 9: Capacity risk concentration in (temperature × day_type) space
# ============================================================================
df["tbin"] = pd.cut(df["temperature_2m"], bins=np.arange(-4, 38, 3))
rmat = (df.pivot_table("rho", index="day_type", columns="tbin",
                        aggfunc="mean", observed=False)
          .reindex(DT_ORDER))
fig, ax = plt.subplots(figsize=(7.48, 2.8))
sns.heatmap(rmat, annot=True, fmt=".2f", cmap="YlOrRd", vmin=0, vmax=0.9,
            cbar_kws={"label":"Mean ρ = L/C","shrink":0.85},
            ax=ax, linewidths=0.3, annot_kws={"size":7.5})
ax.set_xlabel("Air-temperature bin (°C)", fontsize=9)
ax.set_ylabel("Day type", fontsize=9)
ax.set_title(f"Capacity-risk ratio ρ in (temperature × day type) space "
             f"(contract = {CONTRACT_KW} kW)", fontsize=9.5, fontweight="bold")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=7.5)
plt.setp(ax.get_yticklabels(), fontsize=7.5)
plt.tight_layout(); save("Figure_9_risk_concentration")

# ============================================================================
# Figure 10: rho time-series with risk-tier thresholds
# ============================================================================
fig, ax = plt.subplots(figsize=(7.48, 2.8))
ax.plot(df.index, df["rho"], color=C["navy"], lw=0.25, alpha=0.75)
for thr, col, lbl in [(0.50, C["yellow"], "Watch (0.50)"),
                       (0.70, C["orange"], "High (0.70)"),
                       (0.85, C["vermillion"], "Critical (0.85)")]:
    ax.axhline(thr, ls="--", color=col, lw=0.7, label=lbl)
ax.set_ylabel("ρ = Load / Capacity", fontsize=9)
ax.set_xlabel("Date", fontsize=9)
ax.set_title(f"Capacity-risk ratio ρ over the fiscal year "
             f"(max = {df['rho'].max():.3f}; contract = {CONTRACT_KW} kW)",
             fontsize=9.5, fontweight="bold")
ax.legend(loc="upper right", fontsize=8)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7.5)
plt.tight_layout(); save("Figure_10_rho_timeseries")

# ============================================================================
# Persist all results in one JSON
# ============================================================================
out = {
    "metadata":{
        "valid_hours": int(len(df)),
        "valid_days":  int(df.index.normalize().nunique()),
        "period":      f"{df.index.min().date()} to {df.index.max().date()}",
        "contract_kW": CONTRACT_KW,
        "site":        "Yamaguchi University Tokiwa Campus, Ube, Japan",
    },
    "season_signature": {k:v for k,v in seas_res.items()},
    "cooling_by_daytype": rq3,
    "cooling_by_index": res_idx,
    "balance_points": balance_pts,
    "risk": {
        "max_rho": float(df["rho"].max()),
        "P95_rho": float(df["rho"].quantile(0.95)),
        "critical_hours": int((df["rho"]>=0.85).sum()),
        "high_hours":     int((df["rho"]>=0.70).sum()),
        "critical_by_daytype": df[df["rho"]>=0.85]["day_type"].value_counts().to_dict(),
        "high_by_daytype":     df[df["rho"]>=0.70]["day_type"].value_counts().to_dict(),
    }
}
with open(f"{RES}/energies_paper_results.json","w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n💾 {RES}/energies_paper_results.json")
print("\n=== KEY RESULTS ===")
for k,v in out.items():
    if k!="metadata":
        print(f"-- {k} --"); print(json.dumps(v, ensure_ascii=False, indent=2)[:600])
