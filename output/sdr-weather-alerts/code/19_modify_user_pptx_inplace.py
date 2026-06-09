"""Modify the user's existing PPT in-place.

Source: user-uploaded SDR_research_progress_jp.pptx (12 slides)
Output: SDR_research_progress_jp_<today>.pptx (14 slides)

Preserves user customizations:
  - Author "劉 海強 (山口大学 工学部)"
  - Footer "省エネ推進室2026"
  - Slide numbering style, colors, layout

Modifications:
  1. Slide 1: rewrite Notes to clarify SDR = Soft Demand Response, not direct control
  2. Slide 2 pillar ②: replace "空調設定温度を1〜2℃上げる..." with Soft DR multi-option text
  3. Slide 2 pillar ③: replace "SDR発令" with "警報配信 + 管理者判断"
  4. Slide 3: update objective + add Q3 banner about alert delivery framework
  5. Slide 4: replace "ERA5 / AMeDAS同等" with proper ERA5 disclosure note
  6. Slide 9: update P80 description as "SDR発令検討基準" → "管理者への警報基準"
  7. NEW Slide (inserted before Summary): System Overview with HiL boundary
  8. NEW Slide (inserted before Summary): CCRI Alert design + workflow
  9. Slide 12 (Summary, will become 14): update future work — "実機運用試験" → "管理者意思決定評価"
"""
import os, copy, shutil
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

SRC = "/root/.claude/uploads/e566ceec-d72b-4f61-8520-232fd7aca1fd/cd1fae11-SDR_research_progress_jp.pptx"
OUT_DIR = "/home/user/academic-research-skills/output/sdr-weather-alerts/presentation"
FIG = "/home/user/academic-research-skills/output/sdr-weather-alerts/figures_pres"
TODAY = datetime.now().strftime("%Y%m%d")
OUT = f"{OUT_DIR}/SDR_research_progress_jp_{TODAY}.pptx"

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
JP_FONT = "Yu Gothic"

# Copy first (so source untouched if anything fails)
prs = Presentation(SRC)

# ============================================================================
# Helpers
# ============================================================================
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

def replace_textframe(shape, new_text, size=None, bold=None, color=None):
    """Replace all paragraphs in a text frame with new text, preserving frame."""
    tf = shape.text_frame
    # Clear existing paragraphs (keep first)
    p0 = tf.paragraphs[0]
    # Remove extra paragraphs
    for p in list(tf.paragraphs[1:]):
        p._p.getparent().remove(p._p)
    # Clear runs in first paragraph
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    # Determine font defaults from existing or use new
    lines = new_text.split("\n") if isinstance(new_text, str) else new_text
    for i, ln in enumerate(lines):
        p = p0 if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = ln
        if size:  run.font.size = Pt(size)
        if bold is not None: run.font.bold = bold
        if color is not None: run.font.color.rgb = color
        run.font.name = JP_FONT
        rPr = run._r.get_or_add_rPr()
        ea = rPr.find(qn("a:ea"))
        if ea is None:
            ea = rPr.makeelement(qn("a:ea"), {"typeface": JP_FONT}); rPr.append(ea)
        else:
            ea.set("typeface", JP_FONT)

def set_notes(slide, text):
    try:
        ns = slide.notes_slide
        n = ns.notes_text_frame
        if n is None:
            return   # user's pptx notes master has no placeholder; skip silently
        n.text = ""
        for i, ln in enumerate(text.split("\n")):
            p = n.paragraphs[0] if i == 0 else n.add_paragraph()
            p.text = ln
    except (AttributeError, KeyError):
        pass


# ============================================================================
# Audit: find shapes by text content (helper for in-place edits)
# ============================================================================
def find_shape_with_text(slide, marker):
    for sh in slide.shapes:
        if sh.has_text_frame and marker in sh.text_frame.text:
            return sh
    return None

