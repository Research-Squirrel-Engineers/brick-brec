import numpy as np, trimesh, os
rng=np.random.default_rng(5)
S=2/3; P_=8*S; BH=9.6*S; STUD_R=2.4*S; STUD_H=1.7*S; GAP=0.05; CH=0.14
WHITE=(245,245,241); BLACK=(48,50,48)
NLEV=7
QW=[6,5,4,3,2,0,0]                     # white corner quadrant size (studs) per level; level 5 = 2x2
def rk(k): return 9-k                  # arm reach in studs from the centre
def quad(k,sx,sz):
    q=QW[k]; xs=range(2,2+q) if sx>0 else range(-2-q,-2); zs=range(2,2+q) if sz>0 else range(-2-q,-2)
    return {(i,j) for i in xs for j in zs}
def cells_black(k):
    r=rk(k); s=set()
    for i in range(-r,r):
        for j in range(-2,2): s.add((i,j))
    for j in range(-r,r):
        for i in range(-2,2): s.add((i,j))
    return s
def cells_white(k):
    s=set()
    for sx in (-1,1):
        for sz in (-1,1): s|=quad(k,sx,sz)
    return s
# measured yaw (deg) of the upper white blocks in the scan: (level k)->{quadrant:(angle)}
YAW={2:{(-1,-1):2,(1,-1):2,(-1,1):-2,(1,1):-2},
     3:{(-1,-1):5,(1,-1):2,(-1,1):-3.5,(1,1):-3},
     4:{(-1,-1):7,(1,-1):7,(-1,1):-2,(1,1):0}}
# temple: 4 courses on top of the last level
T=[ {(i,j) for i in range(-2,2) for j in range(-2,2)},
    {(-2,-2),(1,-2),(-2,1),(1,1)},
    {(i,j) for i in range(-2,2) for j in range(-2,2)},
    {(i,j) for i in range(-1,1) for j in range(-1,1)} ]
CORE={(i,j) for i in range(-1,1) for j in range(-1,1)}
occ=[cells_white(k)|cells_black(k) for k in range(NLEV)]+[T[0],T[1],T[2],T[3]]

def tile(cells,tries=200):
    cells=set(cells); best=None
    big=[(2,4),(4,2),(2,2)]; small=[(1,4),(4,1),(1,2),(2,1),(1,1)]
    for t in range(tries):
        fx=rng.choice([-1,1]); fz=rng.choice([-1,1]); tr=rng.random()<0.5
        key=lambda c:((c[1],c[0]) if tr else c)
        order=sorted(cells,key=lambda c:(fx*key(c)[0],fz*key(c)[1]))
        free=set(cells); plan=[]
        for c in order:
            if c not in free: continue
            done=False
            for group in (big,small):
                sh=list(group)
                if group is big and rng.random()<0.6: sh=[(2,4),(4,2),(2,2)] if rng.random()<.5 else [(4,2),(2,4),(2,2)]
                elif group is big: rng.shuffle(sh)
                for (a_,b_) in sh:
                    for oi in ([0,-(a_-1)] if a_>1 else [0]):
                        for oj in ([0,-(b_-1)] if b_>1 else [0]):
                            blk=[(c[0]+oi+x,c[1]+oj+y) for x in range(a_) for y in range(b_)]
                            if all(q in free for q in blk):
                                for q in blk: free.discard(q)
                                plan.append((blk,(a_,b_))); done=True; break
                        if done: break
                    if done: break
                if done: break
        sc=-len(plan)-0.3*sum(len(p[0])==1 for p in plan)
        if best is None or sc>best[0]: best=(sc,plan)
    return best[1]

def cbox(c,size,ch=CH):
    sx,sy,sz=size; pts=[]
    for ax in range(3):
        s=np.array([sx,sy,sz],float); s[ax]-=2*ch
        for sg in np.array(np.meshgrid([-1,1],[-1,1],[-1,1])).T.reshape(-1,3): pts.append(sg*s/2)
    m=trimesh.convex.convex_hull(np.array(pts)); m.apply_translation(c); return m
def stud(cx,cy,cz):
    m=trimesh.creation.cylinder(radius=STUD_R,height=STUD_H,sections=32)
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0])); m.apply_translation([cx,cy+STUD_H/2,cz]); return m
out={'w':[],'b':[]}; stats={'w':[0,0,0,0],'b':[0,0,0,0]}
def add(cells,k,col,yaw=0.0):
    pv=np.array([np.mean([(c[0]+.5)*P_ for c in cells]),np.mean([(c[1]+.5)*P_ for c in cells])])
    R=trimesh.transformations.rotation_matrix(np.radians(-yaw),[0,1,0],point=[pv[0],0,pv[1]])
    for blk,(a,b) in tile(cells):
        xs=[(c[0]+.5)*P_ for c in blk]; zs=[(c[1]+.5)*P_ for c in blk]
        cx=(min(xs)+max(xs))/2; cz=(min(zs)+max(zs))/2
        size=(a*P_-2*GAP,BH-GAP,b*P_-2*GAP)
        ms=[cbox([cx,k*BH+BH/2,cz],size)]
        stats[col][{8:0,4:1,1:2}.get(len(blk),3)]+=1
        for c in blk:
            if (c not in occ[k+1]) if k+1<len(occ) else True:
                ms.append(stud((c[0]+.5)*P_,k*BH+BH,(c[1]+.5)*P_))
        for m in ms:
            if yaw: m.apply_transform(R)
            out[col].append(m)
for k in range(NLEV):
    for sx in (-1,1):
        for sz in (-1,1):
            qc=quad(k,sx,sz)
            if qc: add(qc,k,'w',YAW.get(k,{}).get((sx,sz),0))
    add(cells_black(k),k,'b')
add(T[0],NLEV,'b'); PYAW={(1,1):14,(-2,1):-12,(1,-2):16,(-2,-2):-9}
for c_ in T[1]: add({c_},NLEV+1,'w',PYAW[c_])
add(T[2],NLEV+2,'b'); add(T[3],NLEV+3,'b')
print('2x4,2x2,1x1,other  white',stats['w'],' black',stats['b'])
sc=trimesh.Scene()
for col,rgb in (('w',WHITE),('b',BLACK)):
    m=trimesh.util.concatenate(out[col]); m.apply_scale(0.001); m.unmerge_vertices()
    mat=trimesh.visual.material.PBRMaterial(baseColorFactor=list(rgb)+[255],roughnessFactor=0.3,metallicFactor=0.0)
    m=trimesh.Trimesh(m.vertices,m.faces,process=False,vertex_normals=m.vertex_normals); m.visual=trimesh.visual.TextureVisuals(material=mat)
    sc.add_geometry(m,geom_name='bricks_white' if col=='w' else 'bricks_black')
os.makedirs('out6',exist_ok=True); sc.export('out6/lego3.glb'); print('ok',sc.bounds)
