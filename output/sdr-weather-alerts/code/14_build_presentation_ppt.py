"""Build Yamaguchi-University-style Japanese PPT for the energy-saving conference.

12 slides, 16:9. Yamaguchi blue (#003B71) header + footer. Each content slide
uses a 2-column layout: text on left, figure on right (or full-bleed figure).
Slide notes contain the Japanese speaker script (simple language).

v2 (2026-05-17): added correlation analysis (Slide 7) and PCA (Slide 8).
"""
import os, json
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

# Yamaguchi University palette
YU_NAVY   = RGBColor(0x00, 0x3B, 0x71)
YU_NAVY_LT= RGBColor(0x2A, 0x5A, 0x8E)
YU_ORANGE = RGBColor(0xE7, 0x8A, 0x00)
YU_GREEN  = RGBColor(0x2D, 0x9C, 0x5A)
YU_RED    = RGBColor(0xC8, 0x10, 0x2E)
YU_GREY   = RGBColor(0x5A, 0x5A, 0x5A)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG  = RGBColor(0xF4, 0xF6, 0xFA)

# Load summary
with open(f"{RES}/pres_summary.json", "r") as f:
    S = json.load(f)

# ============================================================================
# Helpers
# ============================================================================
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height

JP_FONT = "Yu Gothic"
JP_FONT_FALLBACK = "MS Gothic"


def set_jp_font(run, size=14, bold=False, color=None):
    run.font.name = JP_FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None: run.font.color.rgb = color
    # Apply Asian font fallback via OOXML
    rPr = run._r.get_or_add_rPr()
    eastAsia = rPr.find(qn("a:ea"))
    if eastAsia is None:
        eastAsia = rPr.makeelement(qn("a:ea"), {"typeface": JP_FONT})
        rPr.append(eastAsia)
    else:
        eastAsia.set("typeface", JP_FONT)