# ============================================================================
# SLIDE 1: Update Notes (preserve title content as-is)
# ============================================================================
s1 = prs.slides[0]
set_notes(s1,
"皆さま、本日はお時間をいただきありがとうございます。\n"
"建築学科の劉です。\n"
"本日は『天気予報を活用したキャンパスSDR運用支援システム』について研究の紹介をいたします。\n\n"
"まず重要なキーワードのご確認ですが、本研究の SDR とは「Soft Demand Response」、\n"
"つまり強制的な制御ではなく、節電依頼・設備運用調整・利用者への協力呼びかけ等の\n"
"非強制的な需要調整の総称です。経済産業省 ERAB でも使われる用語です。\n\n"
"本研究は『警報・予告を配信する仕組み』であって、設定温度を自動的に変える等の\n"
"制御システムではありません。予測結果を警報として配信し、最終的な判断は\n"
"設備管理者が行う、意思決定支援の枠組みです。\n\n"
"発表のキーポイントは、(1) 気象と電力の関係性を統計的に解明したこと、\n"
"(2) ハイブリッド気象入力で精度の高い予測モデルを構築したこと、\n"
"(3) CCRI 警報配信フレームワークを設計したこと、の3点です。")

# ============================================================================
# SLIDE 2: Pillar ② and ③ rewording
# ============================================================================
s2 = prs.slides[1]
# Pillar ② body (find by content marker)
p2_body = find_shape_with_text(s2, "設定温度を1〜2")
if p2_body:
    replace_textframe(p2_body,
        "・Soft DR は多様な選択肢\n"
        "  節電依頼/設定温度調整/\n"
        "  照明調光/機器シフト 等\n"
        "・5〜10% の節電効果\n"
        "・管理者が状況に応じ\n"
        "  非強制的に選択",
        size=13, color=YU_GREY)

# Pillar ③ body
p3_body = find_shape_with_text(s2, "SDR発令")
if p3_body:
    replace_textframe(p3_body,
        "・前日の気象予報から\n"
        "  翌日ピークを予測\n"
        "・警報レベルに分類して\n"
        "  管理者へ配信\n"
        "・Soft DR 措置は\n"
        "  管理者の判断で実施",
        size=13, color=YU_GREY)

# Add a clarifying banner at the bottom (new shape)
add_rect(s2, Inches(0.4), Inches(6.4), Inches(12.55), Inches(0.5),
         ACCENT_BG, line=YU_RED)
add_text(s2, Inches(0.55), Inches(6.45), Inches(12.3), Inches(0.4),
         "■ 本研究は「予告・警報を出すまで」が範囲: 実際の Soft DR 措置は管理者の判断による",
         size=12.5, bold=True, color=YU_RED, anchor=MSO_ANCHOR.MIDDLE)

set_notes(s2,
"研究背景を3点でご説明します。\n"
"①、近年の猛暑により電力需要が増加。キャンパス電力の約40%が空調由来です。\n"
"②、Soft DR は多様な選択肢を含む幅広い概念です。節電依頼の学内放送、設定温度\n"
"調整、照明調光、機器運用シフト、利用者協力呼びかけなど、管理者が状況に応じて\n"
"選択する非強制的な手段の総称です。\n"
"③、本研究では翌日のピーク発生可能性を「警報レベル」に分類し、設備管理者に\n"
"配信する仕組みを開発します。\n\n"
"重要な点として、本研究は「予告・警報を出すまで」が範囲です。実際に Soft DR\n"
"措置を選択・実施するのは設備管理者の判断であり、必ず人間が介在する意思決定\n"
"支援システム、という位置付けです。")

