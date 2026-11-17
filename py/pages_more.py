"""Page bodies of the documentation site that are built from the graph: data model, CRM coverage, crosswalk, instance models, figure cards.

Used by step_pages.py (which owns the navigation and the page shell). Everything here reads the ontology graph (g) or the merged graph
with the FDOx bundles and the Wikidata mapping (gm); nothing is typed in by hand except the module grouping, which the check enforces.
"""
from __future__ import annotations

import html
import struct

from rdflib import OWL, RDF, RDFS, Literal, Namespace, URIRef

from crm_coverage import FAMILY, anchors, chains, own_classes
from lrec_utils import IMG, read_pins

LREC = Namespace("https://example.org/lego-reconstruction#")
EX = Namespace("https://example.org/lego-reconstruction/id/")
DCT, PROV, SK = Namespace("http://purl.org/dc/terms/"), Namespace("http://www.w3.org/ns/prov#"), Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA, CRMINF = Namespace("https://schema.org/"), Namespace("http://www.ics.forth.gr/isl/CRMinf/")
CREDIT = "Source: ontology/lrec.ttl and the notes of the repository; Research Squirrel Engineers at LEIZA."

# the three modules of the model; every own class must be listed (step_pages fails otherwise)
MODULES = [
    ("Scan and reconstruction", "From the physical model through the SfM scan, the measurement and the brick reconstruction to its documentation.",
     ["LegoModel", "LegoModelTwin", "ScanDigitization", "RawScan", "ReferencePhoto", "ScanLocation", "ProcessInterval", "AlignmentAndMeasurement",
      "StructureInference", "Assumption", "ProceduralReconstruction", "ReconstructionModel", "ReconstructionScript", "QualityMeasurement",
      "BrickType", "ChangeDocumentation", "AIAssistant"], ["overview", "classes"]),
    ("Identification", "What does the object represent? Evidence supports or weakens hypotheses; a hypothesis proposes a candidate referent, which can be linked to Wikidata.",
     ["Identification", "IdentityHypothesis", "Evidence", "CandidateReferent"], ["identification"]),
    ("Packaging (FDOx)", "The Zenodo records that carry a scan or a reconstruction; identity is the concept DOI, the version DOI is a pin.",
     ["FDOx", "ReconstructionDataset"], ["hub"]),
]

