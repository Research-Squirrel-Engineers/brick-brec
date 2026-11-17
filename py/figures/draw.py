import sys as _s, pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from fira import tw, chip_w
import itertools, json
C=[None,230,520,810,1100,1390,1720,580,1830]; R=[80,250,420,590,760,920,340]
W,H=210,84
SZ={'QM':(210,50),'PL':(170,84)}
def ww(n): return SZ.get(n,(W,H))[0]
def hh(n): return SZ.get(n,(W,H))[1]
GRN=('#166534','#fff'); ORG=('#9a3412','#fff'); PUR=('#4c1d95','#fff'); AMB=('#fbbf24','#000')
N={ # id:(col,row,fill,hdt,lines)
'TA':(1,0,GRN,1,['HC16 Tangible Asset','E22 Human-Made Object','LEGO model (physical)']),
'TW':(4,0,ORG,1,['HC3 Heritage Digital Twin','D1 Digital Object','Digital twin']),
'HDOC':(6,0,ORG,1,['HC4 Heritage Document','E31 Document','Change docs md + json']),
'IMG':(2,1,ORG,1,['HC6 Imagery','D1 Digital Object','Photos (reference)']),
'RAW':(3,1,ORG,1,['HC7 3D Model','D1 · prov:Entity','SfM raw scan OBJ + JPG']),
'OUT':(5,1,ORG,1,['HC7 3D Model','D1 · prov:Entity','dcat:Distribution (DCAT-AP)','Reconstruction (GLB)']),
'BT':(6,1,PUR,0,['E55 Type · skos:Concept','skos:inScheme','closeMatch wd: (Wikidata)','Brick type, colour']),
'DIG':(1,2,ORG,1,['D2 Digitization Process','HC5 · prov:Activity','KIRI scan (SfM)']),
'REC':(4,2,ORG,0,['D7 Digital Machine Event','prov:Activity','Procedural reconstruction','P4 time: time:ProperInterval']),
'QM':(6,6,ORG,0,['dqv:QualityMeasurement','e.g. number of levels = 7']),
'PL':(7,2,ORG,0,['E53 Place · geo:Feature','Capture location','geo:hasGeometry (open)']),
'DEV':(1,3,ORG,0,['D8 Digital Device','Smartphone']),
'MEAS':(2,3,ORG,0,['E16 Measurement','Alignment, grid,','brick height']),
'INF':(3,3,ORG,0,['I5 Inference Making','Structure inference']),
'AGT':(5,3,ORG,0,['E39 Actor · prov:Agent','Flo (person) and','Claude Sonnet 5.5 (AI)','closeMatch wd: (Wikidata)']),
'SW2':(6,3,ORG,0,['D14 Software','schema:SoftwareSourceCode','Python + trimesh (CodeMeta)']),
'SW1':(1,4,ORG,0,['D14 Software','KIRI Engine']),
'DIM':(2,4,AMB,0,['E54 Dimension','Value + accuracy']),
'BEL':(4,4,AMB,0,['I2 Belief','Assumption, e.g. 7 levels']),
'FR':(5,5,ORG,0,['lrec:FDOx · dcat:Dataset','FDOx reconstruction (Zenodo)','Concept DOI ...24305436']),
'FS':(8,5,ORG,0,['lrec:FDOx · dcat:Dataset','FDOx scan (Zenodo)','Concept DOI ...24305428']),
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
('P7 took place at',[anc('DIG','r',0,20),anc('PL','l',0,20)],(392,432)),
('dqv: hasQualityMeasurement',[anc('OUT','b',70),(1460,340),anc('QM','l')],(1500,357)),
('dct: isReferencedBy',[anc('FS','l',0,-16),anc('FR','r',0,-16)],(1610,891)),
('prov: wasDerivedFrom',[anc('FR','r',0,18),anc('FS','l',0,18)],(1610,953)),
('prov: wasAttributedTo',[anc('FR','t'),anc('AGT','b')],(1485,760)),
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
def rects_overlap(a,b,m=2): return a[0]<b[0]+b[2]+m and b[0]<a[0]+a[2]+m and a[1]<b[1]+b[3]+m and b[1]<a[1]+a[3]+m
def inrect(pt,r,m=0): return r[0]-m<=pt[0]<=r[0]+r[2]+m and r[1]-m<=pt[1]<=r[1]+r[3]+m
ROT=('L23 used software',(60,592))          # the one vertical label on the left margin is set by hand (rotated)
def chip_wh(l): return chip_w(l),22
def samples(a,b,step=3):
    n=max(2,int(((b[0]-a[0])**2+(b[1]-a[1])**2)**.5/step))
    return [(a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n) for k in range(n+1)]
BOXES=[(box(n)[0]-ww(n)/2,box(n)[1]-hh(n)/2,ww(n),hh(n)) for n in N]
PLACED={}   # edge index -> (label, centre x, centre y, rect); short edges first, they have the least room
def longest(pts): return max(((b_[0]-a_[0])**2+(b_[1]-a_[1])**2)**.5 for a_,b_ in zip(pts,pts[1:]))
CHIPS=[]
for i,(l,pts,lp) in sorted(enumerate(E),key=lambda e_:longest(e_[1][1])):
    if (l,lp)==ROT:
        c_=(l,lp[0],lp[1],(lp[0]-11,lp[1]-chip_w(l)/2,22,chip_w(l))); CHIPS.append(c_); PLACED[i]=c_; continue
    w,h=chip_wh(l); chosen=None
    for a_,b_ in sorted(zip(pts,pts[1:]),key=lambda s_:-((s_[1][0]-s_[0][0])**2+(s_[1][1]-s_[0][1])**2)):
        for t in (.5,.46,.54,.42,.58,.38,.62,.34,.66,.3,.7,.26,.74,.22,.78):       # the middle of the arrow first, then close to the middle
            cx,cy=a_[0]+(b_[0]-a_[0])*t,a_[1]+(b_[1]-a_[1])*t; r=(cx-w/2,cy-h/2,w,h)
            if inrect(pts[0],r,10) or inrect(pts[-1],r,12): continue                     # keep tail and arrowhead visible
            if any(rects_overlap(r,bx) for bx in BOXES) or any(rects_overlap(r,c[3]) for c in CHIPS): continue
            if any(inrect(q,r,1) for j,(l2,p2,_) in enumerate(E) if j!=i for u,v in zip(p2,p2[1:]) for q in samples(u,v)): continue   # do not hide another line
            chosen=(cx,cy,r); break
        if chosen: break
    if not chosen:                                   # fallback: the hand-set position beside the arrow
        cx,cy=lp[0],lp[1]-2; chosen=(cx,cy,(cx-w/2,cy-h/2,w,h)); bad.append(('label-not-on-arrow',l))
    c_=(l,)+chosen; CHIPS.append(c_); PLACED[i]=c_
CHIPS=[PLACED[i] for i in range(len(E))]
for l,cx,cy,r in CHIPS:
    for bx in BOXES:
        if rects_overlap(r,bx): bad.append(('label-on-box',l))
for (l1,_,_,r1),(l2,_,_,r2) in itertools.combinations(CHIPS,2):
    if rects_overlap(r1,r2): bad.append(('label-on-label',l1,l2))
print('crossings/overlaps:',sorted(set(map(str,bad))))
# svg
w=1990; h=1050
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Fira Sans">',
'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#111"/></marker></defs>',
f'<rect width="{w}" height="{h}" fill="#fff"/>']
for l,pts,lp in E:
    d='M'+' L'.join(f'{x:.0f} {y:.0f}' for x,y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="#111" stroke-width="1.6" marker-end="url(#a)"/>')
for l,cx,cy,r in CHIPS:
    rot=' transform="rotate(-90 %d %d)"'%(cx,cy) if (l,(cx,cy))==ROT else ''
    tw_=chip_w(l)
    o.append(f'<g{rot}><rect x="{cx-tw_/2:.0f}" y="{cy-11:.0f}" width="{tw_:.0f}" height="22" rx="11" fill="#fbbf24" stroke="#000" stroke-width="1.2"/><text x="{cx:.0f}" y="{cy+4.5:.0f}" font-size="12" text-anchor="middle" fill="#000">{l}</text></g>')
for n,(c,r,(fill,fg),hdt,lines) in N.items():
    x,y=box(n); st='#1d4ed8' if hdt else '#000'; sw=4 if hdt else 1.2
    o.append(f'<rect x="{x-ww(n)/2}" y="{y-hh(n)/2}" width="{ww(n)}" height="{hh(n)}" rx="6" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
    n0=len(lines); y0=y-(n0-1)*9
    for k,t in enumerate(lines):
        if tw(t,14 if k==0 else 12.5,k==0)>ww(n)-10: bad.append(('text-too-wide',n,t))
        o.append(f'<text x="{x}" y="{y0+k*18+4:.0f}" font-size="{14 if k==0 else 12.5}" font-weight="{500 if k==0 else 400}" text-anchor="middle" fill="{fg}">{t}</text>')
ly=1010
items=[('#166534','physical object'),('#9a3412','class (CRM / CRMdig / CRMinf / HDT)'),('#fbbf24','value / assumption'),('#4c1d95','type / unit')]
x=60
for col,t in items:
    o.append(f'<rect x="{x}" y="{ly}" width="26" height="16" fill="{col}" stroke="#000"/><text x="{x+34}" y="{ly+13}" font-size="13">{t}</text>'); x+=60+tw(t,13)
o.append(f'<rect x="{x}" y="{ly}" width="26" height="16" fill="#fff" stroke="#1d4ed8" stroke-width="4"/><text x="{x+34}" y="{ly+13}" font-size="13">Heritage Digital Twin class (hdt)</text>')
o.append('</svg>'); open('ontologie_planar.svg','w',encoding='utf-8',newline='\n').write('\n'.join(o))