# ============================================================================
# SLIDE 3: Update objective text + add Q3 banner
# ============================================================================
s3 = prs.slides[2]
# Update right column (Approach body) — find by content
approach_body = find_shape_with_text(s3, "ハイブリッド気象入力")
# Find specifically the body, not title
for sh in s3.shapes:
    if sh.has_text_frame and "発想:" in sh.text_frame.text:
        replace_textframe(sh,
            "発想:\n"
            "  「過去の気象は観測 (ERA5)、\n"
            "    未来の気象は予報 (JMA MSM)」\n\n"
            "理由:\n"
            "  ・過去 → 観測済み、誤差ゼロ\n"
            "  ・未来 → 観測不可、予報が唯一\n\n"
            "結果:\n"
            "  訓練データの質と\n"
            "  実運用の現実性を両立",
            size=13, color=YU_GREY)
        break

# Update left column (Objective body) — mention warning
for sh in s3.shapes:
    if sh.has_text_frame and "目標:" in sh.text_frame.text:
        replace_textframe(sh,
            "目標:\n"
            "  当日 17 時時点で、翌日 0〜23 時の\n"
            "  各時間電力 b00 (kW) を予測\n\n"
            "条件:\n"
            "  ・気象予報 (JMA MSM) を活用\n"
            "  ・実運用可能 (未来情報を使わない)\n"
            "  ・予測精度 MAE ≦ 60 kW\n\n"
            "出力:\n"
            "  時間予測値 → CCRI → 警報",
            size=13, color=YU_GREY)
        break

# Update subtitle to mention Q3
sub_sh = find_shape_with_text(s3, "翌日ピーク予測")
if sub_sh:
    replace_textframe(sub_sh,
        "翌日ピーク予測 → CCRI 警報配信 → 管理者の Soft DR 判断",
        size=14, color=YU_GREY)

# Add bottom banner showing 3 phases
add_rect(s3, Inches(0.4), Inches(6.4), Inches(12.55), Inches(0.5),
         ACCENT_BG, line=YU_ORANGE)
add_text(s3, Inches(0.55), Inches(6.45), Inches(12.3), Inches(0.4),
         "■ 3 段階アプローチ: ① 気象-電力関係の理解  ② 翌日ピーク予測  ③ 警報配信 (CCRI) — Slide 12 で詳述",
         size=12, bold=True, color=YU_NAVY, anchor=MSO_ANCHOR.MIDDLE)

set_notes(s3,
"研究の目的とアプローチです。\n"
"目的は当日17時の時点で翌日各時間の電力負荷を予測し、それを CCRI という\n"
"指標で集約して警報レベルに分類、設備管理者へ配信することです。\n\n"
"アプローチの工夫として、ハイブリッド気象入力を提案します。\n"
"過去の気象は ERA5 観測値、未来の気象は JMA MSM 予報を使い分けることで、\n"
"訓練データの質と実運用での現実性を両立させます。\n\n"
"研究は 3 段階のアプローチで構成されます。\n"
"① 気象-電力関係の理解 (相関+PCA)\n"
"② 翌日ピーク予測 (LightGBM)\n"
"③ 警報配信 (CCRI 設計) — Slide 12 で詳述")

# ============================================================================
# SLIDE 4: ERA5 disclosure
# ============================================================================
s4 = prs.slides[3]
era5_sh = find_shape_with_text(s4, "ERA5 / AMeDAS")
if era5_sh:
    replace_textframe(era5_sh,
        "1. キャンパス電力 (1時間値)\n"
        "    建物 b00 〜 b15, 計15棟\n"
        "    本研究は b00 (主棟) を対象\n\n"
        "2. 気象観測 (ERA5 再解析)\n"
        "    ※ AMeDAS 宇部は湿度なしのため\n"
        "    気温・湿度・日射・WBGT 等\n\n"
        "3. 気象予報 (JMA MSM, 5km)\n"
        "    最大39時間先まで利用可能\n\n"
        "4. カレンダー (営業日, 休日, 曜日)",
        size=12.5, color=YU_GREY)

