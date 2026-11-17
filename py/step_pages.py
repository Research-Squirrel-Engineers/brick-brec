"""pages: build the documentation site under docs/ from the ontology and the figures (static HTML, house style).

Pages: index, ontology (classes, properties), visuals (figures), fdox (the four FDOx, relations),
interpretations (identification hypotheses with status). Everything is generated; docs/ is committed.
"""
from __future__ import annotations

import html
import shutil
import struct
import sys

import rdflib
from rdflib import RDF, RDFS, OWL, Namespace

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from lrec_utils import DOCS, IMG, ONTOLOGY, PY, RELEASE, ROOT, Report, ensure_dirs, load_graph, write_text  # noqa: E402

LREC = Namespace("https://example.org/lego-reconstruction#")
DCT = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
SCHEMA = Namespace("https://schema.org/")
CRMINF = Namespace("http://www.ics.forth.gr/isl/CRMinf/")

CSS = """@font-face{font-family:"Fira Sans";font-weight:400;src:url(fonts/FiraSans-Regular.ttf) format("truetype")}
@font-face{font-family:"Fira Sans";font-weight:500;src:url(fonts/FiraSans-Medium.ttf) format("truetype")}
:root{--bg:#f6f6f3;--card:#fff;--ink:#1f1f1d;--muted:#55544f;--rim:#d8d6ce;--accent:#9a3412}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 "Fira Sans",system-ui,-apple-system,"Segoe UI",Arial,sans-serif}
main{max-width:1040px;margin:0 auto;padding:16px}h1{font-size:28px;font-weight:500;margin:.4em 0}h2{font-size:21px;font-weight:500;margin:1.2em 0 .4em}
nav{max-width:1040px;margin:16px auto 0;border:1px solid var(--rim);border-radius:10px;background:var(--card);font-size:15px;overflow:hidden}
nav .grp{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;padding:9px 14px;border-left:5px solid var(--ink)}
nav .grp+.grp{border-top:2px solid var(--rim);border-left-color:var(--accent)}
nav .lab{width:118px;text-align:center;padding:2px 0;border-radius:4px;background:var(--ink);color:#fff;font-size:12px;letter-spacing:.06em;text-transform:uppercase}
nav .grp+.grp .lab{background:var(--accent)}
nav .lnk{display:flex;flex-wrap:wrap;gap:4px 18px}nav a{color:var(--muted);text-decoration:none}nav a:hover{color:var(--accent)}
nav a.on{color:var(--accent);font-weight:500}a{color:var(--accent)}
@media(max-width:760px){nav .lab{width:100%}}
button{font:inherit;font-size:14px;padding:5px 12px;border:1px solid var(--accent);border-radius:6px;background:#fff;color:var(--accent);cursor:pointer;float:right;margin-left:12px}
button:hover{background:var(--accent);color:#fff}
section,.card{background:var(--card);border:1px solid var(--rim);border-radius:10px;padding:16px;margin-bottom:24px;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--rim);vertical-align:top}th{font-weight:500;color:var(--muted)}
code{font-size:14px;background:#f1efe8;padding:1px 4px;border-radius:4px}.muted{color:var(--muted);font-size:14px}
img{max-width:100%;height:auto}.n{color:var(--accent);font-weight:500;margin-right:8px}.cap{font-size:20px;font-weight:500}
blockquote{background:#fff7e0;border-left:4px solid #fbbf24;margin:12px 0;padding:8px 12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:700px){.grid{grid-template-columns:1fr}}
"""
PAGES = [("index.html", "Overview"), ("ontology.html", "Ontology"), ("visuals.html", "Figures"), ("fdox.html", "FDOx"), ("interpretations.html", "Interpretations")]
FIGPAGES = [("visuals.html#overview", "Whole model"), ("visuals.html#classes", "Class diagram"), ("visuals.html#identification", "Identification")]
JS_COPY = """<script>document.querySelectorAll("button[data-c]").forEach(function(b){b.addEventListener("click",function(){var ok=function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1200)};if(navigator.clipboard){navigator.clipboard.writeText(b.dataset.c).then(ok).catch(function(){})}})});</script>"""