def add_text_box(slide, x, y, w, h, text, size=14, bold=False, color=None,
                 align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top  = Emu(0); tf.margin_bottom = Emu(0)
    lines = text.split("\n") if isinstance(text, str) else text
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = ln
        set_jp_font(r, size=size, bold=bold, color=color)
    return tb


def add_rect(slide, x, y, w, h, fill_color, line_color=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fill_color
    if line_color is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line_color; sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def add_header_footer(slide, slide_no, total=12, title_text="省エネ研究 (山口大学)"):
    # Top header band (navy)
    add_rect(slide, 0, 0, SW, Inches(0.35), YU_NAVY)
    add_text_box(slide, Inches(0.3), Inches(0.04), Inches(8), Inches(0.27),
                 title_text, size=11, bold=True, color=WHITE,
                 anchor=MSO_ANCHOR.MIDDLE)
    add_text_box(slide, Inches(11.5), Inches(0.04), Inches(1.6), Inches(0.27),
                 f"Slide {slide_no} / {total}",
                 size=10, color=WHITE, align=PP_ALIGN.RIGHT,
                 anchor=MSO_ANCHOR.MIDDLE)
    # Bottom footer band
    add_rect(slide, 0, SH - Inches(0.25), SW, Inches(0.25), YU_NAVY)
    add_text_box(slide, Inches(0.3), SH - Inches(0.22), Inches(10), Inches(0.2),
                 "山口大学 (Yamaguchi University) — 省エネ研究会 2026",
                 size=8.5, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def add_title(slide, title, subtitle=None):
    add_text_box(slide, Inches(0.4), Inches(0.5), Inches(12.5), Inches(0.6),
                 title, size=26, bold=True, color=YU_NAVY)
    # Underline accent bar
    add_rect(slide, Inches(0.4), Inches(1.12), Inches(1.2), Inches(0.06), YU_ORANGE)
    if subtitle:
        add_text_box(slide, Inches(0.4), Inches(1.2), Inches(12.5), Inches(0.4),
                     subtitle, size=14, color=YU_GREY)


def add_speaker_notes(slide, text):
    notes = slide.notes_slide.notes_text_frame
    notes.text = ""
    for i, ln in enumerate(text.split("\n")):
        p = notes.paragraphs[0] if i == 0 else notes.add_paragraph()
        p.text = ln


# ============================================================================
# SLIDE 1: Title
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
# Full-bleed navy band
add_rect(slide, 0, 0, SW, SH, YU_NAVY)
# Orange accent stripe
add_rect(slide, 0, Inches(2.6), SW, Inches(0.08), YU_ORANGE)

add_text_box(slide, Inches(0.6), Inches(0.7), Inches(12), Inches(0.5),
             "山口大学  YAMAGUCHI UNIVERSITY",
             size=14, bold=True, color=WHITE)

add_text_box(slide, Inches(0.6), Inches(2.9), Inches(12), Inches(1.5),
             "天気予報を活用した\nキャンパスSDR運用支援システムの研究",
             size=36, bold=True, color=WHITE)

add_text_box(slide, Inches(0.6), Inches(4.6), Inches(12), Inches(0.6),
             "— ハイブリッド気象入力による翌日電力ピーク予測 —",
             size=18, color=RGBColor(0xFF, 0xC8, 0x80))

add_text_box(slide, Inches(0.6), Inches(5.8), Inches(12), Inches(0.4),
             "発表者: 〇〇 〇〇 (山口大学 ○○研究室)",
             size=14, color=WHITE)
add_text_box(slide, Inches(0.6), Inches(6.3), Inches(12), Inches(0.4),
             "省エネ研究会 / 2026年5月",
             size=14, color=WHITE)

add_speaker_notes(slide,
"皆さま、本日はお時間をいただきありがとうございます。\n"
"山口大学の○○です。\n"
"本日は『天気予報を活用したキャンパスSDR運用支援システム』について発表いたします。\n"
"SDRとは「Setpoint Demand Response (設定温度デマンドレスポンス)」、\n"
"つまり気温が高い日にエアコンの設定温度を一時的に上げて、ピーク電力を抑える運用です。\n"
"本研究では、翌日の電力ピークを事前に予測して、SDR発令を判断する仕組みを作りました。")


# ============================================================================
# SLIDE 2: 研究背景
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 2)
add_title(slide, "研究背景", "なぜキャンパスのピーク予測が必要か")

# Three pillar boxes
def pillar(x, color, num, head, body):
    add_rect(slide, x, Inches(2.0), Inches(4.0), Inches(0.6), color)
    add_text_box(slide, x + Inches(0.2), Inches(2.07), Inches(3.6), Inches(0.5),
                 f"{num}.  {head}", size=15, bold=True, color=WHITE,
                 anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, x, Inches(2.6), Inches(4.0), Inches(3.4), LIGHT_BG, line_color=color)
    add_text_box(slide, x + Inches(0.25), Inches(2.75), Inches(3.55), Inches(3.2),
                 body, size=13, color=YU_GREY)

pillar(Inches(0.4),  YU_NAVY, "①", "猛暑による電力ピーク",
       "・山口県は2025年も猛暑\n"
       "・キャンパス電力の40%は空調\n"
       "・ピーク時の契約電力上昇は\n  経費負担に直結")
pillar(Inches(4.65), YU_ORANGE, "②", "SDRの有効性",
       "・空調設定温度を1〜2℃上げる\n  だけで5〜10%節電可能\n"
       "・しかし「いつ発令するか」が\n  運用上の大きな課題")
pillar(Inches(8.9),  YU_GREEN, "③", "予測による事前判断",
       "・前日の気象予報から翌日の\n  電力ピークを予測\n"
       "・リスクの高い日のみSDR発令\n"
       "・快適性と省エネを両立")

add_speaker_notes(slide,
"研究の背景を3点でご説明します。\n"
"まず①、夏の猛暑により電力ピークが増加しています。\n"
"キャンパス電力の約4割が空調です。\n"
"次に②、SDRは設定温度を少し上げるだけで5〜10%の節電効果があり、有効な手段です。\n"
"しかし「どの日に発令すべきか」が運用上の課題となっています。\n"
"そこで③、翌日のピークを事前に予測してSDR発令を判断する仕組みが必要です。\n"
"これが本研究のモチベーションです。")


# ============================================================================
# SLIDE 3: 研究目的とアプローチ
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 3)
add_title(slide, "研究目的とアプローチ", "翌日ピーク予測 → SDR運用判断")

# Left: goal
add_rect(slide, Inches(0.4), Inches(2.0), Inches(6.0), Inches(0.5), YU_NAVY)
add_text_box(slide, Inches(0.6), Inches(2.07), Inches(5.6), Inches(0.4),
             "研究目的", size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
add_rect(slide, Inches(0.4), Inches(2.5), Inches(6.0), Inches(3.3), LIGHT_BG, line_color=YU_NAVY)
add_text_box(slide, Inches(0.6), Inches(2.7), Inches(5.6), Inches(3.0),
             "目標:\n"
             "  当日 17時時点で、翌日0時〜23時の\n"
             "  各時間電力 b00 (kW) を予測する\n\n"
             "条件:\n"
             "  ・気象予報 (JMA MSM) を入力に活用\n"
             "  ・部署可能 (未来情報を使わない)\n"
             "  ・予測精度 MAE ≦ 60 kW\n\n"
             "出力:\n"
             "  時間予測値 → ピーク日のSDR発令推奨",
             size=13, color=YU_GREY)

# Right: approach
add_rect(slide, Inches(6.85), Inches(2.0), Inches(6.1), Inches(0.5), YU_ORANGE)
add_text_box(slide, Inches(7.05), Inches(2.07), Inches(5.7), Inches(0.4),
             "アプローチ: ハイブリッド気象入力", size=14, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
add_rect(slide, Inches(6.85), Inches(2.5), Inches(6.1), Inches(3.3), LIGHT_BG, line_color=YU_ORANGE)
add_text_box(slide, Inches(7.05), Inches(2.7), Inches(5.7), Inches(3.0),
             "発想:\n"
             "  「過去の気象は観測 (AMeDAS)、\n"
             "    未来の気象は予報 (JMA MSM) を使う」\n\n"
             "理由:\n"
             "  ・過去 → すでに観測済み、誤差ゼロ\n"
             "  ・未来 → 観測は存在しない、予報が唯一\n\n"
             "結果:\n"
             "  訓練データの精度を保ちつつ、\n"
             "  実運用での再現性も担保",
             size=13, color=YU_GREY)

add_speaker_notes(slide,
"研究の目的とアプローチです。\n"
"目的は、当日17時の時点で、翌日各時間の電力負荷を予測することです。\n"
"気象予報を活用し、未来情報を使わない部署可能な仕組みを目指します。\n"
"アプローチの工夫として、ハイブリッド気象入力を提案します。\n"
"過去の気象は観測値、未来の気象は予報値を使い分けます。\n"
"こうすることで訓練データの質を保ちつつ、実運用での精度も担保します。\n"
"これが本研究のポイントです。")


# ============================================================================
# SLIDE 4: データと前処理
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 4)
add_title(slide, "データと前処理",
          f"有効データ範囲: {S['data_range']}  ({S['n_hours_valid']:,} 時間)")

# Left: text
add_text_box(slide, Inches(0.4), Inches(2.0), Inches(5.5), Inches(0.4),
             "■ 使用したデータ", size=15, bold=True, color=YU_NAVY)
add_text_box(slide, Inches(0.4), Inches(2.5), Inches(5.5), Inches(3.5),
             "1. キャンパス電力 (1時間値)\n"
             "    建物 b00 〜 b15, 計15棟\n"
             "    本研究は b00 (主棟) を対象\n\n"
             "2. 気象観測 (ERA5 / AMeDAS同等)\n"
             "    気温・湿度・日射量・WBGT等\n\n"
             "3. 気象予報 (JMA MSM, 5km)\n"
             "    最大39時間先まで利用可能\n\n"
             "4. カレンダー (営業日, 休日, 曜日)",
             size=12.5, color=YU_GREY)

# Right: text about cleaning
add_text_box(slide, Inches(6.5), Inches(2.0), Inches(6.5), Inches(0.4),
             "■ データクリーニング", size=15, bold=True, color=YU_NAVY)
add_text_box(slide, Inches(6.5), Inches(2.5), Inches(6.5), Inches(3.5),
             "・センサー停止期間を除外:\n"
             "    2025-09-24 (14時間ゼロ)\n"
             "    2025-10-27 〜 10-31 (5日間ゼロ)\n\n"
             "・有効サンプル数:\n"
             f"    学習: {S['n_train']:,} 時間 ({S['train_range']})\n"
             f"    テスト: {S['n_test']:,} 時間 ({S['test_range']})\n\n"
             "・分割比: 時系列 70 : 30\n"
             "    未来データを学習に使わない\n"
             "    (リーク防止)",
             size=12.5, color=YU_GREY)

add_speaker_notes(slide,
"使用したデータをご説明します。\n"
"電力データは山口大学キャンパスの建物別1時間電力で、本研究は主棟 b00 を予測対象としました。\n"
"気象データは観測値と予報値の両方を使用します。\n"
"データ期間は2025年7月から10月の約4ヶ月間です。\n"
"センサー停止により無効となった期間を除外しています。\n"
"そして、時系列で70%を学習、30%をテストに割り当てました。\n"
"これにより、未来データを学習に使わない、リークを防ぐ評価ができます。")


# ============================================================================
# SLIDE 5: 学習/テスト分割の可視化
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 5)
add_title(slide, "学習データとテストデータ",
          f"学習 {S['n_train']:,} h ({S['train_range']})  →  テスト {S['n_test']:,} h ({S['test_range']})")

slide.shapes.add_picture(f"{FIG}/pres_07_train_test_split.png",
                          Inches(0.4), Inches(2.0), width=Inches(12.5))

add_text_box(slide, Inches(0.4), Inches(5.6), Inches(12.5), Inches(0.5),
             "■ ポイント: テスト期間 (オレンジ) のデータは学習に一切使用していない",
             size=14, bold=True, color=YU_ORANGE)
add_text_box(slide, Inches(0.4), Inches(6.1), Inches(12.5), Inches(0.8),
             "・夏 (7〜9月) のピーク日で学習し、晩夏〜秋初 (9月後半〜10月) で性能評価。\n"
             "・テスト期間にも複数のピーク日が含まれ、SDR発令判断の検証に適切。",
             size=12, color=YU_GREY)

add_speaker_notes(slide,
"こちらが学習データとテストデータの分割です。\n"
"青色が学習データ、約2ヶ月分です。オレンジが評価用のテストデータ、約5週間分です。\n"
"重要なのは、テスト期間のデータは学習に一切使用していない点です。\n"
"これにより、本当の意味で未知の期間に対する予測性能を測れます。\n"
"テスト期間にもピーク日が複数含まれており、SDR発令判断の検証に適しています。")


# ============================================================================
# SLIDE 6: 日内負荷パターン (探索的分析)
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 6)
add_title(slide, "日内負荷パターンの月別比較",
          "7月のピークが最も高く、午後14〜15時にピーク")

