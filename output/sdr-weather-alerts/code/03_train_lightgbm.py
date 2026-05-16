"""Step 3 + 5: Train LightGBM (regression Head A + classification Head B) using walk-forward CV.

Also runs a baseline: persistence + linear regression for comparison.
Path A (manual day_type) vs Path B (K-Means cluster) head-to-head comparison included.
"""
import os, json, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                              f1_score, precision_score, recall_score,
                              roc_auc_score, average_precision_score, confusion_matrix)
from sklearn.linear_model import LinearRegression

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
os.makedirs(RES, exist_ok=True)

# ---------------------------------------------------------------------------
df = pd.read_parquet(f"{PROC}/features.parquet")
print(f"Loaded: {df.shape}  period {df.index.min()} → {df.index.max()}")

# Features and targets
DROP_COLS = ["y", "y_peak", "day_type", "holiday_name", "dow_name", "dow", "is_class_day_x", "is_class_day_y"]
SUB_COLS  = [c for c in df.columns if c.startswith("b") and c not in ("b00",)]
ALL_BLDG_COLS = [c for c in df.columns if c.startswith("b")]
y_reg = df["y"]; y_cls = df["y_peak"]

# Feature columns by variant
common_feats = [c for c in df.columns
                if c not in DROP_COLS + ALL_BLDG_COLS  # exclude targets & all per-building cols
                and c not in ("day_type_id_A", "day_type_id_B")]

feats_A = common_feats + ["day_type_id_A"]
feats_B = common_feats + ["day_type_id_B"]
feats_AB= common_feats + ["day_type_id_A", "day_type_id_B"]

print(f"Common features: {len(common_feats)};  +A: {len(feats_A)};  +B: {len(feats_B)};  +AB: {len(feats_AB)}")

# ---------------------------------------------------------------------------
# Walk-forward CV: expanding window, 3 splits
# ---------------------------------------------------------------------------
n = len(df)
# Train at least 5 weeks then test 2 weeks; 3 splits
splits = []
init_train = int(n * 0.50)        # 50% initial training
test_size  = int(n * 0.15)        # 15% per test fold
step       = test_size
for i in range(3):
    tr_end = init_train + i*step
    te_end = tr_end + test_size
    if te_end > n: break
    splits.append((slice(0, tr_end), slice(tr_end, te_end)))

print("\nWalk-forward CV splits:")
for k, (tr, te) in enumerate(splits):
    print(f"  Fold {k+1}: train={tr.stop - tr.start} hrs ({df.index[tr.start]}→{df.index[tr.stop-1]})  "
          f"test={te.stop - te.start} hrs ({df.index[te.start]}→{df.index[te.stop-1]})")


# ---------------------------------------------------------------------------
# Training utilities
# ---------------------------------------------------------------------------
def train_lgb_reg(X_tr, y_tr, X_te):
    model = lgb.LGBMRegressor(
        n_estimators=600, learning_rate=0.03, num_leaves=63,
        min_data_in_leaf=20, feature_fraction=0.85, bagging_fraction=0.85,
        bagging_freq=5, reg_alpha=0.1, reg_lambda=0.1,
        random_state=42, verbose=-1
    )
    model.fit(X_tr, y_tr,
              eval_set=[(X_tr, y_tr)],
              callbacks=[lgb.early_stopping(50, verbose=False)] if False else None)
    return model, model.predict(X_te)


def train_lgb_cls(X_tr, y_tr, X_te):
    # focal-loss style by sample-weight = 1/(class freq)
    pos = max(y_tr.sum(), 1); neg = len(y_tr) - pos
    w = np.where(y_tr == 1, neg/pos, 1.0)
    model = lgb.LGBMClassifier(
        n_estimators=400, learning_rate=0.03, num_leaves=31,
        min_data_in_leaf=15, feature_fraction=0.85,
        random_state=42, verbose=-1
    )
    model.fit(X_tr, y_tr, sample_weight=w)
    return model, model.predict_proba(X_te)[:, 1]


