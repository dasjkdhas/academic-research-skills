# 気象データ ローカル解析 プレイブック (v1)
**山口大学キャンパス省エネ研究 — JFY2025 (2025-04-01 〜 2026-03-31)**

このドキュメント1枚で、配布した気象 CSV を **自分の PC で** 取り込み・前処理・可視化・統計解析するまでを完結できるようにしてあります。コードはそのままコピペで Python 3.10+ で実行可能です。

---

## 0. 配布ファイル一覧

| ファイル | サイズ | 内容 | 用途 |
|---|---|---|---|
| `amedas_ube_JFY2025.csv` | 327 KB | JMA 宇部站 公式観測 (温度・降水・風速・風向) | **論文の主データ** |
| `amedas_ube_JFY2025_with_wdir_text.csv` | 405 KB | 上記 + 風向の日本語テキスト列 | 検証用 |
| `era5_yamaguchi_JFY2025.csv` | 553 KB | ERA5 全 10 変数 | 完整存档 |
| `era5_yamaguchi_JFY2025_CORE_AMeDASequiv.csv` | 320 KB | ERA5 の 4 コア変数 (AMeDAS と同じ4変数) | **交差検証用** |
| `era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv` | 405 KB | ERA5 の追加 6 変数 (湿度・露点・気圧・雲量・日射) | **Track A 専用 / Track B 論文で使用不可** |

**共通仕様**: ISO 8601 timestamp, JST (UTC+9), UTF-8, 1 時間値, 8,760 行 = 365日 × 24時間.

---

## 1. 環境セットアップ (1 回だけ)

```bash
# Python 3.10+ 前提
pip install pandas numpy scipy scikit-learn matplotlib seaborn jupyter \
            pwlf statsmodels japanize-matplotlib
# japanize-matplotlib: Mac/Windows どちらでも日本語フォントを自動設定
```

**プロジェクトディレクトリ構成 (推奨)**:
```
my-research/
├── data/                              ← ここに配布 CSV を置く
│   ├── amedas_ube_JFY2025.csv
│   ├── era5_yamaguchi_JFY2025_CORE_AMeDASequiv.csv
│   └── era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv
├── figures/                           ← 出力先 (空フォルダ)
└── analysis.ipynb                     ← または analysis.py
```

---

## 2. データロードと初期チェック

```python
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib                     # 日本語表示
from pathlib import Path

DATA = Path("data")
FIG  = Path("figures"); FIG.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="talk")

# --- AMeDAS (主データ) ---
ame = pd.read_csv(DATA / "amedas_ube_JFY2025.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
ame.columns                                    # precipitation, temperature_2m,
                                               # wind_speed_10m, wind_direction_10m

# --- ERA5 CORE (検証用、AMeDAS と同じ 4 変数) ---
era = pd.read_csv(DATA / "era5_yamaguchi_JFY2025_CORE_AMeDASequiv.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")

# --- ERA5 EXTRA (Track A 専用) ---
era_x = pd.read_csv(DATA / "era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv",
                    parse_dates=["timestamp"]).set_index("timestamp")

print(ame.shape, era.shape, era_x.shape)
print("AMeDAS 期間:", ame.index.min(), "→", ame.index.max())
print("欠測 (AMeDAS):"); print(ame.isna().sum())
```

期待される出力:
```
(8760, 4) (8760, 4) (8760, 6)
AMeDAS 期間: 2025-04-01 01:00:00 → 2026-04-01 00:00:00
欠測 (AMeDAS):
precipitation         9
temperature_2m       11
wind_speed_10m        8
wind_direction_10m   48
```

---

## 3. データ品質チェック (3 行で)

```python
# 値域チェック (異常値検出)
def qa(df, label):
    print(f"\n=== {label} ===")
    print(df.describe().loc[["min","max","mean","std"]].round(2).T)
    print(f"欠測率: {df.isna().mean().round(4).to_dict()}")
qa(ame, "AMeDAS"); qa(era, "ERA5 CORE")
```

