"""
HIRAKU-Global Round 7 Interview Presentation — v2 (Architectural redesign)
LIU Haiqiang  ·  Yamaguchi University
Style: Architectural drafting + Academic + Yamaguchi U brand
Format: 16:9 widescreen (13.333 x 7.5 in)
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
import os
from PIL import Image

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")

# ============== DESIGN SYSTEM ==============
# Yamaguchi University inspired deep indigo + academic palette
YU_INDIGO    = RGBColor(0x14, 0x2E, 0x55)
YU_INDIGO_LT = RGBColor(0x2A, 0x4D, 0x82)
YU_INDIGO_DK = RGBColor(0x0A, 0x1E, 0x3D)
ACCENT       = RGBColor(0xC9, 0xA9, 0x61)      # warm gold
ACCENT_DEEP  = RGBColor(0x8C, 0x6F, 0x33)
ACCENT_LT    = RGBColor(0xE4, 0xD2, 0x9D)
ARCH_LINE    = RGBColor(0xB8, 0xC2, 0xCC)
GRID         = RGBColor(0xEC, 0xEF, 0xF3)
DARK         = RGBColor(0x1A, 0x1A, 0x1A)
BODY         = RGBColor(0x4A, 0x55, 0x68)
MUTED        = RGBColor(0x88, 0x95, 0xA8)
LIGHT_BG     = RGBColor(0xF6, 0xF8, 0xFA)
LIGHTER      = RGBColor(0xFA, 0xFB, 0xFC)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
HEAT_HOT     = RGBColor(0xD9, 0x53, 0x4F)
HEAT_WARM    = RGBColor(0xE8, 0x9F, 0x5C)
HEAT_MILD    = RGBColor(0xE6, 0xCB, 0x7B)
HEAT_COOL    = RGBColor(0x6F, 0xA8, 0xC6)
GREEN_PARK   = RGBColor(0x6A, 0x8E, 0x5E)

FONT = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height
blank = prs.slide_layouts[6]
TOTAL = 11


# ============== HELPERS ==============
def add_rect(slide, x, y, w, h, fill=None, line=None, line_w=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_w is not None:
            shp.line.width = line_w
    return shp


def add_oval(slide, x, y, w, h, fill=None, line=None, line_w=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_w is not None:
            shp.line.width = line_w
    return shp


def add_tri(slide, x, y, w, h, fill=None, line=None, line_w=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, x, y, w, h)
    shp.shadow.inherit = False
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_w is not None:
            shp.line.width = line_w
    return shp


def add_line(slide, x1, y1, x2, y2, color=YU_INDIGO, weight=1.0, dash=None):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(weight)
    if dash:
        sppr = line.line._get_or_add_ln()
        prst = sppr.makeelement(qn('a:prstDash'), {'val': dash})
        sppr.append(prst)
    return line


def add_text(slide, x, y, w, h, text, size=14, bold=False, color=DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
             line_spacing=1.15, font=FONT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for m in ['margin_left', 'margin_right', 'margin_top', 'margin_bottom']:
        setattr(tf, m, 0)
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return tb


def corner_marks(slide):
    m = Inches(0.10)
    for cx, cy in [
        (Inches(0.30), Inches(0.45)),
        (SLIDE_W - Inches(0.30), Inches(0.45)),
        (Inches(0.30), SLIDE_H - Inches(0.30)),
        (SLIDE_W - Inches(0.30), SLIDE_H - Inches(0.30)),
    ]:
        add_line(slide, cx - m, cy, cx + m, cy, color=ARCH_LINE, weight=0.5)
        add_line(slide, cx, cy - m, cx, cy + m, color=ARCH_LINE, weight=0.5)


def page_chrome(slide, num, section, title_text=None, dark=False):
    """Architectural-style page chrome with title block"""
    bg = YU_INDIGO_DK if dark else WHITE
    text_main = WHITE if dark else YU_INDIGO
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill=bg)

    # Top brand bar
    add_rect(slide, 0, 0, SLIDE_W, Inches(0.18), fill=YU_INDIGO_DK if not dark else YU_INDIGO)
    add_rect(slide, 0, Inches(0.18), Inches(2.0), Emu(38100), fill=ACCENT)

    add_text(slide, Inches(0.45), Inches(0.02), Inches(8), Inches(0.16),
             "YAMAGUCHI UNIVERSITY  ·  HIRAKU-GLOBAL  ·  7TH COHORT INTERVIEW",
             size=8, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(10.5), Inches(0.02), Inches(2.7), Inches(0.16),
             f"SHEET  {num:02d}  /  {TOTAL:02d}",
             size=8, bold=True, color=ACCENT,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    if section:
        add_text(slide, Inches(0.45), Inches(0.40), Inches(8), Inches(0.30),
                 section, size=10, bold=True, color=ACCENT_DEEP)

    if title_text:
        add_text(slide, Inches(0.45), Inches(0.70), Inches(12.5), Inches(0.95),
                 title_text, size=28, bold=True, color=text_main,
                 line_spacing=1.05)

    # Bottom title block (architectural drawing style)
    bx, by, bw, bh = Inches(9.45), Inches(7.10), Inches(3.45), Inches(0.30)
    add_rect(slide, bx, by, bw, bh, fill=None, line=ARCH_LINE, line_w=Pt(0.6))
    add_line(slide, bx + Inches(1.0), by, bx + Inches(1.0), by + bh,
             color=ARCH_LINE, weight=0.6)
    add_line(slide, bx + Inches(2.25), by, bx + Inches(2.25), by + bh,
             color=ARCH_LINE, weight=0.6)
    c_minor = WHITE if dark else MUTED
    add_text(slide, bx, by, Inches(1.0), bh, f"  {num:02d}/{TOTAL:02d}",
             size=8, color=c_minor, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, bx + Inches(1.05), by, Inches(1.2), bh, "  LIU HAIQIANG",
             size=8, color=c_minor, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, bx + Inches(2.3), by, Inches(1.1), bh, "  2026.06",
             size=8, color=c_minor, anchor=MSO_ANCHOR.MIDDLE)

    add_text(slide, Inches(0.45), Inches(7.18), Inches(8), Inches(0.2),
             "INTERVIEW PRESENTATION  ·  URBAN THERMAL ENVIRONMENT RESEARCH",
             size=8, color=c_minor)

    # Left axis line
    if not dark:
        add_line(slide, Inches(0.45), Inches(0.85), Inches(0.45),
                 Inches(7.00), color=ARCH_LINE, weight=0.5)

    corner_marks(slide)


def add_notes(slide, text):
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.text = text


# Custom shape icons (architectural plan/elevation style)
def icon_building(slide, x, y, size, color=YU_INDIGO):
    """Small building icon - elevation view"""
    s = size
    add_rect(slide, x, y + s * 0.2, s, s * 0.8, fill=None,
             line=color, line_w=Pt(1.2))
    add_tri(slide, x, y, s, s * 0.25, fill=None, line=color, line_w=Pt(1.2))
    # Windows
    win_w = s * 0.18
    win_h = s * 0.15
    for r in range(2):
        for c in range(3):
            wx = x + s * 0.12 + c * (win_w + s * 0.07)
            wy = y + s * 0.35 + r * (win_h + s * 0.08)
            add_rect(slide, wx, wy, win_w, win_h, fill=color)


def icon_person(slide, x, y, size, color=YU_INDIGO):
    """Person icon - simplified"""
    s = size
    head = s * 0.28
    add_oval(slide, x + (s - head) / 2, y, head, head, fill=color)
    # Body trapezoid (use triangle approximation)
    body_w = s * 0.6
    add_rect(slide, x + (s - body_w) / 2, y + head + s * 0.05,
             body_w, s * 0.5, fill=color)
    # Legs
    leg_w = s * 0.12
    add_rect(slide, x + (s - body_w) / 2 + body_w * 0.18,
             y + head + s * 0.55, leg_w, s * 0.18, fill=color)
    add_rect(slide, x + (s - body_w) / 2 + body_w * 0.62,
             y + head + s * 0.55, leg_w, s * 0.18, fill=color)


def icon_city(slide, x, y, size, color=YU_INDIGO):
    """City skyline icon"""
    s = size
    heights = [0.55, 0.85, 0.40, 0.70, 0.50, 0.95, 0.60]
    n = len(heights)
    bw = s * 0.95 / n
    for i, h in enumerate(heights):
        bh = s * h
        bx = x + s * 0.025 + i * bw
        by = y + s - bh
        add_rect(slide, bx, by, bw * 0.85, bh, fill=color)


def icon_satellite(slide, x, y, size, color=YU_INDIGO):
    """Satellite icon"""
    s = size
    # Body
    body_w = s * 0.4
    body_h = s * 0.45
    add_rect(slide, x + (s - body_w) / 2, y + (s - body_h) / 2,
             body_w, body_h, fill=color)
    # Solar panels (left + right rectangles)
    panel_w = s * 0.25
    panel_h = s * 0.3
    add_rect(slide, x, y + (s - panel_h) / 2, panel_w, panel_h,
             fill=None, line=color, line_w=Pt(1.0))
    add_rect(slide, x + s - panel_w, y + (s - panel_h) / 2,
             panel_w, panel_h, fill=None, line=color, line_w=Pt(1.0))
    # Panel ribs
    for px in [x + panel_w * 0.5, x + panel_w * 0.0]:
        pass
    # Antenna
    add_line(slide, x + s / 2, y + (s - body_h) / 2,
             x + s / 2, y, color=color, weight=1.2)
    add_oval(slide, x + s / 2 - s * 0.04, y - s * 0.05,
             s * 0.08, s * 0.08, fill=color)


def icon_tree(slide, x, y, size, color=GREEN_PARK):
    """Tree icon"""
    s = size
    add_tri(slide, x, y, s, s * 0.7, fill=color)
    add_rect(slide, x + s * 0.4, y + s * 0.7, s * 0.2, s * 0.3, fill=color)


def icon_sun(slide, x, y, size, color=HEAT_HOT):
    """Sun icon with rays"""
    s = size
    cx = x + s / 2
    cy = y + s / 2
    r = s * 0.25
    add_oval(slide, cx - r, cy - r, r * 2, r * 2, fill=color)
    # Rays
    import math
    for i in range(8):
        ang = i * math.pi / 4
        rx1 = cx + math.cos(ang) * r * 1.3
        ry1 = cy + math.sin(ang) * r * 1.3
        rx2 = cx + math.cos(ang) * r * 1.9
        ry2 = cy + math.sin(ang) * r * 1.9
        add_line(slide, rx1, ry1, rx2, ry2, color=color, weight=1.5)


def number_chip(slide, x, y, size, num, fill=YU_INDIGO, text_color=ACCENT):
    """Small numbered chip for callouts"""
    add_rect(slide, x, y, size, size, fill=fill)
    add_text(slide, x, y, size, size, f"{num:02d}", size=11,
             bold=True, color=text_color, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)


def section_label(slide, x, y, w, text):
    """Architectural section label with leading line"""
    add_line(slide, x, y + Inches(0.18), x + Inches(0.2),
             y + Inches(0.18), color=ACCENT, weight=1.5)
    add_text(slide, x + Inches(0.25), y, w - Inches(0.25), Inches(0.35),
             text, size=10, bold=True, color=ACCENT_DEEP)


# ============================================================
# SLIDE 01 — TITLE
# ============================================================
def slide_01():
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, fill=YU_INDIGO_DK)

    # Subtle grid lines in background (architectural)
    for i in range(1, 8):
        y = Inches(0.75 * i)
        add_line(s, Inches(0.45), y, SLIDE_W - Inches(0.45), y,
                 color=RGBColor(0x1C, 0x35, 0x60), weight=0.4)
    for i in range(1, 13):
        x = Inches(1.0 * i)
        add_line(s, x, Inches(0.45), x, SLIDE_H - Inches(0.45),
                 color=RGBColor(0x1C, 0x35, 0x60), weight=0.4)

    # Top accent
    add_rect(s, 0, 0, Inches(3.0), Inches(0.10), fill=ACCENT)
    add_text(s, Inches(0.75), Inches(0.30), Inches(8), Inches(0.3),
             "YAMAGUCHI UNIVERSITY  ·  HIRAKU-GLOBAL  ·  7TH COHORT  ·  2026",
             size=10, bold=True, color=ACCENT)

    # Main title (large)
    add_text(s, Inches(0.75), Inches(1.55), Inches(11.8), Inches(1.2),
             "Bridging Cities, Climate, and People",
             size=48, bold=True, color=WHITE, line_spacing=1.0)

    # Long thin gold underline
    add_rect(s, Inches(0.75), Inches(2.75), Inches(3.0), Emu(38100),
             fill=ACCENT)

    # Subtitle
    add_text(s, Inches(0.75), Inches(2.95), Inches(12), Inches(0.7),
             "Urban Thermal Environment Research",
             size=22, color=WHITE)
    add_text(s, Inches(0.75), Inches(3.45), Inches(12), Inches(0.55),
             "from Japanese Regional Cities to International Asia",
             size=18, color=RGBColor(0xB8, 0xC8, 0xDC), italic=True)
    # Thesis line (NEW - explicit research identity)
    add_rect(s, Inches(0.75), Inches(4.10), Inches(0.06), Inches(0.32),
             fill=ACCENT)
    add_text(s, Inches(0.92), Inches(4.10), Inches(12), Inches(0.32),
             "HEAT-ADAPTIVE WALKABLE CITIES  ·  CROSS-SCALE ANALYTICAL FRAMEWORK",
             size=12, bold=True, color=ACCENT,
             anchor=MSO_ANCHOR.MIDDLE)

    # Name block (architectural style)
    nx = Inches(0.75)
    ny = Inches(4.65)
    add_rect(s, nx, ny, Inches(0.06), Inches(1.4), fill=ACCENT)
    add_text(s, nx + Inches(0.25), ny, Inches(11), Inches(0.5),
             "LIU  HAIQIANG, Ph.D.",
             size=24, bold=True, color=WHITE)
    add_text(s, nx + Inches(0.25), ny + Inches(0.5), Inches(11), Inches(0.4),
             "Lecturer (Tenure-track)",
             size=14, color=ACCENT)
    add_text(s, nx + Inches(0.25), ny + Inches(0.83), Inches(11), Inches(0.4),
             "Graduate School of Sciences and Technology for Innovation",
             size=12, color=RGBColor(0xB8, 0xC8, 0xDC))
    add_text(s, nx + Inches(0.25), ny + Inches(1.10), Inches(11), Inches(0.4),
             "Yamaguchi University",
             size=12, color=RGBColor(0xB8, 0xC8, 0xDC))

    # Keyword chips (bottom)
    chips = ["URBAN THERMAL ENVIRONMENT", "INTERNATIONAL COLLABORATION",
             "REGIONAL POLICY", "SOCIAL IMPLEMENTATION"]
    x0 = Inches(0.75)
    y_chip = Inches(6.55)
    cw = Inches(2.95)
    for chip in chips:
        add_rect(s, x0, y_chip, cw, Inches(0.40),
                 fill=None, line=ACCENT, line_w=Pt(0.75))
        add_text(s, x0, y_chip, cw, Inches(0.40), chip,
                 size=9, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x0 += cw + Inches(0.13)

    # Bottom-right architectural title block
    bx, by, bw, bh = Inches(9.5), Inches(7.05), Inches(3.4), Inches(0.32)
    add_rect(s, bx, by, bw, bh, fill=None, line=ACCENT, line_w=Pt(0.6))
    add_line(s, bx + Inches(1.0), by, bx + Inches(1.0), by + bh,
             color=ACCENT, weight=0.6)
    add_line(s, bx + Inches(2.25), by, bx + Inches(2.25), by + bh,
             color=ACCENT, weight=0.6)
    add_text(s, bx, by, Inches(1.0), bh, "  01 / 11",
             size=8, color=ACCENT_LT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, bx + Inches(1.05), by, Inches(1.2), bh, "  TITLE",
             size=8, color=ACCENT_LT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, bx + Inches(2.3), by, Inches(1.1), bh, "  2026.06",
             size=8, color=ACCENT_LT, anchor=MSO_ANCHOR.MIDDLE)

    # Speaker notes
    add_notes(s, """[SLIDE 1 — TITLE — ~25s]

