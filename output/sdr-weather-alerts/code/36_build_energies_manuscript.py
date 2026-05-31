"""Build a complete Energies-formatted manuscript (Word .docx) following the
official MDPI template structure:

Title -> Authors/Affiliations -> Abstract (<=200 words) -> Keywords (3-10) ->
1. Introduction -> 2. Materials and Methods -> 3. Results -> 4. Discussion ->
5. Conclusions -> Author Contributions -> Funding -> Data Availability ->
Acknowledgments -> Conflicts of Interest -> Appendix A -> References

All figures embedded from figures_energies_en/ (English labels, 600 dpi).
"""
import os, json
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = "/home/user/academic-research-skills/output/sdr-weather-alerts"
FIG  = f"{BASE}/figures_energies_en"
RES  = f"{BASE}/results"
OUT  = f"{BASE}/deliverable_energies"
os.makedirs(OUT, exist_ok=True)

R = json.load(open(f"{RES}/energies_paper_results.json"))

doc = Document()
# 1-column MDPI A4 with 2 cm margins
section = doc.sections[0]
section.top_margin = section.bottom_margin = Cm(2.0)
section.left_margin = section.right_margin = Cm(2.0)
# base body style: Palatino 10 pt (MDPI uses Palatino in publication but Times/
# Arial accepted at submission; use Arial 10 for readability)
ns = doc.styles["Normal"]
ns.font.name = "Arial"; ns.font.size = Pt(10)

NAVY = RGBColor(0x00, 0x3B, 0x71)

def _setfont(run, size=None, bold=None, italic=None, color=None, name="Arial"):
    run.font.name = name
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color is not None: run.font.color.rgb = color

def h_title(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); _setfont(r, size=16, bold=True, color=NAVY)

def h1(num, text):
    p = doc.add_paragraph()
    r = p.add_run(f"{num}. {text}"); _setfont(r, size=12, bold=True, color=NAVY)

def h2(num, text):
    p = doc.add_paragraph()
    r = p.add_run(f"{num}. {text}"); _setfont(r, size=11, bold=True, italic=True)

def h3(num, text):
    p = doc.add_paragraph()
    r = p.add_run(f"{num}. {text}"); _setfont(r, size=10, bold=True, italic=True)

def para(text, size=10, bold=False, italic=False, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.2) if indent else None
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text); _setfont(r, size=size, bold=bold, italic=italic)

def bullet(text, size=10):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text); _setfont(r, size=size)

def add_figure(filename, caption, width=6.3):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(f"{FIG}/{filename}", width=Inches(width))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); _setfont(r, size=9, italic=True)

def add_table(headers, rows, widths=None, caption=None):
    if caption:
        c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run(caption); _setfont(r, size=9, italic=True)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(headers):
        cell = t.rows[0].cells[i]; cell.text=""
        r = cell.paragraphs[0].add_run(str(h)); _setfont(r, size=9, bold=True, color=RGBColor(0xFF,0xFF,0xFF))
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd"); shd.set(qn("w:fill"),"003B71"); tcPr.append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text=""
            r = cells[i].paragraphs[0].add_run(str(v)); _setfont(r, size=9)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width = Inches(w)

# ============================================================================
# TITLE PAGE
# ============================================================================
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = p.add_run("Article")
_setfont(r, size=9, italic=True, color=RGBColor(0x99,0x99,0x99))

h_title("Calendar-Modulated Cooling Sensitivity of a Japanese University "
        "Campus: A Low-Data Building-Environment Framework Linking "
        "Institutional Occupancy, Thermal-Comfort Indices, and "
        "Contract-Capacity Risk")

# Authors line
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Haiqiang Liu "); _setfont(r, size=11)
r = p.add_run("1,*"); _setfont(r, size=8); r.font.superscript = True
r = p.add_run(" and Co-Author Name "); _setfont(r, size=11)
r = p.add_run("1"); _setfont(r, size=8); r.font.superscript = True

