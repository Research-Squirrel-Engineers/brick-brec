"""One FDOx as a node and what it is linked to (after figure 16 of geo-lod): the reconstruction FDOx of pyramid 2.

usage: draw_hub.py   (reads the ontology, the four bundle TTLs, the registry pins and the Wikidata mapping through brec_utils)
Every spoke is checked against the merged graph; the run stops if a drawn link no longer stands there. Output: hub.svg
"""
import math
import sys
from pathlib import Path

from rdflib import Namespace, URIRef

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from brec_utils import load_graph  # noqa: E402
from svgkit import AMBER, GREY, ORANGE, PURPLE, Svg, WHITE, GREEN  # noqa: E402
from fira import tw  # noqa: E402

g = load_graph(True)
DCT, PROV, DCAT = Namespace("http://purl.org/dc/terms/"), Namespace("http://www.w3.org/ns/prov#"), Namespace("http://www.w3.org/ns/dcat#")
HDT = Namespace(str(next(ns for p, ns in g.namespaces() if p == "hdt")))
EX = Namespace("https://w3id.org/brec/id/")
HUB = URIRef("https://doi.org/10.5281/zenodo.24305436")
SCAN = URIRef("https://doi.org/10.5281/zenodo.24305428")
FLO, DARIA = URIRef("https://orcid.org/0000-0002-3246-3531"), URIRef("https://orcid.org/0009-0008-0586-9350")
SKETCH = next(o for o in g.objects(HUB, PROV.wasDerivedFrom) if "sketchfab.com" in str(o))
LIC = URIRef("http://creativecommons.org/licenses/by/4.0/")
nfiles = len(list(g.objects(HUB, DCAT.distribution)))
ver = str(g.value(HUB, DCT.hasVersion))
pub = g.value(HUB, DCT.publisher)
subj = sorted(str(o).split("/")[-1] for o in g.objects(HUB, DCT.subject) if "wikidata.org" in str(o))


def need(cond, msg):
    if not cond:
        sys.exit(f"draw_hub: {msg}")


need((HUB, DCT.creator, FLO) in g and (HUB, DCT.contributor, DARIA) in g, "creator/contributor changed")
need((HUB, PROV.wasDerivedFrom, SCAN) in g, "derivation from the scan FDOx missing")
need((HUB, DCT.license, LIC) in g, "licence missing")
need((HUB, PROV.wasAttributedTo, EX.claude_sonnet_5_5) in g and (HUB, PROV.wasGeneratedBy, EX.model2_recon) in g, "attribution or generation missing")
need((HUB, HDT.has_3D_model, EX.model2_v4) in g, "hdt:has_3D_model missing")
need(nfiles > 0 and ver and pub and len(subj) == 2, "files, version, publisher or subjects missing")

W, H = 1750, 1000
svg = Svg(W, H)
HX, HY, HW, HH = 875, 500, 400, 120
svg.rect(HX - HW / 2, HY - HH / 2, HW, HH, ORANGE, sw=3, name="HUB")
for k, (t, size, med) in enumerate([("brec:FDOx · dcat:Dataset", 16, True), ("Lego Pyramid Maya", 15, False), ("(Reconstruction claude.ai)", 15, False), (f"Concept DOI 10.5281/zenodo.{str(HUB).split('.')[-1]}", 13, False)]):
    svg.text(HX, HY - 42 + k * 28, t, size, med, "#fff", "middle", maxw=HW - 20)

# (box centre, width, height, fill, lines, chip label, direction: 1 = hub -> box, -1 = box -> hub)
S = [
    ((300, 100), 300, 78, GREY, ["FDOx: KIRI original", "zenodo.24305428 (scan)"], "prov: wasDerivedFrom", 1),
    ((875, 100), 300, 78, WHITE, ["Sketchfab model", "sketchfab.com/3d-models/…"], "prov: wasDerivedFrom", 1),
    ((1450, 100), 300, 78, WHITE, ["Pinned version DOI", ver], "dct: hasVersion", 1),
    ((150, 330), 250, 78, GREY, ["Florian Thiery", "ORCID 0000-0002-3246-3531"], "dct: creator", 1),
    ((150, 500), 250, 78, GREY, ["Daria Stefan (TU Wien)", "ORCID 0009-0008-0586-9350"], "dct: contributor", 1),
    ((150, 670), 250, 78, PURPLE, ["Publisher", f"wd:{str(pub).split('/')[-1]}"], "dct: publisher", 1),
    ((1600, 330), 270, 78, GREY, ["Claude Sonnet 5.5", "AI assistant (software agent)"], "prov: wasAttributedTo", 1),
    ((1600, 500), 270, 78, ORANGE, ["Procedural reconstruction", "crmdig:D7, prov:Activity"], "prov: wasGeneratedBy", 1),
    ((1600, 670), 270, 78, ORANGE, ["Reconstruction model (GLB)", "hdt:HC 3D Model, dcat:Distribution"], "hdt: has 3D model", 1),
    ((300, 900), 300, 78, PURPLE, ["Licence", "CC BY 4.0"], "dct: license", 1),
    ((875, 900), 300, 78, WHITE, [f"{nfiles} files in the record", "dcat:Distribution"], "dcat: distribution", 1),
    ((1450, 900), 300, 78, PURPLE, ["Subjects", ", ".join("wd:" + q for q in subj)], "dct: subject", 1),
]
NODE = lambda c, w, h: (c[0] - w / 2, c[1] - h / 2, w, h)


def edge_point(c, w, h, to):
    """Point where the line from the centre of a box towards `to` leaves the box border."""
    dx, dy = to[0] - c[0], to[1] - c[1]
    k = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return c[0] + dx * k, c[1] + dy * k


for c, w, h, fill, lines, chip, d in S:
    x, y, ww, hh = NODE(c, w, h)
    svg.rect(x, y, ww, hh, fill, name=lines[0])
    col = "#fff" if fill in (ORANGE, PURPLE) else "#1f1f1d"
    svg.text(c[0], c[1] - 14, lines[0], 15, True, col, "middle", maxw=w - 16)
    svg.text(c[0], c[1] + 12, lines[1], 13, False, col, "middle", maxw=w - 16)
    a = edge_point((HX, HY), HW, HH, c)
    b = edge_point(c, w, h, (HX, HY))
    svg.arrow([a, b], ends=("HUB", lines[0]), sw=1.6)
    svg.chip((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, chip)

svg.legend([(ORANGE, "class (BREC / CRM / HDT)"), (GREY, "instance"), (PURPLE, "term or identifier"), (WHITE, "web resource or record")], 40, 960)
svg.save("hub.svg")
