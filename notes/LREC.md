# LREC: Mini-Ontologie für Scan-Rekonstruktionen (Stand v0.1, 2026-11-13)

Namespace: `https://example.org/lego-reconstruction#` (Präfix `lrec:`, Platzhalter). Instanzen: `https://example.org/lego-reconstruction/id/` (`ex:`).
Dateien: `lrec_v0.1.ttl` (Ontologie plus Beispiel Modell 2), `ontologie_planar.svg/png` (Zeichnung), `ontologie.mmd` (ältere Mermaid-Fassung).

## Klassen (12)

| Klasse | Oberklassen | Bedeutung |
|---|---|---|
| `lrec:LegoModel` | `hdt:Tangible Asset`, `crm:E22 Human-Made Object` | das physische LEGO-Modell |
| `lrec:LegoModelTwin` | `hdt:Heritage Digital Twin` | digitaler Zwilling des Modells |
| `lrec:ScanDigitization` | `crmdig:D2 Digitization Process`, `hdt:Heritage Documenting`, `prov:Activity` | KIRI-Scan (SfM) |
| `lrec:RawScan` | `crmdig:D1 Digital Object`, `hdt:3D Model`, `prov:Entity` | Rohscan (OBJ + JPG) |
| `lrec:AlignmentAndMeasurement` | `crm:E16 Measurement`, `crmdig:D7 Digital Machine Event`, `prov:Activity` | Ausrichtung, Raster, Steinhöhe |
| `lrec:StructureInference` | `crminf:I5 Inference Making`, `prov:Activity` | Ableitung der Struktur (Stufen, Breiten) |
| `lrec:Assumption` | `crminf:I2 Belief`, `prov:Entity` | Annahme, zum Beispiel "7 Stufen" |
| `lrec:ProceduralReconstruction` | `crmdig:D7 Digital Machine Event`, `prov:Activity` | Bau aus Steinen per Skript |
| `lrec:ReconstructionModel` | `crmdig:D1 Digital Object`, `hdt:3D Model`, `prov:Entity`, `dcat:Distribution` | Rekonstruktion als GLB |
| `lrec:ChangeDocumentation` | `crm:E31 Document`, `hdt:Heritage Document`, `prov:Entity` | Änderungsdoku (md + json) |
| `lrec:BrickType` | `crm:E55 Type`, `skos:Concept` | Steintyp (2x4, 2x2, 1x1, 1x2, 1x4) und Farbe |
| `lrec:AIAssistant` | `prov:SoftwareAgent`, `crm:E39 Actor` | KI-Assistent, hier Claude Sonnet 5.5 |

## Properties (3 eigene)

| Property | Art | Domain → Range | Bemerkung |
|---|---|---|---|
| `lrec:usesAssumption` | Object | `ProceduralReconstruction` → `Assumption` | Unterproperty von `prov:used` |
| `lrec:confidence` | Datatype | `Assumption` → `xsd:decimal` | 0 bis 1, geschätzt |
| `lrec:knownDeviation` | Datatype | `ReconstructionModel` → `xsd:string` | dokumentierte Abweichung vom Foto/Original |

Zusätzlich genutzt, aber nicht von LREC definiert: `crm:P14, P39, P40, P70, P90, P91`, `crmdig:L10, L11, L21`, `crminf:J1, J2`, `prov:wasDerivedFrom, wasGeneratedBy, wasAssociatedWith, actedOnBehalfOf, used, startedAtTime`, `dcat:mediaType`, `dct:identifier`, und die HDT-Properties `hdt:has_digital_twin`, `includes_3D_documentation`, `includes_visual_documentation`, `includes_document`, `has_3D_model`.

## Eingebundene Ontologien

CIDOC CRM, CRMdig, CRMinf, Heritage Digital Twin Ontology (Namespace Platzhalter), PROV-O, DCAT, Dublin Core Terms, SKOS, QUDT/Units, OWL/RDFS/XSD.

## Beispiel im Turtle (Modell 2, Version 4)

Rohscan → Messung (Yaw 16,25°) → Strukturableitung (Annahme "7 Stufen", Konfidenz 0,7) → Rekonstruktion (Flo und Claude Sonnet 5.5, `prov:wasAssociatedWith`) → GLB. Der Zwilling bündelt Scan, GLB und Änderungsdoku.

## Offene Punkte

