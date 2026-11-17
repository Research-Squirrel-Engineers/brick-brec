# ZIP-Memo: LEGO-Pyramiden-FDOx (Stand 2026-11-17)

Übergabe an den Chat, in dem die Pyramiden gerendert und die Ontologie entwickelt wurde. Zweck: den Komplex "vier Pyramiden-FDOx" dort einbauen. Alles hier ist in diesem Chat (FDOx-Packager, fdo-squirrel, Registry) tatsächlich gelaufen und von Flo veröffentlicht.

## 1. Worum es geht

Zwei LEGO-Pyramiden, je ein KIRI-Engine-Scan (Original) und eine Rekonstruktion mit Claude, ergibt vier FDOx (`fdo:3DDataFDO`). Jeder FDOx hat ein eigenes Zenodo-Record in der Community "Squirrel FDOx" (CC BY 4.0, Dataset, veröffentlicht 2026-11-17).

| Kürzel | Pyramide | Rolle | Bauer / Beteiligte |
|---|---|---|---|
| P1 | Pyramide mit Säule und Figur | Eigenbau von Flo | Autor Florian Thiery |
| P2 | "Maya"-Stufenpyramide | gebaut von Daria Stefan (TU Wien), Zustimmung zur Veröffentlichung liegt vor; "Maya-Stufenpyramide" bestätigt, "El Castillo" nicht bestätigt | Autor:innen Daria Stefan, Florian Thiery (Project member) |

Scan-Datum 2026-11-12, Apothekertrakt Schloss Schönbrunn, während CHNT31. P2-Scan: Samsung Galaxy A71, 115 Fotos (von Daria). Rekonstruktionen: prozedural aus idealisierten Steinen, nur Maße und Struktur aus dem Scan, kein Scan-Mesh und keine Textur wiederverwendet; KI-Beteiligung ist als Hinweis im Beschreibungstext vermerkt.

## 2. Die vier FDOx

| FDOx | Titel auf Zenodo | Concept-DOI (= `id` im FDOx) | gepinnte Version |
|---|---|---|---|
| P1 Scan | Lego Pyramid / KIRI Original (FDOx) | 10.5281/zenodo.24305240 | 24305241 (v1) |
| P1 Rekonstruktion | Lego Pyramid / Reconstruction claude.ai (FDOx) | 10.5281/zenodo.24305343 | 24305344 (v1) |
| P2 Scan | Lego Pyramid Maya / KIRI Original (FDOx) | 10.5281/zenodo.24305428 | 24310015 (v3) |
| P2 Rekonstruktion | Lego Pyramid Maya / Reconstruction claude.ai (FDOx) | 10.5281/zenodo.24305436 | 24310030 (v2) |

Sketchfab-Modelle (jeweils eigene Seite des FDOx):
- `lego-pyramid-kiri-original-b262c1135f1c4159bf1e3628d468bdc8`
- `lego-pyramid-reconstruction-claudeai-e2fb31006245424e88033714af2c90f5`
- `lego-pyramid-maya-kiri-original-1e9a188abf974999b7909e15323ded0a`
- `lego-pyramid-maya-reconstruction-claudeai-fe33b10adee4421fa3a06cc12f7d6c62`

Wichtig: Die Concept-DOI ist die Identität des FDOx (`id`, Dataset-IRI im TTL, `doi` in der CITATION.cff). Die Versions-DOI ist das, was die Registry pinnt.

## 3. Wie die FDOx verknüpft sind (für die Ontologie)

In der `MD.cff` je FDOx, Block `related_resources`, Ziel jeweils die Concept-DOI des Partners:

- **Scan → Rekonstruktion:** `isReferencedBy`, mit `note` "Procedural reconstruction from idealised bricks, derived from this scan."
- **Rekonstruktion → Scan:** `isDerivedFrom`, mit `note` "Scan this reconstruction was measured from (dimensions, grid, orientation)."
- **Eigene Sketchfab-Seite:** `isDerivedFrom` (bleibt so; Beschluss 2026-11-17). Die Rekonstruktion trägt dadurch zwei `prov:wasDerivedFrom`, unterscheidbar an IRI und Label.

Abbildung in RDF, wie sie fdo-squirrel v1.3.0 erzeugt:
- `isDerivedFrom` → `prov:wasDerivedFrom` (+ `isBasedOn` im Crate); `isReferencedBy` → `dct:isReferencedBy`; `references` → `dct:references`; `isPartOf` → `dct:isPartOf`; `hasPart` → `dct:hasPart`; `isSupplementTo` und `isDocumentedBy` nur als `dct:relation`. `dct:relation` bleibt immer zusätzlich.
- Gibt es eine `note`: `dcat:qualifiedRelation [ a dcat:Relationship ; dct:relation <Ziel> ; dcat:hadRole <Rolle> ; rdfs:comment "note" ]`. Die Rolle ist das typisierte Prädikat. Für `isSupplementTo` und `isDocumentedBy` sind es die IANA-Relationen `related` und `describedby`; das ist ein Vorschlag, kein Standard.
- RO-Crate (1.2): die `note` wird zur `description` der Ziel-CreativeWork.
- Registry: `dcat:Relationship` bekommt per Crosswalk-Zeile `crm:E13_Attribute_Assignment` als CRM-Anker. Das ist eine Deutung (Aussage des Pakets über eine Beziehung), kein DCAT-Axiom, und steht in der Registry als Vorschlag in A4.

