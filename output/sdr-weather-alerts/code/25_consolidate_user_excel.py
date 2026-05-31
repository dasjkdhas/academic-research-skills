"""Consolidate user's 12 monthly Excel files (JFY2025) into clean hourly CSVs.

Each file has two sheets:
  消費電力   : 日付, 時間帯, 消費電力量[kWh]
  気象庁データ : 日付, 時間帯, 気温, 降水量, 日射量, 気圧..., 風速, 風向  (Ube AMeDAS)

Outputs:
  campus_power_hourly_JFY2025.csv          (timestamp, kwh)
  jma_weather_embedded_JFY2025.csv         (timestamp, temperature_2m,
                                            precipitation, wind_speed_10m,
                                            wind_direction_10m)
"""
import os, glob, re, json
import numpy as np
import pandas as pd

UP = "/root/.claude/uploads/905cf6cc-0b4c-49f0-9e74-2db9b9f734f6"
OUT = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"

WDIR16 = {
    "北":0.0,"北北東":22.5,"北東":45.0,"東北東":67.5,"東":90.0,"東南東":112.5,
    "南東":135.0,"南南東":157.5,"南":180.0,"南南西":202.5,"南西":225.0,
    "西南西":247.5,"西":270.0,"西北西":292.5,"北西":315.0,"北北西":337.5,
    "静穏":np.nan,"":np.nan,
}
EXCEL_EPOCH = pd.Timestamp("1899-12-30")

def to_ts(date_serial, t):
    """Combine forward-filled Excel date serial + time into a timestamp."""
    d = EXCEL_EPOCH + pd.Timedelta(days=int(date_serial))
    if hasattr(t, "hour"):
        h, m = t.hour, t.minute
    else:
        hh = str(t).split(":")
        h, m = int(hh[0]), int(hh[1]) if len(hh) > 1 else 0
    return pd.Timestamp(d) + pd.Timedelta(hours=h, minutes=m)

def num(x):
    if pd.isna(x): return np.nan
    s = re.sub(r"[^\d.\-]", "", str(x))
    try: return float(s)
    except ValueError: return np.nan

files = sorted(glob.glob(f"{UP}/*.xlsx"))
print(f"Files: {len(files)}")

power_rows, wx_rows = [], []
for f in files:
    base = os.path.basename(f)
    # --- power ---
    p = pd.read_excel(f, sheet_name="消費電力", header=0)
    p.columns = ["date", "time", "kwh"][:p.shape[1]]
    p["date"] = p["date"].ffill()
    for _, r in p.iterrows():
        if pd.isna(r["date"]) or pd.isna(r["time"]): continue
        try: ts = to_ts(r["date"], r["time"])
        except Exception: continue
        power_rows.append((ts, num(r["kwh"])))
    # --- weather (embedded JMA) ---
    w = pd.read_excel(f, sheet_name="気象庁データ", header=0)
    cols = list(w.columns)
    # locate columns by header text
    def find(key):
        for i, c in enumerate(cols):
            if key in str(c): return i
        return None
    i_date = 0; i_time = 1
    i_temp = find("気温"); i_prec = find("降水"); i_ws = find("風速"); i_wd = find("風向")
    w.iloc[:, i_date] = w.iloc[:, i_date].ffill()
    for _, r in w.iterrows():
        dser = r.iloc[i_date]; tval = r.iloc[i_time]
        if pd.isna(dser) or pd.isna(tval): continue
        try: ts = to_ts(dser, tval)
        except Exception: continue
        wdir_txt = str(r.iloc[i_wd]).strip() if i_wd is not None else ""
        wx_rows.append((
            ts,
            num(r.iloc[i_temp]) if i_temp is not None else np.nan,
            num(r.iloc[i_prec]) if i_prec is not None else np.nan,
            num(r.iloc[i_ws])   if i_ws   is not None else np.nan,
            WDIR16.get(wdir_txt, np.nan),
        ))
    print(f"  {base}: power+wx parsed")

power = (pd.DataFrame(power_rows, columns=["timestamp", "kwh"])
         .drop_duplicates("timestamp").set_index("timestamp").sort_index())
wx = (pd.DataFrame(wx_rows, columns=["timestamp","temperature_2m","precipitation",
                                     "wind_speed_10m","wind_direction_10m"])
      .drop_duplicates("timestamp").set_index("timestamp").sort_index())

power.to_csv(f"{OUT}/campus_power_hourly_JFY2025.csv")
wx.to_csv(f"{OUT}/jma_weather_embedded_JFY2025.csv")

print(f"\nPOWER: {len(power)} rows, {power.index.min()} → {power.index.max()}")
print(f"  valid kwh: {power['kwh'].notna().sum()}, missing: {power['kwh'].isna().sum()}")
print(f"  kwh range: {power['kwh'].min():.0f} – {power['kwh'].max():.0f}")
print(f"\nWEATHER (embedded JMA): {len(wx)} rows")
print(wx.describe().loc[['min','max','mean']].round(2).T.to_string())
print("\nmissing per col:")
print(wx.isna().sum().to_string())
print(f"\n💾 saved → campus_power_hourly_JFY2025.csv, jma_weather_embedded_JFY2025.csv")
