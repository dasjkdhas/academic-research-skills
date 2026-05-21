"""Build v4 PPT — Soft DR Advisory System framing, 16 slides.

Final restructuring per user clarification:
  * SDR = Soft Demand Response (METI ERAB usage), NOT Setpoint DR
  * System scope = ALERT DELIVERY only; never directly controls equipment
  * Soft DR actions are chosen by facility manager (human in the loop)

Slide structure (16 slides):
   1  Title (Soft DR Advisory System)
   2  Background (pillar③ rewritten)
   3  3-RQ framework (Q1 understand + Q2 predict + Q3 alert design)
   4  Data + Method (8-step analytical flow)
   5  System overview (NEW — alert pipeline)
   6  Exploratory ①: daily/monthly pattern
   7  Exploratory ②: scatter grid
   8  Correlation ①: Pearson/Spearman heatmaps
   9  Correlation ②: hour-stratified (KEY)
   10 Correlation ③: standardized regression β
   11 PCA ①: variance explained
   12 PCA ②: loadings + b00 correlation
   13 Prediction: hybrid + result + → CCRI bridge
   14 CCRI alert design + delivery (NEW)
   15 SHAP: statistical-ML consistency
   16 Summary + future work (manager evaluation added)
"""
import os, json
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
RES  = "/home/user/academic-research-skills/output/sdr-weather-alerts/results"
FIG  = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_pres"
OUT  = "/home/user/academic-research-skills/output/sdr-weather-alerts/presentation"
os.makedirs(OUT, exist_ok=True)

TODAY = datetime.now().strftime("%Y%m%d")

# Yamaguchi palette
YU_NAVY    = RGBColor(0x00, 0x3B, 0x71)
YU_NAVY_LT = RGBColor(0x2A, 0x5A, 0x8E)
YU_ORANGE  = RGBColor(0xE7, 0x8A, 0x00)
YU_GREEN   = RGBColor(0x2D, 0x9C, 0x5A)
YU_RED     = RGBColor(0xC8, 0x10, 0x2E)
YU_GREY    = RGBColor(0x5A, 0x5A, 0x5A)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG   = RGBColor(0xF4, 0xF6, 0xFA)
ACCENT_BG  = RGBColor(0xFD, 0xE9, 0xCE)
RED_ALERT  = RGBColor(0xC8, 0x10, 0x2E)
ORANGE_HI  = RGBColor(0xE7, 0x8A, 0x00)
GREEN_OK   = RGBColor(0x2D, 0x9C, 0x5A)

with open(f"{RES}/correlation_pca_summary.json", "r") as f: CR = json.load(f)
with open(f"{RES}/pres_summary.json", "r") as f: PS = json.load(f)

TOTAL = 16
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
JP_FONT = "Yu Gothic"

def set_jp(run, size=14, bold=False, color=None):
    run.font.name = JP_FONT; run.font.size = Pt(size); run.font.bold = bold
    if color is not None: run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {"typeface": JP_FONT}); rPr.append(ea)
    else: ea.set("typeface", JP_FONT)