# figures of the site: stem, caption, note
FIGS = [
    ("story", "From the pyramid to the Linked Open Data cloud",
     "Five stages: the physical pyramid, the SfM scan, the brick reconstruction, the interpretation and the anchoring. Photo counts and confidences are read from the graph; the scan is drawn as noisy points, the reconstruction as bricks (schematic)."),
    ("architecture", "Architecture: CRM family, LREC domain layer, standards, knowledge graph",
     "The three modules of the data model sit under the CRM family and reuse W3C vocabularies; the knowledge graph built from them is linked to the Linked Open Data cloud."),
    ("node", "One pyramid as a node and what it is linked to",
     "Pyramid 2. Every link is a statement in the graph; the dashed box marks a Wikidata item that has not been chosen yet (data/wikidata_mapping.ttl)."),
    ("overview", "Whole model: scan, reconstruction, interpretation, FDOx packages",
     "Shown for pyramid 2. Pyramid 1 is analogous (FDOx concept DOIs 10.5281/zenodo.24305240 for the scan and 10.5281/zenodo.24305343 for the reconstruction). "
     "Noted inside the classes without a node of their own: DCAT-AP, CodeMeta, SKOS, Wikidata (closeMatch), OWL-Time (P4); every class is also a prov:Entity, prov:Activity or prov:Agent (subclass relation, not drawn)."),
    ("classes", "LREC class diagram",
     "Hollow-triangle arrows are rdfs:subClassOf; the parent classes are listed per class so that no lines cross. Amber text marks attributes (datatype properties); the solid arrow is an object property."),
    ("identification", "Identification: evidence, hypotheses, candidates",
     "Confidence is a subjective estimate by the AI assistant (0 to 1), not a measurement; hypotheses overlap and do not sum to 1. Wikidata items are picked by hand (data/wikidata_mapping.ttl)."),
    ("pyramid1", "Pyramid 1: measured, estimated, reconstructed and interpreted",
     "Schematic front view; widths follow the studs of the reconstruction. Numbers in the statements are read from the change documentation and the graph; the figure on the column is drawn schematically (own drawing)."),
    ("pyramid2", "Pyramid 2: measured, estimated, reconstructed and interpreted",
     "Schematic front view; stair-arm reach and corner blocks follow the reconstruction (v2 to v4). The builder confirmed the Maya step pyramid on 2026-11-17; El Castillo is not confirmed."),
    ("hub", "One FDOx and what it is linked to",
     "The reconstruction record of pyramid 2. Every link is a statement in the merged graph (bundle TTL, pins and lrec.ttl)."),
    ("workflow", "Inputs, the four steps of main.py, outputs",
     "Step names are read from main.py; counts from the repository files."),
    ("coverage", "Own classes by their nearest CRM-family anchor",
     "A class with two anchors stands in both groups; (via) marks an anchor reached through another own class."),
    ("crosswalk", "Crosswalk: classes against vocabularies",
     "Direct rdfs:subClassOf parents of every LREC class, one column per vocabulary; orange cells are the CRM family anchors."),
]
FIG_NAV = [("visuals.html#" + s, t) for s, t in [("story", "Story"), ("architecture", "Architecture"), ("overview", "Whole model"), ("classes", "Class diagram"),
                                                 ("identification", "Identification"), ("node", "Pyramid node"), ("pyramid1", "Pyramid 1"), ("pyramid2", "Pyramid 2"),
                                                 ("hub", "FDOx node"), ("workflow", "Workflow"), ("coverage", "CRM anchors"), ("crosswalk", "Crosswalk")]]


def esc(x) -> str:
    return html.escape(str(x))


def q(g, s) -> str:
    return g.namespace_manager.normalizeUri(s).strip("<>") if isinstance(s, URIRef) else str(s)


def label(g, s, lang="en") -> str:
    for l in g.objects(s, RDFS.label):
        if getattr(l, "language", None) == lang:
            return str(l)
    return next((str(l) for l in g.objects(s, RDFS.label)), q(g, s))


def comment(g, s) -> str:
    for lang in ("en", "de"):
        for c in g.objects(s, RDFS.comment):
            if getattr(c, "language", None) == lang:
                return str(c)
    return ""


def fig_by(stem: str, n: str, missing: list) -> str:
    cap, note = next((c, t) for s, c, t in FIGS if s == stem)
    return fig_card(stem, cap, note, n, missing)


def fig_card(stem: str, cap: str, note: str, n: str, missing: list) -> str:
    svg, png = IMG / f"{stem}.svg", IMG / f"{stem}.png"
    if not svg.exists():
        missing.append(f"{stem}.svg")
        return ""
    if png.exists():   # an SVG used as <img> cannot load the page fonts, so the page shows the PNG when there is one
        w, h = struct.unpack(">II", png.read_bytes()[16:24])
        shown = f'<img src="visuals/img/{stem}.png" width="{w}" height="{h}" loading="lazy" alt="{esc(cap)}">'
        dl = f'<a href="visuals/img/{stem}.png">PNG</a> · <a href="visuals/img/{stem}.svg">SVG</a>'
    else:
        shown, dl = f'<img src="visuals/img/{stem}.svg" alt="{esc(cap)}">', f'<a href="visuals/img/{stem}.svg">SVG</a>'
    return (f'<div class=card id={stem}>{shown}<p><button type=button data-c="{esc(cap)}">Copy</button><span class=n>{esc(n)}</span><span class=cap>{esc(cap)}</span></p>'
            f'<p class=muted>{esc(note)} {esc(CREDIT)} {dl}</p></div>')


