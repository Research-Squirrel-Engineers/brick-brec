import sys as _s, pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from fira import tw, chip_w
import rdflib, itertools, sys
LANG=sys.argv[1] if len(sys.argv)>1 else 'de'; SUF='' if LANG=='de' else '_'+LANG
TX={'de':dict(title='LREC v0.4: Klassendiagramm',sub='Pfeile mit hohlem Dreieck = rdfs:subClassOf (Elternklassen stehen pro Klasse einzeln, damit sich nichts kreuzt)',lrec='LREC-Klasse',crm='CRM / CRMdig / CRMinf / Time / GeoSPARQL',hdt='Heritage Digital Twin (hdt)',prov='PROV-O',par='LREC-Oberklasse',dcat='DCAT / DQV / SKOS / schema.org',foot='Gelb = Attribut (Datatype-Property); Pfeil mit Vollspitze = Object-Property. Quelle: ontology/lrec.ttl',inh='(erbt confidence)'),
'en':dict(title='LREC v0.4: class diagram',sub='Hollow-triangle arrows = rdfs:subClassOf (parent classes are listed per class so that no lines cross)',lrec='LREC class',crm='CRM / CRMdig / CRMinf / Time / GeoSPARQL',hdt='Heritage Digital Twin (hdt)',prov='PROV-O',par='LREC parent class',dcat='DCAT / DQV / SKOS / schema.org',foot='Yellow = attribute (datatype property); solid arrowhead = object property. Source: ontology/lrec.ttl',inh='(inherits confidence)')}[LANG]
from rdflib import RDF,RDFS,OWL,Namespace
g=rdflib.Graph(); g.parse(sys.argv[2] if len(sys.argv)>2 else 'ontology/lrec.ttl',format='turtle')
L=Namespace('https://example.org/lego-reconstruction#')
order=['LegoModel','LegoModelTwin','ScanDigitization','RawScan','ReferencePhoto','AlignmentAndMeasurement','StructureInference','Assumption','ProceduralReconstruction','ReconstructionModel','QualityMeasurement','ReconstructionScript','ProcessInterval','ScanLocation','ReconstructionDataset','FDOx','Identification','IdentityHypothesis','Evidence','CandidateReferent','ChangeDocumentation','BrickType','AIAssistant']
def short(u):
    s=g.namespace_manager.normalizeUri(u).strip('<>')
    return s
def pretty(s):
    p,l=s.split(':',1); l=l.replace('_',' ')
    import re; l=re.sub(r'^(E|D|I|HC|P)(\d+)? ',lambda m:(m.group(0)),l)
    return p+':'+l
def vocab(s): return s.split(':')[0]
cls={}
for n in order:
    u=L[n]; par=[short(o) for o in g.objects(u,RDFS.subClassOf)]
    cls[n]=dict(label=next((str(l) for l in g.objects(u,RDFS.label) if getattr(l,'language',None)==LANG),''),par=par)
attrs={'Assumption':['+ confidence : xsd:decimal','+ confidenceBasis : xsd:string'],'IdentityHypothesis':['+ verificationStatus : xsd:string',TX['inh']],'CandidateReferent':['+ wikidataSearchTerm : xsd:string'],'ReconstructionModel':['+ knownDeviation : xsd:string']}
# right = hdt/prov/dcat/skos ; left = crm family
def side(s): return 'L' if vocab(s) in ('crm','crmdig','crminf','time','geo') else 'R'
SW={'lrec':'#d6a58a','time':'#fff','geo':'#fff','dqv':'#4c1d95','schema':'#4c1d95','crm':'#fff','crmdig':'#fff','crminf':'#fff','hdt':'#fff','prov':'#e2e8f0','dcat':'#4c1d95','skos':'#4c1d95','mbo':'#166534'}
CW,BW,GAP=280,340,95; XL=50; XB=XL+CW+GAP; XR=XB+BW+GAP; W=XR+CW+50
CH,SP=30,8
y=40; rows={}
for n in order:
    p=cls[n]['par']; left=[x for x in p if side(x)=='L']; right=[x for x in p if side(x)=='R']
    left.sort(); right.sort(key=lambda s:('0' if vocab(s)=='hdt' else '1' if vocab(s)=='prov' else '2')+s)
    stack=lambda k:k*CH+(k-1)*SP if k else 0
    bh=max(70+18*len(attrs.get(n,[])),stack(len(left))+12,stack(len(right))+12)
    rows[n]=dict(y=y,h=bh,left=left,right=right); y+=bh+(76 if n=='Assumption' else 34)