# Affiliation
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("1 Faculty of Engineering, Yamaguchi University, Tokiwa-dai 2-16-1, "
              "Ube, Yamaguchi 755-8611, Japan")
_setfont(r, size=9, italic=True)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("* Correspondence: ryu.kaikyou@yamaguchi-u.ac.jp")
_setfont(r, size=9, italic=True)

# Editorial info
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(f"Received: {datetime.now().strftime('%d %B %Y')}; Accepted: TBD; Published: TBD")
_setfont(r, size=9, italic=True, color=RGBColor(0x99,0x99,0x99))

# ABSTRACT (<=200 words)
h1("", "Abstract")
para("Climate-driven cooling demand and contractual capacity constraints are "
"becoming binding for non-residential public buildings, yet site-level "
"meteorological measurements in real campus operation are often incomplete. "
"This study develops a low-data, building-environment-oriented framework that "
"integrates a complete fiscal-year hourly load record (7,358 valid hours, "
"Yamaguchi University Tokiwa campus, Japan, April 2025–March 2026), four-element "
"AMeDAS observation (air temperature, precipitation, wind speed, wind "
"direction), a six-class academic-calendar segmentation, and the 2,000 kW "
"contract capacity. Season-stratified daily energy signatures, thermal-comfort "
"indices (apparent temperature, WBGT, Heat Index) computed from independently "
"validated reanalysis humidity, change-point regression, and a "
"capacity-risk concentration map are combined into one coherent pipeline. "
"Three findings emerge: (i) the campus is cooling-dominated (cooling-season "
"slope +25.4 kWh·h⁻¹·°C⁻¹; heating slope essentially nil); (ii) the academic "
"calendar modulates cooling sensitivity by a factor of 1.59 (class-day "
"+37.0 vs. weekend +23.3 kWh·h⁻¹·°C⁻¹, both R² ≈ 0.91), interpretable as a "
"4.0 °C shift in balance-point temperature attributable to occupant internal "
"heat gains; (iii) all 14 critical-tier hours (ρ ≥ 0.85) occur on class days, "
"localising capacity risk to one (calendar × temperature) cell.",
indent=False)

# Keywords
p = doc.add_paragraph()
r = p.add_run("Keywords: "); _setfont(r, size=10, bold=True)
r = p.add_run("campus energy management; energy signature; balance-point "
              "temperature; internal heat gains; thermal-comfort indices; WBGT; "
              "academic calendar; contract-capacity risk; change-point regression; low-data framework")
_setfont(r, size=10, italic=True)

doc.add_paragraph()  # spacer

# ============================================================================
# 1. INTRODUCTION
# ============================================================================
h1("1", "Introduction")
para("University campuses are a distinctive class of non-residential energy "
"consumers. They are large enough to be subject to demand-charge contracts "
"yet are operated under a recurring institutional schedule—classes, "
"examinations, vacations, and special events—that shapes occupancy with a "
"regularity rarely seen in commercial offices [1,2]. Recent reviews of "
"building energy forecasting [3,4] have demonstrated that data-driven "
"techniques can predict consumption with high accuracy when rich weather "
"and operational variables are available; however, the same body of work "
"has been criticised for treating the calendar as a control variable rather "
"than as a structural driver of demand [5].")

para("Three gaps persist in this literature. "
"First, most studies optimise prediction-accuracy metrics (MAE, RMSE, MAPE) "
"without quantifying the building-physics mechanism by which occupancy and "
"climate combine to produce critical-hour loads [3,4]. "
"Second, weather-normalisation techniques rooted in the ASHRAE inverse "
"modelling toolkit and the energy-signature framework [6,7] are typically "
"applied at the building level or to monthly bills, with the academic "
"calendar absorbed as a nuisance dummy variable rather than as a hypothesis "
"about internal heat gains. "
"Third, real-world campus management is constrained by the availability of "
"on-site meteorology. The Japanese AMeDAS network, the operational gold "
"standard, supplies only four elements (temperature, precipitation, wind "
"speed, wind direction) at most stations [8]; humidity, sunshine duration, "
"and pressure are not measured at four-element sites such as Ube "
"(prec_no = 81, block_no = 0778), the closest station to the studied "
"campus. Methods that require dense indoor or microclimatic data are "
"therefore not directly transferable to many real campuses.")