def figures_body(missing: list) -> str:
    return "<h1>Figures</h1>" + "".join(fig_card(s, c, n, f"F{i}", missing) for i, (s, c, n) in enumerate(FIGS, 1))


def module_of(name: str):
    for k, (_, _, names, _) in enumerate(MODULES):
        if name in names:
            return k
    return None


def unassigned(g) -> list:
    return [c.split("#")[1] for c in own_classes(g) if module_of(c.split("#")[1]) is None]


def crm_anchor_cell(g, c) -> str:
    direct = [o for o in g.objects(c, RDFS.subClassOf) if str(o).startswith(FAMILY)]
    if direct:
        return ", ".join(f"<code>{esc(q(g, o))}</code>" for o in sorted(direct, key=str))
    via = anchors(g, c)
    return ", ".join(f"<code>{esc(q(g, o))}</code> (via own class)" for o in via) or "<span class=muted>none</span>"


def model_body(g) -> str:
    classes = own_classes(g)
    props = sorted({p for t in (OWL.ObjectProperty, OWL.DatatypeProperty) for p in g.subjects(RDF.type, t) if str(p).startswith(str(LREC))}, key=str)
    out = [f"<h1>Data model</h1><section><p>Classes, properties, domains and ranges are read from <code>ontology/lrec.ttl</code> at build time: "
           f"{len(classes)} classes and {len(props)} own properties in three modules. Every class is anchored in CIDOC CRM, CRMdig or CRMinf "
           '(see <a href="coverage.html">CRM coverage</a>); the <a href="crosswalk.html">crosswalk</a> shows the parents in the other vocabularies.</p></section>']
    for k, (name, desc, names, figs) in enumerate(MODULES):
        cl = [c for c in classes if c.split("#")[1] in names]
        pr = [p for p in props if (g.value(p, RDFS.domain) or "").split("#")[-1] in names]
        figlinks = " · ".join(f'<a href="visuals.html#{f}">{esc(next(c for s, c, _ in FIGS if s == f))}</a>' for f in figs)
        crows = "".join(f"<tr><td><code>{esc(q(g, c))}</code></td><td>{esc(label(g, c, 'en'))}</td><td>{esc(comment(g, c))}</td><td>{crm_anchor_cell(g, c)}</td></tr>" for c in cl)
        prows = ""
        for p in pr:
            kind = "object" if (p, RDF.type, OWL.ObjectProperty) in g else "data"
            sub = ", ".join(f"<code>{esc(q(g, o))}</code>" for o in g.objects(p, RDFS.subPropertyOf))
            prows += (f"<tr><td><code>{esc(q(g, p))}</code> <span class=muted>({kind})</span></td><td>{esc(q(g, g.value(p, RDFS.domain)))}</td>"
                      f"<td>{esc(q(g, g.value(p, RDFS.range)))}</td><td>{esc(label(g, p, 'en'))}{(' · sub-property of ' + sub) if sub else ''}</td></tr>")
        out.append(f"<section><h2>{esc(name)}</h2><p>{esc(desc)} Figures: {figlinks}.</p><h3>Classes ({len(cl)})</h3>"
                   f"<table><tr><th>Class</th><th>Label</th><th>Comment</th><th>CRM anchor</th></tr>{crows}</table>"
                   + (f"<h3>Properties ({len(pr)})</h3><table><tr><th>Property</th><th>Domain</th><th>Range</th><th>Label</th></tr>{prows}</table>" if pr else "")
                   + "</section>")
    return "".join(out)


def chain_text(g, ch) -> str:
    return " → ".join(f"<code>{esc(q(g, u))}</code>" for u in ch)


