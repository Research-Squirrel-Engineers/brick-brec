"""Own classes grouped by their CRM-family anchor (after the coverage figure of geo-lod). Output: coverage.svg

A class with two anchors stands in both groups; a class that reaches its anchor through another own class is marked "via".
Classes without an anchor are listed in a dashed band at the bottom with the vocabulary they use.
"""
import sys
from pathlib import Path

import rdflib

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from brec_utils import ONTOLOGY  # noqa: E402
from crm_coverage import anchors, chains, own_classes  # noqa: E402
from svgkit import GREY, ORANGE, Svg, WHITE  # noqa: E402
from fira import tw  # noqa: E402

g = rdflib.Graph()
g.parse(ONTOLOGY, format="turtle")
nm = g.namespace_manager
cls = own_classes(g)
groups = {}
for c in cls:
    for ch in chains(g, c):
        groups.setdefault(ch[-1], []).append((c, len(ch) > 2))
miss = [c for c in cls if not anchors(g, c)]
if miss:
    sys.exit(f"draw_coverage: classes without a CRM anchor: {[c.split('#')[1] for c in miss]}")

order = sorted(groups, key=lambda a: (str(a).split("/")[2], str(a)))
ROW, BHH = 50, 34
H = 60 + len(order) * ROW + 70
W = 1750
svg = Svg(W, H)
y = 30
for a in order:
    q = nm.normalizeUri(a).strip("<>")
    svg.rect(40, y, 330, BHH, WHITE, name="anchor " + q)
    svg.text(205, y + BHH / 2, q, 14, True, "#1f1f1d", "middle", maxw=310)
    x = 420
    for c, via in sorted(groups[a], key=lambda t: str(t[0])):
        label = "brec:" + c.split("#")[1] + (" (via)" if via else "")
        w = tw(label, 13) + 24
        svg.rect(x, y, w, BHH, ORANGE, name="class " + label)
        svg.text(x + w / 2, y + BHH / 2, label, 13, False, "#fff", "middle", maxw=w - 8)
        x += w + 12
    if x > W - 40:
        sys.exit("draw_coverage: a group is wider than the figure")
    svg.o.append(f'<path d="M375 {y + BHH / 2} L410 {y + BHH / 2}" stroke="#111" stroke-width="1.4" fill="none"/>')
    y += ROW
svg.legend([(WHITE, "CRM family class (crm, crmdig, crminf)"), (ORANGE, "BREC class")], 40, H - 40)
svg.save("coverage.svg")
