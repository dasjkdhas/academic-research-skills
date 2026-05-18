"""Regenerate all presentation figures in SVG format and package deliverables.

Strategy:
  - Re-import the two figure-generation scripts via exec() with a monkey-patched
    plt.savefig that writes BOTH .png AND .svg to figures_svg/.
  - Then build a zip with all docs, figures (PNG + SVG), PPT, and JSON summaries.
"""
import os
import shutil
import zipfile
from pathlib import Path

BASE   = Path("/home/user/academic-research-skills/output/sdr-weather-alerts")
SVG_DIR = BASE / "figures_svg"
PKG_ROOT = BASE / "package"
ZIP_OUT  = BASE / "SDR_research_package.zip"

SVG_DIR.mkdir(exist_ok=True)
if PKG_ROOT.exists(): shutil.rmtree(PKG_ROOT)
PKG_ROOT.mkdir()

# ============================================================================
# Step 1: re-run both figure scripts with savefig patched to ALSO emit SVG
# ============================================================================
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
_original_savefig = plt.savefig
def _dual_savefig(fname, *args, **kwargs):
    # Save PNG to its original location
    _original_savefig(fname, *args, **kwargs)
    # Also save SVG to figures_svg/
    fname_path = Path(str(fname))
    svg_path = SVG_DIR / fname_path.with_suffix(".svg").name
    kw_svg = {k: v for k, v in kwargs.items() if k != "dpi"}
    _original_savefig(svg_path, *args, **kw_svg, format="svg")
plt.savefig = _dual_savefig

# Re-run both scripts in this process
print("=" * 70)
print("Re-running 13_clean_figures_for_presentation.py with SVG output...")
print("=" * 70)
script1 = BASE / "code" / "13_clean_figures_for_presentation.py"
exec(open(script1).read(), {"__file__": str(script1), "__name__": "__main__"})

# Reset matplotlib state between scripts
plt.close("all")
plt.savefig = _dual_savefig   # patch may have been overridden by rcParams

print("\n" + "=" * 70)
print("Re-running 15_correlation_and_pca_analysis.py with SVG output...")
print("=" * 70)
script2 = BASE / "code" / "15_correlation_and_pca_analysis.py"
exec(open(script2).read(), {"__file__": str(script2), "__name__": "__main__"})

plt.savefig = _original_savefig

svg_files = sorted(SVG_DIR.glob("*.svg"))
print(f"\n✓ {len(svg_files)} SVG figures created in {SVG_DIR}")
for f in svg_files: print(f"  - {f.name}")


# ============================================================================
# Step 2: build package directory structure
# ============================================================================
print("\n" + "=" * 70)
print("Building package directory...")
print("=" * 70)

# 2.1 Documents
DOCS_DIR = PKG_ROOT / "docs"; DOCS_DIR.mkdir()
docs_src = [
    "11_methodology_pivot_forecast_driven.md",
    "12_forecast_driven_results.md",
    "13_amedas_vs_forecast_methodology.md",
    "14_data_acquisition_roadmap.md",
]
for d in docs_src:
    src = BASE / d
    if src.exists():
        shutil.copy(src, DOCS_DIR / d)
        print(f"  doc: {d}")

# 2.2 Presentation
PRES_DIR = PKG_ROOT / "presentation"; PRES_DIR.mkdir()
for f in ["SDR_research_progress_jp.pptx", "speaker_script_jp.md"]:
    src = BASE / "presentation" / f
    if src.exists():
        shutil.copy(src, PRES_DIR / f)
        print(f"  presentation: {f}")

# 2.3 Figures — SVG (primary)
SVG_OUT = PKG_ROOT / "figures_svg"; SVG_OUT.mkdir()
for f in svg_files:
    shutil.copy(f, SVG_OUT / f.name)
print(f"  figures_svg: {len(svg_files)} files")

# 2.4 Figures — PNG (compatibility copy)
PNG_OUT = PKG_ROOT / "figures_png"; PNG_OUT.mkdir()
for f in sorted((BASE / "figures_pres").glob("*.png")):
    shutil.copy(f, PNG_OUT / f.name)
n_png = len(list(PNG_OUT.glob("*.png")))
print(f"  figures_png: {n_png} files")

# 2.5 Results JSON
RES_OUT = PKG_ROOT / "results"; RES_OUT.mkdir()
for f in [
    "arch_compare_summary.json",
    "correlation_pca_summary.json",
    "day_ahead_hybrid_summary.json",
    "pres_summary.json",
]:
    src = BASE / "results" / f
    if src.exists():
        shutil.copy(src, RES_OUT / f)
        print(f"  results: {f}")