def coverage_body(g, missing: list) -> str:
    classes = own_classes(g)
    miss = [c for c in classes if not anchors(g, c)]
    rows = ""
    for c in classes:
        chs = chains(g, c)
        rows += f"<tr><td><code>{esc(q(g, c))}</code></td><td>" + ("<br>".join(chain_text(g, ch) for ch in chs) if chs else '<span class=muted>no CRM-family ancestor</span>') + "</td></tr>"
    if miss:
        raise SystemExit("coverage page: classes without a CRM anchor: " + ", ".join(c.split("#")[1] for c in miss))
    return ("<h1>CRM coverage</h1><section><p>A class counts as anchored when a class of the CIDOC CRM family (crm, crmdig, crminf) is among its ancestors through "
            "<code>rdfs:subClassOf</code>, directly or through another LREC class. The CRM classes themselves are not in this ontology (it imports CIDOC CRM), "
            "so a chain ends at the first class of the family.</p>"
            f"<p><strong>{len(classes)} of {len(classes)}</strong> LREC classes are anchored in the CRM family.</p></section>"
            + fig_by("coverage", "F11", missing)
            + f"<section><h2>Chains to the CRM family ({len(classes)} classes)</h2><table><tr><th>Class</th><th>Chain</th></tr>{rows}</table></section>")


VOCAB = [("crm", "CIDOC CRM"), ("crmdig", "CRMdig"), ("crminf", "CRMinf"), ("hdt", "HDT"), ("prov", "PROV-O"), ("dcat", "DCAT"), ("dqv", "DQV"),
         ("skos", "SKOS"), ("schema", "schema.org"), ("time", "OWL-Time"), ("geo", "GeoSPARQL")]


def crosswalk_body(g, gm, missing: list) -> str:
    ns = {p: str(n) for p, n in g.namespaces()}
    classes = own_classes(g)
    head = "".join(f"<th>{esc(n)}</th>" for _, n in VOCAB)
    rows = ""
    for c in classes:
        cells = ""
        for p, _ in VOCAB:
            ps = [o for o in g.objects(c, RDFS.subClassOf) if str(o).startswith(ns[p])]
            cells += "<td>" + "<br>".join(f"<code>{esc(str(o).replace(ns[p], ''))}</code>" for o in sorted(ps, key=str)) + "</td>"
        rows += f"<tr><td><code>{esc(q(g, c))}</code></td>{cells}</tr>"
    # classes of other vocabularies: superclasses of own classes, and types used in the data
    sup, typ = {}, {}
    for c in classes:
        for o in g.objects(c, RDFS.subClassOf):
            if isinstance(o, URIRef) and not str(o).startswith(str(LREC)):
                sup[o] = sup.get(o, 0) + 1
    for _, t in gm.subject_objects(RDF.type):
        if isinstance(t, URIRef) and not str(t).startswith(str(LREC)) and not str(t).startswith("http://www.w3.org/2002/07/owl#"):
            typ[t] = typ.get(t, 0) + 1
    ext = sorted(set(sup) | set(typ), key=lambda u: (q(gm, u)))
    erows = ""
    for u in ext:
        use = []
        if u in typ:
            use.append(f"in data: {typ[u]} nodes")
        if u in sup:
            use.append(f"superclass of {sup[u]} LREC class" + ("es" if sup[u] > 1 else ""))
        erows += f"<tr><td><code>{esc(q(gm, u))}</code></td><td>{esc('; '.join(use))}</td></tr>"
    return ("<h1>Crosswalk</h1><section><p>Where each LREC class sits in the other vocabularies: the direct parents from <code>rdfs:subClassOf</code>, one column per vocabulary. "
            "An LREC class is at the same time a class of the CRM family, of PROV-O (entity, activity or agent) and, where it applies, of HDT, DCAT, DQV, SKOS, schema.org, OWL-Time or GeoSPARQL. "
            "<code>hdt:</code> is a placeholder namespace until the official HDT namespace is entered.</p>"
            f'<div style="overflow-x:auto"><table><tr><th>LREC class</th>{head}</tr>{rows}</table></div></section>'
            f"<section><h2>Classes of other vocabularies ({len(ext)})</h2><p class=muted>Counted in the merged graph (ontology, four FDOx bundles, Wikidata mapping).</p>"
            f"<table><tr><th>Class</th><th>Use</th></tr>{erows}</table></section>" + fig_by("crosswalk", "F12", missing))


