"""Clean energy signature (ASHRAE-style) for the Track-B paper.

Two rigorous views of the temperature-load response:
  (1) Daily energy signature: daily-mean load vs daily-mean temperature
      + change-point regression -> clean heating/cooling thresholds.
  (2) Temperature-binned response (1C bins) with mean +/- SD bands
      -> non-parametric, assumption-free shape.
Both repeated by calendar state (weekday vs weekend/holiday) for RQ3.
"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pwlf
from scipy.stats import pearsonr

plt.rcParams["font.family"]=["IPAGothic","DejaVu Sans"]
plt.rcParams.update({"axes.grid":True,"grid.alpha":0.3,"axes.unicode_minus":False,
                     "axes.spines.top":False,"axes.spines.right":False})
NAVY="#003B71"; RED="#C8102E"; GRN="#2D9C5A"; ORG="#E78A00"; GREY="#5A5A5A"
PROC="/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG ="/home/user/academic-research-skills/output/sdr-weather-alerts/figures_paper"
RES ="/home/user/academic-research-skills/output/sdr-weather-alerts/results"

df=pd.read_parquet(f"{PROC}/analysis_merged_JFY2025.parquet")

# ---------------------------------------------------------------------------
# (1) Daily energy signature
# ---------------------------------------------------------------------------
daily=df.resample("D").agg(load=("load","mean"),temp=("temperature_2m","mean"),
                           daytype=("daytype",lambda s:s.mode().iloc[0] if len(s.mode()) else "平日"))
daily=daily.dropna()
x=daily["temp"].values; y=daily["load"].values
m=pwlf.PiecewiseLinFit(x,y); m.fit(3)
br=m.fit_breaks; sl=m.slopes
xx=np.linspace(x.min(),x.max(),200); yy=m.predict(xx)
r2=m.r_squared()

# Identify thresholds: heating thr = break where slope changes from - to ~0,
# cooling thr = break where slope changes from ~0 to +.
# With 3 segments we have breaks [min, b1, b2, max] and slopes [s0,s1,s2].
heat_thr=round(br[1],1); cool_thr=round(br[2],1)
heat_slope=round(sl[0],2); base_slope=round(sl[1],2); cool_slope=round(sl[2],2)

fig,ax=plt.subplots(figsize=(10,6.5))
ax.scatter(x,y,s=22,alpha=0.5,color=NAVY,edgecolor="white",linewidth=0.3,label="日 (n=%d)"%len(x))
ax.plot(xx,yy,color=RED,lw=3,label=f"変点回帰 R²={r2:.3f}")
for b in [heat_thr,cool_thr]:
    ax.axvline(b,ls="--",color=GREY,lw=1.2)
ax.text(heat_thr,ax.get_ylim()[0]+20,f" 暖房閾値\n {heat_thr}°C",color=NAVY,fontsize=10,va="bottom")
ax.text(cool_thr,ax.get_ylim()[1]-20,f"冷房閾値\n{cool_thr}°C ",color=RED,fontsize=10,va="top",ha="right")
ax.set_xlabel("日平均気温 (°C)");ax.set_ylabel("日平均負荷 (kWh/h)")
ax.set_title("キャンパス エネルギー署名 (日次) — JFY2025\n"
             f"暖房感度 {heat_slope} / 快適帯 {base_slope} / 冷房感度 {cool_slope} kWh/h per °C",
             fontweight="bold",color=NAVY,fontsize=12)
ax.legend(loc="upper center")
plt.tight_layout(); plt.savefig(f"{FIG}/paperF_energy_signature_daily.png",dpi=150); plt.close()
print("✓ paperF_energy_signature_daily.png")
print(f"   heating_thr={heat_thr}  cooling_thr={cool_thr}  R²={r2:.3f}")
print(f"   slopes: heat={heat_slope} base={base_slope} cool={cool_slope} kWh/h/°C")

# ---------------------------------------------------------------------------
# (2) Temperature-binned response (non-parametric)
# ---------------------------------------------------------------------------
df["tbin"]=pd.cut(df["temperature_2m"],bins=np.arange(-4,38,2))
binned=df.groupby("tbin")["load"].agg(["mean","std","count"]).dropna()
centers=[iv.mid for iv in binned.index]
fig,ax=plt.subplots(figsize=(10,6))
ax.errorbar(centers,binned["mean"],yerr=binned["std"],fmt="o-",color=NAVY,
            ecolor=GREY,elinewidth=1,capsize=3,ms=6,label="平均 ± SD")
ax.axvspan(15,22,alpha=0.12,color=GRN,label="快適帯 (推定)")
ax.set_xlabel("気温 (°C)");ax.set_ylabel("平均負荷 (kWh/h)")
ax.set_title("気温ビン別 平均負荷 (2°C ビン, ノンパラメトリック) — JFY2025",
             fontweight="bold",color=NAVY)
ax.legend()
plt.tight_layout(); plt.savefig(f"{FIG}/paperG_temp_binned.png",dpi=150); plt.close()
print("✓ paperG_temp_binned.png")

# ---------------------------------------------------------------------------
# (3) Calendar-conditioned daily signature (RQ3)
# ---------------------------------------------------------------------------
fig,ax=plt.subplots(figsize=(10,6.5))
rq3={}
for dt,c in [("平日",RED),("週末・祝日",NAVY)]:
    sub=daily[daily["daytype"]==dt]
    if len(sub)<40: continue
    xs=sub["temp"].values; ys=sub["load"].values
    mm=pwlf.PiecewiseLinFit(xs,ys); mm.fit(3)
    xxx=np.linspace(xs.min(),xs.max(),150)
    ax.scatter(xs,ys,s=16,alpha=0.35,color=c)
    ax.plot(xxx,mm.predict(xxx),color=c,lw=3,
            label=f"{dt}: 冷房閾値 {mm.fit_breaks[2]:.1f}°C, 冷房感度 {mm.slopes[2]:.1f}")
    rq3[dt]={"breaks":[round(b,1) for b in mm.fit_breaks],
             "slopes":[round(s,2) for s in mm.slopes],"r2":float(mm.r_squared()),
             "n_days":int(len(sub))}
ax.set_xlabel("日平均気温 (°C)");ax.set_ylabel("日平均負荷 (kWh/h)")
ax.set_title("校歴状態別 エネルギー署名 — 平日は冷房感度が高い (RQ3)",
             fontweight="bold",color=NAVY)
ax.legend(loc="upper center",fontsize=9)
plt.tight_layout(); plt.savefig(f"{FIG}/paperH_calendar_signature.png",dpi=150); plt.close()
print("✓ paperH_calendar_signature.png")

out={
 "daily_energy_signature":{
   "heating_threshold_degC":heat_thr,"cooling_threshold_degC":cool_thr,
   "heating_slope_kwh_per_degC":heat_slope,"comfort_slope":base_slope,
   "cooling_slope_kwh_per_degC":cool_slope,"r2":float(r2),"n_days":int(len(daily))},
 "temp_binned":{str(k):{"mean":round(v["mean"],1),"n":int(v["count"])}
                for k,v in binned.iterrows()},
 "calendar_conditioned":rq3,
}
with open(f"{RES}/energy_signature_JFY2025.json","w") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)
print("\n=== Calendar-conditioned cooling response (RQ3) ===")
for k,v in rq3.items(): print(f"  {k}: cooling_thr={v['breaks'][2]}°C  cooling_slope={v['slopes'][2]}  R²={v['r2']:.2f}  n={v['n_days']}")