def esc(x) -> str:
    return html.escape(str(x))


def page(name: str, title: str, body: str) -> None:
    def row(lab, items):
        return f'<div class=grp><span class=lab>{lab}</span><span class=lnk>' + "".join(f'<a href="{f}"{" class=on" if f == name else ""}>{t}</a>' for f, t in items) + "</span></div>"
    nav = row("Documentation", PAGES) + row("Figures", FIGPAGES)
    write_text(DOCS / name, f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
               f'<title>{esc(title)} | LREC</title><link rel="stylesheet" href="assets/site.css"></head><body><nav>{nav}</nav><main>{body}</main>{JS_COPY}</body></html>')


def label(g, s, lang="en") -> str:
    for l in g.objects(s, RDFS.label):
        if getattr(l, "language", None) == lang:
            return str(l)
    return next((str(l) for l in g.objects(s, RDFS.label)), g.namespace_manager.normalizeUri(s))


def q(g, s) -> str:
    return g.namespace_manager.normalizeUri(s) if isinstance(s, rdflib.URIRef) else str(s)


def main(strict: bool) -> int:
    r = Report(strict)
    ensure_dirs()
    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
    write_text(DOCS / "assets" / "site.css", CSS)
    (DOCS / "assets" / "fonts").mkdir(exist_ok=True)
    for n in ("FiraSans-Regular.ttf", "FiraSans-Medium.ttf", "LICENSE-FiraSans.txt"):
        shutil.copyfile(PY / "figures" / "fonts" / n, DOCS / "assets" / "fonts" / n)
    shutil.copyfile(ONTOLOGY, DOCS / "lrec.ttl")
    (DOCS / "notes").mkdir(exist_ok=True)
    for n in ("LREC_en.md", "LREC.md", "IDENTIFIKATION_en.md", "FDOx_Pyramiden_Metadaten.md", "aenderungen_en.md"):
        shutil.copyfile(ROOT / "notes" / n, DOCS / "notes" / n)

    classes = sorted((c for c in g.subjects(RDF.type, OWL.Class) if str(c).startswith(str(LREC))), key=str)
    props = sorted((p for p in g.subjects(RDF.type, None) if str(p).startswith(str(LREC)) and (p, RDF.type, OWL.ObjectProperty) in g or (p, RDF.type, OWL.DatatypeProperty) in g), key=str)
    props = sorted(set(props), key=str)

    # --- index
    body = (f"<h1>LREC: LEGO Reconstruction Ontology</h1><p class=muted>Release {RELEASE}</p><section>"
            "<p>From a structure-from-motion scan of a LEGO model to an idealised brick reconstruction, its documentation and its interpretation, "
            "modelled with CIDOC CRM (+ CRMdig, CRMinf), PROV-O, DCAT, DQV, OWL-Time, GeoSPARQL, SKOS and Wikidata.</p>"
            f"<p>{len(g)} triples, {len(classes)} LREC classes, {len(props)} own properties. German and English labels.</p>"
            '<p><a href="lrec.ttl">lrec.ttl</a> · <a href="notes/LREC_en.md">LREC (English)</a> · <a href="notes/LREC.md">LREC (Deutsch)</a> · '
            '<a href="notes/FDOx_Pyramiden_Metadaten.md">FDOx metadata (Deutsch)</a> · <a href="notes/aenderungen_en.md">What changed from scan to reconstruction</a></p></section>'
            '<section><h2>Pipeline</h2><pre>scan (KIRI) -> measurement -> reconstruction (bricks, GLB) -> interpretation -> FDOx (Zenodo)\n'
            'main.py: check -> reconstruct -> figures -> pages</pre></section>')
    page("index.html", "LREC", body)

    # --- ontology
    rows = ""
    for c in classes:
        parents = ", ".join(f"<code>{esc(q(g, o))}</code>" for o in sorted(g.objects(c, RDFS.subClassOf), key=str))
        com = next((str(x) for x in g.objects(c, RDFS.comment) if getattr(x, "language", None) == "en"), "")
        rows += f"<tr><td><code>{esc(q(g, c))}</code></td><td>{esc(label(g, c, 'en'))}<br><span class=muted>{esc(label(g, c, 'de'))}</span></td><td>{parents}</td><td>{esc(com)}</td></tr>"
    prow = ""
    for p in props:
        dom = ", ".join(esc(q(g, o)) for o in g.objects(p, RDFS.domain)); rng = ", ".join(esc(q(g, o)) for o in g.objects(p, RDFS.range))
        kind = "object" if (p, RDF.type, OWL.ObjectProperty) in g else "data"
        prow += f"<tr><td><code>{esc(q(g, p))}</code></td><td>{esc(label(g, p, 'en'))}</td><td>{kind}</td><td>{dom}</td><td>{rng}</td></tr>"
    page("ontology.html", "Ontology", f"<h1>Ontology</h1><section><h2>Classes ({len(classes)})</h2><table><tr><th>Class</th><th>Label (en / de)</th><th>Subclass of</th><th>Note</th></tr>{rows}</table></section>"
         f"<section><h2>Own properties ({len(props)})</h2><table><tr><th>Property</th><th>Label</th><th>Kind</th><th>Domain</th><th>Range</th></tr>{prow}</table></section>")

    # --- visuals (English only; what a figure needs to be read goes here, not into the figure)
    figs = [("overview", "Whole model: scan, reconstruction, interpretation, FDOx packages",
             "Shown for pyramid 2. Pyramid 1 is analogous (FDOx concept DOIs 10.5281/zenodo.24305240 for the scan and 10.5281/zenodo.24305343 for the reconstruction). "
             "Noted inside the classes without a node of their own: DCAT-AP, CodeMeta, SKOS, Wikidata (closeMatch), OWL-Time (P4); every class is also a prov:Entity, prov:Activity or prov:Agent (subclass relation, not drawn)."),
            ("classes", "LREC class diagram",
             "Hollow-triangle arrows are rdfs:subClassOf; the parent classes are listed per class so that no lines cross. Amber text marks attributes (datatype properties); the solid arrow is an object property."),
            ("identification", "Identification: evidence, hypotheses, candidates",
             "Confidence is a subjective estimate by the AI assistant (0 to 1), not a measurement; hypotheses overlap and do not sum to 1.")]
    cards = ""
    for i, (stem, cap, note) in enumerate(figs, 1):
        f = f"{stem}.svg"
        if not (IMG / f).exists():
            r.warn(f"{f} missing; run the figures step first")
            continue
        png = IMG / f"{stem}.png"   # an SVG used as <img> cannot load the page fonts, so the page shows the PNG when there is one
        if png.exists():
            wpx, hpx = struct.unpack(">II", png.read_bytes()[16:24])
            shown = f'<img src="visuals/img/{stem}.png" width="{wpx}" height="{hpx}" loading="lazy" alt="{esc(cap)}">'
            dl = f'<a href="visuals/img/{stem}.png">PNG</a> · <a href="visuals/img/{f}">SVG</a>'
        else:
            shown, dl = f'<img src="visuals/img/{f}" alt="{esc(cap)}">', f'<a href="visuals/img/{f}">SVG</a>'
        cards += (f'<div class=card id={stem}>{shown}<p><button type=button data-c="{esc(cap)}">Copy</button><span class=n>F{i}</span><span class=cap>{esc(cap)}</span></p>'
                  f'<p class=muted>{esc(note)} Generated by py/figures from ontology/lrec.ttl. {dl}</p></div>')
    page("visuals.html", "Figures", f"<h1>Figures</h1>{cards}")

    # --- FDOx: bundle TTLs (identity, title, people, relations) + registry pins + lrec.ttl, merged
    gm = load_graph(with_fdox=True)
    fdox = sorted(gm.subjects(RDF.type, LREC.FDOx), key=str)

    def who(n) -> str:
        return str(gm.value(n, RDFS.label) or gm.value(n, SCHEMA.name) or n)

    frows = ""
    for f in fdox:
        doi = str(f).split("doi.org/")[-1]; ver = str(gm.value(f, DCT.hasVersion))
        sk = next((str(o) for o in gm.objects(f, DCT.relation) if "sketchfab.com" in str(o)), "")
        der = ", ".join(f'<a href="{esc(o)}">{esc(str(o).split("zenodo.")[-1])}</a>' for o in sorted(gm.objects(f, PROV.wasDerivedFrom), key=str) if "zenodo" in str(o))
        people = "; ".join([who(o) + " (creator)" for o in sorted(gm.objects(f, DCT.creator), key=str)] +
                           [who(o) + " (contributor)" for o in sorted(gm.objects(f, DCT.contributor), key=str)])
        frows += (f'<tr><td>{esc(gm.value(f, DCT.title))}</td><td><a href="https://doi.org/{esc(doi)}">{esc(doi)}</a></td><td>{esc(ver)}</td>'
                  f'<td>{der or "-"}</td><td>{esc(people)}</td><td><a href="{esc(sk)}">Sketchfab</a></td></tr>')
    rel = ""
    for f in fdox:
        for rr in sorted(gm.objects(f, DCAT.qualifiedRelation), key=lambda n: (str(gm.value(n, DCT.relation)), str(gm.value(n, DCAT.hadRole)))):
            rel += (f"<tr><td>{esc(str(f).split('zenodo.')[-1])}</td><td>{esc(q(gm, gm.value(rr, DCAT.hadRole)))}</td>"
                    f"<td>{esc(str(gm.value(rr, DCT.relation)).split('zenodo.')[-1])}</td><td>{esc(gm.value(rr, RDFS.comment))}</td></tr>")
    page("fdox.html", "FDOx", f"<h1>The four FDOx</h1><section><table><tr><th>Title</th><th>Concept DOI (identity)</th><th>Pinned version DOI</th><th>Derived from</th><th>People</th><th>Model page</th></tr>{frows}</table>"
         "<blockquote>Everything in this table except the pinned version DOI is read from the <code>fdo-metadata.ttl</code> of the published bundles (<code>data/fdox/bundles/</code>); "
         "the version DOI is the registry pin (<code>data/fdox/registry_pins.csv</code>). Check both against the Zenodo page before entering them.</blockquote></section>"
         f"<section><h2>Relations between the FDOx</h2><table><tr><th>From (concept DOI suffix)</th><th>Role</th><th>To</th><th>Note</th></tr>{rel}</table></section>")

    # --- interpretations
    hrows = ""
    for ident in sorted(g.subjects(RDF.type, LREC.Identification), key=str):
        for h in sorted(g.objects(ident, CRMINF.J2_concluded_that), key=str):
            c = g.value(h, LREC.confidence); st = g.value(h, LREC.verificationStatus); sp = g.value(h, LREC.specializes)
            hrows += (f"<tr><td>{esc(q(g, ident))}</td><td>{esc(label(g, h, 'en'))}</td><td>{esc(c)}</td><td>{esc(q(g, sp)) if sp else ''}</td><td>{esc(st)}</td></tr>")
    page("interpretations.html", "Interpretations", "<h1>Identification hypotheses</h1><section><p>Confidence is a subjective estimate by the AI assistant, not a measurement. Hypotheses overlap and do not sum to 1.</p>"
         f"<table><tr><th>Identification</th><th>Hypothesis</th><th>Confidence</th><th>Specialises</th><th>Status</th></tr>{hrows}</table></section>")
    r.ok(f"{len(PAGES)} pages, {len(classes)} classes, {len(props)} properties, {len(fdox)} FDOx, docs/lrec.ttl")
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