**異常値の目安**:
- 気温: -10〜40°C 以外は要確認 (宇部の範囲: -2.9〜35.5)
- 風速: > 30 m/s は台風時のみ
- 湿度 (ERA5 EXTRA): 0〜100% 以外は不正値
- 降水: > 100 mm/h は極端豪雨のみ

---

## 4. 可視化レシピ (10 個、各々独立)

### 図 4.1 — 全年時系列 (overview)

```python
fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
for ax, col, lbl, c in zip(
    axes,
    ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"],
    ["気温 (°C)", "降水量 (mm/h)", "風速 (m/s)", "風向 (°)"],
    ["#C8102E", "#003B71", "#2D9C5A", "#E78A00"]):
    ax.plot(ame.index, ame[col], lw=0.4, color=c, alpha=0.8)
    ax.set_ylabel(lbl); ax.grid(alpha=0.3)
axes[-1].set_xlabel("日付")
fig.suptitle("AMeDAS 宇部 — JFY2025 全年時系列", fontsize=14)
plt.tight_layout()
plt.savefig(FIG / "fig01_overview.png", dpi=150); plt.show()
```

### 図 4.2 — 月×時刻 ヒートマップ (RQ1 用)

```python
ame["month"] = ame.index.month
ame["hour"]  = ame.index.hour
pivot = ame.pivot_table(values="temperature_2m", index="month", columns="hour",
                        aggfunc="mean")

fig, ax = plt.subplots(figsize=(13, 4.5))
sns.heatmap(pivot, cmap="RdBu_r", center=15, ax=ax,
            cbar_kws={"label": "平均気温 (°C)"})
ax.set_title("月×時刻 平均気温 ヒートマップ — AMeDAS 宇部")
ax.set_xlabel("時刻"); ax.set_ylabel("月")
plt.tight_layout(); plt.savefig(FIG / "fig02_heatmap.png", dpi=150); plt.show()
```

### 図 4.3 — 月別ボックスプロット

```python
fig, ax = plt.subplots(figsize=(13, 5))
sns.boxplot(data=ame, x="month", y="temperature_2m",
            palette="coolwarm", ax=ax)
ax.set_title("月別 気温分布 — AMeDAS 宇部 JFY2025")
ax.set_xlabel("月"); ax.set_ylabel("気温 (°C)")
plt.tight_layout(); plt.savefig(FIG / "fig03_monthly_box.png", dpi=150); plt.show()
```

### 図 4.4 — Load Duration Curve (温度版)

```python
fig, ax = plt.subplots(figsize=(10, 5))
sorted_t = ame["temperature_2m"].dropna().sort_values(ascending=False).reset_index(drop=True)
ax.plot(np.arange(len(sorted_t)) / len(sorted_t) * 100, sorted_t,
        color="#C8102E", lw=1.5)
ax.axhline(28, ls="--", color="orange", lw=1, label="28°C 熱中症警戒")
ax.axhline(0,  ls="--", color="blue",   lw=1, label="0°C 凍結リスク")
ax.set_xlabel("超過時間比率 (%)"); ax.set_ylabel("気温 (°C)")
ax.set_title("気温 持続曲線 (Temperature Duration Curve) — JFY2025")
ax.legend(); plt.tight_layout()
plt.savefig(FIG / "fig04_temp_duration.png", dpi=150); plt.show()
```

### 図 4.5 — 風配図 (Wind Rose) ※ matplotlib のみ

```python
from matplotlib import patches as mp_patches
def wind_rose(df, ax, n_bins=16):
    angles = np.deg2rad(df["wind_direction_10m"].dropna())
    speeds = df["wind_speed_10m"].dropna()
    bin_edges = np.linspace(0, 2*np.pi, n_bins+1)
    counts = np.array([
        ((angles >= bin_edges[i]) & (angles < bin_edges[i+1])).sum()
        for i in range(n_bins)])
    ax.bar(bin_edges[:-1], counts, width=2*np.pi/n_bins,
           color="#003B71", alpha=0.75, edgecolor="white")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection="polar")
wind_rose(ame, ax)
ax.set_title("風配図 — AMeDAS 宇部 JFY2025", pad=20)
plt.savefig(FIG / "fig05_windrose.png", dpi=150); plt.show()
```

