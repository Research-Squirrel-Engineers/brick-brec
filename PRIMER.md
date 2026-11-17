# PRIMER: lego-lrec

Arbeitsplan für die LREC-Ontologie und ihre Pipeline. Wird zu Beginn jedes Chats hochgeladen, am Ende zurückgeschrieben.
Intern und deutsch; alles andere im Repo ist britisches Englisch. Stand: 2026-11-17.

---

# Teil A: Immer gültig

## A1 Ausgangslage

| Was | Wo | Rolle |
|---|---|---|
| Ontologie LREC v0.4 (23 Klassen, 16 eigene Properties, 711 Tripel; vor der Umstellung auf die Bundle-TTLs 832 Tripel) | `ontology/lrec.ttl` | Quelle der Wahrheit |
| Rekonstruktionsskripte P1, P2 | `py/reconstruct/` | seeded, lesen keine Scandateien |
| Zeichnungen (Gesamtmodell, Klassen, Identifikation; nur englisch) | `py/figures/` | handgesetzt, kreuzungsfrei |
| Interpretations-Toolkit (Schema 1.1) | `py/interpret/` | Messen → Prompt → frischer Chat → Konverter |
| Vier FDOx auf Zenodo und Sketchfab | `data/fdox/bundles/*.ttl` (Quelle), `registry_pins.csv` | veröffentlicht 2026-11-17 |
| Memo und Original-Bundles aus dem FDOx-Chat | `notes/`, `data/fdox/original_bundles.json` | Quelle der DOIs |

**Befunde** (geprüft, nicht vermutet):

- Beide Rekonstruktionen werden aus den Skripten **byte-identisch** neu erzeugt (Python 3.13.18, numpy 2.5.3, trimesh 5.2.1, Pillow 12.3.0, scipy 1.18.1; unter Python 3.10 mit numpy 2.2.6/scipy 1.15.3 bleibt P2 byte-identisch, P1 weicht in wenigen Bytes ab bei gleicher Geometrie und hat eine zweite erlaubte Prüfsumme in `data/expected_models.json`; geprüft 2026-11-17). Die Skripte lesen keine Scandateien: alle Messwerte stehen als Konstanten darin.
- Die Original-FDOx-Bundles enthalten **Konversionen** (`model.obj`, `.nxs`, `.nxz`, Texturen), nicht die GLB-Quellen. Flächenzahlen der Rekonstruktionen stimmen (49.964 und 42.996), die Prüfsummen nicht (geprüft 2026-11-17).
- Daria Stefan steht in `MD.cff` und `fdo-metadata.ttl` der Maya-FDOx als **Beitragende**, nicht als Erstellerin; das Memo nennt sie Autorin der Zenodo-Records. Unklar, ob beides gleich sein soll (geprüft 2026-11-17).
- Zwei echte Fehler beim Veröffentlichen: falsche Datei im Maya-Scan-Record (v1 enthielt das Bundle der ersten Pyramide) und falsche Concept-DOI `24305438` (gehört einem fremden Record; richtig ist `24305436`). Der Schritt `check` fängt beides jetzt vor dem Upload ab (2026-11-17).
- Die Gesamtzeichnung und die Klassenzeichnung kennen `lrec:FDOx` noch nicht; `python main.py --strict` meldet das (2026-11-17).
- Die frühere Annahme, Hersteller und Set der Modelle müssten ergänzt werden, war **falsch**: beide sind Eigenbauten (P1 Flo, P2 Daria Stefan), korrigiert 2026-11-17.

**Auswirkung der FDOx auf die Modellierung** (aus dem Abgleich mit den Originalen):

