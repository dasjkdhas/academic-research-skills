# 01 — Refined Thesis Statement

> **Working file for**: *Morphological Thresholds of Blue-Green Infrastructure for Land Surface Cooling in a Temperate Mid-Sized City: Evidence from Kumamoto, Japan*
> **Target journal**: *Urban Climate* (Elsevier)
> **Paper stage**: Mid-stage (complete draft, framework revision)

---

## 1. Current Implicit Thesis (extracted from draft)

The draft does not state a single thesis sentence. Reconstructed from §1, §2.4, and the Abstract:

> *"BGI morphology, beyond quantity, shapes urban land surface cooling, and these effects follow threshold-like rather than monotonic patterns in a temperate mid-sized city such as Kumamoto."*

### Diagnosis
- **Too broad**: Covers morphology + quantity + composite + reach in one breath.
- **Not falsifiable**: "shapes" is too weak — what would count as evidence against it?
- **No control claim**: Does not specify that morphology effects are *residual* after controlling area/NDVI.
- **No mechanism**: Says *what* but not *why* — Urban Climate reviewers will request a mechanism.

---

## 2. Recommended Refined Thesis (two-sentence version)

> **In a temperate mid-sized city, the morphology of blue-green infrastructure (BGI) — operationalized as green-space LSI and water-body shape complexity — explains residual variance in land surface cooling that remains after BGI quantity and vegetation condition are accounted for, and this relationship is non-monotonic with empirically identifiable threshold bands (LSI < 4; WBSI ≈ 9 in Kumamoto). Composite BGI configurations further extend the spatial reach of cooling when aligned with prevailing summer winds, supporting an "extension" rather than "replacement" of quantity-based BGI cooling theory.**

### Why this version works

| Property | How it is satisfied |
|---|---|
| **Specificity** | Names the metrics (LSI, WBSI), the scale (mid-sized city), and the empirical band |
| **Falsifiability** | Fails if (a) morphology coefficient is insignificant after controlling area + NDVI, OR (b) the relationship is monotonic rather than threshold-like, OR (c) composite configurations show no spatial reach advantage |
| **Scope honesty** | Limited to Kumamoto; theory positioned as *extension*, not universal law |
| **Contribution claim** | Explicitly: morphology explains *residual* variance — a stronger position than "morphology matters too" |

---

## 3. Falsifiability Test (Pre-Mortem)

What evidence would force us to abandon this thesis?

| Test | Falsification trigger | Current data answer |
|---|---|---|
| Control test | If a regression of LST on area + NDVI fully explains variance | ⚠️ Not run — must add multi-variable regression |
| Monotonicity test | If LSI–LST relationship is linear (no turning point) | ✅ §4.4 evidence supports threshold |
| Composite test | If single-element BGI achieves same reach as composite | ⚠️ Not directly tested — only described |
| Wind interaction test | If cooling reach is similar regardless of wind direction | ⚠️ Only one wind condition observed |

**Action items**: Three of four tests are under-supported by current data. Either:
- (a) Run a multivariable regression on the Lake Ezu data to support the "residual variance" claim, OR
- (b) Soften the thesis to "morphology shows threshold-like associations with LST after accounting for area and NDVI" (associational, not residual-variance).

**Recommendation**: Option (b) — softer language is defensible with current data; option (a) requires re-running analysis.

---

## 4. Final Thesis (associational version, defensible with existing data)

> **In a temperate mid-sized city, blue-green infrastructure morphology — measured by green-space LSI and water-body shape complexity — shows threshold-like, non-monotonic associations with land surface cooling that are not fully captured by BGI quantity or vegetation condition alone (LSI < 4 and WBSI ≈ 9 mark observable threshold bands in Kumamoto). Composite BGI configurations are associated with extended cooling reach (up to ≈ 1.5 km) under directional wind alignment, supporting an extension of quantity-based BGI cooling frameworks rather than their replacement.**

This version:
- Uses **"associations"** not "explains residual variance" → no multivariable regression required
- Hedges generalizability with **"observable in Kumamoto"**
- Frames composite + reach as **conditional** on wind direction
- Positions contribution as **extension** of existing theory (less aggressive, more publishable)

---

## 5. Title Realignment

Current title: *"Morphological Thresholds of Blue-Green Infrastructure for Land Surface Cooling in a Temperate Mid-Sized City: Evidence from Kumamoto, Japan"*

The title is acceptable but **over-promises a tight threshold framing** while the paper actually covers area, NDVI, morphology, composite, and reach.

**Two options**:

- **Option A — keep title, narrow Results**: Subordinate §4.1-4.3 to background, foreground §4.4. (Recommended.)
- **Option B — broaden title**: e.g., *"Quantity, Form, and Configuration: A Multi-Scale Assessment of Blue-Green Infrastructure Cooling in Kumamoto, Japan"* — broader but loses the "thresholds" hook.

**Recommendation**: Option A. Threshold framing is the paper's novelty; restructure Results to match.