def add_text(slide, x, y, w, h, text, size=14, bold=False, color=None,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    for i, ln in enumerate(text.split("\n") if isinstance(text, str) else text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = ln; set_jp(r, size=size, bold=bold, color=color)
    return tb

def add_rect(slide, x, y, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh

def header_footer(slide, no, total=TOTAL,
                  title="省エネ研究 (山口大学) — Soft DR 警報配信システム"):
    add_rect(slide, 0, 0, SW, Inches(0.35), YU_NAVY)
    add_text(slide, Inches(0.3), Inches(0.04), Inches(11), Inches(0.27),
             title, size=11, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(11.5), Inches(0.04), Inches(1.6), Inches(0.27),
             f"Slide {no} / {total}", size=10, color=WHITE,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, 0, SH - Inches(0.25), SW, Inches(0.25), YU_NAVY)
    add_text(slide, Inches(0.3), SH - Inches(0.22), Inches(10), Inches(0.2),
             "山口大学 Yamaguchi University — 省エネ研究会 2026",
             size=8.5, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

def add_title(slide, title, subtitle=None):
    add_text(slide, Inches(0.4), Inches(0.5), Inches(12.5), Inches(0.6),
             title, size=22, bold=True, color=YU_NAVY)
    add_rect(slide, Inches(0.4), Inches(1.05), Inches(1.2), Inches(0.06), YU_ORANGE)
    if subtitle:
        add_text(slide, Inches(0.4), Inches(1.15), Inches(12.5), Inches(0.4),
                 subtitle, size=13, color=YU_GREY)

def add_notes(slide, text):
    n = slide.notes_slide.notes_text_frame; n.text = ""
    for i, ln in enumerate(text.split("\n")):
        p = n.paragraphs[0] if i == 0 else n.add_paragraph()
        p.text = ln

# ===========================================================================
# SLIDE 1: Title
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_rect(slide, 0, 0, SW, SH, YU_NAVY)
add_rect(slide, 0, Inches(2.7), SW, Inches(0.08), YU_ORANGE)

add_text(slide, Inches(0.6), Inches(0.7), Inches(12), Inches(0.5),
         "山口大学  YAMAGUCHI UNIVERSITY", size=14, bold=True, color=WHITE)

add_text(slide, Inches(0.6), Inches(2.9), Inches(12), Inches(1.7),
         "Soft DR のための気象駆動型警報配信システム\n"
         "— 大学キャンパスにおける翌日ピーク予測とリスク階層アラート —",
         size=27, bold=True, color=WHITE)

add_text(slide, Inches(0.6), Inches(4.95), Inches(12), Inches(0.5),
         "A Weather-Driven Advisory System for Soft Demand Response",
         size=15, color=RGBColor(0xFF, 0xC8, 0x80))

add_text(slide, Inches(0.6), Inches(5.95), Inches(12), Inches(0.4),
         "発表者: ○○ ○○ (山口大学 ○○研究室)", size=14, color=WHITE)
add_text(slide, Inches(0.6), Inches(6.45), Inches(12), Inches(0.4),
         "省エネ研究会 / 2026年5月", size=14, color=WHITE)

add_notes(slide,
"皆さま、本日はお時間をいただきありがとうございます。山口大学の○○です。\n"
"本日は『Soft DR のための気象駆動型警報配信システム』について発表いたします。\n\n"
"まずキーワードのご確認ですが、本研究の Soft DR とは、Soft Demand Response、\n"
"つまり強制的な制御ではなく、節電依頼・設備運用調整・利用者への協力呼びかけ\n"
"などの非強制的な需要調整を指します。経済産業省 ERAB でも使われる用語です。\n\n"
"本研究は『警報配信システム』であって、設定温度を勝手に変える等の自動制御\n"
"システムではありません。予測した結果を警報として配信し、最終的な判断は\n"
"設備管理者が行うという、意思決定支援の枠組みです。\n\n"
"キーポイントは「相関分析による気象-電力関係の解明」と「警報配信フレーム\n"
"の設計」の二点になります。")

# ===========================================================================
# SLIDE 2: 背景・課題 (revised pillar ③)
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 2)
add_title(slide, "研究背景と課題", "なぜキャンパス電力ピークの予測・警報が必要か")

def pillar(x, color, num, head, body):
    add_rect(slide, x, Inches(2.0), Inches(4.0), Inches(0.6), color)
    add_text(slide, x + Inches(0.2), Inches(2.07), Inches(3.6), Inches(0.5),
             f"{num}.  {head}", size=15, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, x, Inches(2.6), Inches(4.0), Inches(3.4), LIGHT_BG, line=color)
    add_text(slide, x + Inches(0.25), Inches(2.75), Inches(3.55), Inches(3.2),
             body, size=13, color=YU_GREY)

pillar(Inches(0.4),  YU_NAVY,   "①", "気候変動と猛暑",
       "・近年の夏季猛暑で\n  電力需要急増\n"
       "・キャンパス電力の約 40% が\n  空調由来\n"
       "・契約電力更新は経費直結")

pillar(Inches(4.65), YU_ORANGE, "②", "Soft DR は多様な選択肢",
       "・節電依頼の学内放送\n"
       "・空調設定温度の見直し\n"
       "・照明調光・OA 機器シフト\n"
       "・利用者協力呼びかけ\n"
       "  → 管理者が状況に応じ選択")

pillar(Inches(8.9),  YU_GREEN,  "③", "予測ベース警報配信",
       "・前日の気象予報から\n  翌日ピーク発生確率を予測\n"
       "・警報レベルに分類し\n  設備管理者に配信\n"
       "・管理者が Soft DR を判断")

add_text(slide, Inches(0.4), Inches(6.4), Inches(12.5), Inches(0.5),
         "■ 本研究は「予告・警報を出すまで」が範囲: 実際の Soft DR 措置は管理者の判断による",
         size=13.5, bold=True, color=YU_RED)

add_notes(slide,
"研究背景を3点でご説明します。\n"
"①、近年の猛暑により電力需要が増加。キャンパス電力の約40%が空調由来です。\n"
"②、Soft DR は多様な選択肢を含む幅広い概念です。節電依頼の学内放送、空調\n"
"設定温度の見直し、照明調光、OA 機器の運用シフト、利用者への協力呼びかけ等、\n"
"管理者が状況に応じて選択する非強制的な手段の総称です。\n"
"③、本研究では、翌日のピーク発生可能性を「警報レベル」に分類し、設備管理者\n"
"に配信する仕組みを開発します。\n\n"
"重要な点をご確認ください。本研究は「予告・警報を出すまで」が範囲です。\n"
"実際に空調を操作したり Soft DR 措置を実施したりするのは、管理者の判断と\n"
"なります。人間が必ず介在する意思決定支援システム、という位置付けです。")

# ===========================================================================
# SLIDE 3: 3 RQs
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 3)
add_title(slide, "研究の問い: 3段階アプローチ", "理解 → 予測 → 警報設計")

def rq_box(x, color, num, q, body):
    add_rect(slide, x, Inches(2.0), Inches(4.05), Inches(0.55), color)
    add_text(slide, x + Inches(0.15), Inches(2.08), Inches(3.85), Inches(0.4),
             f"Q{num}",
             size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, x + Inches(0.7), Inches(2.08), Inches(3.3), Inches(0.4),
             q, size=12.5, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, x, Inches(2.55), Inches(4.05), Inches(3.0), LIGHT_BG, line=color)
    add_text(slide, x + Inches(0.18), Inches(2.7), Inches(3.85), Inches(2.85),
             body, size=11.5, color=YU_GREY)

rq_box(Inches(0.4), YU_NAVY, "1", "何が電力ピークを駆動するか?",
       "段階: 理解\n"
       "方法:\n"
       "・Pearson / Spearman 相関\n"
       "・時刻別 層別化相関\n"
       "・標準化重回帰 β\n"
       "・主成分分析 (PCA)\n\n"
       "出力: 駆動要因の同定\n"
       "          + 影響構造の定量化")

rq_box(Inches(4.65), YU_ORANGE, "2", "翌日ピークを精度良く予測できるか?",
       "段階: 予測\n"
       "方法:\n"
       "・ハイブリッド気象入力\n"
       "  (ERA5 観測 + JMA MSM 予報)\n"
       "・LightGBM 回帰モデル\n"
       "・SHAP 値による解釈\n\n"
       "出力: 翌 24 時間の電力予測\n"
       "          MAE = 54 kW (達成)")

rq_box(Inches(8.9), YU_RED, "3", "警報をどう設計・配信するか?",
       "段階: 応用 (新規)\n"
       "方法:\n"
       "・CCRI (Critical Risk Index)\n"
       "・Normal / High / Critical の\n"
       "  3 段階分類\n"
       "・当日 17 時に配信\n\n"
       "出力: 管理者向け警報\n"
       "          + 意思決定支援フレーム")

add_rect(slide, Inches(0.4), Inches(5.7), Inches(12.55), Inches(1.0), ACCENT_BG, line=YU_ORANGE)
add_text(slide, Inches(0.6), Inches(5.78), Inches(12.3), Inches(0.4),
         "■ 三段階の論理: Q1で気象の影響構造を解明 → Q2でその知見を予測モデルに活用 → Q3で警報として実用化",
         size=12.5, bold=True, color=YU_NAVY)
add_text(slide, Inches(0.6), Inches(6.2), Inches(12.3), Inches(0.45),
         "  SHAP 解析で「機械学習モデルが Q1 の発見と一致する要因を学んだか」を検証 (Q1↔Q2 整合性確認)",
         size=10.5, color=YU_GREY)

add_notes(slide,
"研究の問いは3段階で構成されています。\n\n"
"Q1 は理解段階。どの気象因子がピークを駆動するかを、Pearson/Spearman 相関、\n"
"時刻別層別化、標準化回帰、主成分分析で多角的に解明します。\n\n"
"Q2 は予測段階。Q1 の知見を活かし、ハイブリッド気象入力 + LightGBM で翌日\n"
"24時間の予測を行います。\n\n"
"Q3 は応用段階で、本研究の新規貢献です。予測値を CCRI という指標で集約し、\n"
"Normal/High/Critical の3段階に分類して、当日17時に設備管理者へ配信します。\n\n"
"三段階の論理は、Q1 で『気象の影響構造』を解明 → Q2 で『その知見を予測に\n"
"活用』 → Q3 で『警報として実用化』、というストーリーです。\n"
"加えて SHAP 解析により、機械学習モデルが Q1 で発見した要因を重視している\n"
"ことを確認します。これが統計分析と機械学習の整合性確認です。")

# ===========================================================================
# SLIDE 4: データと方法 (8-step flow)
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 4)
add_title(slide, "データと方法",
          f"使用期間: {PS['data_range']} ({PS['n_hours_valid']:,} 有効時間, 2025 年通年に拡張予定)")

# Left: data sources
add_text(slide, Inches(0.4), Inches(1.95), Inches(7.0), Inches(0.4),
         "■ データ源 (観測 = ERA5 再解析、予報 = JMA MSM)",
         size=14, bold=True, color=YU_NAVY)

def src_row(y, cat, src, var, color=YU_GREY):
    add_text(slide, Inches(0.4), y, Inches(2.1), Inches(0.32),
             cat, size=11.5, bold=True, color=YU_NAVY)
    add_text(slide, Inches(2.55), y, Inches(2.0), Inches(0.32),
             src, size=11, color=color)
    add_text(slide, Inches(4.6), y, Inches(2.9), Inches(0.32),
             var, size=11, color=color)

src_row(Inches(2.45), "電力 (1h)", "BEMS 山口大学", "建物別 b00–b15 (主棟 b00 を対象)")
src_row(Inches(2.8),  "気象観測", "ERA5 再解析",   "気温/湿度/日射/気圧/雲/風/降水")
src_row(Inches(3.15), "気象予報", "JMA MSM 5km",   "気温/湿度/日射 等 (+39h)")
src_row(Inches(3.5),  "派生量",   "(計算)",         "WBGT, 体感気温, 露点")

# Note about ERA5
add_rect(slide, Inches(0.4), Inches(3.95), Inches(7.0), Inches(1.4),
         ACCENT_BG, line=YU_ORANGE)
add_text(slide, Inches(0.55), Inches(4.02), Inches(6.7), Inches(0.32),
         "※ AMeDAS 宇部站の制約",
         size=11.5, bold=True, color=YU_RED)
add_text(slide, Inches(0.55), Inches(4.37), Inches(6.7), Inches(0.92),
         "・AMeDAS 宇部は四要素観測 (気温・風・降水・日照) のみ\n"
         "・湿度・気圧データなし → ERA5 再解析を採用\n"
         "・ERA5: 全球グリッド 31km、エネルギー研究で標準\n"
         "  (Hersbach et al. 2020, Q.J.R.M.S.)",
         size=10.5, color=YU_GREY)

# Right: 8-step analytical flow
add_text(slide, Inches(7.85), Inches(1.95), Inches(5.3), Inches(0.4),
         "■ 8 段階 解析フロー", size=14, bold=True, color=YU_NAVY)

def flow(y, num, label, color):
    add_rect(slide, Inches(7.85), y, Inches(0.55), Inches(0.38), color)
    add_text(slide, Inches(7.85), y, Inches(0.55), Inches(0.38),
             num, size=13, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(8.5), y + Inches(0.03), Inches(4.6), Inches(0.35),
             label, size=11, color=YU_GREY, anchor=MSO_ANCHOR.MIDDLE)

# Q1 phase
flow(Inches(2.45),  "①", "探索的データ分析 (パターン把握)",       YU_NAVY)
flow(Inches(2.9),   "②", "ペアワイズ相関 (Pearson, Spearman)",     YU_NAVY)
flow(Inches(3.35),  "③", "時刻別層別化相関 (交絡除去)",            YU_NAVY)
flow(Inches(3.8),   "④", "標準化重回帰 β (相対寄与度)",            YU_NAVY)
flow(Inches(4.25),  "⑤", "主成分分析 (本質的な軸抽出)",            YU_NAVY)
# Q2 phase
flow(Inches(4.85),  "⑥", "ハイブリッド予測モデル + SHAP",          YU_ORANGE)
# Q3 phase ← NEW
flow(Inches(5.45),  "⑦", "CCRI 算出・警報レベル分類",             YU_RED)
flow(Inches(5.9),   "⑧", "管理者ダッシュボード配信",              YU_RED)

# Legend
add_text(slide, Inches(7.85), Inches(6.4), Inches(5.3), Inches(0.35),
         "Q1: 理解 (青)  /  Q2: 予測 (橙)  /  Q3: 警報 (赤)",
         size=10, color=YU_GREY)

add_notes(slide,
"データと方法をご説明します。\n"
"電力データは BEMS から取得した1時間値、b00 主棟が対象。\n"
"気象は ERA5 再解析と JMA MSM 予報を併用します。\n\n"
"重要な開示として、AMeDAS 宇部站は四要素観測のみで、湿度・気圧の観測が\n"
"ありません。そこで Hersbach 等2020以降エネルギー研究で標準的な\n"
"ERA5 再解析を採用しました。\n\n"
"解析フローは8段階です。\n"
"①〜⑤ が Q1 (理解段階、青)\n"
"⑥ が Q2 (予測段階、橙)\n"
"⑦⑧ が Q3 (警報段階、赤) ← 本研究の新規\n\n"
"そして今後のデータ拡張として、2025年通年データの取得を予定しており、\n"
"冬季暖房需要も含めた評価へ拡張する予定です。")

# ===========================================================================
# SLIDE 5: System Overview (NEW)
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 5)
add_title(slide, "システム全体像",
          "気象データ → 予測 → 警報 → 管理者判断 → Soft DR 措置 (人間介在型)")

