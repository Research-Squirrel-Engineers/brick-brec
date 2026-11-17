"""Write data/local-metadata/<slug>/{MD.cff,CITATION.cff} for the four LEGO-pyramid FDOx.

Usage (Windows cmd, from the fdo-3d-packager root):
    python make_local_metadata.py

Everything that differs between the four objects is in the dicts below, so
the script is the place to edit when facts change (P2 scan details, DOIs).
Output is deterministic (no timestamps). Keys named here REPLACE the keys
mdcff generates from Sketchfab (no deep merge, see README of the packager).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data") / "local-metadata"

# --- people -----------------------------------------------------------
FLO = {"label": "Florian Thiery", "id": "https://orcid.org/0000-0002-3246-3531"}
DARIA = {"label": "Daria Stefan", "id": "https://orcid.org/0009-0008-0586-9350"}
CLAUDE = {"label": "Claude (Anthropic), claude-sonnet-5-5"}
FLO_AFF = "Research Squirrel Engineers Network / Leibniz-Zentrum für Archäologie (LEIZA)"

# --- place / time (scan session) ---------------------------------------
SPATIAL = {
    "label": "Schönbrunn Palace, Apothekertrakt, Vienna",
    "id": "http://www.wikidata.org/entity/Q131330",
    "lat": 48.184424,
    "lon": 16.318911,
}
TEMPORAL = {"label": "Scan session 2026-11-12 (during CHNT31)", "start": 2026, "end": 2026}
OSM = "https://www.openstreetmap.org/relation/6892072"

# --- Sketchfab landing pages (also used for cross-links until DOIs exist) -
SF = {
    "p1-scan": "https://sketchfab.com/3d-models/lego-pyramid-kiri-original-b262c1135f1c4159bf1e3628d468bdc8",
    "p1-rec": "https://sketchfab.com/3d-models/lego-pyramid-reconstruction-claudeai-e2fb31006245424e88033714af2c90f5",
    "p2-scan": "https://sketchfab.com/3d-models/lego-pyramid-maya-kiri-original-1e9a188abf974999b7909e15323ded0a",
    "p2-rec": "https://sketchfab.com/3d-models/lego-pyramid-maya-reconstruction-claudeai-fe33b10adee4421fa3a06cc12f7d6c62",
}
TITLE = {
    "p1-scan": "Lego Pyramid (KIRI Original)",
    "p1-rec": "Lego Pyramid (Reconstruction claude.ai)",
    "p2-scan": "Lego Pyramid Maya (KIRI Original)",
    "p2-rec": "Lego Pyramid Maya (Reconstruction claude.ai)",
}

# Zenodo DOIs (created by Florian Thiery 2026-11-17). The first one is the context
# (concept) DOI, as given; they become the id of each FDOx and the target of the
# links between scan and reconstruction.
DOI = {
    "p1-scan": "https://doi.org/10.5281/zenodo.24305240",
    "p1-rec": "https://doi.org/10.5281/zenodo.24305343",
    "p2-scan": "https://doi.org/10.5281/zenodo.24305428",
    "p2-rec": "https://doi.org/10.5281/zenodo.24305436",
}

TODO = "TODO: to be supplied by Florian Thiery"

# --- shared text --------------------------------------------------------
P1_OBJ = (
    "a white stepped LEGO pyramid (nine levels) with a five-brick column and a "
    "minifigure-style warrior figure on top (spiked helmet, mail shirt, tunic, cloak)"
)
P2_OBJ = (
    "a stepped LEGO pyramid with four grey stair arms (seven levels) and a small "
    "temple with four corner pillars on top"
)
SESSION = (
    "scanned on 2026-11-12 in the Apothekertrakt of Schönbrunn Palace, Vienna, where the "
    "model was on display during the CHNT31 conference"
)
AI_NOTE = (
    "AI disclosure: the reconstruction was generated with Claude (Anthropic, "
    "claude-sonnet-5-5) on behalf of Florian Thiery. It is an interpretation model, "
    "not a measurement."
)

HERITAGE_P1 = {
    "object_type": {"label": "LEGO model (interlocking-brick toy, self-built)"},
    "context": (
        "Self-built (own design, no commercial set) by Florian Thiery. Shown at the "
        "Apothekertrakt of Schönbrunn Palace during CHNT31, 2026-11-12 "
        f"({OSM}). The figure on top is read as a medieval warrior; that and any "
        "further identification are open hypotheses, not confirmed."
    ),
    "documentation_purpose": "Test case for FDOx packaging of a scan and its reconstruction.",
}
HERITAGE_P2 = {
    "object_type": {"label": "LEGO model (interlocking-brick toy, self-built)"},
    "context": (
        "Self-built (own design, no commercial set) by Daria Stefan (TU Wien). Shown at "
        "the Apothekertrakt of Schönbrunn Palace during CHNT31, 2026-11-12 "
        f"({OSM}). Identification as a Maya-style stepped pyramid with a temple was "
        "confirmed by the builder. A specific model such as El Castillo (Chichén Itzá) "
        "is NOT confirmed."
    ),
    "documentation_purpose": "Test case for FDOx packaging of a scan and its reconstruction.",
}


def rel_scan(key_other: str, relation: str, note: str) -> dict:
    return {
        "relation": relation,
        "target": {"label": TITLE[key_other], "id": DOI[key_other]},
        "note": note,
    }


def src(key: str) -> dict:
    # mdcff writes this itself; replacing related_resources drops it, so restate it.
    return {
        "relation": "isDerivedFrom",
        "target": {"label": f"Source: {TITLE[key]}", "id": SF[key]},
    }


def md_scan(key: str, other: str, obj: str, builder: str, extra_people: list,
            acq: dict, processing: str, heritage: dict) -> dict:
    return {
        "id": DOI[key],
        "description": (
            f"Photogrammetric 3D scan (KIRI Engine) of {obj}, a hobby build by {builder}; "
            f"{SESSION}. Raw scan without clean-up. The paired reconstruction is a "
            "separate FDOx and derives from this one."
        ),
        "date_created": "2026-11-12",
        "creators": [FLO],
        **({"contributors": extra_people} if extra_people else {}),
        "related_resources": [
            src(key),
            rel_scan(other, "isReferencedBy",
                     "Procedural reconstruction from idealised bricks, derived from this scan."),
        ],
        "spatial": SPATIAL,
        "temporal": TEMPORAL,
        "heritage_object": heritage,
        "technique": {"acquisition": acq, "processing": processing},
    }


def md_rec(key: str, other: str, obj: str, builder: str, extra_people: list,
           processing: dict, heritage: dict) -> dict:
    return {
        "id": DOI[key],
        "description": (
            f"Idealised reconstruction of {obj}, a hobby build by {builder}, rebuilt "
            "procedurally from clean LEGO bricks after a KIRI Engine scan. Only "
            "dimensions and structure were read from the scan; no scan mesh or texture "
            f"was reused. {AI_NOTE}"
        ),
        "creators": [FLO],
        "contributors": [CLAUDE] + extra_people,
        "related_resources": [
            src(key),
            rel_scan(other, "isDerivedFrom",
                     "Scan this reconstruction was measured from (dimensions, grid, orientation)."),
        ],
        "heritage_object": heritage,
        "technique": {
            "processing": processing,
            "programming_languages": ["Python"],
        },
    }


MD = {
    "lego-pyramid-kiri-original": md_scan(
        "p1-scan", "p1-rec", P1_OBJ, "Florian Thiery", [],
        {
            "method": "KIRI Engine (structure from motion photogrammetry), latest app version on "
                      "2026-11-12 (no version number shown in the app), scan at 15:46",
            "hardware": "Samsung Galaxy S26",
            "images_count": "69",
        },
        "KIRI Engine export (GLB, AdvancedExport; a second OBJ export exists). 135,616 "
        "triangles and 68,248 vertices after merging duplicate vertices; not watertight; "
        "no clean-up applied.",
        HERITAGE_P1),
    "lego-pyramid-reconstruction-claudeai": md_rec(
        "p1-rec", "p1-scan", P1_OBJ, "Florian Thiery", [],
        {
            "method": "Procedural rebuild from idealised bricks (script build_lego3.py), not a cleaned scan mesh",
            "random_seed": "numpy.random.default_rng(11)",
            "scale": "2/3 of real LEGO dimensions (8 mm grid, 9.6 mm brick height, 4.8 mm studs), fitted to the scan",
            "structure": "9 levels (14x18 down to 2x2 studs) plus a column of 5 1x1 bricks; 97x 2x4, 5x 2x2, 5x 1x1, all white",
            "figure": "Modelled from 11 photographs supplied by Florian Thiery, 32.3 mm tall, painted head and torso textures",
            "known_deviations": "Cloak, hands and sleeves paler than in the photos; mail shirt as honeycomb pattern; cheek guards flat; sleeves plain tubes",
            "reproducibility": "Re-running the script reproduces lego.glb byte-identically with Python 3.13.18, numpy 2.5.3, trimesh 5.2.1, Pillow 12.3.0, scipy 1.18.1 (sha256 cf51067881aef419856a403725c1352c7c7d14715f286018066991afbc1e9569)",
            "ai_involvement": "Generated with Claude (Anthropic, claude-sonnet-5-5), session 2026-11-12 to 2026-11-17",
        },
        HERITAGE_P1),
    "lego-pyramid-maya-kiri-original": md_scan(
        "p2-scan", "p2-rec", P2_OBJ, "Daria Stefan (TU Wien)", [DARIA],
        {
            "method": "KIRI Engine (structure from motion photogrammetry), latest app version on "
                      "2026-11-12 (no version number shown in the app)",
            "hardware": "Samsung Galaxy A71",
            "images_count": "115",
        },
        "KIRI Engine export (OBJ with MTL and JPG texture). 53,482 triangles and 26,996 "
        "vertices after merging duplicate vertices; not watertight; unit unknown; rotated "
        "by about 16 degrees against the ground, compressed along one axis by a factor of "
        "about 0.72, ground plane included; no clean-up applied.",
        HERITAGE_P2),
    "lego-pyramid-maya-reconstruction-claudeai": md_rec(
        "p2-rec", "p2-scan", P2_OBJ, "Daria Stefan (TU Wien)", [DARIA],
        {
            "method": "Procedural rebuild from idealised bricks (script build_m3.py, version 4), not a cleaned scan mesh",
            "random_seed": "numpy.random.default_rng(5)",
            "alignment": "Scan rotated by 16.25 degrees (sharpness histogram around the temple centre); grid and brick height derived from 4 million surface points (about 13 cells per stud)",
            "structure": "7 levels; four stair arms 4 studs wide reaching 9, 8, 7, 6, 5, 4, 3 studs from the centre; white corner areas 6x6 down to 2x2; temple of 4 layers with four white 1x1 corner pillars",
            "bricks": "white 32x 2x4, 20x 2x2, 12x 1x1, 8 special 1x2/1x4; grey 70x 2x4, 9x 2x2",
            "colours_rgb": "white (245, 245, 241), grey (48, 50, 48)",
            "assumptions": "Seven levels after photo and builder statement (the scan suggests up to eight, the lowest probably merged with the table); pillar rotations 14, -12, 16, -9 degrees and block twist estimated by eye; stair arms on levels 6/7 symmetric in the model but not fully in the photo; scan ground plane not carried over",
            "reproducibility": "Re-running the script reproduces lego3.glb byte-identically with Python 3.13.18, numpy 2.5.3, trimesh 5.2.1, Pillow 12.3.0, scipy 1.18.1 (sha256 543a744f2ec29f9b65c12008cd01b3b2fe829ccf1eeef1bc74b40a27943eac8b)",
            "ai_involvement": "Generated with Claude (Anthropic, claude-sonnet-5-5), session 2026-11-12 to 2026-11-17",
        },
        HERITAGE_P2),
}

def citation(slug: str, md: dict) -> dict:
    return {
        "authors": [{
            "given-names": "Florian",
            "family-names": "Thiery",
            "orcid": "https://orcid.org/0000-0002-3246-3531",
            "affiliation": FLO_AFF,
        }],
        "abstract": md["description"],
        # the package cites itself: concept DOI of this FDOx (same as MD.cff id)
        "doi": md["id"].removeprefix("https://doi.org/"),
    }


def dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8", newline="\n",
    )


def main() -> int:
    for slug, md in MD.items():
        dump(OUT / slug / "MD.cff", md)
        dump(OUT / slug / "CITATION.cff", citation(slug, md))
        print(f"wrote {OUT / slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