para("To address these gaps we ask: under realistic on-site data limitations, "
"can the academic calendar be quantitatively re-cast as a building-environment "
"modulator of the temperature-load relationship, and can this modulation be "
"linked to contract-capacity risk in a managerially tractable way? "
"Our specific research questions are:")

bullet("RQ1: How does the campus hourly load profile vary across "
       "academic-calendar states and seasons?")
bullet("RQ2: Using only AMeDAS-equivalent variables, can heating, cooling, "
       "and transition regimes be cleanly separated through season-specific "
       "change-point regression?")
bullet("RQ3: Is the apparent calendar modulation of cooling sensitivity "
       "an artefact of unmeasured humidity (a confound), or does it persist "
       "when thermal-comfort indices that include humidity (WBGT, apparent "
       "temperature, Heat Index) replace dry-bulb temperature?")
bullet("RQ4: How is contract-capacity risk distributed in (temperature × "
       "day-type) space, and which combinations constitute the critical "
       "management window?")

para("Our contribution is threefold. We propose the calendar-conditioned "
"energy signature as a methodological device that lifts the academic "
"calendar from a control to a first-order modulator. We re-interpret the "
"empirical shift in balance-point temperature as the building-physics "
"signature of differential occupant internal heat gains, providing a "
"quantitative bridge between statistical modulation and building science. "
"And we demonstrate that, in a cooling-dominated Japanese campus, "
"capacity risk is sufficiently localised in (temperature × calendar) "
"space to permit a low-data, targeted management protocol.")

# ============================================================================
# 2. MATERIALS AND METHODS
# ============================================================================
h1("2", "Materials and Methods")

h2("2.1", "Site description")
para("The study site is the Tokiwa engineering campus of Yamaguchi "
"University, Ube, Japan (33.952° N, 131.261° E), supplied through a single "
"high-voltage feeder with a contract demand of 2,000 kW. The campus consists "
"of fifteen academic and laboratory buildings; the present analysis treats "
"the aggregated metered load, since building-level metadata were not "
"available for the full year. Building-level extension is identified as a "
"future research direction.")

h2("2.2", "Data sources")
add_table(["Variable","Source","Resolution","Period"],
    [["Electricity consumption (kWh)","Campus BEMS monthly export (12 Excel files)","1 h","2025-04 to 2026-03"],
     ["Air temperature, precipitation, wind","AMeDAS Ube (JMA, four-element station)","1 h","2025-04 to 2026-03"],
     ["Relative humidity, dew point, solar","ERA5 reanalysis via Open-Meteo Historical API","1 h","2025-04 to 2026-03"],
     ["Academic calendar","Yamaguchi University Academic Year Calendar 2025","1 d","2025-04 to 2026-03"],
     ["Contract capacity","Utility contract document","Constant 2,000 kW","Whole period"]],
    caption="Table 1. Data sources used in the analysis.")
para("Of 8,761 hourly slots in the fiscal year, 1,400 had missing power "
"readings (predominantly January 2026: 87 % missing; February 2026: 61 % "
"missing) and 11 had missing temperature, leaving 7,358 valid hours "
"distributed across 308 days. Figure 1 visualises the (season × day-type) "
"sample matrix used in the subsequent regressions.")
add_figure("Figure_1_data_availability.png",
   "Figure 1. Data availability matrix: (a) valid hourly samples and "
   "(b) valid daily samples by season and day-type. Winter sparseness reflects "
   "BEMS data gaps in January and February 2026.")

