# Model interpretation toolkit ("incognito" workflow)

Goal: give Claude **any** 3D model in a fresh chat without prior knowledge and get back **standardised information** for interpreting it; then write it into the BREC graph.

## Workflow (Windows cmd; commands that belong together are chained in one line)
1. **Measure and render** (local, deterministic):
   `pip install -r requirements.txt && python inspect_model.py my_model.glb --out out`
   → `out/my_model_facts.json` (measurements) and `out/my_model_views.png` (front, right, back, left, top, 3/4).
2. **Build the prompt** (self-contained: rules, JSON schema, format example, facts):
   `python make_prompt.py out/my_model_facts.json`
   → `out/my_model_prompt.md`.
   Optional with owner context: `python make_prompt.py out/my_model_facts.json --context "Scan of a LEGO model, photo attached"` (stored as evidence `owner_note`, not as truth).
3. **Ask in a fresh/incognito chat**: paste the prompt, attach `my_model_views.png` (optionally photos of the real object). Save the answer (pure JSON) as `out/my_model_interpretation.json`.
   **Pass 2 (refinement, recommended):** `python make_prompt.py out/my_model_facts.json --previous out/my_model_interpretation.json` → `out/my_model_prompt2.md`; run it in a fresh chat with the same images, the answer replaces the JSON. Pass 2 re-checks counts (steps, stairs), adds specific named candidates per general hypothesis (`specializes`), separate hypotheses for components (e.g. a figure, `about`) and feature checks.
   Optional without a chat: `pip install anthropic && set ANTHROPIC_API_KEY=... && python ask_claude.py out/my_model_prompt.md out/my_model_views.png` (untested here).
4. **Validate and write into the graph**:
   `python interpretation_to_brec.py out/my_model_interpretation.json --merge ontology/brec.ttl --out brec_merged.ttl && python draw_ident.py brec_merged.ttl en`

## What comes back (schema `brec-model-interpretation/1.1`)
`object` (description, category, construction technique/material, real-size estimate, up axis) · `structure` (shape, levels, symmetry, components, repeated elements) · `capture` (likely origin, defects, floor included) · `evidence` (E1.., source views/facts/photo/owner_note, strength) · `hypotheses` (H1.., confidence, supports/weakens, alternative_to, specializes, candidate with Wikidata search term, **`feature_checks`** expected vs. observed, **`strongest_counterargument`**, **`about`** = component) · `questions_for_owner`.
In the graph: `brec:Identification` → `brec:Evidence` / `brec:IdentityHypothesis` / `brec:CandidateReferent`, plus object, parts and dimensions (CRM E18/E54); the raw JSON is kept as `brec:interpretationJson`.

## What `inspect_model.py` measures
Counts, bounding box, units hint, up-axis estimate (glTF: Y up; otherwise flat-base heuristic), footprint profile along the height (plateaus, type), horizontal surface levels, mirror/90° symmetry, periodic pattern (e.g. stud pitch), dominant colours, mesh quality (merged-vertex topology, boundary edges, components).
Test on our models: the procedural GLB gives 10 raw surface levels (9 without stud tops, 8 equally spaced), `stepped_taper`, 4-fold-like symmetry and a stud pitch of 0.0547 of the extent (expected 0.0556); the raw scan (OBJ) gives an irregular profile (floor included) and low up-axis confidence (0.25), as expected.

## New in 1.1
- `horizontal_surface_levels` separates `count_raw` (includes stud-top levels) from `count_without_stud_tops` and `regular_steps` (equally spaced levels); the views decide the step count.
- Confidence calibration in the prompt (0.1 unlikely ... 0.9 nearly certain); a specific candidate is never more confident than its general case.
- General-to-specific rule and pass 2, so that concrete candidates (building, culture, character type) are proposed.

## Limits
- Heuristic fields can be wrong (listed in the facts as heuristic); the views are authoritative for shape.
- Confidence values are subjective estimates by the model, not measurements; Wikidata identifiers are never produced by the model, only search terms (use `wikidata_match.py`).
- The converter and the schema checks are tested with the example JSON; the prompt was tested with fresh sub-agents without prior knowledge; real photos of the object were not yet supplied in those tests.
- "Incognito" means no conversation history; the model's own knowledge still applies, and `model_id_self_reported` is only self-reported.
