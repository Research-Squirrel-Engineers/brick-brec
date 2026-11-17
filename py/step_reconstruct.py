"""reconstruct: rebuild both LEGO reconstructions from their scripts and compare with the recorded result.

The scripts read no scan files: everything measured from the scans is a constant inside them (see
notes/aenderungen_en.md). Output must be byte-identical with the pinned libraries; with other library
versions the bytes may differ, so the fallback is a geometry check (face count and bounding box).
"""
from __future__ import annotations

import json
import shutil
import sys

import trimesh

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from lrec_utils import DATA, DIST, PY, Report, ensure_dirs, run_script, sha256_file  # noqa: E402


def main(strict: bool) -> int:
    r = Report(strict)
    ensure_dirs()
    work = DIST / "reconstruction_work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    expected = json.load(open(DATA / "expected_models.json", encoding="utf-8"))
    for name, e in sorted(expected.items()):
        script = PY / "reconstruct" / e["script"]
        p = run_script(script, cwd=work)
        out = work / e["output"]
        if p.returncode or not out.exists():
            r.fail(f"{e['script']} failed: " + (p.stderr.strip().splitlines() or ['no output'])[-1])
            continue
        target = DIST / "models" / name
        shutil.copyfile(out, target)
        sha = sha256_file(target)
        if sha == e["sha256"]:
            r.ok(f"{name}: byte-identical to the recorded build ({sha[:12]}...)")
            continue
        if sha in e.get("sha256_alt", {}):
            r.ok(f"{name}: byte-identical to the recorded build for {e['sha256_alt'][sha]} ({sha[:12]}...)")
            continue
        s = trimesh.load(target)
        faces = sum(len(g.faces) for g in s.geometry.values())
        bounds = [round(float(x), 5) for x in s.bounds.ravel()]
        same_geom = faces == e["faces"] and all(abs(a - b) < 2e-5 for a, b in zip(bounds, e["bounds"]))
        (r.warn if same_geom else r.fail)(
            f"{name}: bytes differ from the recorded build; geometry {'matches' if same_geom else 'DIFFERS'} "
            f"({faces} faces vs {e['faces']}). Library versions differ from requirements.txt?")
    shutil.rmtree(work, ignore_errors=True)
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
