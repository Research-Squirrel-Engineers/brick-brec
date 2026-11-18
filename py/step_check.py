"""check: the ontology parses, the drawings agree with it, and the four FDOx bundle TTLs agree with the registry pins and the ontology.

The FDOx checks exist because of real mistakes made while publishing (2026-11-17): a bundle of the wrong
pyramid inside a record, and a concept DOI that belonged to somebody else's record. Both are caught here
before anything is uploaded, not by the registry afterwards.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

import rdflib
from rdflib import RDF, RDFS, OWL, Namespace, URIRef

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from lrec_utils import DATA, FDOX_BUNDLES, parse_bundle, ONTOLOGY, PY, RAW, ROOT, Report, read_pins, run_script, sha256_file  # noqa: E402

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
    p = run_script(PY / "figures" / "check_diagram.py", [str(ONTOLOGY), *map(str, sorted(FDOX_BUNDLES.glob("*.ttl")))], cwd=PY / "figures")
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

    # 2a. every class is anchored in CIDOC CRM (crm, crmdig or crminf, directly or through another LREC class) and belongs to a module of the data model page
    from crm_coverage import NO_ANCHOR_OK, uncovered
    from pages_more import unassigned
    miss = sorted(c.split("#")[-1] for c in uncovered(g))
    if set(miss) != set(NO_ANCHOR_OK):
        r.fail("classes without a CIDOC CRM family ancestor: " + ", ".join(sorted(set(miss) ^ set(NO_ANCHOR_OK))))
    else:
        r.ok(f"{len(classes) - len(miss)} of {len(classes)} classes anchored in CIDOC CRM, CRMdig or CRMinf")
    if unassigned(g):
        r.fail("classes not assigned to a module of the data model (py/pages_more.py, MODULES): " + ", ".join(unassigned(g)))

    # 2c. brick types matched to the Minimal Brick Ontology: the part must be in data/mbo_bricks.csv (a copy of the MBO thesaurus) and its studs must agree with the label "AxB"
    import csv
    SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    mbo_parts = {row["part_number"]: row for row in csv.DictReader((DATA / "mbo_bricks.csv").open(encoding="utf-8"))}
    n_mbo = 0
    for bt in sorted(g.subjects(RDF.type, LREC.BrickType), key=str):
        ms = [o for o in g.objects(bt, SKOS.exactMatch) if str(o).startswith("https://w3id.org/mbo/thesaurus/part/")]
        lab = next((str(x) for x in g.objects(bt, SKOS.prefLabel) if getattr(x, "language", "") == "en"), "")
        if len(ms) != 1:
            r.fail(f"brick type {bt.split('/')[-1]} needs exactly one MBO part (skos:exactMatch), has {len(ms)}")
            continue
        row = mbo_parts.get(str(ms[0]).rsplit("/", 1)[-1])
        dims = sorted((int(x) for x in re.findall(r"\d+", lab)), reverse=True)
        if row is None:
            r.fail(f"{bt.split('/')[-1]}: {ms[0]} is not in data/mbo_bricks.csv")
        elif dims != sorted([int(row["studs_length"]), int(row["studs_width"])], reverse=True):
            r.fail(f"{bt.split('/')[-1]}: label {lab} disagrees with MBO part {row['part_number']} ({row['studs_length']} x {row['studs_width']} studs)")
        else:
            n_mbo += 1
    r.ok(f"{n_mbo} brick types matched to MBO parts, label and studs agree")

    # 2b. curated Wikidata mappings: only for nodes of the ontology, only wd:Q ids, one per node, each with a label
    from lrec_utils import WIKIDATA_MAP
    cands = {str(s_) for s_ in g.subjects(LREC.wikidataSearchTerm, None)}
    if WIKIDATA_MAP.exists():
        wg = rdflib.Graph()
        wg.parse(WIKIDATA_MAP, format="turtle")
        SK = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
        pairs = list(wg.subject_objects(SK.closeMatch))
        for s_, o_ in pairs:
            if (s_, None, None) not in g:
                r.fail(f"wikidata_mapping.ttl: {s_} is not a node of the ontology")
            if not re.fullmatch(r"http://www\.wikidata\.org/entity/Q\d+", str(o_)):
                r.fail(f"wikidata_mapping.ttl: {o_} is not a wd:Q... item")
            if (o_, RDFS.label, None) not in wg:
                r.warn(f"wikidata_mapping.ttl: {o_} has no label")
        if len({s_ for s_, _ in pairs}) != len(pairs):
            r.fail("wikidata_mapping.ttl: a node has two closeMatch items")
        open_ = sorted(c.split("/")[-1] for c in cands - {str(s_) for s_, _ in pairs})
        r.ok(f"{len(pairs)} Wikidata mappings checked" + (f"; still open: {', '.join(open_)}" if open_ else "; all candidates mapped"))
    else:
        r.ok(f"no data/wikidata_mapping.ttl yet: {len(cands)} candidates without Wikidata item (python py/wikidata/match.py)")

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
        if sums.get(x["slug"]) and hashlib.sha256(f.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != sums[x["slug"]]:  # line endings do not count (Git may convert them)
            r.warn(f"{x['slug']}: bundle TTL differs from the recorded checksum (new Zenodo version? update original_bundles.json)")
        b = rdflib.Graph()
        parse_bundle(b, f)
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
