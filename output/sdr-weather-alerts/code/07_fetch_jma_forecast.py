"""Fetch JMA MSM historical forecast data for Yamaguchi (Tokiwa Campus, Ube).

Uses Open-Meteo Historical Forecast API which provides hourly forecast data
from JMA Meso-Scale Model (MSM) - Japan's high-resolution operational
numerical weather prediction.

Two complementary fetches:
  1. JMA MSM forecast — what would have been "tomorrow's forecast" yesterday
  2. JMA GSM forecast — longer range global model

These are juxtaposed with ERA5 observed data already in our dataset.
"""
import os, json, urllib.request, urllib.parse, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
LAT, LON = 33.9522, 131.2614
START, END = "2025-07-06", "2025-10-31"


def fetch_model(model_id: str, name: str) -> pd.DataFrame:
    """Fetch hourly forecast/analysis from given JMA model."""
    params = {
        "latitude": LAT, "longitude": LON,
        "start_date": START, "end_date": END,
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
        "models": model_id,
        "timezone": "Asia/Tokyo",
    }
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    print(f"→ {name}: {url[:100]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "academic-research/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.load(resp)
    df = pd.DataFrame(payload["hourly"])
    df["timestamp"] = pd.to_datetime(df["time"])
    df.drop(columns=["time"], inplace=True)
    df.set_index("timestamp", inplace=True)
    df = df.add_suffix(f"_{name}")
    return df


def main():
    msm = fetch_model("jma_msm", "msm")
    gsm = fetch_model("jma_gsm", "gsm")

    print(f"\nMSM shape: {msm.shape}, period {msm.index.min()} → {msm.index.max()}")
    print(f"GSM shape: {gsm.shape}, period {gsm.index.min()} → {gsm.index.max()}")
    print(f"MSM nan%: {msm.isna().mean().mean()*100:.1f}%")
    print(f"GSM nan%: {gsm.isna().mean().mean()*100:.1f}%")

    fcst = msm.join(gsm, how="outer")
    fcst.to_csv(f"{PROC}/jma_forecast_hourly.csv")
    try:
        fcst.to_parquet(f"{PROC}/jma_forecast_hourly.parquet")
    except Exception:
        pass

    # Quick error analysis vs ERA5 observed (which we already have)
    obs = pd.read_csv(f"{PROC}/weather_hourly.csv",
                      parse_dates=["timestamp"]).set_index("timestamp")
    obs = obs.add_suffix("_obs")
    cmp = obs.join(fcst, how="inner")

    print("\n" + "=" * 70)
    print("FORECAST ERROR ANALYSIS (JMA MSM vs ERA5 observed)")
    print("=" * 70)
    pairs = [
        ("temperature_2m",       "°C"),
        ("relative_humidity_2m", "%"),
        ("precipitation",        "mm"),
        ("wind_speed_10m",       "m/s"),
        ("surface_pressure",     "hPa"),
        ("cloud_cover",          "%"),
        ("shortwave_radiation",  "W/m²"),
    ]
    rows = []
    for v, u in pairs:
        for model in ("msm", "gsm"):
            col_obs = f"{v}_obs"
            col_fcst = f"{v}_{model}"
            if col_obs in cmp.columns and col_fcst in cmp.columns:
                d = cmp[[col_obs, col_fcst]].dropna()
                if len(d) > 100:
                    mae  = (d[col_fcst] - d[col_obs]).abs().mean()
                    rmse = np.sqrt(((d[col_fcst] - d[col_obs])**2).mean())
                    bias = (d[col_fcst] - d[col_obs]).mean()
                    corr = d[col_obs].corr(d[col_fcst])
                    rows.append({"variable": v, "unit": u, "model": model.upper(),
                                 "MAE": mae, "RMSE": rmse, "bias": bias, "r": corr, "n": len(d)})
    err_df = pd.DataFrame(rows)
    print(err_df.round(2).to_string(index=False))
    err_df.to_csv(f"{PROC}/forecast_vs_obs_error.csv", index=False)

    # Save metadata
    meta = {
        "source": "Open-Meteo Historical Forecast API",
        "url":    "https://historical-forecast-api.open-meteo.com/v1/forecast",
        "models": {
            "jma_msm": "JMA Meso-Scale Model (5km, 39-hr horizon, 8x daily)",
            "jma_gsm": "JMA Global Spectral Model (20km, 264-hr horizon)",
        },
        "coordinates": [LAT, LON],
        "period": [START, END],
        "interpretation": "These are the *operational forecast* data products that JMA actually published. Hourly MSM data approximates what was available as 'day-ahead forecast' for SDR planning.",
    }
    with open(f"{PROC}/jma_forecast.meta.json", "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\n💾 saved → jma_forecast_hourly.csv ({fcst.shape})")
    print(f"💾 saved → forecast_vs_obs_error.csv")


if __name__ == "__main__":
    main()
