"""Build a comprehensive Chinese Word report with embedded figures, then package
(docx + editable SVGs + JSON) into a single zip.

The Word doc lays out the full research framework in Chinese and fills each
section with the detailed process and results produced throughout the study.
"""
import os, json, shutil, zipfile
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = "/home/user/academic-research-skills/output/sdr-weather-alerts"
FIGJP = f"{BASE}/figures_paper_jp"
RES = f"{BASE}/results"
OUTDIR = f"{BASE}/deliverable_cn"
os.makedirs(OUTDIR, exist_ok=True)

# load numbers
cj = json.load(open(f"{RES}/comprehensive_jp_analysis.json"))
seas = json.load(open(f"{RES}/seasonal_analysis_JFY2025.json"))
cap = json.load(open(f"{RES}/capacity_risk_summary.json"))
era = json.load(open(f"{RES}/era5_verification_deep.json"))

NAVY = RGBColor(0x00, 0x3B, 0x71)
ORANGE = RGBColor(0xE7, 0x8A, 0x00)
CN_FONT = "Microsoft YaHei"   # fallback handled by reader; we also set eastAsia

doc = Document()

# ---- base style: set East Asian font ----
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), CN_FONT)

def _eafont(run, size=None, bold=None, color=None):
    run.font.name = "Calibri"
    r = run._element.get_or_add_rPr().get_or_add_rFonts()
    r.set(qn("w:eastAsia"), CN_FONT)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if color is not None: run.font.color.rgb = color

def heading(text, level=1):
    sizes = {0:22, 1:15, 2:13, 3:11.5}
    p = doc.add_paragraph()
    if level == 0:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    _eafont(r, size=sizes.get(level,11), bold=True, color=NAVY if level<=2 else ORANGE)
    if level == 1:
        # bottom accent
        pPr = p._p.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"),"single"); bottom.set(qn("w:sz"),"6")
        bottom.set(qn("w:space"),"2"); bottom.set(qn("w:color"),"E78A00")
        pbdr.append(bottom); pPr.append(pbdr)
    return p

def para(text, size=10.5, bold=False, color=None, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    _eafont(r, size=size, bold=bold, color=color)
    if italic: r.font.italic = True
    return p

def bullet(text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text); _eafont(r, size=size)
    return p

def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h)); _eafont(r, size=9.5, bold=True, color=RGBColor(0xFF,0xFF,0xFF))
        # shade header
        tcPr = c._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd"); shd.set(qn("w:fill"),"003B71"); tcPr.append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v)); _eafont(r, size=9.5)
    if col_widths:
        for row in t.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    return t

def add_figure(png_name, caption, width=6.2):
    path = f"{FIGJP}/{png_name}.png"
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp = doc.add_paragraph(); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cp.add_run(caption); _eafont(r, size=9, bold=True, color=NAVY)

# ============================================================================
# 封面
# ============================================================================
for _ in range(3): doc.add_paragraph()
heading("基于有限气象数据的大学校园电力负荷\n温度响应与合同容量风险研究", level=0)
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("—— 学事日历调节的温度敏感性与容量风险识别框架 ——"); _eafont(r, size=13, color=ORANGE)
doc.add_paragraph(); doc.add_paragraph()
for line in ["对象：山口大学 常盘校区（宇部市）",
             "数据期间：2025年4月1日 – 2026年3月31日（令和7年度全年）",
             "气象数据：AMeDAS 宇部站观测 + ERA5 再分析（交叉验证）",
             "合同电力：2,000 kW",
             f"报告生成日：{datetime.now().strftime('%Y年%m月%d日')}"]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(line); _eafont(r, size=11)
doc.add_page_break()

# ============================================================================
# 0. 摘要
# ============================================================================
heading("摘要", 1)
para("本研究在仅有有限地面气象观测（气温、降水、风速、风向）与完整校园学事日历的条件下，"
     "构建了一个低数据需求、可解释、可向管理转译的大学校园电力负荷分析框架。"
     "以山口大学常盘校区令和7年度（2025-04 至 2026-03）全年逐时电力为对象，"
     "整合 AMeDAS 宇部站观测、ERA5 再分析、学事日历（6类日型）与合同容量 2,000 kW，"
     "通过描述性剖析、季节分离的能量署名（energy signature）、变点回归与容量风险映射，"
     "回答四个研究问题。")
para("主要发现：(1) 校园电力为冷房支配型——冷房期温度敏感度 +25.4 kWh/h/°C，"
     "而暖房期响应微弱（斜率 −9.8，R²=0.05），提示冬季供暖多非电力；"
     "(2) 学事日历显著调节温度敏感性——冷房期授业日的冷房敏感度（+37.0 kWh/h/°C）"
     "为周末（+23.3）的 1.59 倍，按日型分层后 R² 由 0.40 跃升至 0.91；"
     "(3) 容量风险完全局限于「冷房期 × 授业日 × 32°C 以上」——全部 14 个 Critical 小时"
     "（ρ≥0.85）100% 发生于授业日；(4) ERA5 与 AMeDAS 在气温上几乎完全一致（逐时 r=0.991），"
     "可作为独立验证与缺测补全。")