Good morning. My name is Liu Haiqiang. I am a tenure-track Lecturer at Yamaguchi University, working on urban thermal environment.

In one sentence — I bridge urban thermal research with international collaboration, regional policy, and social implementation.

In ten minutes, I will show you why my background fits HIRAKU-Global.
""")


# ============================================================
# SLIDE 02 — ABOUT ME (CV)
# ============================================================
def slide_02():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 2, "PROFILE", "Who I am — a researcher trained between Japan and China.")

    # Three pillars of identity
    pillars = [
        ("01", "JAPAN-TRAINED",
         "Ph.D. (Architectural Environmental Engineering)\nSaga University, Japan  ·  2017"),
        ("02", "CHINA-EXPERIENCED",
         "Associate Professor\nZhejiang Sci-Tech University  ·  2018–2023"),
        ("03", "JAPAN-RETURNED",
         "Lecturer (Tenure-track)\nYamaguchi University  ·  since Jan 2026"),
    ]
    px = Inches(0.75)
    py = Inches(1.85)
    pw = Inches(4.05)
    ph = Inches(1.4)
    gap = Inches(0.10)
    for i, (n, h, b) in enumerate(pillars):
        x = px + i * (pw + gap)
        add_rect(s, x, py, pw, ph, fill=LIGHT_BG)
        add_rect(s, x, py, Inches(0.08), ph, fill=ACCENT)
        add_text(s, x + Inches(0.25), py + Inches(0.15), Inches(0.6), Inches(0.3),
                 n, size=10, bold=True, color=ACCENT_DEEP)
        add_text(s, x + Inches(0.95), py + Inches(0.13), Inches(3), Inches(0.35),
                 h, size=14, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.25), py + Inches(0.55), pw - Inches(0.4),
                 Inches(0.85), b, size=11, color=BODY, line_spacing=1.4)

    # Career timeline (horizontal)
    section_label(s, Inches(0.75), Inches(3.50), Inches(8),
                  "CAREER TIMELINE  ·  10 YEARS ACROSS BUILDING → PERSON → CITY")
    tx = Inches(0.75)
    ty = Inches(4.15)
    tw = Inches(11.83)
    line_y = ty + Inches(0.7)
    # Base line
    add_line(s, tx, line_y, tx + tw, line_y, color=YU_INDIGO, weight=1.5)

    events = [
        (0.00, "2009–2011", "Master's\nSaga U.", "BLDG"),
        (0.15, "2014–2017", "Ph.D.\nSaga U.", "BLDG"),
        (0.32, "2017–2018", "Researcher\nSaga U.", "BLDG"),
        (0.46, "2018–2023", "Associate Prof.\nZSTU", "PERSON"),
        (0.66, "2023–2025", "Researcher\nKumamoto City\nPolicy Institute", "CITY"),
        (0.86, "2026—", "Lecturer\nYamaguchi U.", "CITY"),
    ]
    for frac, yr, lbl, stage in events:
        ex = tx + tw * frac
        # Stage color
        col = {"BLDG": YU_INDIGO_LT, "PERSON": ACCENT, "CITY": HEAT_HOT}[stage]
        # Marker (above line)
        add_oval(s, ex - Inches(0.10), line_y - Inches(0.10),
                 Inches(0.20), Inches(0.20), fill=col)
        # Date below marker
        add_text(s, ex - Inches(0.7), line_y - Inches(0.55), Inches(1.4),
                 Inches(0.30), yr, size=9, bold=True, color=YU_INDIGO,
                 align=PP_ALIGN.CENTER)
        # Label below line
        add_text(s, ex - Inches(0.9), line_y + Inches(0.15), Inches(1.8),
                 Inches(0.85), lbl, size=9.5, color=BODY,
                 align=PP_ALIGN.CENTER, line_spacing=1.25)

    # Stage legend (compressed inline)
    leg_y = Inches(5.65)
    legends = [("STAGE 1  ·  BUILDING", YU_INDIGO_LT),
               ("STAGE 2  ·  PERSON", ACCENT),
               ("STAGE 3  ·  CITY", HEAT_HOT)]
    lx = Inches(0.75)
    for txt, col in legends:
        add_oval(s, lx, leg_y + Inches(0.05), Inches(0.16),
                 Inches(0.16), fill=col)
        add_text(s, lx + Inches(0.22), leg_y, Inches(2.5), Inches(0.28),
                 txt, size=9, bold=True, color=BODY,
                 anchor=MSO_ANCHOR.MIDDLE)
        lx += Inches(2.7)

    # Selected Distinctions strip (NEW)
    section_label(s, Inches(0.75), Inches(6.00), Inches(8),
                  "SELECTED DISTINCTIONS  ·  RECOGNITION & SERVICE")
    dist_y = Inches(6.35)
    dist_items = [
        ("2012", "CCTV-featured", "Eco-City Design 1st Prize on China Central TV"),
        ("2011", "Croucher Institute", "Adv. Study Institute (Hong Kong) — early international training"),
        ("2020–", "3 Advisory Roles", "Urban Regen. · Changzhou Sci-Tech Expert · Saga Alumni"),
    ]
    dx0 = Inches(0.75)
    dw = Inches(4.05)
    dgap = Inches(0.10)
    for i, (yr, head, body_t) in enumerate(dist_items):
        x = dx0 + i * (dw + dgap)
        add_rect(s, x, dist_y, dw, Inches(0.55),
                 fill=None, line=ACCENT, line_w=Pt(0.6))
        add_rect(s, x, dist_y, Inches(0.06), Inches(0.55), fill=ACCENT)
        add_text(s, x + Inches(0.18), dist_y + Inches(0.03),
                 Inches(0.7), Inches(0.22),
                 yr, size=9, bold=True, color=ACCENT_DEEP)
        add_text(s, x + Inches(0.78), dist_y + Inches(0.03),
                 dw - Inches(0.9), Inches(0.22),
                 head, size=10, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.18), dist_y + Inches(0.28),
                 dw - Inches(0.3), Inches(0.25),
                 body_t, size=8, color=BODY, italic=True)

    add_notes(s, """[SLIDE 2 — PROFILE — ~45s]