# 2.6 Code (reproducibility)
CODE_OUT = PKG_ROOT / "code"; CODE_OUT.mkdir()
for f in [
    "11_arch_compare_obs_fcst_hybrid.py",
    "12_day_ahead_hybrid_final.py",
    "13_clean_figures_for_presentation.py",
    "14_build_presentation_ppt.py",
    "15_correlation_and_pca_analysis.py",
]:
    src = BASE / "code" / f
    if src.exists():
        shutil.copy(src, CODE_OUT / f)
        print(f"  code: {f}")

# 2.7 README at package root
readme = PKG_ROOT / "README.md"
readme.write_text(
"""# SDR Research Package
山口大学キャンパス省エネ研究  — 翌日電力ピーク予測 + SDR運用支援

## パッケージ構成
- `docs/` — 方法論ピボット、結果、データ取得計画など解説文書
- `presentation/` — 省エネ研究会発表用PPT(12スライド) + 日本語講稿
- `figures_svg/` — 解析結果図表 (ベクター形式、編集可能)
- `figures_png/` — 同じ図のPNG版 (互換性用)
- `results/` — 数値結果JSON (再現性確認用)
- `code/` — 解析スクリプト Python (再実行可能)

## 主要な解析内容
1. 探索的データ分析 (日内パターン、月別)
2. **気象 × 電力 相関分析** (Pearson/Spearman/標準化β)
3. **主成分分析 (PCA)** — 気象10変数を3主成分(76%変動)に圧縮
4. **3アーキテクチャ比較**: 観測のみ / 予報のみ / ハイブリッド
5. ハイブリッド翌日予測モデル (LightGBM)
6. SHAP による特徴量重要度

## 主要結果
- ハイブリッド手法: holdout MAE = 54.0 kW, R² = 0.905, MAPE = 7.3%
- 予報のみベースラインから MAE 10% 改善
- 観測上限から MAE わずか 6% 差
- 気象変数だけで b00 分散の 53% を説明
- PC1 (熱関連) — b00 相関 r=+0.47
- PC2 (湿度×日射) — b00 相関 r=−0.50

## 図表一覧 (figures_svg/, figures_png/)

### 探索的分析 + データ
- `pres_01_overview_daily_profile` — 月別 時刻別 平均消費電力
- `pres_02_temp_load_scatter` — 外気温 × 電力 散布図
- `pres_07_train_test_split` — 学習/テスト分割可視化

### 気象 × 電力 相関分析
- `corr_01_pearson_heatmap` — 相関係数ヒートマップ(時間別)
- `corr_02_daily_heatmap` — 相関係数ヒートマップ(日単位)
- `corr_03_scatter_grid` — 6気象変数 × 電力 散布図
- `corr_04_hourly_stratified` — 時刻別 層別化相関
- `corr_07_standardized_beta` — 標準化回帰係数 β
- `corr_08_framework` — 解析フレームワーク (電力✓ + ガス予約)

### 主成分分析 (PCA)
- `corr_05_pca_variance` — 主成分の寄与率
- `corr_06_pca_loadings` — 主成分の構成 + b00との相関

### 予測モデル結果
- `pres_03_arch_compare` — 3アーキテクチャ MAE/R²比較
- `pres_04_holdout_timeseries` — テスト期間 実測 vs 予測
- `pres_05_pred_vs_actual` — 予測 vs 実測 散布図
- `pres_06_shap_top10` — SHAP特徴量重要度 Top10

## 再現方法
```bash
cd code/
python 13_clean_figures_for_presentation.py    # 探索 + 結果図
python 14_build_presentation_ppt.py             # PPT生成
python 15_correlation_and_pca_analysis.py       # 相関 + PCA
```

## ライセンス & 引用
研究室内利用および学会発表用。外部公開時は要相談。

## バージョン情報
- パッケージ作成日: 2026-05-17
- データ範囲: 2025-07-20 〜 2025-10-26 (有効2,145時間)
- 解析ブランチ: claude/sdr-weather-alerts-research-CwlkS
""", encoding="utf-8")
print(f"  README.md")


# ============================================================================
# Step 3: create zip archive
# ============================================================================
print("\n" + "=" * 70)
print("Creating zip archive...")
print("=" * 70)
if ZIP_OUT.exists(): ZIP_OUT.unlink()
with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for root, _, files in os.walk(PKG_ROOT):
        for f in files:
            full = Path(root) / f
            rel  = full.relative_to(PKG_ROOT.parent)   # store with package/ prefix
            zf.write(full, rel)

size_mb = ZIP_OUT.stat().st_size / 1024 / 1024
n_in_zip = sum(1 for _ in zipfile.ZipFile(ZIP_OUT).namelist())
print(f"\n✅ Created: {ZIP_OUT}")
print(f"   Size : {size_mb:.2f} MB")
print(f"   Files: {n_in_zip}")