slide.shapes.add_picture(f"{FIG}/pres_01_overview_daily_profile.png",
                          Inches(0.4), Inches(2.0), width=Inches(12.5))

add_text_box(slide, Inches(0.4), Inches(6.5), Inches(12.5), Inches(0.7),
             "・7月 (赤): 14時頃に1,360 kW のピーク      ・10月 (紺): ピークが下がり1,040 kW\n"
             "・全月共通: 5〜6時に最低 → 14〜15時にピーク → 夜間に減少",
             size=12, color=YU_GREY)

add_speaker_notes(slide,
"まず探索的にデータの傾向を見ていきます。\n"
"これは月別の1日の負荷パターンです。\n"
"赤い線が7月、青い線が10月です。\n"
"7月の真夏は午後2時頃に最大1,360 kWのピークを迎えますが、10月になると1,040 kW程度まで下がります。\n"
"これは冷房使用量の差によるものです。\n"
"どの月も朝5〜6時に最低、午後14〜15時に最高、夜にかけて減少という共通パターンを示します。")


# ============================================================================
# SLIDE 7: 気象 × 電力 相関分析 (NEW)
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 7)
add_title(slide, "気象 × 電力の相関分析",
          "どの気象要素が電力消費に最も影響するか")

# Left: correlation heatmap
slide.shapes.add_picture(f"{FIG}/corr_01_pearson_heatmap.png",
                          Inches(0.4), Inches(1.9), width=Inches(7.0))