set_notes(s4,
"使用したデータをご説明します。\n"
"電力データは BEMS から取得した1時間値、b00 主棟を対象です。\n\n"
"重要な開示として、気象観測には ERA5 再解析データを採用しました。\n"
"AMeDAS 宇部站は四要素観測 (気温・風・降水・日照) のみで、湿度・気圧の\n"
"観測がありません。ERA5 は ECMWF の全球再解析で、Hersbach 等 2020 年\n"
"以降エネルギー研究分野で標準的に使用されています。\n\n"
"気象予報には JMA MSM (5km 格子、+39h) を使用。\n"
"データ期間は 2025年 7-10月の約 4 ヶ月。今後 2025 年通年に拡張予定です。")

# ============================================================================
# SLIDE 9 (結果① 時系列): update P80 description
# ============================================================================
s9 = prs.slides[8]
p80_sh = find_shape_with_text(s9, "SDR発令検討基準")
if p80_sh:
    replace_textframe(p80_sh,
        "■ 青: 実測値    オレンジ: 予測値    赤点線: P80閾値 (管理者への警報配信基準)",
        size=13, bold=True, color=YU_NAVY)

# ============================================================================
# SLIDE 12 (Summary): update future work to mention 管理者意思決定評価
# ============================================================================
s12 = prs.slides[11]
future_sh = None
for sh in s12.shapes:
    if sh.has_text_frame and "実機運用" in sh.text_frame.text:
        future_sh = sh; break
if future_sh:
    replace_textframe(future_sh,
        "1. 通年データへの拡張\n"
        "    2025 年通年・冬季の暖房需要も検証\n\n"
        "2. 全15棟へのスケールアップ\n"
        "    棟ごとの特性を学習\n\n"
        "3. 管理者の意思決定評価 ★新\n"
        "    インタビュー・アンケートで\n"
        "    警報受信→ Soft DR 措置選択を調査\n\n"
        "4. CCRI 閾値・警報ルールの最適化",
        size=12.5, color=YU_GREY)

# Update achievements
ach_sh = None
for sh in s12.shapes:
    if sh.has_text_frame and "JMA予報を活用" in sh.text_frame.text:
        ach_sh = sh; break
if ach_sh:
    replace_textframe(ach_sh,
        "1. JMA予報を活用した翌日電力予測\n"
        "    ハイブリッド気象入力で MAE 54 kW\n\n"
        "2. 気象-電力関係の体系的解明\n"
        "    PCA で 3 主成分が 76% を説明\n\n"
        "3. CCRI 警報配信フレームの設計\n"
        "    Normal/High/Critical 3段階分類\n\n"
        "4. SHAP で統計-機械学習の整合性確認",
        size=12.5, color=YU_GREY)

set_notes(s12,
"最後にまとめです。本研究の達成内容は4点。\n"
"1. JMA 予報を活用した翌日電力予測。ハイブリッド気象入力で MAE 54 kW、\n"
"   観測上限の 94% の精度を実運用で実現しました。\n"
"2. 相関分析と PCA で気象-電力関係を体系的に解明。3 つの主成分が気象\n"
"   変動の 76% を説明します。\n"
"3. CCRI による警報配信フレームを設計。Normal/High/Critical の3段階分類\n"
"   で管理者へ配信します。\n"
"4. SHAP 解析で機械学習モデルが統計分析と整合的な要因を学んでいることを確認。\n\n"
"今後の課題は4点。\n"
"1. データ拡張: 2025年通年データで冬季暖房需要も検証\n"
"2. 全15棟へのスケールアップ\n"
"3. ★ 管理者の意思決定評価: インタビュー・アンケートで、警報受信時に\n"
"   どの Soft DR 措置を選択するか、信頼性・実用性を定量的に評価\n"
"4. CCRI 閾値・警報ルールの最適化\n\n"
"以上、ご清聴ありがとうございました。")

# ============================================================================
# Build NEW SLIDE: System Overview
# ============================================================================
blank = prs.slide_layouts[6]
sys_slide = prs.slides.add_slide(blank)

