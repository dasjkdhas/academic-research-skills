"""Core Track-B paper analysis: campus load x temperature x calendar (JFY2025).

Data: campus_power_hourly_JFY2025.csv (7361 valid h) + jma_weather_embedded (AMeDAS Ube)
Calendar: auto-generated (weekend + Japanese national holidays JFY2025 + season).
          (Detailed academic calendar class/exam/vacation pending user input.)

Answers (initial):
  RQ1: annual/weekly/diurnal load structure + weekday vs weekend/holiday
  RQ2: temperature-load response via change-point regression
       -> base load, cooling threshold, heating threshold, sensitivities
  RQ3 (preview): calendar-state-conditioned temperature response
"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pwlf
from scipy.stats import pearsonr

plt.rcParams["font.family"] = ["IPAGothic", "DejaVu Sans"]
plt.rcParams.update({"axes.grid":True,"grid.alpha":0.3,"axes.unicode_minus":False,
                     "axes.spines.top":False,"axes.spines.right":False})
NAVY="#003B71"; RED="#C8102E"; GRN="#2D9C5A"; ORG="#E78A00"; GREY="#5A5A5A"

PROC="/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG ="/home/user/academic-research-skills/output/sdr-weather-alerts/figures_paper"
RES ="/home/user/academic-research-skills/output/sdr-weather-alerts/results"
os.makedirs(FIG, exist_ok=True)

# ---------------------------------------------------------------------------
# Load & merge
# ---------------------------------------------------------------------------
pw = pd.read_csv(f"{PROC}/campus_power_hourly_JFY2025.csv",
                 parse_dates=["timestamp"]).set_index("timestamp")
wx = pd.read_csv(f"{PROC}/jma_weather_embedded_JFY2025.csv",
                 parse_dates=["timestamp"]).set_index("timestamp")
df = pw.join(wx, how="inner")
df = df.rename(columns={"kwh":"load"})
df = df.dropna(subset=["load", "temperature_2m"])
print(f"Merged valid hours: {len(df)}  ({df.index.min()} → {df.index.max()})")

# ---------------------------------------------------------------------------
# Calendar features
# ---------------------------------------------------------------------------
JP_HOLIDAYS_JFY2025 = {  # 2025-04-01 .. 2026-03-31
 "2025-04-29","2025-05-03","2025-05-04","2025-05-05","2025-05-06",
 "2025-07-21","2025-08-11","2025-09-15","2025-09-23","2025-10-13",
 "2025-11-03","2025-11-23","2025-11-24",
 "2026-01-01","2026-01-12","2026-02-11","2026-02-23","2026-03-20",
}
df["hour"]=df.index.hour; df["dow"]=df.index.dayofweek; df["month"]=df.index.month
df["date"]=df.index.normalize()
df["is_weekend"]=(df["dow"]>=5).astype(int)
df["is_holiday"]=df.index.strftime("%Y-%m-%d").isin(JP_HOLIDAYS_JFY2025).astype(int)
def season(m): return ("冬" if m in (12,1,2) else "春" if m in (3,4,5)
                       else "夏" if m in (6,7,8) else "秋")
df["season"]=df["month"].map(season)
# day-type: 平日 / 週末・祝日
df["daytype"]=np.where((df["is_weekend"]==1)|(df["is_holiday"]==1),"週末・祝日","平日")

# ---------------------------------------------------------------------------
# RQ1 — Figure A: month x hour load heatmap
# ---------------------------------------------------------------------------
piv=df.pivot_table("load",index="month",columns="hour",aggfunc="mean")
fig,ax=plt.subplots(figsize=(13,4.6))
sns.heatmap(piv,cmap="YlOrRd",ax=ax,cbar_kws={"label":"平均負荷 (kWh/h)"})
ax.set_title("月 × 時刻 平均キャンパス負荷 — JFY2025",fontweight="bold",color=NAVY)
ax.set_xlabel("時刻"); ax.set_ylabel("月")
plt.tight_layout(); plt.savefig(f"{FIG}/paperA_month_hour_heatmap.png",dpi=150); plt.close()
print("✓ paperA_month_hour_heatmap.png")

# ---------------------------------------------------------------------------
# RQ1 — Figure B: diurnal profile by daytype & season
# ---------------------------------------------------------------------------
fig,axes=plt.subplots(1,2,figsize=(14,5),sharey=True)
for dt,c in [("平日",RED),("週末・祝日",NAVY)]:
    g=df[df["daytype"]==dt].groupby("hour")["load"].mean()
    axes[0].plot(g.index,g.values,marker="o",ms=3,color=c,label=dt,lw=2)
axes[0].set_title("平日 vs 週末・祝日 の日内負荷",fontweight="bold",color=NAVY)
axes[0].set_xlabel("時刻");axes[0].set_ylabel("平均負荷 (kWh/h)");axes[0].legend()
scol={"春":GRN,"夏":RED,"秋":ORG,"冬":NAVY}
for s in ["春","夏","秋","冬"]:
    g=df[df["season"]==s].groupby("hour")["load"].mean()
    axes[1].plot(g.index,g.values,marker="o",ms=3,color=scol[s],label=s,lw=2)
axes[1].set_title("季節別 日内負荷",fontweight="bold",color=NAVY)
axes[1].set_xlabel("時刻");axes[1].legend()
plt.tight_layout(); plt.savefig(f"{FIG}/paperB_diurnal_profiles.png",dpi=150); plt.close()
print("✓ paperB_diurnal_profiles.png")

# ---------------------------------------------------------------------------
# RQ1 — Figure C: load duration curve + weekly boxplot
# ---------------------------------------------------------------------------
fig,axes=plt.subplots(1,2,figsize=(14,5))
ld=df["load"].sort_values(ascending=False).reset_index(drop=True)
axes[0].plot(np.arange(len(ld))/len(ld)*100, ld, color=NAVY, lw=1.5)
p95,p80,p50=ld.quantile(0.05),ld.quantile(0.20),ld.quantile(0.50)  # top percentiles
axes[0].axhline(df["load"].quantile(0.95),ls="--",color=RED,label=f"P95={df['load'].quantile(0.95):.0f}")
axes[0].axhline(df["load"].quantile(0.80),ls="--",color=ORG,label=f"P80={df['load'].quantile(0.80):.0f}")
axes[0].set_xlabel("超過時間比率 (%)");axes[0].set_ylabel("負荷 (kWh/h)")
axes[0].set_title("負荷持続曲線 (LDC)",fontweight="bold",color=NAVY);axes[0].legend()
dow_names=["月","火","水","木","金","土","日"]
sns.boxplot(data=df,x="dow",y="load",ax=axes[1],palette="coolwarm")
axes[1].set_xticklabels(dow_names);axes[1].set_xlabel("曜日");axes[1].set_ylabel("負荷")
axes[1].set_title("曜日別 負荷分布",fontweight="bold",color=NAVY)
plt.tight_layout(); plt.savefig(f"{FIG}/paperC_ldc_weekly.png",dpi=150); plt.close()
print("✓ paperC_ldc_weekly.png")

# ---------------------------------------------------------------------------
# RQ2 — change-point temperature response (whole sample)
# ---------------------------------------------------------------------------
def fit_changepoint(sub, n_seg=3):
    s=sub[["temperature_2m","load"]].dropna().sort_values("temperature_2m")
    x=s["temperature_2m"].values; y=s["load"].values
    if len(x)<200: return None
    m=pwlf.PiecewiseLinFit(x,y); m.fit(n_seg)
    xx=np.linspace(x.min(),x.max(),200); yy=m.predict(xx)
    return dict(model=m,breaks=m.fit_breaks.tolist(),slopes=m.slopes.tolist(),
                xx=xx,yy=yy,x=x,y=y,r2=float(m.r_squared()))

res=fit_changepoint(df,3)
fig,ax=plt.subplots(figsize=(11,6))
samp=df.sample(min(4000,len(df)),random_state=42)
sc=ax.scatter(samp["temperature_2m"],samp["load"],c=samp["hour"],cmap="twilight",
              s=8,alpha=0.45)
plt.colorbar(sc,ax=ax,label="時刻")
ax.plot(res["xx"],res["yy"],color=RED,lw=3,label=f"区分線形回帰 (R²={res['r2']:.3f})")
for b in res["breaks"][1:-1]:
    ax.axvline(b,ls="--",color=GREY,lw=1)
    ax.text(b,ax.get_ylim()[1]*0.97,f"{b:.1f}°C",rotation=90,va="top",fontsize=9,color=GREY)
ax.set_xlabel("気温 (°C)");ax.set_ylabel("負荷 (kWh/h)")
ax.set_title("気温-負荷 応答曲線 (変点回帰) — キャンパス全体 JFY2025",fontweight="bold",color=NAVY)
ax.legend(loc="upper center")
plt.tight_layout(); plt.savefig(f"{FIG}/paperD_temp_response.png",dpi=150); plt.close()
print("✓ paperD_temp_response.png")
print(f"   breaks: {[round(b,1) for b in res['breaks']]}")
print(f"   slopes (kWh/°C): {[round(s,2) for s in res['slopes']]}")

# Identify cooling/heating thresholds: cooling = last break where slope turns positive (high T),
# heating = first break where slope is negative (low T)
breaks=res["breaks"]; slopes=res["slopes"]

# ---------------------------------------------------------------------------
# RQ3 preview — calendar-conditioned response (weekday vs weekend/holiday)
# ---------------------------------------------------------------------------
fig,ax=plt.subplots(figsize=(11,6))
cmap={"平日":RED,"週末・祝日":NAVY}
rq3={}
for dt,c in cmap.items():
    r=fit_changepoint(df[df["daytype"]==dt],3)
    if r is None: continue
    ax.plot(r["xx"],r["yy"],color=c,lw=3,label=f"{dt} (R²={r['r2']:.2f})")
    rq3[dt]={"breaks":[round(b,1) for b in r["breaks"]],
             "slopes":[round(s,2) for s in r["slopes"]]}
ax.set_xlabel("気温 (°C)");ax.set_ylabel("負荷 (kWh/h)")
ax.set_title("校歴状態別 気温応答 (平日 vs 週末・祝日) — RQ3 プレビュー",fontweight="bold",color=NAVY)
ax.legend()
plt.tight_layout(); plt.savefig(f"{FIG}/paperE_calendar_response.png",dpi=150); plt.close()
print("✓ paperE_calendar_response.png")

# ---------------------------------------------------------------------------
# Save numeric summary
# ---------------------------------------------------------------------------
summary={
 "n_valid_hours":int(len(df)),
 "period":f"{df.index.min().date()} → {df.index.max().date()}",
 "load_stats_kwh":{"min":float(df["load"].min()),"max":float(df["load"].max()),
                   "mean":float(df["load"].mean()),
                   "P80":float(df["load"].quantile(0.80)),
                   "P95":float(df["load"].quantile(0.95))},
 "weekday_vs_weekend_mean":{
     "平日":float(df[df["daytype"]=="平日"]["load"].mean()),
     "週末・祝日":float(df[df["daytype"]=="週末・祝日"]["load"].mean())},
 "temp_response_whole":{"breaks_degC":[round(b,2) for b in breaks],
                        "slopes_kwh_per_degC":[round(s,3) for s in slopes],
                        "r2":res["r2"]},
 "temp_response_by_daytype":rq3,
 "season_mean_load":{s:float(df[df["season"]==s]["load"].mean()) for s in ["春","夏","秋","冬"]},
}
with open(f"{RES}/campus_load_analysis_JFY2025.json","w") as f:
    json.dump(summary,f,indent=2,ensure_ascii=False)
df.to_parquet(f"{PROC}/analysis_merged_JFY2025.parquet")
print("\n=== SUMMARY ===")
print(json.dumps(summary,ensure_ascii=False,indent=2))
