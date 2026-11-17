"""The LEGO pyramid as one node and what it is linked to (after the stalagmite figure of geo-lod): pyramid 2.

usage: draw_node.py <ontology.ttl> <mapping.ttl or ->   Output: node.svg
Every spoke is checked against the graph; the run stops if a drawn link no longer stands there. A missing Wikidata item is drawn dashed.
"""
import sys
from pathlib import Path

import rdflib
from rdflib import Namespace, RDFS, URIRef

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svgkit import GREY, ORANGE, PURPLE, Svg, WHITE, INK, MUTED  # noqa: E402
from shapes import stepped  # noqa: E402

L, EX = Namespace("https://example.org/lego-reconstruction#"), Namespace("https://example.org/lego-reconstruction/id/")
CRM, CRMDIG = Namespace("http://www.cidoc-crm.org/cidoc-crm/"), Namespace("http://www.ics.forth.gr/isl/CRMdig/")
SK = Namespace("http://www.w3.org/2004/02/skos/core#")
g = rdflib.Graph()
g.parse(sys.argv[1], format="turtle")
if sys.argv[2] != "-":
    g.parse(sys.argv[2], format="turtle")
HDT = Namespace(str(next(ns for p, ns in g.namespaces() if p == "hdt")))
P = EX.lego_pyramid_2


def need(c, m):
    if not c:
        sys.exit(f"draw_node: {m}")


need((L.LegoModel, rdflib.RDFS.subClassOf, CRM["E22_Human-Made_Object"]) in g, "LegoModel is no longer a crm:E22")
need((P, L.builtBy, EX.daria) in g, "builder changed")
need((P, HDT.has_digital_twin, EX.lego_pyramid_2_twin) in g, "digital twin missing")
need((P, HDT.has_3D_model, EX.model2_scan) in g and (P, HDT.has_3D_model, EX.model2_v4) in g, "3D models missing")
need((EX.model2_scan_event, CRMDIG.L1_digitized, P) in g, "scan event does not digitise the pyramid")
need((EX.hyp_m2_a, L.hypothesisAbout, P) in g, "hypothesis a missing")
need((EX.model2_scan_event, CRM.P7_took_place_at, EX.scan_place) in g, "scan place missing")
wd = g.value(EX.scan_place, SK.closeMatch)
need(wd is not None, "scan place has no Wikidata item")
cand = g.value(EX.hyp_m2_a, L.proposesReferent)
cand_wd = g.value(cand, SK.closeMatch)
conf = float(g.value(EX.hyp_m2_a, L.confidence))
need(conf == 0.7, "confidence of hypothesis a changed")
n = g.value(EX.model2_scan_event, L.imageCount)
need(int(n) == 115, "photo count changed")
FDOX = URIRef("https://doi.org/10.5281/zenodo.24305436")
need((FDOX, HDT.has_3D_model, EX.model2_v4) in g, "FDOx does not carry the model")

W, H = 1750, 1000
svg = Svg(W, H)
CX, CY = 875, 480
PW, PH = 240, 300
svg.rect(CX - PW / 2, CY - PH / 2, PW, PH, "#ffffff", stroke="#ffffff", check=True, name="PYR")
stepped(svg, CX, CY + PH / 2 - 4, 14, 38, "solid", ["#e2e8f0"] * 7)
svg.text(CX, CY + PH / 2 + 34, "LEGO pyramid 2", 30, True, INK, "middle", maxw=300)
svg.text(CX, CY + PH / 2 + 66, "one node, one IRI", 18, False, MUTED, "middle", maxw=300)


def ep(c, w, h, to):
    dx, dy = to[0] - c[0], to[1] - c[1]
    k = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return c[0] + dx * k, c[1] + dy * k


def box(c, w, h, fill, l1, l2, dash=None):
    svg.rect(c[0] - w / 2, c[1] - h / 2, w, h, fill, dash=dash, name=l1)
    col = "#fff" if fill in (ORANGE, PURPLE) else INK
    svg.text(c[0], c[1] - 14, l1, 15, True, col, "middle", maxw=w - 16)
    svg.text(c[0], c[1] + 12, l2, 13, False, col, "middle", maxw=w - 16)


BW, BH = 290, 78
# spokes: centre, fill, line 1, line 2, chip, direction (1 pyramid -> box, -1 box -> pyramid), dash
S = [((170, 110), ORANGE, "CIDOC CRM family", "lrec:LegoModel, subclass of crm:E22", "rdf:type", 1, None),
     ((170, 290), PURPLE, "Daria Stefan (TU Wien)", "ORCID 0009-0008-0586-9350", "lrec: builtBy", 1, None),
     ((170, 470), ORANGE, "Digital twin", "lrec:LegoModelTwin, crmdig:D1", "hdt: has digital twin", 1, None),
     ((170, 640), ORANGE, "Scan digitisation", f"{n} photos, Samsung Galaxy A71", "crmdig: L1 digitized", -1, None),
     ((1580, 110), ORANGE, "Identity hypothesis", f"Maya step pyramid, confidence {conf:.2f}", "lrec: hypothesisAbout", -1, None),
     ((1580, 470), GREY, "Raw scan", "KIRI Engine, ex:model2_scan", "hdt: has 3D model", 1, None),
     ((1580, 650), ORANGE, "Reconstruction model", "GLB, ex:model2_v4", "hdt: has 3D model", 1, None)]
for c, fill, l1, l2, chip, d, dash in S:
    box(c, BW, BH, fill, l1, l2, dash)
    a, b = ep((CX, CY), PW, PH, c), ep(c, BW, BH, (CX, CY))
    pts = [a, b] if d == 1 else [b, a]
    svg.arrow(pts, ends=("PYR", l1))
    svg.chip((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, chip)
# chains
def chain(c1, c2, fill2, l1, l2, chip, dash=None, up=False):
    box(c2, BW, BH, fill2, l1, l2, dash)
    a, b = ep(c1, BW, BH, c2), ep(c2, BW, BH, c1)
    pts = [b, a] if up else [a, b]
    svg.arrow(pts, ends=("x", "y"))
    svg.chip((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, chip)


def link(c1, c2, chip, up=False):
    a, b = ep(c1, BW, BH, c2), ep(c2, BW, BH, c1)
    svg.arrow([b, a] if up else [a, b], ends=tuple(n for n, _ in svg.boxes))
    svg.chip((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, chip)


box((170, 780), BW, BH, ORANGE, "Scan location", "Apothekertrakt, Schönbrunn")
link((170, 640), (170, 780), "crm: P7 took place at")
box((170, 920), BW, BH, PURPLE, f"Wikidata {str(wd).split('/')[-1]}", "same place as the scan location")
link((170, 780), (170, 920), "skos: closeMatch")
box((1580, 290), BW, BH, PURPLE, "Candidate referent", "Wikidata item still to be chosen" if cand_wd is None else f"Wikidata {str(cand_wd).split('/')[-1]}", dash="7 5" if cand_wd is None else None)
link((1580, 110), (1580, 290), "lrec: proposesReferent")
box((1580, 830), BW, BH, PURPLE, "FDOx on Zenodo", "10.5281/zenodo.24305436")
link((1580, 650), (1580, 830), "hdt: has 3D model", up=True)
svg.legend([(ORANGE, "class or reconstruction"), (GREY, "instance"), (PURPLE, "term or identifier")], 560, 960)
svg.save("node.svg")
