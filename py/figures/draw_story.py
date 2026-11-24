"""From the physical pyramid to the Linked Open Data cloud, in five stages: original, SfM scan, brick reconstruction, interpretation, anchoring.

usage: draw_story.py <ontology.ttl> <mapping.ttl or ->   Output: story.svg
Counts and confidences in the captions are read from the graph; the run stops if the hand-written statement no longer stands there.
"""
import sys
from pathlib import Path

import rdflib
from rdflib import Namespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import GREY, ORANGE, PURPLE, Svg, WHITE, wrap, INK, MUTED  # noqa: E402
from shapes import stepped  # noqa: E402

L, EX = Namespace("https://example.org/brick-reconstruction#"), Namespace("https://example.org/brick-reconstruction/id/")
g = rdflib.Graph()
g.parse(sys.argv[1], format="turtle")
if sys.argv[2] != "-":
    g.parse(sys.argv[2], format="turtle")


def need(c, m):
    if not c:
        sys.exit(f"draw_story: {m}")


n1, n2 = int(g.value(EX.model1_scan_event, L.imageCount)), int(g.value(EX.model2_scan_event, L.imageCount))
need((n1, n2) == (69, 115), f"photo counts changed: {n1}, {n2}")
c_a, c_b = float(g.value(EX.hyp_m2_a, L.confidence)), float(g.value(EX.hyp_m2_b, L.confidence))
need((c_a, c_b) == (0.7, 0.35), "confidences of the two top hypotheses changed")
need((EX.assume_7_levels, None, None) in g, "seven-level assumption missing")
need((EX.lego_pyramid_2, L.builtBy, EX.daria) in g, "builder changed")

W, H, SW, GAP, M = 1950, 640, 250, 150, 50
svg = Svg(W, H)
X = [M + SW / 2 + i * (SW + GAP) for i in range(5)]
heads = [("1 Original", "What exists?"), ("2 SfM scan", "What was captured?"), ("3 Reconstruction", "What was built from it?"),
         ("4 Interpretation", "What does it represent?"), ("5 Linked data", "Where is it anchored?")]
for x, (t, s) in zip(X, heads):
    svg.text(x, 40, t, 26, True, INK, "middle", maxw=SW + 60)
    svg.text(x, 74, s, 15, False, MUTED, "middle", maxw=SW + 60)
DT, DB = 110, 380   # drawing area
for x in X:
    svg.rect(x - SW / 2, DT, SW, DB - DT, "#fbfbf9", stroke="#d8d6ce", check=False)
stepped(svg, X[0], DB - 20, 14, 30, "solid")
stepped(svg, X[1], DB - 20, 14, 30, "points")
stepped(svg, X[2], DB - 20, 14, 30, "bricks", [ORANGE, "#b45309", ORANGE, "#b45309", ORANGE, "#b45309", ORANGE])
# interpretation: hypotheses as small ranked boxes, as they stand in the graph
for k, (t, c, fill) in enumerate([("Maya step pyramid", c_a, ORANGE), ("El Castillo", c_b, ORANGE)]):
    y = DT + 40 + k * 70
    svg.rect(X[3] - 110, y, 220, 52, fill, name="hyp" + t)
    svg.text(X[3], y + 17, t, 15, True, "#fff", "middle", maxw=200)
    svg.text(X[3], y + 37, f"confidence {c:.2f}", 13, False, "#fff", "middle", maxw=200)
svg.text(X[3], DT + 190, "subjective estimate, not a measurement", 12, False, MUTED, "middle", maxw=SW - 10)
svg.rect(X[3] - 110, DT + 215, 220, 40, GREY, name="builder")
svg.text(X[3], DT + 235, "builder confirms Maya", 14, True, INK, "middle", maxw=200)
# linked data: the targets
for k, (t, s, fill) in enumerate([("CRM family and HDT", "classes of the nodes", ORANGE), ("Wikidata", "places and candidates", PURPLE),
                                  ("FDOx on Zenodo", "scan and reconstruction", PURPLE), ("ORCID", "people", PURPLE)]):
    y = DT + 12 + k * 65
    svg.rect(X[4] - 110, y, 220, 54, fill, name="t" + t)
    svg.text(X[4], y + 18, t, 15, True, "#fff", "middle", maxw=200)
    svg.text(X[4], y + 38, s, 12, False, "#fff", "middle", maxw=200)
for i, chip in enumerate(["photographed", "reconstructed", "interpreted", "anchored"]):
    a, b = (X[i] + SW / 2 + 6, 245), (X[i + 1] - SW / 2 - 6, 245)
    svg.arrow([a, b])
    svg.chip((a[0] + b[0]) / 2, 245, chip)
caps = [(["Self-built LEGO pyramids,", "by Flo and Daria Stefan"], GREY),
        ([f"{n1} and {n2} photos,", "smartphone, KIRI Engine (SfM)"], GREY),
        (["Bricks only, seven levels,", "every change documented"], GREY),
        (["Evidence supports hypotheses;", "each proposes a candidate"], GREY),
        (["One IRI per node,", "close matches, DOIs, CRM and HDT"], GREY)]
for x, (lines, fill) in zip(X, caps):
    yy = DB + 24
    svg.rect(x - SW / 2, yy, SW, 84, fill, name="cap" + lines[0])
    for j, ln in enumerate(lines):
        svg.text(x, yy + 26 + j * 24, ln, 14, j == 0, INK, "middle", maxw=SW - 12)
svg.legend([(GREY, "model or statement"), (ORANGE, "class or reconstruction"), (PURPLE, "term or identifier")], 50, H - 50)
svg.save("story.svg")
