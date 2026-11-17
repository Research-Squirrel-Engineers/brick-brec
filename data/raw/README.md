# data/raw

Raw scan inputs are large (up to 22 MB per file) and are **not** part of the repository. They are the originals of the
four FDOx and are published on Zenodo and Sketchfab (see `data/fdox/registry_pins.csv` and `data/fdox/bundles/`).

If you place them here, `python main.py --only check` verifies them against `CHECKSUMS.json`:

| Label in CHECKSUMS.json | Put it here as |
|---|---|
| `3DModel_Custom.glb (P1 scan)` | `data/raw/p1/3DModel_Custom.glb` |
| `3DModel.obj (P1 scan, second export)` and `3DModel.obj (P2 scan)` | `data/raw/p1/3DModel.obj`, `data/raw/p2/3DModel.obj` (same file name, different content) |
| `3DModel.mtl`, `3DModel.jpg` (P2 scan) | `data/raw/p2/` |

The reconstruction scripts do not read these files; everything measured from the scans is a constant inside
`py/reconstruct/*.py`. Keep the files unchanged and read-only.
