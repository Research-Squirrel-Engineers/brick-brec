# Sucht Wikidata-QIDs fuer alle lrec:CandidateReferent (lrec:wikidataSearchTerm) und die Basis-Begriffe.
# Schreibt wikidata_mapping.ttl (skos:closeMatch). Es wird nichts automatisch uebernommen: du waehlst pro Begriff.
# Windows cmd (eine Zeile):  pip install rdflib && python wikidata_match.py ontology/lrec.ttl
import json, sys, urllib.parse, urllib.request
import rdflib
ttl = sys.argv[1] if len(sys.argv) > 1 else "ontology/lrec.ttl"
g = rdflib.Graph(); g.parse(ttl, format="turtle")
L = rdflib.Namespace("https://example.org/lego-reconstruction#")
EX = "https://example.org/lego-reconstruction/id/"
terms = {"ex:" + str(s).replace(EX, ""): str(t) for s, t in g.subject_objects(L.wikidataSearchTerm)}
terms.update({"ex:claude_sonnet_5_5": "Claude", "ex:brick_scheme": "Lego brick", "ex:lego_pyramid_1": "Lego"})
out = ["@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
       "@prefix wd: <http://www.wikidata.org/entity/> .",
       "@prefix ex: <https://example.org/lego-reconstruction/id/> ."]
for k, term in terms.items():
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "wbsearchentities", "search": term, "language": "en", "format": "json", "limit": 6})
    req = urllib.request.Request(url, headers={"User-Agent": "lrec-match/0.2 (research use)"})
    res = json.load(urllib.request.urlopen(req))["search"]
    print("\n" + k + "  (Suche: " + term + ")")
    for i, r in enumerate(res):
        print(f"  [{i}] {r['id']}  {r.get('label')} - {r.get('description')}")
    sel = input("  Nummer (Enter = ueberspringen): ").strip()
    if sel.isdigit() and int(sel) < len(res):
        out.append(f"{k} skos:closeMatch wd:{res[int(sel)]['id']} .")
open("wikidata_mapping.ttl", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\ngeschrieben: wikidata_mapping.ttl  (danach draw_ident.py erneut ausfuehren)")