### 図 4.6 — ERA5 vs AMeDAS 一致性検証

```python
from scipy.stats import pearsonr
j = era.join(ame, how="inner", lsuffix="_era", rsuffix="_ame").dropna()
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, var, label in zip(
    axes, ["temperature_2m", "precipitation", "wind_speed_10m"],
    ["気温 (°C)", "降水 (mm/h)", "風速 (m/s)"]):
    x = j[f"{var}_ame"]; y = j[f"{var}_era"]
    m = ~(x.isna() | y.isna()); x, y = x[m], y[m]
    r = pearsonr(x, y)[0]
    mae = (y - x).abs().mean()
    ax.scatter(x, y, s=4, alpha=0.2, color="#003B71")
    lo, hi = min(x.min(), y.min()), max(x.max(), y.max())
    ax.plot([lo, hi], [lo, hi], "k--", lw=1)
    ax.set_xlabel(f"AMeDAS {label}"); ax.set_ylabel(f"ERA5 {label}")
    ax.set_title(f"r={r:.3f}, MAE={mae:.2f}")
fig.suptitle("ERA5 vs AMeDAS 一致性検証", fontsize=14)
plt.tight_layout(); plt.savefig(FIG / "fig06_validation.png", dpi=150); plt.show()
```

### 図 4.7 — 累積度時 CDH / HDH (温度反応の基礎)

```python
T = ame["temperature_2m"].dropna()
# 基準温度ベースの度時 (degree-hour)
for base in [18, 20, 22, 24]:
    cdh = (T - base).clip(lower=0).cumsum()
    hdh = (base - T).clip(lower=0).cumsum()
    if base == 22:
        fig, ax1 = plt.subplots(figsize=(12, 4.5))
        ax2 = ax1.twinx()
        ax1.plot(T.index, cdh, color="#C8102E", label=f"CDH base{base}")
        ax2.plot(T.index, hdh, color="#003B71", label=f"HDH base{base}")
        ax1.set_ylabel("累積 CDH (°C·h)", color="#C8102E")
        ax2.set_ylabel("累積 HDH (°C·h)", color="#003B71")
        ax1.set_title(f"累積 度時 (Base = {base}°C) — JFY2025")
        plt.tight_layout(); plt.savefig(FIG / f"fig07_cdh_hdh_base{base}.png", dpi=150)
        plt.show()
```

### 図 4.8 — 風向 sin/cos エンコーディング

```python
wd_rad = np.deg2rad(ame["wind_direction_10m"])
ame["wd_sin"] = np.sin(wd_rad)
ame["wd_cos"] = np.cos(wd_rad)
fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(ame["wd_sin"], ame["wd_cos"], s=2, alpha=0.15, color="#003B71")
ax.set_aspect("equal"); ax.set_xlabel("sin (風向)"); ax.set_ylabel("cos (風向)")
ax.set_title("風向 円形エンコーディング (機械学習用)")
ax.add_patch(plt.Circle((0,0), 1, fill=False, color="red", lw=1))
plt.tight_layout(); plt.savefig(FIG / "fig08_wind_sincos.png", dpi=150); plt.show()
```

### 図 4.9 — 日別統計 (24h 集約)

```python
daily = ame[["temperature_2m", "precipitation", "wind_speed_10m"]].resample("D").agg({
    "temperature_2m":  ["mean", "min", "max"],
    "precipitation":   "sum",
    "wind_speed_10m":  "mean",
})
daily.columns = ["t_mean", "t_min", "t_max", "precip_total", "wind_mean"]

fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
axes[0].fill_between(daily.index, daily["t_min"], daily["t_max"],
                    alpha=0.3, color="#C8102E", label="日内変動")
axes[0].plot(daily.index, daily["t_mean"], color="#C8102E", lw=1)
axes[0].set_ylabel("気温 (°C)"); axes[0].legend(loc="upper right")
axes[1].bar(daily.index, daily["precip_total"], color="#003B71", width=1)
axes[1].set_ylabel("日降水量 (mm)")
axes[2].plot(daily.index, daily["wind_mean"], color="#2D9C5A", lw=1)
axes[2].set_ylabel("日平均風速 (m/s)"); axes[2].set_xlabel("日付")
fig.suptitle("日別気象サマリー — AMeDAS 宇部 JFY2025")
plt.tight_layout(); plt.savefig(FIG / "fig09_daily_summary.png", dpi=150); plt.show()
```

