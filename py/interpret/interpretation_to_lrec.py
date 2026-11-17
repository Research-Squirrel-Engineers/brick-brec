#!/usr/bin/env python
"""interpretation_to_lrec.py <x_interpretation.json> [--merge ontology/lrec.ttl --out merged.ttl]
Validates the JSON answer of the 'incognito' chat against interpretation_schema.json (+ reference checks) and writes it as LREC Turtle
(Identification, Evidence, IdentityHypothesis, CandidateReferent, object/parts/dimensions). With --merge the fragment is appended to your ontology."""
import argparse, json, os, re, sys
import rdflib
from rdflib import RDF, RDFS, OWL, XSD, Literal, Namespace, URIRef
HERE = os.path.dirname(os.path.abspath(__file__))
NS = dict(lrec='https://example.org/lego-reconstruction#', ex='https://example.org/lego-reconstruction/id/', crm='http://www.cidoc-crm.org/cidoc-crm/', crmdig='http://www.ics.forth.gr/isl/CRMdig/',
          crminf='http://www.ics.forth.gr/isl/CRMinf/', prov='http://www.w3.org/ns/prov#', dct='http://purl.org/dc/terms/', skos='http://www.w3.org/2004/02/skos/core#')
def check(d):
    errs = []
    try:
        import jsonschema
        v = jsonschema.Draft202012Validator(json.load(open(os.path.join(HERE, 'interpretation_schema.json'))))
        errs += [f"schema: {'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(d)]
    except ImportError: print('note: pip install jsonschema for full schema validation (only reference checks run)')
    E = {e['id'] for e in d.get('evidence', [])}; H = {h['id']: h for h in d.get('hypotheses', [])}
    for h in H.values():
        for e in h['supports'] + h['weakens'] + [c['evidence'][i] for c in h.get('feature_checks', []) for i in range(len(c['evidence']))]:
            if e not in E: errs.append(f"{h['id']}: unknown evidence {e}")
        for o in h['alternative_to'] + ([h['specializes']] if h['specializes'] else []):
            if o not in H: errs.append(f"{h['id']}: unknown hypothesis {o}")
        if h['specializes'] in H and h['confidence'] > H[h['specializes']]['confidence'] + 1e-9: errs.append(f"{h['id']}: special case has higher confidence than its general hypothesis")
        if not 0 <= h['confidence'] <= 1: errs.append(f"{h['id']}: confidence outside 0..1")
    P = {p['id'] for p in d.get('structure', {}).get('components', [])}
    for h in H.values():
        if h.get('about') and h['about'] not in P: errs.append(f"{h['id']}: unknown component {h['about']}")
    return errs
def build(d):
    g = rdflib.Graph()
    for k, v in NS.items(): g.bind(k, v)
    L, EX, CRM, CI, PROV, DCT = (Namespace(NS[k]) for k in ('lrec', 'ex', 'crm', 'crminf', 'prov', 'dct'))
    slug = re.sub(r'[^A-Za-z0-9]+', '_', d['model_id']).strip('_'); R = lambda s: EX[f'{slug}_{s}']
    en = lambda t: Literal(t, lang='en')
    # property declarations for the fragment
    for p, rng, dom in ((L.evidenceStrength, XSD.string, L.Evidence), (L.interpretationJson, RDF.JSON, L.Identification), (L.strongestCounterargument, XSD.string, L.IdentityHypothesis)):
        g.add((p, RDF.type, OWL.DatatypeProperty)); g.add((p, RDFS.range, rng)); g.add((p, RDFS.domain, dom))
    model, obj, views, facts = R('model'), R('object'), R('views'), R('facts')
    g.add((model, RDF.type, URIRef(NS['crmdig'] + 'D1_Digital_Object'))); g.add((model, RDFS.label, en(f"3D model {d['model_id']}")))
    g.add((views, RDF.type, URIRef(NS['crmdig'] + 'D1_Digital_Object'))); g.add((views, RDFS.label, en('Standard views (contact sheet)'))); g.add((views, PROV.wasDerivedFrom, model))
    g.add((facts, RDF.type, URIRef(NS['crmdig'] + 'D1_Digital_Object'))); g.add((facts, RDFS.label, en('Measured facts (JSON)'))); g.add((facts, PROV.wasDerivedFrom, model))
    o = d['object']; g.add((obj, RDF.type, CRM.E18_Physical_Thing)); g.add((obj, RDFS.label, en(f"Object shown by {d['model_id']}"))); g.add((obj, DCT.description, en(o['short_description'])))
    g.add((obj, DCT.type, Literal(o['category']))); g.add((obj, DCT['format'], Literal(o['construction_technique'])))
    if o.get('construction_material'): g.add((obj, DCT.medium, en(o['construction_material'])))
    s = o['estimated_real_size']
    if s['value'] is not None:
        sz = R('size'); g.add((sz, RDF.type, CRM.E54_Dimension)); g.add((sz, RDFS.label, en('Estimated real size (largest extent)'))); g.add((sz, CRM.P90_has_value, Literal(s['value'])))
        g.add((sz, DCT.description, en(f"unit {s['unit']}; {s.get('basis') or ''}"))); g.add((sz, L.confidence, Literal(round(s['confidence'], 2), datatype=XSD.decimal))); g.add((obj, CRM.P43_has_dimension, sz))
    st = d['structure']
    if st['levels'] is not None:
        lv = R('levels'); g.add((lv, RDF.type, CRM.E54_Dimension)); g.add((lv, RDFS.label, en('Number of levels'))); g.add((lv, CRM.P90_has_value, Literal(st['levels']))); g.add((obj, CRM.P43_has_dimension, lv))
    g.add((obj, RDFS.comment, en(f"Overall shape: {st['overall_shape']}. Mirror axes: {', '.join(st['symmetry']['mirror_axes']) or 'none'}; rotational fold: {st['symmetry']['rotational_fold']}.")))
    for p in st['components']:
        pr = R(p['id']); g.add((pr, RDF.type, CRM.E18_Physical_Thing)); g.add((pr, RDFS.label, en(p['name']))); g.add((pr, DCT.description, en(p['description'])))
        if p.get('count') is not None: g.add((pr, RDFS.comment, en(f"count: {p['count']}")))
        g.add((obj, CRM.P46_is_composed_of, pr))
    ai = R('interpreter'); iv = d['interpreter']; g.add((ai, RDF.type, L.AIAssistant)); g.add((ai, RDFS.label, en(iv['name']))); g.add((ai, DCT.identifier, Literal(iv['model_id_self_reported'])))
    g.add((ai, RDFS.comment, en(f"Self-reported model identifier; may differ from the serving model. Context: {iv['context']}")))
    ident = R('ident'); g.add((ident, RDF.type, L.Identification)); g.add((ident, RDFS.label, en(f"Identification of {d['model_id']}"))); g.add((ident, CRM.P41_classified, obj))
    g.add((ident, PROV.wasAssociatedWith, ai)); g.add((ident, L.interpretationJson, Literal(json.dumps(d, ensure_ascii=False), datatype=RDF.JSON)))
    for e in d['evidence']:
        ev = R(e['id']); g.add((ev, RDF.type, L.Evidence)); g.add((ev, RDFS.label, en(e['statement']))); g.add((ev, L.evidenceStrength, Literal(e['strength'])))
        src = {'facts': facts, 'views': views}.get(e['source'])
        if src is None:
            src = R(e['source']); g.add((src, RDF.type, URIRef(NS['crmdig'] + 'D1_Digital_Object'))); g.add((src, RDFS.label, en({'photo': 'Reference photos supplied by the owner', 'owner_note': 'Owner-supplied context note'}.get(e['source'], 'Other source'))))
        g.add((ev, PROV.wasDerivedFrom, src)); g.add((ident, CI.J1_used_as_premise, ev))
    for h in d['hypotheses']:
        hy = R(h['id']); g.add((hy, RDF.type, L.IdentityHypothesis)); g.add((hy, RDFS.label, en(h['label']))); g.add((hy, L.hypothesisAbout, R(h['about']) if h.get('about') else obj)); g.add((hy, L.strongestCounterargument, en(h['strongest_counterargument'])))
        for fc in h.get('feature_checks', []): g.add((hy, RDFS.comment, en(f"feature check: {fc['feature']} -> {fc['observed']} ({', '.join(fc['evidence'])})")))
        g.add((hy, L.confidence, Literal(round(h['confidence'], 2), datatype=XSD.decimal))); g.add((hy, L.confidenceBasis, en('subjective estimate by the AI assistant from views and facts, not a measurement')))
        g.add((hy, L.verificationStatus, en('open: confirmation by the owner needed'))); g.add((hy, PROV.wasAttributedTo, ai)); g.add((hy, PROV.wasGeneratedBy, ident)); g.add((ident, CI.J2_concluded_that, hy))
        for e in h['supports']: g.add((R(e), L.supports, hy))
        for e in h['weakens']: g.add((R(e), L.weakens, hy))
        for a in h['alternative_to']: g.add((hy, L.alternativeTo, R(a)))
        if h['specializes']: g.add((hy, L.specializes, R(h['specializes'])))
        c = h['candidate']
        if c['kind'] != 'none' and c['label']:
            cr = R('C' + h['id'][1:]); g.add((cr, RDF.type, L.CandidateReferent)); g.add((cr, RDFS.label, en(c['label']))); g.add((cr, RDFS.comment, en(f"candidate kind: {c['kind']}")))
            if c['wikidata_search_term']: g.add((cr, L.wikidataSearchTerm, Literal(c['wikidata_search_term'])))
            g.add((hy, L.proposesReferent, cr))
    return g
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('--merge'); ap.add_argument('--out'); A = ap.parse_args()
    d = json.load(open(A.json, encoding='utf-8')); errs = check(d)
    if errs: print('VALIDATION ERRORS:'); [print(' -', e) for e in errs]; sys.exit(1)
    g = build(d); frag = g.serialize(format='turtle')
    if A.merge:
        out = A.out or 'merged.ttl'; base = open(A.merge, encoding='utf-8').read(); open(out, 'w', encoding='utf-8').write(base.rstrip('\n') + f"\n\n# ---- interpretation of {d['model_id']} ----\n" + frag)
        rdflib.Graph().parse(out, format='turtle')
    else:
        out = A.out or A.json.replace('.json', '.ttl'); open(out, 'w', encoding='utf-8').write(frag)
    print(f'ok: {len(g)} triples -> {out}')
if __name__ == '__main__': main()
