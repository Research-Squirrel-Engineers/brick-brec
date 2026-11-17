import sys as _s, pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from fira import tw, chip_w
# Zeichnet die Identifikations-Hypothesen aus ontology/lrec.ttl (kreuzungsfrei: Bus-Linien statt Einzelkanten).
import sys, os, textwrap, rdflib
from rdflib import RDF, RDFS, Namespace, URIRef
ttl = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.ttl') else 'ontology/lrec.ttl'
LANG = [a for a in sys.argv[1:] if a in ('de', 'en')] or ['de']; LANG = LANG[0]; SUF = '' if LANG == 'de' else '_en'
TX = {'de': dict(t='LREC v0.3: Was stellt das Objekt dar? (Beobachtung → Identifikation → Hypothese → Kandidat)', st='Konfidenz = subjektive Einschätzung des KI-Assistenten (0 bis 1), keine Messung; Hypothesen überlappen und summieren sich nicht zu 1', j1='J1 Prämisse', j2='J2 schließt auf', sup='stützt', wk='schwächt', main='Hauptannahme', spec='Spezialfall von', alt='Alternative zu', id='Kennung', status='Status', search='Suche', pr='proposesReferent', l1='Beobachtung (crminf:I4)', l2='Identifikation (E17 + I5)', l3='Hypothese (crminf:I2)', l4='Kandidat / Wikidata', s1='Modell 1: Stufenpyramide mit Säule und Figur', s2='Figur auf Modell 1', s3='Modell 2: Stufenpyramide mit grauen Treppen und Tempel', open='offen'),
 'en': dict(t='LREC v0.3: What does the object represent? (observation → identification → hypothesis → candidate)', st='Confidence = subjective estimate by the AI assistant (0 to 1), not a measurement; hypotheses overlap and do not sum to 1', j1='J1 premise', j2='J2 concluded that', sup='supports', wk='weakens', main='main assumption', spec='special case of', alt='alternative to', id='id', status='Status', search='search', pr='proposesReferent', l1='Observation (crminf:I4)', l2='Identification (E17 + I5)', l3='Hypothesis (crminf:I2)', l4='Candidate / Wikidata', s1='Model 1: stepped pyramid with column and figure', s2='Figure on model 1', s3='Model 2: stepped pyramid with grey stairs and temple', open='open'), }[LANG]
g = rdflib.Graph(); g.parse(ttl, format='turtle')
for _m in [a for a in sys.argv[1:] if a.endswith('.ttl')][1:]: g.parse(_m, format='turtle')   # optional 2nd TTL: data/wikidata_mapping.ttl
L = Namespace('https://example.org/lego-reconstruction#'); EX = Namespace('https://example.org/lego-reconstruction/id/')
CI = Namespace('http://www.ics.forth.gr/isl/CRMinf/'); SK = Namespace('http://www.w3.org/2004/02/skos/core#')
def lab(u): return next((str(l) for l in g.objects(u, RDFS.label) if l.language == LANG), next((str(l) for l in g.objects(u, RDFS.label)), ''))
def val(u, p): return next((str(l) for l in g.objects(u, p) if getattr(l, 'language', None) == LANG), next((str(l) for l in g.objects(u, p)), ''))
def loc(u): return str(u).split('/')[-1]
X0, XE, XI, XH, XC = 40, 40, 560, 1040, 1650
WE, WI, WH, WC = 340, 240, 430, 330
y = 20; o = []; known = {'ident_m1': TX['s1'], 'ident_fig': TX['s2'], 'ident_m2': TX['s3']}
sections = [(loc(i), known.get(loc(i)) or lab(i)) for i in sorted(g.subjects(RDF.type, L.Identification), key=lambda i: (loc(i) not in known, loc(i)))]
def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;')
def chip(cx, cy, t):
    w = chip_w(t)
    return f'<rect x="{cx-w/2:.0f}" y="{cy-11:.0f}" width="{w:.0f}" height="22" rx="11" fill="#fbbf24" stroke="#000" stroke-width="1.2"/><text x="{cx:.0f}" y="{cy+4.5:.0f}" font-size="12" text-anchor="middle">{esc(t)}</text>'
