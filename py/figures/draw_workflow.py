"""The workflow in one picture: inputs, the four steps of `python main.py`, outputs (after figure 14 of geo-lod).

usage: draw_workflow.py   Output: workflow.svg
Step names and descriptions are read from main.py, counts from the repository files; the run stops if they no longer fit the drawing.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lrec_utils import DATA, FDOX_BUNDLES, ONTOLOGY, ROOT, WIKIDATA_MAP, read_pins  # noqa: E402
import rdflib  # noqa: E402
from svgkit import AMBER, GREY, ORANGE, PURPLE, Svg, WHITE, GREEN, wrap  # noqa: E402

steps = re.findall(r'\("(\w+)", "[^"]+", "([^"]+)"\)', (ROOT / "main.py").read_text(encoding="utf-8").split("STEPS = [")[1].split("]")[0])
names = [n for n, _ in steps]
if names != ["check", "reconstruct", "figures", "pages"]:
    sys.exit(f"draw_workflow: the steps of main.py changed ({names}); redraw the figure")
_g = rdflib.Graph()
_g.parse(ONTOLOGY, format="turtle")
n_trip = len(_g)
n_bund = len(list(FDOX_BUNDLES.glob("*.ttl")))
n_pins = len(read_pins())
n_map = WIKIDATA_MAP.read_text(encoding="utf-8").count("skos:closeMatch") if WIKIDATA_MAP.exists() else 0
glb = sorted(json.load(open(DATA / "expected_models.json", encoding="utf-8")))
if len(glb) != 2:
    sys.exit("draw_workflow: expected_models.json no longer lists two models")

W, H = 1750, 860
svg = Svg(W, H)
BW, BH = 340, 108


def box(x, y, w, h, fill, head, lines, name=None):
    svg.rect(x, y, w, h, fill, name=name or head)
    col = "#fff" if fill in (ORANGE, PURPLE, GREEN) else "#1f1f1d"
    yy = y + 24
    svg.text(x + w / 2, yy, head, 15, True, col, "middle", maxw=w - 16)
    for ln in lines:
        yy += 21
        svg.text(x + w / 2, yy, ln, 13, False, col, "middle", maxw=w - 16)


LX, MX, RX = 40, 560, 1170
ROWS = [90, 290, 490, 690]
# steps (middle): the four steps of main.py, in order
for (n, d), y in zip(steps, ROWS):
    svg.rect(MX, y, BW, BH, ORANGE, name="step " + n)
    svg.text(MX + BW / 2, y + 26, f"python main.py --only {n}", 15, True, "#fff", "middle", maxw=BW - 16)
    for k, ln in enumerate(wrap(d, 13, BW - 24)[:3]):
        svg.text(MX + BW / 2, y + 52 + k * 20, ln, 13, False, "#fff", "middle", maxw=BW - 16)
for y in ROWS[:-1]:
    svg.arrow([(MX + BW / 2, y + BH), (MX + BW / 2, y + 200)], ends=("step check", "step reconstruct", "step figures", "step pages"))

# inputs (left)
box(LX, 40, 330, 100, GREY, "Ontology lrec.ttl", [f"{n_trip} triples", "read by check, figures and pages"])
box(LX, 190, 330, 100, GREY, f"{n_bund} FDOx bundle TTLs and pins", [f"{n_pins} concept and version DOIs", "metadata of the Zenodo records"])
box(LX, 340, 330, 100, GREY, "Scripts with scan measurements", ["parameters read once from the", "KIRI Engine SfM scans (not in the repo)"])
box(LX, 490, 330, 100, GREY, "Wikidata mapping", [f"{n_map} curated closeMatch items", "py/wikidata/match.py, run locally"])
# outputs (right)
box(RX, 290, 340, 108, PURPLE, "GLB reconstructions", [f"{len(glb)} models, SHA-256 compared", "with the recorded build"])
box(RX, 490, 340, 108, PURPLE, "Figures", ["SVG and PNG, Fira Sans", "English, checked for overlaps"])
box(RX, 690, 340, 108, PURPLE, "Documentation site", ["docs/, GitHub Pages", "pages, tables, figures"])
box(RX, 90, 340, 108, PURPLE, "Check report", ["dist/pipeline_report.txt", "OK, WARN or ERROR per check"])

def link(a_box, b_box, chip):
    (ax, ay, aw, ah), (bx, by, bw, bh) = a_box, b_box
    a = (ax + aw, ay + ah / 2)
    b = (bx, by + bh / 2) if bx > ax else (bx + bw, by + bh / 2)
    svg.arrow([a, b], ends=())
    svg.chip((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, chip)

link((LX, 40, 330, 100), (MX, ROWS[0], BW, BH), "parses")
link((LX, 190, 330, 100), (MX, ROWS[0], BW, BH), "matches")
link((LX, 340, 330, 100), (MX, ROWS[1], BW, BH), "parametrise")
link((LX, 490, 330, 100), (MX, ROWS[2], BW, BH), "labels")
link((MX, ROWS[0], BW, BH), (RX, 90, 340, 108), "reports")
link((MX, ROWS[1], BW, BH), (RX, 290, 340, 108), "builds")
link((MX, ROWS[2], BW, BH), (RX, 490, 340, 108), "draws")
link((MX, ROWS[3], BW, BH), (RX, 690, 340, 108), "writes")
svg.legend([(GREY, "input in the repository"), (ORANGE, "step of main.py"), (PURPLE, "output")], 40, 830)
svg.save("workflow.svg")