Briefly — who I am.

Three pillars. Japan-trained: Ph.D. from Saga University in 2017. China-experienced: Associate Professor at Zhejiang Sci-Tech University, 2018 to 2023. Japan-returned: Yamaguchi University since January 2026.

The timeline below shows ten years of continuity, moving from building, to person, to city.

What this gives me is rare — I work natively in both Japanese regional cities and Chinese high-density urbanism, through one continuous research agenda on urban heat.
""")


# ============================================================
# SLIDE 03 — WHY MY RESEARCH MATTERS
# ============================================================
def slide_03():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 3, "PROBLEM SETTING",
                "Climate change becomes a local problem — on every street.")

    # Left: street section schematic (architectural)
    sx = Inches(0.75)
    sy = Inches(1.85)
    sw = Inches(6.4)
    sh = Inches(3.30)
    add_rect(s, sx, sy, sw, sh, fill=LIGHTER, line=ARCH_LINE, line_w=Pt(0.5))
    section_label(s, sx + Inches(0.15), sy + Inches(0.10), Inches(5),
                  "STREET SECTION  ·  WHAT AN ELDERLY RESIDENT FACES")

    # Sky
    sky_top = sy + Inches(0.55)
    # Sun
    icon_sun(s, sx + Inches(5.0), sky_top + Inches(0.05), Inches(0.7),
             color=HEAT_HOT)

    # Ground
    ground_y = sy + sh - Inches(0.45)
    add_rect(s, sx + Inches(0.3), ground_y, sw - Inches(0.6),
             Inches(0.10), fill=YU_INDIGO)

    # Buildings (varying heights, hot side)
    base_y = ground_y
    icon_building(s, sx + Inches(0.5), base_y - Inches(1.4),
                  Inches(0.9), color=YU_INDIGO_LT)
    icon_building(s, sx + Inches(1.5), base_y - Inches(1.8),
                  Inches(0.9), color=YU_INDIGO_LT)
    # Hot zone shading
    add_rect(s, sx + Inches(0.4), base_y - Inches(0.05),
             Inches(2.4), Inches(0.05), fill=HEAT_HOT)
    add_text(s, sx + Inches(0.45), ground_y + Inches(0.18),
             Inches(2.5), Inches(0.3),
             "HOT  ·  built-up", size=9, bold=True, color=HEAT_HOT)

    # Person walking
    icon_person(s, sx + Inches(2.85), base_y - Inches(0.85),
                Inches(0.55), color=DARK)

    # Trees (cool zone)
    icon_tree(s, sx + Inches(4.0), base_y - Inches(1.1),
              Inches(0.8), color=GREEN_PARK)
    icon_tree(s, sx + Inches(4.95), base_y - Inches(0.95),
              Inches(0.7), color=GREEN_PARK)
    add_rect(s, sx + Inches(3.9), base_y - Inches(0.05),
             Inches(2.0), Inches(0.05), fill=HEAT_COOL)
    add_text(s, sx + Inches(3.95), ground_y + Inches(0.18),
             Inches(2.5), Inches(0.3),
             "COOL  ·  green & wind", size=9, bold=True, color=HEAT_COOL)

    # 500-1000m corridor annotation
    add_line(s, sx + Inches(0.4), sy + sh - Inches(0.05),
             sx + Inches(5.9), sy + sh - Inches(0.05),
             color=ACCENT, weight=2.0)
    add_text(s, sx + Inches(0.4), sy + sh + Inches(0.0),
             Inches(5.5), Inches(0.3),
             "← 500–1000 m daily-activity corridor →",
             size=9, bold=True, color=ACCENT_DEEP, italic=True,
             align=PP_ALIGN.CENTER)

    # Right side: data + 3 questions
    rx = Inches(7.45)
    section_label(s, rx, Inches(1.85), Inches(5.5),
                  "THE NUMBERS  ·  FDMA 2024")

    # Big number 1
    add_text(s, rx, Inches(2.30), Inches(5.6), Inches(1.0),
             "91,000+", size=46, bold=True, color=HEAT_HOT, line_spacing=1.0)
    add_text(s, rx, Inches(3.25), Inches(5.6), Inches(0.35),
             "heatstroke emergency transports — Japan, 2023",
             size=11, color=BODY)

    # Big numbers 2
    add_text(s, rx, Inches(3.70), Inches(5.6), Inches(0.55),
             "1,200+  in Yamaguchi  ·  60%  aged 65+",
             size=18, bold=True, color=YU_INDIGO)
    add_text(s, rx, Inches(4.25), Inches(5.6), Inches(0.4),
             "Heat is no longer just weather — it is a regional public-health issue.",
             size=11, color=BODY, italic=True)

    # 3 questions
    section_label(s, rx, Inches(4.85), Inches(5.5),
                  "MY THREE QUESTIONS")
    qy = Inches(5.30)
    qs = [("WHERE", "is it hot?"),
          ("WHY", "is it hot?"),
          ("HOW", "to cool & re-vitalize the city?")]
    for i, (k, v) in enumerate(qs):
        y = qy + i * Inches(0.45)
        add_rect(s, rx, y + Inches(0.05), Inches(0.06), Inches(0.30),
                 fill=ACCENT)
        add_text(s, rx + Inches(0.2), y, Inches(1.4), Inches(0.4),
                 k, size=15, bold=True, color=YU_INDIGO)
        add_text(s, rx + Inches(1.55), y + Inches(0.04), Inches(4), Inches(0.4),
                 v, size=13, color=BODY)

    # Bottom triple-challenge band
    band_y = Inches(6.85)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.30),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y, Inches(11.6), Inches(0.30),
             "REGIONAL CITIES FACE A TRIPLE CHALLENGE   ·   CLIMATE WARMING  +  AGING SOCIETY  +  CITY-CENTER DECLINE",
             size=11, bold=True, color=ACCENT, anchor=MSO_ANCHOR.MIDDLE)

    add_notes(s, """[SLIDE 3 — WHY MY RESEARCH MATTERS — ~50s]

Why does this research matter?

In 2023, Japan recorded over 91,000 emergency heatstroke transports. In Yamaguchi alone, 1,200 cases — and 60 percent were aged 65 or older.

But not every street is equally hot. As the section drawing shows: built-up zones trap heat; green-and-wind zones stay cool. Elderly residents walk through this contrast every day, over 500 to 1,000 meters.

So my research asks three simple questions — Where is it hot? Why is it hot? How can we cool the city while keeping it walkable?

This sits at the intersection of climate warming, aging society, and city-center decline — the triple challenge of regional cities.
""")


# ============================================================
# SLIDE 04 — RESEARCH TRAJECTORY
# ============================================================
def slide_04():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 4, "RESEARCH TRAJECTORY",
                "10 years, three stages — Building → Person → City.")

    # Three stage boxes
    stages = [
        ("STAGE 01", "BUILDING",
         "How does building type & form\nshape indoor thermal & energy?",
         "183 households across 3 cities\nWindow-to-wall ratio optimization\nResidential building types comparison",
         "Sustainability  ·  JCEA  ·  Procedia", icon_building),
        ("STAGE 02", "PERSON",
         "How do indoor conditions\naffect learning, health, behavior?",
         "Classroom thermal × learning\nPM2.5 health-effect assessment\nElderly spatial needs",
         "Building & Env. Q1 (Top 5)  ·  Env. Pollution Q1  ·  Energies Q1", icon_person),
        ("STAGE 03", "CITY",
         "How do GBI, wind & morphology\nregulate pedestrian heat exposure?",
         "Satellite LST + Sentinel-2 LCZ\nCourtyard CFD wind analysis\nKumamoto green-infra mapping",
         "Sustainability Q2  ·  Book Chapter  ·  MLIT EBPM-cited", icon_city),
    ]
    sx0 = Inches(0.75)
    sy = Inches(1.85)
    sw = Inches(4.05)
    sh = Inches(4.0)
    gap = Inches(0.10)

    for i, (lab, name, q, methods, papers, icon_fn) in enumerate(stages):
        x = sx0 + i * (sw + gap)
        # Card
        add_rect(s, x, sy, sw, sh, fill=WHITE, line=ARCH_LINE, line_w=Pt(0.6))
        # Header
        add_rect(s, x, sy, sw, Inches(0.45), fill=YU_INDIGO)
        add_text(s, x + Inches(0.25), sy, Inches(1.5), Inches(0.45),
                 lab, size=10, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        # Big name
        add_text(s, x + Inches(0.25), sy + Inches(0.60), sw - Inches(2),
                 Inches(0.55), name, size=22, bold=True, color=YU_INDIGO)
        # Icon (right side)
        icon_fn(s, x + sw - Inches(1.3), sy + Inches(0.55),
                Inches(1.0))
        # Question
        section_label(s, x + Inches(0.25), sy + Inches(1.30),
                      sw - Inches(0.4), "QUESTION")
        add_text(s, x + Inches(0.25), sy + Inches(1.55), sw - Inches(0.4),
                 Inches(0.8), q, size=11.5, color=DARK, italic=True,
                 line_spacing=1.35)
        # Methods/findings
        section_label(s, x + Inches(0.25), sy + Inches(2.35),
                      sw - Inches(0.4), "WORK")
        add_text(s, x + Inches(0.25), sy + Inches(2.60), sw - Inches(0.4),
                 Inches(1.05), methods, size=11, color=BODY,
                 line_spacing=1.4)
        # Papers
        section_label(s, x + Inches(0.25), sy + Inches(3.45),
                      sw - Inches(0.4), "OUTPUTS")
        add_text(s, x + Inches(0.25), sy + Inches(3.65), sw - Inches(0.4),
                 Inches(0.35), papers, size=10.5, bold=True,
                 color=ACCENT_DEEP)

    # Connecting arrows between stages
    arr_y = sy + Inches(0.22)
    for i in range(2):
        x1 = sx0 + (i + 1) * sw + i * gap
        x2 = x1 + gap
        add_line(s, x1, arr_y, x2, arr_y, color=ACCENT, weight=2.5)

    # Bottom claim
    band_y = Inches(6.10)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.85),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.12), Inches(11.6),
             Inches(0.35), "WHAT BINDS THE THREE STAGES",
             size=10, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.40), Inches(11.6),
             Inches(0.4),
             "Each stage was pushed forward by a question the previous stage could only partly answer.  "
             "Stage 3 is where HIRAKU-Global begins.",
             size=13, bold=True, color=WHITE)

    add_notes(s, """[SLIDE 4 — RESEARCH TRAJECTORY — ~60s]

My research has moved through three stages — not jumped between topics.

Stage 1 — Building. How does form shape indoor thermal and energy performance? This gave me the physical side, but not the human side.

