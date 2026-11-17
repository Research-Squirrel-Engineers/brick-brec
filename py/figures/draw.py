import itertools, json
C=[None,230,520,810,1100,1390,1720,560]; R=[80,250,420,590,760,920,340]
W,H=210,84
SZ={'QM':(210,50),'PL':(190,84)}
def ww(n): return SZ.get(n,(W,H))[0]
def hh(n): return SZ.get(n,(W,H))[1]
GRN=('#166534','#fff'); ORG=('#9a3412','#fff'); PUR=('#4c1d95','#fff'); AMB=('#fbbf24','#000')
N={ # id:(col,row,fill,hdt,lines)
'TA':(1,0,GRN,1,['HC16 Tangible Asset','E22 Human-Made Object','LEGO-Modell (physisch)']),
'TW':(4,0,ORG,1,['HC3 Heritage Digital Twin','D1 Digital Object','Digitaler Zwilling']),
'HDOC':(6,0,ORG,1,['HC4 Heritage Document','E31 Document','Änderungsdoku md + json']),
'IMG':(2,1,ORG,1,['HC6 Imagery','D1 Digital Object','Fotos (Referenz)']),
'RAW':(3,1,ORG,1,['HC7 3D Model','D1 · prov:Entity','SfM-Rohscan OBJ + JPG']),
'OUT':(5,1,ORG,1,['HC7 3D Model','D1 · prov:Entity','dcat:Distribution (DCAT-AP)','Rekonstruktion (GLB)']),
'BT':(6,1,PUR,0,['E55 Type · skos:Concept','skos:inScheme','closeMatch wd: (Wikidata)','Steintyp, Farbe']),
'DIG':(1,2,ORG,1,['D2 Digitization Process','HC5 · prov:Activity','KIRI-Scan (SfM)']),
'REC':(4,2,ORG,0,['D7 Digital Machine Event','prov:Activity','Prozedurale Rekonstruktion','P4 Zeit: time:ProperInterval']),
'QM':(6,6,ORG,0,['dqv:QualityMeasurement','z. B. Stufenzahl = 7']),
'PL':(7,2,ORG,0,['E53 Place · geo:Feature','Aufnahmeort','geo:hasGeometry (offen)']),
'DEV':(1,3,ORG,0,['D8 Digital Device','Smartphone']),
'MEAS':(2,3,ORG,0,['E16 Measurement','Ausrichtung, Raster,','Steinhöhe']),
'INF':(3,3,ORG,0,['I5 Inference Making','Strukturableitung']),
'AGT':(5,3,ORG,0,['E39 Actor · prov:Agent','Flo (Person) und','Claude Sonnet 5.5 (KI)','closeMatch wd: (Wikidata)']),
'SW2':(6,3,ORG,0,['D14 Software','schema:SoftwareSourceCode','Python + trimesh (CodeMeta)']),
'SW1':(1,4,ORG,0,['D14 Software','KIRI Engine']),
'DIM':(2,4,AMB,0,['E54 Dimension','Wert + Genauigkeit']),
'BEL':(4,4,AMB,0,['I2 Belief','Annahme, z. B. 7 Stufen']),
'UNIT':(2,5,PUR,0,['E58 Measurement Unit','qudt:Unit']),
}
def box(n): c,r=N[n][:2]; return (C[c],R[r])
def anc(n,side,dx=0,dy=0):
    x,y=box(n)
    return {'t':(x+dx,y-hh(n)/2),'b':(x+dx,y+hh(n)/2),'l':(x-ww(n)/2,y+dy),'r':(x+ww(n)/2,y+dy)}[side]