# Helper for flow box
def fbox(x, y, w, h, label, sub, fc, ec=None, tc=WHITE, label_size=11.5, sub_size=9.5):
    add_rect(slide, x, y, w, h, fc, line=ec)
    add_text(slide, x, y + Inches(0.10), w, Inches(0.30),
             label, size=label_size, bold=True, color=tc,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, x, y + h - Inches(0.30), w, Inches(0.22),
             sub, size=sub_size, color=tc,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# Layer 1: Inputs (top, three boxes)
add_text(slide, Inches(0.4), Inches(1.9), Inches(2.5), Inches(0.3),
         "[入力層]", size=11.5, bold=True, color=YU_NAVY)
fbox(Inches(0.4), Inches(2.2), Inches(2.2), Inches(0.7),
     "気象観測", "ERA5 再解析", YU_NAVY)
fbox(Inches(2.85), Inches(2.2), Inches(2.2), Inches(0.7),
     "気象予報", "JMA MSM (+39h)", YU_NAVY_LT)
fbox(Inches(5.3), Inches(2.2), Inches(2.2), Inches(0.7),
     "電力履歴", "BEMS 1h", YU_NAVY_LT)

# Layer 2: Model
add_text(slide, Inches(0.4), Inches(3.15), Inches(2.5), Inches(0.3),
         "[モデル層]", size=11.5, bold=True, color=YU_NAVY)
fbox(Inches(2.85), Inches(3.45), Inches(2.2), Inches(0.7),
     "LightGBM Hybrid", "MAE 54 kW, R²=0.91", YU_ORANGE)

# Layer 3: Judge
add_text(slide, Inches(0.4), Inches(4.4), Inches(2.5), Inches(0.3),
         "[判定層]", size=11.5, bold=True, color=YU_NAVY)
fbox(Inches(2.85), Inches(4.7), Inches(2.2), Inches(0.7),
     "CCRI 算出", "リスク指標", YU_ORANGE)

# Layer 4: Alert delivery
add_text(slide, Inches(0.4), Inches(5.65), Inches(2.5), Inches(0.3),
         "[配信層]", size=11.5, bold=True, color=YU_NAVY)
fbox(Inches(2.85), Inches(5.95), Inches(0.95), Inches(0.7),
     "Normal", "🟢 通知なし", GREEN_OK)
fbox(Inches(3.9), Inches(5.95), Inches(0.95), Inches(0.7),
     "High", "🟠 メール", ORANGE_HI)
fbox(Inches(4.95), Inches(5.95), Inches(0.95), Inches(0.7),
     "Critical", "🔴 SMS+メール", RED_ALERT)

# Right side: human in loop & Soft DR actions
# Dividing line
add_rect(slide, Inches(7.95), Inches(2.0), Inches(0.04), Inches(4.8), YU_RED)
add_text(slide, Inches(7.6), Inches(1.85), Inches(1.0), Inches(0.3),
         "境界線", size=10, bold=True, color=YU_RED, align=PP_ALIGN.CENTER)

# Right column: human + actions
add_text(slide, Inches(8.4), Inches(1.9), Inches(4.7), Inches(0.3),
         "[管理者の判断 + Soft DR 措置]", size=11.5, bold=True, color=YU_RED)
add_rect(slide, Inches(8.4), Inches(2.2), Inches(4.7), Inches(0.7),
         ACCENT_BG, line=YU_RED)
add_text(slide, Inches(8.4), Inches(2.25), Inches(4.7), Inches(0.6),
         "★ 設備管理者の判断 ★\n警報受信 → 状況確認 → 措置選択",
         size=11, bold=True, color=YU_RED,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# Soft DR action examples
def action(y, num, lbl):
    add_text(slide, Inches(8.4), y, Inches(0.4), Inches(0.4),
             f"{num}.", size=12, bold=True, color=YU_NAVY,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(8.85), y, Inches(4.2), Inches(0.4),
             lbl, size=11, color=YU_GREY, anchor=MSO_ANCHOR.MIDDLE)

action(Inches(3.15), "1", "節電依頼の学内放送・メール")
action(Inches(3.65), "2", "空調設定温度の見直し (+1〜2℃)")
action(Inches(4.15), "3", "照明調光 (廊下・共用空間)")
action(Inches(4.65), "4", "非必須機器の運用時刻シフト")
action(Inches(5.15), "5", "利用者への協力呼びかけ")

# Bottom note
add_rect(slide, Inches(8.4), Inches(5.85), Inches(4.7), Inches(0.85),
         LIGHT_BG, line=YU_NAVY)
add_text(slide, Inches(8.55), Inches(5.92), Inches(4.5), Inches(0.4),
         "本研究の境界線:",
         size=11, bold=True, color=YU_NAVY)
add_text(slide, Inches(8.55), Inches(6.27), Inches(4.5), Inches(0.5),
         "「予測 → 警報配信」までが対象\n"
         "Soft DR 実施は管理者の判断",
         size=10, color=YU_GREY)

add_notes(slide,
"本研究のシステム全体像をご説明します。\n\n"
"システムは4つの層で構成されています。\n"
"・入力層: 気象観測 (ERA5)、気象予報 (JMA MSM)、電力履歴 (BEMS)\n"
"・モデル層: LightGBM ハイブリッドモデル\n"
"・判定層: CCRI を算出してリスクを定量化\n"
"・配信層: Normal/High/Critical の3段階で管理者へ配信\n\n"
"重要なのは右側にある『境界線』です。本研究の範囲は警報配信までで、\n"
"その先の Soft DR 措置 — 節電依頼、空調温度調整、照明調光、機器シフト、\n"
"利用者協力呼びかけ等 — は、設備管理者の判断で実施されます。\n\n"
"つまり本システムは自動制御システムではなく、人間 (管理者) が判断する\n"
"ための情報を提供する意思決定支援システムである、ということです。\n"
"この『人間が必ず介在する』設計が、Soft DR の本質と整合しています。")

# ===========================================================================
# SLIDE 6: 日内・月別パターン
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 6)
add_title(slide, "探索的分析①: 日内・月別 負荷パターン",
          "→ ピーク時刻と振幅の把握")

slide.shapes.add_picture(f"{FIG}/pres_01_overview_daily_profile.png",
                          Inches(0.4), Inches(1.9), width=Inches(8.0))

add_text(slide, Inches(8.6), Inches(2.0), Inches(4.5), Inches(0.4),
         "■ 主な観察", size=14, bold=True, color=YU_NAVY)
add_text(slide, Inches(8.6), Inches(2.5), Inches(4.5), Inches(4.5),
         "1. ピーク時刻\n"
         "    全月 14〜15 時\n\n"
         "2. ピーク振幅\n"
         "    7月: 1,360 kW\n"
         "    10月: 1,040 kW\n\n"
         "3. 冷房負荷\n"
         "    約 320 kW\n\n"
         "4. ベース負荷\n"
         "    早朝 5〜6 時 550〜700 kW",
         size=12, color=YU_GREY)

add_notes(slide,
"まず探索的分析として、月別の日内負荷パターンを見ます。\n"
"赤線が7月、青線が10月。\n"
"7月の真夏は午後2時頃に最大1,360 kWのピーク、10月の秋は1,040 kW まで\n"
"下がります。差は約320 kW で、これが冷房負荷の典型的な大きさです。\n"
"全月共通で、朝5〜6時に最低、午後14〜15時に最高、夜にかけて減少。\n"
"次にこのピークを駆動する気象要素の特定に進みます。")

# ===========================================================================
# SLIDE 7: 散布図グリッド
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 7)
add_title(slide, "探索的分析②: 気象 × 電力 散布図グリッド",
          "→ 各気象変数と b00 の関係を視覚的に確認 (色: 時刻)")