### 図 4.10 — 季節 × 時刻 平均気温 (4 季節カラム)

```python
def get_season(m):
    if m in (3,4,5):   return "春"
    if m in (6,7,8):   return "夏"
    if m in (9,10,11): return "秋"
    return "冬"
ame["season"] = ame.index.month.map(get_season)
hourly_season = ame.groupby(["season", "hour"])["temperature_2m"].mean().unstack(0)

fig, ax = plt.subplots(figsize=(11, 5))
colors = {"春": "#2D9C5A", "夏": "#C8102E", "秋": "#E78A00", "冬": "#003B71"}
for s in ["春", "夏", "秋", "冬"]:
    ax.plot(hourly_season.index, hourly_season[s], marker="o", lw=2,
            color=colors[s], label=s)
ax.set_xlabel("時刻"); ax.set_ylabel("平均気温 (°C)")
ax.set_title("季節別 時刻別 平均気温 — JFY2025")
ax.legend(); plt.tight_layout()
plt.savefig(FIG / "fig10_diurnal_season.png", dpi=150); plt.show()
```

---

## 5. 解析手法詳細

### 5.1 ピアソン / スピアマン相関

```python
from scipy.stats import pearsonr, spearmanr

cols = ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"]
def corr_matrix(df):
    n = len(cols); P = np.eye(n); S = np.eye(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                m = ~(df[cols[i]].isna() | df[cols[j]].isna())
                P[i,j] = pearsonr(df[cols[i]][m], df[cols[j]][m])[0]
                S[i,j] = spearmanr(df[cols[i]][m], df[cols[j]][m])[0]
    return pd.DataFrame(P, index=cols, columns=cols), \
           pd.DataFrame(S, index=cols, columns=cols)

P_ame, S_ame = corr_matrix(ame)
print("Pearson:");  print(P_ame.round(3))
print("Spearman:"); print(S_ame.round(3))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.heatmap(P_ame, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            vmin=-1, vmax=1, ax=axes[0]); axes[0].set_title("Pearson")
sns.heatmap(S_ame, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            vmin=-1, vmax=1, ax=axes[1]); axes[1].set_title("Spearman")
plt.tight_layout(); plt.savefig(FIG / "fig11_corr_matrix.png", dpi=150); plt.show()
```

### 5.2 偏相関 (Partial Correlation) — 交絡を取り除く

```python
from sklearn.linear_model import LinearRegression

def partial_corr(df, target_y, target_x, controls):
    """y と x の偏相関 (controls を線形で剥がす)"""
    sub = df[[target_y, target_x] + controls].dropna()
    yres = sub[target_y] - LinearRegression().fit(sub[controls], sub[target_y]).predict(sub[controls])
    xres = sub[target_x] - LinearRegression().fit(sub[controls], sub[target_x]).predict(sub[controls])
    return pearsonr(xres, yres)[0]

# 例: 風速と気温の関係を、時刻と月の影響を制御して測る
ame["month"] = ame.index.month
ame["hour"]  = ame.index.hour
r_raw  = pearsonr(*ame[["wind_speed_10m","temperature_2m"]].dropna().T.values)[0]
r_part = partial_corr(ame, "wind_speed_10m", "temperature_2m", ["hour", "month"])
print(f"raw r            = {r_raw:+.3f}")
print(f"partial (h+mon)  = {r_part:+.3f}")
```

### 5.3 時刻別 層別化相関 (Hour-stratified)

