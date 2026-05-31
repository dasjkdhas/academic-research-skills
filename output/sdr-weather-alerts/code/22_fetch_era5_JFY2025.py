"""Fetch ERA5 hourly weather for Yamaguchi U Tokiwa Campus, JFY 2025.

Period: 2025-04-01 → 2026-03-31 (Japanese fiscal year 2025)
Source: Open-Meteo Historical API (ERA5 reanalysis + ERA5T early release)
Coords: 33.9522 N, 131.2614 E (Ube, near 宇部 AMeDAS station ~0.8 km away)

IMPORTANT — Variable usage policy for Track B paper (low-data framework):
  CORE variables permitted in main analysis (match AMeDAS Ube observation):
    - temperature_2m       ✓
    - precipitation        ✓
    - wind_speed_10m       ✓
    - wind_direction_10m   ✓

  EXTRA variables fetched (NOT permitted in Track B main analysis;
  available for Track A advisory system / sensitivity analysis only):
    - relative_humidity_2m, dew_point_2m, apparent_temperature
    - surface_pressure, cloud_cover, shortwave_radiation

Note on 2026 coverage: ERA5 archive typically lags ~2-3 months; ERA5T
(early release) extends to a few days before today. Open-Meteo blends
both. Some most-recent days may have provisional values.
"""
import os, json, urllib.request, urllib.parse, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd

LAT  = 33.9522
LON  = 131.2614
START = "2025-04-01"
END   = "2026-03-31"

OUT_DIR = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
os.makedirs(OUT_DIR, exist_ok=True)

CORE_VARS = [
    "temperature_2m",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
]
EXTRA_VARS = [
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "surface_pressure",
    "cloud_cover",
    "shortwave_radiation",
]
ALL_VARS = CORE_VARS + EXTRA_VARS

params = {
    "latitude":  LAT,
    "longitude": LON,
    "start_date": START,
    "end_date":   END,
    "hourly": ",".join(ALL_VARS),
    "timezone": "Asia/Tokyo",
}
url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
print(f"GET {url[:140]}...")
req = urllib.request.Request(url, headers={"User-Agent": "academic-research/1.0"})
with urllib.request.urlopen(req, timeout=120) as resp:
    payload = json.load(resp)

hourly = payload["hourly"]
df = pd.DataFrame(hourly)
df["timestamp"] = pd.to_datetime(df["time"])
df.drop(columns=["time"], inplace=True)
df = df[["timestamp"] + ALL_VARS].set_index("timestamp")
df = df[~df.index.duplicated(keep="first")].sort_index()

print(f"\nFetched: {df.shape}")
print(f"Period: {df.index.min()} → {df.index.max()}")
print(f"Expected hours: {(pd.Timestamp(END) - pd.Timestamp(START)).days * 24 + 24:,}")
print(f"Got hours: {len(df):,}")

# Coverage report
expected_idx = pd.date_range(f"{START} 00:00", f"{END} 23:00", freq="h", tz="Asia/Tokyo")
expected_idx = expected_idx.tz_localize(None)
missing = expected_idx.difference(df.index)
print(f"Missing hours: {len(missing)}")
if len(missing) > 0:
    print(f"  First missing: {missing[0]}, Last missing: {missing[-1]}")

# Per-variable coverage
print("\nPer-variable non-null counts:")
print(df.notna().sum().to_string())

# Quick value-range sanity check
print("\nValue ranges:")
print(df.describe().loc[["min", "max", "mean", "std"]].round(2).T.to_string())

# Save CSV
csv_path = os.path.join(OUT_DIR, "era5_yamaguchi_JFY2025.csv")
df.to_csv(csv_path)
try:
    df.to_parquet(os.path.join(OUT_DIR, "era5_yamaguchi_JFY2025.parquet"))
except Exception as e:
    print(f"(parquet skipped: {e})")

# Two split exports: CORE only (AMeDAS-equivalent) for Track B; EXTRA for Track A reference
core_csv  = os.path.join(OUT_DIR, "era5_yamaguchi_JFY2025_CORE_AMeDASequiv.csv")
extra_csv = os.path.join(OUT_DIR, "era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv")
df[CORE_VARS].to_csv(core_csv)
df[EXTRA_VARS].to_csv(extra_csv)

# Metadata
meta = {
    "source": "Open-Meteo Historical API (ERA5 + ERA5T)",
    "url":    "https://archive-api.open-meteo.com/v1/archive",
    "coordinates": {"latitude": LAT, "longitude": LON,
                    "site": "Yamaguchi U. Engineering Faculty, Tokiwa campus, Ube"},
    "reference_amedas_station": "宇部 (Ube), ~0.8 km",
    "period_start": START,
    "period_end":   END,
    "n_hours":      int(len(df)),
    "n_missing":    int(len(missing)),
    "timezone":     "Asia/Tokyo (JST, UTC+9)",
    "fiscal_year":  "Japanese FY 2025 (April 1 2025 → March 31 2026)",
    "files": {
        "all_variables":  "era5_yamaguchi_JFY2025.csv (+ .parquet)",
        "core_AMeDASequiv": "era5_yamaguchi_JFY2025_CORE_AMeDASequiv.csv",
        "extra_TrackA_only": "era5_yamaguchi_JFY2025_EXTRA_TrackA_only.csv",
    },
    "variables_CORE_for_TrackB_paper": CORE_VARS,
    "variables_EXTRA_TrackA_only": EXTRA_VARS,
    "usage_policy": (
        "For the Energy-journal Track B paper (low-data framework), use ONLY "
        "the CORE variables (AMeDAS-equivalent). EXTRA variables are kept for "
        "Track A (advisory-system reference) and sensitivity/limitations only."
    ),
}
with open(os.path.join(OUT_DIR, "era5_yamaguchi_JFY2025.meta.json"), "w") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)

print(f"\n💾 saved:")
print(f"   → {csv_path}")
print(f"   → {core_csv}")
print(f"   → {extra_csv}")
print(f"   → era5_yamaguchi_JFY2025.meta.json")