slide.shapes.add_picture(f"{FIG}/corr_03_scatter_grid.png",
                          Inches(0.4), Inches(1.9), width=Inches(10.0))

add_text(slide, Inches(10.6), Inches(2.0), Inches(2.5), Inches(0.4),
         "■ 視覚的所見", size=14, bold=True, color=YU_NAVY)
add_text(slide, Inches(10.6), Inches(2.5), Inches(2.5), Inches(4.5),
         "・気温\n  明瞭な正相関\n\n"
         "・湿度\n  負相関\n\n"
         "・日射量\n  最強の正相関\n\n"
         "・WBGT\n  非線形\n\n"
         "・雲量\n  明確な関係なし\n\n"
         "・体感気温\n  線形に近い正相関",
         size=10.5, color=YU_GREY)

add_notes(slide,
"次に各気象変数と電力 b00 の関係を散布図で見ます。色は時刻を表します。\n"
"気温と日射量は明瞭な正相関、湿度は負相関、WBGT は非線形、雲量は\n"
"明確な関係なし、体感気温は線形に近い正相関を示します。\n"
"視覚的傾向は把握できましたが、次に定量的な相関係数で評価します。")

# ===========================================================================
# SLIDE 8: Pearson/Spearman heatmaps
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 8)
add_title(slide, "相関分析①  Pearson / Spearman 相関係数",
          "→ 定量的に「電力を駆動する気象因子」をランク付け")