Stage 2 — Person. How do indoor conditions affect learning, health, behavior? This is where my two Q1 papers come from — Building and Environment, top 5 in its field, and Environmental Pollution. But I was still indoors.

Stage 3 — City. How do green-blue infrastructure, wind, and morphology together regulate pedestrian heat exposure? This is where the Kumamoto work — and the MLIT-cited case — comes from.

Each stage was pushed forward by a question the previous one could only partly answer. Stage 3 is where HIRAKU-Global begins.
""")


# ============================================================
# SLIDE 05 — ORIGINALITY (CORE)
# ============================================================
def slide_05():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 5, "ORIGINALITY  ·  CORE",
                "Satellite + measurement + CFD + national-level policy — in one workflow.")

    # Left: Cross-scale altitude diagram
    dx = Inches(0.75)
    dy = Inches(1.85)
    dw = Inches(5.7)
    dh = Inches(4.3)
    add_rect(s, dx, dy, dw, dh, fill=LIGHTER, line=ARCH_LINE, line_w=Pt(0.5))
    section_label(s, dx + Inches(0.20), dy + Inches(0.10), Inches(5),
                  "CROSS-SCALE WORKFLOW  ·  SATELLITE → BLOCK → PEDESTRIAN")

    # Altitude axis on the left
    ax = dx + Inches(0.55)
    ay_top = dy + Inches(0.65)
    ay_bot = dy + dh - Inches(0.45)
    add_line(s, ax, ay_top, ax, ay_bot, color=YU_INDIGO, weight=1.5)
    # Tick marks
    for ty in [ay_top + Inches(0.1), dy + Inches(2.0), dy + Inches(3.3),
               ay_bot - Inches(0.1)]:
        add_line(s, ax - Inches(0.08), ty, ax + Inches(0.08), ty,
                 color=YU_INDIGO, weight=1.0)
    add_text(s, ax - Inches(0.45), ay_top - Inches(0.05),
             Inches(0.4), Inches(0.3), "km", size=8, color=MUTED,
             align=PP_ALIGN.RIGHT)
    add_text(s, ax - Inches(0.45), ay_bot - Inches(0.20),
             Inches(0.4), Inches(0.3), "m", size=8, color=MUTED,
             align=PP_ALIGN.RIGHT)

    # Satellite (top)
    icon_satellite(s, dx + Inches(1.0), dy + Inches(0.65),
                   Inches(0.85), color=YU_INDIGO)
    add_text(s, dx + Inches(2.05), dy + Inches(0.75),
             Inches(3.5), Inches(0.3),
             "LANDSAT-8/9  +  SENTINEL-2",
             size=10, bold=True, color=YU_INDIGO)
    add_text(s, dx + Inches(2.05), dy + Inches(1.05),
             Inches(3.5), Inches(0.3),
             "LST × LCZ — 30 m resolution screening",
             size=9, color=BODY, italic=True)

    # Block scale (middle)
    by_block = dy + Inches(2.0)
    icon_city(s, dx + Inches(0.85), by_block - Inches(0.05),
              Inches(1.1), color=YU_INDIGO_LT)
    # Wind arrows
    for i, ay in enumerate([by_block - Inches(0.4), by_block - Inches(0.1)]):
        add_line(s, dx + Inches(2.05), ay,
                 dx + Inches(2.85), ay, color=HEAT_COOL, weight=1.5)
        add_tri(s, dx + Inches(2.80), ay - Inches(0.04),
                Inches(0.08), Inches(0.08), fill=HEAT_COOL)
    add_text(s, dx + Inches(2.95), by_block - Inches(0.30),
             Inches(3.0), Inches(0.3),
             "BLOCK-SCALE CFD",
             size=10, bold=True, color=YU_INDIGO)
    add_text(s, dx + Inches(2.95), by_block - Inches(0.05),
             Inches(3.0), Inches(0.3),
             "OpenFOAM — wind × morphology × GBI",
             size=9, color=BODY, italic=True)

    # Pedestrian scale (bottom)
    by_ped = dy + Inches(3.3)
    icon_person(s, dx + Inches(1.20), by_ped, Inches(0.55), color=DARK)
    # Path line
    add_line(s, dx + Inches(0.85), by_ped + Inches(0.65),
             dx + Inches(4.5), by_ped + Inches(0.65),
             color=ACCENT, weight=2.0)
    # Trees along path
    icon_tree(s, dx + Inches(2.3), by_ped + Inches(0.2), Inches(0.4),
              color=GREEN_PARK)
    icon_tree(s, dx + Inches(3.5), by_ped + Inches(0.2), Inches(0.4),
              color=GREEN_PARK)
    add_text(s, dx + Inches(2.05), by_ped - Inches(0.10),
             Inches(3.5), Inches(0.3),
             "PEDESTRIAN  ·  WBGT FIELD",
             size=10, bold=True, color=YU_INDIGO)
    add_text(s, dx + Inches(2.05), by_ped + Inches(0.15),
             Inches(3.5), Inches(0.3),
             "Elderly walking corridor, 500–1000 m",
             size=9, color=BODY, italic=True)

    # Right: 4 originality cards (2x2)
    rx = Inches(6.85)
    ry = Inches(1.85)
    cw = Inches(2.95)
    ch = Inches(2.05)
    cgap = Inches(0.10)
    cards = [
        ("01", "MULTI-SOURCE",
         "Satellite RS\n+ on-site measurement\n+ CFD"),
        ("02", "CUMULATIVE",
         "Pedestrian-scale\nheat retention zones\n(not instantaneous T)"),
        ("03", "POLICY-APPLIED",
         "Kumamoto City green-\ninfrastructure policy\n(Book chapter A-1)"),
        ("04", "MLIT EBPM",
         "Adopted by MLIT as\nan Evidence-Based\nPolicy Making case"),
    ]
    for i, (n, h, b) in enumerate(cards):
        r, c = divmod(i, 2)
        x = rx + c * (cw + cgap)
        y = ry + r * (ch + cgap)
        add_rect(s, x, y, cw, ch, fill=WHITE, line=ARCH_LINE, line_w=Pt(0.5))
        add_rect(s, x, y, cw, Inches(0.35), fill=YU_INDIGO)
        add_text(s, x + Inches(0.15), y, Inches(0.5), Inches(0.35),
                 n, size=10, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.7), y, cw - Inches(0.8), Inches(0.35),
                 h, size=10, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.15), y + Inches(0.50),
                 cw - Inches(0.3), Inches(1.5), b,
                 size=11, color=DARK, line_spacing=1.4)
        if i == 3:
            # Highlight the MLIT card with gold border
            add_rect(s, x, y, cw, ch, fill=None, line=ACCENT, line_w=Pt(1.5))

    # Patent + data source footer (small annotation under cross-scale diagram)
    add_text(s, dx + Inches(0.20), dy + dh + Inches(0.02),
             dw - Inches(0.4), Inches(0.22),
             "Methods validated in C-1 (Sustainability 2024) & A-1 book chapter  ·  + Utility Model Patent CN 210135674 U",
             size=8.5, color=MUTED, italic=True)

    # Bottom claim
    band_y = Inches(6.45)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.50),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.05), Inches(11.6), Inches(0.25),
             "RESEARCH  →  POLICY  →  NATIONAL RECOGNITION",
             size=10, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.25), Inches(11.6), Inches(0.25),
             "Few researchers combine satellite, measurement, CFD, and national-level policy adoption in one continuous workflow.",
             size=11.5, bold=True, color=WHITE)

    add_notes(s, """[SLIDE 5 — ORIGINALITY (CORE) — ~70s]

This is the core of my originality.

I work at three scales — chained as one workflow, not three separate studies.

Top — satellite. Landsat-8/9 and Sentinel-2 tell me where heat accumulates.

Middle — block-scale CFD. OpenFOAM tells me why, given wind and building form.

Bottom — pedestrian validation. WBGT along the actual 500-to-1,000-meter walking corridors of elderly residents.

Four things make this original. First, multi-source data fusion. Second, cumulative heat exposure — not instantaneous temperature. Third, already applied to Kumamoto's green-infrastructure policy.

And fourth — most importantly — cited by Japan's MLIT as an Evidence-Based Policy Making case.

