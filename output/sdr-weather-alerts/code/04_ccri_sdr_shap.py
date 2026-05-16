"""Step 7+8+9: Build CCRI risk index, run SDR counterfactual, generate SHAP explanations.

CCRI(t) = w1·ŷ(t)/C_adaptive + w2·P(peak|t) + w3·Ê[duration|t]
where:
  - C_adaptive   : 80% percentile of training data (used as 'effective capacity')
  - P(peak|t)    : LightGBM head B output
  - duration_t   : rolling 6h forward expected high-risk hour count
"""
import os, json, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import joblib

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures"

sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.05)

bundle = joblib.load(f"{RES}/lightgbm_models.pkl")
model_reg = bundle["model_reg"]
model_cls = bundle["model_cls"]
features  = bundle["features"]
p95_thr   = bundle["p95_thr"]

test_df = pd.read_parquet(f"{PROC}/test_df_with_preds.parquet")
full_df = pd.read_parquet(f"{PROC}/features.parquet")

# Recompute thresholds based on full training period (P50, P80, P95)
train_df = full_df.iloc[:bundle["split_pt"]]
p50 = train_df["b00"].quantile(0.50)
p80 = train_df["b00"].quantile(0.80)
p95 = train_df["b00"].quantile(0.95)
print(f"Training thresholds: P50={p50:.1f}  P80={p80:.1f}  P95={p95:.1f} kW")

# ============================================================================
# STEP 7: CCRI Risk Index
# ============================================================================
print("\n" + "=" * 70)
print("STEP 7: CCRI Risk Index")
print("=" * 70)

C_adaptive = p80   # treat P80 as effective capacity for risk normalization

# Compute predictions over the test_df (already in test_df)
yhat = test_df["pred_reg"]
ppk  = test_df["pred_cls_prob"]

# Duration: expected number of next-6h hours where pred ≥ p80
duration = []
for i in range(len(test_df)):
    end = min(i + 6, len(test_df))
    duration.append((yhat.iloc[i:end] >= p80).sum())
test_df["pred_duration_6h"] = duration

# Weights tuned by training-set F1 maximization for "High" tier
# (For Step 0 demo, fixed weights are fine — paper will calibrate)
w1, w2, w3 = 0.50, 0.30, 0.20

test_df["CCRI"] = (
    w1 * (test_df["pred_reg"] / C_adaptive).clip(0, 2)
    + w2 * test_df["pred_cls_prob"]
    + w3 * (test_df["pred_duration_6h"] / 6)
)

# 3-tier classification
def tier(c):
    if c >= 0.85: return "Critical"
    if c >= 0.65: return "High"
    return "Normal"
test_df["risk_tier"] = test_df["CCRI"].apply(tier)
print(f"Tier distribution in test set:\n{test_df['risk_tier'].value_counts()}")

# Plot: Predicted vs Actual with CCRI tier overlay
fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(test_df.index, test_df["b00"], lw=1.0, label="Actual load (kW)", color="#1f4e79")
ax.plot(test_df.index, yhat, lw=1.0, label="LightGBM forecast", color="#d62728", alpha=0.8)
ax.axhline(p80, ls="--", color="orange", lw=1, label=f"P80 (training) = {p80:.0f} kW")
ax.axhline(p95, ls=":", color="red", lw=1, label=f"P95 (training) = {p95:.0f} kW")
crit  = test_df[test_df["risk_tier"] == "Critical"]
high  = test_df[test_df["risk_tier"] == "High"]
ax.scatter(crit.index,  crit["b00"],  color="red",    s=18, label=f"CCRI Critical (n={len(crit)})", zorder=5)
ax.scatter(high.index,  high["b00"],  color="orange", s=10, label=f"CCRI High (n={len(high)})", zorder=4, alpha=0.6)
ax.set_title("Step 7: CCRI Risk Tagging — Test Period")
ax.set_xlabel("Time"); ax.set_ylabel("Load (kW)"); ax.legend(loc="upper right", fontsize=9)
plt.xticks(rotation=20, ha="right"); plt.tight_layout()
plt.savefig(f"{FIG}/fig08_ccri_test.png", dpi=130); plt.close()
print("✓ fig08: CCRI tagging")

# Save CCRI per timestamp
test_df[["b00", "pred_reg", "pred_cls_prob", "pred_duration_6h", "CCRI", "risk_tier"]].to_csv(
    f"{RES}/ccri_results.csv"
)

# ============================================================================
# STEP 8: SDR Action Counterfactual (Tier 1)
# ============================================================================
print("\n" + "=" * 70)
print("STEP 8: SDR Action-Benefit Decomposition (Tier 1, submetered buildings)")
print("=" * 70)