| Bereich | Auswirkung |
|---|---|
| Identität | Der FDOx ist die zitierbare Einheit. Seine IRI ist die Concept-DOI; die Registry pinnt die Versions-DOI. Im Graphen zwei getrennte Felder (`dct:identifier`, `dct:hasVersion`). |
| Doppelung | `lrec:ReconstructionDataset` (interne Hülle) und `lrec:FDOx` (veröffentlichtes Paket) überlappen. Vorschlag in A4. |
| Eine Quelle der Wahrheit | `MD.cff` (YAML) und der Graph führen dieselben Fakten (Titel, Beteiligte, Beziehungen). Solange beides von Hand gepflegt wird, entstehen Abweichungen wie Ersteller/Beitragende. |
| Provenienz | FDOx flacht die Kette Messung → Strukturableitung → Rekonstruktion auf ein `prov:wasDerivedFrom` ab. Der Graph ist reicher; die Details stehen nur als Freitext in `technique.processing`. |
| Interpretation | Die Hypothesen (mit Argumenten und Konfidenz) kommen im FDOx nur als Satz vor. Status „bestätigt" und Graph können auseinanderlaufen. |
| Rollen | Drei verschiedene Rollen sind zu trennen: Erbauer des Objekts (`lrec:builtBy`), Aufnehmender (`crm:P14` an der Scan-Aktivität), Beteiligte am Record (`dct:creator`/`dct:contributor`). |
| Versionen | Modellversion (z. B. `model2_v4`) ≠ Record-Version (Zenodo v1, v2, v3). Die Zenodo-Versionen von 2026-11-17 sind Korrekturen der Pakete, keine neuen Modelle. |
| Dateien | Quelle (GLB/OBJ) und Bundle-Konversion (OBJ/Nexus) sind verschiedene digitale Objekte mit eigener Prüfsumme; die Konversion ist eine Aktivität. |
| KI-Beteiligung | Im FDOx nur als Beitragende ohne IRI (leerer Knoten). Im Graphen `ex:claude_sonnet_5_5` (`lrec:AIAssistant`); beide verbinden. |

## A2 Zielbild

```
Scan (KIRI) ──► Messung ──► Rekonstruktion (Steine, GLB) ──► Interpretation ──► FDOx (Zenodo + Sketchfab)
                    │                 │                            │                   │
                    └──────── ontology/lrec.ttl (ein Graph) ───────┴───────────────────┘
                                          │
                       check → reconstruct → figures → pages  (python main.py)
                                          │
                       dist/ (GLB, Bericht)   docs/ (Ontologie-Seite, Zeichnungen)
```

Eigenschaften des Ergebnisses (jeweils prüfbar):

1. `python main.py` läuft offline durch; zweimal hintereinander ausgeführt bleibt `git status` sauber.
2. Beide Rekonstruktionen stimmen byte-identisch mit dem aufgezeichneten Ergebnis überein (`data/expected_models.json`).
3. Die vier `fdo-metadata.ttl` der Bundles, die Registry-Pins und `lrec.ttl` stimmen überein (Concept-DOI, Versions-DOI, Ersteller, Sketchfab-Seite, keine Fremd-DOI), geprüft vor jedem Upload.
4. Jede Zeichnung zeigt jede LREC-Klasse und jede Kante des Gesamtmodells; `--strict` läuft grün.
5. Jede Hypothese trägt Konfidenz, Argumente und einen Status; „bestätigt" nur mit Quelle und Datum.

## A3 Querschnittsregeln

- Rohdaten unter `data/raw/`, unverändert, schreibgeschützt, **nicht** im Repo (groß; Prüfsummen in `CHECKSUMS.json`). Produkte nach `dist/` und `docs/`.
- Kein Generator liest die Uhr. Datumsangaben kommen aus `RELEASE` oder aus den Daten.
- Zweimal laufen lassen: `git status` muss danach leer sein.
- Das Netz wird nur von Skripten genutzt, die du selbst startest (`wikidata_match.py`, `ask_claude.py`); die Pipeline selbst ist offline.
- Kopierter Code bringt seine Prüfungen mit.
- Zahlen, Prüfsummen und DOIs stehen nie nur im Chat, sondern in `data/` oder `ontology/`.
- Sprache: Chat auf Deutsch (du), Repo auf britischem Englisch, `PRIMER.md` auf Deutsch. Windows `cmd`, zusammengehörige Befehle in **einer** Zeile.
- Konfidenzen sind subjektive Schätzungen der KI, keine Messungen; sie stehen so im Graphen.

