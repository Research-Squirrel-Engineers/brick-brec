# Identification: what do the two LEGO models represent?

State: 13 Nov 2026 · File: `lrec_v0.3.ttl` · Drawing: `identifikation_en.png/.svg` (`python draw_ident.py en`)

Procedure: (1) recognise from the photos and scans, (2) give reasons (here), (3) write it into the graph as a CRMinf argumentation.
Confidence is a **subjective estimate** by the AI assistant (0 to 1), not a measurement. Hypotheses overlap and do not sum to 1. Nothing has been confirmed by the owner; all hypotheses have the status "open: confirmation by Flo needed".

## Model 2: stepped pyramid with grey stairs and temple
| Id | Hypothesis | Confidence | supports | weakens |
|---|---|---|---|---|
| m2_a | Mesoamerican (Maya) step pyramid with a temple on top, generic | 0.70 | E1 E2 E3 | – |
| m2_b | El Castillo, Chichén Itzá (special case of a) | 0.35 | E2 E3 | E5 (7 instead of 9 levels) |
| m2_e | Free design without a specific model | 0.15 | E5 | – |
| m2_c | Angkor temple mountain (e.g. Bakong) | 0.10 | E1 E2 | E3 |
| m2_d | Ziggurat with temple | 0.08 | E1 E3 | E2 (four stairs untypical) |

Observations: E1 seven centred levels · E2 four grey stair arms, each 4 studs wide · E3 temple with four corner pillars, hollow inside · E4 surroundings (white brick architecture, weak) · E5 strong abstraction.

## Model 1: stepped pyramid with column and figure
| Id | Hypothesis | Confidence |
|---|---|---|
| m1_a | Monument: statue of a warrior on a column above a stepped base | 0.55 |
| m1_c | Free play or fantasy scene | 0.20 |
| m1_d | Abstracted watchtower or lookout | 0.15 |
| m1_b | Specific historical monument (special case of a, cannot be determined) | 0.10 |

Figure: f_a medieval warrior / soldier 0.75 · f_b Cobi series (style-based guess only) 0.40.

## Modelling
`lrec:Identification` (⊑ `crm:E17`, `crminf:I5`) uses `lrec:Evidence` (⊑ `crminf:I4`) as premises (`J1`) and concludes on `lrec:IdentityHypothesis` (⊑ `lrec:Assumption` ⊑ `crminf:I2`) (`J2`). Relations: `lrec:supports`, `lrec:weakens`, `lrec:alternativeTo`, `lrec:specializes`, `lrec:proposesReferent` → `lrec:CandidateReferent` (with `lrec:wikidataSearchTerm`; the QID is added later as `skos:closeMatch`).

## Wikidata (Windows cmd, one line)
`pip install rdflib && python wikidata_match.py lrec_v0.3.ttl && python draw_ident.py en`

The script lists the Wikidata hits per candidate and you choose the number; it writes `wikidata_mapping.ttl`, which `draw_ident.py` reads automatically and shows as a QID in the drawing.

## Open
- Confirmation by the owner: what are the models actually (original, location, manufacturer of the figure)? The owner does not know at the moment, so the hypotheses stay as they are.
- `skos:closeMatch` to Wikidata after checking.