1. HDT-Namespace und Klassennamen gegen die offizielle OWL-Datei prüfen (Platzhalter, zwei Veröffentlichungen nummerieren unterschiedlich).
2. Property-Codes aus dem Gedächtnis gegen die aktuellen Spezifikationen prüfen (`L21`, `J1`, `J2`, `L10`, `L11`).
3. Klassen fehlen noch für: Fotos (`hdt:Imagery`), Brick-Instanzen, Drehwinkel/Parameter, Figur als Teil des Modells, Software-Skripte.
4. Weitere Vokabulare wählen (Vorschlag: PAV, P-Plan, SOSA, DQV, RO-Crate, CodeMeta).
5. Modell 1 als zweites Beispiel ergänzen (Figur, Säule, 9 Ebenen).
6. SHACL-Shapes und Validierung.
7. `owl:imports` im Kopf nennt nur CRM und PROV-O, die übrigen Importe ergänzen.
8. Modellkennung: Claude Sonnet 5.5 ist das konfigurierte Modell der Sitzung, das tatsächlich bedienende Modell kann abweichen.

---

## v0.2 (13.11.2026): neue Vokabulare

Datei: `lrec_v0.2.ttl` (= `mini_ontology.ttl`), Diagramm: `lrec_klassen.png/.svg` (`draw_classes.py`, liest v0.2).

| Vokabular | Einbindung in LREC | Neue Klasse / Nutzung |
|---|---|---|
| DQV | Qualitaet der Rekonstruktion | `lrec:QualityMeasurement` ⊑ `dqv:QualityMeasurement`; `dqv:Metric`, `dqv:Dimension` als Instanzen; `dqv:hasQualityMeasurement` am Modell |
| CRMinf | schon in v0.1 | `I5 Inference Making`, `I2 Belief` (Assumption); J1/J2 weiterhin zu pruefen |
| DCAT + DCAT-AP | Datensatz-Huelle | `lrec:ReconstructionDataset` ⊑ `dcat:Dataset`, `dct:conformsTo` DCAT-AP; Distribution bleibt `lrec:ReconstructionModel` |
| CodeMeta (schema.org) | Skripte | `lrec:ReconstructionScript` ⊑ `crmdig:D14_Software`, `schema:SoftwareSourceCode`; `lrec:usesScript` ⊑ `prov:used`; zusaetzlich `crmdig:L23` |
| OWL-Time | Zeitraeume | `lrec:ProcessInterval` ⊑ `crm:E52_Time-Span`, `time:ProperInterval`; via `crm:P4_has_time-span` |
| GeoSPARQL | Aufnahmeort | `lrec:ScanLocation` ⊑ `crm:E53_Place`, `geo:Feature` (Geometrie noch offen) |
| SKOS | Steintypen | `ex:brick_scheme` (ConceptScheme), 2x4/2x2/1x1 als `lrec:BrickType` |
| Wikidata | Verknuepfung | `skos:closeMatch` auf `wd:Q...`; Mapping per `wikidata_match.py` -> `wikidata_mapping.ttl` |

Neue Klassen: 5 (gesamt 17), neue Object-Property: `lrec:usesScript`.

### Offen
- Wikidata-QIDs: Sandbox erreicht Wikidata nicht. Lokal ausfuehren (Windows cmd, eine Zeile): `cd onto && python wikidata_match.py`
- `schema:codeRepository` ist Platzhalter; Aufnahmeort braucht echte Geometrie (`geo:hasGeometry`/`geo:asWKT`).
- `dcat:Dataset`-Pflichtfelder von DCAT-AP (Publisher, Lizenz) fehlen noch.
- CRMdig-Codes L1/L23 und DCAT-AP-Profil-URI pruefen; HDT-Namespace weiterhin Platzhalter.

### Nachtrag v0.2: Abgleich Gesamtzeichnung <-> Turtle
- Neue Klasse `lrec:ReferencePhoto` (⊑ `crmdig:D1`, `hdt:HC_Imagery`, `prov:Entity`); gesamt jetzt 18 LREC-Klassen. `lrec:LegoModelTwin` ist zusaetzlich ⊑ `crmdig:D1`.
- Neue Instanzen: `ex:model2_photos`, `ex:smartphone` (D8), `ex:kiri_engine` (D14), `unit:DEG` (E58, qudt:Unit); Kanten `L12`, `L23`, `L11` am Scan, `P2 has type` am Modell, `hdt:includes_visual_documentation`.
- `check_diagram.py` prueft automatisch, dass alle Knoten (21) und Kanten (26) der Gesamtzeichnung in `lrec_v0.2.ttl` stehen: `python check_diagram.py lrec_v0.2.ttl` (Stand: 0 Fehler).
- `mini_ontology.ttl` = `lrec_v0.2.ttl` (identische Kopie).

## v0.3 (13.11.2026): Identifikation
Neue Klassen (gesamt 22): `lrec:Identification`, `lrec:IdentityHypothesis`, `lrec:Evidence`, `lrec:CandidateReferent`. Neue Properties: `hypothesisAbout`, `proposesReferent`, `supports`, `weakens`, `alternativeTo`, `specializes`, `wikidataSearchTerm`, `confidenceBasis`, `verificationStatus`. Details: `IDENTIFIKATION.md`. `mini_ontology.ttl` = `lrec_v0.3.ttl`.