# Right: key findings + standardized β
add_text_box(slide, Inches(7.6), Inches(1.95), Inches(5.4), Inches(0.4),
             "■ 主な所見", size=15, bold=True, color=YU_NAVY)
add_text_box(slide, Inches(7.6), Inches(2.4), Inches(5.4), Inches(2.0),
             "1. 最強の正相関: 日射量\n"
             "    Pearson r = +0.67 (時間別)\n\n"
             "2. 強い正相関: 気温\n"
             "    Pearson r = +0.57\n\n"
             "3. 強い負相関: 湿度\n"
             "    Pearson r = −0.52",
             size=12.5, color=YU_GREY)

# Bottom right: small β plot
slide.shapes.add_picture(f"{FIG}/corr_07_standardized_beta.png",
                          Inches(7.6), Inches(4.5), width=Inches(5.5))

add_text_box(slide, Inches(0.4), Inches(6.7), Inches(7.0), Inches(0.4),
             "■ 線形重回帰でも気象だけで b00 分散の 53% を説明",
             size=12, bold=True, color=YU_ORANGE)

add_speaker_notes(slide,
"まず気象と電力の関係性を見ていきます。\n"
"左の図は、各気象変数と電力消費 b00 の相関係数です。\n"
"最も強い正相関は「日射量」、r = +0.67 です。\n"
"次が「気温」、r = +0.57。\n"
"そして「湿度」は負相関、r = −0.52 です。\n"
"右下の標準化回帰係数では、日射量と気温が主な「電力を上げる」要因、\n"
"湿度と気圧が「電力を下げる」要因として現れています。\n"
"気象変数だけで電力分散の約 53% を説明できることが分かりました。")


