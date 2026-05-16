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
    add_text(s, Inches(0.75), Inches(3.45), Inches(12), Inches(0.6),
             "from Japanese Regional Cities to International Asia",
             size=18, color=RGBColor(0xB8, 0xC8, 0xDC), italic=True)

    # Name block (architectural style)
    nx = Inches(0.75)
    ny = Inches(4.50)
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

    # Stage legend
    leg_y = Inches(5.85)
    legends = [("STAGE 1  ·  BUILDING", YU_INDIGO_LT),
               ("STAGE 2  ·  PERSON", ACCENT),
               ("STAGE 3  ·  CITY", HEAT_HOT)]
    lx = Inches(0.75)
    for txt, col in legends:
        add_oval(s, lx, leg_y + Inches(0.05), Inches(0.18),
                 Inches(0.18), fill=col)
        add_text(s, lx + Inches(0.25), leg_y, Inches(3), Inches(0.3),
                 txt, size=9.5, bold=True, color=BODY,
                 anchor=MSO_ANCHOR.MIDDLE)
        lx += Inches(3.0)

    # Key claim band
    band_y = Inches(6.30)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.65),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.13), Inches(11.6), Inches(0.4),
             "ONE OF THE FEW RESEARCHERS WHO WORKS NATIVELY ACROSS JAPANESE REGIONAL CITIES",
             size=10, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.35), Inches(11.6), Inches(0.3),
             "and Chinese high-density urbanism — through one continuous research agenda on urban heat.",
             size=12, color=WHITE, italic=True)

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
         "183 households across 3 cities\nWindow-to-wall ratio optimization\nCFD wind environment",
         "C-6, C-7, C-11, D-3", icon_building),
        ("STAGE 02", "PERSON",
         "How do indoor conditions\naffect learning, health, behavior?",
         "Classroom thermal × learning\nPM2.5 health risk\nElderly spatial needs",
         "C-3 (Q1, Top 5), C-5 (Q1)", icon_person),
        ("STAGE 03", "CITY",
         "How do GBI, wind & morphology\nregulate pedestrian heat exposure?",
         "Satellite LST + Sentinel-2 LCZ\nKumamoto green-infra mapping\nMLIT EBPM-cited",
         "C-1, C-14, C-15, A-1", icon_city),
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

    # Bottom claim
    band_y = Inches(6.25)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.70),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.10), Inches(11.6), Inches(0.3),
             "RESEARCH  →  POLICY  →  NATIONAL RECOGNITION",
             size=10, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.35), Inches(11.6), Inches(0.35),
             "Few researchers combine satellite, measurement, CFD, and national-level policy adoption in one continuous workflow.",
             size=12, bold=True, color=WHITE)

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
                "Quality first. Continuity second. All Q1 led by me.")

    # Big number block (4 columns)
    nums = [
        ("15", "peer-reviewed\npapers"),
        ("10", "English\nSCI / SCIE"),
        ("8", "with Impact\nFactor"),
        ("3", "Q1 papers — all\n1st / co-1st / corresponding"),
    ]
    x0 = Inches(0.75)
    y0 = Inches(1.85)
    nw = Inches(3.02)
    nh = Inches(2.10)
    gap = Inches(0.10)
    for i, (num, lab) in enumerate(nums):
        x = x0 + i * (nw + gap)
        fill = YU_INDIGO if i == 3 else LIGHT_BG
        tc = WHITE if i == 3 else YU_INDIGO
        bc = ACCENT if i == 3 else BODY
        add_rect(s, x, y0, nw, nh, fill=fill)
        # number-line decoration
        add_rect(s, x + Inches(0.3), y0 + Inches(1.65),
                 Inches(0.4), Emu(38100), fill=ACCENT if i == 3 else YU_INDIGO)
        add_text(s, x, y0 + Inches(0.20), nw, Inches(1.30),
                 num, size=80, bold=True, color=tc,
                 align=PP_ALIGN.CENTER, line_spacing=1.0)
        add_text(s, x + Inches(0.3), y0 + Inches(1.75), nw - Inches(0.6),
                 Inches(0.5), lab, size=11, color=bc, line_spacing=1.3,
                 bold=(i == 3))

    # Q1 journals row
    section_label(s, Inches(0.75), Inches(4.20), Inches(12),
                  "Q1 JOURNALS  ·  ALL FIRST / CO-FIRST / CORRESPONDING AUTHOR")
    journals = [
        ("Building and Environment", "IF ≈ 7.1  ·  Q1",
         "TOP 5 IN FIELD  ·  Co-first author\nClassroom thermal × learning"),
        ("Environmental Pollution", "IF ≈ 7.3  ·  Q1",
         "Top-tier Environmental Science\nPM2.5 health-effects assessment"),
        ("Energies", "IF ≈ 3.1  ·  Q1",
         "First author\nClassroom comfort × learning efficiency"),
    ]
    jx0 = Inches(0.75)
    jy = Inches(4.70)
    jw = Inches(4.05)
    jh = Inches(1.50)
    for i, (jn, jq, jr) in enumerate(journals):
        x = jx0 + i * (jw + Inches(0.10))
        add_rect(s, x, jy, jw, jh, fill=WHITE, line=ARCH_LINE, line_w=Pt(0.6))
        add_rect(s, x, jy, Inches(0.07), jh, fill=ACCENT)
        add_text(s, x + Inches(0.25), jy + Inches(0.15),
                 jw - Inches(0.4), Inches(0.4),
                 jn, size=13, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.25), jy + Inches(0.55),
                 jw - Inches(0.4), Inches(0.30),
                 jq, size=10.5, bold=True, color=ACCENT_DEEP)
        add_text(s, x + Inches(0.25), jy + Inches(0.85),
                 jw - Inches(0.4), Inches(0.6),
                 jr, size=10.5, color=BODY, italic=True, line_spacing=1.35)

    # Bottom continuity line
    band_y = Inches(6.35)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.60),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.06), Inches(11.6),
             Inches(0.25), "RESEARCH LINE  ·  ONE CONTINUOUS AGENDA",
             size=9, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.30), Inches(11.6),
             Inches(0.30),
             "Building energy  →  Indoor comfort & learning  →  PM2.5 health  →  Urban heat & LULC  →  Green-blue infrastructure  →  Policy",
             size=11.5, bold=True, color=WHITE)

    add_notes(s, """[SLIDE 6 — RESEARCH OUTPUTS — ~50s]

Now my publications — quality first.

Fifteen peer-reviewed papers. Ten English SCI or SCIE. Eight with impact factor. Three in Q1 — and this is what I want you to remember: all three Q1 papers are first, co-first, or corresponding author. I led them.

The three Q1 journals — Building and Environment, in the top 5 of its field. Environmental Pollution, top-tier environmental science. And Energies.

What matters more than the journal count is the line that connects them — building energy, indoor comfort, PM2.5 health, urban heat, green infrastructure, policy. One continuous research agenda.
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

    # Future network diagram (bottom)
    nx = Inches(0.75)
    ny = Inches(5.25)
    nw = Inches(12.0)
    nh = Inches(1.5)
    add_rect(s, nx, ny, nw, nh, fill=LIGHTER, line=ARCH_LINE, line_w=Pt(0.5))
    section_label(s, nx + Inches(0.15), ny + Inches(0.10), Inches(8),
                  "FUTURE NETWORK  ·  BUILDING ON EXISTING FRIENDSHIP")

    # Central hub (Yamaguchi)
    cx = nx + nw / 2
    cy = ny + Inches(0.95)
    add_rect(s, cx - Inches(0.85), cy - Inches(0.2), Inches(1.7),
             Inches(0.4), fill=YU_INDIGO)
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

    # Bottom note
    add_text(s, Inches(0.75), Inches(6.95), Inches(12), Inches(0.25),
             "IN ALL THREE CASES — I WAS THE ORGANIZER, NOT JUST A PARTICIPANT.",
             size=11, bold=True, color=YU_INDIGO,
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

    # Bottom feasibility claim
    band_y = Inches(5.05)
    add_rect(s, Inches(0.75), band_y, Inches(12.0), Inches(0.85),
             fill=YU_INDIGO)
    add_text(s, Inches(0.95), band_y + Inches(0.13), Inches(11.6),
             Inches(0.30),
             "FEASIBILITY — ALREADY PROVEN",
             size=10, bold=True, color=ACCENT)
    add_text(s, Inches(0.95), band_y + Inches(0.40), Inches(11.6),
             Inches(0.40),
             "Satellite pipeline running (C-1, 2024)  ·  CFD methodology established (C-2, D-3)  ·  Partners aligned  ·  First Japanese grant won",
             size=12, bold=True, color=WHITE)

    # Bottom: Risk awareness
    section_label(s, Inches(0.75), Inches(6.10), Inches(8),
                  "RISK MANAGEMENT  ·  WHAT COULD GO WRONG, AND HOW I HANDLE IT")
    add_text(s, Inches(0.75), Inches(6.45), Inches(12),
             Inches(0.6),
             "Anchor Yamaguchi as the primary case  ·  expand stepwise to Ube and Matsue  ·  "
             "online collaboration if travel is constrained  ·  Kumamoto baseline retained as pre-validated reference.",
             size=11, color=BODY, italic=True, line_spacing=1.4)

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
                "During HIRAKU-Global, and after tenure — a long-term anchor.")

    # Left: During HIRAKU - 3I framework alignment
    lx = Inches(0.75)
    ly = Inches(1.85)
    section_label(s, lx, ly, Inches(6.0),
                  "DURING HIRAKU-GLOBAL  ·  ALIGNED WITH THE 3I FRAMEWORK")

    rows = [
        ("INNOVATIVE",
         "Cross-scale wind × GBI ×\npedestrian-heat mechanism paper",
         "Reproducible city-to-corridor\ndiagnostic workflow"),
        ("INFLUENTIAL",
         "Continued Q1 publications\nthrough the HIRAKU period",
         "Kakenhi Kiban C (FY2026)\n→ Kiban B target"),
        ("IMPACTFUL",
         "Deliver outputs to Yamaguchi,\nUbe, Matsue municipalities",
         "Continue MLIT EBPM-aligned\npolicy translation"),
    ]
    ry = ly + Inches(0.42)
    rh = Inches(0.95)
    for i, (lab, d1, d2) in enumerate(rows):
        y = ry + i * (rh + Inches(0.08))
        # Tag
        add_rect(s, lx, y, Inches(1.5), rh, fill=YU_INDIGO)
        add_text(s, lx, y, Inches(1.5), rh, lab,
                 size=11, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_rect(s, lx + Inches(1.55), y, Inches(2.20), rh,
                 fill=WHITE, line=ARCH_LINE, line_w=Pt(0.5))
        add_text(s, lx + Inches(1.70), y, Inches(2.05), rh, d1,
                 size=10, color=DARK, anchor=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.3)
        add_rect(s, lx + Inches(3.80), y, Inches(2.20), rh,
                 fill=WHITE, line=ARCH_LINE, line_w=Pt(0.5))
        add_text(s, lx + Inches(3.95), y, Inches(2.05), rh, d2,
                 size=10, color=DARK, anchor=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.3)

    # Right: Post-tenure — concentric expansion + anchors
    rx = Inches(7.20)
    ry2 = Inches(1.85)
    section_label(s, rx, ry2, Inches(5.7),
                  "POST-TENURE  ·  LONG-TERM ANCHOR  ·  LOCAL-TO-GLOBAL")

    rings = [
        ("LAB",      "Stable group at Yamaguchi U."),
        ("REGION",   "Chugoku-Shikoku heat toolkit"),
        ("W. JAPAN", "Urban-thermal research hub"),
        ("ASIA",     "EU · China · SE Asia platform"),
        ("GLOBAL",   "Local-to-Global model export"),
    ]
    ry3 = ry2 + Inches(0.42)
    rh2 = Inches(0.55)
    for i, (n, d) in enumerate(rings):
        y = ry3 + i * (rh2 + Inches(0.02))
        indent = Inches(i * 0.12)
        add_rect(s, rx + indent, y, Inches(0.45), rh2,
                 fill=YU_INDIGO)
        add_text(s, rx + indent, y, Inches(0.45), rh2,
                 str(i + 1), size=14, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_rect(s, rx + indent + Inches(0.5), y, Inches(1.50), rh2,
                 fill=LIGHT_BG)
        add_text(s, rx + indent + Inches(0.60), y, Inches(1.40), rh2,
                 n, size=11, bold=True, color=YU_INDIGO,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, rx + indent + Inches(2.05), y, Inches(3.6), rh2,
                 d, size=10, color=BODY, italic=True,
                 anchor=MSO_ANCHOR.MIDDLE)

    # Bottom: WHAT I GIVE BACK
    band_y = Inches(5.30)
    section_label(s, Inches(0.75), band_y, Inches(12),
                  "WHAT I GIVE BACK  ·  ACTIVE MEMBER, NOT ONLY RECIPIENT")

    gives = [
        ("INTERNATIONAL WORKSHOP",
         "Year 4 at Yamaguchi University\nUrban thermal × GBI × climate adaptation"),
        ("CHINA-JAPAN BRIDGE",
         "Annual seminar · academic translation\nFieldwork & collaboration support"),
        ("TEACHING & MENTORING",
         "Graduate supervision\nCross-discipline seminars"),
        ("DEPT. & REGION SERVICE",
         "Active in faculty collaboration\nSupport to Chugoku-Shikoku cities"),
    ]
    gy = Inches(5.75)
    gx0 = Inches(0.75)
    gw = Inches(2.97)
    gh2 = Inches(1.05)
    gap = Inches(0.08)
    for i, (h, b) in enumerate(gives):
        x = gx0 + i * (gw + gap)
        add_rect(s, x, gy, gw, gh2, fill=WHITE, line=ACCENT, line_w=Pt(0.8))
        add_rect(s, x, gy, Inches(0.06), gh2, fill=ACCENT)
        add_text(s, x + Inches(0.2), gy + Inches(0.10),
                 gw - Inches(0.3), Inches(0.30),
                 h, size=10.5, bold=True, color=YU_INDIGO)
        add_text(s, x + Inches(0.2), gy + Inches(0.42),
                 gw - Inches(0.3), Inches(0.6),
                 b, size=9.5, color=BODY, italic=True, line_spacing=1.35)

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
# BUILD
# ============================================================
for fn in [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06,
           slide_07, slide_08, slide_09, slide_10, slide_11]:
    fn()

out = "/home/user/academic-research-skills/interview_materials/HIRAKU_Global_Interview_Liu.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Slides: {len(prs.slides)}  |  Size: 16:9  ({prs.slide_width/914400:.3f} x {prs.slide_height/914400:.3f} in)")