## A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Identität eines FDOx | Concept-DOI (`id`, Dataset-IRI); die Registry pinnt die Versions-DOI | 2026-11-17 |
| Sketchfab-Seite im FDOx | bleibt `isDerivedFrom` (zweites `prov:wasDerivedFrom` der Rekonstruktion); eigene Beziehung wäre sauberer, nicht blockierend | 2026-11-17 |
| Scan → Rekonstruktion | `isReferencedBy` mit Notiz; Rekonstruktion → Scan `isDerivedFrom` mit Notiz | 2026-11-17 |
| Identifikation P2 | „Maya-Stufenpyramide" bestätigt durch die Erbauerin; „El Castillo" nicht bestätigt (nicht widerlegt) | 2026-11-17 |
| Rekonstruktion | prozedural aus idealisierten Steinen; nur Maße und Struktur aus dem Scan, kein Mesh, keine Textur | 2026-11-12 |
| KI-Beteiligung | im Beschreibungstext des FDOx und als Beitragende vermerkt | 2026-11-17 |
| Quelle der Ontologie | `ontology/lrec.ttl` (v0.4 ist die Quelle; die Hilfsskripte `translate_en.py`, `add_fdox.py` aus dem Chat sind abgelöst) | Vorschlag |
| `lrec:FDOx` und `lrec:ReconstructionDataset` | `lrec:FDOx` = veröffentlichtes Paket (Scan und Rekonstruktion), Unterklasse von `dcat:Dataset`; die beiden Rekonstruktions-FDOx tragen zusätzlich `lrec:ReconstructionDataset`, die Scan-FDOx nicht; keine Unterklassenbeziehung zwischen beiden | 2026-11-17 |
| Quelle für FDOx-Metadaten | die `fdo-metadata.ttl` der veröffentlichten Bundles (`data/fdox/bundles/`), unverändert abgelegt; `lrec.ttl` führt die FDOx-Knoten unter derselben IRI und ergänzt nur LREC-eigene Aussagen (Typ, Scan-Aktivität, Modell, KI-Zuschreibung); die Versions-DOI steht nur in `data/fdox/registry_pins.csv`. Die Overrides `MD.cff`/`CITATION.cff` bleiben Eingabe des Packagers (S3) | 2026-11-17 |
| Rolle von Daria Stefan | Beitragende (`dct:contributor`) bei den Maya-FDOx, Ersteller bleibt Flo; Daria allein als Erbauerin des Objekts (`lrec:builtBy`) | 2026-11-17 |
| Figuren | SVG ist das Produkt; PNG optional (`--png`, resvg_py oder Playwright) | Vorschlag |
| Figuren: Sprache und Aufbau | nur englisch, ohne Kopf- und Fußzeile (Titel, Quelle und Erläuterungen stehen auf der Seite bzw. der Folie, nicht im Bild); Beschriftungen der Pfeile als gelbe Chips (`#fbbf24`) mittig auf dem Pfeil, nie daneben; `check`/`figures` melden Überlappungen von Chips mit Kästen, Chips und fremden Linien | 2026-11-17 |
| `dist/`, `docs/` | werden committet, nicht ignoriert | 2026-11-17 |

## A5 Was in welchem Chat hochgeladen wird

Standard: `PRIMER.md` und das Repo ohne Erzeugtes und ohne große Rohdaten, in einer Zeile:

```cmd
powershell -NoProfile -Command "Compress-Archive -Path PRIMER.md,README.md,main.py,requirements.txt,ontology,py,data,notes,interpretations -DestinationPath bundle.zip -Force"
```

Nicht hochladen: `.git/`, `.venv/`, `dist/`, `docs/` (alles erzeugt), die Scandateien unter `data/raw/` (nur auf Nachfrage), die Bundle-ZIPs der FDOx (bei Prüfungen dazulegen).

## A6 IRI-Landkarte

| Pfad | Inhalt | Ziel des Redirects | Status |
|---|---|---|---|
| `https://doi.org/10.5281/zenodo.<concept>` | die vier FDOx | Zenodo | aktiv |
| `https://example.org/lego-reconstruction#` | LREC-Klassen und -Properties | Platzhalter | geplant (w3id oder Zenodo, S0) |
| `https://example.org/lego-reconstruction/id/` | Beispielindividuen | Platzhalter | geplant |
| `https://example.org/placeholder/hdt#` | HDT-Klassen | Platzhalter, durch den offiziellen Namespace ersetzen | geplant |