Few researchers can show all four — satellite, measurement, CFD, and national policy adoption — in one workflow.
""")


# ============================================================
# SLIDE 06 — RESEARCH OUTPUTS
# ============================================================
def slide_06():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 6, "RESEARCH OUTPUTS",
                "15 peer-reviewed papers · 3 Q1 · 2 led, 1 contributed.")

    # Big number block (4 columns) — compressed
    nums = [
        ("15", "peer-reviewed\npapers"),
        ("10", "English\nSCI / SCIE"),
        ("8", "with Impact\nFactor"),
        ("3", "Q1 papers\n(2 led + 1 contributed)"),
    ]
    x0 = Inches(0.75)
    y0 = Inches(1.85)
    nw = Inches(3.02)
    nh = Inches(1.70)
    gap = Inches(0.10)
    for i, (num, lab) in enumerate(nums):
        x = x0 + i * (nw + gap)
        fill = YU_INDIGO if i == 3 else LIGHT_BG
        tc = WHITE if i == 3 else YU_INDIGO
        bc = ACCENT if i == 3 else BODY
        add_rect(s, x, y0, nw, nh, fill=fill)
        add_rect(s, x + Inches(0.3), y0 + Inches(1.30),
                 Inches(0.4), Emu(38100), fill=ACCENT if i == 3 else YU_INDIGO)
        add_text(s, x, y0 + Inches(0.10), nw, Inches(1.15),
                 num, size=68, bold=True, color=tc,
                 align=PP_ALIGN.CENTER, line_spacing=1.0)
        add_text(s, x + Inches(0.3), y0 + Inches(1.38), nw - Inches(0.6),
                 Inches(0.4), lab, size=10, color=bc, line_spacing=1.25,
                 bold=(i == 3))

    # Q1 journals row — accurate author labels
    section_label(s, Inches(0.75), Inches(3.70), Inches(12),
                  "Q1 JOURNALS  ·  HONEST AUTHOR POSITIONING")
    journals = [
        ("Building and Environment", "IF ≈ 7.1  ·  Q1  ·  Top 5 in field",
         "Co-first author  ·  led design & supervision\nClassroom thermal × learning", True),
        ("Energies", "IF ≈ 3.1  ·  Q1",
         "First author\nClassroom comfort × learning efficiency", True),
        ("Environmental Pollution", "IF ≈ 7.3  ·  Q1",
         "Co-author  ·  research-team member\nPM2.5 health-effects assessment", False),
    ]
    jx0 = Inches(0.75)
    jy = Inches(4.15)
    jw = Inches(4.05)
    jh = Inches(1.30)
    for i, (jn, jq, jr, led) in enumerate(journals):
        x = jx0 + i * (jw + Inches(0.10))
        add_rect(s, x, jy, jw, jh, fill=WHITE, line=ARCH_LINE, line_w=Pt(0.6))
        accent_color = ACCENT if led else MUTED
        add_rect(s, x, jy, Inches(0.07), jh, fill=accent_color)
        add_text(s, x + Inches(0.25), jy + Inches(0.10),
                 jw - Inches(0.4), Inches(0.35),
                 jn, size=12.5, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.25), jy + Inches(0.45),
                 jw - Inches(0.4), Inches(0.25),
                 jq, size=10, bold=True, color=ACCENT_DEEP if led else MUTED)
        add_text(s, x + Inches(0.25), jy + Inches(0.72),
                 jw - Inches(0.4), Inches(0.55),
                 jr, size=10, color=BODY, italic=True, line_spacing=1.30)

    # Publication timeline — first/co-first author papers (NEW)
    section_label(s, Inches(0.75), Inches(5.55), Inches(12),
                  "FIRST / CO-FIRST AUTHOR PAPERS  ·  PEER-REVIEWED ENGLISH BY YEAR")
    years_data = [
        ("2017", [("JCEA", "peer-reviewed", LIGHT_BG, BODY)]),
        ("2020", [("Lowland Tech.", "peer-reviewed", LIGHT_BG, BODY)]),
        ("2021", [
            ("Energies", "Q1  ·  first", YU_INDIGO, WHITE),
            ("Sustainability", "Q2  ·  first", YU_INDIGO_LT, WHITE),
        ]),
        ("2023", [
            ("Building & Env.", "Q1 Top 5  ·  co-1st", ACCENT, WHITE),
        ]),
        ("2024", [
            ("Sustainability", "Q2  ·  first", YU_INDIGO_LT, WHITE),
            ("Kumamoto Pol. ×2", "Japanese  ·  first", LIGHT_BG, BODY),
        ]),
    ]
    col_w = Inches(2.40)
    strip_x = Inches(0.75)
    strip_y = Inches(5.95)
    strip_h = Inches(1.00)
    axis_y = strip_y + strip_h - Inches(0.15)

    # Horizontal axis line
    add_line(s, strip_x, axis_y, strip_x + Inches(12.0), axis_y,
             color=YU_INDIGO, weight=1.2)

    for i, (year, papers) in enumerate(years_data):
        x = strip_x + i * (col_w + Inches(0.05))
        # Year tick & label
        add_oval(s, x + col_w / 2 - Inches(0.07), axis_y - Inches(0.07),
                 Inches(0.14), Inches(0.14), fill=YU_INDIGO)
        # Stack papers above
        n = len(papers)
        paper_h = Inches(0.28)
        paper_gap = Inches(0.04)
        # bottom paper sits just above axis
        for j, (jn, qn, bg, fg) in enumerate(papers):
            # papers in `papers` list: index 0 = bottom-most
            py = axis_y - Inches(0.20) - (j + 1) * paper_h - j * paper_gap
            add_rect(s, x + Inches(0.10), py, col_w - Inches(0.20), paper_h,
                     fill=bg)
            add_text(s, x + Inches(0.15), py + Inches(0.01),
                     col_w - Inches(0.30), Inches(0.14),
                     jn, size=8.5, bold=True, color=fg)
            add_text(s, x + Inches(0.15), py + Inches(0.14),
                     col_w - Inches(0.30), Inches(0.12),
                     qn, size=7.5, color=fg, italic=True)
        # Year label below axis
        add_text(s, x, axis_y + Inches(0.10), col_w, Inches(0.20),
                 year, size=10, bold=True, color=YU_INDIGO,
                 align=PP_ALIGN.CENTER)

    # Continuity inline (very compact, no band)
    add_text(s, Inches(0.75), Inches(6.97), Inches(12), Inches(0.10),
             "ONE CONTINUOUS LINE: building energy → indoor comfort → PM2.5 → urban heat → green infra → policy",
             size=8.5, bold=True, color=YU_INDIGO, italic=True)

    add_notes(s, """[SLIDE 6 — RESEARCH OUTPUTS — ~50s]

Now my publications — quality first, and honest positioning.

Fifteen peer-reviewed papers. Ten English SCI or SCIE. Eight with impact factor. Three in Q1.

I want to be precise about authorship — I led two of the three Q1 papers, and contributed to one. As first or co-first author: Building and Environment, top 5 in its field; and Energies. As co-author: Environmental Pollution, where I joined a research-team study on PM2.5 health.

The timeline below shows my first or co-first authored papers by year — including two Kumamoto Urban Policy articles in 2024.

What matters more than journal count is the line that connects them — building energy, indoor comfort, PM2.5 health, urban heat, green infrastructure, policy. One continuous research agenda.
""")


# ============================================================
# SLIDE 07 — INTERNATIONAL COLLABORATION
# ============================================================
def slide_07():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 7, "INTERNATIONAL COLLABORATION",
                "Organizer, not just participant — three concrete records.")

    # Three records
    records = [
        ("01", "SAKURA SCIENCE PROGRAM",
         "Organized ZSTU × Japanese\nuniversities student-researcher\nexchanges over multiple years",
         "Sustained partnership — paused\nby COVID, friendship intact"),
        ("02", "ZHEJIANG CARBON-NEUTRAL CENTER",
         "Built the Zhejiang International\nCo-op Center on Carbon Neutrality,\nas ZSTU representative",
         "1 of 4 provincial centers\n— ZSTU as core unit"),
        ("03", "5-COUNTRY ONLINE FORUM",
         "Organized international forum:\nChina · Japan · UK (UCL) ·\nIndonesia · Bangladesh",
         "Multi-country coordination\nunder COVID constraints"),
    ]
    x0 = Inches(0.75)
    y0 = Inches(1.85)
    cw = Inches(4.05)
    ch = Inches(3.20)
    gap = Inches(0.10)
    for i, (n, h, b, f) in enumerate(records):
        x = x0 + i * (cw + gap)
        add_rect(s, x, y0, cw, ch, fill=WHITE, line=ARCH_LINE, line_w=Pt(0.6))
        add_rect(s, x, y0, cw, Inches(0.55), fill=YU_INDIGO)
        add_text(s, x + Inches(0.25), y0, Inches(0.6), Inches(0.55),
                 n, size=14, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.95), y0, cw - Inches(1.0), Inches(0.55),
                 h, size=11.5, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.25), y0 + Inches(0.85),
                 cw - Inches(0.4), Inches(1.40),
                 b, size=12, color=DARK, line_spacing=1.4)
        # Divider
        add_rect(s, x + Inches(0.25), y0 + Inches(2.35),
                 cw - Inches(0.5), Emu(6350), fill=ACCENT)
        add_text(s, x + Inches(0.25), y0 + Inches(2.45),
                 cw - Inches(0.4), Inches(0.65),
                 f, size=10.5, color=ACCENT_DEEP, italic=True,
                 line_spacing=1.35)

    # Invited lectures strip (NEW)
    inv_y = Inches(5.20)
    add_rect(s, Inches(0.75), inv_y, Inches(12.0), Inches(0.35),
             fill=None, line=ACCENT, line_w=Pt(0.5))
    add_rect(s, Inches(0.75), inv_y, Inches(0.06), Inches(0.35), fill=ACCENT)
    add_text(s, Inches(0.92), inv_y, Inches(2.8), Inches(0.35),
             "INVITED TALKS",
             size=9, bold=True, color=ACCENT_DEEP, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(3.7), inv_y, Inches(9.0), Inches(0.35),
             "Shanghai Inst. for Global City (2025)  ·  Shanghai Normal U. (2025)  ·  Hangzhou Fengjinglishe (2021)",
             size=10, color=YU_INDIGO, anchor=MSO_ANCHOR.MIDDLE)

    # Future network diagram (bottom)
    nx = Inches(0.75)
    ny = Inches(5.65)
    nw = Inches(12.0)
    nh = Inches(1.30)
    add_rect(s, nx, ny, nw, nh, fill=LIGHTER, line=ARCH_LINE, line_w=Pt(0.5))
    section_label(s, nx + Inches(0.15), ny + Inches(0.08), Inches(8),
                  "FUTURE NETWORK  ·  BUILDING ON EXISTING FRIENDSHIP")

    # Central hub (Yamaguchi)
    cx = nx + nw / 2
    cy = ny + Inches(0.62)
    add_rect(s, cx - Inches(0.85), cy - Inches(0.18), Inches(1.7),
             Inches(0.36), fill=YU_INDIGO)
    add_text(s, cx - Inches(0.85), cy - Inches(0.2), Inches(1.7),
             Inches(0.4), "YAMAGUCHI U.", size=11, bold=True,
             color=ACCENT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Partners around
    partners = [
        (-4.5, 0.0, "UCL", "Dr. Huanfa Chen"),
        (-2.4, 0.0, "ZSTU", "Sakura net"),
        (2.4, 0.0, "ZHEJIANG U.", "Prof. Jian Ge"),
        (4.5, 0.0, "ASIA NODES", "Indonesia · Bangladesh"),
    ]
    for off, _, name, sub in partners:
        px = cx + Inches(off)
        py = cy
        # Connection line
        add_line(s, cx, cy, px, py, color=ACCENT, weight=1.0,
                 dash="dash")
        # Node
        add_rect(s, px - Inches(0.85), py - Inches(0.20),
                 Inches(1.7), Inches(0.4),
                 fill=WHITE, line=YU_INDIGO, line_w=Pt(1.0))
        add_text(s, px - Inches(0.85), py - Inches(0.20),
                 Inches(1.7), Inches(0.4),
                 name, size=10, bold=True, color=YU_INDIGO,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, px - Inches(0.85), py + Inches(0.22),
                 Inches(1.7), Inches(0.3),
                 sub, size=8, color=BODY, italic=True,
                 align=PP_ALIGN.CENTER)

    add_notes(s, """[SLIDE 7 — INTERNATIONAL COLLABORATION — ~55s]

International collaboration, for me, means organizing — not just attending.

Three concrete records.

One — the Sakura Science Program. I organized exchanges between Zhejiang Sci-Tech University and Japanese universities over multiple years. Paused by COVID; friendship intact.

Two — during COVID, I helped build the Zhejiang International Cooperation Center on Carbon Neutrality. Only four such centers province-wide; ZSTU was the core unit of one.

Three — I organized a five-country online forum: China, Japan, UK at UCL, Indonesia, and Bangladesh.

The future network below builds on these existing friendships, with Yamaguchi University at the center.

