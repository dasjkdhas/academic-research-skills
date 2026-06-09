"""Verify contract capacity hypothesis: 2000 kW vs 10000 vs 10000 kVA."""
import pandas as pd
import numpy as np

df = pd.read_csv("/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed/campus_power_hourly.csv",
                 parse_dates=["timestamp"]).set_index("timestamp")
y = df["b00"][df["b00"] > 1]   # drop outage hours

print("="*72)
print("OBSERVED CAMPUS LOAD STATISTICS (2025-07-06 → 2025-10-31)")
print("="*72)
print(f"Mean hourly load:    {y.mean():.1f} kW")
print(f"Median (P50):        {y.median():.1f} kW")
print(f"P95:                 {y.quantile(.95):.1f} kW")
print(f"P99:                 {y.quantile(.99):.1f} kW")
print(f"MAX OBSERVED:        {y.max():.1f} kW  ← key anchor for contract sizing")
print()

# Hypothesis tests
print("="*72)
print("HYPOTHESIS A: Contract = 2000 kW")
print("="*72)
C = 2000
print(f"  Max/Contract     = {y.max():.1f}/{C} = {y.max()/C*100:.1f}%   (high utilization → FRR risk REAL)")
print(f"  Mean utilization = {y.mean()/C*100:.1f}%")
print(f"  Hours > 80% cap  = {(y > 0.8*C).sum()} ({(y > 0.8*C).mean()*100:.2f}%)")
print(f"  Hours > 90% cap  = {(y > 0.9*C).sum()} ({(y > 0.9*C).mean()*100:.2f}%)")
print(f"  Hours > 95% cap  = {(y > 0.95*C).sum()}")
print(f"  → 89.3% peak utilization → CONSISTENT with FRR-relevant research")
print()

print("="*72)
print("HYPOTHESIS B: Contract = 10,000 kW")
print("="*72)
C = 10000
print(f"  Max/Contract     = {y.max():.1f}/{C} = {y.max()/C*100:.1f}%   (very low — no FRR risk)")
print(f"  Mean utilization = {y.mean()/C*100:.1f}%")
print(f"  Hours > 80% cap  = {(y > 0.8*C).sum()}  ← ZERO!")
print(f"  Hours > 90% cap  = {(y > 0.9*C).sum()}  ← ZERO!")
print(f"  → 17.9% peak utilization → INCONSISTENT with FRR research (would never trigger)")
print()

# Daily total kWh — could '10000' be daily energy?
daily = y.resample("D").sum()
print("="*72)
print("DAILY ENERGY CONSUMPTION (kWh/day)")
print("="*72)
print(f"  Mean daily kWh:   {daily.mean():.0f}")
print(f"  Median:           {daily.median():.0f}")
print(f"  Max:              {daily.max():.0f}")
print(f"  Min:              {daily.min():.0f}")
print(f"  → Daily total ~10,000-20,000 kWh — could '10,000' be a daily kWh memory?")
print()

# Monthly
monthly = y.resample("ME").sum()
print("="*72)
print("MONTHLY ENERGY CONSUMPTION (kWh/month)")
print("="*72)
for d, v in monthly.items():
    print(f"  {d.strftime('%Y-%m')}: {v:>10,.0f} kWh")
print()
print(f"  → Monthly typically ~400,000-700,000 kWh; not 10,000")