def metrics_reg(y_true, y_pred):
    return {
        "MAE":  mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MAPE": (np.abs((y_true - y_pred) / y_true.replace(0, np.nan))).mean() * 100,
        "R2":   r2_score(y_true, y_pred),
    }


def metrics_cls(y_true, y_score, thr=0.5):
    y_hat = (y_score >= thr).astype(int)
    out = {
        "AUC":   roc_auc_score(y_true, y_score) if y_true.sum() > 0 else np.nan,
        "AP":    average_precision_score(y_true, y_score) if y_true.sum() > 0 else np.nan,
        "F1":    f1_score(y_true, y_hat, zero_division=0),
        "Prec":  precision_score(y_true, y_hat, zero_division=0),
        "Rec":   recall_score(y_true, y_hat, zero_division=0),
        "n_pos_true": int(y_true.sum()),
        "n_pos_pred": int(y_hat.sum()),
    }
    return out


# ---------------------------------------------------------------------------
# Run experiments across 4 variants × 2 heads
# ---------------------------------------------------------------------------
ALL_RESULTS = []

for variant_name, feat_cols in [
    ("Common (no day-type)", common_feats),
    ("+PathA (manual)",      feats_A),
    ("+PathB (clustering)",  feats_B),
    ("+PathA+B (both)",      feats_AB),
]:
    print(f"\n{'='*70}\nVARIANT: {variant_name}  ({len(feat_cols)} features)\n{'='*70}")

    fold_reg = []; fold_cls = []
    for fk, (tr, te) in enumerate(splits):
        Xtr, ytr_reg, ytr_cls = df[feat_cols].iloc[tr], y_reg.iloc[tr], y_cls.iloc[tr]
        Xte, yte_reg, yte_cls = df[feat_cols].iloc[te], y_reg.iloc[te], y_cls.iloc[te]

        # ----- Recompute peak threshold from training only (fold-specific) -----
        p95_tr = ytr_reg.quantile(0.95)
        ytr_cls_fold = (ytr_reg >= p95_tr).astype(int)
        yte_cls_fold = (yte_reg >= p95_tr).astype(int)

        # Head A (regression)
        mA, pA = train_lgb_reg(Xtr, ytr_reg, Xte)
        m_reg = metrics_reg(yte_reg, pA)
        m_reg["fold"] = fk + 1

        # Head B (classification)
        mB, pB = train_lgb_cls(Xtr, ytr_cls_fold, Xte)
        m_cls = metrics_cls(yte_cls_fold, pB)
        m_cls["fold"] = fk + 1
        m_cls["p95_thr"] = float(p95_tr)

        # Persistence baseline (y_t = y_t-24)
        baseline_pred = df["b00_lag24"].iloc[te]
        m_base = metrics_reg(yte_reg, baseline_pred)
        m_base["fold"] = fk + 1

        # Linear baseline
        lin = LinearRegression().fit(Xtr.fillna(0), ytr_reg)
        m_lin = metrics_reg(yte_reg, lin.predict(Xte.fillna(0)))
        m_lin["fold"] = fk + 1

        fold_reg.append({"variant": variant_name, **m_reg, "model": "LightGBM"})
        fold_reg.append({"variant": variant_name, **m_base, "model": "Persistence(24h)"})
        fold_reg.append({"variant": variant_name, **m_lin,  "model": "LinearReg"})
        fold_cls.append({"variant": variant_name, **m_cls, "model": "LightGBM"})

        print(f"  Fold {fk+1}: "
              f"LightGBM MAE={m_reg['MAE']:.1f} R²={m_reg['R2']:.3f}  |  "
              f"Persist MAE={m_base['MAE']:.1f} R²={m_base['R2']:.3f}  |  "
              f"Linear MAE={m_lin['MAE']:.1f} R²={m_lin['R2']:.3f}  |  "
              f"Peak F1={m_cls['F1']:.3f} AUC={m_cls['AUC']:.3f}")

    ALL_RESULTS.extend([("reg", fold_reg), ("cls", fold_cls)])