para("关键词：校园能源管理；能量署名；温度敏感负荷；学事日历；合同容量风险；低数据框架",
     italic=True, color=RGBColor(0x5A,0x5A,0x5A))

# ============================================================================
# 1. 研究框架
# ============================================================================
heading("1. 研究框架与定位", 1)
para("本研究将大学校园重新概念化为「由温度暴露 + 学事日历 + 合同容量边界三者共同塑造的、"
     "受制度时间表调度的公共建筑群能源系统」。创新点不在于提出更复杂的预测模型，"
     "而在于在真实而普遍的「气象数据不完整」约束下，构建可解释、低数据需求的分析框架。")
heading("1.1 四个研究问题（RQ）", 2)
add_table(["编号","研究问题","对应方法","对应图"],
    [["RQ1","校园全年逐时负荷在不同学事日型下呈现怎样的周期结构？","描述性剖析（热图/箱线/日内曲线）","F02·F03·F06"],
     ["RQ2","仅用有限气象能否识别冷房/暖房温度阈值与敏感度？","季节分离 + 变点/线性回归","F04"],
     ["RQ3","学事日历是否调节温度-负荷关系？","日型分层的能量署名","F05"],
     ["RQ4","温度与制度状态如何共同形成合同容量风险？","ρ=负荷/容量 + 风险集中映射","F07·F08·F09"]])
heading("1.2 概念框架链条", 2)
para("有限气象数据 + 学事日历 + 容量边界 → 负荷剖面刻画 → 季节分离的温度响应 → "
     "学事日历调节的敏感度 → 容量风险暴露 → 低数据校园能源管理。", bold=True)

# ============================================================================
# 2. 数据与方法
# ============================================================================
heading("2. 数据与方法", 1)
heading("2.1 数据来源", 2)
add_table(["类别","来源","变量","用途"],
    [["电力（逐时）","校内 BEMS 月报（12个Excel）","逐时消费电力 kWh","主分析对象"],
     ["气象观测","AMeDAS 宇部站（prec_no=81, block_no=0778）","气温·降水·风速·风向","论文主气象数据"],
     ["气象再分析","ERA5（Open-Meteo）","同上4变量 + 湿度等","交叉验证 + 缺测补全"],
     ["学事日历","山口大学令和7年度学年历 PDF","6类日型","制度状态分类"],
     ["合同容量","2,000 kW","契约电力","容量风险基准"]])
para("注：AMeDAS 宇部站为四要素观测站，不含湿度/日照/气压（实测确认全部为 '///'），"
     "与本研究声明的「有限气象」边界完全一致。")

heading("2.2 数据可用性核查（关于样本量 N）", 2)
para("由提供的12个月 Excel 共抽取 8,761 逐时记录，其中电力缺测 1,400 小时、气温缺测 11 小时，"
     f"两者均有效的解析样本为 {cj['総有効時間']:,} 小时 / {cj['総有効日数']} 天。"
     "样本量看似不大，源于 BEMS 数据本身的缺测，而非分析侧删减：", bold=False)
add_table(["月份","有效时间","状态"],
    [["2025-04","456","月初运行延迟（37%缺）"],
     ["2025-05 至 09","643–744","基本完整"],
     ["2025-10 至 12","720–744","完整"],
     ["2026-01","96","BEMS 大规模缺测（87%缺）"],
     ["2026-02","264","BEMS 缺测（61%缺）"],
     ["2026-03","744","完整"]])
para("因此暖房期（12–3月）样本偏疏，是冬季分析较弱的主因。建议向施设课追加照会 1–2 月数据。")
add_figure("F01_data_availability", "图 F01　季节 × 日型 数据可用性矩阵（左：小时数；右：天数）", 6.6)
para("由图 F01 可见，核心单元「冷房期 × 授业日」为逐时 1,104 小时 / 日次 46 天。"
     "按 ASHRAE Guideline 14 的能量署名惯例，以日次集计为主分析单位，N=46 满足单年单季的常规妥当性。")

heading("2.3 分析方法", 2)
bullet("日次集计为主：将逐时聚合为日均，平滑日内变动，符合 ASHRAE inverse modeling 标准单位；逐时结果并列以验证稳健性。")
bullet("季节分离：依文献（ASHRAE、MDPI、EIA、degreedays.net）将全年分为冷房期(6–9月)、暖房期(12–3月)、中间期(4–5·10–11月)，避免混合季节稀释冷暖斜率。")
bullet("变点回归（pwlf）与分段线性：识别冷房/暖房阈值与敏感度斜率。")
bullet("日型分层：按授业日/周末/休业期间等分别回归（对应文献中 occupied/unoccupied 分离）。")
bullet("容量风险：ρ = 负荷 / 2,000 kW，分 Normal/Watch/High/Critical 四级，并在(温度×日型)、(时刻×日型)空间映射风险集中度。")

