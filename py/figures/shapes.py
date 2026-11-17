"""Schematic LEGO pyramid shapes shared by the story and node figures (front view, studs on top of every level)."""
import math

from svgkit import AMBER, GREY, ORANGE, PURPLE, WHITE

LEVEL_W = [15, 13, 11, 9, 7, 5, 3]   # studs per level, bottom to top: seven levels as in the reconstruction of pyramid 2


def stepped(svg, cx, base, unit, lh, mode="solid", fills=None):
    """Draw the seven levels from the base line upwards. mode: solid (the original), points (scan, noisy dots), bricks (reconstruction)."""
    x0 = cx - LEVEL_W[0] * unit / 2
    top = base - len(LEVEL_W) * lh
    if mode == "points":
        # scan: the same outline as dots, shifted by a fixed wobble, plus a few stray points; no random numbers, so the output is stable
        k = 0
        for lv, w in enumerate(LEVEL_W):
            y = base - (lv + 1) * lh
            for i in range(int(w * 2)):
                x = cx - w * unit / 2 + (i + 0.5) * unit / 2
                for dy in (0, lh * 0.5, lh):
                    k += 1
                    wob = math.sin(k * 1.7) * 3.2
                    svg.o.append(f'<circle cx="{x + wob:.1f}" cy="{y + dy + math.cos(k * 2.3) * 3.2:.1f}" r="1.7" fill="#555"/>')
        for i in range(14):
            svg.o.append(f'<circle cx="{cx + math.sin(i * 5.1) * LEVEL_W[0] * unit * 0.62:.1f}" cy="{base - lh * 7 * abs(math.sin(i * 3.3)) - 4:.1f}" r="1.7" fill="#999"/>')
        return top
    for lv, w in enumerate(LEVEL_W):
        y = base - (lv + 1) * lh
        fill = (fills or [GREY] * 7)[lv] if mode == "solid" else (fills or [ORANGE] * 7)[lv]
        if mode == "solid":
            svg.o.append(f'<rect x="{cx - w * unit / 2:.1f}" y="{y:.1f}" width="{w * unit:.1f}" height="{lh:.1f}" fill="{fill}" stroke="#000" stroke-width="1.2"/>')
            for i in range(w):
                sx = cx - w * unit / 2 + (i + 0.5) * unit
                svg.o.append(f'<rect x="{sx - unit * 0.28:.1f}" y="{y - 4:.1f}" width="{unit * 0.56:.1f}" height="4" rx="1.5" fill="{fill}" stroke="#000" stroke-width="0.8"/>')
        else:   # bricks: a seam every two studs, as the reconstruction lays 2x4 and 2x2 bricks
            for i in range(0, w, 2):
                bw = min(2, w - i) * unit
                svg.o.append(f'<rect x="{cx - w * unit / 2 + i * unit:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{lh:.1f}" fill="{fill}" stroke="#000" stroke-width="1"/>')
    return top