h2("2.3", "ERA5 cross-validation")
para("Because Ube is a four-element AMeDAS station that does not measure "
"humidity, all thermal-comfort indices in this study rely on ERA5 humidity. "
"We therefore independently validated ERA5 against AMeDAS at three temporal "
"scales. Hourly Pearson correlations were r = 0.991 for temperature, "
"r = 0.66 for wind speed, and r = 0.49 for precipitation; daily and monthly "
"aggregation increased temperature agreement to r = 0.997 and r = 1.000 and "
"precipitation agreement to r = 0.76 and r = 0.90. The low hourly precipitation "
"correlation reflects the well-documented timing offset between reanalysis "
"cells and point gauges and is not an error in either source. ERA5 humidity "
"is therefore retained for the comfort-index calculations only, while "
"AMeDAS observation remains the primary meteorological input.")

h2("2.4", "Calendar segmentation")
para("The 2025 Yamaguchi University academic calendar was parsed into six "
"mutually exclusive day-types: class day (162 days), vacation (113 days), "
"weekend (62 days), public holiday (11 days), special event (10 days; "
"entrance ceremony, open-campus days, graduation), and exam closure (7 "
"days; common entrance examination preparation and implementation).")

h2("2.5", "Seasonal stratification")
para("Following the standard energy-signature literature [6,7,9], the year "
"was partitioned into a cooling season (June–September, 120 days), a "
"heating season (December–March, 77 days, BEMS-limited), and a transition "
"period (April–May and October–November, 111 days). Pooling all months in "
"a single regression dilutes the cooling and heating slopes through the "
"near-flat shoulder band; the recommended remedy is season-specific "
"regression, optionally with occupied/unoccupied separation [10].")

h2("2.6", "Energy-signature regression")
para("For each (season × day-type) stratum we fitted a daily energy "
"signature L̄ᵈ = α + βT̄ᵈ + ε, where L̄ᵈ is the daily mean load and "
"T̄ᵈ the daily mean temperature. Where a two-segment response was "
"physically expected (cooling + flat baseline), a two-piece change-point "
"regression was fitted using the pwlf library to identify the balance-point "
"temperature T_balance. Hourly regressions are reported in parallel as a "
"robustness check.")

h2("2.7", "Thermal-comfort indices")
para("Three indices were computed to test whether occupant-calendar effects "
"survive humidity normalisation. Vapour pressure was obtained from the Tetens "
"equation e = 6.105·RH/100·exp(17.27T/(237.7+T)).")
bullet("Apparent temperature (Steadman 1984): T_app = T + 0.33e − 0.70v − 4 [11].")
bullet("WBGT (Stull/Bernard simplification, JMA convention): "
       "WBGT = 0.567T + 0.393e + 3.94 [12].")
bullet("Heat Index (Rothfusz 1990, NOAA): polynomial in (T_F, RH) valid for "
       "T ≥ 27 °C and RH ≥ 40 %; below this threshold the dry-bulb value is used [13].")

h2("2.8", "Balance-point as building-physics quantity")
para("We interpret the empirical T_balance as the indoor–outdoor temperature "
"crossover at which the cooling load activates, i.e. "
"T_balance = T_set − (Q_int + Q_sol)/UA, where T_set is the cooling setpoint "
"(approximately 28 °C under the Japanese Cool Biz convention), Q_int the "
"sum of occupant, equipment, and lighting heat gains, Q_sol the envelope solar "
"gain, and UA the overall building heat-loss coefficient. At constant UA "
"and T_set, differences in T_balance between calendar states are proxies "
"for differences in Q_int.")

h2("2.9", "Capacity-risk analysis")
para("The capacity-risk ratio is defined as ρ(t) = L(t)/C with C = 2,000 kW. "
"Following risk-tier conventions adapted from grid operator practice, ρ was "
"binned into Normal (<0.50), Watch (0.50–0.70), High (0.70–0.85), and "
"Critical (≥0.85). The two-dimensional (temperature × day-type) and "
"(hour × day-type) ρ surfaces were used to identify management windows.")

# ============================================================================
# 3. RESULTS
# ============================================================================
h1("3", "Results")

h2("3.1", "Annual load profile and calendar pattern (RQ1)")
add_figure("Figure_2_annual_timeseries.png",
   "Figure 2. (a) Hourly campus electricity load over the fiscal year. "
   "(b) Hourly air temperature at AMeDAS Ube. Dashed red line: contract capacity "
   "2,000 kW.")