# ============================================================================
# SLIDE 8: 主成分分析 (PCA)  (NEW)
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 8)
add_title(slide, "主成分分析 (PCA)",
          "気象10変数の本質を 3 つの主成分に圧縮")

# Left: variance explained
slide.shapes.add_picture(f"{FIG}/corr_05_pca_variance.png",
                          Inches(0.4), Inches(1.9), width=Inches(6.4))

# Right: loadings heatmap (full)
slide.shapes.add_picture(f"{FIG}/corr_06_pca_loadings.png",
                          Inches(6.95), Inches(1.9), width=Inches(6.2))

# Bottom: interpretation
add_text_box(slide, Inches(0.4), Inches(6.2), Inches(12.5), Inches(0.4),
             "■ 解釈: 3つの主成分で気象変動の 76% を説明", size=14,
             bold=True, color=YU_NAVY)
add_text_box(slide, Inches(0.4), Inches(6.65), Inches(12.5), Inches(0.8),
             "・PC1 (41.7%) = 「熱関連成分」気温・体感・WBGT が共に寄与   →  b00 と +0.47 の相関\n"
             "・PC2 (21.1%) = 「湿度・日射成分」湿度↑かつ日射↓ (悪天候)   →  b00 と −0.50 の相関\n"
             "・PC3 (13.1%) = 「風・降水成分」 (b00 への影響は小)",
             size=11.5, color=YU_GREY)

