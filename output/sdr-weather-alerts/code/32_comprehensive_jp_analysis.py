"""キャンパス電力需要の包括分析 — 日本語版 (PNG + SVG)。

修正点 (v3):
  - 用語を日本語ネイティブに統一 (上課日→授業日, 校歴→学年暦, 節假日→祝日)
  - 時別 (hourly) と日次 (daily) の両水準でサンプルサイズを明示
  - データ内訳ヒートマップを追加 (なぜ N が小さいかを可視化)
  - すべての図を PNG + SVG (編集可能) で出力
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

plt.rcParams["font.family"]=["IPAGothic","DejaVu Sans"]
plt.rcParams.update({
    "axes.grid":True, "grid.alpha":0.3, "axes.unicode_minus":False,
    "axes.spines.top":False, "axes.spines.right":False,
    "svg.fonttype": "none",   # SVG でテキストを編集可能に
    "pdf.fonttype": 42,
})

NAVY="#003B71"; RED="#C8102E"; GRN="#2D9C5A"; ORG="#E78A00"; GREY="#5A5A5A"; PURP="#8E44AD"
PROC="/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
FIG ="/home/user/academic-research-skills/output/sdr-weather-alerts/figures_paper_jp"
RES ="/home/user/academic-research-skills/output/sdr-weather-alerts/results"
os.makedirs(FIG, exist_ok=True)
CONTRACT=2000

# 日本語ラベル統一 (中国語混入を排除)
LABEL_MAP = {
 "上課日": "授業日", "校歴": "学年暦", "校歴状態": "日種別",
 "節假日": "祝日", "校園": "キャンパス", "中間期": "中間期 (春・秋)",
}
DAYTYPE_REMAP = {  # 学年暦 CSV 内のラベル名 → ネイティブ日本語
 "上課日":"授業日", "週末":"週末", "祝日":"祝日", "節假日":"祝日",
 "休業":"休業期間", "活動日":"行事日", "試験期":"試験期間",
}

def savefig(name):
    plt.savefig(f"{FIG}/{name}.png", dpi=150, bbox_inches="tight")
    plt.savefig(f"{FIG}/{name}.svg", bbox_inches="tight")
    plt.close()
    print(f"  ✓ {name}.png + .svg")

def linfit(x, y):
    X = np.asarray(x).reshape(-1,1); y = np.asarray(y)
    m = LinearRegression().fit(X, y); yhat = m.predict(X)
    ss = 1 - ((y-yhat)**2).sum() / ((y-y.mean())**2).sum()
    return float(m.coef_[0]), float(m.intercept_), float(ss)

# ===========================================================================
# データ読込
# ===========================================================================
pw=pd.read_csv(f"{PROC}/campus_power_hourly_JFY2025.csv",parse_dates=["timestamp"]).set_index("timestamp")
wx=pd.read_csv(f"{PROC}/jma_weather_embedded_JFY2025.csv",parse_dates=["timestamp"]).set_index("timestamp")
cal=pd.read_csv(f"{PROC}/academic_calendar_JFY2025.csv",parse_dates=["date"])
cal["day_type_jp"] = cal["day_type"].map(DAYTYPE_REMAP).fillna(cal["day_type"])

df=pw.join(wx,how="inner").rename(columns={"kwh":"load"}).dropna(subset=["load","temperature_2m"])
df["date"]=df.index.normalize()
df=df.reset_index().merge(cal[["date","day_type_jp"]], on="date", how="left").set_index("timestamp")
df=df.rename(columns={"day_type_jp":"day_type"})
df["hour"]=df.index.hour; df["month"]=df.index.month; df["dow"]=df.index.dayofweek

def season(m):
    if m in (6,7,8,9): return "冷房期 (6–9月)"
    if m in (12,1,2,3): return "暖房期 (12–3月)"
    return "中間期 (4–5・10–11月)"
df["season"]=df["month"].map(season)
df["rho"]=df["load"]/CONTRACT

print(f"\n総有効時間: {len(df)} 時間")
print(f"対象期間 : {df.index.min()} – {df.index.max()}")

# ===========================================================================
# 図 1: データ可用性マトリクス (N が小さい理由の明示)
# ===========================================================================
order_dt = ["授業日","試験期間","行事日","週末","祝日","休業期間"]
order_se = ["暖房期 (12–3月)","中間期 (4–5・10–11月)","冷房期 (6–9月)"]
hours_mat = df.pivot_table(values="load", index="season", columns="day_type",
                            aggfunc="count").reindex(order_se).reindex(order_dt, axis=1).fillna(0).astype(int)
days_mat = df.groupby([df.index.normalize(),"season","day_type"]).size().reset_index() \
           .groupby(["season","day_type"]).size().unstack(fill_value=0) \
           .reindex(order_se).reindex(order_dt, axis=1).fillna(0).astype(int)

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.heatmap(hours_mat, annot=True, fmt="d", cmap="Blues", ax=axes[0],
            cbar_kws={"label":"有効時間数"})
axes[0].set_title("(a) 季節×日種別 有効時間数 [時間]", fontweight="bold", color=NAVY)
axes[0].set_xlabel("日種別"); axes[0].set_ylabel("季節区分")
sns.heatmap(days_mat, annot=True, fmt="d", cmap="Greens", ax=axes[1],
            cbar_kws={"label":"有効日数"})
axes[1].set_title("(b) 季節×日種別 有効日数 [日]", fontweight="bold", color=NAVY)
axes[1].set_xlabel("日種別"); axes[1].set_ylabel("")
plt.suptitle(f"データ可用性マトリクス — 総 {len(df):,} 時間 / "
             f"{df.index.normalize().nunique()} 日 (年間 8,760 時間中)",
             fontsize=13, fontweight="bold", color=NAVY, y=1.02)
plt.tight_layout(); savefig("F01_data_availability")

# ===========================================================================
# 図 2: 年間時系列 (負荷 + 気温)
# ===========================================================================
fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
axes[0].plot(df.index, df["load"], color=NAVY, lw=0.3, alpha=0.7)
axes[0].axhline(CONTRACT, ls="--", color=RED, lw=1, label=f"契約電力 {CONTRACT} kW")
axes[0].set_ylabel("時別需要電力 [kWh/h]"); axes[0].legend(loc="upper right")
axes[0].set_title("(a) キャンパス需要電力の年間推移", fontweight="bold", color=NAVY)
axes[1].plot(df.index, df["temperature_2m"], color=ORG, lw=0.4, alpha=0.8)
axes[1].axhline(0, ls=":", color=GREY, lw=0.6)
axes[1].set_ylabel("外気温 [°C]"); axes[1].set_xlabel("日付")
axes[1].set_title("(b) AMeDAS 宇部 観測気温", fontweight="bold", color=NAVY)
axes[1].xaxis.set_major_locator(mdates.MonthLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=30, ha="right")
plt.tight_layout(); savefig("F02_annual_timeseries")

# ===========================================================================
# 図 3: 日種別 需要分布 + 日内プロファイル
# ===========================================================================
dtcol={"授業日":RED,"試験期間":PURP,"行事日":ORG,"週末":NAVY,"祝日":GREY,"休業期間":GRN}
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
sns.boxplot(data=df, x="day_type", y="load", order=order_dt,
            palette=[dtcol[d] for d in order_dt], ax=axes[0], showfliers=False)
axes[0].axhline(CONTRACT, ls="--", color=RED, alpha=0.6, label=f"契約電力 {CONTRACT} kW")
axes[0].set_xlabel("日種別"); axes[0].set_ylabel("時別需要 [kWh/h]")
axes[0].set_title("(a) 日種別 需要電力の箱ひげ図", fontweight="bold", color=NAVY)
axes[0].legend()
for dt in order_dt:
    g = df[df["day_type"]==dt].groupby("hour")["load"].mean()
    if len(g): axes[1].plot(g.index, g.values, marker="o", ms=3, lw=2,
                            color=dtcol[dt], label=f"{dt} (n={(df['day_type']==dt).sum():,} h)")
axes[1].set_xlabel("時刻 [時]"); axes[1].set_ylabel("平均需要 [kWh/h]")
axes[1].set_title("(b) 日種別 日内需要プロファイル", fontweight="bold", color=NAVY)
axes[1].legend(fontsize=8, ncol=2)
plt.tight_layout(); savefig("F03_daytype_distribution")

# ===========================================================================
# 図 4: 季節分離 エネルギー署名 (時別 + 日次)
# ===========================================================================
scol={"冷房期 (6–9月)":RED,"中間期 (4–5・10–11月)":GRN,"暖房期 (12–3月)":NAVY}
daily=df.groupby("date").agg(load=("load","mean"),temp=("temperature_2m","mean"),
                              season=("season",lambda s:s.iloc[0]),
                              day_type=("day_type",lambda s:s.iloc[0])).dropna()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
seas_res={}
# 時別
for s in order_se:
    sub = df[df["season"]==s]
    if not len(sub): continue
    sl, ic, r2 = linfit(sub["temperature_2m"].values, sub["load"].values)
    seas_res[s] = {"hourly":{"slope":round(sl,2),"r2":round(r2,3),"n_hours":int(len(sub))}}
    axes[0].scatter(sub["temperature_2m"], sub["load"], s=2, alpha=0.15, color=scol[s])
    xx = np.linspace(sub["temperature_2m"].min(), sub["temperature_2m"].max(), 50)
    axes[0].plot(xx, sl*xx+ic, color=scol[s], lw=3,
                 label=f"{s}: 傾き {sl:+.1f}, R²={r2:.2f}, n={len(sub):,} 時間")
axes[0].set_xlabel("外気温 [°C]"); axes[0].set_ylabel("時別需要 [kWh/h]")
axes[0].set_title("(a) 時別データによる線形回帰", fontweight="bold", color=NAVY)
axes[0].legend(loc="upper left", fontsize=9)

# 日次
for s in order_se:
    sub = daily[daily["season"]==s]
    if len(sub) < 5: continue
    sl, ic, r2 = linfit(sub["temp"].values, sub["load"].values)
    seas_res[s]["daily"] = {"slope":round(sl,2),"r2":round(r2,3),"n_days":int(len(sub))}
    axes[1].scatter(sub["temp"], sub["load"], s=25, alpha=0.55, color=scol[s])
    xx = np.linspace(sub["temp"].min(), sub["temp"].max(), 50)
    axes[1].plot(xx, sl*xx+ic, color=scol[s], lw=3,
                 label=f"{s}: 傾き {sl:+.1f}, R²={r2:.2f}, n={len(sub)} 日")
axes[1].set_xlabel("日平均気温 [°C]"); axes[1].set_ylabel("日平均需要 [kWh/h]")
axes[1].set_title("(b) 日次データによる線形回帰 (ASHRAE 推奨)", fontweight="bold", color=NAVY)
axes[1].legend(loc="upper left", fontsize=9)
plt.suptitle("季節分離 エネルギー署名 — 時別と日次の比較",
             fontsize=13, fontweight="bold", color=NAVY, y=1.02)
plt.tight_layout(); savefig("F04_seasonal_signatures")

# ===========================================================================
# 図 5: 冷房期 × 日種別 (時別 + 日次, 全データを表示)
# ===========================================================================
cool_hour = df[df["season"]=="冷房期 (6–9月)"]
cool_day  = daily[daily["season"]=="冷房期 (6–9月)"]

fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
rq3 = {}
for dt in ["授業日","週末","休業期間"]:
    sub_h = cool_hour[cool_hour["day_type"]==dt]
    sub_d = cool_day[cool_day["day_type"]==dt]
    if len(sub_h) < 30: continue
    c = dtcol[dt]
    sl_h, ic_h, r2_h = linfit(sub_h["temperature_2m"].values, sub_h["load"].values)
    sl_d, ic_d, r2_d = linfit(sub_d["temp"].values, sub_d["load"].values)
    rq3[dt] = {
        "hourly":{"slope":round(sl_h,2),"r2":round(r2_h,3),"n_hours":int(len(sub_h))},
        "daily" :{"slope":round(sl_d,2),"r2":round(r2_d,3),"n_days":int(len(sub_d))},
    }
    # 時別
    axes[0].scatter(sub_h["temperature_2m"], sub_h["load"], s=2, alpha=0.18, color=c)
    xx = np.linspace(sub_h["temperature_2m"].min(), sub_h["temperature_2m"].max(), 40)
    axes[0].plot(xx, sl_h*xx+ic_h, color=c, lw=3,
                 label=f"{dt}: 傾き {sl_h:+.1f}, R²={r2_h:.2f}, n={len(sub_h):,} 時間")
    # 日次
    axes[1].scatter(sub_d["temp"], sub_d["load"], s=30, alpha=0.55, color=c)
    xx = np.linspace(sub_d["temp"].min(), sub_d["temp"].max(), 40)
    axes[1].plot(xx, sl_d*xx+ic_d, color=c, lw=3,
                 label=f"{dt}: 傾き {sl_d:+.1f}, R²={r2_d:.2f}, n={len(sub_d)} 日")
for ax in axes:
    ax.set_xlabel("外気温 [°C]"); ax.set_ylabel("需要 [kWh/h]")
axes[0].set_title("(a) 時別データ (細かいサンプル)", fontweight="bold", color=NAVY)
axes[1].set_title("(b) 日次データ (ASHRAE 推奨)", fontweight="bold", color=NAVY)
axes[0].legend(loc="upper left", fontsize=9); axes[1].legend(loc="upper left", fontsize=9)
plt.suptitle("冷房期における日種別 エネルギー署名 — 学年暦による温度感度の調節",
             fontsize=13, fontweight="bold", color=NAVY, y=1.02)
plt.tight_layout(); savefig("F05_cooling_by_daytype")

# ===========================================================================
# 図 6: 月×時刻 平均負荷ヒートマップ
# ===========================================================================
piv = df.pivot_table("load", index="month", columns="hour", aggfunc="mean")
fig, ax = plt.subplots(figsize=(13, 4.5))
sns.heatmap(piv, cmap="YlOrRd", ax=ax, cbar_kws={"label":"平均需要 [kWh/h]"})
ax.set_title("月別・時刻別 平均需要電力 — 夏季 14時前後にピーク",
             fontweight="bold", color=NAVY)
ax.set_xlabel("時刻 [時]"); ax.set_ylabel("月")
plt.tight_layout(); savefig("F06_month_hour_heatmap")

# ===========================================================================
# 図 7: 容量リスク ρ = 負荷/契約 の時系列
# ===========================================================================
fig, ax = plt.subplots(figsize=(15, 4.5))
ax.plot(df.index, df["rho"], color=NAVY, lw=0.35, alpha=0.7)
for thr, col, lbl in [(0.50,"#FFC107","Watch (0.50)"),(0.70,ORG,"High (0.70)"),
                       (0.85,RED,"Critical (0.85)")]:
    ax.axhline(thr, ls="--", color=col, lw=1, label=lbl)
ax.set_ylabel("ρ = 需要 / 契約電力"); ax.set_xlabel("日付")
ax.set_title(f"容量リスク比 ρ の年間推移 — 最大値 {df['rho'].max():.3f} "
             f"(契約 {CONTRACT} kW)", fontweight="bold", color=NAVY)
ax.legend(loc="upper right")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
plt.tight_layout(); savefig("F07_rho_timeseries")

# ===========================================================================
# 図 8: (気温×日種別) リスク集中ヒートマップ
# ===========================================================================
df["tbin"] = pd.cut(df["temperature_2m"], bins=np.arange(-4,38,3))
rmat = df.pivot_table("rho", index="day_type", columns="tbin", aggfunc="mean")
rmat = rmat.reindex(order_dt)
fig, ax = plt.subplots(figsize=(13, 4.8))
sns.heatmap(rmat, annot=True, fmt=".2f", cmap="YlOrRd", vmin=0, vmax=0.9,
            cbar_kws={"label":"平均 ρ"}, ax=ax, linewidths=0.3)
ax.set_xlabel("気温区分 [°C]"); ax.set_ylabel("日種別")
ax.set_title("(気温 × 日種別) 空間における容量リスク ρ の集中 — 授業日×32°C 以上に局在",
             fontweight="bold", color=NAVY, fontsize=12)
plt.tight_layout(); savefig("F08_risk_concentration")

# ===========================================================================
# 図 9: (時刻×日種別) リスクヒートマップ
# ===========================================================================
rhour = df.pivot_table("rho", index="day_type", columns="hour", aggfunc="mean").reindex(order_dt)
fig, ax = plt.subplots(figsize=(15, 4.5))
sns.heatmap(rhour, cmap="YlOrRd", vmin=0, vmax=0.9,
            cbar_kws={"label":"平均 ρ"}, ax=ax, linewidths=0.2)
ax.set_xlabel("時刻 [時]"); ax.set_ylabel("日種別")
ax.set_title("(時刻 × 日種別) 容量リスクの集中 — 管理介入の対象時間帯を特定",
             fontweight="bold", color=NAVY)
plt.tight_layout(); savefig("F09_risk_by_hour")

# ===========================================================================
# 結果の保存
# ===========================================================================
def risk_tier(r):
    if r>=0.85: return "Critical"
    if r>=0.70: return "High"
    if r>=0.50: return "Watch"
    return "Normal"
df["risk"]=df["rho"].apply(risk_tier)

summary = {
 "総有効時間": int(len(df)),
 "総有効日数": int(df.index.normalize().nunique()),
 "対象期間": f"{df.index.min().date()} – {df.index.max().date()}",
 "契約電力_kW": CONTRACT,
 "データ可用性": {"時間": hours_mat.to_dict(), "日": days_mat.to_dict()},
 "季節別_エネルギー署名": seas_res,
 "冷房期_日種別_エネルギー署名": rq3,
 "容量リスク統計": {
   "最大_ρ": float(df["rho"].max()),
   "P95_ρ": float(df["rho"].quantile(0.95)),
   "Critical_時間数": int((df["rho"]>=0.85).sum()),
   "High以上_時間数": int((df["rho"]>=0.70).sum()),
   "Critical発生時の日種別内訳": df[df["risk"]=="Critical"]["day_type"].value_counts().to_dict(),
   "High以上の日種別内訳": df[df["rho"]>=0.70]["day_type"].value_counts().to_dict(),
 },
}
with open(f"{RES}/comprehensive_jp_analysis.json", "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
print(f"\n💾 results/comprehensive_jp_analysis.json")
print("\n=== サマリ ===")
print(json.dumps(summary, ensure_ascii=False, indent=2, default=str)[:2400])