```python
hourly_r = {}
for h in range(24):
    sub = ame[ame["hour"] == h].dropna(subset=["temperature_2m", "wind_speed_10m"])
    if len(sub) > 30:
        hourly_r[h] = pearsonr(sub["temperature_2m"], sub["wind_speed_10m"])[0]
hourly_r = pd.Series(hourly_r)

fig, ax = plt.subplots(figsize=(10, 4))
hourly_r.plot.bar(ax=ax, color="#003B71")
ax.axhline(0, color="black", lw=0.5)
ax.set_xlabel("時刻"); ax.set_ylabel("r (温度 vs 風速)")
ax.set_title("時刻別 層別化相関")
plt.tight_layout(); plt.savefig(FIG / "fig12_hourly_corr.png", dpi=150); plt.show()
```

### 5.4 変点 / 分段回帰 (将来の電力データ到着時に使用)

電力データが届いた後、温度反応の変点を見つける典型的手法。今は **温度の自己統計** だけ示します:

```python
import pwlf                                # piecewise linear fit
# 例: 月平均気温の年内ピース
monthly_T = ame["temperature_2m"].resample("ME").mean().reset_index()
monthly_T["month_num"] = np.arange(len(monthly_T))
x = monthly_T["month_num"].values; y = monthly_T["temperature_2m"].values

model = pwlf.PiecewiseLinFit(x, y)
breaks = model.fit(3)                      # 3 セグメント
print("Breakpoints (months index):", breaks)

xx = np.linspace(0, len(x)-1, 200)
yy = model.predict(xx)
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(monthly_T["timestamp"], y, "o", color="#C8102E", label="月平均気温")
ax.plot(monthly_T["timestamp"].iloc[xx.astype(int).clip(0,len(x)-1)], yy,
        "-", color="#003B71", label="区分線形回帰 (3 piece)")
ax.set_xlabel("月"); ax.set_ylabel("気温 (°C)")
ax.set_title("月平均気温の区分線形フィット (将来 電力データに同様の手法を適用)")
ax.legend(); plt.tight_layout()
plt.savefig(FIG / "fig13_pwlf_demo.png", dpi=150); plt.show()
```

**電力データが届いた後の標準コード** (テンプレート):
```python
# 想定: df["b00"] と df["temperature_2m"] が結合済み
import pwlf
xy = df[["temperature_2m", "b00"]].dropna().sort_values("temperature_2m")
model = pwlf.PiecewiseLinFit(xy["temperature_2m"].values, xy["b00"].values)
model.fit(2)                               # 2 セグメント = 1 変点
print("Change point (°C):", model.fit_breaks[1])
print("Heating slope (kW/°C):", model.beta[1])
print("Cooling slope (kW/°C):", model.beta[1] + model.beta[2])
```

### 5.5 GAM (Generalized Additive Model) — 滑らかな温度反応

```python
# pip install pygam
# 電力データが届いた後の使用例:
# from pygam import LinearGAM, s, f
# gam = LinearGAM(s(0) + f(1)).fit(X=df[["temperature_2m","hour"]], y=df["b00"])
# gam.summary()
# 個別 partial dependence: gam.partial_dependence(term=0, X=...)
```

### 5.6 統合データセット作成 (AMeDAS 主 + ERA5 補完)

```python
# AMeDAS を主、ERA5 でギャップを埋める統合データセット
combined = ame[["temperature_2m", "precipitation",
                "wind_speed_10m", "wind_direction_10m"]].copy()
for col in combined.columns:
    combined[col] = combined[col].fillna(era[col])      # ERA5 で穴埋め
combined["data_source"] = "AMeDAS"
mask = ame[combined.columns[:4]].isna().any(axis=1) & ~era[combined.columns[:4]].isna().any(axis=1)
combined.loc[mask, "data_source"] = "ERA5_filled"

print(combined["data_source"].value_counts())
combined.to_csv("data/weather_combined_JFY2025.csv")
```

これを論文の Methods に書く際は: 「**主データは AMeDAS。気温は r=0.991 で ERA5 と一致を確認したため、AMeDAS の欠測時刻 (温度 11h, 風向 48h) は ERA5 で埋めた。**」と明示。