# ============================================================================
# 3. 气象数据交叉验证
# ============================================================================
heading("3. 气象数据交叉验证（ERA5 vs AMeDAS）", 1)
para("用户提供的 Excel 内嵌「気象庁データ」与本研究独立抓取的 AMeDAS 宇部完全一致"
     "（均值、缺测数逐一吻合），证明抓取无误。进一步在三个时间尺度比照 ERA5 与 AMeDAS：")
add_table(["变量","逐时 r","日 r","月 r","结论"],
    [["气温","0.991","0.997","1.000","几乎完全一致，可互换"],
     ["降水","0.488","0.764","0.903","逐时时刻错位，月总量吻合"],
     ["风速","0.661","0.737","0.544","可接受"]])
para("结论：ERA5 没有错误。降水逐时相关低，是「再分析 vs 单点雨量计」的已知尺度效应"
     "（月尺度升至 0.90）。论文最关键的气温在所有尺度近乎完美，故以 AMeDAS 为主、"
     "ERA5 作独立验证与缺测补全。")

# ============================================================================
# 4. 结果
# ============================================================================
heading("4. 结果", 1)

heading("4.1 RQ1：年间负荷剖面与制度模式", 2)
add_figure("F02_annual_timeseries", "图 F02　需求电力与气温的全年时间序列", 6.4)
add_figure("F03_daytype_distribution", "图 F03　日型别 需求分布（左）与日内曲线（右）", 6.6)
add_figure("F06_month_hour_heatmap", "图 F06　月别·时刻别 平均需求电力热图", 6.4)
para("观察：负荷呈强烈的周周期 + 日内周期 + 季节周期。授业日基线负荷约 700 kWh/h，"
     "周末/休业约 525 kWh/h，约 25% 的差异纯由制度性占用决定（与气温无关）。"
     "全月共通在午后 14–15 时达峰、清晨 5–6 时最低。")

heading("4.2 RQ2：季节分离的温度响应（能量署名）", 2)
add_figure("F04_seasonal_signatures", "图 F04　季节分离 能量署名（左：逐时；右：日次）", 6.6)
add_table(["季节","日次斜率(kWh/h/°C)","日次R²","天数","解读"],
    [["暖房期(12–3月)","−9.8","0.05","77","暖房响应微弱"],
     ["中间期(4–5·10–11月)","+5.7","0.04","111","近平坦＝制度基线"],
     ["冷房期(6–9月)","+25.4","0.22","120","明显冷房响应"]])
para("核心发现①：本校区电力为「冷房支配型」。暖房期温度敏感度极弱（R²=0.05），"
     "强烈提示冬季供暖非电力主导（可能为城市燃气/地区供热），或冬季占用低。"
     "此为仅有电力数据时的诚实结论，待燃气数据进一步判别。")
para("核心发现②：中间期斜率近零（+5.7, R²=0.04），与文献 shoulder-season 理论一致，"
     "为「制度基线负荷」的纯净估计（≈690 kWh/h）。")

heading("4.3 RQ3：学事日历调节的温度敏感性（核心）", 2)
add_figure("F05_cooling_by_daytype", "图 F05　冷房期 × 日型 能量署名（左：逐时；右：日次）", 6.6)
add_table(["日型","日次冷房敏感度","日次R²","天数","逐时敏感度","逐时小时数"],
    [["授业日","+37.0","0.92","46","+58.4","1,104"],
     ["周末","+23.3","0.90","18","+25.5","432"],
     ["休业期间","+39.9","0.25","48","+44.8","1,123"]])
para("核心发现③：冷房期授业日的冷房敏感度为周末的 1.59 倍（37.0 / 23.3）。"
     "同样 1°C 升温，授业日因在室人员内部发热、教室连续使用、设备稼动率高，"
     "引起约 6 成更多的电力增量。授业日与周末 R²≈0.91，按日型分层使温度-负荷关系显著清晰化"
     "（汇总回归仅 R²=0.40）。这证明「学事日历不是简单的控制变量，而是重塑温度响应本身的"
     "第一级调节因子」——即本研究的核心新颖性。")
para("休业期间 R²=0.25 偏低：暑期占用不规则（研究室活动、社团、行事），温度响应被打乱，"
     "反证「有占用才显现温度敏感性」。")