for iid, title in sections:
    I = URIRef(str(EX) + iid)
    evs = sorted(g.objects(I, CI.J1_used_as_premise)); hs = sorted(g.objects(I, CI.J2_concluded_that), key=lambda h: -float(g.value(h, L.confidence)))
    eid = {e: f'E{i+1}' for i, e in enumerate(evs)}
    HH, GH = 116, 14; EH = 56
    top = y + 40; total_h = max(len(hs) * (HH + GH), len(evs) * (EH + 10)) - GH
    o.append(f'<text x="{X0}" y="{y+16}" font-size="19" font-weight="500">{esc(title)}</text>')
    # evidence
    ey0 = top + (total_h - (len(evs) * (EH + 10) - 10)) / 2; ys = []
    for i, e in enumerate(evs):
        yy = ey0 + i * (EH + 10); ys.append(yy + EH / 2)
        o.append(f'<rect x="{XE}" y="{yy:.0f}" width="{WE}" height="{EH}" rx="6" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        o.append(f'<text x="{XE+10}" y="{yy+18:.0f}" font-size="12.5" font-weight="500">{eid[e]}</text>')
        for k, ln in enumerate(textwrap.wrap(lab(e), 46)[:3]): o.append(f'<text x="{XE+36}" y="{yy+18+k*15:.0f}" font-size="12">{esc(ln)}</text>')
    cy = top + total_h / 2; busx = XE + WE + 30
    for yy in ys: o.append(f'<path d="M{XE+WE} {yy:.0f} L{busx} {yy:.0f}" stroke="#111" stroke-width="1.3" fill="none"/>')
    o.append(f'<path d="M{busx} {min(ys):.0f} L{busx} {max(ys):.0f}" stroke="#111" stroke-width="1.3"/>')
    o.append(f'<path d="M{busx} {cy:.0f} L{XI} {cy:.0f}" stroke="#111" stroke-width="1.6" marker-end="url(#a)"/>')
    o.append(chip((busx + XI) / 2, cy, TX["j1"]))
    # identification node
    o.append(f'<rect x="{XI}" y="{cy-40:.0f}" width="{WI}" height="80" rx="7" fill="#9a3412" stroke="#000" stroke-width="1.3"/>')
    o.append(f'<text x="{XI+WI/2}" y="{cy-12:.0f}" font-size="14" font-weight="500" text-anchor="middle" fill="#fff">lrec:Identification</text>')
    o.append(f'<text x="{XI+WI/2}" y="{cy+6:.0f}" font-size="12" text-anchor="middle" fill="#fff">E17 Type Assignment</text><text x="{XI+WI/2}" y="{cy+22:.0f}" font-size="12" text-anchor="middle" fill="#fff">I5 Inference Making</text>')
    bus2 = XI + WI + 170; hy = [top + (total_h - (len(hs) * (HH + GH) - GH)) / 2 + i * (HH + GH) for i in range(len(hs))]
    o.append(f'<path d="M{XI+WI} {cy:.0f} L{bus2} {cy:.0f}" stroke="#111" stroke-width="1.6"/>')
    o.append(chip((XI + WI + bus2) / 2, cy, TX["j2"]))
    centers = [h + HH / 2 for h in hy]
    o.append(f'<path d="M{bus2} {min(centers+[cy]):.0f} L{bus2} {max(centers+[cy]):.0f}" stroke="#111" stroke-width="1.6"/>')
    for hh, c in zip(hs, centers):
        yy = c - HH / 2; conf = float(g.value(hh, L.confidence))
        o.append(f'<path d="M{bus2} {c:.0f} L{XH} {c:.0f}" stroke="#111" stroke-width="1.6" marker-end="url(#a)"/>')
        o.append(f'<rect x="{XH}" y="{yy:.0f}" width="{WH}" height="{HH}" rx="7" fill="#fbbf24" stroke="#000" stroke-width="1.2"/>')
        for k, ln in enumerate(textwrap.wrap(lab(hh), 58)[:2]): o.append(f'<text x="{XH+10}" y="{yy+19+k*16:.0f}" font-size="13.5" font-weight="500">{esc(ln)}</text>')
        by = yy + 46; o.append(f'<rect x="{XH+10}" y="{by:.0f}" width="260" height="11" fill="#fff" stroke="#000"/><rect x="{XH+10}" y="{by:.0f}" width="{260*conf:.0f}" height="11" fill="#9a3412"/>')
        o.append(f'<text x="{XH+278}" y="{by+10:.0f}" font-size="12.5" font-weight="500">{conf:.2f}</text>')
        sup = ' '.join(eid[e] for e in evs if (e, L.supports, hh) in g); wk = ' '.join(eid[e] for e in evs if (e, L.weakens, hh) in g)
        o.append(f'<text x="{XH+10}" y="{yy+78:.0f}" font-size="12">{TX["sup"]}: {sup or "–"}    {TX["wk"]}: {wk or "–"}</text>')
        rel = []
        for p, w in ((L.specializes, TX['spec']), (L.alternativeTo, TX['alt'])):
            for t in g.objects(hh, p): rel.append(f'{w} {loc(t).split("_")[-1]}')
        o.append(f'<text x="{XH+10}" y="{yy+95:.0f}" font-size="11.5" fill="#222">{esc("; ".join(rel)) or TX["main"]} · {TX["id"]} {loc(hh).replace("hyp_", "")}</text>')
        o.append(f'<text x="{XH+10}" y="{yy+110:.0f}" font-size="11" fill="#222">{TX["status"]}: {esc(val(hh, L.verificationStatus))}</text>')
        cand = g.value(hh, L.proposesReferent)
        if cand:
            o.append(f'<path d="M{XH+WH} {c:.0f} L{XC} {c:.0f}" stroke="#111" stroke-width="1.4" marker-end="url(#a)"/>')
            qid = g.value(cand, SK.closeMatch); q = str(qid).split('/')[-1] if qid else TX['open']
            wl = next((str(l) for l in g.objects(qid, RDFS.label)), '') if qid else ""
            o.append(f'<rect x="{XC}" y="{c-32:.0f}" width="{WC}" height="64" rx="6" fill="#4c1d95" stroke="#000" stroke-width="1.2"/>')
            for k, ln in enumerate(textwrap.wrap(lab(cand), 40)[:2]): o.append(f'<text x="{XC+10}" y="{c-12+k*16:.0f}" font-size="13" font-weight="500" fill="#fff">{esc(ln)}</text>')
            o.append(f'<text x="{XC+10}" y="{c+24:.0f}" font-size="12" fill="#fff">Wikidata: {q}  ({esc(wl) if qid else TX["search"] + ": " + esc(str(g.value(cand, L.wikidataSearchTerm)))})</text>')
            o.append(chip((XH + WH + XC) / 2, c, TX["pr"]))
    y = top + total_h + 60
W = XC + WC + 40; H = y + 70
hd = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" font-family="Fira Sans">',
 '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10z" fill="#111"/></marker></defs>',
 f'<rect width="{W}" height="{H:.0f}" fill="#fff"/>']
leg = H - 40; x = 40
for col, st, t in [('#fff', '#000', TX["l1"]), ('#9a3412', '#000', TX["l2"]), ('#fbbf24', '#000', TX["l3"]), ('#4c1d95', '#000', TX["l4"])]:
    o.append(f'<rect x="{x}" y="{leg:.0f}" width="26" height="16" fill="{col}" stroke="{st}"/><text x="{x+34}" y="{leg+13:.0f}" font-size="13">{t}</text>'); x += 70 + tw(t, 13)
open('identifikation' + SUF + '.svg', 'w', encoding='utf-8', newline='\n').write('\n'.join(hd + o + ['</svg>'])); print('ok', W, int(H))