Heritage-Objekt: `object_type` "LEGO model (interlocking-brick toy, self-built)", `documentation_purpose` "Test case for FDOx packaging of a scan and its reconstruction." (siehe `make_local_metadata.py`).

## 4. Werkzeuge und Stand

- **fdo-squirrel v1.3.0** (Commit 23c26d6, Tag und GitHub-Release): Patch S29, Beziehungstyp und `note` bleiben in TTL und Crate erhalten; Blank Nodes je Feld und Position.
- **fdo-3d-packager** (Commit 86bd2fd): `requirements.txt` auf `fdo-squirrel @ …@v1.3.0` gepinnt, PRIMER S21.
- **Pipeline:** fetch → convert → nexus → mdcff → bundle → build_fdo → validate. Overrides pro Slug in `data/local-metadata/<slug>/{MD.cff,CITATION.cff}`; ein überschriebenes Feld ersetzt das generierte ganz. Die mdcff-Warnung "overrides structural field(s) id" ist hier gewollt.
- **Validierung:** rocrate-validator 0.13.1, `ro-crate-1.2`, 66 geprüft, 63 bestanden, 0 fehlgeschlagen, 3 übersprungen (zuletzt für die beiden Maya-Bundles bestätigt).
- **Registry** (`FDOx-squirrel/fdo-squirrel-registry`, alter Remote war `Research-Squirrel-Engineers/…`): 13 Einträge in `sources.json`, 12 Records im Katalog, SHACL-Gate grün. Commits 253aee9 → a80199d (CRM-Anker, erste zwei Pyramiden) → 156353a → 262569d (Maya) → 19dfec4 (PRIMER). Heinz Eau (18740524) bleibt "skipped" (kein `fdo-metadata.ttl` im ZIP), unabhängig von den Pyramiden.

## 5. Was schiefging und was daraus folgt

1. **Falsche Datei im Maya-Scan-Record.** v1 enthielt das Bundle der ersten Pyramide. Aufgefallen durch die Registry: `package subject …24305240 is not its concept DOI …24305428`. Korrektur: neue Zenodo-Version.
2. **Falsche Concept-DOI.** `24305438` gehört einem fremden Record ("Simulator for Topological Tensor Networks"); die Maya-Rekonstruktion hat `24305436`. Die falsche DOI stand in der `id` und `doi` der Rekonstruktion und im Link des Maya-Scans. Korrektur: Overrides geändert, beide Bundles neu gebaut, Scan v3 und Rekonstruktion v2.
3. **Lehre:** DOIs vor dem Eintragen gegen die Zenodo-Seite prüfen (Titel und Dateiname). Die Registry fängt falsche IDs ab, aber erst nach dem Upload.
4. **Concept-DOI ist keine Versions-DOI.** Die Registry bricht ab, wenn eine Concept-DOI als `version_doi` steht; `--resolve` schlägt die Korrektur vor.
5. **Technisches aus dem Aufbau:** veraltetes `build\lib` plus 1980er ZIP-Zeitstempel führten zu falsch installierten Dateien (Lösung: `build` und `egg-info` löschen, neu installieren). Der Packager braucht `--slug` oder `--all-slugs`, sobald mehrere Slugs unter `data/raw/` liegen. `--publisher-label` und `--publisher-id` müssen gesetzt sein.

## 6. Offene Punkte

- Mermaid-Bild fehlt in den Bundles: `mmdc … unknown option '-w'` (gehört zu fdo-squirrel; `mmdc --version` prüfen).
- Registry-Pin `fdo-squirrel@504b7af` auf v1.3.0 heben.
- Registry-Release-Bundle (S8) ist noch nicht auf Zenodo.
- Zenodo-DOI des fdo-squirrel-v1.3.0-Releases könnte in die `CITATION.cff` des Repos.
- Im Packager wäre eine eigene Beziehung für die Sketchfab-Quelle sauberer als `isDerivedFrom`; nicht blockierend (eigener Chat, ein Repo pro Chat).
- Scan-Uhrzeit des Maya-Scans optional nachtragen.

## 7. Konventionen (für den Zielchat)

Deutsch im Chat, britisches Englisch in formalen Texten und im Repo. Windows-cmd-Befehle zusammengehörig in einer Zeile mit `&&`. Lieferung als Patch-ZIP mit `PATCH-README.md`; Entscheidungen mit Datum in der Beschlusslage (A4) des jeweiligen PRIMER.

## 8. Im ZIP

- `ZIP-MEMO_Pyramiden-FDOx.md` (dieses Memo)
- `pyramiden-fdox.csv` (Tabelle der vier FDOx)
- `make_local_metadata.py` (erzeugt die Overrides für die vier Slugs; DOI-Dictionary mit den richtigen Concept-DOIs)
