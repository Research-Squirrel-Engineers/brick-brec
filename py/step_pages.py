"""pages: build the documentation site under docs/ from the ontology and the figures (static HTML, house style).

Pages: index, data model (modules, classes, properties), CRM coverage, crosswalk, bricks (MBO), instance models, fdox, sparql, viewer, figures (overview and four categories).
Everything is generated; docs/ is committed.
"""
from __future__ import annotations

import html
import shutil
import struct
import sys

import rdflib
from rdflib import RDF, RDFS, OWL, Namespace

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import pages_more  # noqa: E402
import pages_web  # noqa: E402
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
textarea.sparql{display:block;width:100%;min-width:100%;box-sizing:border-box;resize:vertical;font:13px/1.4 ui-monospace,Consolas,monospace;border:1px solid var(--rim);border-radius:6px;padding:8px;background:#fbfbf9}\nsection.q .CodeMirror{height:auto;border:1px solid var(--rim);border-radius:6px;font:13px/1.45 ui-monospace,Consolas,monospace;background:#fbfbf9}.CodeMirror-gutters{background:#f1efe8;border-right:1px solid var(--rim)}
.cm-s-default .cm-keyword{color:#9a3412;font-weight:500}.cm-s-default .cm-variable-2{color:#166534}.cm-s-default .cm-atom{color:#4c1d95}.cm-s-default .cm-string{color:#92400e}
.cm-s-default .cm-comment{color:#6b7280;font-style:italic}.cm-s-default .cm-number{color:#1d4ed8}.cm-s-default .cm-def{color:#4c1d95}.cm-s-default .cm-builtin{color:#9a3412}
.cm-lint-err{background:#fde8e1;border-bottom:2px solid #9a3412}.lint{font-size:13px;min-height:1.4em;margin-top:4px;color:var(--muted)}.lint.good{color:#166534}.lint.bad{color:#9a3412}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#bbb}.dot.ok{background:#166534}.dot.busy{background:#fbbf24}.dot.err{background:#9a3412}\n.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}.grid .card{margin-bottom:0}@media(max-width:700px){.grid{grid-template-columns:1fr}}
"""
PAGES = [("index.html", "Overview"), ("ontology.html", "Data model"), ("coverage.html", "CRM coverage"), ("crosswalk.html", "Crosswalk"), ("bricks.html", "Bricks (MBO)")]
EXPLORE = [("instances.html", "Instance models"), ("fdox.html", "FDOx"), ("sparql.html", "SPARQL"), ("viewer.html", "3D viewer")]
FIGPAGES = pages_more.FIGPAGES
JS_COPY = """<script>document.querySelectorAll("button[data-c]").forEach(function(b){b.addEventListener("click",function(){var ok=function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1200)};if(navigator.clipboard){navigator.clipboard.writeText(b.dataset.c).then(ok).catch(function(){})}})});</script>"""


def esc(x) -> str:
    return html.escape(str(x))


CSSV = __import__("hashlib").sha256(CSS.encode("utf-8")).hexdigest()[:8]   # cache buster: a browser must not keep an old stylesheet after a change


def page(name: str, title: str, body: str, head: str = "") -> None:
    def row(lab, items):
        return f'<div class=grp><span class=lab>{lab}</span><span class=lnk>' + "".join(f'<a href="{f}"{" class=on" if f == name else ""}>{t}</a>' for f, t in items) + "</span></div>"
    nav = row("Documentation", PAGES) + row("Data and tools", EXPLORE) + row("Figures", FIGPAGES)
    write_text(DOCS / name, f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
               f'<title>{esc(title)} | LREC</title><link rel="stylesheet" href="assets/site.css?v={CSSV}">{head}</head><body><nav>{nav}</nav><main>{body}</main>{JS_COPY}</body></html>')


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

    # --- data model, CRM coverage, crosswalk, figures (bodies in pages_more.py)
    gm = load_graph(with_fdox=True)
    missing: list = []
    page("ontology.html", "Data model", pages_more.model_body(g))
    page("coverage.html", "CRM coverage", pages_more.coverage_body(g, missing))
    page("crosswalk.html", "Crosswalk", pages_more.crosswalk_body(g, gm, missing))
    page("instances.html", "Instance models", pages_more.instances_body(gm, missing))
    page("visuals.html", "Figures", pages_more.figures_overview_body(missing))
    for slug, title, _, _ in pages_more.FIGCATS:
        page(f"visuals-{slug}.html", "Figures: " + title, pages_more.figures_cat_body(slug, missing))
    page("bricks.html", "Bricks (MBO)", pages_more.bricks_body(g, missing))
    pages_web.write_graph(gm)
    page("sparql.html", "SPARQL", pages_web.sparql_page(gm, r), pages_web.sparql_head())
    page("viewer.html", "3D viewer", pages_web.viewer_page(r))
    for m in sorted(set(missing)):
        r.warn(f"{m} missing; run the figures step first")

    # --- FDOx: bundle TTLs (identity, title, people, relations) + registry pins + lrec.ttl, merged
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

    r.ok(f"{len(PAGES) + len(EXPLORE) + len(FIGPAGES)} pages, {len(classes)} classes, {len(props)} properties, {len(fdox)} FDOx, docs/lrec.ttl")
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
