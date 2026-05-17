"""
HIRAKU-Global 7th Cohort Interview Q&A Preparation
LIU Haiqiang  ·  Yamaguchi University
Output: Word document (.docx) — 20-min Q&A response handbook
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# Set base style
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10.5)

# Set page margins
for section in doc.sections:
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

# Colors
COL_PRIMARY = RGBColor(0x14, 0x2E, 0x55)   # Yamaguchi indigo
COL_ACCENT  = RGBColor(0x8C, 0x6F, 0x33)   # gold deep
COL_BODY    = RGBColor(0x33, 0x33, 0x33)
COL_MUTED   = RGBColor(0x66, 0x66, 0x66)
COL_RED     = RGBColor(0xB0, 0x30, 0x2C)   # for warnings
COL_GREEN   = RGBColor(0x2F, 0x6F, 0x4E)


def set_cell_bg(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)


def add_para(text, size=10.5, bold=False, color=None, align=None, italic=False, space_after=2):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return p


def add_title(text, size=20, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = color or COL_PRIMARY
    return p


def add_section_header(text, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    # Top border
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), '142E55')
    pBdr.append(bottom)
    pPr.append(pBdr)
    run = p.add_run(text)
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = color or COL_PRIMARY


def add_qa(num, star, q_cn, q_en, intent, strategy, answer_en, warning=None):
    """Add a question-answer block"""
    # Question number header
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    star_mark = "★ " if star else ""
    run = p.add_run(f"Q{num}  {star_mark}")
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = COL_ACCENT if star else COL_PRIMARY

    # Chinese question
    p_cn = doc.add_paragraph()
    p_cn.paragraph_format.space_after = Pt(2)
    p_cn.paragraph_format.left_indent = Cm(0.6)
    run = p_cn.add_run("【中】 ")
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = COL_PRIMARY
    run2 = p_cn.add_run(q_cn)
    run2.font.size = Pt(11)
    run2.font.bold = True
    run2.font.color.rgb = COL_BODY

    # English question
    p_en = doc.add_paragraph()
    p_en.paragraph_format.space_after = Pt(6)
    p_en.paragraph_format.left_indent = Cm(0.6)
    run = p_en.add_run("【EN】 ")
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = COL_PRIMARY
    run2 = p_en.add_run(q_en)
    run2.font.size = Pt(11)
    run2.font.italic = True
    run2.font.color.rgb = COL_BODY

    # Reviewer intent
    if intent:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Cm(0.6)
        r = p.add_run("评审用意：")
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = COL_ACCENT
        r2 = p.add_run(intent)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COL_MUTED
        r2.font.italic = True

    # Strategy
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Cm(0.6)
    r = p.add_run("回答策略：")
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = COL_ACCENT
    r2 = p.add_run(strategy)
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COL_BODY

    # English answer (in a bordered box style)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.6)
    r = p.add_run("英文标准回答：")
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = COL_GREEN

    # Add the English answer in a single-cell table for box effect
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_ALIGN_PARAGRAPH.LEFT
    tbl.autofit = False
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(16.6)
    set_cell_bg(cell, "F6F8FA")
    cell.paragraphs[0].paragraph_format.left_indent = Cm(0.3)
    cell.paragraphs[0].paragraph_format.right_indent = Cm(0.3)
    cell.paragraphs[0].paragraph_format.space_before = Pt(3)
    cell.paragraphs[0].paragraph_format.space_after = Pt(3)
    run = cell.paragraphs[0].add_run(answer_en)
    run.font.size = Pt(10.5)
    run.font.color.rgb = COL_BODY
    # Indent cell from page
    for row in tbl.rows:
        for c in row.cells:
            c._tc.tcPr.append(OxmlElement('w:tcMar'))

    # Warning if any
    if warning:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Cm(0.6)
        r = p.add_run("⚠ 注意：")
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = COL_RED
        r2 = p.add_run(warning)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COL_BODY
        r2.font.italic = True


# ====================================================
# COVER / HEADER
# ====================================================
add_title("HIRAKU-Global 第7期面试")
add_title("20 分钟质疑应答 · 完整问答集 (中英对照)", size=14, color=COL_ACCENT)

add_para("LIU Haiqiang  ·  山口大学  ·  Lecturer (Tenure-track)",
         size=11, color=COL_MUTED)
add_para("Yamaguchi University  ·  Graduate School of Sciences and Technology for Innovation",
         size=10, color=COL_MUTED, italic=True)

# Spacer
doc.add_paragraph()

# Usage notes block
tbl = doc.add_table(rows=1, cols=1)
tbl.autofit = False
cell = tbl.rows[0].cells[0]
set_cell_bg(cell, "FFF8E1")
p = cell.paragraphs[0]
p.paragraph_format.space_before = Pt(6)
p.paragraph_format.space_after = Pt(2)
r = p.add_run("使用说明  /  HOW TO USE\n")
r.font.size = Pt(11)
r.font.bold = True
r.font.color.rgb = COL_PRIMARY

usage = [
    "★ 标记为高频核心问题 — 必须熟练掌握",
    "每题结构：评审用意 → 回答策略（中文）→ 英文标准回答 → 注意点",
    "英文回答控制在 60-100 词 — 应答应简洁有力，不超过 30 秒",
    "若被追问技术细节而无法回答，可承认边界并把问题转化为 future plan",
    "全程不与他人比较；用客观事实 + 数字 + 已发生的成果说服评审",
]
for u in usage:
    p = cell.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("  •  " + u)
    r.font.size = Pt(10)
    r.font.color.rgb = COL_BODY

doc.add_paragraph()

# Table of contents
add_section_header("目录  /  CONTENTS")
toc_items = [
    "A. 研究内容与独创性 / Research Content & Originality      (6 questions)",
    "B. 研究计划与可行性 / Research Plan & Feasibility         (5 questions)",
    "C. 国际合作 / International Collaboration                 (4 questions)",
    "D. 研究资金 / Funding                                    (4 questions)",
    "E. HIRAKU-Global 项目相关 / HIRAKU-Global                (4 questions)",
    "F. 履历与能力 / Career & Skills                          (3 questions)",
    "G. 山口大学・地域贡献 / Yamaguchi & Regional Contribution (3 questions)",
    "H. 困难・敏感问题 / Tough & Sensitive Questions          (4 questions)",
    "I. 总结性问题 / Closing-Style Questions                  (2 questions)",
]
for t in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t)
    r.font.size = Pt(10.5)
    r.font.color.rgb = COL_BODY

doc.add_page_break()

# ====================================================
# SECTION A — RESEARCH CONTENT & ORIGINALITY
# ====================================================
add_section_header("A. 研究内容与独创性  /  Research Content & Originality")

add_qa(
    num="A1", star=True,
    q_cn="您研究的独创性在哪里？",
    q_en="What is the originality of your research?",
    intent="评审最常用的开场问题。考察是否能用一句话讲清楚研究的核心独创点。",
    strategy="不要罗列方法。用'我做了什么别人没做'的句式 → 突出 cross-scale 工作流 + 累积热暴露 + 已被 MLIT 采用。",
    answer_en="The originality is not in measuring heat — many can do that. What is rare is the combination: I integrate satellite remote sensing, on-site measurement, and CFD into one continuous workflow, evaluate cumulative pedestrian heat exposure rather than instantaneous temperature, and the workflow has already been applied to Kumamoto City's green-infrastructure policy and cited by Japan's MLIT as an Evidence-Based Policy Making case. Few researchers can show all four — satellite, measurement, CFD, and national policy adoption — in one workflow.",
    warning="MLIT EBPM 是您最强的硬证据，必须在 20 秒内点出来。",
)

add_qa(
    num="A2", star=False,
    q_cn="您的研究为何重要？",
    q_en="Why is your research important?",
    intent="考察是否能让非专门评审理解研究的社会意义。",
    strategy="数据 → 街道层面 → 三个简单问题。",
    answer_en="In 2023, Japan recorded over 91,000 emergency heatstroke transports, with about 1,200 in Yamaguchi alone — 60 percent aged 65 or older. But not every street is equally hot. My research answers three simple questions — where it is hot, why it is hot, and how we can cool the city while keeping it walkable. This sits at the intersection of climate warming, aging society, and city-center decline — the triple challenge of regional cities like Yamaguchi.",
    warning=None,
)

add_qa(
    num="A3", star=True,
    q_cn="您的研究与现有的城市热岛研究有什么不同？",
    q_en="How does your research differ from existing urban heat island studies?",
    intent="考察对学科现状的认知与差异化定位能力。",
    strategy="承认领域已有成熟工作 → 指出两个分裂的研究流派（LST vs CFD）→ 您把它们连起来 + 加入行人尺度验证。",
    answer_en="The urban heat-island literature has a mature LST-based diagnostic body, and a separate body of ENVI-met or CFD micro-climate studies. But these two bodies are rarely coupled into an intervention logic at the scale of a walkable neighborhood. My approach chains satellite-scale screening, block-scale CFD, and pedestrian-scale validation as one inference path — and it ends in a number a planner can act on, delta-WBGT per corridor segment, not a separate analysis.",
    warning="不要贬低现有研究——只说明您把它们'连起来'。",
)

add_qa(
    num="A4", star=False,
    q_cn="请用非专业语言解释您的研究方法。",
    q_en="Can you explain your method to a non-expert?",
    intent="考察跨学科沟通能力（评价点 V）。",
    strategy="用三个高度比喻：卫星看 city → 街区看 block → 走路看 pedestrian。",
    answer_en="Imagine looking at the city from three heights. From a satellite, I see which neighborhoods are hot. Down at building height, I use computer simulation to see why — how wind, buildings, and trees interact. And finally on the street, I walk with sensors along the routes elderly residents actually use. Each height answers a different question, but together they tell us where to plant a tree, where to add a cool shelter, and which street to protect as a wind corridor.",
    warning=None,
)

add_qa(
    num="A5", star=False,
    q_cn="您在熊本研究中最重要的发现是什么？",
    q_en="What is the most important finding from your Kumamoto work?",
    intent="考察研究深度与表达能力。",
    strategy="一句核心发现：'同样的绿地，作用差异很大' → 引出 wind × morphology 调节作用。",
    answer_en="The most important finding is that the cooling value of an urban forest patch is not a property of the patch itself. In Kumamoto, identical forest patches produced very different daytime cooling effects depending on whether they sat inside a ventilated corridor or behind a wind-shadowing block. And the patches most valuable to vulnerable residents were not the largest ones — they were the ones closest to elderly daily-activity nodes. This finding directly shaped my LST × land-cover priority-intervention map in the city's policy chapter.",
    warning=None,
)

add_qa(
    num="A6", star=False,
    q_cn="为什么您聚焦于高齢者？",
    q_en="Why do you focus on elderly residents?",
    intent="考察社会问题意识与研究对象选择的合理性。",
    strategy="数据 + 山口的人口结构 + 高齢者步行路径具体可识别。",
    answer_en="Three reasons. First, the data: 60 percent of Yamaguchi heatstroke patients in 2023 were aged 65 or older. Second, Yamaguchi's 65-plus share is well above the national average — a typical western-Japan regional city. Third, elderly daily-activity corridors are 500 to 1,000 meters and have identifiable nodes — clinic, supermarket, station — which makes them a tractable spatial unit for measurement and intervention. Focusing on the most vulnerable group also makes the science most actionable for policy.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION B — RESEARCH PLAN & FEASIBILITY
# ====================================================
add_section_header("B. 研究计划与可行性  /  Research Plan & Feasibility")

add_qa(
    num="B1", star=True,
    q_cn="为什么选择山口・宇部・松江这三个城市？",
    q_en="Why these three cities — Yamaguchi, Ube, Matsue?",
    intent="考察案例选择的科学合理性。",
    strategy="三种风环境对比 → 同一行政区域 → 可比较性强。",
    answer_en="They were chosen because they span three contrasting wind regimes within one administrative region. Yamaguchi is an inland basin, Ube is a coastal sea-breeze city, and Matsue is a Sea-of-Japan lakeside city. That contrast is exactly what my research question requires — to see how local wind regulates the cooling effectiveness of green infrastructure under different urban morphologies. Keeping them within Chugoku also means logistics and partnership-building remain tractable within the HIRAKU-Global timeframe.",
    warning=None,
)

add_qa(
    num="B2", star=True,
    q_cn="您的研究计划中最大的风险是什么？您如何管理？",
    q_en="What is the biggest risk in your plan, and how will you manage it?",
    intent="考察自我认知与项目管理能力。承认风险比假装没有风险更有说服力。",
    strategy="承认风险 → 给出具体管理对策 → 不说'没有风险'。",
    answer_en="The main risk is over-extension — trying to cover too many cities and methods at once. I manage this in three ways. First, I anchor Yamaguchi as the primary case and expand stepwise to Ube and Matsue only after Year 1 diagnostics. Second, if travel is constrained, I keep international collaboration alive online — I have done this before during COVID. Third, I retain Kumamoto data as a pre-validated reference so I always have a comparative baseline. The principle is simple — deliver, not over-promise.",
    warning="不要回答'没有风险'——评审会觉得您准备不足。",
)

add_qa(
    num="B3", star=False,
    q_cn="5年时间足够完成这个计划吗？",
    q_en="Is five years enough for this plan?",
    intent="考察时间规划的现实性。",
    strategy="逐年具体说明 → 强调'已有基础'缩短启动时间。",
    answer_en="Yes — because I am not starting from zero. The satellite pipeline is already running from my 2024 Sustainability paper. The CFD methodology was established in my courtyard wind-environment work. Kumamoto data provides a pre-validated baseline. So Year 1 starts with diagnosis, not setup. The five-year schedule is built around clear milestones — overseas stay in Year 2, mechanism paper in Year 3, validation in Year 4, synthesis and Kakenhi Kiban B in Year 5. Each year has one core deliverable, not a wishlist.",
    warning=None,
)

add_qa(
    num="B4", star=False,
    q_cn="如果无法收集足够的行人尺度实测数据怎么办？",
    q_en="What if you cannot collect enough pedestrian-scale field data?",
    intent="考察实验失败的应对方案。",
    strategy="承认 fallback → 用 Kumamoto 已有数据 + 浙江比较数据补足。",
    answer_en="I have a layered backup. First, the Kumamoto baseline already includes corridor-level measurements I can use as a reference set. Second, the Zhejiang collaboration provides comparative urban data under different morphologies. Third, the CFD-predicted mechanisms can be partially validated against literature-reported WBGT under similar configurations. The pedestrian campaign is essential but it is one validation channel, not the only one. The overall inference path remains robust if any single channel underperforms.",
    warning=None,
)

add_qa(
    num="B5", star=False,
    q_cn="您如何平衡田野调查与教学职责？",
    q_en="How will you balance fieldwork with teaching duties?",
    intent="考察时间管理与对教学的态度。教授特别关心这点。",
    strategy="主动谈教学 → 把田野调查融入研究指导 → 集中式 fieldwork 安排。",
    answer_en="I treat teaching and research as complementary, not competing. Fieldwork is concentrated in the July–August heatwave window, which aligns with the summer recess. During the academic term, my graduate students join the analysis and writing — making fieldwork part of their training. I also bring my research into the classroom: real Kumamoto and Yamaguchi cases give students concrete material to engage with. The result is a research program that strengthens teaching, not one that competes with it.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION C — INTERNATIONAL COLLABORATION
# ====================================================
add_section_header("C. 国际合作  /  International Collaboration")

add_qa(
    num="C1", star=True,
    q_cn="您在国际合作中的具体角色是什么？",
    q_en="What exactly was your role in international collaboration?",
    intent="确认您是'组织者'还是'参与者'。",
    strategy="三个具体记录 → 反复用'organize / coordinate / build'三个动词。",
    answer_en="In all three of my international collaborations, I was the organizer, not just a participant. First, I organized the Sakura Science Program exchanges between Zhejiang Sci-Tech University and Japanese universities, over multiple years. Second, during COVID, I helped build the Zhejiang International Cooperation Center on Carbon Neutrality — one of only four such centers province-wide, with ZSTU as core unit. Third, I organized a five-country online forum across China, Japan, the UK at UCL, Indonesia, and Bangladesh. These are coordination roles, not co-authorship roles.",
    warning="'organizer / not participant' 这组对比一定要明确说出。",
)

add_qa(
    num="C2", star=True,
    q_cn="为什么选 UCL？为什么选浙江大学？",
    q_en="Why UCL? Why Zhejiang University?",
    intent="考察合作伙伴选择的策略性 — 是否互补、是否有真实基础。",
    strategy="UCL 提供互补能力（geospatial / ML）→ 浙江大学提供高密度城市对照。两个都是基于已有友好关系。",
    answer_en="UCL with Dr. Huanfa Chen — because his expertise in high-resolution geospatial data and machine-learning urban morphology classification is complementary to my thermal-environment and CFD strengths. The two-month stay in Year 2 is built around joint methodology development. Zhejiang University with Professor Jian Ge — because Zhejiang offers a high-density Chinese urban setting that contrasts directly with Japanese regional cities, testing whether my framework travels. Both partners build on existing friendly relationships — not from scratch.",
    warning=None,
)

add_qa(
    num="C3", star=False,
    q_cn="HIRAKU 结束后您如何维持国际合作？",
    q_en="How will you sustain international collaboration after HIRAKU?",
    intent="考察可持续性 — 是否只是 HIRAKU 期间的烟火。",
    strategy="科研产出 → 共同基金 → 学生交流 → 年度活动。",
    answer_en="Three concrete mechanisms. First, joint publications — by HIRAKU's end I aim for at least two co-authored papers with UCL and Zhejiang that lock in the relationship. Second, joint funding — I will use the HIRAKU outputs as the foundation for an international collaborative grant. Third, an annual workshop hosted at Yamaguchi that I will organize as a recurring event. Long-term collaboration cannot survive on goodwill alone — it survives on shared deliverables and shared funding.",
    warning=None,
)

add_qa(
    num="C4", star=False,
    q_cn="Sakura 计划已经停止——这个合作还有效吗？",
    q_en="The Sakura Program is paused — is the collaboration still alive?",
    intent="考察您对合作关系的实际把握。",
    strategy="承认 program 停了 → 但关系活着 → 给出近期具体交流证据。",
    answer_en="The Sakura formal exchange paused because of COVID, but the underlying institutional relationships are intact. I remain in regular contact with ZSTU colleagues — including being invited to give academic talks at related Chinese institutions in 2025. In HIRAKU-Global I plan to formally reactivate the Sakura framework with Yamaguchi University rather than ZSTU as the Japanese anchor. The bridge is real; only the program label was paused.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION D — FUNDING
# ====================================================
add_section_header("D. 研究资金  /  Funding")

add_qa(
    num="D1", star=True,
    q_cn="为什么您之前在日本没有取得外部研究基金？",
    q_en="Why have you not obtained external funding in Japan before?",
    intent="最敏感问题之一。考察您能否把劣势转化为优势。",
    strategy="制度原因 + 不是借口 + 转化为政策能力 + 接到山口入职后立刻有结果。",
    answer_en="Before Yamaguchi University, my Japanese position was at the Kumamoto City Policy Research Institute — a municipal post, not a university faculty position. The institutional rule did not permit personal external grants such as JSPS Kakenhi. So the absence reflects the role, not my ability. That position gave me something most academic researchers do not have — strong policy-translation skills, including the MLIT EBPM-cited work. After joining Yamaguchi University in January 2026, I immediately started applying — and was ranked number one out of thirteen applicants in the Yamaguchi regional research program. The Japan pattern has already started.",
    warning="千万不要说成借口。用 'reflects the role, not the ability' 这种句式把性质讲清。",
)

add_qa(
    num="D2", star=True,
    q_cn="您能拿到 Kakenhi 的证据是什么？",
    q_en="What is your evidence that you can obtain Kakenhi?",
    intent="考察是否有客观可信的指标支撑'未来能拿到'的说法。",
    strategy="三层证据：山口校内已#1 → 中国累计1亿日元基金记录 → 已发表 Q1 论文支撑申请。",
    answer_en="Three layers of evidence. First — direct: I was ranked number one out of thirteen applicants in the Yamaguchi University regional research program, with four selected. Second — track record: across eight Chinese projects I have accumulated approximately 100 million yen total, with five as Leading Researcher in a highly competitive environment. Third — the underlying assets: three Q1 papers as first or responsible author and an MLIT EBPM-cited policy chapter form a strong evidence base for a Kakenhi Kiban C application, with a clear path to Kiban B during HIRAKU.",
    warning=None,
)

add_qa(
    num="D3", star=False,
    q_cn="中国的基金制度不同——这种经验如何转化？",
    q_en="The Chinese funding system is different — how does that experience translate?",
    intent="考察制度适应能力。",
    strategy="承认制度不同 → 但核心能力相同 → 已经在日本开始证明。",
    answer_en="The two systems differ in process — but the core competencies transfer directly. In both, you must define a clear scientific question, design a feasible plan, manage budget and timeline, and communicate impact to non-specialist reviewers. Those skills are identical. The Chinese experience also taught me to operate under high competition. The Yamaguchi number-one ranking within months of joining is, I think, the most direct evidence that the transfer is already happening.",
    warning=None,
)

add_qa(
    num="D4", star=False,
    q_cn="如果科研费 Kiban B 申请失败怎么办？",
    q_en="What if your Kakenhi Kiban B application fails?",
    intent="考察 contingency planning。",
    strategy="不示弱 → 给出 fallback ladder：Kiban C extension / 共同研究費 / 国際共同加速 / 民間助成.",
    answer_en="I plan upward in steps, so failure at one level is not the end. If Kiban B does not succeed on the first attempt, I revise based on reviewer feedback and resubmit, while continuing with Kiban C extension funding and the Yamaguchi internal collaborative grants. The Chugoku-Shikoku evidence base is also a strong fit for several private foundation grants and the JST Strategic Basic Research Programs. Funding diversification is part of the plan, not an emergency response.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION E — HIRAKU-GLOBAL
# ====================================================
add_section_header("E. HIRAKU-Global 项目相关  /  HIRAKU-Global")

add_qa(
    num="E1", star=True,
    q_cn="您为什么需要 HIRAKU-Global？",
    q_en="Why do you need HIRAKU-Global?",
    intent="评审最直接的问题。考察是否真正理解项目价值。",
    strategy="不要说'我想国际化'——具体说项目的四类支援如何放大已有基础。",
    answer_en="I am at a turning point. I have publications, international experience, an MLIT-cited policy case, and my first Japanese grant. What I need is structured support to scale up — and HIRAKU-Global provides exactly that: a structured mentor system, dedicated overseas dispatch support, the starter-course development modules, and a peer network. HIRAKU is not where I start — it is the multiplier that lets an already-producing researcher become an international research leader anchored at Yamaguchi.",
    warning="'multiplier, not starter' 是核心表达——必须说出来。",
)

add_qa(
    num="E2", star=True,
    q_cn="您将为 HIRAKU 社群贡献什么？",
    q_en="What will you contribute to the HIRAKU community?",
    intent="考察是否只是受益者，还是同时是贡献者。",
    strategy="四项具体贡献：国际研讨会 / 日中桥接 / 跨学科 seminar / Peer mentoring。",
    answer_en="Four concrete contributions. First, in Year 4 I will host an international workshop at Yamaguchi on urban thermal science and climate adaptation, bringing HIRAKU researchers together with my overseas collaborators. Second, I will provide a standing China-Japan academic bridge — annual online seminars, translation, and fieldwork support for HIRAKU members. Third, I will run cross-discipline seminars on cross-scale analysis and translational research design. Fourth, peer mentoring — supporting newer HIRAKU members through international communication and grant-writing. I want to be an active member, not only a recipient.",
    warning=None,
)

add_qa(
    num="E3", star=False,
    q_cn="取得 tenure 之后您的愿景是什么？",
    q_en="What is your post-tenure vision?",
    intent="考察长期承诺与对学校的认同。",
    strategy="Lab → Region → 西日本 → Asia → Global 五层递进。强调长期扎根山口。",
    answer_en="After tenure, my goal is singular — to make Yamaguchi University a regional hub for urban thermal research in Western Japan. Concretely: a stable research group of graduate students, a steady first-author Q1 publication pipeline, an international comparative platform with European, Chinese, and Southeast Asian partners, and the scalable diagnostic workflow exportable to other Asian and global cities facing aging and climate stress. I am here as a long-term anchor — not a short-term visitor.",
    warning=None,
)

add_qa(
    num="E4", star=False,
    q_cn="您如何衡量自己在 HIRAKU 期间的成功？",
    q_en="How will you measure your own success during HIRAKU?",
    intent="考察成果意识与 KPI 思维。",
    strategy="按 3I 框架对应具体可量化指标。",
    answer_en="By measurable outputs aligned with HIRAKU's 3I framework. For Innovative — at least one mechanism paper plus the reusable diagnostic workflow. For Influential — continued Q1 publications and the Kakenhi Kiban C secured, with a Kiban B application submitted. For Impactful — concrete deliverables to Yamaguchi, Ube, and Matsue municipalities; at least one MLIT-aligned or EBPM-aligned application of the workflow. And finally — at least one HIRAKU-organized international workshop hosted at Yamaguchi. Specific, dated, and verifiable.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION F — CAREER & SKILLS
# ====================================================
add_section_header("F. 履历与能力  /  Career & Skills")

add_qa(
    num="F1", star=True,
    q_cn="您最强的论文成就是什么？",
    q_en="What is your strongest publication achievement?",
    intent="考察对自身研究价值的认识。",
    strategy="不说'我有很多论文'——选出最具说明力的两本 Q1。",
    answer_en="My strongest are the two Q1 papers in Building and Environment and Environmental Pollution. Building and Environment is in the top 5 of its field; I am co-first author on a study linking classroom thermal comfort with student learning performance, and I led the experimental design and supervision. Environmental Pollution is a top-tier environmental science journal on PM2.5 health-effects assessment. Together they show that my work is recognized in two related but distinct international communities — building science and environmental science.",
    warning=None,
)

add_qa(
    num="F2", star=False,
    q_cn="您为什么从中国回到日本？",
    q_en="Why did you leave China to come back to Japan?",
    intent="考察职业选择的逻辑性与对日本的承诺。",
    strategy="积极理由，不批评中国 → 日本研究环境的吸引 + 山口大学的契合。",
    answer_en="My doctoral training was in Japan, and my research has always been comparative across Japan and China. Returning to Japan as a faculty member was a natural step — Japan's regional cities are exactly where my Stage-3 research questions are most needed, and Yamaguchi University, with its HPC environment and active municipal relationships, is the right institutional home for the work. The move is about fit between the research and the institution.",
    warning=None,
)

add_qa(
    num="F3", star=True,
    q_cn="您如何与其他领域的研究者沟通？",
    q_en="How will you communicate with researchers from other fields?",
    intent="评价点 V。考察跨学科沟通能力。",
    strategy="从问题而非术语出发 → 用真实案例 → 已有跨学科经验。",
    answer_en="I start from the problem, not the jargon. Heat, walkability, and elderly health are shared concerns across architecture, urban planning, public health, and policy science. I have worked across all four — Stage 1 was engineering, Stage 2 was health-related, Stage 3 is urban-planning and policy. So I have practiced this translation across my own career. Plain language first, technical detail only when needed, and always with a concrete city or street as the anchor.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION G — YAMAGUCHI & REGION
# ====================================================
add_section_header("G. 山口大学・地域贡献  /  Yamaguchi & Regional Contribution")

add_qa(
    num="G1", star=True,
    q_cn="您将如何贡献山口大学？",
    q_en="How will you contribute to Yamaguchi University?",
    intent="评价点 IV。考察对学校的具体贡献意愿。",
    strategy="三个方向：学术 visibility + 国际网络 + 地域贡献。",
    answer_en="In three concrete ways. First, by publishing high-quality Q1 papers under Yamaguchi University's name, building the university's visibility in urban thermal research. Second, by bringing international partners — UCL, Zhejiang, and the Asia network — into Yamaguchi's research ecosystem, including hosting the Year-4 international workshop at the university. Third, by producing research that local governments — Yamaguchi, Ube, Matsue — can use directly, which strengthens the university's regional role and demonstrates its societal value.",
    warning=None,
)

add_qa(
    num="G2", star=True,
    q_cn="您的研究如何直接惠及山口市民？",
    q_en="How does your research directly benefit Yamaguchi residents?",
    intent="评审最关心的'地域贡献'实质问题。",
    strategy="非常具体：街道层面 heat-risk map + 高齢者步行路径 cooling-shelter 提案 + 给市役所政策资料。",
    answer_en="Three direct benefits. First, street-corridor-resolution heat-risk maps showing exactly which streets pose the greatest summer risk for elderly residents — useful for city walking plans and emergency response. Second, intervention priority maps showing where to plant canopy, where to site cooling shelters, and which streets to preserve as ventilation corridors. Third, planning recommendations delivered directly to the municipality in a format Yamaguchi's planning offices can use without me standing beside them. The aim is research that municipal staff can apply on their own.",
    warning=None,
)

add_qa(
    num="G3", star=False,
    q_cn="您会长期留在山口大学吗？",
    q_en="Will you stay long-term at Yamaguchi University?",
    intent="tenure-track 项目最关心的承诺问题。",
    strategy="明确承诺 → 给出长期愿景的具体支撑。",
    answer_en="Yes — I came to Yamaguchi University to build, not to pass through. My five-year HIRAKU plan and my post-tenure vision are both built on Yamaguchi as the anchor: a stable research group, sustained international partnerships with the university at the center, and Yamaguchi as Western Japan's reference point for urban thermal science. I see myself contributing to this university for the long term — that is the only timescale on which the work I want to do is possible.",
    warning="这一题要回答得坚定。tenure-track 项目最害怕'拿了支援就走'的人。",
)

doc.add_page_break()

# ====================================================
# SECTION H — TOUGH QUESTIONS
# ====================================================
add_section_header("H. 困难・敏感问题  /  Tough & Sensitive Questions")

add_qa(
    num="H1", star=True,
    q_cn="为什么我们应该选择您？",
    q_en="Why should we choose you?",
    intent="最直接也最关键的'闭环'问题。",
    strategy="四个 foundation + 'already in motion' → 'multiplier, not starter' → 长期承诺。",
    answer_en="Because four foundations are already in motion. Quality — fifteen peer-reviewed papers, three Q1, all as first or responsible author. Bridge — Sakura Program, Zhejiang Carbon-Neutral Center, five-country forum, all as organizer. Funding — approximately 100 million yen total in China, and ranked number one out of thirteen at Yamaguchi within months of arrival. Implementation — Kumamoto's green-infrastructure policy and the MLIT EBPM citation. HIRAKU-Global will not start something new — it will multiply what is already producing. And I am here as a long-term anchor at Yamaguchi University.",
    warning="这是您唯一可以'稍微大声'说出 4 foundation 的问题。务必练到流畅。",
)

add_qa(
    num="H2", star=False,
    q_cn="您的论文产出在 2023-2025 年减少——为什么？",
    q_en="Your publication output slowed in 2023–2025 — why?",
    intent="考察对履历空缺期的合理解释能力。",
    strategy="解释 Kumamoto 性质 + 该时期换成 policy output → 已经在 2024 年重新加速。",
    answer_en="During 2023 to 2025 I worked at the Kumamoto Institute of Policy Research — a municipal post where outputs were measured differently. What I produced was policy-oriented: the A-1 book chapter, two policy-oriented articles in Kumamoto Urban Policy, and the MLIT EBPM-cited work. The first-author SCI pipeline re-accelerated with my 2024 Sustainability paper, and continues now at Yamaguchi. The slowdown reflects the role I held during those two years, not a slowdown in research itself.",
    warning="保持平静 — 不要显得防御。",
)

add_qa(
    num="H3", star=False,
    q_cn="您独立指导过研究团队吗？",
    q_en="Have you independently supervised a research team?",
    intent="考察研究 group 经营能力。",
    strategy="ZSTU 时期作为副教授指导 → Building and Environment 共同第一作者学生现为清华博士研究员。",
    answer_en="Yes. During my Associate Professorship at Zhejiang Sci-Tech University from 2018 to 2023, I supervised graduate students through to publication. One of them is co-first author with me on the Building and Environment paper — and is now a doctoral researcher at Tsinghua University. That experience showed me how to develop a junior researcher from data collection through to a Q1 publication. I will bring the same approach to graduate supervision at Yamaguchi.",
    warning=None,
)

add_qa(
    num="H4", star=False,
    q_cn="如果与您的 HIRAKU mentor 在研究方向上产生分歧，您会如何处理？",
    q_en="How would you handle a research-direction disagreement with your HIRAKU mentor?",
    intent="考察沟通成熟度与心理素质。",
    strategy="尊重 + 倾听 + 沟通 → 做决定的责任仍在自己 → 不会逃避反馈。",
    answer_en="I would treat it as an opportunity, not a conflict. First, I would listen carefully — a senior mentor sees patterns I may not see. Second, I would explain my reasoning in detail and propose a small test or pilot to evaluate the disagreement empirically rather than rhetorically. Third, the responsibility for the research direction remains mine, but I would not ignore advice — I would integrate it visibly into the plan. Good mentorship requires honest disagreement, not silent compliance.",
    warning=None,
)

doc.add_page_break()

# ====================================================
# SECTION I — CLOSING-STYLE QUESTIONS
# ====================================================
add_section_header("I. 总结性问题  /  Closing-Style Questions")

add_qa(
    num="I1", star=True,
    q_cn="您的 5 年和 10 年职业愿景是什么？",
    q_en="What is your five-year and ten-year career vision?",
    intent="考察长期规划能力。",
    strategy="5 年具体 → 10 年战略性 → 都以山口大学为锚。",
    answer_en="In five years — by HIRAKU completion — I aim to be an established researcher in heat-adaptive urban design, with a Kakenhi Kiban B, an active UCL-Zhejiang international network, stable graduate students, and tenure at Yamaguchi University. In ten years, I want Yamaguchi University to be one of the recognized reference points for urban thermal research in Asia — and I want to contribute to international policy discussions on climate-adapted regional cities. The five-year goal is what I can promise; the ten-year goal is what I am building toward.",
    warning=None,
)

add_qa(
    num="I2", star=False,
    q_cn="如果只有 1 分钟说服我们，您会说什么？",
    q_en="If you had only one minute to convince us, what would you say?",
    intent="压力测试 + 自我浓缩能力测试。",
    strategy="60 秒版本 — 4 foundation + multiplier + 长期承诺。",
    answer_en="Four foundations, already in motion. Fifteen papers, three Q1, all led by me. Three concrete records of organizing international cooperation, not just attending it. Approximately 100 million yen of competitive funding, and ranked number one out of thirteen at Yamaguchi within months of arrival. And research already cited by Japan's MLIT as an EBPM case. HIRAKU-Global will not start something new — it will multiply what is already producing. I am here as a long-term anchor at Yamaguchi University. That is why selecting me is investing in a return that has already begun.",
    warning="必须练到能在 50-55 秒内念完。",
)

# ====================================================
# CLOSING NOTES
# ====================================================
doc.add_page_break()
add_section_header("附录：应答总体策略  /  Overall Q&A Strategy")

strategies = [
    ("开场原则", "评审第一个问题往往是 A1 或 H1。把'4 foundation + already in motion'作为底牌，但不要每题都重复全部——只在 A1、H1、I2 三题完整使用。"),
    ("数字记忆锚点", "91,000 / 1,200 / 60% / 500-1000m / 15·10·8·3 / ~100M JPY / #1 of 13 / 4 selected / Sakura / 5-country / MLIT EBPM. 每个数字必须能在 2 秒内说出。"),
    ("关键短语", "Multiplier, not starter / Organizer, not participant / Long-term anchor / Already in motion / Cited by MLIT as an EBPM case / Reflects the role, not the ability."),
    ("处理不会答的问题", "1) 'That is a good point.' 2) 承认 boundary。3) 转化为 future plan。例：'I have not done this yet, but in HIRAKU period I plan to address it by...'"),
    ("被打断怎么办", "保持平静。停顿，听完，再回答。不要抢话，但也不要因为被打断就放弃要点。"),
    ("如果日语提问", "'Thank you. May I answer in English?' 礼貌切回。或者用简单日语承接（'はい、その点については'）再切英语。"),
    ("情绪管理", "永远不要表现'紧张感'或'防御性'。即使被追问 funding gap 或 publication gap，也保持事实陈述语气。"),
    ("收尾", "如果有 'Any final words?' 用 I2 的 60 秒版本作为承接。"),
]
for head, body in strategies:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("◆ " + head + "  ")
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COL_PRIMARY
    r2 = p.add_run(body)
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = COL_BODY

# Footer
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("— END —")
r.font.size = Pt(10)
r.font.color.rgb = COL_MUTED
r.font.italic = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("HIRAKU-Global 第7期面试  ·  20 分钟质疑应答完整问答集")
r.font.size = Pt(9)
r.font.color.rgb = COL_MUTED
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("LIU Haiqiang  ·  Yamaguchi University  ·  2026")
r.font.size = Pt(9)
r.font.color.rgb = COL_MUTED

out = "/home/user/academic-research-skills/interview_materials/HIRAKU_QA_Handbook_Liu.docx"
doc.save(out)
print(f"Saved: {out}")
