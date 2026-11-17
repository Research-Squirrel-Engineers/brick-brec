"""figures: draw the overview, the class diagram and the identification figures (SVG, German and English).

The figure scripts in py/figures/ are hand-laid-out drawings with crossing and overlap checks. The English overview is the
German one with its 26 labels replaced from data/overview_labels_en.json. SVG is the product; PNG is optional (--png) and
needs resvg_py or playwright. Nothing here reads the clock.
"""
from __future__ import annotations

import json
import re
import shutil
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from lrec_utils import DATA, DIST, IMG, ONTOLOGY, PY, Report, ensure_dirs, run_script, write_text  # noqa: E402


def to_png(svg, png) -> str:
    try:
        import resvg_py  # type: ignore
        png.write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(svg), zoom=2.0)))
        return "resvg_py"
    except Exception:
        pass
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(device_scale_factor=2)
            pg.goto(svg.resolve().as_uri())
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
    jobs = [
        ("draw.py", [], "ontologie_planar.svg", "overview_de.svg"),
        ("draw_classes.py", ["de", str(ONTOLOGY)], "lrec_klassen.svg", "classes_de.svg"),
        ("draw_classes.py", ["en", str(ONTOLOGY)], "lrec_klassen_en.svg", "classes_en.svg"),
        ("draw_ident.py", [str(ONTOLOGY), "de"], "identifikation.svg", "identification_de.svg"),
        ("draw_ident.py", [str(ONTOLOGY), "en"], "identifikation_en.svg", "identification_en.svg"),
    ]
    made = []
    for script, args, produced, final in jobs:
        p = run_script(PY / "figures" / script, args, cwd=work)
        f = work / produced
        if p.returncode or not f.exists():
            r.fail(f"{script} {args[0] if args and not args[0].endswith('.ttl') else ''}: " + (p.stderr.strip().splitlines() or ["no output"])[-1])
            continue
        write_text(IMG / final, f.read_text(encoding="utf-8"))
        made.append(final)
        r.ok(f"{final}")
    # English overview from the German one
    de = IMG / "overview_de.svg"
    if de.exists():
        m = json.load(open(DATA / "overview_labels_en.json", encoding="utf-8"))
        svg = re.sub(r"(<text[^>]*>)(.*?)(</text>)", lambda x: x.group(1) + m.get(x.group(2), x.group(2)) + x.group(3), de.read_text(encoding="utf-8"), flags=re.S)
        write_text(IMG / "overview_en.svg", svg)
        made.append("overview_en.svg")
        r.ok("overview_en.svg (German drawing, 26 labels replaced)")
    shutil.rmtree(work, ignore_errors=True)
    if png:
        used = ""
        for f in made:
            used = to_png(IMG / f, IMG / f.replace(".svg", ".png")) or used
        r.ok(f"PNG written with {used}") if used else r.warn("no PNG renderer available (pip install resvg_py, or playwright + chromium)")
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv, "--png" in sys.argv))
