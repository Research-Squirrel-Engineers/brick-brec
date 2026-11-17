#!/usr/bin/env python
"""lego-lrec orchestrator: the single entry point.

    python main.py                  all steps, in order
    python main.py --list           print steps and exit
    python main.py --only figures   one step
    python main.py --from figures   this step and everything after
    python main.py --skip pages     everything but this
    python main.py --dry-run        print the plan, run nothing
    python main.py --strict         warnings become errors (what CI runs)
    python main.py --png            also render PNG next to the SVG figures (needs resvg_py or playwright)

Each step is also runnable on its own: python py/step_check.py [--strict]
No step touches the network; there is no fetching step.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

if sys.version_info < (3, 10):
    sys.exit(f"lego-lrec needs Python 3.10 or newer (3.12 or newer recommended); this is {sys.version.split()[0]}. See README.md.")
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# (name, module file, what it does)
STEPS = [
    ("check", "py/step_check.py", "ontology parses, drawings match it, FDOx bundle TTLs match pins and ontology"),
    ("reconstruct", "py/step_reconstruct.py", "rebuild both reconstructions (GLB) and compare with the recorded result"),
    ("figures", "py/step_figures.py", "draw overview, class diagram and identification figures (SVG)"),
    ("pages", "py/step_pages.py", "build the documentation site under docs/"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--from", dest="from_")
    ap.add_argument("--skip", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--png", action="store_true")
    a = ap.parse_args()
    names = [s[0] for s in STEPS]
    if a.list:
        for n, f, d in STEPS:
            print(f"{n:12} {f:26} {d}")
        return 0
    for n in [a.only, a.from_, *a.skip]:
        if n and n not in names:
            ap.error(f"unknown step '{n}'; known: {', '.join(names)}")
    plan = [s for s in STEPS if (not a.only or s[0] == a.only) and s[0] not in a.skip]
    if a.from_:
        plan = [s for s in plan if names.index(s[0]) >= names.index(a.from_)]
    if a.dry_run:
        for n, f, d in plan:
            print(f"would run {n}: python {f}{' --strict' if a.strict else ''}")
        return 0
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    report, timings, rc = [], [], 0
    for n, f, d in plan:
        cmd = [sys.executable, str(ROOT / f)] + (["--strict"] if a.strict else []) + (["--png"] if a.png and n == "figures" else [])
        print(f"\n=== {n}: {d}")
        t0 = time.time()
        p = subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
        for line in p.stdout:
            line = line.rstrip("\n")
            print(line)
            report.append(f"[{n}] {line}")
        p.wait()
        timings.append((n, time.time() - t0))
        if p.returncode:
            rc = p.returncode
            print(f"step '{n}' failed (exit {p.returncode}); stopping")
            break
    (ROOT / "dist").mkdir(exist_ok=True)
    # the report file has no timings or dates, so a rerun does not change it
    (ROOT / "dist" / "pipeline_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    total = sum(t for _, t in timings) or 1.0
    print("\nstep          seconds   share")
    for n, t in timings:
        print(f"{n:12} {t:8.1f}  {100 * t / total:5.1f}%")
    return rc


if __name__ == "__main__":
    sys.exit(main())
