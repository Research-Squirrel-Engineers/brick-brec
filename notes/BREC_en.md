# BREC: mini ontology for scan reconstructions (state v0.3, 2026-11-13)

Namespace: `https://example.org/brick-reconstruction#` (prefix `brec:`, placeholder). Instances: `https://example.org/brick-reconstruction/id/` (`ex:`).
Files: `brec_v0.3.ttl` (= `mini_ontology.ttl`; ontology plus example for model 2 and identification hypotheses, labels in German and English), `ontologie_planar_en.svg/png` (overview drawing), `brec_klassen_en.svg/png` (class diagram), `identifikation_en.svg/png` (identification), `check_diagram.py` (drawing ↔ Turtle check), `wikidata_match.py`.
Language: the Turtle file carries `@de` and `@en` labels (`translate_en.py` adds the English ones); the drawing scripts take a language argument (`python draw_classes.py en`, `python draw_ident.py en`).

## Classes (22)

| Class | Parent classes | Meaning |
|---|---|---|
| `brec:BrickModel` | `hdt:Tangible Asset`, `crm:E22 Human-Made Object` | the physical LEGO model |
| `brec:BrickModelTwin` | `hdt:Heritage Digital Twin`, `crmdig:D1 Digital Object` | digital twin of the model |
| `brec:ScanDigitization` | `crmdig:D2 Digitization Process`, `hdt:Heritage Documenting`, `prov:Activity` | KIRI scan (SfM) |
| `brec:RawScan` | `crmdig:D1 Digital Object`, `hdt:3D Model`, `prov:Entity` | raw scan (OBJ + JPG) |
| `brec:ReferencePhoto` | `crmdig:D1 Digital Object`, `hdt:Imagery`, `prov:Entity` | reference photo |
| `brec:AlignmentAndMeasurement` | `crm:E16 Measurement`, `crmdig:D7 Digital Machine Event`, `prov:Activity` | alignment, grid, brick height |
| `brec:StructureInference` | `crminf:I5 Inference Making`, `prov:Activity` | derivation of the structure (levels, widths) |
| `brec:Assumption` | `crminf:I2 Belief`, `prov:Entity` | assumption, e.g. "7 levels" |
| `brec:ProceduralReconstruction` | `crmdig:D7 Digital Machine Event`, `prov:Activity` | construction from bricks by script |
| `brec:ReconstructionModel` | `crmdig:D1 Digital Object`, `hdt:3D Model`, `prov:Entity`, `dcat:Distribution` | reconstruction as GLB |
| `brec:QualityMeasurement` | `dqv:QualityMeasurement` | quality measurement of the reconstruction |
| `brec:ReconstructionScript` | `crmdig:D14 Software`, `schema:SoftwareSourceCode`, `prov:Entity` | reconstruction script (CodeMeta) |
| `brec:ProcessInterval` | `crm:E52 Time-Span`, `time:ProperInterval` | time interval of a process |
| `brec:ScanLocation` | `crm:E53 Place`, `geo:Feature` | capture location |
| `brec:ReconstructionDataset` | `dcat:Dataset`, `prov:Entity` | dataset wrapper (DCAT-AP) around GLB, documentation, scripts |
| `brec:Identification` | `crm:E17 Type Assignment`, `crminf:I5 Inference Making`, `prov:Activity` | identification: what does the object represent? |
| `brec:IdentityHypothesis` | `brec:Assumption` | identification hypothesis with confidence |
| `brec:Evidence` | `crminf:I4 Proposition Set`, `prov:Entity` | observation / argument |
| `brec:CandidateReferent` | `crm:E1 CRM Entity` | possible original (type or individual) |
| `brec:ChangeDocumentation` | `crm:E31 Document`, `hdt:Heritage Document`, `prov:Entity` | change documentation (md + json) |
| `brec:BrickType` | `crm:E55 Type`, `skos:Concept` | brick type (2x4, 2x2, 1x1, 1x2, 1x4) and colour |
| `brec:AIAssistant` | `prov:SoftwareAgent`, `crm:E39 Actor` | AI assistant, here Claude Sonnet 5.5 |

## Own properties (13)