# Building list — Tier 1 candidates (top 4 by share)
TIER1_BUILDINGS = ["b07", "b01", "b05", "b13"]   # elec_electronics, eng_main, civil_practice, welfare
SDR_ACTIONS = {
    "A1_cooling_setpoint_up_2C": {
        "description": "Raise cooling setpoint by 2°C in afternoon",
        "active_hours": list(range(11, 18)),       # 11:00-17:59
        "active_buildings": ["b01", "b07", "b13"],  # HVAC-intensive
        "reduction_pct": 0.12,                      # empirical: 2°C ≈ 8-15%
    },
    "A2_lighting_dim_30pct": {
        "description": "Dim non-essential lighting by 30%",
        "active_hours": list(range(13, 16)),       # afternoon
        "active_buildings": ["b06", "b09"],         # lecture hall, library
        "reduction_pct": 0.30 * 0.2,                # lighting ~20% of bldg, dim 30%
    },
    "A3_lab_equipment_defer": {
        "description": "Defer non-critical lab equipment 1h",
        "active_hours": [14, 15, 16],
        "active_buildings": ["b07", "b05"],         # elec_electronics, civil_practice (labs)
        "reduction_pct": 0.18,
    },
    "A4_elevator_reduce": {
        "description": "Reduce elevator service to 50%",
        "active_hours": list(range(11, 17)),
        "active_buildings": ["b01"],                # main bldg has most elevators
        "reduction_pct": 0.03,
    },
}

# Counterfactual: for each Critical/High CCRI hour, simulate each action
critical_hours = test_df[test_df["risk_tier"].isin(["High", "Critical"])]
print(f"Hours in High/Critical tier: {len(critical_hours)}")
if len(critical_hours) == 0:
    # Fallback: use top-5% predicted hours
    thr = test_df["pred_reg"].quantile(0.95)
    critical_hours = test_df[test_df["pred_reg"] >= thr]
    print(f"  ↳ fallback: using top-5% predicted hours (n={len(critical_hours)})")

# Build 3D matrix: action × building × CCRI-hour
results_3d = []
for action_id, action in SDR_ACTIONS.items():
    for b in TIER1_BUILDINGS:
        if b not in action["active_buildings"]:
            continue
        # Reduction estimate per active hour for this building
        for ts in critical_hours.index:
            if ts.hour not in action["active_hours"]:
                continue
            b_load_base = full_df.loc[ts, b] if b in full_df.columns else 0
            delta = -b_load_base * action["reduction_pct"]
            results_3d.append({
                "timestamp": ts,
                "action_id": action_id,
                "building":  b,
                "base_load_kW":   float(b_load_base),
                "delta_kW":       float(delta),
                "reduction_pct":  action["reduction_pct"],
            })
sdr_3d = pd.DataFrame(results_3d)
print(f"\nSDR Tier-1 matrix: {sdr_3d.shape}  (action × building × hour records)")

# Aggregate to action × building (mean Δ kW per applicable hour)
agg_ab = sdr_3d.groupby(["action_id", "building"]).agg(
    mean_delta_kW=("delta_kW", "mean"),
    total_delta_kW=("delta_kW", "sum"),
    n_hours=("delta_kW", "size")
).round(2)
print("\nAction × Building summary (mean Δ kW per applicable hour):")
print(agg_ab.to_string())
agg_ab.to_csv(f"{RES}/sdr_action_building_matrix.csv")

# Total system-wide peak reduction if all actions applied simultaneously
# For each timestamp, sum all action deltas
total_per_hour = sdr_3d.groupby("timestamp")["delta_kW"].sum()
sim_load = critical_hours["b00"].copy()
common_idx = sim_load.index.intersection(total_per_hour.index)
sim_load.loc[common_idx] = sim_load.loc[common_idx] + total_per_hour.loc[common_idx]

base_peak = critical_hours["b00"].max()
sim_peak  = sim_load.max()
peak_reduction_kW = base_peak - sim_peak
peak_reduction_pct = peak_reduction_kW / base_peak * 100

# RDCR (Risk Duration Compression Ratio)
risk_t_base = len(critical_hours)
risk_t_sim  = (sim_load >= p80).sum()
RDCR = 1 - risk_t_sim / max(risk_t_base, 1)

print("\n--- Aggregate SDR Impact ---")
print(f"  Baseline peak in critical window:    {base_peak:.1f} kW")
print(f"  Simulated peak after all actions:    {sim_peak:.1f} kW")
print(f"  → Peak reduction:                    {peak_reduction_kW:.1f} kW ({peak_reduction_pct:.1f}%)")
print(f"  Baseline risk hours:                 {risk_t_base}")
print(f"  Simulated risk hours:                {risk_t_sim}")
print(f"  → RDCR (Risk Duration Compression):  {RDCR*100:.1f}%")

