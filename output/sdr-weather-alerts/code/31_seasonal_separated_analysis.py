"""Season-separated temperature response (per deep-research recommendation).

Seasons (Japan/Yamaguchi, month-based):
  冷房期 Cooling : Jun, Jul, Aug, Sep   -> expect positive (cooling) slope
  過渡期 Transit : Apr, May, Oct, Nov    -> expect near-flat (baseload)
  暖房期 Heating : Dec, Jan, Feb, Mar    -> expect negative (heating) slope

Within cooling season we further stratify by calendar state (上課日/週末/休業).
Linear (single-slope) fit per season is appropriate because within a season
the response is largely monotonic, avoiding the V-shape contamination of the
pooled annual model.
"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

plt.rcParams["font.family"]=["IPAGothic","DejaVu Sans"]
plt.rcParams.update({"axes.grid":True,"grid.alpha":0.3,"axes.unicode_minus":False,
                     "axes.spines.top":False,"axes.spines.right":False})
NAVY="#003B71"; RED="#C8102E"; GRN="#2D9C5A"; ORG="#E78A00"; GREY="#5A5A5A"
PROC="/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG ="/home/user/academic-research-skills/output/sdr-weather-alerts/figures_paper"
RES ="/home/user/academic-research-skills/output/sdr-weather-alerts/results"
CONTRACT=2000

pw=pd.read_csv(f"{PROC}/campus_power_hourly_JFY2025.csv",parse_dates=["timestamp"]).set_index("timestamp")
wx=pd.read_csv(f"{PROC}/jma_weather_embedded_JFY2025.csv",parse_dates=["timestamp"]).set_index("timestamp")
cal=pd.read_csv(f"{PROC}/academic_calendar_JFY2025.csv",parse_dates=["date"])
df=pw.join(wx,how="inner").rename(columns={"kwh":"load"}).dropna(subset=["load","temperature_2m"])
df["date"]=df.index.normalize()
df=df.reset_index().merge(cal[["date","day_type"]],on="date",how="left").set_index("timestamp")
df["month"]=df.index.month

def season(m):
    if m in (6,7,8,9):  return "冷房期 (夏)"
    if m in (12,1,2,3): return "暖房期 (冬)"
    return "過渡期 (春秋)"
df["season"]=df["month"].map(season)
scol={"冷房期 (夏)":RED,"過渡期 (春秋)":GRN,"暖房期 (冬)":NAVY}

# daily aggregation
daily=df.groupby("date").agg(load=("load","mean"),temp=("temperature_2m","mean"),
                             season=("season",lambda s:s.iloc[0]),
                             day_type=("day_type",lambda s:s.iloc[0])).dropna()

def linfit(x,y):
    X=x.reshape(-1,1); m=LinearRegression().fit(X,y)
    yhat=m.predict(X); ss=1-((y-yhat)**2).sum()/((y-y.mean())**2).sum()
    return float(m.coef_[0]), float(m.intercept_), float(ss), int(len(x))

# ---- per-season linear signature ----
seas_res={}
fig,ax=plt.subplots(figsize=(11,6.5))
for s in ["暖房期 (冬)","過渡期 (春秋)","冷房期 (夏)"]:
    sub=daily[daily["season"]==s]
    sl,ic,r2,n=linfit(sub["temp"].values,sub["load"].values)
    seas_res[s]={"slope_kwh_per_degC":round(sl,2),"intercept":round(ic,1),
                 "r2":round(r2,3),"n_days":n,
                 "temp_range":[round(sub["temp"].min(),1),round(sub["temp"].max(),1)],
                 "mean_load":round(sub["load"].mean(),1)}
    ax.scatter(sub["temp"],sub["load"],s=20,alpha=0.45,color=scol[s])
    xx=np.linspace(sub["temp"].min(),sub["temp"].max(),50)
    ax.plot(xx,sl*xx+ic,color=scol[s],lw=3,
            label=f"{s}: 傾き {sl:+.1f} kWh/h/°C, R²={r2:.2f}, n={n}")
ax.set_xlabel("日平均気温 (°C)");ax.set_ylabel("日平均負荷 (kWh/h)")
ax.set_title("季節分離 エネルギー署名 — 冷房期(+)/過渡期(~0)/暖房期(−)",
             fontweight="bold",color=NAVY,fontsize=12)
ax.legend(loc="upper center",fontsize=10)
plt.tight_layout(); plt.savefig(f"{FIG}/paperN_seasonal_signatures.png",dpi=150); plt.close()
print("✓ paperN_seasonal_signatures.png")
print("\n=== Per-season linear signature ===")
for s,v in seas_res.items(): print(f"  {s}: slope={v['slope_kwh_per_degC']:+.2f}  R²={v['r2']}  n={v['n_days']}  Trange={v['temp_range']}")

# ---- cooling season x calendar state ----
cool=daily[daily["season"]=="冷房期 (夏)"]
cs_res={}
fig,ax=plt.subplots(figsize=(10,6.5))
cmap={"上課日":RED,"週末":NAVY,"休業":GRN}
for dt,c in cmap.items():
    sub=cool[cool["day_type"]==dt]
    if len(sub)<15: continue
    sl,ic,r2,n=linfit(sub["temp"].values,sub["load"].values)
    cs_res[dt]={"cooling_slope_kwh_per_degC":round(sl,2),"r2":round(r2,3),"n_days":n,
                "mean_load":round(sub["load"].mean(),1)}
    ax.scatter(sub["temp"],sub["load"],s=24,alpha=0.5,color=c)
    xx=np.linspace(sub["temp"].min(),sub["temp"].max(),40)
    ax.plot(xx,sl*xx+ic,color=c,lw=3,label=f"{dt}: 冷房感度 {sl:+.1f}, R²={r2:.2f}, n={n}")
ax.set_xlabel("日平均気温 (°C)");ax.set_ylabel("日平均負荷 (kWh/h)")
ax.set_title("冷房期 × 校歴状態 — 冷房感度の制度的調節 (季節分離後)",
             fontweight="bold",color=NAVY,fontsize=12)
ax.legend(loc="upper left",fontsize=10)
plt.tight_layout(); plt.savefig(f"{FIG}/paperO_cooling_by_daytype.png",dpi=150); plt.close()
print("✓ paperO_cooling_by_daytype.png")
print("\n=== Cooling season x calendar state ===")
for dt,v in cs_res.items(): print(f"  {dt}: cooling_slope={v['cooling_slope_kwh_per_degC']:+.2f}  R²={v['r2']}  n={v['n_days']}")

# ---- seasonal capacity-risk summary ----
df["rho"]=df["load"]/CONTRACT
seas_risk={}
for s in ["冷房期 (夏)","過渡期 (春秋)","暖房期 (冬)"]:
    sub=df[df["season"]==s]
    seas_risk[s]={"mean_rho":round(sub["rho"].mean(),3),"max_rho":round(sub["rho"].max(),3),
                  "P95_rho":round(sub["rho"].quantile(0.95),3),
                  "hours_high_or_above":int((sub["rho"]>=0.70).sum()),
                  "hours_critical":int((sub["rho"]>=0.85).sum())}
print("\n=== Seasonal capacity risk ===")
for s,v in seas_risk.items(): print(f"  {s}: mean ρ={v['mean_rho']}, max={v['max_rho']}, High+={v['hours_high_or_above']}h, Critical={v['hours_critical']}h")

out={"seasons_def":{"冷房期":"Jun-Sep","過渡期":"Apr-May,Oct-Nov","暖房期":"Dec-Mar"},
     "per_season_signature":seas_res,
     "cooling_season_by_daytype":cs_res,
     "seasonal_capacity_risk":seas_risk}
with open(f"{RES}/seasonal_analysis_JFY2025.json","w") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)
print("\n💾 saved → results/seasonal_analysis_JFY2025.json")