H=y+60
def chip(x,yc,t,v):
    fill=SW[v]; fg='#fff' if v in('dcat','skos','mbo') else '#000'; st='#1d4ed8' if v=='hdt' else '#000'; sw=3.5 if v=='hdt' else 1.2
    return f'<rect x="{x}" y="{yc-CH/2}" width="{CW}" height="{CH}" rx="5" fill="{fill}" stroke="{st}" stroke-width="{sw}"/><text x="{x+CW/2}" y="{yc+5}" font-size="12.5" text-anchor="middle" fill="{fg}">{t}</text>'
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Fira Sans">',
'<defs><marker id="s" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="11" markerHeight="11" orient="auto"><path d="M1 1L11 6L1 11z" fill="#fff" stroke="#111" stroke-width="1.3"/></marker><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10z" fill="#111"/></marker></defs>',
f'<rect width="{W}" height="{H}" fill="#fff"/>']
segs=[]
for n,r in rows.items():
    top=r['y']; h=r['h']; cy=top+h/2
    # parents
    def place(lst,x_chip,x_edge_box,x_edge_chip,sg):
        k=len(lst); tot=k*CH+(k-1)*SP; y0=cy-tot/2+CH/2
        for i,t in enumerate(lst):
            yc=y0+i*(CH+SP); o.append(f'<path d="M{x_edge_box} {yc:.0f} L{x_edge_chip} {yc:.0f}" stroke="#111" stroke-width="1.5" fill="none" marker-end="url(#s)"/>')
            o.append(chip(x_chip,yc,pretty(t),vocab(t))); segs.append((x_edge_box,yc,x_edge_chip,yc))
    place(r['left'],XL,XB,XL+CW,'L'); place(r['right'],XR,XB+BW,XR,'R')
    o.append(f'<rect x="{XB}" y="{top}" width="{BW}" height="{h}" rx="7" fill="#9a3412" stroke="#000" stroke-width="1.3"/>')
    o.append(f'<text x="{XB+BW/2}" y="{top+h/2-(9*len(attrs.get(n,[])))-4:.0f}" font-size="15" font-weight="500" text-anchor="middle" fill="#fff">lrec:{n}</text>')
    o.append(f'<text x="{XB+BW/2}" y="{top+h/2-(9*len(attrs.get(n,[])))+15:.0f}" font-size="12.5" text-anchor="middle" fill="#fff">{cls[n]["label"]}</text>')
    for i,a in enumerate(attrs.get(n,[])):
        o.append(f'<text x="{XB+BW/2}" y="{top+h/2+(9*len(attrs.get(n,[])))+8+i*18:.0f}" font-size="12.5" text-anchor="middle" fill="#fbbf24" font-weight="500">{a}</text>')
# property edge: ProceduralReconstruction -> Assumption (adjacent rows)
a=rows['Assumption']; b=rows['ProceduralReconstruction']; xm=XB+BW/2
y1=b['y']; y2=a['y']+a['h']
o.append(f'<path d="M{xm} {y1} L{xm} {y2}" stroke="#111" stroke-width="2" fill="none" marker-end="url(#a)"/>')
UA='lrec:usesAssumption (sub-property of prov:used)'; UW=chip_w(UA,12.5)
o.append(f'<rect x="{xm-UW/2}" y="{(y1+y2)/2-11}" width="{UW}" height="22" rx="11" fill="#fbbf24" stroke="#000" stroke-width="1.2"/><text x="{xm}" y="{(y1+y2)/2+4}" font-size="12.5" text-anchor="middle">{UA}</text>')
ly=H-56; x=50
items=[('#9a3412','#000',TX["lrec"]),('#fff','#000',TX["crm"]),('#fff','#1d4ed8',TX["hdt"]),('#e2e8f0','#000',TX["prov"]),('#d6a58a','#000',TX["par"]),('#4c1d95','#000',TX["dcat"]),('#166534','#000','Minimal Brick Ontology (mbo)'),('#fbbf24','#000','attribute (datatype property)')]
for f,s,t in items:
    sw=3.5 if s=='#1d4ed8' else 1.2
    o.append(f'<rect x="{x}" y="{ly}" width="26" height="16" fill="{f}" stroke="{s}" stroke-width="{sw}"/><text x="{x+34}" y="{ly+13}" font-size="13">{t}</text>'); x+=58+tw(t,13)
    if f=='#fff' and s=='#1d4ed8': x=50; ly+=26
o.append('</svg>')
open('lrec_klassen'+SUF+'.svg','w',encoding='utf-8',newline='\n').write('\n'.join(o))
print('rows',len(rows),'size',W,H)