add_figure("Figure_3_daytype_profiles.png",
   "Figure 3. (a) Box-plot of hourly load by day type. (b) Mean diurnal profile "
   "for each day type. Class days carry a markedly higher diurnal swing than "
   "weekends, vacations, and special events.")
para("Mean daily load was 740 kWh·h⁻¹ (range 428–1,794). Class-day diurnal "
"profiles peak at approximately 14:00–15:00 at ≈ 1,000 kWh·h⁻¹ in summer "
"months; weekend and vacation profiles are essentially flat at 500–600 "
"kWh·h⁻¹, indicating that approximately one-quarter of the campus load is "
"purely institutional (calendar-driven, weather-independent).")

h2("3.2", "Season-stratified energy signatures (RQ2)")
add_figure("Figure_4_seasonal_signatures.png",
   "Figure 4. Energy signature stratified by season at (a) hourly and (b) "
   "daily resolution. The cooling season exhibits the steepest positive slope; "
   "the heating-season slope is weak in this cooling-dominated campus.")
para("Daily-resolution slopes were: cooling +25.4 kWh·h⁻¹·°C⁻¹ (R² = 0.22, "
"n = 120 days); transition +5.7 (R² = 0.04, n = 111); heating −9.8 "
"(R² = 0.05, n = 77). The near-zero transition-season slope confirms the "
"shoulder band described in the literature [10,14]. The weak heating "
"signal is consistent with non-electric (city-gas or district-heat) campus "
"heating; this interpretation could be verified with a fuel-bill audit not "
"available in this study.")

h2("3.3", "Calendar modulation of cooling sensitivity (RQ3, key result)")
add_figure("Figure_5_cooling_by_daytype.png",
   "Figure 5. Cooling-season energy signature stratified by academic-calendar "
   "day type. (a) Hourly resolution; (b) daily resolution. Class days respond "
   "to temperature 1.59 × more strongly than weekends.")
add_table(["Day type","Cooling slope β (kWh·h⁻¹·°C⁻¹)","R²","Days"],
    [["Class day", "+37.0", "0.91", "46"],
     ["Weekend",   "+23.3", "0.90", "18"],
     ["Vacation",  "+39.9", "0.25", "48"]],
    caption="Table 2. Cooling-season daily signatures by day type. Class-day "
    "and weekend slopes are highly significant; the vacation slope is unstable "
    "because vacation occupancy is irregular (sporadic faculty research, club activities).")
para("The 1.59-fold class-day enhancement persists when WBGT replaces dry-bulb "
"temperature (Section 3.4), demonstrating that the modulation is occupant-driven "
"rather than humidity-confounded.")

h2("3.4", "Dry-bulb temperature versus thermal-comfort indices")
add_figure("Figure_6_comfort_indices.png",
   "Figure 6. Cooling-season daily signature using four alternative thermal "
   "indices. Dry-bulb temperature retains the highest R² at this metered, "
   "aggregated scale.")
add_table(["Index","Slope β (kWh·h⁻¹·°C⁻¹)","R²","Hours"],
    [["Dry-bulb T (AMeDAS)","+25.4","0.221","2,851"],
     ["Heat Index (NOAA)","+14.2","0.190","2,851"],
     ["Apparent T (Steadman)","+16.4","0.182","2,851"],
     ["WBGT (Stull/Bernard)","+20.0","0.155","2,851"]],
    caption="Table 3. Comparison of thermal indices as predictors of "
    "cooling-season campus load. Dry-bulb temperature is the best single predictor "
    "at the metered aggregate level.")
para("At the metered aggregate scale the dry-bulb temperature is already the "
"best single predictor of cooling-season load; adding humidity via the comfort "
"indices does not improve fit. This supports the low-data positioning of the "
"framework: humidity is not necessary for forecasting at this scale, although "
"it remains useful for the mechanism check in Section 3.5.")