add_speaker_notes(slide,
"次に主成分分析、PCAの結果です。\n"
"気象データは 10個の変数からなりますが、互いに相関するため、独立な成分に分解しました。\n"
"左のグラフは各主成分の寄与率です。\n"
"PC1 が 41.7%、PC2 が 21.1%、PC3 が 13.1%。\n"
"つまり、3つの主成分だけで、気象変動の 76% を表現できます。\n\n"
"右のヒートマップは、各主成分の構成を示しています。\n"
"PC1 は「熱関連成分」、気温・体感気温・WBGT が共に寄与します。\n"
"PC2 は「湿度と日射の対立成分」、悪天候の日に対応します。\n"
"右側のバーは、各主成分と b00 の相関を示しており、\n"
"PC1 は +0.47、PC2 は −0.50、PC3 は +0.16 となっています。\n"
"つまり、気温と湿天候という 2つの軸が電力を主に左右していることが分かります。")


# ============================================================================
# SLIDE 9: 結果① 時系列予測
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 9)
hC_mae = S["results"]["C_Hybrid"]["MAE"]
hC_r2  = S["results"]["C_Hybrid"]["R2"]
hC_mape= S["results"]["C_Hybrid"]["MAPE"]
add_title(slide, "結果① テスト期間の予測",
          f"提案手法 (Hybrid):  MAE = {hC_mae} kW,  R² = {hC_r2},  MAPE = {hC_mape}%")

slide.shapes.add_picture(f"{FIG}/pres_04_holdout_timeseries.png",
                          Inches(0.4), Inches(1.9), width=Inches(12.5))

add_text_box(slide, Inches(0.4), Inches(6.3), Inches(12.5), Inches(0.4),
             "■ 青: 実測値    オレンジ: 予測値    赤点線: P80閾値 (SDR発令検討基準)",
             size=13, bold=True, color=YU_NAVY)
add_text_box(slide, Inches(0.4), Inches(6.8), Inches(12.5), Inches(0.5),
             "・予測線は実測線を概ね追従。複数のピーク日 (10/07, 10/14, 10/22) を正しく捕捉。",
             size=12, color=YU_GREY)

add_speaker_notes(slide,
"ここからは結果のご紹介です。\n"
"こちらがテスト期間の予測結果です。\n"
"青い線が実測値、オレンジの線が予測値です。\n"
"赤い点線はP80閾値、つまりSDR発令を検討するべき水準です。\n"
"全体として、予測値は実測値をよく追従しており、複数のピーク日も正しく捕捉できています。\n"
f"平均誤差 (MAE) は約 {hC_mae} kW、決定係数 R² は {hC_r2} と良好な精度を達成しました。")


# ============================================================================
# SLIDE 10: 結果② 散布図
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 10)
add_title(slide, "結果② 予測 vs 実測の対応",
          f"散布図で見る予測精度  —  MAE {hC_mae} kW, MAPE {hC_mape}%")

slide.shapes.add_picture(f"{FIG}/pres_05_pred_vs_actual.png",
                          Inches(0.4), Inches(2.0), width=Inches(6.5))

# Right side: result table + interpretation
add_text_box(slide, Inches(7.5), Inches(2.0), Inches(5.5), Inches(0.4),
             "■ 3アーキテクチャの精度比較", size=15, bold=True, color=YU_NAVY)

# Table
def add_table_cell(x, y, w, h, text, bold=False, color=YU_GREY, bg=None, size=12):
    if bg is not None: add_rect(slide, x, y, w, h, bg)
    add_text_box(slide, x + Inches(0.05), y + Inches(0.04), w - Inches(0.1), h - Inches(0.08),
                 text, size=size, bold=bold, color=color, anchor=MSO_ANCHOR.MIDDLE)

table_x = Inches(7.5); table_y = Inches(2.5)
col_w = [Inches(2.2), Inches(1.1), Inches(1.0), Inches(1.0)]
row_h = Inches(0.45)
headers = ["手法", "MAE(kW)", "R²", "MAPE(%)"]
x = table_x
for i, hd in enumerate(headers):
    add_table_cell(x, table_y, col_w[i], row_h, hd, bold=True, color=WHITE, bg=YU_NAVY)
    x += col_w[i]
