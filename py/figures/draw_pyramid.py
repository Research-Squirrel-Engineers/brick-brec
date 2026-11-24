"""Schematic of one pyramid with what was measured, estimated, reconstructed and interpreted about it (after the stalagmite figure of geo-lod).

usage: draw_pyramid.py <1|2> <ontology.ttl> <mapping.ttl or -> <notes/aenderungen_en.json>

The drawing is schematic (widths in studs from the reconstruction script's parameters, front view). Every number in a statement is read
from the change documentation (aenderungen_en.json) or from the graph; the run stops if a value drawn by hand no longer stands there.
Output: pyramid<N>.svg in the working directory.
"""
import json
import sys
from pathlib import Path

import rdflib
from rdflib import RDFS, Namespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import AMBER, GREY, ORANGE, PURPLE, Svg, WHITE, INK  # noqa: E402
from fira import tw  # noqa: E402

MODEL = sys.argv[1]
ONT, MAP, NOTES = sys.argv[2], sys.argv[3], sys.argv[4]
L = Namespace("https://example.org/brick-reconstruction#")
EX = Namespace("https://example.org/brick-reconstruction/id/")
SK = Namespace("http://www.w3.org/2004/02/skos/core#")
g = rdflib.Graph()
g.parse(ONT, format="turtle")
if MAP != "-":
    g.parse(MAP, format="turtle")
notes = json.load(open(NOTES, encoding="utf-8"))


def en(s, p=RDFS.label):
    return next((str(x) for x in g.objects(s, p) if getattr(x, "language", None) == "en"), "")


def need(cond, msg):
    if not cond:
        sys.exit(f"draw_pyramid: {msg}")


W, H = 1750, 1000
CX, GY, S = 875, 800, 30           # centre x, ground y, px per stud
HB = S * 1.2                      # brick height 9.6 mm against stud pitch 8 mm
svg = Svg(W, H)
BRICK_W, BRICK_G, BRICK_B, FIG = "#f4f4f1", "#6b7280", "#1f2937", None


def brick(x, y, w, h, fill):
    svg.rect(x, y, w, h, fill, "#000", 1, 1, check=False)


def studs(x0, x1, y, fill):
    n = int(round((x1 - x0) / S))
    for k in range(n):
        svg.rect(x0 + k * S + S * 0.2, y - S * 0.16, S * 0.6, S * 0.16, fill, "#000", 0.8, 1, check=False)


# ---------------------------------------------------------------- statements and targets
meas, assum, recon, interp = [], [], [], []      # (target (x, y), head, [lines])
T = {}                                           # named points of the drawing

