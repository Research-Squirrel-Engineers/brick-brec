# lego-lrec

LREC, the **LEGO Reconstruction Ontology**, with the pipeline that reproduces its figures, models and documentation site.
It documents the path from a structure-from-motion scan (KIRI Engine) of a LEGO model to an idealised brick reconstruction,
its interpretation (what does the object represent, with arguments and confidence) and its packaging as FDOx on Zenodo.

Two pyramids are modelled: P1 (pyramid with column and figure) and P2 (stepped "Maya" pyramid with temple), each as a scan
FDOx and a reconstruction FDOx (four in total, see `data/fdox/bundles/`).

## Quick start (Windows cmd)

```cmd
pip install -r requirements.txt && python main.py
```

Python 3.12 or newer is the verified reference (3.13.18). Python 3.10 and 3.11 work too (the pins switch automatically; see the comments in
`requirements.txt`). Older versions stop with a message.

Everything runs offline. The run rebuilds both reconstructions (byte-identical with the pinned libraries), redraws the figures
and regenerates `docs/` and `dist/`. Run it twice: `git status` must stay clean.

```cmd
python main.py --list
python main.py --only figures
python main.py --from figures
python main.py --dry-run
python main.py --strict
python main.py --no-png
```

`--strict` turns warnings into errors; a complete run is expected to pass it. `--no-png` skips the PNG that is rendered next to each SVG figure.

Wikidata mappings of the identification candidates are curated by hand: `python py/wikidata/match.py` (needs the network, not part of `main.py`) lists the Wikidata hits per search term and writes your picks to `data/wikidata_mapping.ttl`; `python main.py` reads that file (check, figure, pages). `--list` only writes `dist/wikidata_candidates.md`.

The figures are set in Fira Sans (SIL Open Font Licence, `py/figures/fonts/`); the SVG names the font, the PNG is rendered with the font files, and the docs pages carry the font files in `docs/assets/fonts/`.

## Layout

| Path | Role |
|---|---|
| `ontology/lrec.ttl` | the ontology and the worked examples (source of truth, German and English labels) |
| `py/step_*.py` | the four pipeline steps (`check`, `reconstruct`, `figures`, `pages`), each runnable on its own |
| `py/reconstruct/` | procedural brick reconstructions of P1 and P2 (seeded, no scan files read) |
| `py/figures/` | hand-laid-out SVG drawings with crossing checks; `wikidata_match.py` is interactive (run it yourself) |
| `py/interpret/` | toolkit for "fresh chat" interpretation of any 3D model (facts, prompt, schema, converter), see its README |
| `py/fdox/` | script that writes the FDOx override files for the fdo-3d-packager |
| `data/fdox/` | the four `fdo-metadata.ttl` of the published bundles (source of truth for identity, title, people, relations), the registry pins (version DOIs) and bundle checksums |
| `interpretations/` | archived interpretation runs (prompt, images, raw answer, converted Turtle) |
| `notes/` | long-form documentation (German and English) |
| `dist/`, `docs/` | generated products, committed |

## Documentation site

`docs/index.html` (open locally or publish with GitHub Pages from `/docs`) has the ontology tables, the figures in both
languages, the four FDOx and the identification hypotheses with their status.

## Links

- Repository: <https://github.com/Research-Squirrel-Engineers/lego-lrec>
- Documentation site (GitHub Pages, from `docs/`): <https://research-squirrel-engineers.github.io/lego-lrec/>

## Licence

MIT, see `LICENSE`. The scan and reconstruction models on Sketchfab and Zenodo are CC BY 4.0.
