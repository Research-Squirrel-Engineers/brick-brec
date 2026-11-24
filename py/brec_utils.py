"""Shared constants and helpers for brick-brec. Create-once module: paths, release, canonical writers."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# No generator reads the clock. This constant is the only "date" a product may carry.
RELEASE = "0.5.0"

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "py"
ONTOLOGY = ROOT / "ontology" / "brec.ttl"
DATA = ROOT / "data"
RAW = DATA / "raw"
FDOX_BUNDLES = DATA / "fdox" / "bundles"
FDOX_PINS = DATA / "fdox" / "registry_pins.csv"
WIKIDATA_MAP = DATA / "wikidata_mapping.ttl"   # curated by py/wikidata/match.py
DIST = ROOT / "dist"
DOCS = ROOT / "docs"
IMG = DOCS / "visuals" / "img"

NS = {
    "brec": "https://w3id.org/brec/ontology#",
    "ex": "https://w3id.org/brec/id/",
}


def ensure_dirs() -> None:
    for p in (DIST, DIST / "models", DOCS, DOCS / "assets", DOCS / "visuals", IMG):
        p.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    """UTF-8, LF line endings, one trailing newline: byte-stable on every platform."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, data) -> None:
    write_text(path, json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_script(script: Path, args: list[str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a Python script in UTF-8 mode: on Windows open() without an encoding means cp1252 and breaks on umlauts."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONHASHSEED="0")
    return subprocess.run(
        [sys.executable, str(script), *(args or [])],
        cwd=str(cwd or ROOT), env=env, capture_output=True, text=True, encoding="utf-8",
    )


class Report:
    """Collects OK / WARN / FAIL lines; `strict` turns warnings into a failing exit code."""

    def __init__(self, strict: bool = False):
        self.strict, self.warnings, self.failures = strict, 0, 0

    def ok(self, msg: str) -> None:
        print(f"OK    {msg}")

    def warn(self, msg: str) -> None:
        self.warnings += 1
        print(f"WARN  {msg}")

    def fail(self, msg: str) -> None:
        self.failures += 1
        print(f"FAIL  {msg}")

    def exit_code(self) -> int:
        return 1 if self.failures or (self.strict and self.warnings) else 0


def read_pins() -> list[dict]:
    """The registry pins (slug, concept DOI, pinned version DOI, Zenodo version): the one FDOx fact the bundle TTLs do not carry."""
    import csv

    with open(FDOX_PINS, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


CRMDIG_OLD, CRMDIG_NEW = "http://www.ics.forth.gr/isl/CRMdig/", "http://www.cidoc-crm.org/extensions/crmdig/"


def parse_bundle(g, path):
    """Parse a published FDOx bundle TTL. The bundles on Zenodo still use the CRMdig 3.2.1 namespace; the ontology uses the one of CRMdig 5.0,
    so the old namespace is rewritten on reading. The files themselves stay as published (they change with the next Zenodo version)."""
    from pathlib import Path
    g.parse(data=Path(path).read_text(encoding="utf-8").replace(CRMDIG_OLD, CRMDIG_NEW), format="turtle")


def load_graph(with_fdox: bool = True):
    """The ontology graph; with_fdox adds the four bundle TTLs (identical node IRIs merge) and the registry pins as dct:hasVersion."""
    import rdflib
    from rdflib import Literal, URIRef
    from rdflib.namespace import DCTERMS

    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
    if WIKIDATA_MAP.exists():
        g.parse(WIKIDATA_MAP, format="turtle")
    if with_fdox:
        for f in sorted(FDOX_BUNDLES.glob("*.ttl")):
            parse_bundle(g, f)
        for x in read_pins():
            g.add((URIRef("https://doi.org/" + x["concept_doi"]), DCTERMS.hasVersion, Literal(x["pinned_version_doi"])))
    return g