if MODEL == "2":
    m2 = notes["model_2"]
    rv = m2["reconstruction_versions"]["v2_to_v4"]
    reach, quad = rv["stair_arms"]["reach_studs_per_level"], rv["white_corner_quadrant_studs_per_level"]
    n_lv = rv["levels"]
    need(len(reach) == n_lv == len(quad) == 7, "levels differ between the lists")
    yaw = m2["measurement"]["yaw_deg"]
    pitch, bh = m2["measurement"]["stud_pitch_in_scan_cells"], m2["measurement"]["brick_height_in_scan_units"]
    pil = rv["temple"]["pillar_yaw_deg"]
    wb = rv["white_block_yaw_deg"]
    allyaw = [v for lv in ("level_3", "level_4", "level_5") for v in wb[lv].values()]
    bc = rv["brick_counts"]
    n_w, n_g = sum(bc["white"].values()), sum(bc["grey"].values())
    scan = EX.model2_scan_event
    imgs = int(g.value(scan, L.imageCount))
    dev = str(g.value(scan, L.captureDevice))
    need(any("0.72" in x for x in m2["original"]["problems"]), "scan compression factor 0.72 no longer in the notes")
    need(any("16" in x and "rotated" in x for x in m2["original"]["problems"]), "yaw problem no longer in the notes")

    # drawing, bottom up
    for i in range(n_lv):
        y = GY - (i + 1) * HB
        r = reach[i] * S
        brick(CX - r, y, 2 * r, HB, BRICK_G)
        q = quad[i] * S
        if q:
            brick(CX - 2 * S - q, y, q, HB, BRICK_W)
            brick(CX + 2 * S, y, q, HB, BRICK_W)
        studs(CX - r, CX + r, y, BRICK_G)
    ty = GY - n_lv * HB
    brick(CX - 2 * S, ty - HB, 4 * S, HB, BRICK_G)                                  # course 1
    for xx in (CX - 2 * S, CX + S):                                                    # course 2: pillars, hollow between
        brick(xx, ty - 2 * HB, S, HB, BRICK_W)
    svg.rect(CX - S, ty - 2 * HB, 2 * S, HB, "#e5e7eb", "#000", 0.8, 0, check=False)
    brick(CX - 2 * S, ty - 3 * HB, 4 * S, HB, BRICK_G)                              # course 3: lintel
    brick(CX - S, ty - 4 * HB, 2 * S, HB, BRICK_G)                                  # course 4
    top = ty - 4 * HB - S * 0.16
    studs(CX - S, CX + S, ty - 4 * HB, BRICK_G)
    base_l, base_r = CX - reach[0] * S, CX + reach[0] * S

    meas += [
        ((base_l + 6, GY - 8), "Yaw of the pyramid", [f"{yaw} degrees against the ground in the scan, corrected for the model"]),
        ((CX - reach[0] * S, GY - 0.75 * HB), "Stud pitch", [f"{pitch} scan cells per stud; brick height {bh} scan units"]),
        ((CX - reach[2] * S, GY - 2.5 * HB), "Scan distorted", ["Compressed along one axis (about factor 0.72); stair side partly disintegrated; ground rises towards the pyramid"]),
        ((CX - reach[5] * S, GY - 5.5 * HB), "Capture", [f"{imgs} photos, {dev}; KIRI Engine (structure from motion)"]),
    ]
    assum += [
        ((CX - reach[6] * S, ty + HB * 0.5), "Seven levels", ["According to the photo and the builder; the scan suggests eight levels of 20 x 20 studs"]),
        ((CX - 2 * S, ty - 1.5 * HB), "Pillar rotation", [f"Estimated by eye from a close-up: front {pil['front']}, left {pil['left']}, right {pil['right']}, back {pil['back']} degrees; direction uncertain"]),
        ((CX - 2 * S - quad[3] * S, GY - 3.5 * HB), "Rotated white blocks", [f"{min(allyaw):g} to {max(allyaw):g} degrees on levels 3 to 5, read from the compressed scan (about 20 % uncertain)"]),
        ((CX - reach[1] * S, GY - 1.5 * HB), "Hidden bricks", ["Inner distribution of the bricks is estimated, not read from the scan"]),
    ]
    recon += [
        ((CX + reach[1] * S, GY - 1.5 * HB), "Stair arms", [f"Four arms, {rv['stair_arms']['width_studs']} studs wide, reach {reach[0]} to {reach[-1]} studs per level, grey"]),
        ((CX + 2 * S + quad[0] * S, GY - 0.5 * HB), "White corner blocks", [f"Quadrants of {', '.join(str(q) for q in quad[:5])} studs on levels 1 to 5; level 5 as 2 x 2"]),
        ((CX + 2 * S, ty - 1.5 * HB), "Temple", [f"{rv['temple']['courses']} courses: grey 4 x 4, four white 1 x 1 pillars (hollow), grey lintel, grey 2 x 2"]),
        ((CX + reach[3] * S, GY - 3.5 * HB), "Bricks", [f"{n_w + n_g} in total: {n_w} white and {n_g} grey; only 2 x 4, 2 x 2, 1 x 1 and {bc['white']['other_1x2_1x4']} of 1 x 2 / 1 x 4"]),
        ((CX + reach[5] * S, GY - 5.5 * HB), "Known deviation", [en(EX.model2_v4, L.knownDeviation)]),
    ]
    hyp_ids = ["hyp_m2_a", "hyp_m2_b", "hyp_m2_e", "hyp_m2_c", "hyp_m2_d"]
    apex = (CX, top)
    fig_note = None