---

# Teil B: Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen: Namespace (w3id), HDT-Namespace (Rest); `FDOx` vs. `ReconstructionDataset` und Rolle Daria Stefan entschieden 2026-11-17 (A4) | lego-lrec | – | teilweise erledigt 2026-11-17 |
| S1 | Skelett und Pipeline (`check`, `reconstruct`, `figures`, `pages`) | lego-lrec | – | erledigt 2026-11-17 |
| S2 | FDOx-Ebene in alle Zeichnungen (Gesamtmodell, Klassen; Identifikation braucht sie nicht) | lego-lrec | S0 | erledigt 2026-11-17 |
| S3 | Bundle-TTLs als einzige Quelle der FDOx-Metadaten: Umstellung von `check` und Seite erledigt 2026-11-17; offen: Overrides `MD.cff`/`CITATION.cff` gegen die erzeugte TTL prüfen | lego-lrec | S0 | teilweise erledigt 2026-11-17 |
| S4 | LREC-Graph als Datei in die FDOx; Versionsmodell (Modell vs. Record); Konversion als Aktivität | lego-lrec | S3 | offen |
| S5 | Interpretationen t4/t5 in den Graphen mergen; Wikidata-IDs mit `wikidata_match.py` | lego-lrec | – | offen |
| S6 | Ontologie-Seite veröffentlichen (GitHub Pages, Zenodo-Release) | lego-lrec | S2, S0 | offen |
| S7 | SHACL-Shapes (FDOx, Identifikation) und DCAT-AP-Pflichtfelder | lego-lrec | S3 | offen |
| S8 | Modell 1 vollständig als Beispiel; CRMdig-/CRMinf-Codes prüfen | lego-lrec | – | offen |
| S9 | Skill `kiri-scan-to-lego-reconstruction` um FDOx und Repo-Struktur erweitern | Claude-Skill | S1 | Vorschlag erstellt 2026-11-17 |

Unabhängig voneinander: S5, S8 und S2 (nach S0) können in beliebiger Reihenfolge laufen. S3 und S4 bauen aufeinander auf.

---

# Teil C: Die Schritte

## S1 Skelett und Pipeline

**Ziel:** Ein Befehl (`python main.py`) baut Modelle, Zeichnungen und Seite aus den Quellen neu.

**Uploads:** keine.

Schritte: `check` (Ontologie, Zeichnungs-Abgleich, FDOx-Tabelle gegen Graph), `reconstruct` (beide GLB, Byte-Vergleich), `figures` (SVG, englisch), `pages` (`docs/`).

**Abnahme:** `python main.py` läuft zweimal durch, `git status` bleibt danach sauber, beide Rekonstruktionen „byte-identical", ein WARN (FDOx fehlt im Klassendiagramm, Schritt S2).

### Erledigt 2026-11-17

Alle vier Schritte laufen (ca. 5 Sekunden, davon 4 für die Rekonstruktion). Die frühere Einzelskript-Welt (Ordner `out4`, `out6`, relative Pfade) ist in einen Arbeitsordner unter `dist/` gekapselt. Die Zeichnungen sind seit dem Folgeschritt (siehe A4, Figuren) nur noch englisch; die Ersetzungstabelle `data/overview_labels_en.json` ist entfallen.

## S2 FDOx-Ebene in alle Zeichnungen

**Ziel:** `lrec:FDOx`, `dcat:Relationship`, Scan-Sitzung und die Rolle des Bauers erscheinen in Gesamtmodell, Klassendiagramm und Identifikation.

**Uploads:** die aktuellen Zeichnungen aus `docs/visuals/img/` zur Ansicht.

Die Zeichnungen sind handgesetzt; neue Knoten brauchen Platz, ohne Kanten zu kreuzen. Die Prüfungen in `check_diagram.py` müssen mit erweitert werden (heute 21 Knoten, 26 Kanten).

**Abnahme:** `python main.py --strict` grün, Sichtprüfung beider Sprachen, keine Kreuzung und keine Überlappung.

### Erledigt 2026-11-17