# Persist last model+pred for downstream use (use +PathA+B variant)
final_variant = feats_AB
all_idx = df.index
# Split: train on first 70%, evaluate last 30%
split_pt = int(len(df) * 0.70)
tr = slice(0, split_pt); te = slice(split_pt, len(df))
Xtr, ytr_reg = df[final_variant].iloc[tr], y_reg.iloc[tr]
Xte, yte_reg = df[final_variant].iloc[te], y_reg.iloc[te]
p95_tr = ytr_reg.quantile(0.95)
ytr_cls = (ytr_reg >= p95_tr).astype(int)
yte_cls = (yte_reg >= p95_tr).astype(int)

mA_final, pA_final = train_lgb_reg(Xtr, ytr_reg, Xte)
mB_final, pB_final = train_lgb_cls(Xtr, ytr_cls, Xte)

# Save trained models
import joblib
joblib.dump({"model_reg": mA_final, "model_cls": mB_final, "p95_thr": float(p95_tr),
             "features": final_variant, "split_pt": split_pt},
            f"{RES}/lightgbm_models.pkl")
np.save(f"{RES}/test_predictions_reg.npy", pA_final)
np.save(f"{RES}/test_predictions_cls.npy", pB_final)

# Save the test set frame (for downstream CCRI / SDR analysis)
test_df = df.iloc[te].copy()
test_df["pred_reg"]      = pA_final
test_df["pred_cls_prob"] = pB_final
test_df["y_cls_fold"]    = yte_cls.values
test_df["p95_thr_train"] = p95_tr
test_df.to_parquet(f"{PROC}/test_df_with_preds.parquet")

# Final summary table
import pandas as pd
reg_rows = []; cls_rows = []
for kind, lst in ALL_RESULTS:
    if kind == "reg":
        reg_rows.extend(lst)
    else:
        cls_rows.extend(lst)
reg_df = pd.DataFrame(reg_rows)
cls_df = pd.DataFrame(cls_rows)

# Aggregate (mean ± std across folds)
agg_reg = reg_df.groupby(["variant", "model"]).agg(
    MAE_mean=("MAE","mean"), MAE_std=("MAE","std"),
    RMSE_mean=("RMSE","mean"), R2_mean=("R2","mean"),
    MAPE_mean=("MAPE","mean")
).round(3)
agg_cls = cls_df.groupby("variant").agg(
    F1_mean=("F1","mean"), AUC_mean=("AUC","mean"), AP_mean=("AP","mean"),
    Prec_mean=("Prec","mean"), Rec_mean=("Rec","mean")
).round(3)

print("\n" + "="*70)
print("REGRESSION RESULTS (mean across 3 folds)")
print("="*70)
print(agg_reg.to_string())
print("\n" + "="*70)
print("CLASSIFICATION (PEAK) RESULTS")
print("="*70)
print(agg_cls.to_string())

agg_reg.to_csv(f"{RES}/results_regression.csv")
agg_cls.to_csv(f"{RES}/results_classification.csv")

# Final test-fold summary (for paper Table)
final_reg = metrics_reg(yte_reg, pA_final)
final_cls = metrics_cls(yte_cls, pB_final)
final_summary = {
    "test_period": [str(test_df.index.min()), str(test_df.index.max())],
    "test_hours":  int(len(test_df)),
    "p95_thr_kW":  float(p95_tr),
    "regression":  final_reg,
    "classification": final_cls,
}
with open(f"{RES}/final_test_summary.json", "w") as f:
    json.dump(final_summary, f, indent=2)
print("\n" + "="*70)
print("FINAL HOLDOUT TEST (last 30% of period, +PathA+B variant)")
print("="*70)
print(json.dumps(final_summary, indent=2))

print(f"\n💾 models → {RES}/lightgbm_models.pkl")
print(f"💾 results → {RES}/results_*.csv + final_test_summary.json")
print(f"💾 test_df_with_preds.parquet ready for Step 7/8/9")