E=[ # (label, pts, label_xy)
('hdt: has digital twin',[anc('TA','r'),anc('TW','l')],(665,66)),
('hdt: includes visual documentation',[anc('TW','b',-70),anc('IMG','t',0)],(700,142)),
('hdt: includes 3D documentation',[anc('TW','b',-25),anc('RAW','t',0)],(940,170)),
('hdt: includes 3D documentation',[anc('TW','b',40),anc('OUT','t',0)],(1300,150)),
('hdt: includes document',[anc('TW','r'),anc('HDOC','l')],(1400,66)),
('L1 digitized',[anc('DIG','t'),anc('TA','b')],(285,250)),
('L11 had output',[anc('DIG','r',0,-30),anc('RAW','b',-40)],(540,338)),
('L10 had input',[anc('REC','t',-60),anc('RAW','b',70)],(985,342)),
('L11 had output',[anc('REC','t',60),anc('OUT','b',-50)],(1255,336)),
('L21 used as derivation source',[anc('OUT','l'),anc('RAW','r')],(1100,238)),
('P2 has type',[anc('OUT','r'),anc('BT','l')],(1555,238)),
('P70 documents',[anc('HDOC','r'),(1890,80),(1890,390),anc('REC','r',0,-30)],(1560,392)),
('P39 measured',[anc('MEAS','t',80),anc('RAW','b',20)],(695,505)),
('P40 observed dimension',[anc('MEAS','b'),anc('DIM','t')],(440,678)),
('P91 has unit',[anc('DIM','b'),anc('UNIT','t')],(570,848)),
('J1 used as premise',[anc('INF','b',-40),anc('DIM','t',50)],(668,674)),
('J2 concluded that',[anc('INF','b',40),anc('BEL','t',-40)],(972,674)),
('lrec: usesAssumption',[anc('REC','b'),anc('BEL','t')],(1180,602)),
('L12 happened on device',[anc('DIG','b'),anc('DEV','t')],(310,505)),
('L23 used software',[anc('DIG','l'),(60,420),(60,760),anc('SW1','l')],(60,592)),
('P14 carried out by',[anc('REC','b',30),(1130,535),(1350,535),anc('AGT','t',-40)],(1240,535)),
('P7 took place at',[anc('DIG','r',0,20),anc('PL','l',0,20)],(400,432)),
('dqv: hasQualityMeasurement',[anc('OUT','b',70),(1460,340),anc('QM','l')],(1520,357)),
('L23 used software',[anc('REC','b',60),(1160,518),(1680,518),anc('SW2','t',-40)],(1590,518)),
]
def seg_int(p,q,r,s):
    def o(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    d1,d2,d3,d4=o(p,q,r),o(p,q,s),o(r,s,p),o(r,s,q)
    return d1*d2<0 and d3*d4<0
segs=[]
for i,(l,pts,_) in enumerate(E):
    for a,b in zip(pts,pts[1:]): segs.append((i,a,b))
bad=[]
for (i,a,b),(j,c,d) in itertools.combinations(segs,2):
    if i!=j and seg_int(a,b,c,d): bad.append((E[i][0],E[j][0]))
# edges through foreign boxes
def inbox(pt,n,m=3):
    x,y=box(n); return abs(pt[0]-x)<ww(n)/2-m and abs(pt[1]-y)<hh(n)/2-m
for i,a,b in segs:
    for k in range(1,40):
        t=k/40; pt=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
        for n in N:
            if inbox(pt,n): bad.append(('box',E[i][0],n)); break
print('crossings/overlaps:',sorted(set(map(str,bad))))
# svg
w=1990; h=1100
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Arial,Helvetica,sans-serif">',
'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#111"/></marker></defs>',
f'<rect width="{w}" height="{h}" fill="#fff"/>']
for l,pts,lp in E:
    d='M'+' L'.join(f'{x:.0f} {y:.0f}' for x,y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="#111" stroke-width="1.6" marker-end="url(#a)"/>')
for l,pts,lp in E:
    tw=len(l)*6.6+10
    rot=' transform="rotate(-90 %d %d)"'%lp if l=='L23 used software' and lp==(60,592) else ''
    o.append(f'<g{rot}><rect x="{lp[0]-tw/2:.0f}" y="{lp[1]-11}" width="{tw:.0f}" height="17" fill="#fff" opacity="0.92"/><text x="{lp[0]}" y="{lp[1]+2}" font-size="12" text-anchor="middle" fill="#111">{l}</text></g>')
for n,(c,r,(fill,fg),hdt,lines) in N.items():
    x,y=box(n); st='#1d4ed8' if hdt else '#000'; sw=4 if hdt else 1.2
    o.append(f'<rect x="{x-ww(n)/2}" y="{y-hh(n)/2}" width="{ww(n)}" height="{hh(n)}" rx="6" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
    n0=len(lines); y0=y-(n0-1)*9
    for k,t in enumerate(lines):
        o.append(f'<text x="{x}" y="{y0+k*18+4:.0f}" font-size="{14 if k==0 else 12.5}" font-weight="{700 if k==0 else 400}" text-anchor="middle" fill="{fg}">{t}</text>')
ly=1010
items=[('#166534','physisches Objekt'),('#9a3412','Klasse (CRM / CRMdig / CRMinf / HDT)'),('#fbbf24','Wert / Annahme'),('#4c1d95','Typ / Einheit')]
x=60
for col,t in items:
    o.append(f'<rect x="{x}" y="{ly}" width="26" height="16" fill="{col}" stroke="#000"/><text x="{x+34}" y="{ly+13}" font-size="13">{t}</text>'); x+=60+len(t)*7
o.append(f'<rect x="{x}" y="{ly}" width="26" height="16" fill="#fff" stroke="#1d4ed8" stroke-width="4"/><text x="{x+34}" y="{ly+13}" font-size="13">Heritage-Digital-Twin-Klasse (hdt)</text>')
o.append(f'<text x="60" y="{ly+44}" font-size="12" fill="#444">In Klasse notiert (ohne eigenen Knoten): DCAT-AP, CodeMeta, SKOS, Wikidata (closeMatch), OWL-Time (P4). Zusätzlich je Klasse: prov:Entity / prov:Activity / prov:Agent (Unterklassenbeziehung, nicht als Pfeil gezeichnet).</text>')
o.append('</svg>'); open('ontologie_planar.svg','w').write('\n'.join(o))