# Header/footer mimicking original style
add_rect(sys_slide, 0, 0, prs.slide_width, Inches(0.35), YU_NAVY)
add_text(sys_slide, Inches(0.3), Inches(0.04), Inches(11), Inches(0.27),
         "省エネ研究 (山口大学)", size=11, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
add_text(sys_slide, Inches(11.5), Inches(0.04), Inches(1.6), Inches(0.27),
         "Slide / 14", size=10, color=WHITE,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
add_rect(sys_slide, 0, prs.slide_height - Inches(0.25),
         prs.slide_width, Inches(0.25), YU_NAVY)
add_text(sys_slide, Inches(0.3), prs.slide_height - Inches(0.22),
         Inches(10), Inches(0.2),
         "山口大学 (Yamaguchi University) — 省エネ推進室2026",
         size=8.5, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

# Title
add_text(sys_slide, Inches(0.4), Inches(0.5), Inches(12.5), Inches(0.6),
         "システム全体像", size=24, bold=True, color=YU_NAVY)
add_rect(sys_slide, Inches(0.4), Inches(1.08), Inches(1.2), Inches(0.06), YU_ORANGE)
add_text(sys_slide, Inches(0.4), Inches(1.18), Inches(12.5), Inches(0.4),
         "気象データ → 予測 → 警報 → 管理者判断 → Soft DR 措置 (人間介在型)",
         size=13, color=YU_GREY)

# Flow boxes
def fbox(slide, x, y, w, h, label, sub, fc, tc=WHITE):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fc; sh.line.fill.background()
    sh.shadow.inherit = False
    add_text(slide, x, y + Inches(0.10), w, Inches(0.30),
             label, size=11.5, bold=True, color=tc,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, x, y + h - Inches(0.30), w, Inches(0.22),
             sub, size=9.5, color=tc,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# Left side: pipeline
add_text(sys_slide, Inches(0.4), Inches(1.9), Inches(2.5), Inches(0.3),
         "[入力層]", size=11.5, bold=True, color=YU_NAVY)
fbox(sys_slide, Inches(0.4), Inches(2.2), Inches(2.2), Inches(0.7),
     "気象観測", "ERA5 再解析", YU_NAVY)
fbox(sys_slide, Inches(2.85), Inches(2.2), Inches(2.2), Inches(0.7),
     "気象予報", "JMA MSM (+39h)", YU_NAVY_LT)
fbox(sys_slide, Inches(5.3), Inches(2.2), Inches(2.2), Inches(0.7),
     "電力履歴", "BEMS 1h", YU_NAVY_LT)

add_text(sys_slide, Inches(0.4), Inches(3.15), Inches(2.5), Inches(0.3),
         "[モデル層]", size=11.5, bold=True, color=YU_NAVY)
fbox(sys_slide, Inches(2.85), Inches(3.45), Inches(2.2), Inches(0.7),
     "LightGBM Hybrid", "MAE 54 kW", YU_ORANGE)

add_text(sys_slide, Inches(0.4), Inches(4.4), Inches(2.5), Inches(0.3),
         "[判定層]", size=11.5, bold=True, color=YU_NAVY)
fbox(sys_slide, Inches(2.85), Inches(4.7), Inches(2.2), Inches(0.7),
     "CCRI 算出", "リスク指標", YU_ORANGE)

add_text(sys_slide, Inches(0.4), Inches(5.65), Inches(2.5), Inches(0.3),
         "[配信層]", size=11.5, bold=True, color=YU_NAVY)
fbox(sys_slide, Inches(2.85), Inches(5.95), Inches(0.95), Inches(0.7),
     "Normal", "通知なし", GREEN_OK)
fbox(sys_slide, Inches(3.9), Inches(5.95), Inches(0.95), Inches(0.7),
     "High", "メール", ORANGE_HI)
fbox(sys_slide, Inches(4.95), Inches(5.95), Inches(0.95), Inches(0.7),
     "Critical", "SMS+メール", RED_ALERT)

# Dividing line + human boundary
add_rect(sys_slide, Inches(7.95), Inches(2.0), Inches(0.04), Inches(4.8), YU_RED)
add_text(sys_slide, Inches(7.5), Inches(1.85), Inches(1.0), Inches(0.3),
         "境界線", size=10, bold=True, color=YU_RED, align=PP_ALIGN.CENTER)

# Right column
add_text(sys_slide, Inches(8.4), Inches(1.9), Inches(4.7), Inches(0.3),
         "[管理者の判断 + Soft DR 措置]", size=11.5, bold=True, color=YU_RED)
add_rect(sys_slide, Inches(8.4), Inches(2.2), Inches(4.7), Inches(0.7),
         ACCENT_BG, line=YU_RED)
add_text(sys_slide, Inches(8.4), Inches(2.25), Inches(4.7), Inches(0.6),
         "★ 設備管理者の判断 ★\n警報受信 → 状況確認 → 措置選択",
         size=11, bold=True, color=YU_RED,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

def action(slide, y, num, lbl):
    add_text(slide, Inches(8.4), y, Inches(0.4), Inches(0.4),
             f"{num}.", size=12, bold=True, color=YU_NAVY,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(8.85), y, Inches(4.2), Inches(0.4),
             lbl, size=11, color=YU_GREY, anchor=MSO_ANCHOR.MIDDLE)

action(sys_slide, Inches(3.15), "1", "節電依頼の学内放送・メール")
action(sys_slide, Inches(3.65), "2", "空調設定温度の見直し (+1〜2℃)")
action(sys_slide, Inches(4.15), "3", "照明調光 (廊下・共用空間)")
action(sys_slide, Inches(4.65), "4", "非必須機器の運用時刻シフト")
action(sys_slide, Inches(5.15), "5", "利用者への協力呼びかけ")

add_rect(sys_slide, Inches(8.4), Inches(5.85), Inches(4.7), Inches(0.85),
         LIGHT_BG, line=YU_NAVY)
add_text(sys_slide, Inches(8.55), Inches(5.92), Inches(4.5), Inches(0.4),
         "本研究の境界線:", size=11, bold=True, color=YU_NAVY)
add_text(sys_slide, Inches(8.55), Inches(6.27), Inches(4.5), Inches(0.5),
         "「予測 → 警報配信」までが対象\nSoft DR 実施は管理者の判断",
         size=10, color=YU_GREY)

set_notes(sys_slide,
"本研究のシステム全体像をご説明します。\n\n"
"システムは4つの層で構成されています。\n"
"・入力層: 気象観測 (ERA5)、気象予報 (JMA MSM)、電力履歴 (BEMS)\n"
"・モデル層: LightGBM ハイブリッドモデル\n"
"・判定層: CCRI を算出してリスクを定量化\n"
"・配信層: Normal/High/Critical の3段階で管理者へ配信\n\n"
"重要なのは右側にある『境界線』です。本研究の範囲は警報配信までで、\n"
"その先の Soft DR 措置 — 節電依頼、設定温度調整、照明調光、機器シフト、\n"
"利用者協力呼びかけ等 — は、設備管理者の判断で実施されます。\n\n"
"つまり本システムは自動制御システムではなく、人間 (管理者) が判断する\n"
"ための情報を提供する意思決定支援システムである、ということです。")

# ============================================================================
# Build NEW SLIDE: CCRI Alert Design
# ============================================================================
ccri_slide = prs.slides.add_slide(blank)

# Header/footer
add_rect(ccri_slide, 0, 0, prs.slide_width, Inches(0.35), YU_NAVY)
add_text(ccri_slide, Inches(0.3), Inches(0.04), Inches(11), Inches(0.27),
         "省エネ研究 (山口大学)", size=11, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
add_text(ccri_slide, Inches(11.5), Inches(0.04), Inches(1.6), Inches(0.27),
         "Slide / 14", size=10, color=WHITE,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
add_rect(ccri_slide, 0, prs.slide_height - Inches(0.25),
         prs.slide_width, Inches(0.25), YU_NAVY)
add_text(ccri_slide, Inches(0.3), prs.slide_height - Inches(0.22),
         Inches(10), Inches(0.2),
         "山口大学 (Yamaguchi University) — 省エネ推進室2026",
         size=8.5, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

# Title
add_text(ccri_slide, Inches(0.4), Inches(0.5), Inches(12.5), Inches(0.6),
         "CCRI 警報の設計と配信", size=24, bold=True, color=YU_NAVY)
add_rect(ccri_slide, Inches(0.4), Inches(1.08), Inches(1.2), Inches(0.06), YU_ORANGE)
add_text(ccri_slide, Inches(0.4), Inches(1.18), Inches(12.5), Inches(0.4),
         "予測値 → リスク指標 → 警報レベル → 配信タイミング",
         size=13, color=YU_GREY)

# Left: CCRI formula
add_text(ccri_slide, Inches(0.4), Inches(1.95), Inches(6.0), Inches(0.4),
         "■ CCRI 算出式", size=14, bold=True, color=YU_NAVY)
add_rect(ccri_slide, Inches(0.4), Inches(2.4), Inches(6.2), Inches(1.5),
         LIGHT_BG, line=YU_NAVY)
add_text(ccri_slide, Inches(0.55), Inches(2.5), Inches(5.9), Inches(0.45),
         "CCRI = 0.50 × (予測値 / P80)\n"
         "       + 0.30 × P95超過確率",
         size=12.5, bold=True, color=YU_NAVY)
add_text(ccri_slide, Inches(0.55), Inches(3.4), Inches(5.9), Inches(0.45),
         "       + 0.20 × (6h 連続超過時間 / 6)",
         size=12.5, bold=True, color=YU_NAVY)

# Tier explanation
add_text(ccri_slide, Inches(0.4), Inches(4.05), Inches(6.0), Inches(0.4),
         "■ 警報レベル", size=14, bold=True, color=YU_NAVY)

def tier(slide, y, color, lvl, range_str, action):
    add_rect(slide, Inches(0.4), y, Inches(0.7), Inches(0.55), color)
    add_text(slide, Inches(0.4), y, Inches(0.7), Inches(0.55),
             lvl, size=12, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(1.2), y, Inches(2.3), Inches(0.55),
             range_str, size=11, bold=True, color=YU_GREY,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(3.6), y, Inches(3.0), Inches(0.55),
             action, size=11, color=YU_GREY, anchor=MSO_ANCHOR.MIDDLE)

tier(ccri_slide, Inches(4.5), RED_ALERT, "高",  "Critical CCRI ≥ 0.85", "メール + SMS")
tier(ccri_slide, Inches(5.1), ORANGE_HI, "中", "High 0.65 ≤ CCRI < 0.85", "メール")
tier(ccri_slide, Inches(5.7), GREEN_OK,  "低",  "Normal  CCRI < 0.65", "通知なし")

# Right: workflow
add_text(ccri_slide, Inches(7.0), Inches(1.95), Inches(6.0), Inches(0.4),
         "■ 配信ワークフロー (1 日 1 回)", size=14, bold=True, color=YU_NAVY)

def step(slide, y, t, label):
    add_rect(slide, Inches(7.0), y, Inches(1.7), Inches(0.55), YU_NAVY_LT)
    add_text(slide, Inches(7.0), y, Inches(1.7), Inches(0.55),
             t, size=11, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(8.8), y, Inches(4.2), Inches(0.55),
             label, size=11, color=YU_GREY, anchor=MSO_ANCHOR.MIDDLE)

step(ccri_slide, Inches(2.45), "当日 16:00", "JMA予報・最新観測の自動取得")
step(ccri_slide, Inches(3.1),  "当日 16:30", "ハイブリッドモデル予測実行")
step(ccri_slide, Inches(3.75), "当日 16:45", "CCRI 算出・警報レベル分類")
step(ccri_slide, Inches(4.4),  "当日 17:00", "管理者へメール/SMS 配信 ★")
step(ccri_slide, Inches(5.05), "当日 17:00–", "管理者が Soft DR 措置を判断")
step(ccri_slide, Inches(5.7),  "翌日", "実績との比較で品質検証")

# Bottom emphasis
add_rect(ccri_slide, Inches(0.4), Inches(6.4), Inches(12.55), Inches(0.55),
         ACCENT_BG, line=YU_ORANGE)
add_text(ccri_slide, Inches(0.55), Inches(6.45), Inches(12.3), Inches(0.45),
         "■ Soft DR 措置の選択 (節電依頼・温度調整・照明・機器シフト等) は 管理者の判断",
         size=12.5, bold=True, color=YU_RED, anchor=MSO_ANCHOR.MIDDLE)

set_notes(ccri_slide,
"これが本研究の応用部分です。CCRI 警報の設計と配信について説明します。\n\n"
"CCRI = Campus Critical Risk Index は、3つの要素の重み付き和で構成されます。\n"
"・50%: 予測値の相対大きさ (P80 比)\n"
"・30%: P95 超過確率 (分類モデルから)\n"
"・20%: 6時間連続超過の長さ (持続性)\n"
"『大きさ』『確率』『持続』の3軸で総合的にリスクを評価します。\n\n"
"閾値による3段階分類:\n"
"・Critical (CCRI ≥ 0.85): メール + SMS の緊急配信\n"
"・High (0.65 ≤ CCRI < 0.85): メール通知\n"
"・Normal (< 0.65): 通知なし\n\n"
"配信ワークフローは1日1回、当日17時に翌日の警報を配信します。\n"
"16時に予報取得 → 16:30 予測 → 16:45 CCRI 算出 → 17:00 配信、という\n"
"自動化フローです。\n\n"
"重要な点として、Soft DR 措置の選択 — 節電依頼、温度調整、照明調光、\n"
"機器シフト等 — は設備管理者の判断によります。\n"
"本システムは情報を提供し、人間が最終決定する設計です。")


# ============================================================================
# Reorder: move 2 new slides (current 13, 14) to positions 12, 13
# (so original Summary becomes 14)
# ============================================================================
xml_slides = prs.slides._sldIdLst
slides_list = list(xml_slides)
# Currently: [0..11] = original 12 slides, [12] = sys_overview, [13] = ccri
# We want: [0..10] = original 1-11, [11] = sys_overview, [12] = ccri, [13] = original Summary
old_summary = slides_list[11]      # original Slide 12 (Summary)
sys_overview = slides_list[12]
ccri = slides_list[13]
# Remove all three from end
for el in [old_summary, sys_overview, ccri]:
    xml_slides.remove(el)
# Re-append in desired order
xml_slides.append(sys_overview)
xml_slides.append(ccri)
xml_slides.append(old_summary)


# ============================================================================
# Update slide number footers (1/14, 2/14, ... 14/14)
# Find the "Slide N / 12" text on each slide and update to N / 14
# ============================================================================
total = len(prs.slides)
for i, slide in enumerate(prs.slides):
    new_no = i + 1
    for sh in slide.shapes:
        if sh.has_text_frame:
            t = sh.text_frame.text
            if "Slide " in t and "/" in t:
                # Replace whole frame
                replace_textframe(sh, f"Slide {new_no} / {total}",
                                  size=10, color=WHITE)
                # Re-apply right-align via paragraph
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.RIGHT
                break

# ============================================================================
# Save
# ============================================================================
prs.save(OUT)
print(f"✅ Modified PPT saved → {OUT}")
print(f"   Total slides: {total}")
print(f"   Size       : {os.path.getsize(OUT) / 1024:.1f} KB")
