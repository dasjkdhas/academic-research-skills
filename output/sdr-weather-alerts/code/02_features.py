"""Step 1: Feature engineering — join power + weather + calendar; build lag/cyclic/day-type features.

Outputs:
  data_processed/features.parquet
  data_processed/feature_dict.md
"""
import os, warnings, json
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"


def main():
    pw  = pd.read_csv(f"{PROC}/campus_power_hourly.csv",
                      parse_dates=["timestamp"]).set_index("timestamp")
    wx  = pd.read_csv(f"{PROC}/weather_hourly.csv",
                      parse_dates=["timestamp"]).set_index("timestamp")
    cal = pd.read_csv(f"{PROC}/calendar.csv", parse_dates=["date"]).set_index("date")

    # Align — use common hours
    common = pw.index.intersection(wx.index)
    pw, wx = pw.loc[common], wx.loc[common]
    print(f"Aligned hours: {len(common)}  ({common.min()} → {common.max()})")

    df = pw.join(wx, how="inner")

    # Join calendar by date
    df["date_only"] = df.index.normalize()
    cal_lookup = cal.reset_index().rename(columns={"date": "date_only"})
    df = df.reset_index().merge(cal_lookup, on="date_only", how="left").set_index("timestamp")
    df.drop(columns=["date_only"], inplace=True)

    # ------------------------------------------------------------------
    # Time features
    # ------------------------------------------------------------------
    df["hour"]        = df.index.hour
    df["dow_int"]     = df.index.dayofweek
    df["month"]       = df.index.month
    df["day_of_year"] = df.index.dayofyear
    df["week_of_year"] = df.index.isocalendar().week.astype(int)
    df["is_weekend"]  = (df["dow_int"] >= 5).astype(int)
    df["is_class_day"] = df["is_class_day"].astype(int)

    # Cyclical encoding
    df["hour_sin"]  = np.sin(2*np.pi*df["hour"]/24);  df["hour_cos"]  = np.cos(2*np.pi*df["hour"]/24)
    df["dow_sin"]   = np.sin(2*np.pi*df["dow_int"]/7); df["dow_cos"]  = np.cos(2*np.pi*df["dow_int"]/7)
    df["month_sin"] = np.sin(2*np.pi*df["month"]/12); df["month_cos"] = np.cos(2*np.pi*df["month"]/12)

    # Day-of-week × hour interaction
    df["dow_hour"] = df["dow_int"]*100 + df["hour"]

    # ------------------------------------------------------------------
    # Day-type one-hot (Path A: manual labels)
    # ------------------------------------------------------------------
    le = LabelEncoder()
    df["day_type_id_A"] = le.fit_transform(df["day_type"].fillna("unknown"))
    DAY_TYPE_MAP = dict(zip(le.classes_, range(len(le.classes_))))
    print(f"Day type classes (Path A): {DAY_TYPE_MAP}")

    # ------------------------------------------------------------------
    # Day-type Path B: unsupervised K-Means on daily 24h profile
    # ------------------------------------------------------------------
    daily_profile = df["b00"].groupby(df.index.date).apply(
        lambda x: x.reset_index(drop=True).iloc[:24]
    ).unstack()
    daily_profile.columns = [f"h{i:02d}" for i in range(daily_profile.shape[1])]
    daily_profile.index = pd.to_datetime(daily_profile.index)
    daily_profile = daily_profile.dropna(thresh=20)  # need at least 20 hours per day

    # Normalize each row (shape clustering)
    profile_norm = daily_profile.div(daily_profile.mean(axis=1), axis=0)

    K = 5  # number of automatic day-types
    km = KMeans(n_clusters=K, n_init=20, random_state=42)
    profile_norm = profile_norm.fillna(profile_norm.mean())
    day_cluster = pd.Series(km.fit_predict(profile_norm), index=profile_norm.index, name="day_type_id_B")
    print(f"Cluster (Path B) sizes: {day_cluster.value_counts().sort_index().to_dict()}")

    # Map back per-hour
    cluster_lookup = day_cluster.reset_index().rename(columns={"index":"date_only"})
    cluster_lookup["date_only"] = pd.to_datetime(cluster_lookup["date_only"])
    df["date_only"] = df.index.normalize()
    df = df.reset_index().merge(cluster_lookup, on="date_only", how="left").set_index("timestamp")
    df.drop(columns=["date_only"], inplace=True)
    df["day_type_id_B"] = df["day_type_id_B"].fillna(-1).astype(int)

    # Path A vs Path B agreement metric (Adjusted Rand Index, NMI)
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    valid_days = day_cluster.index.intersection(cal.index)
    a = cal.loc[valid_days, "day_type"].astype("category").cat.codes.values
    b = day_cluster.reindex(valid_days).values
    ari = adjusted_rand_score(a, b)
    nmi = normalized_mutual_info_score(a, b)
    print(f"Path A (manual) vs Path B (clustering) agreement: ARI={ari:.3f}, NMI={nmi:.3f}")

    # ------------------------------------------------------------------
    # Lag features for b00
    # ------------------------------------------------------------------
    for lag in [1, 2, 3, 6, 12, 24, 48, 168]:
        df[f"b00_lag{lag}"] = df["b00"].shift(lag)

    df["b00_roll24_mean"] = df["b00"].shift(1).rolling(24).mean()
    df["b00_roll24_std"]  = df["b00"].shift(1).rolling(24).std()
    df["b00_roll168_mean"] = df["b00"].shift(1).rolling(168).mean()

    # ------------------------------------------------------------------
    # Weather derived features
    # ------------------------------------------------------------------
    df["temp_lag24"]   = df["temperature_2m"].shift(24)
    df["temp_lag168"]  = df["temperature_2m"].shift(168)
    df["wbgt_lag1"]    = df["wbgt_approx"].shift(1)
    # Cooling/heating degree hour (base 20°C / 18°C)
    df["cdh_20"] = (df["temperature_2m"] - 20).clip(lower=0)
    df["hdh_18"] = (18 - df["temperature_2m"]).clip(lower=0)
    # Heat alert one-hot (drop reference)
    for lvl in [2, 3, 4]:
        df[f"heat_alert_ge{lvl}"] = (df["heat_alert_level"] >= lvl).astype(int)

    # ------------------------------------------------------------------
    # Target variants
    # ------------------------------------------------------------------
    df["y"] = df["b00"]                               # regression target (Head A)
    # Adaptive peak threshold = P95 of training (we'll compute on training only later)
    # Provisional binary: top 5% globally (will be re-computed per-fold)
    p95 = df["b00"].quantile(0.95)
    df["y_peak"] = (df["b00"] >= p95).astype(int)     # binary target (Head B)
    print(f"Provisional P95 threshold: {p95:.1f} kW  → positive class = {df['y_peak'].sum()} hrs ({df['y_peak'].mean()*100:.2f}%)")

    # Drop early rows with NaN due to lags AND any rows where the target y is NaN/zero
    df_clean = df.dropna(subset=[c for c in df.columns if c.startswith("b00_lag") or c.startswith("b00_roll")])
    df_clean = df_clean.dropna(subset=["y", "b00"])
    df_clean = df_clean[df_clean["b00"] > 1.0]  # drop meter-outage hours
    print(f"After lag-dropping NaNs + outage-dropping: {df_clean.shape}")

    # Save
    out_path = os.path.join(PROC, "features.parquet")
    df_clean.to_parquet(out_path)
    df_clean.to_csv(os.path.join(PROC, "features.csv"))
    print(f"💾 saved → {out_path}")

    # Feature dictionary
    fdict = []
    fdict.append("# Feature Dictionary\n")
    fdict.append(f"Generated at {pd.Timestamp.now()}\n")
    fdict.append(f"Shape after lag dropping: {df_clean.shape}\n")
    fdict.append(f"Period: {df_clean.index.min()} → {df_clean.index.max()}\n\n")
    fdict.append("## Path A vs Path B Day-Type Agreement\n")
    fdict.append(f"- Adjusted Rand Index: **{ari:.3f}**")
    fdict.append(f"- Normalized Mutual Info: **{nmi:.3f}**")
    fdict.append(f"- Path A classes (manual): {DAY_TYPE_MAP}")
    fdict.append(f"- Path B clusters (K-Means, K={K}): {day_cluster.value_counts().sort_index().to_dict()}\n\n")
    fdict.append("## Features by group\n")
    for c in df_clean.columns:
        fdict.append(f"- `{c}`  ({df_clean[c].dtype})  mean={df_clean[c].mean() if pd.api.types.is_numeric_dtype(df_clean[c]) else 'n/a'}")
    with open(f"{PROC}/feature_dict.md", "w") as f:
        f.write("\n".join(fdict))

    return df_clean


if __name__ == "__main__":
    main()