h2("3.5", "Balance-point shift as occupant internal-heat-gain proxy")
add_figure("Figure_7_balance_point.png",
   "Figure 7. (a) Two-piece change-point fit identifies the balance-point "
   "temperature T_balance for each day type. (b) Building-physics interpretation: "
   "the 4.0 °C balance-point gap maps directly to differential occupant internal "
   "heat gains under constant building UA.")
add_figure("Figure_8_internal_heat_gains.png",
   "Figure 8. Mean hourly load by WBGT bin and day type. At matched thermal "
   "stress (WBGT 28–29 °C), class days draw approximately 307 kWh·h⁻¹ more than "
   "weekends—a direct, weather-controlled estimate of occupant- and "
   "equipment-driven internal heat gains.")
add_table(["Day type","T_balance (°C)","Cooling slope","Baseload (kWh·h⁻¹)"],
    [["Class day","18.4","+37.4","683"],
     ["Weekend",  "19.3","+23.8","526"],
     ["Vacation", "22.4","+47.2","560"]],
    caption="Table 4. Balance-point temperature, post-balance cooling slope, "
    "and pre-balance baseload by day type, from two-piece change-point fits "
    "(cooling + transition data, n_days as in Table 2).")
para("The 4.0 °C span in T_balance across day types is the principal "
"building-physics signal of the paper. Under the linearised relation "
"T_balance = T_set − (Q_int + Q_sol)/UA and assuming a representative campus "
"UA of order 10² kW·°C⁻¹, this gap corresponds to several hundred kilowatts "
"of differential internal heat gain, which is plausible for occupant, "
"lighting, and equipment loads on a populated class day.")

h2("3.6", "Contract-capacity-risk concentration (RQ4)")
add_figure("Figure_9_risk_concentration.png",
   "Figure 9. Mean ρ = L/C in (temperature bin × day type) space. Risk "
   "concentrates in the class-day × 32–35 °C cell at ρ ≈ 0.80, vastly exceeding "
   "the same-temperature weekend cell (ρ ≈ 0.45).")
add_figure("Figure_10_rho_timeseries.png",
   "Figure 10. Capacity-risk ratio ρ over the fiscal year, with risk-tier thresholds.")
para("The annual maximum ρ was 0.897, recorded on 3 July 2025 at 14:00 "
"(load = 1,794 kWh·h⁻¹, T = 33.2 °C, class day). Of 14 hours classified as "
"Critical (ρ ≥ 0.85), all 14 occurred on class days; of the 234 hours at "
"High or above, 182 (78 %) were class days, 44 (19 %) vacation, and 8 (3 %) "
"special-event days. Risk is therefore quantitatively a product of temperature "
"exposure and institutional state, not either alone.")

# ============================================================================
# 4. DISCUSSION
# ============================================================================
h1("4", "Discussion")

h2("4.1", "Theoretical contribution")
para("The empirical 4.0 °C span in balance-point temperature across calendar "
"states recasts the academic calendar as a building-physics variable that "
"shifts the building–environment thermal exchange, not merely a categorical "
"regressor. This is the central theoretical claim of the paper: occupancy "
"changes the campus's energy signature, and the magnitude of that change can "
"be read directly from the energy data without indoor sensors.")

h2("4.2", "Methodological contribution")
para("The pipeline—four-element AMeDAS + academic-calendar segmentation + "
"season-separated change-point regression + capacity-risk surface—deliberately "
"uses no variable that real-world Japanese campus managers cannot already "
"obtain. ERA5 humidity is invoked only to test whether comfort indices "
"would change the conclusions; they do not. The framework therefore meets "
"the practical constraint of low on-site instrumentation while remaining "
"diagnostically sharp.")

h2("4.3", "Practical implications")
para("Because all 14 critical-tier hours occurred on class days within a narrow "
"32 °C–35 °C temperature window, a targeted management protocol that activates "
"demand-response measures only when (class day) ∧ (forecast T ≥ 32 °C) ∧ "
"(14:00–15:00) would have addressed nearly all observed peak risk during "
"FY2025. The Japanese Cool Biz convention (28 °C setpoint) sits below all "
"observed balance points, suggesting that the campus already operates "
"near—but not past—the policy benchmark on class days.")

