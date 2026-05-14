"""
HIRAKU-Global Round 7 Interview Presentation Builder
Style: Academic high-end minimalist | 16:9 widescreen | 1920x1080+ export
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from copy import deepcopy
from lxml import etree

# ============== DESIGN SYSTEM ==============
PRIMARY      = RGBColor(0x0A, 0x25, 0x40)   # Deep navy
SECONDARY    = RGBColor(0x2A, 0x5F, 0x8F)   # Mid blue
ACCENT       = RGBColor(0xC9, 0xA9, 0x61)   # Warm gold
ACCENT_DEEP  = RGBColor(0xA8, 0x86, 0x3F)   # Deep gold
DARK         = RGBColor(0x1A, 0x1A, 0x1A)
BODY         = RGBColor(0x4A, 0x55, 0x68)
MUTED        = RGBColor(0x9A, 0xA5, 0xB1)
LIGHT_BG     = RGBColor(0xF7, 0xFA, 0xFC)
LINE_GRAY    = RGBColor(0xE5, 0xE7, 0xEB)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)

FONT_EN = "Calibri"
FONT_HEAD = "Calibri"  # use a clean sans-serif

# ============== PRESENTATION ==============
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height
blank_layout = prs.slide_layouts[6]


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


def add_line(slide, x1, y1, x2, y2, color=PRIMARY, weight=1.5):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(weight)
    return line


def add_text(slide, x, y, w, h, text, size=18, bold=False, color=DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT_EN,
             italic=False, line_spacing=1.15):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    # Handle multi-line text
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


def add_rich_text(slide, x, y, w, h, segments, align=PP_ALIGN.LEFT,
                  anchor=MSO_ANCHOR.TOP, line_spacing=1.2):
    """segments: list of (text, size, bold, color) or 'NEWLINE'"""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for m in ['margin_left', 'margin_right', 'margin_top', 'margin_bottom']:
        setattr(tf, m, 0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for seg in segments:
        if seg == 'NEWLINE':
            p = tf.add_paragraph()
            p.alignment = align
            p.line_spacing = line_spacing
            continue
        text, size, bold, color = seg
        run = p.add_run()
        run.text = text
        run.font.name = FONT_EN
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
    return tb


def slide_frame(slide, page_num, total, section_tag, slide_title=None):
    """Standard page chrome: top accent line, page number, section tag"""
    # Background
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill=WHITE)
    # Top accent thin bar
    add_rect(slide, 0, 0, SLIDE_W, Inches(0.08), fill=PRIMARY)
    # Top secondary thin gold line
    add_rect(slide, 0, Inches(0.08), Inches(2.2), Inches(0.04), fill=ACCENT)
    # Bottom footer line
    add_rect(slide, Inches(0.6), Inches(7.15), Inches(12.13), Emu(9525),
             fill=LINE_GRAY)
    # Page number
    add_text(slide, Inches(11.8), Inches(7.22), Inches(1.2), Inches(0.3),
             f"{page_num:02d} / {total:02d}", size=10, color=MUTED,
             align=PP_ALIGN.RIGHT)
    # Section tag (bottom-left)
    add_text(slide, Inches(0.6), Inches(7.22), Inches(8), Inches(0.3),
             f"HIRAKU-Global  ·  7th Cohort Interview  ·  LIU Haiqiang",
             size=10, color=MUTED)
    # Slide title strip
    if slide_title:
        add_text(slide, Inches(0.6), Inches(0.35), Inches(11), Inches(0.5),
                 slide_title, size=12, bold=True, color=ACCENT_DEEP,
                 font=FONT_HEAD)


# ============== SLIDE 1 — TITLE ==============
def slide_01():
    s = prs.slides.add_slide(blank_layout)
    # Full bleed dark background
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, fill=PRIMARY)
    # Decorative gold lines
    add_rect(s, Inches(0.8), Inches(2.4), Inches(0.6), Inches(0.04), fill=ACCENT)
    # Main title
    add_text(s, Inches(0.8), Inches(2.55), Inches(11), Inches(1.2),
             "Bridging Cities, Climate, and People",
             size=44, bold=True, color=WHITE, line_spacing=1.0)
    add_text(s, Inches(0.8), Inches(3.5), Inches(11), Inches(0.8),
             "Urban Thermal Environment Research from Local Japan to Global Asia",
             size=22, color=RGBColor(0xCB, 0xD5, 0xE0))
    # Divider
    add_rect(s, Inches(0.8), Inches(4.55), Inches(2.2), Emu(9525), fill=ACCENT)
    # Name + position
    add_text(s, Inches(0.8), Inches(4.75), Inches(11), Inches(0.5),
             "LIU  HAIQIANG, Ph.D.",
             size=20, bold=True, color=WHITE, font=FONT_HEAD)
    add_text(s, Inches(0.8), Inches(5.20), Inches(11), Inches(0.4),
             "Lecturer (Tenure-track)  ·  Graduate School of Sciences and Technology for Innovation",
             size=14, color=RGBColor(0xCB, 0xD5, 0xE0))
    add_text(s, Inches(0.8), Inches(5.50), Inches(11), Inches(0.4),
             "Yamaguchi University",
             size=14, color=RGBColor(0xCB, 0xD5, 0xE0))
    # Keyword chips at bottom
    chips = ["Urban Thermal Environment", "International Collaboration",
             "Regional Policy", "Social Implementation"]
    x0 = Inches(0.8)
    y_chip = Inches(6.35)
    for chip in chips:
        w = Inches(2.7)
        add_rect(s, x0, y_chip, w, Inches(0.42),
                 fill=None, line=ACCENT, line_w=Pt(0.75))
        add_text(s, x0, y_chip, w, Inches(0.42), chip,
                 size=11, bold=True, color=ACCENT, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
        x0 += w + Inches(0.15)
    # Bottom corner: HIRAKU mark
    add_text(s, Inches(0.8), Inches(7.0), Inches(11.8), Inches(0.3),
             "HIRAKU-Global  ·  7th Cohort Interview  ·  2026",
             size=9, color=RGBColor(0x88, 0x95, 0xA8))


# ============== SLIDE 2 — Why my research matters ==============
def slide_02():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 2, 10, "02", "WHY MY RESEARCH MATTERS")
    # Big claim
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "Global climate change becomes local — on every street.",
             size=32, bold=True, color=PRIMARY, line_spacing=1.05)
    add_text(s, Inches(0.6), Inches(1.85), Inches(12), Inches(0.5),
             "Heat ↘  walkability ↘  urban vitality.  Regional aging cities face this triple challenge most strongly.",
             size=15, color=BODY)

    # Three tiers
    tiers = [
        ("GLOBAL", "Climate change + urban warming",
         "A worldwide challenge\nwith very local impact"),
        ("CITY", "Walkability & vitality",
         "Heat empties streets;\nempty streets weaken cities"),
        ("PEOPLE", "Elderly, students, commuters",
         "Different streets carry\nvery different heat risks"),
    ]
    x0 = Inches(0.6)
    y0 = Inches(2.95)
    box_w = Inches(4.05)
    box_h = Inches(2.4)
    for i, (tag, head, body_t) in enumerate(tiers):
        x = x0 + i * (box_w + Inches(0.13))
        add_rect(s, x, y0, box_w, box_h, fill=LIGHT_BG)
        add_rect(s, x, y0, Inches(0.08), box_h, fill=ACCENT)
        add_text(s, x + Inches(0.3), y0 + Inches(0.25), box_w - Inches(0.5),
                 Inches(0.35), tag, size=11, bold=True, color=ACCENT_DEEP)
        add_text(s, x + Inches(0.3), y0 + Inches(0.65), box_w - Inches(0.5),
                 Inches(0.7), head, size=18, bold=True, color=PRIMARY,
                 line_spacing=1.1)
        add_text(s, x + Inches(0.3), y0 + Inches(1.45), box_w - Inches(0.5),
                 Inches(0.9), body_t, size=13, color=BODY, line_spacing=1.3)

    # Three questions footer
    add_text(s, Inches(0.6), Inches(5.65), Inches(12), Inches(0.4),
             "MY THREE QUESTIONS", size=11, bold=True, color=ACCENT_DEEP)
    y_q = Inches(6.0)
    qs = [("WHERE", "is it hot?"), ("WHY", "is it hot?"),
          ("HOW", "to cool & re-vitalize the city?")]
    qx = Inches(0.6)
    qw = Inches(4.05)
    for i, (k, v) in enumerate(qs):
        x = qx + i * (qw + Inches(0.13))
        add_text(s, x, y_q, qw, Inches(0.5), k, size=22, bold=True,
                 color=PRIMARY)
        add_text(s, x + Inches(1.4), y_q + Inches(0.08), qw - Inches(1.4),
                 Inches(0.5), v, size=15, color=BODY)


# ============== SLIDE 3 — Originality ==============
def slide_03():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 3, 10, "03", "ORIGINALITY OF MY RESEARCH")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "I do not only measure heat — I diagnose it, and the diagnosis is already used.",
             size=28, bold=True, color=PRIMARY, line_spacing=1.05)

    # Four originality cards
    cards = [
        ("01", "MULTI-SOURCE DATA",
         "Satellite remote sensing\n(Landsat-8/9, Sentinel-2)\n+ on-site measurement + CFD"),
        ("02", "CUMULATIVE HEAT EXPOSURE",
         "Beyond instantaneous T:\nevaluate pedestrian\nheat retention zones"),
        ("03", "POLICY-APPLIED",
         "Applied to Kumamoto City's\ngreen-infrastructure policy\n(LST × land-cover map)"),
        ("04", "NATIONAL RECOGNITION",
         "Referenced by MLIT\nas an EBPM\nevaluation case"),
    ]
    x0 = Inches(0.6)
    y0 = Inches(2.25)
    cw = Inches(3.02)
    ch = Inches(3.05)
    gap = Inches(0.07)
    for i, (num, head, body_t) in enumerate(cards):
        x = x0 + i * (cw + gap)
        # Card body
        add_rect(s, x, y0, cw, ch, fill=WHITE, line=LINE_GRAY, line_w=Pt(0.5))
        # Top accent strip
        add_rect(s, x, y0, cw, Inches(0.45), fill=PRIMARY)
        add_text(s, x + Inches(0.25), y0, Inches(0.8), Inches(0.45),
                 num, size=13, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        # Headline
        add_text(s, x + Inches(0.25), y0 + Inches(0.75), cw - Inches(0.5),
                 Inches(0.75), head, size=14, bold=True, color=PRIMARY,
                 line_spacing=1.15)
        # Body
        add_text(s, x + Inches(0.25), y0 + Inches(1.55), cw - Inches(0.5),
                 Inches(1.4), body_t, size=12, color=BODY, line_spacing=1.4)

    # Bottom strong claim band
    band_y = Inches(5.70)
    add_rect(s, Inches(0.6), band_y, Inches(12.13), Inches(1.0),
             fill=PRIMARY)
    add_text(s, Inches(0.85), band_y + Inches(0.18), Inches(11.5), Inches(0.4),
             "RESEARCH  →  POLICY  →  NATIONAL RECOGNITION",
             size=12, bold=True, color=ACCENT)
    add_text(s, Inches(0.85), band_y + Inches(0.50), Inches(11.5), Inches(0.5),
             "Few researchers combine satellite, measurement, CFD, and national-level policy adoption in one workflow.",
             size=15, bold=True, color=WHITE)


# ============== SLIDE 4 — Research outputs ==============
def slide_04():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 4, 10, "04", "RESEARCH OUTPUTS  ·  QUALITY & CONTINUITY")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "Quality first.  Continuity second.  Volume third.",
             size=28, bold=True, color=PRIMARY, line_spacing=1.05)

    # Big number block
    nums = [
        ("15", "peer-reviewed\npapers"),
        ("10", "English\nSCI/SCIE"),
        ("8", "with Impact\nFactor"),
        ("3", "Q1 papers — all\n1st / corresponding"),
    ]
    x0 = Inches(0.6)
    y0 = Inches(2.20)
    nw = Inches(3.02)
    nh = Inches(2.0)
    gap = Inches(0.07)
    for i, (num, lab) in enumerate(nums):
        x = x0 + i * (nw + gap)
        fill = PRIMARY if i == 3 else LIGHT_BG
        text_c = WHITE if i == 3 else PRIMARY
        body_c = ACCENT if i == 3 else BODY
        add_rect(s, x, y0, nw, nh, fill=fill)
        add_text(s, x, y0 + Inches(0.2), nw, Inches(1.1), num,
                 size=72, bold=True, color=text_c, align=PP_ALIGN.CENTER,
                 line_spacing=1.0)
        add_text(s, x, y0 + Inches(1.35), nw, Inches(0.6), lab,
                 size=12, color=body_c, align=PP_ALIGN.CENTER,
                 line_spacing=1.3, bold=(i == 3))

    # Q1 journals row
    add_text(s, Inches(0.6), Inches(4.50), Inches(12), Inches(0.4),
             "Q1 JOURNALS — ALL FIRST / CO-FIRST / CORRESPONDING AUTHOR",
             size=11, bold=True, color=ACCENT_DEEP)
    journals = [
        ("Building and Environment", "IF ≈ 7.1  ·  Q1", "Top 5 in field  ·  Co-first author"),
        ("Environmental Pollution", "IF ≈ 7.3  ·  Q1", "Top-tier Env. Science"),
        ("Energies", "IF ≈ 3.1  ·  Q1", "First author"),
    ]
    jx = Inches(0.6)
    jy = Inches(4.95)
    jw = Inches(4.05)
    jh = Inches(1.30)
    for i, (jn, jq, jr) in enumerate(journals):
        x = jx + i * (jw + Inches(0.13))
        add_rect(s, x, jy, jw, jh, fill=WHITE, line=ACCENT, line_w=Pt(0.75))
        add_rect(s, x, jy, Inches(0.07), jh, fill=ACCENT)
        add_text(s, x + Inches(0.25), jy + Inches(0.15), jw - Inches(0.4),
                 Inches(0.45), jn, size=14, bold=True, color=PRIMARY)
        add_text(s, x + Inches(0.25), jy + Inches(0.60), jw - Inches(0.4),
                 Inches(0.35), jq, size=11, color=ACCENT_DEEP, bold=True)
        add_text(s, x + Inches(0.25), jy + Inches(0.92), jw - Inches(0.4),
                 Inches(0.35), jr, size=11, color=BODY, italic=True)

    # Bottom continuity line
    add_text(s, Inches(0.6), Inches(6.45), Inches(12), Inches(0.4),
             "RESEARCH LINE", size=10, bold=True, color=ACCENT_DEEP)
    add_text(s, Inches(0.6), Inches(6.78), Inches(12), Inches(0.4),
             "Building energy  →  Indoor comfort & learning  →  Urban heat & LULC  →  Green-blue infrastructure  →  Pedestrian heat & policy",
             size=13, color=PRIMARY, bold=True)


# ============== SLIDE 5 — International Collaboration ==============
def slide_05():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 5, 10, "05", "INTERNATIONAL COLLABORATION  ·  ORGANIZER, NOT JUST PARTICIPANT")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "Three concrete records of organizing international cooperation.",
             size=28, bold=True, color=PRIMARY, line_spacing=1.05)

    # Three records
    records = [
        ("01", "Sakura Science Program",
         "Organized ZSTU × Japanese\nuniversities student-researcher\nexchanges multiple times",
         "Sustained partnership\n(paused by COVID, friendship intact)"),
        ("02", "Zhejiang Carbon-Neutral Center",
         "Built the Zhejiang International\nCo-op Center on Carbon Neutrality\nas ZSTU representative",
         "1 of 4 provincial centers\n— ZSTU as core unit"),
        ("03", "5-Country Online Forum",
         "Organized international forum:\nChina · Japan · UK (UCL) ·\nIndonesia · Bangladesh",
         "Multi-country coordination\nunder COVID restrictions"),
    ]
    x0 = Inches(0.6)
    y0 = Inches(2.25)
    cw = Inches(4.05)
    ch = Inches(3.4)
    gap = Inches(0.13)
    for i, (num, head, body_t, footer) in enumerate(records):
        x = x0 + i * (cw + gap)
        add_rect(s, x, y0, cw, ch, fill=WHITE, line=LINE_GRAY, line_w=Pt(0.75))
        add_rect(s, x, y0, cw, Inches(0.5), fill=PRIMARY)
        add_text(s, x + Inches(0.3), y0, Inches(1.0), Inches(0.5),
                 num, size=14, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.3), y0 + Inches(0.75), cw - Inches(0.6),
                 Inches(0.6), head, size=16, bold=True, color=PRIMARY,
                 line_spacing=1.15)
        add_text(s, x + Inches(0.3), y0 + Inches(1.50), cw - Inches(0.6),
                 Inches(1.2), body_t, size=12.5, color=BODY, line_spacing=1.4)
        # Footer line
        add_rect(s, x + Inches(0.3), y0 + Inches(2.75), cw - Inches(0.6),
                 Emu(6350), fill=ACCENT)
        add_text(s, x + Inches(0.3), y0 + Inches(2.85), cw - Inches(0.6),
                 Inches(0.5), footer, size=11, color=ACCENT_DEEP, italic=True,
                 line_spacing=1.3)

    # Bottom future network band
    band_y = Inches(5.95)
    add_rect(s, Inches(0.6), band_y, Inches(12.13), Inches(0.85),
             fill=PRIMARY)
    add_text(s, Inches(0.85), band_y + Inches(0.12), Inches(11.5), Inches(0.35),
             "FUTURE NETWORK · BUILT ON EXISTING FRIENDSHIP",
             size=11, bold=True, color=ACCENT)
    add_text(s, Inches(0.85), band_y + Inches(0.42), Inches(11.5), Inches(0.4),
             "Yamaguchi U.  ↔  UCL (Dr. Huanfa Chen)  ↔  Zhejiang U. (Prof. Jian Ge)  ↔  ZSTU  ↔  Shanghai / Indonesia / Bangladesh nodes",
             size=13, bold=True, color=WHITE)


# ============== SLIDE 6 — Funding ==============
def slide_06():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 6, 10, "06", "FUNDING & PROJECT LEADERSHIP")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "Approximately 100 million yen — and the Japan pattern has already started.",
             size=27, bold=True, color=PRIMARY, line_spacing=1.05)

    # Three-phase timeline
    phases = [
        ("CHINA  2018–2023",
         "≈ 100 M JPY",
         "Across 8 projects ·  5 as Leading Researcher\nNational Social Science Fund (collaborator)\nHigh-competition environment",
         PRIMARY, WHITE, ACCENT),
        ("KUMAMOTO  2023–2025",
         "Municipal post",
         "Institutional rule:\nexternal competitive grants\nnot permitted\n→ but produced MLIT EBPM-cited outputs",
         LIGHT_BG, PRIMARY, ACCENT_DEEP),
        ("YAMAGUCHI  since Jan 2026",
         "# 1  /  13",
         "Ranked #1 of 13 applicants\nin Yamaguchi U. regional research\n(4 selected) — within months of joining",
         PRIMARY, WHITE, ACCENT),
    ]
    x0 = Inches(0.6)
    y0 = Inches(2.25)
    pw = Inches(4.05)
    ph = Inches(3.7)
    gap = Inches(0.13)
    for i, (head, big, body_t, bg, hc, accent_c) in enumerate(phases):
        x = x0 + i * (pw + gap)
        add_rect(s, x, y0, pw, ph, fill=bg)
        # Top tag
        add_text(s, x + Inches(0.3), y0 + Inches(0.3), pw - Inches(0.6),
                 Inches(0.4), head, size=11, bold=True, color=accent_c)
        # Big figure
        add_text(s, x + Inches(0.3), y0 + Inches(0.85), pw - Inches(0.6),
                 Inches(1.3), big, size=42, bold=True, color=hc,
                 line_spacing=1.0)
        # Divider
        add_rect(s, x + Inches(0.3), y0 + Inches(2.20),
                 Inches(0.8), Emu(9525), fill=accent_c)
        # Body
        add_text(s, x + Inches(0.3), y0 + Inches(2.40), pw - Inches(0.6),
                 Inches(1.2), body_t, size=12, color=hc, line_spacing=1.4)

    # Forward-looking strip
    fy = Inches(6.20)
    add_rect(s, Inches(0.6), fy, Inches(12.13), Inches(0.7),
             fill=None, line=ACCENT, line_w=Pt(1.0))
    add_text(s, Inches(0.85), fy + Inches(0.18), Inches(11.5), Inches(0.4),
             "NEXT  →  Kakenhi Kiban C  (FY2026 autumn)  →  Kiban B  during HIRAKU-Global",
             size=14, bold=True, color=PRIMARY)


# ============== SLIDE 7 — Plan & International Development ==============
def slide_07():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 7, 10, "07", "RESEARCH PLAN  ·  FEASIBILITY & INTERNATIONAL DEVELOPMENT")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "Not starting from zero.  Pipeline running, partners ready, first grant won.",
             size=26, bold=True, color=PRIMARY, line_spacing=1.05)

    # Left column: 3 cities × 3 wind regimes
    add_text(s, Inches(0.6), Inches(2.05), Inches(6), Inches(0.4),
             "3 CITIES  ×  3 WIND REGIMES", size=12, bold=True,
             color=ACCENT_DEEP)
    cities = [
        ("YAMAGUCHI", "Inland basin"),
        ("UBE", "Coastal sea-breeze"),
        ("MATSUE", "Sea-of-Japan lakeside"),
    ]
    cy = Inches(2.50)
    for i, (cn, cd) in enumerate(cities):
        y = cy + i * Inches(0.85)
        add_rect(s, Inches(0.6), y, Inches(0.06), Inches(0.65), fill=ACCENT)
        add_text(s, Inches(0.85), y, Inches(2.5), Inches(0.4),
                 cn, size=18, bold=True, color=PRIMARY)
        add_text(s, Inches(0.85), y + Inches(0.40), Inches(5), Inches(0.3),
                 cd, size=13, color=BODY, italic=True)

    # Middle column: 3-step method chain
    mx = Inches(5.30)
    add_text(s, mx, Inches(2.05), Inches(4), Inches(0.4),
             "METHOD CHAIN  ·  CITY-TO-CORRIDOR", size=12, bold=True,
             color=ACCENT_DEEP)
    steps = [
        ("STEP 1", "Satellite diagnosis",
         "Landsat-8/9 LST × Sentinel-2 LCZ"),
        ("STEP 2", "Block-scale CFD",
         "OpenFOAM wind × morphology × GBI"),
        ("STEP 3", "Pedestrian validation",
         "WBGT along elderly walking corridors"),
    ]
    sy = Inches(2.50)
    for i, (st, sh, sb) in enumerate(steps):
        y = sy + i * Inches(0.85)
        add_rect(s, mx, y, Inches(0.6), Inches(0.65), fill=PRIMARY)
        add_text(s, mx, y, Inches(0.6), Inches(0.65),
                 st.split()[1], size=18, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, mx + Inches(0.75), y, Inches(3.5), Inches(0.4),
                 sh, size=15, bold=True, color=PRIMARY)
        add_text(s, mx + Inches(0.75), y + Inches(0.40), Inches(3.5),
                 Inches(0.35), sb, size=11, color=BODY, italic=True)

    # Right column: international partners
    rx = Inches(9.7)
    add_text(s, rx, Inches(2.05), Inches(4), Inches(0.4),
             "PARTNERS  ·  ALREADY ON BOARD", size=12, bold=True,
             color=ACCENT_DEEP)
    partners = [
        ("UCL", "Dr. Huanfa Chen", "2-month stay  ·  Year 2"),
        ("Zhejiang U.", "Prof. Jian Ge", "Short visit  ·  Year 3"),
        ("Sakura net & 5-country forum",
         "Indonesia · Bangladesh · UCL",
         "Reactivation as expansion nodes"),
    ]
    py = Inches(2.50)
    for i, (pa, pn, pd) in enumerate(partners):
        y = py + i * Inches(0.85)
        add_rect(s, rx, y, Inches(0.06), Inches(0.65), fill=ACCENT)
        add_text(s, rx + Inches(0.2), y, Inches(3.5), Inches(0.4),
                 pa, size=14, bold=True, color=PRIMARY, line_spacing=1.05)
        add_text(s, rx + Inches(0.2), y + Inches(0.40), Inches(3.5),
                 Inches(0.35), f"{pn}   ·   {pd}", size=10.5,
                 color=BODY, italic=True)

    # Bottom strong claim
    band_y = Inches(5.85)
    add_rect(s, Inches(0.6), band_y, Inches(12.13), Inches(1.0),
             fill=PRIMARY)
    add_text(s, Inches(0.85), band_y + Inches(0.18), Inches(11.5), Inches(0.4),
             "FEASIBILITY — ALREADY PROVEN",
             size=12, bold=True, color=ACCENT)
    add_text(s, Inches(0.85), band_y + Inches(0.50), Inches(11.5), Inches(0.5),
             "Satellite pipeline running (C-1, 2024)  ·  CFD methodology established  ·  Partners aligned  ·  First Japanese grant won",
             size=13, bold=True, color=WHITE)


# ============== SLIDE 8 — Aspirations DURING HIRAKU ==============
def slide_08():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 8, 10, "08", "DURING HIRAKU-GLOBAL  ·  MEET & EXCEED THE 3I GOAL")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "Aligning my action plan with HIRAKU-Global's 3I framework.",
             size=27, bold=True, color=PRIMARY, line_spacing=1.05)

    # 3I framework header
    add_text(s, Inches(0.6), Inches(2.05), Inches(12), Inches(0.4),
             "HIRAKU-GLOBAL  3I  FRAMEWORK   →   MY DELIVERABLES",
             size=11, bold=True, color=ACCENT_DEEP)

    rows = [
        ("INNOVATIVE",
         "Cross-scale wind × GBI × pedestrian-heat mechanism paper",
         "Reproducible city-to-corridor diagnostic workflow"),
        ("INFLUENTIAL",
         "Continued Q1 publications during HIRAKU period",
         "Kakenhi Kiban C (FY2026)  →  Kiban B"),
        ("IMPACTFUL",
         "Deliver outputs to Yamaguchi, Ube, Matsue municipalities",
         "Continue MLIT EBPM-aligned policy translation"),
    ]
    rx = Inches(0.6)
    ry = Inches(2.50)
    rh = Inches(0.95)
    for i, (lab, d1, d2) in enumerate(rows):
        y = ry + i * (rh + Inches(0.10))
        # Tag block
        add_rect(s, rx, y, Inches(2.4), rh, fill=PRIMARY)
        add_text(s, rx, y, Inches(2.4), rh, lab, size=15, bold=True,
                 color=ACCENT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # Deliverable 1
        add_rect(s, rx + Inches(2.5), y, Inches(5.0), rh,
                 fill=WHITE, line=LINE_GRAY, line_w=Pt(0.5))
        add_text(s, rx + Inches(2.65), y, Inches(4.8), rh, d1,
                 size=12, color=DARK, anchor=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.3)
        # Deliverable 2
        add_rect(s, rx + Inches(7.6), y, Inches(5.13), rh,
                 fill=WHITE, line=LINE_GRAY, line_w=Pt(0.5))
        add_text(s, rx + Inches(7.75), y, Inches(4.9), rh, d2,
                 size=12, color=DARK, anchor=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.3)

    # Give-back band
    gy = Inches(5.70)
    add_text(s, Inches(0.6), gy, Inches(12), Inches(0.4),
             "WHAT I GIVE BACK  ·  ACTIVE MEMBER, NOT ONLY RECIPIENT",
             size=11, bold=True, color=ACCENT_DEEP)
    gives = [
        ("Year-4 international workshop",
         "Urban thermal × GBI × climate adaptation"),
        ("China–Japan bridging",
         "Annual seminar · translation · fieldwork support"),
        ("Cross-discipline seminars",
         "Cross-scale analysis · translational research"),
    ]
    gx = Inches(0.6)
    gy2 = Inches(6.15)
    gw = Inches(4.05)
    for i, (gh, gb) in enumerate(gives):
        x = gx + i * (gw + Inches(0.13))
        add_rect(s, x, gy2, Inches(0.06), Inches(0.8), fill=ACCENT)
        add_text(s, x + Inches(0.2), gy2, gw - Inches(0.2), Inches(0.4),
                 gh, size=13, bold=True, color=PRIMARY)
        add_text(s, x + Inches(0.2), gy2 + Inches(0.42), gw - Inches(0.2),
                 Inches(0.4), gb, size=11, color=BODY, italic=True)


# ============== SLIDE 9 — After tenure ==============
def slide_09():
    s = prs.slides.add_slide(blank_layout)
    slide_frame(s, 9, 10, "09", "POST-TENURE  ·  LONG-TERM VISION & LEADERSHIP")
    add_text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(1.0),
             "A long-term anchor — not a short-term passenger.",
             size=28, bold=True, color=PRIMARY, line_spacing=1.05)

    # Concentric expansion (left side)
    add_text(s, Inches(0.6), Inches(2.0), Inches(6), Inches(0.4),
             "LOCAL-TO-GLOBAL  ·  EXPANDING IMPACT", size=11,
             bold=True, color=ACCENT_DEEP)
    rings = [
        ("Lab", "Stable research group at Yamaguchi U."),
        ("Region", "Chugoku-Shikoku heat-adaptation toolkit"),
        ("Western Japan", "Urban-thermal research hub"),
        ("Asia", "Comparative platform: EU · China · SE Asia"),
        ("Global", "Local-to-Global model for aging climate cities"),
    ]
    rx = Inches(0.6)
    ry = Inches(2.55)
    for i, (rn, rd) in enumerate(rings):
        y = ry + i * Inches(0.62)
        # Indent progressively
        indent = Inches(i * 0.18)
        add_rect(s, rx + indent, y + Inches(0.10), Inches(0.35),
                 Inches(0.35), fill=PRIMARY)
        add_text(s, rx + indent, y + Inches(0.10), Inches(0.35),
                 Inches(0.35), str(i + 1), size=11, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, rx + indent + Inches(0.5), y, Inches(2.2), Inches(0.4),
                 rn.upper(), size=13, bold=True, color=PRIMARY)
        add_text(s, rx + indent + Inches(0.5), y + Inches(0.30), Inches(5),
                 Inches(0.4), rd, size=11, color=BODY, italic=True)

    # Right side: Strategic anchors
    sx = Inches(7.3)
    add_text(s, sx, Inches(2.0), Inches(5.5), Inches(0.4),
             "STRATEGIC ANCHORS", size=11, bold=True, color=ACCENT_DEEP)

    anchors = [
        ("KAKENHI KIBAN B",
         "as PI — wind × GBI cross-scale\nmechanism, using Chugoku-Shikoku\nevidence base as pilot foundation"),
        ("YAMAGUCHI U. AS HUB",
         "Western Japan's reference point\nfor urban thermal science &\nclimate-adaptive spatial design"),
        ("LOCAL-TO-GLOBAL EXPORT",
         "Diagnostic workflow exportable to\nAsian & global cities facing\naging × climate-change crises"),
    ]
    ay = Inches(2.55)
    for i, (ah, ab) in enumerate(anchors):
        y = ay + i * Inches(1.1)
        add_rect(s, sx, y, Inches(5.43), Inches(1.0),
                 fill=WHITE, line=ACCENT, line_w=Pt(0.75))
        add_rect(s, sx, y, Inches(0.08), Inches(1.0), fill=ACCENT)
        add_text(s, sx + Inches(0.25), y + Inches(0.10), Inches(5),
                 Inches(0.35), ah, size=13, bold=True, color=PRIMARY)
        add_text(s, sx + Inches(0.25), y + Inches(0.42), Inches(5),
                 Inches(0.6), ab, size=10.5, color=BODY, line_spacing=1.35)

    # Bottom commitment band
    band_y = Inches(6.0)
    add_rect(s, Inches(0.6), band_y, Inches(12.13), Inches(0.95),
             fill=PRIMARY)
    add_text(s, Inches(0.85), band_y + Inches(0.15), Inches(11.5),
             Inches(0.4), "COMMITMENT", size=11, bold=True, color=ACCENT)
    add_text(s, Inches(0.85), band_y + Inches(0.42), Inches(11.5),
             Inches(0.5),
             "Anchor Yamaguchi University inside the international urban-climate network — as a long-term faculty, not a short-term visitor.",
             size=14, bold=True, color=WHITE)


# ============== SLIDE 10 — Closing ==============
def slide_10():
    s = prs.slides.add_slide(blank_layout)
    # Full dark bleed
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, fill=PRIMARY)
    add_rect(s, 0, 0, Inches(2.2), Inches(0.06), fill=ACCENT)

    add_text(s, Inches(0.8), Inches(0.55), Inches(12), Inches(0.4),
             "CLOSING", size=11, bold=True, color=ACCENT)
    add_text(s, Inches(0.8), Inches(0.95), Inches(12), Inches(1.0),
             "Four foundations — already in motion.",
             size=32, bold=True, color=WHITE, line_spacing=1.05)

    # Four pillars
    pillars = [
        ("QUALITY",
         "15 papers · 3 Q1\nall 1st / responsible",
         "Building & Env.  ·  Env. Pollution  ·  Energies"),
        ("BRIDGE",
         "Sakura · Zhejiang Center · 5-country forum",
         "UCL  ·  Zhejiang U.  ·  Asia network"),
        ("FUNDING",
         "≈ 100 M JPY · # 1 of 13",
         "Kakenhi Kiban C → Kiban B"),
        ("IMPLEMENTATION",
         "Kumamoto green-infra policy",
         "MLIT EBPM evaluation case"),
    ]
    px = Inches(0.8)
    py = Inches(2.4)
    pw = Inches(2.95)
    ph = Inches(2.7)
    gap = Inches(0.12)
    for i, (lab, big, footer) in enumerate(pillars):
        x = px + i * (pw + gap)
        # Top accent
        add_rect(s, x, py, pw, Inches(0.08), fill=ACCENT)
        # Label
        add_text(s, x, py + Inches(0.2), pw, Inches(0.4),
                 lab, size=12, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER)
        # Big content
        add_text(s, x, py + Inches(0.75), pw, Inches(1.3),
                 big, size=17, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, line_spacing=1.25)
        # Bottom divider
        add_rect(s, x + Inches(0.7), py + Inches(1.95),
                 pw - Inches(1.4), Emu(6350), fill=ACCENT)
        # Footer
        add_text(s, x, py + Inches(2.10), pw, Inches(0.55),
                 footer, size=10.5, color=RGBColor(0xCB, 0xD5, 0xE0),
                 align=PP_ALIGN.CENTER, italic=True, line_spacing=1.35)

    # Powerful statement
    add_rect(s, Inches(0.8), Inches(5.55), Inches(11.73), Inches(0.05),
             fill=ACCENT)
    add_text(s, Inches(0.8), Inches(5.75), Inches(11.73), Inches(0.6),
             "HIRAKU-Global is the multiplier — not the starter.",
             size=24, bold=True, color=WHITE)
    add_text(s, Inches(0.8), Inches(6.30), Inches(11.73), Inches(0.45),
             "I will give it back to Yamaguchi University, to the Chugoku-Shikoku region, and to the HIRAKU community.",
             size=14, color=RGBColor(0xCB, 0xD5, 0xE0), italic=True)

    add_text(s, Inches(0.8), Inches(6.95), Inches(11.73), Inches(0.4),
             "Thank you very much.  I look forward to your questions.",
             size=12, bold=True, color=ACCENT)


# ============== BUILD ==============
for fn in [slide_01, slide_02, slide_03, slide_04, slide_05,
           slide_06, slide_07, slide_08, slide_09, slide_10]:
    fn()

out_path = "/home/user/academic-research-skills/interview_materials/HIRAKU_Global_Interview_Liu.pptx"
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Slide count: {len(prs.slides)}")
print(f"Slide size: {prs.slide_width / 914400:.3f} x {prs.slide_height / 914400:.3f} inches (16:9)")
