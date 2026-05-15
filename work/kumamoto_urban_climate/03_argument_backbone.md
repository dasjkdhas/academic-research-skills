# 03 — Argument Backbone (CER per chapter)

> Each section's Claim → Evidence → Reasoning chain.
> Marks `[GAP]` where current draft is weak and needs strengthening.

---

## §1 Introduction

**Claim**: Quantity-oriented BGI cooling theory cannot explain why sites of comparable BGI area show different cooling outcomes; morphology is the under-tested dimension that may close this gap, especially in temperate mid-sized cities.

**Evidence**:
- *Quantity supports cooling*: Cao 2010; Bartesaghi Koc 2018; Weng 2009; de Almeida 2021
- *Morphology evidence is mixed*: Zhou 2011 (some shape effects); Liu 2024 (fragmentation may weaken cooling); Irie 2022 (Tokyo case)
- *Mid-sized cities under-studied*: Li 2011 and Zhao 2016 focus on Shanghai (megacity); Rees 2024 on Kharkiv

**Reasoning**:
1. If quantity were sufficient, sites of equal area should have equal cooling → empirical observation refutes this premise
2. Boundary form controls heat-exchange interface and patch coherence → morphology *should* explain residual variance theoretically
3. Existing morphology literature has not converged on monotonic vs. threshold behaviour → an explicit threshold test is needed
4. Mid-sized cities differ from megacities in BGI-built ratio and patch granularity → findings may differ qualitatively

**[GAP]**: Reasoning step 2 is currently asserted, not argued. **Action**: Add 1-2 sentences citing Zhou 2011 mechanism arguments + Coutts 2016 thermal exchange theory.

**[GAP]**: Step 4 transferability claim needs a citation supporting why mid-sized cities specifically deserve separate analysis. **Action**: Cite an urban climate review noting size-class differences (search for one).

---

## §2 Conceptual Framework (NEW SECTION)

**Claim**: BGI cooling has three mechanistic channels (evapotranspiration, shading, edge interaction with surroundings) — only the third is morphology-sensitive, and it is non-linear because edge density has both positive (interface area) and negative (fragmentation) effects.

**Evidence**:
- Evapotranspiration: Weng 2009; Coutts 2016
- Shading: Bartesaghi Koc 2018
- Edge interaction / fragmentation trade-off: Zhou 2011; Liu 2024

**Reasoning**:
1. As shape complexity increases from 1 (compact) → moderate → high (fragmented):
   - Interface area with built surroundings grows → more heat exchange potential
   - Patch core area shrinks → less coherent cooling pool
2. These two opposing effects predict a non-monotonic response: cooling improves up to a complexity threshold, then weakens
3. The same logic applies differently to water (no fragmentation cost; only interface gain) vs. green (both effects active)
4. Hypotheses:
   - **H1**: LSI ↔ LST is non-monotonic with a turning point at low LSI for green
   - **H2**: WBSI ↔ LST is monotonic-with-diminishing-returns for water
   - **H3**: Composite (green + blue + favourable wind) extends reach beyond single-element BGI

**[GAP]**: §2 does not exist in the current draft. **Action**: Write this section using Weng 2009, Coutts 2016, Zhou 2011, Liu 2024 — all already cited. Length: ~500 words.

---

## §3 Materials and Methods

**Claim**: A multi-scale design (45-year citywide + Lake Ezu local) is necessary to disentangle background thermal trends from local morphology effects, and Lake Ezu provides sufficient BGI heterogeneity to test the hypotheses.

**Evidence**:
- 9 time points spanning 1976–2021
- 30 m Landsat resolution
- 8 directional sectors + 3 transects at Lake Ezu
- 5 indicator groups (area, NDVI, LSI, WBSI, cooling reach)

**Reasoning**:
1. Citywide analysis controls for the temporal trend — if local 2021 patterns matched the long-term warming axis, morphology effects would be confounded with secular change
2. Lake Ezu is selected because it offers co-located green + blue + transitional cover within one urban setting — necessary for composite tests
3. Sector + transect designs separate orientation effects from morphology effects
4. Indicator set covers all three mechanisms (quantity, vegetation quality, form)

**[GAP — critical]**: §3.1-3.5 in current draft list *what* was done but rarely *why*. **Action items**:
- §3.2: Add one sentence on why 9 time points (avoiding both data gaps and over-frequent sampling)
- §3.4: Add one sentence on why 900 m grid (matches Kumamoto Green Master Plan; ~10-15 min walking)
- §3.5: Add why Lake Ezu (representativeness vs convenience — be honest)
- §3.5: Add formal definition of WBSI and note its relation to standard LSI (currently ambiguous — see CA5 in file 04)
- §3.6: Add note on spatial autocorrelation handling — currently absent (see CA2 in file 04)

---

## §4.1 Results — Citywide Thermal Background

**Claim** (= C1): Long-term LULC change in Kumamoto has measurably restructured the citywide thermal field, with built-up expansion strongly associated with LST increase and forest/cropland decline associated with warming.

**Evidence**:
- Built-up vs LST: R² = 0.938 (p < 0.01); +10% built-up ↔ +0.3°C
- Forest vs LST: R² = 0.959; +10% forest ↔ −0.2°C
- Cropland vs LST: R² = 0.984; +10% cropland ↔ −0.3°C
- High-temp class surpassed low-temp class by ~2014

**Reasoning**:
1. The 45-year LULC trajectory provides a baseline against which Lake Ezu results are interpreted
2. The high R² indicates strong city-scale coupling between LULC and LST