- **Gesamtzeichnung:** zwei neue Knoten `lrec:FDOx` (Scan, Rekonstruktion von Pyramide 2, Concept-DOI `...24305428` und `...24305436`) unten rechts, mit den Kanten `dct:isReferencedBy` (Scan → Rekonstruktion), `prov:wasDerivedFrom` (Rekonstruktion → Scan) und `prov:wasAttributedTo` (Rekonstruktion → KI-Agent). Pyramide 1 steht als Fußnote (`...24305240`, `...24305343`), weil die Zeichnung nur Pyramide 2 zeigt. 23 Knoten, 29 Kanten, keine Kreuzung.
- **Nicht gezeichnet:** die Kanten `hdt:has_3D_model` von den FDOx zu den Modellknoten (RAW, OUT). Der Bereich dazwischen ist so dicht belegt, dass sie nicht kreuzungsfrei gehen; die Zuordnung steht im Graphen. Wer sie zeichnen will, muss QM und SW2 umsetzen (offen).
- **`check_diagram.py`** liest jetzt `lrec.ttl` **und** die Bundle-TTLs, weil `dct:isReferencedBy` und `prov:wasDerivedFrom` zwischen den FDOx nur dort stehen.
- **Klassendiagramm:** `lrec:FDOx` (Eltern `crmdig:D1`, `prov:Entity`, `dcat:Dataset`); Legende auf zwei Zeilen umgebrochen (die Einträge überlappten), Fußzeile nennt `ontology/lrec.ttl` statt `lrec_v0.3.ttl`.
- **Identifikation:** unverändert. Die Hypothesen hängen nicht an den FDOx.
- **Ergebnis:** `python main.py --strict` endet mit Exit 0, es gibt keine bekannte Lücke mehr.
- **Nachtrag (Darstellung):** Zeichnungen nur englisch (`overview.svg`, `classes.svg`, `identification.svg`), keine Kopf- und Fußzeilen; die Erläuterungen (Pyramide 1, Konfidenz, Pfeile) stehen jetzt in den Bildunterschriften von `docs/visuals.html`. Pfeilbeschriftungen sind gelbe Chips; `draw.py` setzt sie automatisch auf die Mitte des Pfeils (kurze Pfeile zuerst, mit Prüfung gegen Kästen, andere Chips und fremde Linien); die Pyramide-2-Ortsbox ist dafür schmaler (170 statt 190) und ein Stück nach rechts gerückt, damit der Pfeil P7 lang genug ist. Im Klassendiagramm ist der Abstand zwischen `Assumption` und `ProceduralReconstruction` größer, in der Identifikationsgrafik sind die Pfeile zwischen den Spalten länger. `figures` schlägt fehl, wenn `draw.py` Überlappungen meldet.

## S3 Bundle-TTLs als einzige Quelle der FDOx-Metadaten

**Ziel:** Identität, Titel, Beteiligte, Beziehungen und Dateien eines FDOx stehen genau einmal, in dessen `fdo-metadata.ttl`; `MD.cff`/`CITATION.cff` (Eingabe des Packagers) werden dagegen geprüft und nicht daneben gepflegt.

**Uploads:** die vier Bundle-ZIPs (zum Vergleich), `py/fdox/make_local_metadata.py` im aktuellen Stand.

**Abnahme:** das erzeugte `MD.cff` ist inhaltsgleich mit dem veröffentlichten (Differenz nur dort, wo S0 etwas beschlossen hat); `check` schlägt bei einem falschen Titel oder einer falschen DOI fehl.

### Erledigt 2026-11-17 (Teil 1: Quelle umgestellt)

Die vier `fdo-metadata.ttl` liegen unverändert in `data/fdox/bundles/` (Prüfsumme in `data/fdox/original_bundles.json`). Sie benutzen dasselbe Vokabular wie unsere FDOx-Knoten (`dcat:Dataset`, `crmdig:D1`, `prov:wasDerivedFrom`, `dcat:qualifiedRelation`) und dieselbe IRI (Concept-DOI), deshalb verschmelzen sie mit `lrec.ttl` ohne `owl:sameAs`. Aus `lrec.ttl` entfielen die kopierten Titel, Ersteller, Distributionen und `ex:rel_*`-Knoten sowie die Properties `lrec:fdoType`, `lrec:sketchfabPage`, `lrec:relationNote`. Die Versions-DOI ist die einzige FDOx-Angabe, die die Bundles nicht kennen: `data/fdox/registry_pins.csv`. `py/lrec_utils.load_graph()` lädt alles zusammen; `check` und die FDOx-Seite benutzen es. Geprüft: eine falsche Concept-DOI in den Pins (24305438) und eine Relation auf eine Fremd-DOI in einer Bundle-TTL lassen `check` fehlschlagen. Daria Stefan steht in beiden Maya-Bundles bereits als `dct:contributor`.