slide.shapes.add_picture(f"{FIG}/corr_01_pearson_heatmap.png",
                          Inches(0.3), Inches(1.9), width=Inches(6.4))
add_text(slide, Inches(0.3), Inches(6.65), Inches(6.4), Inches(0.3),
         "(a) 時間別データ (n=2,635 hours)",
         size=10.5, bold=True, color=YU_GREY, align=PP_ALIGN.CENTER)

slide.shapes.add_picture(f"{FIG}/corr_02_daily_heatmap.png",
                          Inches(6.9), Inches(1.9), width=Inches(6.2))
add_text(slide, Inches(6.9), Inches(6.65), Inches(6.2), Inches(0.3),
         "(b) 日単位集計後 (n=113 days)",
         size=10.5, bold=True, color=YU_GREY, align=PP_ALIGN.CENTER)

add_notes(slide,
"Pearson 相関と Spearman 順位相関のヒートマップです。\n"
"左が時間別、右が日単位集計後の相関です。\n\n"
"時間別での最強の相関は:\n"
"・日射量: Pearson r=+0.67 (最強の正相関)\n"
"・気温: r=+0.57\n"
"・湿度: r=-0.52 (最強の負相関)\n\n"
"日単位に集計しても傾向は同じです。日射・気温・湿度の3変数が支配的な\n"
"要因であることが分かります。\n\n"
"しかし、これが本物の関係性か、それとも「日内変動の見せかけ」かを\n"
"次のスライドで検証します。")

# ===========================================================================
# SLIDE 9: Hour-stratified (KEY)
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 9)
add_title(slide, "相関分析②  時刻別 層別化相関 (重要発見)",
          "→ 日内変動の交絡を除去 → 真の気象効果を抽出")

slide.shapes.add_picture(f"{FIG}/corr_04_hourly_stratified.png",
                          Inches(0.4), Inches(1.9), width=Inches(12.5))

add_rect(slide, Inches(0.4), Inches(5.9), Inches(12.55), Inches(1.1),
         ACCENT_BG, line=YU_ORANGE)
add_text(slide, Inches(0.6), Inches(6.0), Inches(12.3), Inches(0.4),
         "■ 重要な発見:  時刻を固定しても気温・WBGT・体感気温の正相関は維持",
         size=13, bold=True, color=YU_NAVY)
add_text(slide, Inches(0.6), Inches(6.45), Inches(12.3), Inches(0.5),
         "  → 「日射と電力が共にピークを取るのは時刻が同じだから」という擬似相関ではなく、\n"
         "     「暑い日ほど電力が増える」という本質的な気象-電力結合が存在することを実証",
         size=11, color=YU_GREY)

add_notes(slide,
"本研究の重要な発見の一つです。\n\n"
"日射と電力は共に正午頃ピークを取るので、時刻という交絡因子による\n"
"擬似相関の懸念があります。\n"
"そこで時刻別に層別化した相関を計算しました。同じ時刻内で気象と\n"
"電力がどう動くかを見る分析です。\n\n"
"結果、気温・WBGT・体感気温の正相関は、ほぼすべての時刻で維持\n"
"されています。\n"
"これは『暑い日ほど電力が増える』という本質的な結合の存在を実証\n"
"しており、見かけ相関ではないと言えます。")

# ===========================================================================
# SLIDE 10: Standardized regression
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 10)
add_title(slide, "相関分析③  標準化重回帰係数 β",
          "→ 各気象変数の「相対的寄与度」を一つの指標で比較")

slide.shapes.add_picture(f"{FIG}/corr_07_standardized_beta.png",
                          Inches(0.4), Inches(1.9), width=Inches(8.0))

