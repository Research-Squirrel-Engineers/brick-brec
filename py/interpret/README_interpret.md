# Werkzeugkette zur Modell-Interpretation ("Inkognito"-Workflow)

Ziel: Du gibst Claude in einem frischen Chat ohne Vorwissen **irgendein** 3D-Modell und bekommst **standardisierte Angaben** zurück, mit denen man das Modell interpretieren kann; danach werden sie in den LREC-Graphen geschrieben.

## Ablauf (Windows cmd; zusammengehörige Befehle in einer Zeile)
1. **Messen und rendern** (lokal, deterministisch):
   `pip install -r requirements.txt && python inspect_model.py mein_modell.glb --out out`
   → `out/mein_modell_facts.json` (Messwerte) und `out/mein_modell_views.png` (vorn, rechts, hinten, links, oben, 3/4).
2. **Prompt bauen** (in sich geschlossen: Regeln, JSON-Schema, Formatbeispiel, Messwerte):
   `python make_prompt.py out/mein_modell_facts.json` → `out/mein_modell_prompt.md`.
   Optional mit Kontext des Eigentümers: `python make_prompt.py out/mein_modell_facts.json --context "Scan eines LEGO-Modells, Foto liegt bei"` (wird als Evidenz `owner_note` geführt, nicht als Wahrheit).
3. **In einem frischen/Inkognito-Chat fragen**: Prompt einfügen, `mein_modell_views.png` anhängen (optional Fotos des echten Objekts). Antwort (reines JSON) als `out/mein_modell_interpretation.json` speichern.
   **Durchgang 2 (Verfeinerung, empfohlen):** `python make_prompt.py out/mein_modell_facts.json --previous out/mein_modell_interpretation.json` → `out/mein_modell_prompt2.md`; in einem frischen Chat mit denselben Bildern ausführen, die Antwort ersetzt das JSON. Durchgang 2 prüft Zahlen (Stufen, Treppen), ergänzt spezifische benannte Kandidaten pro allgemeiner Hypothese (`specializes`), eigene Hypothesen für Bauteile (z. B. Figur, `about`) und Merkmalsvergleiche.
   Optional ohne Chat: `pip install anthropic && set ANTHROPIC_API_KEY=... && python ask_claude.py out/mein_modell_prompt.md out/mein_modell_views.png` (hier ungetestet).
4. **Prüfen und in den Graphen schreiben**:
   `python interpretation_to_lrec.py out/mein_modell_interpretation.json --merge ontology/lrec.ttl --out lrec_merged.ttl && python draw_ident.py lrec_merged.ttl en`

## Was zurückkommt (Schema `lrec-model-interpretation/1.1`)
`object` (Beschreibung, Kategorie, Bautechnik/Material, Größenschätzung, Up-Achse) · `structure` (Form, Ebenen, Symmetrie, Bauteile, Wiederholungen) · `capture` (Herkunft, Defekte, Boden enthalten) · `evidence` (E1.., Quelle Ansichten/Messwerte/Foto/Eigentümer-Notiz, Stärke) · `hypotheses` (H1.., Konfidenz, stützt/schwächt, Alternative, Spezialfall, Kandidat mit Wikidata-Suchbegriff, **`feature_checks`** erwartet vs. beobachtet, **`strongest_counterargument`**, **`about`** = Bauteil) · `questions_for_owner`.
Im Graphen: `lrec:Identification` → `lrec:Evidence` / `lrec:IdentityHypothesis` / `lrec:CandidateReferent`, dazu Objekt, Teile und Maße (CRM E18/E54); das Roh-JSON bleibt als `lrec:interpretationJson` erhalten.

## Neu in 1.1
- `horizontal_surface_levels` trennt `count_raw` (zählt Noppenebenen mit) von `count_without_stud_tops` und `regular_steps` (gleichmäßig verteilte Ebenen); für Stufen zählen die Bilder.
- Kalibrierung der Konfidenz im Prompt (0,1 unwahrscheinlich … 0,9 fast sicher); Spezialfälle nie sicherer als der allgemeine Fall.
- Allgemein-zu-spezifisch-Regel und Durchgang 2, damit konkrete Kandidaten (Bauwerk, Kultur, Figurentyp) vorgeschlagen werden.

## Grenzen
- Heuristische Felder können falsch sein; für die Form zählen die Bilder.
- Konfidenzen sind subjektive Schätzungen, keine Messungen; Wikidata-IDs liefert das Modell nie, nur Suchbegriffe (dann `wikidata_match.py`).
- Getestet mit frischen Sub-Agenten ohne Vorwissen (Ergebnisse siehe unten bzw. Antwort im Chat); echte Fotos des Objekts wurden dabei noch nicht mitgegeben.
- "Inkognito" heißt: keine Gesprächshistorie; das Wissen des Modells bleibt, und `model_id_self_reported` ist nur selbstberichtet.