else:
    m1 = notes["model_1"]
    lv = m1["reconstruction"]["structure"]["levels_studs_w_x_l"]
    widths = [int(x.split("x")[0]) for x in lv]
    need(len(lv) == 9, "model 1 has no nine levels any more")
    col = m1["reconstruction"]["structure"]["column"]
    need("5 bricks" in col, "column no longer 5 bricks")
    scan = EX.model1_scan_event
    imgs, dev = int(g.value(scan, L.imageCount)), str(g.value(scan, L.captureDevice))
    probs = m1["original"]["problems"]
    need(any("38 scan units" in x for x in probs), "figure height 38 scan units no longer in the notes")
    for i, wd in enumerate(widths):
        y = GY - (i + 1) * HB
        r = wd * S / 2
        brick(CX - r, y, 2 * r, HB, BRICK_W)
        studs(CX - r, CX + r, y, BRICK_W)
    ty = GY - 9 * HB
    cx0 = CX - S                                                                    # column at the corner of the top step
    for k in range(5):
        brick(cx0, ty - (k + 1) * HB, S, HB, BRICK_W)
    colx, coltop = cx0 + S / 2, ty - 5 * HB
    # minifigure, schematic: legs, torso with cloak, head, helmet with spike (own drawing, no real character)
    fx, fy = colx, coltop - S * 0.16
    svg.rect(fx - 18, fy - 62, 36, 44, "#7f1d1d", "#000", 1, 3, check=False)       # cloak behind
    svg.rect(fx - 13, fy - 20, 11, 20, "#1d4ed8", "#000", 1, 1, check=False)       # legs
    svg.rect(fx + 2, fy - 20, 11, 20, "#1d4ed8", "#000", 1, 1, check=False)
    svg.rect(fx - 14, fy - 5, 13, 5, "#78350f", "#000", 1, 1, check=False)         # shoes
    svg.rect(fx + 1, fy - 5, 13, 5, "#78350f", "#000", 1, 1, check=False)
    svg.rect(fx - 14, fy - 52, 28, 32, "#9ca3af", "#000", 1, 3, check=False)       # torso (chain mail)
    svg.rect(fx - 14, fy - 28, 28, 4, "#78350f", "#000", 1, 0, check=False)        # belt
    svg.o.append(f'<circle cx="{fx:.1f}" cy="{fy - 64:.1f}" r="11" fill="#f2c9a0" stroke="#000" stroke-width="1"/>')
    svg.o.append(f'<path d="M{fx - 12:.1f} {fy - 66:.1f} A12 12 0 0 1 {fx + 12:.1f} {fy - 66:.1f} Z" fill="#d1d5db" stroke="#000" stroke-width="1"/>')
    svg.o.append(f'<path d="M{fx - 3:.1f} {fy - 77:.1f} L{fx:.1f} {fy - 90:.1f} L{fx + 3:.1f} {fy - 77:.1f} Z" fill="#d1d5db" stroke="#000" stroke-width="1"/>')
    top = fy - 90
    base_l, base_r = CX - widths[0] * S / 2, CX + widths[0] * S / 2

    meas += [
        ((base_l, GY - 0.3 * HB), "Footprint", [f"{lv[0].replace('x', ' x ')} studs at the base, {len(lv)} equally high steps"]),
        ((CX - widths[4] * S / 2, GY - 4.5 * HB), "Scan problems", ["Edges and studs very noisy, flat ground and base untidy"]),
        ((fx - 18, fy - 40), "Figure in the scan", ["Deformed and stretched, about 38 scan units high; modelled anew from photos"]),
        ((CX - widths[1] * S / 2, GY - 1.5 * HB), "Capture", [f"{imgs} photos, {dev}; KIRI Engine (structure from motion)"]),
    ]
    assum += [
        ((CX - widths[2] * S / 2, GY - 2.5 * HB), "Bricks", ["Only 2 x 4, 2 x 2 and 1 x 1 in white, as stated by the builder"]),
        ((CX - widths[6] * S / 2, GY - 6.5 * HB), "Hidden bricks", ["Hidden distribution is random, not read from the scan"]),
    ]
    recon += [
        ((CX + widths[3] * S / 2, GY - 3.5 * HB), "Tiling", ["Each level split into 2 x 2 blocks and tiled with 2 x 4 and 2 x 2 bricks (best of 400 random tilings)"]),
        ((colx + S / 2, coltop + 2.5 * HB), "Column", ["Five 1 x 1 bricks stacked on the top step"]),
        ((fx + 18, fy - 40), "Figure", [f"Rebuilt from {m1['reconstruction']['figure']['source']}, 1:1 and scaled by 2/3; head and torso painted"]),
        ((fx + 14, fy - 24), "Known deviation", ["Chain mail as a honeycomb pattern, cloak and sleeves slightly paler, cheek guards flat"]),
    ]
    hyp_ids = ["hyp_m1_a", "hyp_m1_c", "hyp_m1_d", "hyp_m1_b", "hyp_f_a", "hyp_f_b"]
    apex = (colx, top)