add_text(slide, Inches(8.6), Inches(2.0), Inches(4.5), Inches(0.4),
         "■ 主な所見", size=14, bold=True, color=YU_NAVY)
add_text(slide, Inches(8.6), Inches(2.5), Inches(4.5), Inches(4.5),
         "1. 最大の正寄与: 日射量\n"
         "    β = +0.41\n\n"
         "2. 次点: 気温\n"
         "    β = +0.22\n\n"
         "3. 最大の負寄与: 湿度\n"
         "    β = −0.19\n\n"
         "4. 寄与小: 風・降水・雲量\n\n"
         "5. R² = 0.527\n"
         "   気象だけで電力分散の\n"
         "   53% を説明",
         size=12, color=YU_GREY)

add_notes(slide,
"標準化重回帰係数 β は『他の変数の影響を取り除いた独立な寄与』を表します。\n"
"派生変数 (体感気温・WBGT 等) は共線性が高いため、7つの独立した気象\n"
"変数のみで再回帰しました。\n\n"
"最大の正寄与は日射量 β=+0.41、次が気温 β=+0.22、最大の負寄与は\n"
"湿度 β=-0.19 です。\n"
"重要な指標として R² = 0.527。つまり気象変数だけで電力分散の53%を\n"
"説明できることが分かりました。残りの47%は曜日・時刻・休日等の\n"
"非気象要因です。")

# ===========================================================================
# SLIDE 11: PCA variance
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 11)
add_title(slide, "主成分分析①  各主成分の寄与率",
          "→ 気象10変数を「独立な3軸」に次元削減")

slide.shapes.add_picture(f"{FIG}/corr_05_pca_variance.png",
                          Inches(0.4), Inches(1.9), width=Inches(8.0))

add_text(slide, Inches(8.6), Inches(2.0), Inches(4.5), Inches(0.4),
         "■ なぜ PCA を使うか", size=14, bold=True, color=YU_NAVY)
add_text(slide, Inches(8.6), Inches(2.5), Inches(4.5), Inches(4.5),
         "問題:\n"
         "  気象10変数は互いに\n"
         "  相関 → 寄与解釈が困難\n\n"
         "解決:\n"
         "  PCAで直交独立な成分に\n"
         "  変換\n\n"
         "結果:\n"
         "  ・PC1: 41.7%\n"
         "  ・PC2: 21.1%\n"
         "  ・PC3: 13.1%\n"
         "  → 3成分で 76% を説明",
         size=12, color=YU_GREY)

add_notes(slide,
"気象10変数は互いに相関しているため、独立な寄与の解釈が困難です。\n"
"そこで PCA で直交独立な成分に変換しました。\n\n"
"PC1 が 41.7%、PC2 が 21.1%、PC3 が 13.1%。3 つの主成分だけで気象\n"
"変動の76%を説明できます。\n"
"残りの4成分は寄与が5%以下と小さく、本質的な変動は3軸で十分捉え\n"
"られます。")

# ===========================================================================
# SLIDE 12: PCA loadings
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 12)
add_title(slide, "主成分分析②  各主成分の構成と b00 への影響",
          "→ 主成分の物理的意味 + b00 との関係性を定量化")

slide.shapes.add_picture(f"{FIG}/corr_06_pca_loadings.png",
                          Inches(0.4), Inches(1.9), width=Inches(12.5))

add_rect(slide, Inches(0.4), Inches(5.9), Inches(12.55), Inches(1.1),
         ACCENT_BG, line=YU_ORANGE)
add_text(slide, Inches(0.6), Inches(5.95), Inches(12.3), Inches(0.4),
         "■ 主成分の物理的解釈",
         size=13, bold=True, color=YU_NAVY)
add_text(slide, Inches(0.6), Inches(6.35), Inches(12.3), Inches(0.65),
         "・PC1 (41.7%) = 「熱関連成分」 (気温・WBGT・体感気温が同方向)  → b00 と r=+0.47\n"
         "・PC2 (21.1%) = 「湿度↑×日射↓ の悪天候成分」  (湿度高+日射弱)  → b00 と r=−0.50\n"
         "・PC3 (13.1%) = 「風・降水成分」 (b00 への影響は小さい r=+0.16)",
         size=11, color=YU_GREY)

add_notes(slide,
"PCA の本質を見ます。\n"
"PC1 は気温・WBGT・体感気温が共に高い正の寄与で「熱関連成分」と解釈\n"
"でき、b00 と +0.47 の相関です。「暑い日 → 電力増」という直感に合います。\n\n"
"PC2 は湿度が大きな正、日射が大きな負の寄与で『悪天候成分』。b00 とは\n"
"-0.50 の相関で、悪天候の日は電力が下がります。\n\n"
"PC3 は風・降水で影響は限定的です。\n\n"
"まとめると、気象変動は『熱』と『天候』の2軸で大半が表現でき、これが\n"
"電力に強く影響することが定量的に示されました。")

# ===========================================================================
# SLIDE 13: Prediction model + CCRI bridge
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 13)
add_title(slide, "予測モデル: ハイブリッド気象入力 + 結果",
          f"Q1 の知見を活用 → MAE = {PS['results']['C_Hybrid']['MAE']} kW → CCRI へ接続")

slide.shapes.add_picture(f"{FIG}/pres_03_arch_compare.png",
                          Inches(0.3), Inches(1.9), width=Inches(7.0))
slide.shapes.add_picture(f"{FIG}/pres_04_holdout_timeseries.png",
                          Inches(7.5), Inches(1.9), width=Inches(5.6))

# Bridge to CCRI
add_rect(slide, Inches(0.4), Inches(5.7), Inches(12.55), Inches(1.3),
         LIGHT_BG, line=YU_RED)
add_text(slide, Inches(0.55), Inches(5.78), Inches(12.3), Inches(0.4),
         "■ 性能 → 警報への流れ",
         size=13, bold=True, color=YU_NAVY)
add_text(slide, Inches(0.55), Inches(6.18), Inches(12.3), Inches(0.8),
         f"・MAE = {PS['results']['C_Hybrid']['MAE']} kW,  "
         f"R² = {PS['results']['C_Hybrid']['R2']},  "
         f"MAPE = {PS['results']['C_Hybrid']['MAPE']}%   "
         "(従来比 10% 改善、観測上限の 94%)\n"
         "・予測値 → CCRI 算出 → Normal / High / Critical 分類 → 管理者へ配信 (次スライドで詳細)",
         size=11, color=YU_GREY)