Offen in S3: `make_local_metadata.py` gegen die erzeugten TTLs prüfen (Overrides ergeben dieselben Felder?).

## S4 Graph in die FDOx, Versionsmodell

**Ziel:** Jeder FDOx enthält den Auszug des LREC-Graphen als Dokumentation; Modellversion und Record-Version sind getrennt modelliert.

**Abnahme:** der Auszug parst, die Beziehungen im Graphen und im Bundle stimmen überein.

## S5, S6, S7, S8, S9

Siehe Teil B. Diese Schritte werden beschrieben, sobald sie an der Reihe sind.

---

# Teil D: Offene Punkte

- Ist Daria Stefan Ersteller oder Beitragende der Maya-FDOx (Zenodo-Record gegen Bundle)? Als Formular im nächsten Chat fragen.
- Wikidata (2026-11-17): Zuordnung der Kandidaten kuratiert in `data/wikidata_mapping.ttl` (Quelle, von Hand geprüft), erzeugt mit `py/wikidata/match.py` (Netz, nicht in `main.py`); `check` prüft Knoten, QID-Form, Label; Abbildung zeigt QID und Label. Offen: Auswahl der QIDs durch Flo.
- Seitenkopf wie GeoScience-FAIRification-LOD: zwei Zeilen (Documentation, Figures) mit Labels, Kopierknopf je Abbildung.
- Erledigt 2026-11-17: Abbildungen in Fira Sans nach dem Muster von GeoScience-FAIRification-LOD (Schrift im SVG benannt, nicht eingebettet; Textbreiten mit Pillow-BASIC gemessen, `py/figures/fira.py`; PNG mit resvg-py und den Fontdateien aus `py/figures/fonts/`; Docs-Seiten zeigen das PNG, SVG als Download).
- Die Mermaid-Übersicht fehlt in den FDOx-Bundles (`mmdc … unknown option '-w'`); gehört zu fdo-squirrel, nicht hierher.
- Der Registry-Pin auf `fdo-squirrel` v1.3.0 ist noch zu heben (anderes Repo).
- Wikidata-IDs der Kandidaten (Maya-Pyramide, El Castillo, Kriegerfigur …) fehlen noch.
- Erledigt 2026-11-18: alle 23 Klassen an CIDOC CRM geankert (`lrec:QualityMeasurement` unter `crm:E54_Dimension`, `lrec:ReconstructionDataset` unter `crmdig:D1_Digital_Object`; Vorschlag, die Wahl von E54 bzw. D1 ist von Flo zu bestätigen); `check` schlägt fehl, wenn eine Klasse keinen Vorfahren der CRM-Familie hat (`py/crm_coverage.py`).
- Erledigt 2026-11-18: neue Seiten Datenmodell (drei Module), CRM-Abdeckung, Crosswalk, Instanzmodelle; neue Abbildungen Story, Architektur, Pyramidenknoten, Pyramide 1 und 2 (gemessen/geschätzt/rekonstruiert/interpretiert), FDOx-Knoten, Workflow, CRM-Anker, Crosswalk-Matrix. Zeitbalken-Abbildung entfernt (auf Wunsch).
- Zurückgestellt: SPARQL-Seite im Browser (Pyodide, wdt-sparql) und 3D-Ansicht der GLB-Modelle.
- Offen: Wikidata-IDs für `ex:c_cobi`, `ex:c_elcastillo`, `ex:c_maya` (`python py/wikidata/match.py --set ex:c_cobi=Q… …`); der Knoten-Abbildung zeigt `c_maya` gestrichelt, bis die ID da ist.
