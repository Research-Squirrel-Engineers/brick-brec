"""check: the ontology parses, the drawings agree with it, and the four FDOx bundle TTLs agree with the registry pins and the ontology.

The FDOx checks exist because of real mistakes made while publishing (2026-11-17): a bundle of the wrong
pyramid inside a record, and a concept DOI that belonged to somebody else's record. Both are caught here
before anything is uploaded, not by the registry afterwards.
"""
from __future__ import annotations

import json
import re
import sys

import rdflib
from rdflib import RDF, RDFS, OWL, Namespace, URIRef

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from lrec_utils import DATA, FDOX_BUNDLES, ONTOLOGY, PY, RAW, ROOT, Report, read_pins, run_script, sha256_file  # noqa: E402

LREC = Namespace("https://example.org/lego-reconstruction#")
DCT = Namespace("http://purl.org/dc/terms/")
FDO = Namespace("https://w3id.org/fdo-squirrel/")
FLO = "https://orcid.org/0000-0002-3246-3531"


def main(strict: bool) -> int:
    r = Report(strict)
    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
    r.ok(f"{ONTOLOGY.name} parses: {len(g)} triples")

    # 1. overview drawing vs graph (nodes and edges)
    p = run_script(PY / "figures" / "check_diagram.py", [str(ONTOLOGY)], cwd=PY / "figures")
    m = re.search(r"Fehler\s+(\d+)", p.stdout)
    if p.returncode or not m:
        r.fail("check_diagram.py did not run: " + (p.stderr.strip().splitlines() or ["?"])[-1])
    elif int(m.group(1)):
        r.fail(f"overview drawing disagrees with the graph in {m.group(1)} places:\n" + p.stdout)
    else:
        r.ok("overview drawing agrees with the graph (" + p.stdout.strip().splitlines()[-1] + ")")

    # 2. every LREC class has German and English labels, and is drawn in the class diagram
    src = (PY / "figures" / "draw_classes.py").read_text(encoding="utf-8")
    classes = sorted(c for c in g.subjects(RDF.type, OWL.Class) if str(c).startswith(str(LREC)))
    for c in classes:
        labels = {lit.language for lit in g.objects(c, RDFS.label) if isinstance(lit, rdflib.Literal)}
        if not {"de", "en"} <= labels:
            r.warn(f"class {c.split('#')[-1]} lacks a label in {sorted({'de', 'en'} - labels)}")
        de = next((str(lit) for lit in g.objects(c, RDFS.label) if getattr(lit, "language", None) == "de"), "")
        name = c.split("#")[-1]
        if name not in src and de.split(" (")[0] not in src:
            r.warn(f"class {name} is in the ontology but not in the class diagram (py/figures/draw_classes.py)")
    r.ok(f"{len(classes)} LREC classes checked for labels and for presence in the class diagram")

    # 3. FDOx: the four bundle TTLs (source of truth for identity, title, people, relations) vs registry pins vs lrec.ttl
    pins = read_pins()
    concept = [x["concept_doi"] for x in pins]
    version = [x["pinned_version_doi"] for x in pins]
    if len(set(concept)) != len(concept) or set(concept) & set(version):
        r.fail("a DOI appears twice, or a concept DOI is also used as a version DOI")
    mine = {str(s) for s in g.subjects(RDF.type, LREC.FDOx)}
    want_iris = {"https://doi.org/" + c for c in concept}
    if mine != want_iris:
        r.fail(f"lrec:FDOx nodes in lrec.ttl differ from the registry pins: only in lrec.ttl {sorted(mine - want_iris)}, only in pins {sorted(want_iris - mine)}")
    sums = {k: v.get("bundle_ttl_sha256") for k, v in json.load(open(DATA / "fdox" / "original_bundles.json", encoding="utf-8")).items()}
    for x in pins:
        f = FDOX_BUNDLES / f"{x['slug']}.ttl"
        iri = URIRef("https://doi.org/" + x["concept_doi"])
        if not f.exists():
            r.fail(f"{x['slug']}: bundle TTL missing ({f.relative_to(ROOT)})")
            continue
        if sums.get(x["slug"]) and sha256_file(f) != sums[x["slug"]]:
            r.warn(f"{x['slug']}: bundle TTL differs from the recorded checksum (new Zenodo version? update original_bundles.json)")
        b = rdflib.Graph()
        b.parse(f, format="turtle")
        if (iri, RDF.type, FDO["3DDataFDO"]) not in b:
            r.fail(f"{x['slug']}: no fdo:3DDataFDO with IRI {iri} in the bundle TTL (wrong or missing concept DOI in the pins?)")
            continue
        title = b.value(iri, DCT.title)
        creators = sorted(str(o) for o in b.objects(iri, DCT.creator))
        contribs = sorted(str(o) for o in b.objects(iri, DCT.contributor) if isinstance(o, URIRef))
        sketch = [str(o) for o in b.objects(iri, DCT.relation) if "sketchfab.com" in str(o)]
        zen = {str(o) for o in b.objects(iri, DCT.relation) if "doi.org/10.5281/zenodo" in str(o)}
        bad = []
        if creators != [FLO]:
            bad.append(f"creator {creators}")
        if len(sketch) != 1 or not sketch[0].startswith("https://sketchfab.com/3d-models/" + x["slug"] + "-"):
            bad.append(f"Sketchfab link {sketch} does not belong to slug {x['slug']}")
        foreign = sorted(z for z in zen if z not in want_iris)
        if foreign:
            bad.append(f"relation to a DOI outside the four FDOx: {foreign}")
        if bad:
            r.fail(f"{x['slug']}: " + "; ".join(bad))
        else:
            who = ", ".join(sorted({str(b.value(URIRef(c), RDFS.label)) for c in contribs})) or "none with an IRI"
            r.ok(f"{x['slug']}: bundle TTL = pins = lrec.ttl (concept {x['concept_doi']}, pinned {x['pinned_version_doi']} {x['zenodo_version']}; contributors: {who})")

    # 4. raw inputs, only if the user has put them here (they are large and not part of the repository)
    sums = json.load(open(RAW / "CHECKSUMS.json", encoding="utf-8"))
    present = {p.name: p for p in RAW.rglob("*") if p.is_file()}
    for label, want in sums.items():
        name = label.split(" (")[0]
        hits = [p for n, p in present.items() if n == name]
        for p in hits:
            if sha256_file(p) == want:
                r.ok(f"raw input {name} matches the recorded checksum")
            else:
                r.warn(f"raw input {p.relative_to(RAW)} differs from the recorded checksum ({label}); ignore if it is the other scan's file of the same name")
    if not present.keys() - {"README.md", "CHECKSUMS.json"}:
        r.ok("no raw inputs present (optional, see data/raw/README.md)")
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