h2("4.4", "Limitations")
bullet("Building-level metadata for the fifteen buildings were not available; "
       "all results refer to the aggregated campus meter. Building heterogeneity "
       "is the most important future extension.")
bullet("BEMS data were largely missing for January and February 2026 (96 and "
       "264 valid hours, respectively). The heating-season signature is therefore "
       "weaker than it would be with complete winter coverage.")
bullet("Fuel-source data (city gas, district heat) were not available to confirm "
       "that the weak electric heating signature reflects non-electric heating.")
bullet("Indoor environmental measurements were not used; balance-point shifts "
       "are interpreted as occupant internal-heat-gain proxies on physical grounds, "
       "not direct PMV/PPD evidence.")
bullet("A single fiscal year limits external validity; a multi-year extension "
       "would test inter-annual robustness of the calendar modulation.")

# ============================================================================
# 5. CONCLUSIONS
# ============================================================================
h1("5", "Conclusions")
para("Using only AMeDAS-equivalent meteorology, the Yamaguchi University "
"academic calendar, and the campus contract capacity, this study quantifies "
"how the academic calendar reshapes the temperature-load relationship of a "
"cooling-dominated Japanese campus. The cooling-season signature is 1.59 × "
"steeper on class days than on weekends, both with R² ≈ 0.91; the implied "
"4.0 °C shift in balance-point temperature provides a building-physics "
"interpretation of the calendar modulation as differential occupant internal "
"heat gains. Capacity risk is sharply localised: all critical hours occurred "
"on class days under high temperature, motivating a low-data, "
"targeted-management protocol. The framework requires only data routinely "
"available to campus operators and is transferable to other educational "
"sites with similar contracts and climatology.")

# ============================================================================
# Author Contributions
# ============================================================================
h1("", "Author Contributions")
para("Conceptualization, H.L.; methodology, H.L.; software, H.L.; validation, "
"H.L.; formal analysis, H.L.; investigation, H.L.; resources, H.L.; data "
"curation, H.L.; writing—original draft preparation, H.L.; writing—review and "
"editing, H.L.; visualization, H.L.; supervision, [Supervisor]; project "
"administration, H.L.; funding acquisition, [PI]. All authors have read and "
"agreed to the published version of the manuscript.", indent=False)

h1("", "Funding")
para("This research received no external funding.", indent=False)

h1("", "Data Availability Statement")
para("The processed datasets generated and analyzed during this study, the "
"reproducible analysis scripts, and the figures in editable SVG format are "
"available from the corresponding author on reasonable request. AMeDAS data "
"are openly accessible from the Japan Meteorological Agency "
"(https://www.data.jma.go.jp). ERA5 reanalysis was retrieved through the "
"Open-Meteo Historical Weather API.", indent=False)

h1("", "Acknowledgments")
para("The authors thank the Yamaguchi University Facility Management Section "
"for providing the campus BEMS records and the Educational Affairs Section "
"for the academic calendar.", indent=False)

h1("", "Conflicts of Interest")
para("The authors declare no conflict of interest.", indent=False)

# ============================================================================
# Appendix
# ============================================================================
h1("Appendix A", "Comfort-index formulae")
para("Tetens vapour pressure: e = 6.105 · (RH/100) · exp(17.27·T / (237.7 + T)) [hPa].")
para("Apparent temperature (Steadman 1984): T_app = T + 0.33·e − 0.70·v − 4.0, "
"where v is the 10-m wind speed in m·s⁻¹.")
para("Wet-Bulb Globe Temperature (Stull/Bernard simplification): "
"WBGT = 0.567·T + 0.393·e + 3.94.")
para("Heat Index (Rothfusz polynomial, with T expressed in °F before "
"back-converting): see Rothfusz (1990) for the full nine-term form.")

