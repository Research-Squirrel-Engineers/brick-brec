"""Crosswalk: every LREC class against the vocabularies it is a subclass of (direct rdfs:subClassOf parents), as a matrix.

usage: draw_crosswalk.py <ontology.ttl>   Output: crosswalk.svg
CRM family columns are filled, because every class must have an entry there (directly or through another LREC class; those show "via").
"""
import sys
from pathlib import Path

import rdflib
from rdflib import RDFS

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crm_coverage import anchors, own_classes  # noqa: E402
from fira import tw  # noqa: E402
from pages_more import MODULES, VOCAB  # noqa: E402
from svgkit import GREY, ORANGE, Svg, WHITE, INK, MUTED  # noqa: E402

g = rdflib.Graph()
g.parse(sys.argv[1], format="turtle")
ns = {p: str(n) for p, n in g.namespaces()}
classes = own_classes(g)
FAMILY = {"crm", "crmdig", "crminf"}
CW = {p: (170 if p in FAMILY else 152) for p, _ in VOCAB}
X0, ROW, HEAD = 40, 30, 70
W = X0 + 250 + sum(CW.values()) + 40
rows = []
for name, _, names, _ in MODULES:
    rows.append(("module", name))
    rows += [("class", c) for c in classes if str(c).split("#")[1] in names]
H = HEAD + len(rows) * ROW + 90
svg = Svg(int(W), int(H))
x = X0 + 250
xs = {}
for p, label in VOCAB:
    xs[p] = x
    svg.text(x + CW[p] / 2, HEAD - 26, label, 15, True, INK, "middle", maxw=CW[p] - 6)
    x += CW[p]


def short(u, p, full):
    loc = str(u).replace(ns[p], "")
    if p in FAMILY and not full:
        return loc.split("_")[0]
    return loc.replace("_", " ") if p in FAMILY else loc


y = HEAD
for kind, v in rows:
    if kind == "module":
        svg.rect(X0, y + 2, W - X0 - 40, ROW - 4, "#f1efe8", stroke="#d8d6ce", check=False)
        svg.text(X0 + 10, y + ROW / 2, v, 14, True, INK, maxw=400)
    else:
        svg.text(X0 + 10, y + ROW / 2, "lrec:" + str(v).split("#")[1], 13, False, INK, maxw=235)
        direct_any = False
        for p, _ in VOCAB:
            ps = sorted((o for o in g.objects(v, RDFS.subClassOf) if str(o).startswith(ns[p])), key=str)
            cell = ", ".join(short(o, p, True) for o in ps)
            if p in FAMILY and not ps:
                via = [a for a in anchors(g, v) if str(a).startswith(ns[p])]
                cell = ", ".join(short(a, p, True) + " (via)" for a in via)
                ps = via
            if not ps:
                svg.rect(xs[p] + 2, y + 2, CW[p] - 4, ROW - 4, WHITE, stroke="#e6e4dc", sw=1, rx=4, check=False)
                continue
            if tw(cell, 11) > CW[p] - 10:
                cell = ", ".join(short(o, p, False) for o in ps) + (" (via)" if p in FAMILY and not any(g.objects(v, RDFS.subClassOf)) else "")
            fill = ORANGE if p in FAMILY else GREY
            svg.rect(xs[p] + 2, y + 2, CW[p] - 4, ROW - 4, fill, rx=4, check=False)
            svg.text(xs[p] + CW[p] / 2, y + ROW / 2, cell, 11, False, "#fff" if p in FAMILY else INK, "middle", maxw=CW[p] - 10)
    y += ROW
svg.legend([(ORANGE, "CRM family anchor"), (GREY, "parent in another vocabulary")], X0, H - 40)
svg.save("crosswalk.svg")
