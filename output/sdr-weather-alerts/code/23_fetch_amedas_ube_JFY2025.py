"""Scrape JMA AMeDAS Ube (宇部) hourly observations for JFY2025.

Station: 宇部 (Ube), prec_no=81, block_no=0778, type AMeDAS (4-element)
Period:  2025-04-01 → 2026-03-31 (Japanese fiscal year 2025)
Endpoint: hourly_a1.php (one day per request)

Confirmed measured columns at Ube (others are '///' unmeasured):
  precipitation (mm), temperature (degC), wind_speed (m/s), wind_direction (16-pt JP text)
  → matches the user's stated AMeDAS variable boundary exactly.

Output: amedas_ube_JFY2025.csv  (timestamp, precipitation, temperature_2m,
                                 wind_speed_10m, wind_direction_10m)
"""
import os, re, time, json, urllib.request
import numpy as np
import pandas as pd
from datetime import date, timedelta

OUT_DIR = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
PREC, BLOCK = 81, "0778"
START = date(2025, 4, 1)
END   = date(2026, 3, 31)

WDIR16 = {
    "北": 0.0, "北北東": 22.5, "北東": 45.0, "東北東": 67.5,
    "東": 90.0, "東南東": 112.5, "南東": 135.0, "南南東": 157.5,
    "南": 180.0, "南南西": 202.5, "南西": 225.0, "西南西": 247.5,
    "西": 270.0, "西北西": 292.5, "北西": 315.0, "北北西": 337.5,
    "静穏": np.nan,
}

def clean_num(tok):
    """Parse a JMA numeric cell; return np.nan for missing markers."""
    tok = tok.strip()
    if tok in ("", "///", "×", "--", "#", ")", "]"):
        return np.nan
    # strip trailing quality symbols ] ) #
    tok = re.sub(r"[^\d.\-]", "", tok)
    if tok in ("", "-", "."):
        return np.nan
    try:
        return float(tok)
    except ValueError:
        return np.nan

def fetch_day(d, retries=3):
    url = (f"https://www.data.jma.go.jp/stats/etrn/view/hourly_a1.php?"
           f"prec_no={PREC}&block_no={BLOCK}&year={d.year}&month={d.month}&day={d.day}&view=")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
            rows = re.findall(r'<tr class="mtx"[^>]*>(.*?)</tr>', html, re.S)
            recs = []
            for r in rows:
                cells = [re.sub(r"<[^>]+>", "", c).strip()
                         for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
                if len(cells) < 8:
                    continue
                # cells: [hour, precip, temp, c3, c4, c5, wind_speed, wind_dir, ...]
                try:
                    hour = int(cells[0])
                except ValueError:
                    continue
                precip = clean_num(cells[1])
                temp   = clean_num(cells[2])
                wspd   = clean_num(cells[6])
                wdir_t = cells[7].strip()
                wdir   = WDIR16.get(wdir_t, np.nan)
                # timestamp: hour 1..24, hour 24 → next day 00:00
                ts = pd.Timestamp(d) + pd.Timedelta(hours=hour)
                recs.append((ts, precip, temp, wspd, wdir, wdir_t))
            return recs
        except Exception as e:
            if attempt == retries - 1:
                print(f"  ! failed {d}: {e}")
                return []
            time.sleep(1.5 * (attempt + 1))
    return []

all_recs = []
d = START
total_days = (END - START).days + 1
done = 0
while d <= END:
    all_recs.extend(fetch_day(d))
    done += 1
    if done % 30 == 0 or d == END:
        print(f"  {done}/{total_days} days  (latest {d}, rows so far {len(all_recs)})")
    time.sleep(0.15)
    d += timedelta(days=1)

df = pd.DataFrame(all_recs, columns=["timestamp", "precipitation", "temperature_2m",
                                     "wind_speed_10m", "wind_direction_10m", "wind_dir_text"])
df = df.drop_duplicates(subset="timestamp").set_index("timestamp").sort_index()

print(f"\nTotal hourly records: {len(df)}")
print(f"Range: {df.index.min()} → {df.index.max()}")
print("\nMissing per column:")
print(df[["precipitation","temperature_2m","wind_speed_10m","wind_direction_10m"]].isna().sum().to_string())
print("\nValue ranges:")
print(df[["precipitation","temperature_2m","wind_speed_10m","wind_direction_10m"]]
      .describe().loc[["min","max","mean"]].round(2).T.to_string())

csv_path = os.path.join(OUT_DIR, "amedas_ube_JFY2025.csv")
df.drop(columns=["wind_dir_text"]).to_csv(csv_path)
df.to_csv(os.path.join(OUT_DIR, "amedas_ube_JFY2025_with_wdir_text.csv"))

meta = {
    "source": "JMA 過去の気象データ (hourly_a1.php)",
    "station": "宇部 (Ube) AMeDAS", "prec_no": PREC, "block_no": BLOCK,
    "station_type": "AMeDAS 4-element (precip, temp, wind speed, wind dir)",
    "period": f"{START} → {END}",
    "n_hours": int(len(df)),
    "timezone": "Asia/Tokyo (JST)",
    "columns": ["precipitation (mm)", "temperature_2m (degC)",
                "wind_speed_10m (m/s)", "wind_direction_10m (deg, 16-pt)"],
    "note": "Humidity / sunshine / pressure NOT measured at Ube (confirmed '///').",
}
with open(os.path.join(OUT_DIR, "amedas_ube_JFY2025.meta.json"), "w") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)
print(f"\n💾 saved → {csv_path}")