# interpreted statements from the graph
for hid in hyp_ids:
    h = EX[hid]
    need((h, None, None) in g, f"{hid} missing in the graph")
    conf = float(g.value(h, L.confidence))
    cand = g.value(h, L.proposesReferent)
    wd = g.value(cand, SK.closeMatch) if cand else None
    wl = next((str(x) for x in g.objects(wd, RDFS.label)), "") if wd else ""
    st = en(h, L.verificationStatus)
    lines = [f"Confidence {conf:.2f} (subjective estimate). {st}."] + ([f"Wikidata: {str(wd).split('/')[-1]} ({wl})"] if wd else [])
    interp.append((None, en(h), lines))

# ---------------------------------------------------------------- layout of the columns
COLW, LX, RX = 500, 40, W - 40 - 500
TOPY, BOTY = 36, 905


def layout(items):
    """Vertical positions of the statement boxes: (y, height, font size) per item, spread evenly over the column."""
    for size in (13, 12, 11):
        hs = [svg.height_of(COLW, ln, hd, size) for _, hd, ln, _ in items]
        gap = (BOTY - TOPY - sum(hs)) / max(1, len(items) - 1) if len(items) > 1 else 0
        if gap >= 8:
            break
    else:
        sys.exit("draw_pyramid: statements do not fit the column")
    out, y = [], TOPY
    for h in hs:
        out.append((y, h, size))
        y += h + gap
    return out


def column(items, pos, x, side):
    for (tgt, hd, ln, fill), (y, h, size) in zip(items, pos):
        svg.block(x, y, COLW, h, ln, fill, hd, size)
        ex = x + COLW if side == "L" else x
        svg.arrow([(ex, y + h / 2), tgt], head=False, dot=True, sw=1.1, ends=(hd[:30],))


def crossings(lines):
    def o(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    n = 0
    for i, (a, b) in enumerate(lines):
        for c, d in lines[i + 1:]:
            if o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0:
                n += 1
    return n


left = [(t, hd, ln, GREY) for t, hd, ln in meas] + [(t, hd, ln, AMBER) for t, hd, ln in assum]
left.sort(key=lambda it: it[0][1])
right_r = sorted([(t, hd, ln, ORANGE) for t, hd, ln in recon], key=lambda it: it[0][1])
n_i = len(interp)
# interpreted statements: boxes at the top of the right column, their leaders end in a small fan at the apex; try both fan orders
best = None
import itertools
fan = [((n_i - 1) / 2 - k) * 14 for k in range(n_i)]
for perm in itertools.permutations(range(n_i)):
    right_i = [((apex[0] + fan[perm[k]], apex[1] - 4), hd, ln, PURPLE) for k, (_, hd, ln) in enumerate(interp)]
    col_r = right_i + right_r
    pos_r = layout(col_r)
    c = crossings([((RX, y + h / 2), it[0]) for it, (y, h, _) in zip(col_r, pos_r)])
    if best is None or c < best[0]:
        best = (c, col_r, pos_r)
    if c == 0:
        break
_, col_r, pos_r = best
column(left, layout(left), LX, "L")
column(col_r, pos_r, RX, "R")

svg.legend([(GREY, "measured in the scan"), (AMBER, "estimated or assumed"), (ORANGE, "reconstructed"), (PURPLE, "interpreted (hypothesis)")], 40, 950)
svg.save(f"pyramid{MODEL}.svg")