---

## 6. 再現可能なエンドツーエンド・スクリプト

下記を `analysis.py` として保存し `python analysis.py` で実行すると、全 13 枚の図が `figures/` に生成されます。

```python
# analysis.py — END-TO-END (約 100 行)
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import japanize_matplotlib
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

DATA = Path("data"); FIG = Path("figures"); FIG.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="talk")

ame = pd.read_csv(DATA/"amedas_ube_JFY2025.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
era = pd.read_csv(DATA/"era5_yamaguchi_JFY2025_CORE_AMeDASequiv.csv",
                  parse_dates=["timestamp"]).set_index("timestamp")
ame["month"] = ame.index.month; ame["hour"] = ame.index.hour

# --- すべての図を順次出力 ---
# (上の §4.1〜4.10、§5.1〜5.3 のコードを順番に貼り付け)
print("✓ done — 13 figures in", FIG)
```

---

## 7. 電力データ到着後の作業フロー

電力 CSV (`b00_JFY2025.csv` 等) が届いたら、以下の順で論文 RQ を回答できます:

| RQ | 必要なステップ | 使うレシピ |
|----|---|------|
| RQ1: 校歴ごとの周期構造 | 電力 + 校歴で月×時刻ヒートマップ | §4.2 を電力に置き換え |
| RQ2: 温度応答閾値 | 温度 × 電力 散布図 + 変点回帰 | §5.4 テンプレート |
| RQ3: 校歴調節の温度感度 | 校歴状態ごとに §5.4 を回す | §5.4 × グループ |
| RQ4: 容量リスク | 電力 / 契約電力 → リスク階層 → ヒートマップ | §4.2 を ρ=L/C に |

---

## 付録 A: トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| 日本語が□表示 | フォント未設定 | `pip install japanize-matplotlib` 後 import |
| `KeyError: temperature_2m` | カラム名違い | `print(df.columns)` で確認 |
| `pwlf` 動作遅い | 全データで fit | サンプル数を `<10000` に絞る (`.sample(...)`) |
| 風向が直線状の縞 | AMeDAS は 16方位 離散化 | 散布図では正常、回帰前に sin/cos エンコード |
| 数値解析の seasonal_decompose エラー | 欠測あり | `.interpolate(limit=3)` で短期穴埋め |

## 付録 B: 引用可能なデータ仕様

| 項目 | 値 |
|---|---|
| AMeDAS 観測所 | 宇部 (prec_no=81, block_no=0778), 4要素観測 |
| AMeDAS 座標 | おおよそ 33.9°N, 131.3°E |
| AMeDAS 取得元 | 気象庁 過去の気象データ (data.jma.go.jp) |
| ERA5 取得元 | Open-Meteo Historical API (ERA5 + ERA5T) |
| ERA5 解像度 | ~31 km グローバルグリッド、座標補間 |
| ERA5 引用 | Hersbach, H., et al. (2020). *Q.J.R. Meteorol. Soc.*, 146(730), 1999–2049. |
| 期間 | JFY2025: 2025-04-01 〜 2026-03-31 (365日, 8,760時間) |
| タイムゾーン | Asia/Tokyo (UTC+9) |
| 文字コード | UTF-8 |

---

## 付録 C: チェックリスト (論文投稿前)

- [ ] 全 13 図が再生成可能 (`analysis.py` 一回で)
- [ ] AMeDAS / ERA5 の役割を Methods に明記 (主データ + 検証)
- [ ] ERA5 vs AMeDAS 一致性検証図を Methods に掲載 (r=0.991 を引用)
- [ ] EXTRA 6 変数 (湿度・日射・雲量等) は Track B 実証で使用していない
- [ ] AMeDAS 宇部站が 4 要素観測 (湿度未測定) であることを明示
- [ ] 欠測ハンドリング (ERA5 補完または 線形補間) を明記

---

**作成日**: 2026-05-31
**バージョン**: v1
**作成者**: Yamaguchi University 省エネ研究 (劉)
