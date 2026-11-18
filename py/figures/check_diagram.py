# Prueft, dass jeder Knoten und jede Kante der Gesamtzeichnung (draw.py) in der Turtle-Datei steht.
import sys, rdflib
from rdflib import RDF, RDFS, URIRef
ttls = sys.argv[1:] or ['ontology/lrec.ttl']   # ontology first, then optional FDOx bundle TTLs
g = rdflib.Graph()
OLD_DIG = 'http://www.ics.forth.gr/isl/CRMdig/'   # the published FDOx bundles still use the CRMdig 3.2.1 namespace
for ttl in ttls: g.parse(data=open(ttl, encoding='utf-8').read().replace(OLD_DIG, 'http://www.cidoc-crm.org/extensions/crmdig/'), format='turtle')
def U(s):
    p, l = s.split(':', 1)
    return URIRef({'ex': 'https://example.org/lego-reconstruction/id/', 'crm': 'http://www.cidoc-crm.org/cidoc-crm/',
                   'crmdig': 'http://www.cidoc-crm.org/extensions/crmdig/', 'crminf': 'http://www.ics.forth.gr/isl/CRMinf/',
                   'hdt': 'https://example.org/placeholder/hdt#', 'prov': 'http://www.w3.org/ns/prov#',
                   'lrec': 'https://example.org/lego-reconstruction#', 'dqv': 'http://www.w3.org/ns/dqv#',
                   'unit': 'http://qudt.org/vocab/unit/', 'skos': 'http://www.w3.org/2004/02/skos/core#',
                   'geo': 'http://www.opengis.net/ont/geosparql#', 'dcat': 'http://www.w3.org/ns/dcat#', 'dct': 'http://purl.org/dc/terms/',
                   'zenodo': 'https://doi.org/10.5281/zenodo.'}[p] + l)
def sup(c, seen=None):
    seen = seen or set()
    for o in g.objects(c, RDFS.subClassOf):
        if o not in seen: seen.add(o); sup(o, seen)
    return seen
def classes(i):
    out = set()
    for t in g.objects(i, RDF.type): out |= {t} | sup(t)
    return out
NODES = {  # Knoten: (Instanz, erwartete Klassenteile)
 'TA': ('ex:lego_pyramid_2', ['E22', 'HC_Tangible']), 'TW': ('ex:lego_pyramid_2_twin', ['HC_Heritage_Digital_Twin', 'D1']),
 'HDOC': ('ex:model2_changes', ['HC_Heritage_Document', 'E31']), 'IMG': ('ex:model2_photos', ['HC_Imagery', 'D1']),
 'RAW': ('ex:model2_scan', ['HC_3D_Model', 'D1', 'Entity']), 'OUT': ('ex:model2_v4', ['HC_3D_Model', 'D1', 'Distribution']),
 'BT': ('ex:brick_2x4', ['E55', 'Concept']), 'DIG': ('ex:model2_scan_event', ['D2', 'HC_Heritage_Documenting', 'Activity']),
 'REC': ('ex:model2_recon', ['D7', 'Activity']), 'DEV': ('ex:smartphone', ['D8']),
 'MEAS': ('ex:model2_measure', ['E16']), 'INF': ('ex:infer', ['I5']), 'AGT1': ('ex:flo', ['E21']), 'AGT2': ('ex:claude_sonnet_5_5', ['E39', 'SoftwareAgent']),
 'SW2': ('ex:build_m3', ['D14', 'SoftwareSourceCode']), 'SW1': ('ex:kiri_engine', ['D14']), 'DIM': ('ex:model2_yaw', ['E54']),
 'BEL': ('ex:assume_7_levels', ['I2']), 'UNIT': ('unit:DEG', ['E58']), 'QM': ('ex:quality_levels', ['QualityMeasurement']),
 'PL': ('ex:scan_place', ['E53', 'Feature']),
 'FR': ('zenodo:24305436', ['FDOx', 'ReconstructionDataset', 'Dataset']), 'FS': ('zenodo:24305428', ['FDOx', 'Dataset']),
}
EDGES = [  # (Subjekt, Praedikat, Objekt) wie in der Zeichnung
 ('TA','hdt:has_digital_twin','TW'), ('TW','hdt:includes_visual_documentation','IMG'), ('TW','hdt:includes_3D_documentation','RAW'),
 ('TW','hdt:includes_3D_documentation','OUT'), ('TW','hdt:includes_document','HDOC'), ('DIG','crmdig:L1_digitized','TA'),
 ('DIG','crmdig:L11_had_output','RAW'), ('REC','crmdig:L10_had_input','RAW'), ('REC','crmdig:L11_had_output','OUT'),
 ('OUT','crmdig:L21_used_as_derivation_source','RAW'), ('OUT','crm:P2_has_type','BT'), ('HDOC','crm:P70_documents','REC'),
 ('MEAS','crm:P39_measured','RAW'), ('MEAS','crm:P40_observed_dimension','DIM'), ('DIM','crm:P91_has_unit','UNIT'),
 ('INF','crminf:J1_used_as_premise','DIM'), ('INF','crminf:J2_concluded_that','BEL'), ('REC','lrec:usesAssumption','BEL'),
 ('DIG','crmdig:L12_happened_on_device','DEV'), ('DIG','crmdig:L23_used_software_or_firmware','SW1'),
 ('REC','crm:P14_carried_out_by','AGT1'), ('REC','crm:P14_carried_out_by','AGT2'), ('REC','crmdig:L23_used_software_or_firmware','SW2'),
 ('FS','dct:isReferencedBy','FR'), ('FR','prov:wasDerivedFrom','FS'), ('FR','prov:wasAttributedTo','AGT2'),
 ('DIG','crm:P7_took_place_at','PL'), ('OUT','dqv:hasQualityMeasurement','QM'), ('REC','crm:P4_has_time-span','TIME'),
]
inst = {k: v[0] for k, v in NODES.items()}; inst['TIME'] = 'ex:model2_time'
bad = 0
for k, (i, parts) in NODES.items():
    cl = ' '.join(map(str, classes(U(i))))
    miss = [p for p in parts if p not in cl]
    if (U(i), None, None) not in g: print('FEHLT Instanz', k, i); bad += 1
    elif miss: print('FEHLT Klasse', k, i, miss); bad += 1
for s_, p, o in EDGES:
    if (U(inst[s_]), U(p), U(inst[o])) not in g: print('FEHLT Kante', s_, p, o); bad += 1
print('Knoten', len(NODES), 'Kanten', len(EDGES), 'Fehler', bad)