def _pin(gm, z):
    for p in read_pins():
        if p["concept_doi"].endswith(z):
            return p
    return {}


def _person(gm, n) -> str:
    name = label(gm, n, "en") if (n, RDFS.label, None) in gm else ""
    if name:
        return name
    for o in gm.objects(n, URIRef("http://www.w3.org/2002/07/owl#sameAs")):
        for f in gm.subjects(DCT.creator, o):
            a = gm.value(f, SCHEMA.author)
            if a:
                return str(a)
    return q(gm, n)


def instances_body(gm, missing: list) -> str:
    cfg = [
        ("Pyramid 1", EX.lego_pyramid_1, EX.model1_scan_event, EX.model1_scan, [EX.model1_recon_glb], ("24305240", "24305343"), [EX.ident_m1, EX.ident_fig], "pyramid1", "F4"),
        ("Pyramid 2", EX.lego_pyramid_2, EX.model2_scan_event, EX.model2_scan, [EX.model2_v4], ("24305428", "24305436"), [EX.ident_m2], "pyramid2", "F5"),
    ]
    out = ["<h1>Instance models</h1><section><p>The two LEGO pyramids as nodes of the graph: who built them, how they were scanned, which records carry the scan and the reconstruction, "
           "and what they were identified as. All values are read from the merged graph and the registry pins.</p></section>"]
    for name, model, scan_ev, scan, recs, (z_scan, z_rec), idents, fig, fn in cfg:
        place = gm.value(scan_ev, URIRef("http://www.cidoc-crm.org/cidoc-crm/P7_took_place_at"))
        wd = gm.value(place, SK.closeMatch)
        rows = [("Model", esc(label(gm, model, "en"))),
                ("Built by", esc(_person(gm, gm.value(model, LREC.builtBy)))),
                ("Scan", f"{esc(gm.value(scan_ev, LREC.imageCount))} photos, {esc(gm.value(scan_ev, LREC.captureDevice))}; {esc(next((str(x) for x in gm.objects(scan_ev, DCT.description) if getattr(x, 'language', '') == 'en'), ''))}"),
                ("Place", esc(min((str(x) for x in gm.objects(place, RDFS.label) if getattr(x, "language", "") == "en"), default=q(gm, place))) + (f' (<a href="{esc(wd)}">{esc(str(wd).split("/")[-1])}</a>)' if wd else "")),
                ("Reconstruction", esc("; ".join(label(gm, r_, "en") for r_ in recs)))]
        for z, role in ((z_scan, "FDOx: scan"), (z_rec, "FDOx: reconstruction")):
            pin = _pin(gm, z)
            node = URIRef("https://doi.org/10.5281/zenodo." + z)
            rows.append((role, f'{esc(gm.value(node, DCT.title))}: <a href="https://doi.org/10.5281/zenodo.{z}">10.5281/zenodo.{z}</a> '
                               f'(pinned version <a href="https://doi.org/{esc(pin.get("pinned_version_doi", ""))}">{esc(pin.get("zenodo_version", ""))}</a>)'))
        hyp = []
        for idn in idents:
            sub = []
            for h in sorted(gm.objects(idn, CRMINF.J2_concluded_that), key=lambda x: -float(gm.value(x, LREC.confidence))):
                cand = gm.value(h, LREC.proposesReferent)
                w = gm.value(cand, SK.closeMatch) if cand else None
                sub.append(f"{float(gm.value(h, LREC.confidence)):.2f} {esc(label(gm, h, 'en'))}" + (f' (<a href="{esc(w)}">{esc(str(w).split("/")[-1])}</a>)' if w else ""))
            hyp.append((f"<strong>{esc(label(gm, idn, 'en'))}</strong><br>" if len(idents) > 1 else "") + "<br>".join(sub))
        rows.append(("Identification", "<br><br>".join(hyp)))
        tr = "".join(f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in rows)
        out.append(f"<section><h2>{name}</h2><table>{tr}</table></section>" + fig_by(fig, fn, missing))
    return "".join(out)