In all three cases — I was the organizer.
""")


# ============================================================
# SLIDE 08 — FUNDING & LEADERSHIP
# ============================================================
def slide_08():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 8, "FUNDING & PROJECT LEADERSHIP",
                "≈ 100 million JPY total — and the Japan pattern has already started.")

    # Three phases
    phases = [
        ("CHINA  ·  2018–2023",
         "≈ 100 M\nJPY",
         "8 projects  ·  5 as Leading Researcher\nIncluding NSSFC General Project\n(collaborator)",
         "HIGH-COMPETITION ENVIRONMENT",
         YU_INDIGO, WHITE),
        ("KUMAMOTO  ·  2023–2025",
         "Municipal\npost",
         "Institutional rule:\nexternal competitive grants\nnot permitted",
         "POLICY-OUTPUT  ·  MLIT EBPM-CITED",
         LIGHT_BG, YU_INDIGO),
        ("YAMAGUCHI  ·  since Jan 2026",
         "# 1\n/ 13",
         "Top-ranked applicant\nin Yamaguchi U. regional\nresearch program (4 selected)",
         "JAPAN PATTERN HAS STARTED",
         YU_INDIGO, WHITE),
    ]
    px0 = Inches(0.75)
    py = Inches(1.85)
    pw = Inches(4.05)
    ph = Inches(4.0)
    gap = Inches(0.10)
    for i, (h, big, body_t, footer, bg, hc) in enumerate(phases):
        x = px0 + i * (pw + gap)
        add_rect(s, x, py, pw, ph, fill=bg)
        # Top tag
        accent_c = ACCENT if hc == WHITE else ACCENT_DEEP
        add_text(s, x + Inches(0.25), py + Inches(0.25),
                 pw - Inches(0.5), Inches(0.4),
                 h, size=11, bold=True, color=accent_c)
        # Big figure
        add_text(s, x + Inches(0.25), py + Inches(0.7),
                 pw - Inches(0.5), Inches(1.65),
                 big, size=46, bold=True, color=hc, line_spacing=0.95)
        # Divider
        add_rect(s, x + Inches(0.25), py + Inches(2.40),
                 Inches(0.8), Emu(12700), fill=accent_c)
        # Body
        add_text(s, x + Inches(0.25), py + Inches(2.60),
                 pw - Inches(0.5), Inches(1.0),
                 body_t, size=12, color=hc, line_spacing=1.4)
        # Footer tag
        add_text(s, x + Inches(0.25), py + Inches(3.60),
                 pw - Inches(0.5), Inches(0.3),
                 footer, size=9, bold=True, color=accent_c, italic=True)

    # Forward path
    fy = Inches(6.10)
    add_rect(s, Inches(0.75), fy, Inches(12.0), Inches(0.80),
             fill=None, line=ACCENT, line_w=Pt(1.2))
    add_text(s, Inches(0.95), fy + Inches(0.10), Inches(11.6), Inches(0.30),
             "FORWARD PATH",
             size=10, bold=True, color=ACCENT_DEEP)
    add_text(s, Inches(0.95), fy + Inches(0.36), Inches(11.6), Inches(0.4),
             "KAKENHI KIBAN C  (FY2026 autumn)   →   KAKENHI KIBAN B  (during HIRAKU)",
             size=15, bold=True, color=YU_INDIGO)

    add_notes(s, """[SLIDE 8 — FUNDING & LEADERSHIP — ~60s]

Funding — the honest picture in three phases.

China, 2018 to 2023. Across eight projects, approximately 100 million yen total. Five as Leading Researcher, in a highly competitive environment.

Kumamoto, 2023 to 2025. Municipal post — institutional rule did not permit external grants such as Kakenhi. What I produced instead was the MLIT EBPM-cited policy work.

Yamaguchi, since January 2026 — the first time I could apply in Japan. Within months, I was ranked number one out of thirteen applicants in the Yamaguchi regional research program. Four were selected.

Forward path — Kakenhi Kiban C this autumn, building toward Kiban B during HIRAKU. The Japan pattern has started.
""")


# ============================================================
# SLIDE 09 — RESEARCH PLAN
# ============================================================
def slide_09():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 9, "RESEARCH PLAN  ·  FEASIBILITY & INTERNATIONAL",
                "Not from zero — pipeline running, partners ready, first grant won.")

    # Left: Western Japan schematic map with 3 cities
    mx = Inches(0.75)
    my = Inches(1.85)
    mw = Inches(4.2)
    mh = Inches(3.0)
    add_rect(s, mx, my, mw, mh, fill=LIGHTER, line=ARCH_LINE, line_w=Pt(0.5))
    section_label(s, mx + Inches(0.15), my + Inches(0.10), Inches(5),
                  "3 CITIES  ×  3 WIND REGIMES")

    # Simplified Honshu/Western Japan outline (using a few connected rectangles)
    # Just a stylized shape for reference
    # Sea of Japan (top)
    add_rect(s, mx + Inches(0.3), my + Inches(0.45), mw - Inches(0.6),
             Inches(0.65), fill=HEAT_COOL)
    add_text(s, mx + Inches(0.4), my + Inches(0.50), Inches(3), Inches(0.3),
             "SEA OF JAPAN", size=8, bold=True, color=WHITE, italic=True)

    # Land mass (stylized)
    add_rect(s, mx + Inches(0.3), my + Inches(1.10),
             mw - Inches(0.6), Inches(1.0), fill=LIGHT_BG,
             line=ARCH_LINE, line_w=Pt(0.6))
    add_text(s, mx + Inches(0.4), my + Inches(1.15),
             Inches(3), Inches(0.3),
             "CHUGOKU REGION  ·  WESTERN HONSHU",
             size=8, bold=True, color=MUTED, italic=True)

    # Seto Inland Sea (bottom)
    add_rect(s, mx + Inches(0.3), my + Inches(2.10),
             mw - Inches(0.6), Inches(0.5), fill=HEAT_COOL)
    add_text(s, mx + Inches(0.4), my + Inches(2.18),
             Inches(3), Inches(0.3),
             "SETO INLAND SEA", size=8, bold=True, color=WHITE, italic=True)

    # City dots
    cities = [
        (0.65, 1.5, "MATSUE", "LAKESIDE"),
        (1.95, 1.7, "YAMAGUCHI", "BASIN"),
        (2.85, 1.95, "UBE", "COASTAL"),
    ]
    for cxoff, cyoff, name, regime in cities:
        cx_d = mx + Inches(cxoff)
        cy_d = my + Inches(cyoff)
        add_oval(s, cx_d - Inches(0.12), cy_d - Inches(0.12),
                 Inches(0.24), Inches(0.24), fill=HEAT_HOT)
        # Label
        add_text(s, cx_d + Inches(0.18), cy_d - Inches(0.14),
                 Inches(1.6), Inches(0.22),
                 name, size=9, bold=True, color=YU_INDIGO)
        add_text(s, cx_d + Inches(0.18), cy_d + Inches(0.04),
                 Inches(1.6), Inches(0.22),
                 regime, size=7, color=BODY, italic=True)

    # N indicator
    add_text(s, mx + mw - Inches(0.45), my + Inches(0.85),
             Inches(0.3), Inches(0.3), "N",
             size=11, bold=True, color=YU_INDIGO, align=PP_ALIGN.CENTER)
    add_tri(s, mx + mw - Inches(0.38), my + Inches(0.55),
            Inches(0.16), Inches(0.30), fill=YU_INDIGO)

    # Middle: Method chain (vertical pipeline)
    px = Inches(5.20)
    py = Inches(1.85)
    pw = Inches(3.4)
    ph = Inches(3.0)
    section_label(s, px, py, Inches(3.4),
                  "METHOD CHAIN  ·  CITY → CORRIDOR")
    steps = [
        ("01", "SATELLITE SCREENING",
         "Landsat-8/9 LST × Sentinel-2 LCZ\nYears 1–2"),
        ("02", "BLOCK CFD",
         "OpenFOAM wind × morphology × GBI\nYear 3"),
        ("03", "PEDESTRIAN VALIDATION",
         "WBGT field measurement\nYear 4"),
    ]
    sy = py + Inches(0.40)
    for i, (n, h, b) in enumerate(steps):
        y = sy + i * Inches(0.85)
        add_rect(s, px, y, pw, Inches(0.75),
                 fill=WHITE, line=ARCH_LINE, line_w=Pt(0.5))
        add_rect(s, px, y, Inches(0.55), Inches(0.75),
                 fill=YU_INDIGO)
        add_text(s, px, y, Inches(0.55), Inches(0.75),
                 n, size=14, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, px + Inches(0.7), y + Inches(0.08),
                 pw - Inches(0.8), Inches(0.30),
                 h, size=11, bold=True, color=YU_INDIGO)
        add_text(s, px + Inches(0.7), y + Inches(0.38),
                 pw - Inches(0.8), Inches(0.35),
                 b, size=9, color=BODY, italic=True, line_spacing=1.25)
        # Connector arrow (down)
        if i < 2:
            add_line(s, px + pw / 2, y + Inches(0.75),
                     px + pw / 2, y + Inches(0.85),
                     color=ACCENT, weight=2.0)

    # Right: 5-year timeline (Gantt-style)
    gx = Inches(8.85)
    gy = Inches(1.85)
    gw = Inches(4.05)
    gh = Inches(3.0)
    section_label(s, gx, gy, Inches(4),
                  "5-YEAR PLAN  ·  HIRAKU PERIOD")

    # Year columns
    year_h = Inches(0.40)
    year_y = gy + Inches(0.4)
    year_w = gw / 5
    for yi in range(5):
        x = gx + yi * year_w
        add_rect(s, x, year_y, year_w, year_h,
                 fill=LIGHT_BG, line=ARCH_LINE, line_w=Pt(0.5))
        add_text(s, x, year_y, year_w, year_h,
                 f"Y{yi+1}", size=10, bold=True, color=YU_INDIGO,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Tasks bars
    tasks = [
        ("LST × LCZ diagnosis", 0, 2, YU_INDIGO_LT),
        ("UCL stay (2 months)", 1, 1, ACCENT),
        ("Block-scale CFD", 2, 1, YU_INDIGO_LT),
        ("Zhejiang U. visit", 2, 1, ACCENT),
        ("Pedestrian WBGT", 3, 1, YU_INDIGO_LT),
        ("Int'l workshop", 3, 1, ACCENT),
        ("Synthesis + Kakenhi B", 4, 1, HEAT_HOT),
    ]
    ty0 = year_y + Inches(0.55)
    bar_h = Inches(0.20)
    bar_gap = Inches(0.05)
    for i, (name, start, dur, col) in enumerate(tasks):
        y = ty0 + i * (bar_h + bar_gap)
        bx = gx + start * year_w + Inches(0.03)
        bw_ = dur * year_w - Inches(0.06)
        add_rect(s, bx, y, bw_, bar_h, fill=col)
        # Label
        add_text(s, gx, y - Inches(0.02),
                 Inches(4), Inches(0.25),
                 name, size=8, color=DARK,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    # Place labels INSIDE / OVER bars
    for i, (name, start, dur, col) in enumerate(tasks):
        y = ty0 + i * (bar_h + bar_gap)
        bx = gx + start * year_w + Inches(0.06)
        add_text(s, bx, y, year_w * dur, bar_h,
                 name, size=7, bold=True, color=WHITE,
                 anchor=MSO_ANCHOR.MIDDLE)

    # Feasibility claim (compressed)
    band_y = Inches(4.95)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.55),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.05), Inches(11.6),
             Inches(0.22),
             "FEASIBILITY — ALREADY PROVEN",
             size=9, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.27), Inches(11.6),
             Inches(0.28),
             "Satellite pipeline running  ·  CFD methodology established  ·  Partners aligned  ·  First Japanese grant won",
             size=11, bold=True, color=WHITE)

    # Budget plan strip (NEW)
    section_label(s, Inches(0.75), Inches(5.60), Inches(12),
                  "BUDGET PLAN  ·  STARTUP FUND  ¥ 2 M  /  OVERSEAS DISPATCH  ¥ 2 M")
    budget_items = [
        ("¥ 700K", "Field\nequipment", "WBGT · loggers ·\nradiometers"),
        ("¥ 350K", "Data &\nworkstation", "GIS · CFD ·\nstorage"),
        ("¥ 300K", "Student\nRAs", "Master's students\nfrom Year 1"),
        ("¥ 300K", "Domestic\nfieldwork", "Yamaguchi · Ube ·\nMatsue surveys"),
        ("¥ 800K", "UCL stay\nYear 2", "2 months  ·  joint\nmethod paper"),
        ("¥ 400K", "Zhejiang U.\nYear 3", "Comparative\nframework"),
    ]
    bx0 = Inches(0.75)
    by = Inches(6.00)
    bw = Inches(2.00)
    bh = Inches(0.75)
    bgap = Inches(0.05)
    for i, (amt, head, det) in enumerate(budget_items):
        x = bx0 + i * (bw + bgap)
        fill = YU_INDIGO if i < 4 else LIGHT_BG
        tc = WHITE if i < 4 else YU_INDIGO
        sc = ACCENT if i < 4 else ACCENT_DEEP
        bc = RGBColor(0xCB, 0xD5, 0xE0) if i < 4 else BODY
        add_rect(s, x, by, bw, bh, fill=fill)
        add_text(s, x + Inches(0.10), by + Inches(0.05),
                 bw - Inches(0.2), Inches(0.25),
                 amt, size=13, bold=True, color=sc)
        add_text(s, x + Inches(0.10), by + Inches(0.28),
                 bw - Inches(0.2), Inches(0.22),
                 head, size=9, bold=True, color=tc, line_spacing=1.15)
        add_text(s, x + Inches(0.10), by + Inches(0.50),
                 bw - Inches(0.2), Inches(0.25),
                 det, size=7.5, color=bc, italic=True, line_spacing=1.2)

    # Risk awareness (compressed single line)
    add_text(s, Inches(0.75), Inches(6.88), Inches(12), Inches(0.16),
             "RISK MANAGED  ·  ANCHOR YAMAGUCHI FIRST · STEPWISE EXPANSION · ONLINE COLLAB FALLBACK · KUMAMOTO BASELINE AS REFERENCE",
             size=8.5, bold=True, color=ACCENT_DEEP)

    add_notes(s, """[SLIDE 9 — RESEARCH PLAN (CORE) — ~70s]