rows = [
    ("A: 観測のみ (上限)", S["results"]["A_Obs"]["MAE"], S["results"]["A_Obs"]["R2"], S["results"]["A_Obs"]["MAPE"], LIGHT_BG, YU_GREY),
    ("B: 予報のみ", S["results"]["B_Forecast"]["MAE"], S["results"]["B_Forecast"]["R2"], S["results"]["B_Forecast"]["MAPE"], WHITE, YU_GREY),
    ("C: Hybrid (本研究)", S["results"]["C_Hybrid"]["MAE"], S["results"]["C_Hybrid"]["R2"], S["results"]["C_Hybrid"]["MAPE"], RGBColor(0xFD, 0xE9, 0xCE), YU_RED),
]
for r_idx, (name, mae, r2, mape, bg, fg) in enumerate(rows):
    y = table_y + Inches(0.45 * (r_idx + 1))
    x = table_x
    bold = "本研究" in name
    add_table_cell(x, y, col_w[0], row_h, name, bold=bold, color=fg, bg=bg)
    x += col_w[0]
    add_table_cell(x, y, col_w[1], row_h, f"{mae}", bold=bold, color=fg, bg=bg)
    x += col_w[1]
    add_table_cell(x, y, col_w[2], row_h, f"{r2}", bold=bold, color=fg, bg=bg)
    x += col_w[2]
    add_table_cell(x, y, col_w[3], row_h, f"{mape}", bold=bold, color=fg, bg=bg)

# Interpretation box
add_text_box(slide, Inches(7.5), Inches(4.6), Inches(5.5), Inches(0.4),
             "■ ポイント", size=15, bold=True, color=YU_NAVY)
add_text_box(slide, Inches(7.5), Inches(5.0), Inches(5.5), Inches(1.8),
             f"・C (Hybrid) は B より MAE 10%改善\n"
             f"  ({S['results']['B_Forecast']['MAE']} → {hC_mae} kW)\n\n"
             f"・A (上限) との差はわずか 6%\n"
             f"  ({S['results']['A_Obs']['MAE']} → {hC_mae} kW)\n\n"
             "・上限値に迫る精度を実運用で実現",
             size=12.5, color=YU_GREY)

add_speaker_notes(slide,
"次に散布図とアーキテクチャ比較です。\n"
"左の散布図では、点が対角線 y=x に沿って分布しており、予測値と実測値がよく一致していることが分かります。\n"
"右の表は、3つの手法を比較したものです。\n"
"A は観測値のみを使う理論上限、B は予報値のみを使う従来手法、そして C が本研究のハイブリッド手法です。\n"
f"Cは B より MAE が 10% 改善し、A との差はわずか 6% です。\n"
"つまり、観測値を使った理論上限に近い精度を、実運用で実現できたということです。")


# ============================================================================
# SLIDE 11: 結果③ 特徴量重要度 (SHAP)
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 11)
add_title(slide, "結果③ 何が予測を決めているか",
          "SHAP値で見る上位特徴量")

slide.shapes.add_picture(f"{FIG}/pres_06_shap_top10.png",
                          Inches(0.4), Inches(2.0), width=Inches(8.0))

# Right: interpretation
add_text_box(slide, Inches(8.6), Inches(2.0), Inches(4.5), Inches(0.4),
             "■ 解釈", size=15, bold=True, color=YU_NAVY)
add_text_box(slide, Inches(8.6), Inches(2.5), Inches(4.5), Inches(4.5),
             "1. 前週同時刻の負荷が最重要\n"
             "    → 週周期パターンが強い\n\n"
             "2. 営業日 / 休日フラグ\n"
             "    → 平日と休日で大差\n\n"
             "3. 前日同時刻の気温\n"
             "    → 暑熱の連続性を反映\n\n"
             "4. 日射量 (予報)\n"
             "    → 翌日の冷房需要を予測",
             size=12.5, color=YU_GREY)