add_notes(slide,
"Q1で発見した気象の影響構造を活かし、翌日のピーク予測モデルを構築しました。\n"
"工夫は『ハイブリッド気象入力』で、過去の気象は ERA5 観測、未来の気象は\n"
"JMA 予報を使い分けます。\n\n"
"3アーキテクチャ比較:\n"
"・A 観測のみ MAE 50.7 kW (理論上限)\n"
"・B 予報のみ MAE 59.7 kW (従来)\n"
"・C ハイブリッド MAE 54.0 kW (本研究)\n"
"理論上限とわずか6%、従来比10%改善です。\n\n"
"しかし予測がゴールではありません。予測値を CCRI で集約し、警報レベル\n"
"に分類して管理者へ配信する、これが Q3 で次のスライドで説明します。")

# ===========================================================================
# SLIDE 14: CCRI Alert Design (NEW)
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 14)
add_title(slide, "Q3  CCRI 警報の設計と配信",
          "予測値 → リスク指標 → 警報レベル → 配信タイミング")

# Left: CCRI formula
add_text(slide, Inches(0.4), Inches(1.95), Inches(6.0), Inches(0.4),
         "■ CCRI 算出式", size=14, bold=True, color=YU_NAVY)
add_rect(slide, Inches(0.4), Inches(2.4), Inches(6.2), Inches(1.5),
         LIGHT_BG, line=YU_NAVY)
add_text(slide, Inches(0.55), Inches(2.5), Inches(5.9), Inches(0.45),
         "CCRI = 0.50 × (予測値 / P80)\n"
         "       + 0.30 × P95超過確率",
         size=12.5, bold=True, color=YU_NAVY)
add_text(slide, Inches(0.55), Inches(3.4), Inches(5.9), Inches(0.45),
         "       + 0.20 × (6h 連続超過時間 / 6)",
         size=12.5, bold=True, color=YU_NAVY)

# Left: tier explanation
add_text(slide, Inches(0.4), Inches(4.05), Inches(6.0), Inches(0.4),
         "■ 警報レベル", size=14, bold=True, color=YU_NAVY)

def tier(y, color, lvl, range_str, action):
    add_rect(slide, Inches(0.4), y, Inches(0.7), Inches(0.55), color)
    add_text(slide, Inches(0.4), y, Inches(0.7), Inches(0.55),
             lvl, size=12, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(1.2), y, Inches(2.3), Inches(0.55),
             range_str, size=11, bold=True, color=YU_GREY,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(3.6), y, Inches(3.0), Inches(0.55),
             action, size=11, color=YU_GREY, anchor=MSO_ANCHOR.MIDDLE)

tier(Inches(4.5), RED_ALERT, "🔴",  "Critical  CCRI ≥ 0.85", "メール + SMS")
tier(Inches(5.1), ORANGE_HI, "🟠", "High      0.65 ≤ CCRI < 0.85", "メール")
tier(Inches(5.7), GREEN_OK,  "🟢",  "Normal    CCRI < 0.65", "通知なし")

# Right: workflow
add_text(slide, Inches(7.0), Inches(1.95), Inches(6.0), Inches(0.4),
         "■ 配信ワークフロー (1 日 1 回)", size=14, bold=True, color=YU_NAVY)

def step(y, t, label, sub):
    add_rect(slide, Inches(7.0), y, Inches(1.7), Inches(0.55),
             YU_NAVY_LT)
    add_text(slide, Inches(7.0), y, Inches(1.7), Inches(0.55),
             t, size=11, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(8.8), y, Inches(4.2), Inches(0.55),
             label, size=11, color=YU_GREY,
             anchor=MSO_ANCHOR.MIDDLE)

step(Inches(2.45), "当日 16:00", "JMA予報・最新観測の自動取得",  None)
step(Inches(3.1),  "当日 16:30", "ハイブリッドモデル予測実行", None)
step(Inches(3.75), "当日 16:45", "CCRI 算出・警報レベル分類", None)
step(Inches(4.4),  "当日 17:00", "管理者へメール/SMS 配信 ★", None)
step(Inches(5.05), "当日 17:00–", "管理者が Soft DR 措置を判断", None)
step(Inches(5.7),  "翌日", "実績との比較で品質検証", None)

# Bottom emphasis
add_rect(slide, Inches(0.4), Inches(6.4), Inches(12.55), Inches(0.55),
         ACCENT_BG, line=YU_ORANGE)
add_text(slide, Inches(0.55), Inches(6.45), Inches(12.3), Inches(0.45),
         "■ Soft DR 措置の選択 (節電依頼・温度調整・照明・機器シフト等) は 管理者の判断",
         size=12.5, bold=True, color=YU_RED, anchor=MSO_ANCHOR.MIDDLE)

add_notes(slide,
"これが本研究の応用部分、Q3 の内容です。CCRI 警報の設計と配信について\n"
"ご説明します。\n\n"
"CCRI = Campus Critical Risk Index は、3つの要素の重み付き和です。\n"
"・50% × 予測値の相対大きさ (P80 比)\n"
"・30% × P95 超過確率 (分類モデルから)\n"
"・20% × 6時間連続超過の長さ (持続性)\n"
"これにより『大きさ』『確率』『持続』の3軸で総合的にリスクを評価します。\n\n"
"閾値による3段階分類:\n"
"・Critical (CCRI ≥ 0.85): メール + SMS の緊急配信\n"
"・High (0.65 ≤ CCRI < 0.85): メール通知\n"
"・Normal (< 0.65): 通知なし\n\n"
"配信ワークフローは1日1回、当日17時に翌日の警報を配信します。\n"
"16時に予報取得 → 16:30 予測 → 16:45 CCRI 算出 → 17:00 配信、という\n"
"自動化フローです。\n\n"
"最後に強調したい点ですが、実際の Soft DR 措置 — 節電依頼、温度調整、\n"
"照明調光、機器シフト等 — の選択は、設備管理者の判断によります。\n"
"本システムは情報を提供し、人間が最終決定する設計です。")

# ===========================================================================
# SLIDE 15: SHAP
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 15)
add_title(slide, "解釈と検証: SHAP値が示す重要特徴量",
          "→ 機械学習モデルが Q1 の発見 (熱関連 + 日射) と一致する特徴量を重視")

