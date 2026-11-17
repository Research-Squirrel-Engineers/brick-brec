# Identifikation: Was stellen die beiden LEGO-Modelle dar?

Stand: 13.11.2026 · Datei: `lrec_v0.3.ttl` · Zeichnung: `identifikation.png/.svg` (`draw_ident.py`)

Vorgehen: (1) Erkennen anhand der Fotos und der Scans, (2) Begründen (hier), (3) als CRMinf-Argumentation in den Graphen schreiben.
Konfidenz ist eine **subjektive Einschätzung** des KI-Assistenten (0 bis 1), keine Messung. Hypothesen überlappen und summieren sich nicht zu 1.

## Modell 2: Stufenpyramide mit grauen Treppen und Tempel
| Kennung | Hypothese | Konfidenz | stützt | schwächt |
|---|---|---|---|---|
| m2_a | Mesoamerikanische (Maya) Stufenpyramide mit Tempelaufsatz, generisch | 0.70 | E1 E2 E3 | – |
| m2_b | El Castillo, Chichén Itzá (Spezialfall von a) | 0.35 | E2 E3 | E5 (7 statt 9 Ebenen) |
| m2_e | Freies Design ohne konkretes Vorbild | 0.15 | E5 | – |
| m2_c | Angkor-Tempelberg (z. B. Bakong) | 0.10 | E1 E2 | E3 |
| m2_d | Zikkurat mit Tempel | 0.08 | E1 E3 | E2 (vier Treppen untypisch) |

Beobachtungen: E1 sieben zentrierte Stufen · E2 vier graue Treppenarme, je 4 Noppen breit · E3 Tempel mit vier Eckpfeilern, innen hohl · E4 Umgebung (weiße Backstein-Architektur, schwach) · E5 starke Abstraktion.

## Modell 1: Stufenpyramide mit Säule und Figur
| Kennung | Hypothese | Konfidenz |
|---|---|---|
| m1_a | Denkmal: Standbild eines Kriegers auf Säule über Stufenunterbau | 0.55 |
| m1_c | Freie Spiel-/Fantasieszene | 0.20 |
| m1_d | Abstrahierter Wach-/Aussichtsturm | 0.15 |
| m1_b | Konkretes historisches Denkmal (Spezialfall von a, nicht bestimmbar) | 0.10 |

Figur: f_a mittelalterlicher Krieger/Soldat 0.75 · f_b Cobi-Serie (nur Stilvermutung) 0.40.

## Modellierung
`lrec:Identification` (⊑ `crm:E17`, `crminf:I5`) nutzt `lrec:Evidence` (⊑ `crminf:I4`) als Prämissen (`J1`) und schließt auf `lrec:IdentityHypothesis` (⊑ `lrec:Assumption` ⊑ `crminf:I2`) (`J2`). Relationen: `lrec:supports`, `lrec:weakens`, `lrec:alternativeTo`, `lrec:specializes`, `lrec:proposesReferent` → `lrec:CandidateReferent` (mit `lrec:wikidataSearchTerm`; QID später als `skos:closeMatch`).

## Wikidata (Windows cmd, eine Zeile)
`pip install rdflib && python wikidata_match.py lrec_v0.3.ttl && python draw_ident.py lrec_v0.3.ttl`

Das Script zeigt je Kandidat die Wikidata-Treffer, du wählst die Nummer; erzeugt `wikidata_mapping.ttl` (wird von `draw_ident.py` automatisch gelesen und im Bild als QID angezeigt).

## Offen
- Bestätigung durch Flo: Was sind die Modelle tatsächlich (Vorbild, Standort, Hersteller der Figur)? Danach Hypothesen anpassen (`lrec:verificationStatus`).
- `skos:closeMatch` zu Wikidata nach Prüfung.