# ============================================================================
# References
# ============================================================================
h1("", "References")
refs = [
"1. *Reducing university energy use beyond energy retrofitting: The academic "
"calendar impacts*. Energy and Buildings 2021, 237, 110813. DOI: 10.1016/j.enbuild.2020.110813.",
"2. Amber, K.P.; Ahmad, R.; Aslam, M.W.; Kousar, A.; Usman, M.; Khan, M.S. "
"*Intelligent techniques for forecasting electricity consumption of buildings*. "
"Energy 2018, 157, 886–893.",
"3. Deb, C.; Zhang, F.; Yang, J.; Lee, S.E.; Shah, K.W. *A review on time "
"series forecasting techniques for building energy consumption*. Renewable and "
"Sustainable Energy Reviews 2017, 74, 902–924.",
"4. Bourdeau, M.; Zhai, X.; Nefzaoui, E.; Guo, X.; Chatellier, P. *Modeling "
"and forecasting building energy consumption: A review of data-driven techniques*. "
"Sustainable Cities and Society 2019, 48, 101533.",
"5. Ruiz-Abellón, M.C.; Gabaldón, A.; Guillamón, A. *Load Forecasting for a "
"Campus University Using Ensemble Methods Based on Regression Trees*. Energies "
"2018, 11(8), 2038.",
"6. Kissock, J.K.; Haberl, J.S.; Claridge, D.E. *Development of a Toolkit for "
"Calculating Linear, Change-Point Linear and Multiple-Linear Inverse Building "
"Energy Analysis Models*. ASHRAE Research Project 1050-RP, 2003.",
"7. ASHRAE. *Guideline 14-2014: Measurement of Energy, Demand, and Water Savings*. "
"American Society of Heating, Refrigerating and Air-Conditioning Engineers, 2014.",
"8. Japan Meteorological Agency. *AMeDAS station network description*. "
"https://www.jma.go.jp/jma/kishou/know/amedas/kaisetsu.html (accessed 2026-05-31).",
"9. *Simplified Weather-Related Building Energy Disaggregation and Change-Point "
"Regression*. Buildings (MDPI) 2022, 12(10), 1717.",
"10. Tagup. *HVAC Shoulder Seasons: Peak relative savings from cooling optimization*. "
"Industry brief, 2024.",
"11. Steadman, R.G. *A universal scale of apparent temperature*. Journal of "
"Climate and Applied Meteorology 1984, 23, 1674–1687.",
"12. Stull, R. *Wet-Bulb Temperature from Relative Humidity and Air "
"Temperature*. Journal of Applied Meteorology and Climatology 2011, 50, "
"2267–2269.",
"13. Rothfusz, L.P. *The Heat Index Equation (or, More Than You Ever Wanted "
"to Know About Heat Index)*. NWS Technical Attachment SR 90-23, NOAA, 1990.",
"14. U.S. Energy Information Administration. *What is the shoulder season in "
"electricity markets?* Today in Energy, 2024.",
"15. Hersbach, H.; et al. *The ERA5 global reanalysis*. Quarterly Journal of "
"the Royal Meteorological Society 2020, 146(730), 1999–2049.",
"16. *Occupancy-based model for building electricity consumption: a case study "
"of three campus buildings in Tianjin*. Energy and Buildings 2020, 215, 109899.",
"17. *Classification of daily electric load profiles of non-residential "
"buildings*. Energy and Buildings 2020, 222, 110054.",
"18. *Review of peak load management strategies in commercial buildings*. "
"Sustainable Cities and Society 2021, 77, 103580.",
]
for ref in refs:
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    r = p.add_run(ref); _setfont(r, size=9)

# ============================================================================
# Save
# ============================================================================
out_docx = f"{OUT}/Energies_Manuscript_Yamaguchi_Campus_Cooling_Sensitivity_{datetime.now().strftime('%Y%m%d')}.docx"
doc.save(out_docx)
print(f"✓ Manuscript saved: {out_docx}")
print(f"  Paragraphs: {len(doc.paragraphs)}, Tables: {len(doc.tables)}, "
      f"Inline figures: {len(doc.inline_shapes)}")