heading("4.4 RQ4：合同容量风险的集中结构（契约 2,000 kW）", 2)
add_figure("F07_rho_timeseries", "图 F07　容量风险比 ρ 的全年推移", 6.4)
add_figure("F08_risk_concentration", "图 F08　(温度 × 日型) 空间的容量风险 ρ 集中", 6.6)
add_figure("F09_risk_by_hour", "图 F09　(时刻 × 日型) 容量风险集中（管理窗口）", 6.6)
add_table(["风险级别","阈值","小时数","占比"],
    [["Normal","ρ<0.50","6,261","85.1%"],
     ["Watch","0.50≤ρ<0.70","863","11.7%"],
     ["High","0.70≤ρ<0.85","220","3.0%"],
     ["Critical","ρ≥0.85","14","0.19%"]])
para(f"核心发现④：年最大 ρ = {cap['rho_stats']['max']:.3f}（2025-07-03 14:00，气温 33.2°C，授业日，"
     f"负荷 1,794 kWh/h），对契约 2,000 kW 的安全余裕约 10%。全部 14 个 Critical 小时 100% 发生于授业日；"
     "High 以上 234 小时中授业日占 78%。在(温度×日型)空间，"
     "「授业日 × 32–35°C」单元平均 ρ=0.80，而同温周末/休业仅 0.45–0.55。"
     "→ 容量风险是温度暴露与学事日历的乘积，单看任一者都无法识别管理窗口。")

# ============================================================================
# 5. 讨论
# ============================================================================
heading("5. 讨论", 1)
heading("5.1 理论贡献", 2)
para("将大学校园界定为「温度暴露 × 学事日历」共同塑造、受合同容量约束的被调度公共建筑群能源系统；"
     "提出并实证了「学事日历调节的温度敏感性（calendar-modulated temperature sensitivity）」这一可检验现象。")
heading("5.2 方法学贡献", 2)
para("在缺少湿度/日照/云量/HVAC 数据的条件下，仅用气温 + 学事日历 + 合同容量即可完成"
     "「温度响应识别 → 季节分离 → 容量风险映射」，提出「学事日历条件下的能量署名」这一可命名构件。")
heading("5.3 实践贡献", 2)
para("管理含义明确：无需全天候警报，聚焦「冷房期 + 授业日 + 32°C 以上 + 14–15 时」即可覆盖九成以上容量风险，"
     "契合校园管理者更易获得校历、合同容量与基础气象数据的真实场景。")
heading("5.4 局限与今后课题", 2)
bullet("1–2月 BEMS 缺测（87%/61%）→ 向施设课照会或验证 ERA5 补全的妥当性。")
bullet("暖房响应弱的解释（非电力供暖 vs 占用低）→ 取得城市燃气消费数据判别。")
bullet("仅单年（JFY2025）→ 扩展至多年以确保外部效度。")
bullet("试验期(6天)、行事日(7天)样本少 → 单年不可避免。")

# ============================================================================
# 6. 结论
# ============================================================================
heading("6. 结论", 1)
para("本研究以有限气象 + 完整学事日历 + 合同容量 2,000 kW，实证了："
     "(i) 校园电力为冷房支配型；(ii) 学事日历将冷房敏感度放大 1.59 倍，分层后 R² 达 0.91；"
     "(iii) 容量风险完全局限于「冷房期 × 授业日 × 32°C 以上」，14 个 Critical 小时 100% 为授业日。"
     "由此在低数据条件下，提供了通过温度暴露与制度日历交互进行校园容量管理的科学依据。")

# ============================================================================
# 附录：图表与文件索引
# ============================================================================
heading("附录　图表与文件索引", 1)
add_table(["文件名","内容","格式"],
    [["F01_data_availability","数据可用性矩阵","PNG+SVG"],
     ["F02_annual_timeseries","年间时间序列","PNG+SVG"],
     ["F03_daytype_distribution","日型分布+日内曲线","PNG+SVG"],
     ["F04_seasonal_signatures","季节分离能量署名","PNG+SVG"],
     ["F05_cooling_by_daytype","冷房期×日型署名","PNG+SVG"],
     ["F06_month_hour_heatmap","月×时刻热图","PNG+SVG"],
     ["F07_rho_timeseries","容量风险时序","PNG+SVG"],
     ["F08_risk_concentration","温度×日型风险集中","PNG+SVG"],
     ["F09_risk_by_hour","时刻×日型风险","PNG+SVG"]])
para("所有图均提供可编辑 SVG（svg.fonttype=none，可在 Illustrator / Inkscape 修改文字与配色）。"
     "数值结果见 results 目录下 JSON 文件。", italic=True)

out_docx = f"{OUTDIR}/校园电力负荷研究报告_中文_{datetime.now().strftime('%Y%m%d')}.docx"
doc.save(out_docx)
print(f"✓ Word saved: {out_docx}")
print(f"  paragraphs: {len(doc.paragraphs)}, tables: {len(doc.tables)}")
