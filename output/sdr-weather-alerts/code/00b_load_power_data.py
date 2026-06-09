"""Step 0b: Load and merge all 4 electric power Excel files into a tidy hourly dataset.

Yamaguchi University Engineering Faculty — Central Electric Room
"""
import os
import json
import re
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

DATA_DIR = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_raw"
OUT_DIR  = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"

POWER_FILES = [
    "ba9615e5-_________202507060804.xlsm",
    "9285aea1-_________202508030901.xlsm",
    "e852e4f8-_________202508310921am8.xlsm",
    "115b3552-_________202509241026.xlsm",
]

# Stable schema (col_id → human-readable English-ish name)
SCHEMA = {
    "b00": ("0: 高圧受電盤(kWh)",                          "HV_main_total"),
    "b01": ("1: 工学部本館(kWh)",                          "engineering_main"),
    "b02": ("2: 総合研究棟2号館(kWh)",                     "research_2"),
    "b03": ("3: 予備(kWh)",                                "reserve"),
    "b04": ("4: 環境共生系専攻課棟(kWh)",                  "env_coexist_dept"),
    "b05": ("5: 社建実習棟(kWh)",                          "civil_practice"),
    "b06": ("6: D講義棟(kWh)",                             "lecture_hall_D"),
    "b07": ("7: 電気電子棟(kWh)",                          "elec_electronics"),
    "b08": ("8: 変電棟所内(kWh)",                          "substation_internal"),
    "b09": ("9: 図書館(kWh)",                              "library"),
    "b10": ("10: 知能情報棟(kWh)",                         "info_sci"),
    "b11": ("11: 先端研究棟(kWh)",                         "advanced_research"),
    "b12": ("12: メディア基盤センター(kWh)",                "media_center"),
    "b13": ("13: 福利厚生棟(kWh)",                         "welfare"),
    "b14": ("社会実習棟:連携盤T148_1(kWh)",                "civil_practice_T148_1"),
    "b15": ("社会実習棟:連携盤T148_2(kWh)",                "civil_practice_T148_2"),
    "b16": ("ﾒﾃﾞｨｱ基盤ｾﾝﾀｰ:屋上ｷｭｰﾋﾞｸﾙ 電力量(kWh)",   "media_center_rooftop"),
}
COL2ID = {v[0]: k for k, v in SCHEMA.items()}


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    new = {}
    for c in df.columns:
        cs = str(c).strip()
        if cs in COL2ID:
            new[c] = COL2ID[cs]
        else:
            m = re.match(r"^\s*(\d+)\s*:", cs)
            if m:
                new[c] = f"b{int(m.group(1)):02d}"
            else:
                # Best-effort fallback for the two T148 + rooftop cubicle columns
                if "T148_1" in cs:
                    new[c] = "b14"
                elif "T148_2" in cs:
                    new[c] = "b15"
                elif "屋上" in cs or "屋上ｷｭｰﾋﾞｸﾙ" in cs:
                    new[c] = "b16"
    df = df.rename(columns=new)
    return df


def _read_one(fpath: str) -> pd.DataFrame:
    fname = os.path.basename(fpath)
    print(f"\n→ {fname}")
    delta = pd.read_excel(fpath, sheet_name="電力使用量", engine="openpyxl")
    cum   = pd.read_excel(fpath, sheet_name="電力量",     engine="openpyxl")

    for df in (delta, cum):
        df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(subset=["timestamp"], inplace=True)
        df["timestamp"] = df["timestamp"].dt.round("h")
        df.set_index("timestamp", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)

    delta = _rename_columns(delta)
    cum   = _rename_columns(cum)

    # Keep only numeric, building-id columns
    bcols = [c for c in delta.columns if isinstance(c, str) and c.startswith("b")]
    delta = delta[bcols].apply(pd.to_numeric, errors="coerce")
    cum   = cum[[c for c in cum.columns if c in bcols]].apply(pd.to_numeric, errors="coerce")

    delta = delta[~delta.index.duplicated(keep="first")]
    cum   = cum[~cum.index.duplicated(keep="first")]

    # Decide per-column whether to use delta or diff(cum):
    out = pd.DataFrame(index=delta.index.union(cum.index).sort_values())
    for c in bcols:
        d_total = delta[c].abs().sum() if c in delta.columns else 0
        if d_total > 1.0:
            # Sanity: clip negatives (meter glitches)
            s = delta[c].reindex(out.index).clip(lower=0)
        else:
            # Compute diff from cumulative
            cu = cum[c].reindex(out.index).interpolate(limit=1)
            s = cu.diff().clip(lower=0)
        out[c] = s

    # Drop rows that are entirely NaN
    out = out.dropna(how="all")
    print(f"   parsed {out.shape}  {out.index.min()} → {out.index.max()}  total b00={out['b00'].sum():.0f} kWh")
    return out