add_speaker_notes(slide,
"こちらが予測の根拠となる特徴量です。SHAP値で重要度を可視化しました。\n"
"最も重要なのが「前週同時刻の負荷」です。週周期パターンが強いことを示しています。\n"
"次いで「営業日フラグ」、平日と休日で電力消費が大きく異なります。\n"
"3位は「前日同時刻の気温」、暑熱の連続性を反映しています。\n"
"4位は「日射量予報」、翌日の冷房需要を予測する重要な情報源です。\n"
"このように、モデルは現実的な物理的・運用的要因を捉えていることが分かります。")


# ============================================================================
# SLIDE 12: まとめと今後の課題
# ============================================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_header_footer(slide, 12)
add_title(slide, "まとめと今後の課題", "達成内容と次のステップ")

# Left box: achievements
add_rect(slide, Inches(0.4), Inches(2.0), Inches(6.2), Inches(0.5), YU_NAVY)
add_text_box(slide, Inches(0.55), Inches(2.07), Inches(6.0), Inches(0.4),
             "■ 達成内容", size=15, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
add_rect(slide, Inches(0.4), Inches(2.5), Inches(6.2), Inches(3.5), LIGHT_BG, line_color=YU_NAVY)
add_text_box(slide, Inches(0.55), Inches(2.65), Inches(5.9), Inches(3.3),
             "1. JMA予報を活用した翌日電力予測\n"
             "    システムを構築 \n\n"
             "2. ハイブリッド気象入力 (新手法)\n"
             "    過去=観測 + 未来=予報\n\n"
             "3. 達成精度:\n"
             f"    MAE {hC_mae} kW (誤差 ~7%)\n"
             f"    R² {hC_r2}\n\n"
             "4. 上限値の94%の精度を実運用で実現",
             size=12.5, color=YU_GREY)

# Right box: future work
add_rect(slide, Inches(6.85), Inches(2.0), Inches(6.1), Inches(0.5), YU_ORANGE)
add_text_box(slide, Inches(7.0), Inches(2.07), Inches(5.9), Inches(0.4),
             "■ 今後の課題", size=15, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
add_rect(slide, Inches(6.85), Inches(2.5), Inches(6.1), Inches(3.5), LIGHT_BG, line_color=YU_ORANGE)
add_text_box(slide, Inches(7.0), Inches(2.65), Inches(5.8), Inches(3.3),
             "1. 通年データへの拡張\n"
             "    冬季の暖房需要も検証\n\n"
             "2. 全15棟へのスケールアップ\n"
             "    棟ごとの特性を学習\n\n"
             "3. 実機運用の試験導入\n"
             "    現場担当者との連携\n\n"
             "4. SDR発令ルールの最適化\n"
             "    閾値・連続時間の校正",
             size=12.5, color=YU_GREY)

# Final thank-you bar
add_rect(slide, Inches(0.4), Inches(6.2), Inches(12.55), Inches(0.65), YU_NAVY)
add_text_box(slide, Inches(0.4), Inches(6.25), Inches(12.55), Inches(0.55),
             "ご清聴ありがとうございました。  ご質問をお待ちしております。",
             size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

add_speaker_notes(slide,
"最後にまとめです。\n"
"本研究の達成内容は4点です。\n"
"1つ目、JMA気象予報を活用した翌日電力予測システムを構築しました。\n"
"2つ目、ハイブリッド気象入力という新しい手法を提案しました。\n"
"3つ目、平均誤差 54 kW、誤差率 約7%、決定係数 0.905 という良好な精度を達成しました。\n"
"4つ目、理論上限の約94%の精度を実運用で実現できました。\n\n"
"今後の課題は、通年データへの拡張、全15棟へのスケールアップ、実機での試験運用、\n"
"そしてSDR発令ルールの最適化です。\n\n"
"以上で発表を終わります。ご清聴ありがとうございました。\n"
"ご質問をお願いいたします。")


# ============================================================================
# Save
# ============================================================================
out_pptx = f"{OUT}/SDR_research_progress_jp.pptx"
prs.save(out_pptx)
print(f"\n✅ PPT saved → {out_pptx}")
print(f"   Slides: {len(prs.slides)}")
print(f"   Size  : {os.path.getsize(out_pptx) / 1024:.1f} KB")