**[GAP — critical]**: R² values 0.94–0.98 with only 9 time points × N grids are suspiciously high — reviewers will ask about spatial autocorrelation, sample independence, and possible over-fit. **Action**:
- Report sample size (number of grids × time points)
- Add Moran's I or note on spatial autocorrelation
- Consider reporting cross-validated R² or note that R² is descriptive, not predictive
- Soften interpretation: "explains" → "is associated with"

---

## §4.2 Results — Quantity and Vegetation Insufficient (merged from current §4.2 + §4.3)

**Claim** (= C2 + C3): Among Lake Ezu sectors, BGI area and NDVI both correlate with LST in expected directions, but neither fully explains observed heterogeneity — sectors of similar area or NDVI still differ by several °C.

**Evidence**:
- South-southeast: 39% water → lowest LST
- South-southwest: 58% cropland → 2nd lowest LST despite less direct BGI
- East-/north-northeast: lowest BGI → highest LST
- NDVI optimum 0.5–0.6 for cooling efficiency; LST peaks at NDVI ≈ −0.02 (31.43°C)

**Reasoning**:
1. The sector contrasts show that quantity correlates with cooling but does not predict it precisely
2. The NDVI curve shows non-linearity, suggesting vegetation *quality* contributes beyond presence
3. These residual differences motivate the morphology test in §4.3

**[GAP]**: The "residual" framing is currently implicit. **Action**: Add one transition sentence at end of §4.2 explicitly stating that the unexplained between-sector variance motivates the next section.

---

## §4.3 Results — Morphological Thresholds ★ (promoted from current §4.4)

**Claim** (= C4): Both green-space LSI and water-body shape complexity show non-monotonic associations with LST. Empirical threshold bands are identifiable in Kumamoto: LSI < 4 (green) and WBSI ≈ 9 (water).

**Evidence**:
- LSI ↔ LST: minimum LST 27.59°C at LSI = 2.86; LST rises to 30.74°C at LSI = 9.06
- WBSI ↔ LST: LST 27.28°C at WBSI = 9.41; 25.89°C at WBSI = 16.08 (diminishing returns at higher WBSI)

**Reasoning**:
1. Green-space behaviour: cooling improves up to LSI ≈ 4 then weakens — consistent with H1 (fragmentation cost dominates at high complexity)
2. Water-body behaviour: cooling improves monotonically but with diminishing slope — consistent with H2 (no fragmentation cost; only interface benefit)
3. The differing patterns support the conceptual framework's mechanism asymmetry

**[GAP — critical]**: Current evidence is descriptive (single LST minimum per range). Reviewers will want:
- Sample size per range
- Confidence intervals or bootstrap
- A clear figure showing the scatter, not just min values
- Acknowledgement that thresholds are observational, not parametrically fit

**Action**: Add note that thresholds are "empirically identified bands" not "estimated parameters"; supply a Results figure with the full scatter + smoothed curve.

---

## §4.4 Results — Composite BGI and Spatial Reach (was §4.5)

**Claim** (= C5): Composite BGI configurations (water + green + transition cover) are associated with stronger and more extensive cooling than single-element BGI, with cooling reach extending up to ≈1.5 km under prevailing summer wind alignment.

**Evidence**:
- Transect 1: 4.7°C drop within 450 m of central water body; 2°C threshold within ~300 m
- Transect 2: 3°C threshold extends to ~1.5 km in prevailing wind direction
- Transect 3: 4.6°C southwest-to-northeast gradient

**Reasoning**:
1. Composite configurations engage multiple cooling mechanisms simultaneously
2. Wind direction modulates advective transport of cooled air
3. Hence reach is determined by both spatial arrangement AND meteorological conditions

**[GAP — critical]**: Current language ("extended cooling to") is causal. With only 3 transects under one wind condition, this is association, not causation. **Action**: rewrite throughout as "is associated with" / "co-occurred with" — see CA6 in file 04.

---

## §5 Discussion — Synthesis Backbone

**Claim** (= C6 + C7): The Kumamoto findings extend, rather than replace, quantity-based BGI cooling theory by demonstrating that morphology and composite structure contribute additional, mechanism-grounded explanatory layers — with transferability conditional on city-class and climate similarity.

**Evidence**: Synthesis across §4.1–§4.4 + literature

**Reasoning**:
1. Citywide trend (§4.1) confirms classical quantity-driven results
2. Sector contrasts (§4.2) and threshold patterns (§4.3) reveal residuals quantity cannot explain
3. Composite/reach (§4.4) suggests planning configurations matter at neighbourhood scale
4. Together, this is an *extension* of theory — not a refutation
5. Transferability is bounded: results are plausibly informative for other temperate mid-sized cities, but threshold values are city-specific

**[GAP]**: Discussion currently lacks (a) a direct comparison of Kumamoto thresholds to published values in other cities (b) explicit acknowledgment that the contribution is "extension" not "replacement". **Action**: Add comparative table in §5.2 if values exist; add framing sentence in §5.1.

---

## Cross-Section Coherence Check

Read §4.1 → §4.2 → §4.3 → §4.4 in sequence:

| Transition | Status |
|---|---|
| §4.1 → §4.2 | ✅ Citywide trend → narrows to local case at Lake Ezu — natural funnel |
| §4.2 → §4.3 | ⚠️ Needs explicit "residual motivates morphology test" sentence |
| §4.3 → §4.4 | ⚠️ Needs sentence linking patch-level morphology to neighbourhood-scale reach |

**Action**: Add two transition sentences (one at end of §4.2, one at end of §4.3).