| Property | Kind | Domain → range | Remark |
|---|---|---|---|
| `brec:usesAssumption` | object | `ProceduralReconstruction` → `Assumption` | sub-property of `prov:used` |
| `brec:usesScript` | object | `ProceduralReconstruction` → `ReconstructionScript` | sub-property of `prov:used` |
| `brec:confidence` | datatype | `Assumption` → `xsd:decimal` | 0 to 1, estimated |
| `brec:confidenceBasis` | datatype | `Assumption` → `xsd:string` | basis of the estimate |
| `brec:knownDeviation` | datatype | `ReconstructionModel` → `xsd:string` | documented deviation from the photo/original |
| `brec:hypothesisAbout` | object | `IdentityHypothesis` → `crm:E1` | the LEGO object concerned |
| `brec:proposesReferent` | object | `IdentityHypothesis` → `CandidateReferent` | proposed original (analogous to `crm:P62 depicts`, but only a hypothesis) |
| `brec:supports` / `brec:weakens` | object | `Evidence` → `IdentityHypothesis` | argument for / against |
| `brec:alternativeTo` | object, symmetric | `IdentityHypothesis` ↔ `IdentityHypothesis` | competing hypotheses |
| `brec:specializes` | object | `IdentityHypothesis` → `IdentityHypothesis` | special case |
| `brec:wikidataSearchTerm` | datatype | `CandidateReferent` → `xsd:string` | search term for `wikidata_match.py` |
| `brec:verificationStatus` | datatype | `IdentityHypothesis` → `xsd:string` | e.g. "open: confirmation by Flo needed" |

Used but not defined by BREC: `crm:P2, P4, P7, P14, P39, P40, P41, P46, P70, P90, P91`, `crmdig:L1, L10, L11, L12, L21, L23`, `crminf:J1, J2`, `prov:wasDerivedFrom, wasGeneratedBy, wasAssociatedWith, wasAttributedTo, actedOnBehalfOf, used, startedAtTime`, `dcat:mediaType, distribution`, `dct:identifier, conformsTo, format`, `dqv:hasQualityMeasurement, computedOn, isMeasurementOf, value`, `time:hasBeginning`, the HDT properties `hdt:has_digital_twin`, `includes_3D_documentation`, `includes_visual_documentation`, `includes_document`, `has_3D_model`, and `skos:inScheme, closeMatch`.

## Integrated vocabularies

CIDOC CRM, CRMdig, CRMinf, Heritage Digital Twin Ontology (namespace is a placeholder), PROV-O, DCAT and DCAT-AP, DQV, CodeMeta/schema.org, OWL-Time, GeoSPARQL, SKOS, Dublin Core Terms, QUDT/Units, Wikidata (links via `skos:closeMatch`), OWL/RDFS/XSD.

## Example (model 2, version 4)

Raw scan → measurement (yaw 16.25°) → structure inference (assumption "7 levels", confidence 0.7) → reconstruction (Flo and Claude Sonnet 5.5, `prov:wasAssociatedWith`) → GLB. The twin bundles scan, GLB, photos and change documentation. In addition: dataset wrapper (DCAT-AP), script `build_m3.py` (CodeMeta), quality measurement (number of levels = 7), time interval (OWL-Time), capture location (GeoSPARQL), brick types as SKOS scheme.

## Identification (v0.3)

Three identifications (model 1, figure, model 2) with 10 observations, 11 hypotheses and 8 candidates; see `IDENTIFIKATION_en.md`. Confidence values are subjective estimates by the AI assistant, not measurements; all hypotheses carry the status "open: confirmation by Flo needed".

## Consistency check

`python check_diagram.py brec_v0.3.ttl` checks that all 21 nodes and 26 edges of the overview drawing are present in the Turtle file (state: 0 errors).

## Open points

1. Check the HDT namespace and class names against the official OWL file (placeholder; two publications number differently).
2. Check the property codes against the current specifications (`L1`, `L10`, `L11`, `L12`, `L21`, `L23`, `J1`, `J2`, DCAT-AP profile URI).
3. Wikidata QIDs: run `wikidata_match.py` locally (Windows cmd, one line: `pip install rdflib && python wikidata_match.py brec_v0.3.ttl && python draw_ident.py en`).
4. `schema:codeRepository` is a placeholder; the capture location needs a real geometry (`geo:hasGeometry` / `geo:asWKT`); DCAT-AP mandatory fields (publisher, licence) are missing.
5. Add model 1 as a second full example (figure, column, 9 levels).
6. SHACL shapes and validation; complete `owl:imports` in the header (currently only CRM and PROV-O).
7. Further vocabularies to consider: PAV, P-Plan, SOSA, RO-Crate.
8. Model identity: Claude Sonnet 5.5 is the model configured for the session; the model actually serving a turn may differ.
