# Kumamoto BGI Paper — Framework Working Files

> Paper: *Morphological Thresholds of Blue-Green Infrastructure for Land Surface Cooling in a Temperate Mid-Sized City: Evidence from Kumamoto, Japan*
> Authors: Haiqiang Liu et al.
> Target journal: *Urban Climate* (Elsevier)
> Stage: Mid-stage (complete English draft, framework revision)

## Files in this directory

| # | File | Purpose |
|---|---|---|
| 01 | `01_refined_thesis.md` | Diagnoses the implicit thesis, proposes a falsifiable two-sentence version, and aligns the title |
| 02 | `02_thesis_architecture_map.md` | Maps the thesis → 7 sub-claims → chapter sections; reverse-tests each section back to the thesis |
| 03 | `03_argument_backbone.md` | Per-section Claim → Evidence → Reasoning chains, with explicit `[GAP]` markers and recommended fixes |
| 04 | `04_counter_argument_register.md` | 10 counter-arguments scored 1-5 by strength; 4 strength-≥-4 critiques flagged as section blockers |
| 05 | `05_revised_outline.md` | Restructured chapter outline with per-section word allocations, revision actions, and acceptance criteria |

## How to use these files

1. Read in order: 01 → 02 → 03 → 04 → 05.
2. **Decision points** requiring author input:
   - Thesis version (file 01 §4): associational vs residual-variance framing
   - Title (file 01 §5): keep current vs broaden
   - CA1 response (file 04): run partial correlation, or acknowledge as limitation
   - CA9 response (file 04): run multivariable model, or defend univariate design
3. Use file 05 as the working table of contents; mark sections off as you revise.

## Relation to the `academic-paper` skill

This framework was constructed using methods from:

- `academic-paper/agents/socratic_mentor_agent.md` — chapter-by-chapter planning logic
- `academic-paper/agents/argument_builder_agent.md` — CER decomposition
- `academic-paper/agents/structure_architect_agent.md` — outline + word allocation
- `academic-paper-reviewer/references/quality_rubrics.md` — Dimension 4 (Argument Coherence) as evaluation rubric
- `shared/anti_sycophancy_protocol.md` — counter-argument strength thresholds

The 5-file pattern in this directory corresponds to a proposed "pre-outline framework" layer that currently does not exist as an explicit stage in the `academic-paper` skill. If the pattern is useful, it could be promoted into the skill itself as a Phase 1.5 artefact set.

## Next steps

After author review of these files:

1. Resolve decision points (thesis version, title, CA1/CA9 responses)
2. Revise the draft according to `05_revised_outline.md` workflow steps 1-8
3. Self-evaluate against Argument Coherence rubric (target ≥ 80/100)
4. Optionally run the revised draft through `academic-paper-reviewer` for a full multi-perspective review before submission