This is the project I will run during HIRAKU-Global.

Left — three cities, three wind regimes within one region: Matsue lakeside, Yamaguchi basin, Ube coastal. The contrast is exactly what the science needs.

Middle — the method chain. Step 1 satellite screening — already running. Step 2 block CFD — methodology already established. Step 3 pedestrian WBGT — co-designed with Yamaguchi City's elderly-care offices.

Right — the five-year plan. Year 1 diagnosis. Year 2 UCL stay with Dr. Huanfa Chen. Year 3 CFD plus Zhejiang visit. Year 4 pedestrian field plus international workshop at Yamaguchi. Year 5 synthesis and Kakenhi B.

This plan does not start from zero. Pipeline running. Partners ready. First grant won.

I also manage risk — anchor Yamaguchi first, expand stepwise, use online collaboration when needed. Deliver, not over-promise.
""")


# ============================================================
# SLIDE 10 — DURING HIRAKU + POST-TENURE
# ============================================================
def slide_10():
    s = prs.slides.add_slide(blank)
    page_chrome(s, 10, "ASPIRATIONS",
                "Year-by-year KPI · 3I framework × 5 years.")

    # 3I × 5 Year KPI matrix (full-width, NEW)
    section_label(s, Inches(0.75), Inches(1.85), Inches(12),
                  "DURING HIRAKU-GLOBAL  ·  YEAR-BY-YEAR KPI MATRIX")

    mx = Inches(0.75)
    my = Inches(2.25)
    label_w = Inches(1.60)
    col_w = Inches(2.05)  # 5 columns
    row_h = Inches(0.70)
    header_h = Inches(0.30)

    # Year header row
    add_rect(s, mx, my, label_w, header_h, fill=YU_INDIGO_DK)
    add_text(s, mx, my, label_w, header_h, "3I  /  YEAR",
             size=9, bold=True, color=ACCENT,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    year_labels = ["YEAR 1", "YEAR 2", "YEAR 3", "YEAR 4", "YEAR 5"]
    for j, yl in enumerate(year_labels):
        x = mx + label_w + j * col_w
        add_rect(s, x, my, col_w, header_h, fill=YU_INDIGO)
        add_text(s, x, my, col_w, header_h, yl, size=9.5, bold=True,
                 color=ACCENT, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)

    # Matrix rows
    matrix = [
        ("INNOVATIVE",
         ["LCZ × LST\ndiagnosis", "UCL joint\nmethod paper",
          "Mechanism\npaper (1st)", "Comparative\npaper", "Synthesis +\nworkflow"]),
        ("INFLUENTIAL",
         ["Kakenhi C\nsubmission", "First UCL\nco-author paper",
          "Q1 mechanism\npublished", "Q1 + int'l\nworkshop", "Kakenhi B\nsubmission"]),
        ("IMPACTFUL",
         ["Yamaguchi\nbaseline data", "Ube · Matsue\ncase design",
          "Heat-risk\nmaps (3 cities)", "Intervention\nmaps delivered",
          "Policy\nguidelines"]),
    ]
    for i, (lab, cells) in enumerate(matrix):
        ry = my + header_h + i * row_h
        # Tag
        add_rect(s, mx, ry, label_w, row_h, fill=YU_INDIGO)
        add_text(s, mx, ry, label_w, row_h, lab, size=11, bold=True,
                 color=ACCENT, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
        for j, cell_text in enumerate(cells):
            x = mx + label_w + j * col_w
            fill_col = LIGHTER if (i + j) % 2 == 0 else WHITE
            add_rect(s, x, ry, col_w, row_h,
                     fill=fill_col, line=ARCH_LINE, line_w=Pt(0.4))
            add_text(s, x + Inches(0.08), ry, col_w - Inches(0.16), row_h,
                     cell_text, size=9, color=DARK,
                     anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.25,
                     align=PP_ALIGN.CENTER)

    # Post-tenure compressed horizontal rings (NEW layout)
    section_label(s, Inches(0.75), Inches(4.78), Inches(12),
                  "POST-TENURE  ·  LOCAL-TO-GLOBAL  ·  LONG-TERM ANCHOR")
    ring_y = Inches(5.10)
    ring_w = Inches(2.40)
    ring_h = Inches(0.75)
    rings = [
        ("1", "LAB",      "Stable group at\nYamaguchi U."),
        ("2", "REGION",   "Chugoku-Shikoku\nheat toolkit"),
        ("3", "W. JAPAN", "Urban-thermal\nresearch hub"),
        ("4", "ASIA",     "EU · CN · SE Asia\nplatform"),
        ("5", "GLOBAL",   "Local-to-Global\nmodel export"),
    ]
    rx0 = Inches(0.75)
    rgap = Inches(0.05)
    for i, (n, name, desc) in enumerate(rings):
        x = rx0 + i * (ring_w + rgap)
        add_rect(s, x, ring_y, ring_w, ring_h,
                 fill=LIGHT_BG)
        add_rect(s, x, ring_y, Inches(0.50), ring_h, fill=YU_INDIGO)
        add_text(s, x, ring_y, Inches(0.50), ring_h, n,
                 size=18, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.55), ring_y + Inches(0.05),
                 ring_w - Inches(0.65), Inches(0.25),
                 name, size=10, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.55), ring_y + Inches(0.30),
                 ring_w - Inches(0.65), Inches(0.55),
                 desc, size=8.5, color=BODY, italic=True,
                 line_spacing=1.30)

    # WHAT I GIVE BACK
    section_label(s, Inches(0.75), Inches(5.95), Inches(12),
                  "WHAT I GIVE BACK  ·  ACTIVE MEMBER, NOT ONLY RECIPIENT")
    gives = [
        ("INT'L WORKSHOP",
         "Year 4 at Yamaguchi"),
        ("CHINA–JAPAN BRIDGE",
         "Annual seminar · translation"),
        ("TEACHING & MENTORING",
         "Grad supervision · seminars"),
        ("DEPT. & REGION",
         "Faculty collaboration · cities"),
    ]
    gy = Inches(6.30)
    gx0 = Inches(0.75)
    gw = Inches(2.97)
    gh2 = Inches(0.60)
    gap = Inches(0.08)
    for i, (h, b) in enumerate(gives):
        x = gx0 + i * (gw + gap)
        add_rect(s, x, gy, gw, gh2, fill=WHITE, line=ACCENT, line_w=Pt(0.8))
        add_rect(s, x, gy, Inches(0.06), gh2, fill=ACCENT)
        add_text(s, x + Inches(0.18), gy + Inches(0.07),
                 gw - Inches(0.3), Inches(0.25),
                 h, size=10, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.18), gy + Inches(0.32),
                 gw - Inches(0.3), Inches(0.30),
                 b, size=9, color=BODY, italic=True)

    add_notes(s, """[SLIDE 10 — ASPIRATIONS — ~60s]

What will I do during and after HIRAKU-Global?

Aligned with the 3I framework. Innovative — the cross-scale mechanism paper and a reusable diagnostic workflow. Influential — continued Q1 publications and the Kakenhi path. Impactful — deliverables to Yamaguchi, Ube, and Matsue.

After tenure — and this is critical — I will be a long-term anchor at Yamaguchi University. The rings on the right show the path: from my lab, to the region, to Western Japan as an urban thermal hub, to an Asia platform, to a Local-to-Global model.