# Plot SDR action heatmap
fig, ax = plt.subplots(figsize=(8.5, 4))
pivot_ab = agg_ab["mean_delta_kW"].unstack("building")
sns.heatmap(pivot_ab, annot=True, fmt=".1f", cmap="RdBu_r", center=0,
            cbar_kws={"label": "Mean Δ kW per applicable hour"}, ax=ax)
ax.set_title("Step 8: SDR Action × Building Contribution (Tier 1)")
ax.set_xlabel("Building"); ax.set_ylabel("SDR Action")
plt.tight_layout()
plt.savefig(f"{FIG}/fig09_sdr_action_matrix.png", dpi=130); plt.close()
print("✓ fig09: SDR action-building heatmap")

# Plot baseline vs simulated load
fig, ax = plt.subplots(figsize=(15, 4.5))
ax.plot(critical_hours.index, critical_hours["b00"], lw=1.2, color="#d62728", label="Baseline (high-risk hours)")
ax.plot(sim_load.index, sim_load.values, lw=1.2, color="#1f4e79", label="After SDR actions (simulated)")
ax.axhline(p80, ls="--", color="orange", label=f"P80 risk threshold ({p80:.0f} kW)")
ax.set_title("Step 8: SDR Counterfactual — peak reduction & risk-duration compression")
ax.set_xlabel("Time"); ax.set_ylabel("Load (kW)"); ax.legend()
plt.xticks(rotation=20, ha="right"); plt.tight_layout()
plt.savefig(f"{FIG}/fig10_sdr_counterfactual.png", dpi=130); plt.close()

# ============================================================================
# STEP 9: SHAP Explanations
# ============================================================================
print("\n" + "=" * 70)
print("STEP 9: SHAP Interpretability")
print("=" * 70)

X_te = test_df[features]
explainer = shap.TreeExplainer(model_reg)
shap_values = explainer.shap_values(X_te.sample(min(500, len(X_te)), random_state=42))

# Summary plot
shap.summary_plot(shap_values, X_te.sample(min(500, len(X_te)), random_state=42),
                  show=False, max_display=15)
plt.tight_layout()
plt.savefig(f"{FIG}/fig11_shap_summary.png", dpi=130, bbox_inches="tight"); plt.close()
print("✓ fig11: SHAP summary")

# Feature importance bar plot
shap.summary_plot(shap_values, X_te.sample(min(500, len(X_te)), random_state=42),
                  plot_type="bar", show=False, max_display=15)
plt.tight_layout()
plt.savefig(f"{FIG}/fig12_shap_importance.png", dpi=130, bbox_inches="tight"); plt.close()
print("✓ fig12: SHAP importance bar")

# Top features by mean(|SHAP|)
mean_abs = np.abs(shap_values).mean(axis=0)
top10_idx = np.argsort(mean_abs)[::-1][:10]
sample_X = X_te.sample(min(500, len(X_te)), random_state=42)
top10 = [(sample_X.columns[i], float(mean_abs[i])) for i in top10_idx]
print("\nTop-10 features by mean(|SHAP|):")
for f, v in top10:
    print(f"  {f:30s}  {v:.2f}")

# ============================================================================
# Persist final summary
# ============================================================================
final = {
    "step7_ccri": {
        "thresholds": {"P50": float(p50), "P80": float(p80), "P95": float(p95)},
        "C_adaptive_used": float(C_adaptive),
        "weights_w1_w2_w3": [w1, w2, w3],
        "tier_distribution": test_df["risk_tier"].value_counts().to_dict(),
        "tier_definition": {
            "Critical": "CCRI >= 0.85",
            "High":     "0.65 <= CCRI < 0.85",
            "Normal":   "CCRI < 0.65",
        },
    },
    "step8_sdr": {
        "tier1_buildings": TIER1_BUILDINGS,
        "n_critical_hours_analyzed": int(len(critical_hours)),
        "baseline_peak_kW": float(base_peak),
        "simulated_peak_kW": float(sim_peak),
        "peak_reduction_kW": float(peak_reduction_kW),
        "peak_reduction_pct": float(peak_reduction_pct),
        "RDCR": float(RDCR),
        "actions": {k: {"desc": v["description"], "reduction_pct": v["reduction_pct"]}
                    for k, v in SDR_ACTIONS.items()},
    },
    "step9_shap": {
        "n_samples_explained": 500,
        "top10_features": [{"feature": f, "mean_abs_shap": v} for f, v in top10],
    },
}
with open(f"{RES}/step7_8_9_summary.json", "w") as f:
    json.dump(final, f, indent=2)
print(f"\n💾 final summary → {RES}/step7_8_9_summary.json")
print(f"💾 figures → {FIG}/fig08-12")
