"""figures: draw the overview, the class diagram and the identification figure (SVG, English only, no header or footer).

The figure scripts in py/figures/ are hand-laid-out drawings with crossing and overlap checks; the labels on the arrows are amber
chips centred on the arrows. SVG (Fira Sans named, not embedded) is the product; the PNG next to it (resvg_py, Fira Sans from py/figures/fonts)
is what the docs pages show, because an SVG used as <img> cannot load fonts. --no-png skips it. Nothing here reads the clock.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from lrec_utils import DIST, IMG, ONTOLOGY, PY, Report, ensure_dirs, run_script, write_text  # noqa: E402


def to_png(svg, png) -> str:
    """PNG with Fira Sans: resvg_py gets the font files and ignores system fonts, so the result is the same on every machine."""
    fonts = [str(PY / "figures" / "fonts" / n) for n in ("FiraSans-Regular.ttf", "FiraSans-Medium.ttf")]
    try:
        import resvg_py  # type: ignore
        png.write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(svg), background="#ffffff", skip_system_fonts=True, font_files=fonts, zoom=2.0)))
        return "resvg_py"
    except Exception:
        pass
    try:   # fallback: Chromium; Fira Sans is loaded from the font files through @font-face
        from playwright.sync_api import sync_playwright  # type: ignore
        faces = "".join(f'@font-face{{font-family:"Fira Sans";font-weight:{w};src:url({pathlib.Path(f).as_uri()})}}' for f, w in zip(fonts, (400, 500)))
        html = f"<style>{faces}body{{margin:0}}</style>" + svg.read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(device_scale_factor=2)
            pg.set_content(html)
            pg.evaluate("document.fonts.ready")
            pg.locator("svg").screenshot(path=str(png))
            b.close()
        return "playwright"
    except Exception:
        return ""


def main(strict: bool, png: bool) -> int:
    r = Report(strict)
    ensure_dirs()
    work = DIST / "figures_work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    for old in IMG.glob("*"):   # the figures are English only; drop what earlier versions wrote (de/en pairs)
        if old.is_file():
            old.unlink()
    jobs = [
        ("draw.py", [], "ontologie_planar.svg", "overview.svg"),
        ("draw_classes.py", ["en", str(ONTOLOGY)], "lrec_klassen_en.svg", "classes.svg"),
        ("draw_ident.py", [str(ONTOLOGY), "en"], "identifikation_en.svg", "identification.svg"),
    ]
    made = []
    for script, args, produced, final in jobs:
        p = run_script(PY / "figures" / script, args, cwd=work)
        f = work / produced
        if p.returncode or not f.exists():
            r.fail(f"{script}: " + (p.stderr.strip().splitlines() or ["no output"])[-1])
            continue
        write_text(IMG / final, f.read_text(encoding="utf-8"))
        made.append(final)
        r.ok(f"{final}")
        if script == "draw.py":   # the drawing script reports overlaps of its labels, boxes and lines
            m = re.search(r"crossings/overlaps: (\[.*\])", p.stdout)
            if m and m.group(1) != "[]":
                r.fail(f"overview drawing: crossings or overlaps {m.group(1)}")
    shutil.rmtree(work, ignore_errors=True)
    if png:
        used = ""
        for f in made:
            used = to_png(IMG / f, IMG / f.replace(".svg", ".png")) or used
        r.ok(f"PNG written with {used}") if used else r.warn("no PNG renderer available (pip install resvg_py, or playwright + chromium)")
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv, "--no-png" not in sys.argv))