I am not only a recipient. I will give back — an international workshop at Yamaguchi, a China–Japan academic bridge, teaching and mentoring graduate students, and active service to the department and the region.
""")


# ============================================================
# SLIDE 11 — CLOSING + COMMITMENTS
# ============================================================
def slide_11():
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, fill=YU_INDIGO_DK)
    # Subtle grid background
    for i in range(1, 8):
        y = Inches(0.75 * i)
        add_line(s, Inches(0.45), y, SLIDE_W - Inches(0.45), y,
                 color=RGBColor(0x1C, 0x35, 0x60), weight=0.4)
    for i in range(1, 13):
        x = Inches(1.0 * i)
        add_line(s, x, Inches(0.45), x, SLIDE_H - Inches(0.45),
                 color=RGBColor(0x1C, 0x35, 0x60), weight=0.4)

    # Top brand
    add_rect(s, 0, 0, Inches(3.0), Inches(0.10), fill=ACCENT)
    add_text(s, Inches(0.75), Inches(0.30), Inches(8), Inches(0.3),
             "CLOSING  ·  4 FOUNDATIONS  ·  4 COMMITMENTS",
             size=10, bold=True, color=ACCENT)

    add_text(s, Inches(0.75), Inches(0.90), Inches(12), Inches(0.9),
             "Four foundations — already in motion.",
             size=32, bold=True, color=WHITE, line_spacing=1.0)

    # Four foundations (compact pillars)
    pillars = [
        ("QUALITY", "15 papers · 3 Q1\nall 1st / responsible author",
         "Building & Env.  ·  Env. Pollution  ·  Energies"),
        ("BRIDGE", "Sakura · Zhejiang Center\n· 5-country forum",
         "UCL  ·  Zhejiang U.  ·  Asia"),
        ("FUNDING", "≈ 100 M JPY · # 1 of 13",
         "Kakenhi C → B"),
        ("IMPLEMENTATION", "Kumamoto green-infra\n+ MLIT EBPM case",
         "→ Yamaguchi · Ube · Matsue"),
    ]
    px = Inches(0.75)
    py = Inches(2.05)
    pw = Inches(2.95)
    ph = Inches(2.20)
    gap = Inches(0.12)
    for i, (lab, big, footer) in enumerate(pillars):
        x = px + i * (pw + gap)
        add_rect(s, x, py, pw, Inches(0.06), fill=ACCENT)
        add_text(s, x, py + Inches(0.18), pw, Inches(0.35),
                 lab, size=11, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER)
        add_text(s, x, py + Inches(0.65), pw, Inches(1.1),
                 big, size=14, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, line_spacing=1.3)
        add_rect(s, x + Inches(0.7), py + Inches(1.65),
                 pw - Inches(1.4), Emu(6350), fill=ACCENT)
        add_text(s, x, py + Inches(1.78), pw, Inches(0.4),
                 footer, size=9, color=RGBColor(0xCB, 0xD5, 0xE0),
                 align=PP_ALIGN.CENTER, italic=True, line_spacing=1.3)

    # Four commitments (what professors want to hear)
    cy = Inches(4.55)
    add_text(s, Inches(0.75), cy, Inches(12), Inches(0.3),
             "FOUR COMMITMENTS",
             size=10, bold=True, color=ACCENT)
    commits = [
        ("RESEARCH",
         "Deliver papers,\nworkflow, and Kakenhi B"),
        ("TEACHING & MENTORING",
         "Supervise students;\nteaching informed by research"),
        ("DEPARTMENT & COLLABORATION",
         "Active member of the\nfaculty community"),
        ("REGION & LONG-TERM",
         "A long-term anchor at\nYamaguchi University"),
    ]
    cx = Inches(0.75)
    cy2 = Inches(4.90)
    cw = Inches(2.95)
    ch = Inches(1.00)
    for i, (h, b) in enumerate(commits):
        x = cx + i * (cw + gap)
        add_rect(s, x, cy2, cw, ch, fill=None,
                 line=ACCENT, line_w=Pt(0.8))
        add_rect(s, x, cy2, Inches(0.06), ch, fill=ACCENT)
        add_text(s, x + Inches(0.2), cy2 + Inches(0.10),
                 cw - Inches(0.3), Inches(0.3),
                 h, size=10, bold=True, color=ACCENT)
        add_text(s, x + Inches(0.2), cy2 + Inches(0.40),
                 cw - Inches(0.3), Inches(0.55),
                 b, size=10, color=WHITE, italic=True,
                 line_spacing=1.35)

    # Powerful statement
    add_rect(s, Inches(0.75), Inches(6.20), Inches(12), Emu(25400),
             fill=ACCENT)
    add_text(s, Inches(0.75), Inches(6.35), Inches(12), Inches(0.55),
             "HIRAKU-Global is the multiplier — not the starter.",
             size=22, bold=True, color=WHITE)
    add_text(s, Inches(0.75), Inches(6.90), Inches(12), Inches(0.35),
             "Thank you very much.  I look forward to your questions.",
             size=11, bold=True, color=ACCENT)

    # Architectural corner marks
    corner_marks(s)

    add_notes(s, """[SLIDE 11 — CLOSING — ~25s]

To close.

Four foundations — already in motion. Quality. Bridge. Funding. Implementation.

And four commitments — research, teaching, collaboration, long-term anchor.

HIRAKU-Global is the multiplier — not the starter.

Thank you very much. I look forward to your questions.
""")


# ============================================================
# APPENDIX / BACKUP SLIDES (for 20-min Q&A — NOT part of 10-min talk)
# ============================================================
def appendix_chrome(slide, idx, total_app, title_text, subtitle):
    """Chrome for backup slides — visually distinct (gold band marked APPENDIX)"""
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill=WHITE)
    # Top band — gold to signal "backup, not main"
    add_rect(slide, 0, 0, SLIDE_W, Inches(0.18), fill=ACCENT_DEEP)
    add_rect(slide, 0, Inches(0.18), Inches(2.0), Emu(38100), fill=YU_INDIGO)
    add_text(slide, Inches(0.45), Inches(0.02), Inches(8), Inches(0.16),
             "APPENDIX  ·  BACKUP FOR Q&A  ·  NOT PART OF THE 10-MIN TALK",
             size=8, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(10.5), Inches(0.02), Inches(2.7), Inches(0.16),
             f"BACKUP  A{idx}  /  A{total_app}",
             size=8, bold=True, color=YU_INDIGO,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(0.45), Inches(0.38), Inches(8), Inches(0.30),
             "ORIGINAL APPLICATION FIGURE", size=10, bold=True,
             color=ACCENT_DEEP)
    add_text(slide, Inches(0.45), Inches(0.66), Inches(12.5), Inches(0.45),
             title_text, size=22, bold=True, color=YU_INDIGO,
             line_spacing=1.0)
    add_text(slide, Inches(0.45), Inches(1.18), Inches(12.5), Inches(0.30),
             subtitle, size=11, color=BODY, italic=True)
    corner_marks(slide)


def add_figure_fit(slide, img_path, x, y, max_w, max_h):
    """Place image scaled to fit inside box, centered, with thin frame"""
    with Image.open(img_path) as im:
        iw, ih = im.size
    ar = iw / ih
    box_ar = max_w / max_h
    if ar > box_ar:
        w = max_w
        h = int(max_w / ar)
    else:
        h = max_h
        w = int(max_h * ar)
    px = x + (max_w - w) // 2
    py = y + (max_h - h) // 2
    # Frame
    add_rect(slide, px - Emu(9525), py - Emu(9525),
             w + Emu(19050), h + Emu(19050),
             fill=None, line=ARCH_LINE, line_w=Pt(0.75))
    slide.shapes.add_picture(img_path, px, py, width=w, height=h)


def appendix_slide(idx, total_app, fig_file, title, subtitle, qa_hint, notes):
    s = prs.slides.add_slide(blank)
    appendix_chrome(s, idx, total_app, title, subtitle)
    # Figure area
    fig_path = os.path.join(FIG_DIR, fig_file)
    add_figure_fit(s, fig_path, Inches(0.6), Inches(1.65),
                   Inches(9.4), Inches(5.2))
    # Right rail — Q&A hint
    rx = Inches(10.25)
    add_rect(s, rx, Inches(1.65), Inches(2.65), Inches(5.2),
             fill=LIGHT_BG)
    add_rect(s, rx, Inches(1.65), Inches(2.65), Inches(0.45),
             fill=YU_INDIGO)
    add_text(s, rx + Inches(0.18), Inches(1.65), Inches(2.4), Inches(0.45),
             "IF ASKED ABOUT…", size=10, bold=True, color=ACCENT,
             anchor=MSO_ANCHOR.MIDDLE)
    yy = Inches(2.30)
    for line in qa_hint:
        add_rect(s, rx + Inches(0.18), yy + Inches(0.04),
                 Inches(0.08), Inches(0.08), fill=ACCENT)
        add_text(s, rx + Inches(0.38), yy, Inches(2.15), Inches(0.7),
                 line, size=10, color=DARK, line_spacing=1.25)
        yy += Inches(0.75)
    add_notes(s, notes)


APP_FIGS = [
    ("fig1_trajectory.png",
     "Research Trajectory & Academic Framework",
     "Figure 1 (application) — full Building → Person → City framework with key actions, methods, and significance.",
     ["My three research\nstages in detail",
      "Why each stage\nled to the next",
      "Specific methods\nper stage",
      "How Stage 3 leads\nto this project"],
     "[BACKUP A1 — Research Trajectory] Use if a reviewer asks for the detailed evolution of my research, the specific methods at each stage, or how the three stages connect. This is the full framework from my application; Slide 4 is its simplified version."),
    ("fig2_crossscale.png",
     "Cross-Scale Scientific Framework",
     "Figure 2 (application) — green-blue-wind mechanisms, three core scientific questions, technical pathway, and domain-specific knowledge model.",
     ["The 3 core\nscientific questions",
      "City / Block /\nHuman scale detail",
      "How the scales\nare integrated",
      "Expected academic\n& applied outcomes"],
     "[BACKUP A2 — Cross-Scale Framework] Use if a reviewer wants the scientific depth behind Slide 5 — the Q0/Q1/Q2 questions, the three analytical scales, and how they integrate into one knowledge model."),
    ("fig3_workflow.png",
     "Diagnostic Workflow & 5-Year Plan",
     "Figure 3 (application) — three-step sequential chain (screening → mechanism → validation) mapped onto the five-year HIRAKU timeline.",
     ["Year-by-year\ndeliverables",
      "The 3-step\nmethod chain",
      "Where UCL &\nZhejiang fit in",
      "Screening →\nvalidation logic"],
     "[BACKUP A3 — Workflow & Plan] Use if a reviewer probes feasibility or the year-by-year schedule. Shows the full screening-explanation-validation chain behind Slide 9."),
    ("fig4_collaboration.png",
     "International Collaboration Framework",
     "Figure 4 (application) — core project team at Yamaguchi with UCL and Zhejiang as primary nodes; US and Thailand as reserve expansion nodes.",
     ["Roles of UCL &\nZhejiang partners",
      "What each partner\ncontributes",
      "Reserve nodes\n(US, Thailand)",
      "How the network\ngrows cumulatively"],
     "[BACKUP A4 — Collaboration] Use if a reviewer asks for detail on partner roles, complementarity, or how the network expands. Expands the hub-and-spoke diagram on Slide 7."),
]


# ============================================================
# BUILD
# ============================================================
for fn in [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06,
           slide_07, slide_08, slide_09, slide_10, slide_11]:
    fn()

# Appendix slides
for i, (fig, title, sub, hint, notes) in enumerate(APP_FIGS, 1):
    appendix_slide(i, len(APP_FIGS), fig, title, sub, hint, notes)

out = "/home/user/academic-research-skills/interview_materials/HIRAKU_Global_Interview_Liu.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Slides: {len(prs.slides)}  |  Size: 16:9  ({prs.slide_width/914400:.3f} x {prs.slide_height/914400:.3f} in)")
