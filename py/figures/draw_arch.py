"""Architecture: CIDOC CRM family, the LREC domain layer in three modules, reused W3C standards, the knowledge graph and the Linked Open Data cloud.

usage: draw_arch.py <ontology.ttl>   Output: architecture.svg
Class counts per module come from the ontology and the module list of the data model page; the run stops if a CRM family member
named in the figure is no longer used as an anchor.
"""
import sys
from pathlib import Path

import rdflib

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crm_coverage import anchors, own_classes  # noqa: E402
from pages_more import MODULES  # noqa: E402
from svgkit import AMBER, GREY, ORANGE, PURPLE, Svg, WHITE, INK, MUTED  # noqa: E402

g = rdflib.Graph()
g.parse(sys.argv[1], format="turtle")
classes = own_classes(g)
fam = {str(a).split("/")[2] for c in classes for a in anchors(g, c)}
if not {"www.cidoc-crm.org", "www.ics.forth.gr"} <= fam or not any("CRMinf" in str(a) for c in classes for a in anchors(g, c)) \
        or not any("CRMdig" in str(a) for c in classes for a in anchors(g, c)):
    sys.exit("draw_arch: the ontology no longer uses crm, crmdig and crminf anchors")
count = [sum(1 for c in classes if str(c).split("#")[1] in names) for _, _, names, _ in MODULES]
if sum(count) != len(classes):
    sys.exit("draw_arch: classes without a module")

W, H = 1750, 1030
svg = Svg(W, H)
LW = 1120


def panel(x, y, w, h, fill, title, size=22, sub=None):
    svg.rect(x, y, w, h, fill, rx=14, check=False)
    svg.text(x + 24, y + 28, title, size, True, INK, maxw=w - 48)
    if sub:
        svg.text(x + 24, y + 56, sub, 15, False, MUTED, maxw=w - 48)


def node(x, y, w, h, fill, l1, l2, big=False):
    svg.rect(x, y, w, h, fill, name=l1)
    col = "#fff" if fill in (ORANGE, PURPLE) else INK
    svg.text(x + w / 2, y + h / 2 - 11, l1, 19 if big else 16, True, col, "middle", maxw=w - 14)
    svg.text(x + w / 2, y + h / 2 + 13, l2, 13, False, col, "middle", maxw=w - 14)


# CRM family
panel(30, 30, LW, 250, "#edf1f9", "CRM family")
node(60, 84, LW - 60, 60, "#d4e0f4", "CIDOC CRM", "events, things, places, time-spans, types, actors")
node(60, 168, 520, 96, "#e2d6ef", "CRMdig", "digital objects, digitisation, software, derivation")
node(610, 168, 520, 96, "#d7e8d2", "CRMinf", "beliefs, propositions, inference making")
# domain layer
panel(30, 360, LW, 270, "#f5f6f0", "LREC domain layer", sub=f"{len(classes)} classes in three modules, all anchored in the CRM family")
cols = ["#fff0cc", "#d7e8d2", "#f7d9ea"]
sub = ["from scan to documented reconstruction", "evidence, hypotheses, candidates", "Zenodo records and datasets"]
mw = (LW - 60 - 2 * 20) / 3
for k, (name, _, _, _) in enumerate(MODULES):
    node(45 + k * (mw + 20), 440, mw, 160, cols[k], name, f"{count[k]} classes; {sub[k]}")
# standards
panel(30, 730, LW, 110, "#e4e4df", "W3C and community standards")
svg.text(30 + LW / 2, 800, "PROV-O, DCAT, DQV, OWL-Time, GeoSPARQL, SKOS, schema.org, CodeMeta", 17, False, INK, "middle", maxw=LW - 40)
# knowledge graph panel
KX, KW = 1270, 450
panel(KX, 30, KW, 810, WHITE, "Knowledge graph", 24, "instances typed by the classes")
cx, cy = KX + KW / 2, 450
outer = [(-170, -170, 0), (130, -230, 1), (175, -35, 1), (180, 150, 1), (-70, 250, 1), (-170, 40, 0), (-150, -70, 0)]
for dx, dy, _ in outer:
    svg.o.append(f'<path d="M{cx:.0f} {cy} L{cx + dx:.0f} {cy + dy}" stroke="#555" stroke-width="1.6" fill="none"/>')
svg.o.append(f'<circle cx="{cx:.0f}" cy="{cy}" r="38" fill="#e2e8f0" stroke="#000" stroke-width="1.4"/>')
for dx, dy, ext in outer:
    svg.o.append(f'<circle cx="{cx + dx:.0f}" cy="{cy + dy}" r="{22 if ext else 26}" fill="{"#4c1d95" if ext else "#e2e8f0"}" stroke="#000" stroke-width="1.4"/>')
# Linked Open Data cloud
svg.rect(30, 890, W - 60, 110, "#efeaf6", rx=14, check=False)
svg.text(54, 945, "Linked Open Data cloud", 22, True, INK, maxw=290)
bx = 360
for t, s2, fill in [("Wikidata", "places, candidates", WHITE), ("FDOx", "Zenodo records", WHITE), ("ORCID", "people", WHITE), ("OpenStreetMap", "geometry", WHITE),
                    ("Other knowledge graphs", "linked via close matches", PURPLE)]:
    w = 250 if fill == PURPLE else 215
    node(bx, 915, w, 62, fill, t, s2)
    bx += w + 20
# arrows with amber chips centred on them
for x in (200, 605, 1010 - 0):
    svg.arrow([(x, 360), (x, 280)], sw=1.6)
svg.chip(605, 320, "anchored by rdfs:subClassOf")
for x in (200, 590, 980):
    svg.arrow([(x, 630), (x, 730)], sw=1.6)
svg.chip(590, 680, "reused, not copied")
svg.arrow([(30 + LW, 495), (KX, 495)])
svg.chip((30 + LW + KX) / 2, 495, "builds")
svg.arrow([(KX + KW / 2, 840), (KX + KW / 2, 890)])
svg.chip(KX + KW / 2, 865, "linked")
svg.legend([(GREY, "instance"), (PURPLE, "external identifier")], 60, 1012 - 12) if False else None
svg.save("architecture.svg")