slide.shapes.add_picture(f"{FIG}/pres_06_shap_top10.png",
                          Inches(0.3), Inches(1.9), width=Inches(8.0))

add_text(slide, Inches(8.5), Inches(2.0), Inches(4.5), Inches(0.4),
         "■ 統計-機械学習の整合性", size=14, bold=True, color=YU_NAVY)
add_text(slide, Inches(8.5), Inches(2.5), Inches(4.5), Inches(4.5),
         "Q1 の発見:\n"
         "  熱関連 (PC1) + 過去負荷\n\n"
         "SHAP 上位 (機械学習):\n"
         "  1. 前週同時刻負荷\n"
         "  2. 営業日フラグ\n"
         "  3. 前日同時刻気温 ←気象\n"
         "  4. 前日同時刻負荷\n"
         "  5. 年内日付\n"
         "  6. 日射量 (予報) ←気象\n\n"
         "→ 統計 (気象) +\n"
         "    時間構造 (周期)\n"
         "    の両方を学習",
         size=11, color=YU_GREY)

add_notes(slide,
"最後に SHAP 値で機械学習モデルの解釈を確認します。\n\n"
"SHAP 上位の特徴量は、前週同時刻負荷、営業日フラグ、前日同時刻気温、\n"
"前日同時刻負荷、年内日付、日射量予報の順です。\n\n"
"重要なのは、Q1 で発見した『熱関連 (気温)』と『日射量』が SHAP 上位\n"
"にも入っていることです。これは『機械学習モデルが統計分析と整合的な\n"
"要因を学んだ』ことの検証になります。\n\n"
"加えて、機械学習は『前週負荷』『前日負荷』など時間構造も学習しており、\n"
"これが予測精度の向上に寄与しています。")

# ===========================================================================
# SLIDE 16: Summary + future
# ===========================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
header_footer(slide, 16)
add_title(slide, "まとめと今後の課題", "達成内容と次のステップ")

# Achievements
add_rect(slide, Inches(0.4), Inches(1.95), Inches(6.2), Inches(0.5), YU_NAVY)
add_text(slide, Inches(0.55), Inches(2.02), Inches(6.0), Inches(0.4),
         "■ 達成した成果", size=14, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
add_rect(slide, Inches(0.4), Inches(2.45), Inches(6.2), Inches(3.7), LIGHT_BG, line=YU_NAVY)
add_text(slide, Inches(0.55), Inches(2.6), Inches(5.9), Inches(3.5),
         "1. Q1. 気象-電力関係の解明\n"
         "    ・気象だけで b00 分散の 53% 説明\n"
         "    ・PC1(熱)+PC2(湿度×日射) で 63%要約\n\n"
         "2. Q2. 翌日ピーク予測の達成\n"
         "    ・ハイブリッド手法で MAE = 54 kW\n"
         "    ・観測上限の 94% を実運用で実現\n\n"
         "3. Q3. 警報配信フレーム設計\n"
         "    ・CCRI 3 段階分類\n"
         "    ・自動配信ワークフロー定義\n\n"
         "4. SHAP で統計-機械学習の整合性確認",
         size=11.5, color=YU_GREY)

# Future work
add_rect(slide, Inches(6.85), Inches(1.95), Inches(6.1), Inches(0.5), YU_ORANGE)
add_text(slide, Inches(7.0), Inches(2.02), Inches(5.9), Inches(0.4),
         "■ 今後の課題", size=14, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
add_rect(slide, Inches(6.85), Inches(2.45), Inches(6.1), Inches(3.7), LIGHT_BG, line=YU_ORANGE)
add_text(slide, Inches(7.0), Inches(2.6), Inches(5.8), Inches(3.5),
         "1. データ拡張\n"
         "    ・2025年通年データ取得\n"
         "    ・冬季 (暖房) 需要の評価\n\n"
         "2. 警報品質のフィールド検証\n"
         "    ・予報精度の継続評価\n"
         "    ・空振り率/見逃し率の運用測定\n\n"
         "3. 管理者の意思決定評価  ★新\n"
         "    ・インタビュー・アンケート\n"
         "    ・警報受信 → どの Soft DR を選択?\n"
         "    ・信頼性・実用性の評価\n\n"
         "4. 他棟 (b01-b15) へのスケール",
         size=11.5, color=YU_GREY)

# Thank-you bar
add_rect(slide, Inches(0.4), Inches(6.2), Inches(12.55), Inches(0.65), YU_NAVY)
add_text(slide, Inches(0.4), Inches(6.25), Inches(12.55), Inches(0.55),
         "ご清聴ありがとうございました。  ご質問をお待ちしております。",
         size=18, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_notes(slide,
"まとめです。達成した成果は4点:\n"
"1. Q1 気象-電力関係の解明: 気象だけで b00 分散の 53% を説明、主成分で\n"
"   気象変動の63%を要約\n"
"2. Q2 翌日ピーク予測: ハイブリッド手法で MAE 54 kW、観測上限の94%を実現\n"
"3. Q3 警報配信フレーム設計: CCRI 3段階分類 + 自動ワークフロー定義\n"
"4. SHAP で統計分析と機械学習の整合性を確認\n\n"
"今後の課題は4点:\n"
"1. データ拡張 (2025年通年・冬季暖房評価)\n"
"2. 警報品質のフィールド検証 — 予報精度・空振り率・見逃し率を運用で測定\n"
"3. 管理者の意思決定評価 ← 重要な新規課題。インタビュー・アンケートで、\n"
"   警報受信時に管理者がどの Soft DR 措置を選択し、信頼性と実用性をどう\n"
"   評価するかを定量的に調べます。これにより情報提供から意思決定支援の\n"
"   品質まで全体を評価できます。\n"
"4. 他棟へのスケール\n\n"
"以上、ご清聴ありがとうございました。ご質問をお願いいたします。")

# ============================================================================
# Save with today's date suffix
# ============================================================================
out_pptx = f"{OUT}/SDR_research_progress_jp_{TODAY}.pptx"
prs.save(out_pptx)
print(f"\n✅ PPT v4 saved → {out_pptx}")
print(f"   Slides: {len(prs.slides)}")
print(f"   Size  : {os.path.getsize(out_pptx) / 1024:.1f} KB")
