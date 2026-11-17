#!/usr/bin/env python
"""make_prompt.py <facts.json> [--out file.md]: builds ONE self-contained prompt for a fresh ('incognito') chat.
Paste the prompt, attach <stem>_views.png (and optionally photos), save the JSON answer as <stem>_interpretation.json."""
import argparse, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
T = """You are analysing a 3D model with NO prior information. This is a fresh session: you know nothing about the project, the person or the origin of the model. Do not assume a context (toys, archaeology, architecture ...) unless the images or the facts show it.

INPUTS
1. The attached image is a contact sheet with six views of the model (front, right, back, left, top, 3/4). Axes: a and b are the two horizontal axes, "up" is vertical; the front view looks along +b. If photos of the real object are attached as well, treat them as additional evidence (source "photo").
2. FACTS below: objective measurements computed by a script from the mesh. Numbers are reliable; fields described as heuristic can be wrong. The images are authoritative for shape. Note: horizontal_surface_levels.count_raw includes stud tops and is not a number of steps; count the steps in the views.

TASK
Return ONE JSON document that follows the SCHEMA below, so that others can interpret this model without seeing it.

RULES
1. Output JSON only: no markdown fence, no commentary before or after.
2. Keep observation and interpretation apart: "evidence" = statements that can be checked in the views/facts/photos; "hypotheses" = what the object represents or is made of.
3. Give 3 to 8 hypotheses. Include "free design without a real-world model" or "unknown" if plausible. confidence = your subjective estimate from 0 to 1 (0.1 unlikely but possible, 0.3 plausible, 0.5 as likely as not, 0.7 likely, 0.9 nearly certain); hypotheses may overlap and need not sum to 1.
4. Work from general to specific. First state class-level hypotheses (what kind of thing). Then, for each, propose 1 to 3 SPECIFIC named candidates (a real building, culture, period, character type, object type) that would explain the distinctive features, each linked with "specializes" to its general hypothesis and never more confident than it. A specific candidate needs distinctive evidence; if you only have a hunch, give it a low confidence (0.1 to 0.3) instead of omitting it. Hypotheses about a component (for example a figure on top) use "about": "P<n>"; the whole object uses null. Describe each notable component and detail separately (headgear, clothing, symbols, stairs, top structure) and let each carry its own evidence.
5. For every hypothesis fill "feature_checks": features you would expect if the hypothesis were true (for example number of stairs, orientation, proportions, attributes) and whether they are observed (yes, partly, no, unknown) with evidence ids. Fill "strongest_counterargument" with one sentence. Every hypothesis lists at least one supporting evidence id; list weakening evidence where it exists. Use ids E1.., H1.., P1.. exactly.
6. Unknown values are null. Do not invent measurements; numbers come from the facts or are explicitly labelled as estimates (with the basis).
7. wikidata_search_term is a plain English search string, never a Q-identifier (you cannot verify identifiers).
8. questions_for_owner: the questions whose answers would settle the most uncertain points.
9. interpreter.model_id_self_reported is your own model identifier as known to you, or "unknown". It is self-reported and may be wrong.
10. Write all text in English. Use the model_id from the facts.

SCHEMA (JSON Schema)
{schema}

FORMAT EXAMPLE (shows only the structure; it is NOT about this model, do not copy content)
{example}

{context}FACTS
{facts}
"""

PASS2 = """You are refining an earlier interpretation of a 3D model. The attached image is the contact sheet (and photos, if any). Below is YOUR PREVIOUS ANSWER (JSON) and the FACTS.

TASK
Return the complete, improved JSON document (same schema, same rules as before, schema version lrec-model-interpretation/1.1). Concretely:
1. Re-check every evidence statement against the images; correct or add evidence, especially counts (steps, stairs, pillars) and details of components.
2. For each general hypothesis add 1 to 3 specific named candidates (real buildings, cultures, periods, character types, object types) with "specializes", each with feature_checks (expected vs. observed) and a strongest_counterargument. Low confidence is fine, omitting is not.
3. Give each notable component (for example a figure, a top structure) its own hypotheses with "about": "P<n>".
4. Keep ids stable where possible, use new ids for new items, keep confidences consistent (specific <= general). Output JSON only, no fence, no commentary.
{rules_tail}
PREVIOUS ANSWER
{previous}

SCHEMA (JSON Schema)
{schema}
{context}FACTS
{facts}
"""
CTX = """OWNER-SUPPLIED CONTEXT (from the person who owns the model; treat as evidence with source "owner_note", it can be wrong; do not let it replace what the images show)
{c}

"""
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('facts'); ap.add_argument('--out'); ap.add_argument('--context', help='free text from the owner (what it is, where from, capture setup)'); ap.add_argument('--previous', help='previous answer JSON -> builds the refinement (pass 2) prompt'); A = ap.parse_args()
    facts = json.load(open(A.facts, encoding='utf-8')); schema = json.dumps(json.load(open(os.path.join(HERE, 'interpretation_schema.json'), encoding='utf-8')), separators=(',', ':'))
    example = json.dumps(json.load(open(os.path.join(HERE, 'example_interpretation.json'), encoding='utf-8')), separators=(',', ':'))
    facts['footprint_profile'].pop('data', None)
    ctx = CTX.format(c=A.context) if A.context else ''
    if A.previous:
        out = A.out or A.facts.replace('_facts.json', '_prompt2.md'); body = PASS2.format(previous=json.dumps(json.load(open(A.previous, encoding='utf-8')), separators=(',', ':'), ensure_ascii=False), schema=schema, context=ctx, facts=json.dumps(facts, indent=1), rules_tail='')
    else:
        out = A.out or A.facts.replace('_facts.json', '_prompt.md'); body = T.format(schema=schema, example=example, context=ctx, facts=json.dumps(facts, indent=1))
    open(out, 'w', encoding='utf-8').write(body)
    print('wrote', out, '- paste it into a fresh chat and attach', A.facts.replace('_facts.json', '_views.png'))
if __name__ == '__main__': main()
