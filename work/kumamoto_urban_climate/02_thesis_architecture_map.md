# 02 — Thesis-Architecture Map

> Maps the refined thesis (file `01_refined_thesis.md`) to sub-claims and to the chapters/sections that must carry the burden of proof.

---

## 1. Top Thesis (final associational version)

**T**: BGI morphology in a temperate mid-sized city shows threshold-like, non-monotonic associations with land surface cooling beyond what quantity and vegetation condition capture; composite BGI configurations under directional wind extend cooling reach.

---

## 2. Decomposition into Sub-Claims

| ID | Sub-claim | Required evidence | Current location | Status |
|---|---|---|---|---|
| **C1** | Long-term urban expansion in Kumamoto has restructured the citywide thermal field. | 1976-2021 LULC + LST trends; LULC–LST regressions | §4.1 | ✅ Present — but R² explanation needed |
| **C2** | At the local scale, BGI **area alone** does not fully explain cooling heterogeneity. | Sectors with similar area but different LST | §4.2-4.3 | ✅ Present — but logic of "residual" must be explicit |
| **C3** | **NDVI** matters but is also insufficient; an NDVI optimum near 0.5–0.6 implies non-linearity. | NDVI–LST curve with turning point | §4.3 | ✅ Present — frame as "necessary but not sufficient" |
| **C4** ★ | **Morphology** (LSI for green, shape complexity for water) shows threshold-like LST associations: LSI < 4 and WBSI ≈ 9. | Per-patch LSI/WBSI vs LST scatter or table | §4.4 | ✅ Present — **promote to lead Results section** |
| **C5** | **Composite BGI** configurations + favourable wind = extended cooling reach (≈1.5 km). | Transect data showing 2°C / 3°C thresholds beyond patch edge | §4.5 | ✅ Present — but causal language must be softened |
| **C6** | These thresholds and reach patterns extend, not replace, quantity-based BGI cooling theory. | Discussion synthesis comparing to literature | §5.1-5.2 | ⚠️ Implicit only — make explicit |
| **C7** | The findings are *plausibly* transferable to other temperate mid-sized cities but **not directly generalizable**. | Limitations + transferability statement | §5.4 (limitations) | ⚠️ Present but inconsistent with Abstract |

★ = core contribution claim

---

## 3. Section ↔ Sub-Claim Burden Map

| Section | Carries claim(s) | Supporting evidence type |
|---|---|---|
| §1 Introduction | Frames T (no proof needed; signals it) | Citations only |
| §2 Conceptual Framework (NEW) | Mechanism for C4 (why threshold); positions C6 | Theoretical |
| §3 Methods | Justifies measurement approach for C1–C5 | Design rationale |
| §4.1 Results — citywide | **C1** | 45-year LULC + LST regressions |
| §4.2 Results — quantity insufficient | **C2** + **C3** (merged) | Sector area-LST contrasts + NDVI curve |
| §4.3 Results — morphology thresholds ★ | **C4** | Per-patch LSI/WBSI vs LST |
| §4.4 Results — composite + reach | **C5** | Three transects, 2°C/3°C envelope |
| §5.1 Discussion — beyond area | **C2** + **C4** synthesis | — |
| §5.2 Discussion — mechanism | **C4** mechanism | — |
| §5.3 Discussion — composite | **C5** with conditional language | — |
| §5.4 Discussion — counter-arguments (NEW) | Defends C4, C5 against confounding | — |
| §5.5 Planning implications | **C6** | — |
| §5.6 Limitations | **C7** | — |
| §6 Conclusion | Restates T + contribution | — |

---

## 4. Reverse Test — From section back to thesis

For each Results section, can a reader walk back to **T**?

| Section | Reverse path | OK? |
|---|---|---|
| §4.1 → T | Citywide trend → makes case that BGI cooling matters → motivates C2-C5 → T | ✅ |
| §4.2 (merged) → T | Quantity is insufficient → opens space for morphology → C4 → T | ✅ |
| §4.3 (was §4.4) → T | Threshold patterns directly support C4 → core of T | ✅ |
| §4.4 (was §4.5) → T | Composite reach supports C5 → second clause of T | ✅ (with softened causal language) |

**Verdict**: After restructure, every Results section maps cleanly to a sub-claim and back to T. No section is orphaned.

---

## 5. Identified Orphans / Redundancies

- **§4.2 + §4.3 in current draft** describe the same gap ("area alone insufficient") at two different angles (sector contrast vs NDVI). **→ Merge into single section** "Heterogeneity not explained by quantity or vegetation".
- **§2.1-2.4 in current draft** repeat gap discussion already present in §1.1-1.3. **→ Compress §2 into single subsection of §1, OR replace §2 with a Conceptual Framework section.**
- **§5.4 in current draft** bundles implications + limitations + future work. **→ Split into three subsections.**

---

## 6. Word-Burden Allocation (preview, finalized in file 05)

For a 7,500-word Urban Climate paper:

| Section | Words | % | Justification |
|---|---|---|---|
| Abstract | 250 | 3.3% | Journal limit |
| §1 Introduction (incl. compressed lit) | 1,200 | 16% | Heavier than typical to absorb lit review |
| §2 Conceptual Framework | 500 | 6.7% | Lean — just mechanism + hypotheses |
| §3 Methods | 1,500 | 20% | Multi-scale design needs space + justification |
| §4 Results | 2,000 | 26.7% | Four subsections; §4.3 (thresholds) gets 30% of Results |
| §5 Discussion | 1,800 | 24% | Six subsections incl. counter-arguments |
| §6 Conclusion | 250 | 3.3% | Tight contribution claim |
| **Total** | **7,500** | 100% | Aligns with Urban Climate norms |

Detailed word-count target per subsection in file `05_revised_outline.md`.
