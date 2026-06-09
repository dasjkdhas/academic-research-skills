"""Step 1a: Fetch hourly weather for Yamaguchi U Engineering Faculty (Tokiwa campus, Ube).

Source: Open-Meteo Historical API (ERA5 reanalysis)
Coordinates: 33.9522 N, 131.2614 E (Yamaguchi U Tokiwa Campus)
Closest JMA AMeDAS reference station: 宇部 (Ube) — distance ~0.8 km

Variables fetched:
  - temperature_2m       (°C)
  - relative_humidity_2m (%)
  - precipitation        (mm)
  - wind_speed_10m       (m/s)
  - surface_pressure     (hPa)
  - cloud_cover          (%)
  - shortwave_radiation  (W/m²) — for solar/HVAC modeling
  - dew_point_2m         (°C)   — for WBGT computation
  - apparent_temperature (°C)   — JMA-style perceived temperature
"""
import os, json, urllib.request, urllib.parse, warnings
warnings.filterwarnings('ignore')
import pandas as pd

LAT  = 33.9522
LON  = 131.2614
START = "2025-07-06"
END   = "2025-10-31"

OUT_DIR = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
os.makedirs(OUT_DIR, exist_ok=True)

params = {
    "latitude":  LAT,
    "longitude": LON,
    "start_date": START,
    "end_date":   END,
    "hourly": ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        "precipitation",
        "wind_speed_10m",
        "wind_direction_10m",
        "surface_pressure",
        "cloud_cover",
        "shortwave_radiation",
    ]),
    "timezone": "Asia/Tokyo",
}

url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
print(f"GET {url[:120]}...")

req = urllib.request.Request(url, headers={"User-Agent": "academic-research/1.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    payload = json.load(resp)

hourly = payload["hourly"]
df = pd.DataFrame(hourly)
df["timestamp"] = pd.to_datetime(df["time"])
df.drop(columns=["time"], inplace=True)
df = df[["timestamp"] + [c for c in df.columns if c != "timestamp"]]
df.set_index("timestamp", inplace=True)

# Restrict to whole-hour, ascending
df = df[~df.index.duplicated(keep="first")].sort_index()

print(f"\nWeather data: {df.shape}")
print(f"Period: {df.index.min()} → {df.index.max()}")
print(f"\nSummary:\n{df.describe().T[['mean','min','max','count']].round(2)}")

# WBGT proxy (simple): WBGT ≈ 0.7*Tw + 0.2*Tg + 0.1*Ta
# Without globe temperature, use: WBGT ≈ 0.567*T + 0.393*e + 3.94
# where e = vapor pressure (hPa) = (RH/100) * 6.105 * exp(17.27*T/(237.7+T))
import numpy as np
T = df["temperature_2m"]
RH = df["relative_humidity_2m"]
e = (RH/100) * 6.105 * np.exp(17.27*T/(237.7+T))
df["wbgt_approx"] = 0.567*T + 0.393*e + 3.94

# Heat-index alert level (JMA-style 危険レベル)
def heat_alert(w):
    if pd.isna(w): return np.nan
    if w >= 31:    return 4   # danger
    if w >= 28:    return 3   # severe warning
    if w >= 25:    return 2   # warning
    if w >= 21:    return 1   # caution
    return 0
df["heat_alert_level"] = df["wbgt_approx"].apply(heat_alert).astype("Int64")

csv_path = os.path.join(OUT_DIR, "weather_hourly.csv")
df.to_csv(csv_path)
try:
    df.to_parquet(os.path.join(OUT_DIR, "weather_hourly.parquet"))
except Exception:
    pass

meta = {
    "source": "Open-Meteo Historical API (ERA5 reanalysis)",
    "url":    "https://archive-api.open-meteo.com/v1/archive",
    "coordinates": {"latitude": LAT, "longitude": LON,
                    "site": "Yamaguchi U. Engineering Faculty, Tokiwa campus, Ube"},
    "reference_amedas_station": "宇部 (Ube), ~0.8 km away",
    "period_start": START,
    "period_end":   END,
    "hourly_variables": list(df.columns),
    "derived":  ["wbgt_approx (°C)", "heat_alert_level (0-4 JMA-style)"],
    "timezone": "Asia/Tokyo (JST, UTC+9)",
}
with open(os.path.join(OUT_DIR, "weather_hourly.meta.json"), "w") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)

print(f"\n💾 saved → {csv_path}")
print(f"\nHeat alert distribution: {df['heat_alert_level'].value_counts().sort_index().to_dict()}")