def merge_power_files() -> pd.DataFrame:
    parts = []
    for f in POWER_FILES:
        p = os.path.join(DATA_DIR, f)
        if not os.path.exists(p):
            continue
        try:
            parts.append(_read_one(p))
        except Exception as e:
            print(f"   ERROR {f}: {e}")

    combined = pd.concat(parts, axis=0)
    # For overlapping timestamps, average across files (more stable than last-wins
    # because overlapping monthly exports should agree)
    combined = combined.groupby(combined.index).mean().sort_index()

    # Drop all-zero columns (e.g., b03 reserve)
    keep = [c for c in combined.columns if combined[c].fillna(0).abs().sum() > 1.0]
    combined = combined[keep]
    return combined


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    merged = merge_power_files()

    print("\n" + "=" * 78)
    print("MERGED HOURLY POWER DATA — Yamaguchi U. Engineering Faculty")
    print("=" * 78)
    print(f"Shape:  {merged.shape}")
    print(f"Period: {merged.index.min()} → {merged.index.max()}")
    print(f"Hours:  {len(merged)}  ({len(merged)/24:.1f} days)")

    expected = pd.date_range(merged.index.min(), merged.index.max(), freq="h")
    missing  = expected.difference(merged.index)
    print(f"Expected: {len(expected)}; missing: {len(missing)} ({len(missing)/len(expected)*100:.2f}%)")

    print(f"\nPer-column summary (kW per hour):")
    print(f"{'col':4s}  {'building':25s}  {'mean':>9s}  {'min':>7s}  {'max':>8s}  {'nan%':>6s}")
    print("-" * 72)
    for c in merged.columns:
        s = merged[c]
        bname = SCHEMA.get(c, ('', 'unknown'))[1]
        print(f"{c:4s}  {bname:25s}  {s.mean():9.2f}  {s.min():7.2f}  {s.max():8.2f}  {s.isna().mean()*100:6.1f}")

    # Sanity check: how well does sum(subs) ≈ b00?
    sub_cols = [c for c in merged.columns if c not in ("b00", "b03")]
    sum_subs = merged[sub_cols].sum(axis=1)
    diff = merged["b00"] - sum_subs
    print(f"\nSanity (b00 vs sum of submeters):")
    print(f"  mean b00       = {merged['b00'].mean():.2f}")
    print(f"  mean sum_subs  = {sum_subs.mean():.2f}")
    print(f"  mean residual  = {diff.mean():.2f}  (= unsubmetered load incl. outdoor/HVAC/etc.)")
    print(f"  residual_ratio = {diff.mean()/merged['b00'].mean()*100:.1f}% of total")

    # Save
    csv_path = os.path.join(OUT_DIR, "campus_power_hourly.csv")
    merged.to_csv(csv_path)
    try:
        merged.to_parquet(os.path.join(OUT_DIR, "campus_power_hourly.parquet"))
    except Exception:
        pass
    print(f"\n💾 saved → {csv_path}")

    meta = {
        "source": "Yamaguchi University Engineering Faculty - Central Electric Room",
        "site_location": "Tokiwa campus, Ube city, Yamaguchi prefecture, Japan",
        "files_used": POWER_FILES,
        "period_start": str(merged.index.min()),
        "period_end":   str(merged.index.max()),
        "total_hours":  int(len(merged)),
        "missing_hours": int(len(missing)),
        "columns": {c: SCHEMA.get(c, ('', 'unknown'))[1] for c in merged.columns},
        "target_column": "b00",
        "target_name":   "HV_main_total_kW",
        "contract_capacity_kW": 2000,
        "submetered_fraction": float(sum_subs.mean() / merged["b00"].mean()),
        "residual_unsubmetered_fraction": float(diff.mean() / merged["b00"].mean()),
    }
    with open(os.path.join(OUT_DIR, "campus_power_hourly.meta.json"), "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"💾 saved → campus_power_hourly.meta.json")


if __name__ == "__main__":
    main()
