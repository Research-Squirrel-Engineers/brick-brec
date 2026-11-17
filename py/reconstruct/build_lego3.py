import numpy as np, trimesh, os
from PIL import Image, ImageDraw, ImageFilter
rng=np.random.default_rng(11)
S=2/3; P_=8*S; BH=9.6*S; STUD_R=2.4*S; STUD_H=1.7*S; GAP=0.05; CH=0.14
LEVELS=[(14-2*k,18-2*k) for k in range(7)]+[(2,4),(2,2)]
NCOL=5; COL=(-P_/2,-P_/2)
WHITE=(237,237,233)
bricks=[]
def cbox(c,size,ch=CH):
    sx,sy,sz=size; pts=[]
    for ax in range(3):
        s=np.array([sx,sy,sz],float); s[ax]-=2*ch
        for sg in np.array(np.meshgrid([-1,1],[-1,1],[-1,1])).T.reshape(-1,3): pts.append(sg*s/2)
    m=trimesh.convex.convex_hull(np.array(pts)); m.apply_translation(c); return m
def stud(cx,cy,cz):
    m=trimesh.creation.cylinder(radius=STUD_R,height=STUD_H,sections=32)
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0])); m.apply_translation([cx,cy+STUD_H/2,cz]); return m
def covered(k,cx,cz):
    if k+1<len(LEVELS):
        w,l=LEVELS[k+1]; return abs(cx)<w*P_/2-1e-6 and abs(cz)<l*P_/2-1e-6
    return abs(cx-COL[0])<1e-6 and abs(cz-COL[1])<1e-6
nb24=nb22=nb11=0
for k,(w,l) in enumerate(LEVELS):
    y0=k*BH; yc=y0+BH/2
    bw,bl=w//2,l//2               # blocks of 2x2 studs
    bx=lambda i:(i-bw/2+0.5)*2*P_; bz=lambda j:(j-bl/2+0.5)*2*P_
    best=None
    for trial in range(400):
        used=np.zeros((bw,bl),bool); plan=[]
        order=[(i,j) for j in range(bl) for i in range(bw)]; 
        if trial>0: rng.shuffle(order)
        for i,j in order:
            if used[i,j]: continue
            opts=[]
            if i+1<bw and not used[i+1,j]: opts.append('x')
            if j+1<bl and not used[i,j+1]: opts.append('z')
            if i>0 and not used[i-1,j]: opts.append('-x')
            if j>0 and not used[i,j-1]: opts.append('-z')
            o=opts[rng.integers(len(opts))] if opts else None
            if o=='x': cells=[(i,j),(i+1,j)]
            elif o=='-x': cells=[(i-1,j),(i,j)]
            elif o=='z': cells=[(i,j),(i,j+1)]
            elif o=='-z': cells=[(i,j-1),(i,j)]
            else: cells=[(i,j)]
            for c in cells: used[c]=True
            plan.append(cells)
        sc_=sum(len(c)==2 for c in plan)
        if best is None or sc_>best[0]: best=(sc_,plan)
    for cells in best[1]:
        if len(cells)==2:
            (a,b),(c,d)=cells
            cx=(bx(a)+bx(c))/2; cz=(bz(b)+bz(d))/2
            size=(4*P_-2*GAP,BH-GAP,2*P_-2*GAP) if a!=c else (2*P_-2*GAP,BH-GAP,4*P_-2*GAP); nb24+=1
        else:
            (a,b),=cells; cx,cz=bx(a),bz(b); size=(2*P_-2*GAP,BH-GAP,2*P_-2*GAP); nb22+=1
        bricks.append(cbox([cx,yc,cz],size))
        for (ci,cj) in cells:
            for dx in (-.5,.5):
                for dz in (-.5,.5):
                    sx=bx(ci)+dx*P_; sz=bz(cj)+dz*P_
                    if not covered(k,sx,sz): bricks.append(stud(sx,y0+BH,sz))
top=len(LEVELS)*BH
for n in range(NCOL):
    bricks.append(cbox([COL[0],top+n*BH+BH/2,COL[1]],(P_-2*GAP,BH-GAP,P_-2*GAP))); nb11+=1
col_top=top+NCOL*BH; bricks.append(stud(COL[0],col_top,COL[1]))
print('bricks 2x4:',nb24,'2x2:',nb22,'1x1:',nb11)
bm=trimesh.util.concatenate(bricks); bm.apply_scale(0.001); bm.unmerge_vertices()
bmat=trimesh.visual.material.PBRMaterial(baseColorFactor=list(WHITE)+[255],roughnessFactor=0.3,metallicFactor=0.0)
bm=trimesh.Trimesh(bm.vertices,bm.faces,process=False,vertex_normals=bm.vertex_normals); bm.visual=trimesh.visual.TextureVisuals(material=bmat)

# ============================ minifigure =================================================
Y0=col_top+STUD_H
def sup_pt(th,a,b,n):
    c,s=np.cos(th),np.sin(th); e=2.0/n
    return -a*np.sign(c)*abs(c)**e, b*np.sign(s)*abs(s)**e
def loft(rings,n=56,sup=2.0,cap_top=True,cap_bot=True,uv=True,uvr=None):
    """rings: (y,a,b[,cx,cz]) ; front = -x, left = +z. u=0.5 is the front."""
    th=np.pi+np.linspace(0,2*np.pi,n+1); V=[];UV=[];F=[]
    y0,y1=rings[0][0],rings[-1][0]
    for r in rings:
        y,a,b=r[:3]; cx=r[3] if len(r)>3 else 0; cz=r[4] if len(r)>4 else 0
        for t in th:
            x,z=sup_pt(t,a,b,sup); V.append([x+cx,y,z+cz]); UV.append([((t/(2*np.pi))+0.5)%1.0 if t<2*np.pi else 1.0, (y-y0)/max(y1-y0,1e-9)])
    # fix wrap: u for last column
    V=np.array(V);UV=np.array(UV); m=len(th)
    UV.reshape(len(rings),m,2)[:,-1,0]=1.0; UV.reshape(len(rings),m,2)[:,0,0]=0.0
    # explicit u from angle so that front=0.5, seam at back
    for ri in range(len(rings)):
        P=V[ri*m:(ri+1)*m]; seg=np.linalg.norm(np.diff(P,axis=0),axis=1); cum=np.concatenate([[0],np.cumsum(seg)]); tot=cum[-1]
        front=cum[n//2]
        for ki in range(m):
            UV[ri*m+ki,0]=0.5+(cum[ki]-front)/tot
    for ri in range(len(rings)-1):
        for ki in range(n):
            a_=ri*m+ki;b_=a_+1;c_=a_+m;d_=c_+1; F+= [(a_,c_,b_),(b_,c_,d_)]
    V=list(V);UV=list(UV)
    for cap,ri,flip in ((cap_bot,0,True),(cap_top,len(rings)-1,False)):
        if not cap: continue
        base=len(V); r=rings[ri]; cx=r[3] if len(r)>3 else 0; cz=r[4] if len(r)>4 else 0
        V.append([cx,r[0],cz]); UV.append([0.0,0.0 if flip else 1.0])
        for ki in range(m): V.append(list(np.array(V[ri*m+ki])+[0,0,0])); UV.append([0.0,0.0 if flip else 1.0])
        for ki in range(n):
            f=(base,base+1+ki,base+2+ki); F.append(f[::-1] if not flip else f)
    mesh=trimesh.Trimesh(np.array(V),np.array(F),process=False)
    # orient outward
    c=mesh.triangles_center; nrm=mesh.face_normals; cen=np.array([np.mean([r[3] if len(r)>3 else 0 for r in rings]),(y0+y1)/2,np.mean([r[4] if len(r)>4 else 0 for r in rings])])
    if ((c-cen)*nrm).sum()<0: mesh.faces=mesh.faces[:,::-1]
    return mesh,np.array(UV)
def frame(mesh,p0,d,roll=0):
    d=np.asarray(d,float); d/=np.linalg.norm(d); R=trimesh.geometry.align_vectors([0,1,0],d)
    T=np.eye(4); T[:3,:3]=R[:3,:3]; T[:3,3]=p0; mesh.apply_transform(T); return mesh
def setvis(mesh,uv,mat):
    out=trimesh.Trimesh(mesh.vertices,mesh.faces,process=False,vertex_normals=mesh.vertex_normals)
    out.visual=trimesh.visual.TextureVisuals(uv=uv,material=mat) if uv is not None else trimesh.visual.TextureVisuals(material=mat)
    return out
def pbr(c,r=0.5,m=0.0,tex=None,ds=False):
    return trimesh.visual.material.PBRMaterial(baseColorFactor=list(c)+[255],roughnessFactor=r,metallicFactor=m,baseColorTexture=tex,doubleSided=ds)

# ---------------- colours (from the photos) ----------------------------------------------
FACE=(198,164,126); HAND=(226,186,146); LEGB=(30,92,178); SHOE=(116,78,46); SOLE=(146,108,68)
SLEEVE=(184,198,224); TUNIC=(216,216,215); CAPEC=(204,168,134); SILVER=(186,191,199); MAILC=(150,156,168)
FS=S    # figure is a 1:1 minifigure, scaled like the bricks
def unit(v): v=np.asarray(v,float); return v/np.linalg.norm(v)
# ---------------- textures ------------------------------------------------------------------
def head_tex():
    W,H=1024,384; im=Image.new('RGB',(W,H),FACE); d=ImageDraw.Draw(im)
    pxmm=W/28.9; ymm=lambda m: H*(1-(m)/10.9)   # m = mm above chin
    fx=W//2
    # soft cheek shading
    sh=Image.new('RGB',(W,H),FACE); sd=ImageDraw.Draw(sh)
    sd.ellipse([fx-190,ymm(6)-40,fx+190,ymm(0.2)+30],fill=(212,182,146)); im=Image.blend(im,sh.filter(ImageFilter.GaussianBlur(25)),0.7); d=ImageDraw.Draw(im)
    for sgn in (-1,1):
        ex=fx+sgn*95; ey=ymm(7.0)
        d.ellipse([ex-34,ey-17,ex+34,ey+17],fill=(238,232,222))                  # sclera
        d.ellipse([ex-13+sgn*3,ey-15,ex+13+sgn*3,ey+15],fill=(86,56,36)); d.ellipse([ex-6+sgn*3,ey-7,ex+6+sgn*3,ey+7],fill=(20,14,12))
        d.arc([ex-36,ey-20,ex+36,ey+20],195,345,fill=(120,90,70),width=3)      # lid
        d.polygon([(ex-sgn*40,ymm(8.1)),(ex,ymm(8.7)),(ex+sgn*42,ymm(8.2)),(ex+sgn*42,ymm(7.8)),(ex,ymm(8.3)),(ex-sgn*40,ymm(7.7))],fill=(72,46,32))   # brow
    d.polygon([(fx-8,ymm(6.0)),(fx+8,ymm(6.0)),(fx+22,ymm(3.9)),(fx-22,ymm(3.9))],fill=(190,158,122))                       # nose shade
    d.polygon([(fx-105,ymm(2.6)),(fx-70,ymm(3.9)),(fx-12,ymm(3.8)),(fx,ymm(3.5)),(fx+12,ymm(3.8)),(fx+70,ymm(3.9)),(fx+105,ymm(2.6)),(fx+88,ymm(1.5)),(fx+28,ymm(2.3)),(fx,ymm(2.1)),(fx-28,ymm(2.3)),(fx-88,ymm(1.5))],fill=(108,66,42))   # moustache
    d.line([(fx-26,ymm(1.05)),(fx+26,ymm(1.05))],fill=(150,100,85),width=4)                                                  # mouth
    return im.filter(ImageFilter.GaussianBlur(1.0))
def torso_per():
    th=np.linspace(0,2*np.pi,200); pts=np.array([sup_pt(t,3.7,6.9,3.0) for t in th]); return np.linalg.norm(np.diff(pts,axis=0),axis=1).sum()
def torso_tex(Y0t=7.4,Y1t=28.6):
    per=torso_per(); W=1024; pxmm=W/per; H=int(W*(Y1t-Y0t)/per)
    im=Image.new('RGB',(W,H),TUNIC); d=ImageDraw.Draw(im); fx=W//2
    row=lambda y: (1-(y-Y0t)/(Y1t-Y0t))*H; hw=5.45*pxmm
    # mail panel (chest to hem of print)
    top,bot=row(27.2),row(10.8)
    d.rectangle([fx-hw,top,fx+hw,bot],fill=(236,238,242))
    cw,ch=19,15
    for r_,y in enumerate(np.arange(top,bot,ch*0.8)):
        for x in np.arange(fx-hw-(cw/2 if r_%2 else 0),fx+hw+cw,cw):
            d.ellipse([x-cw/2,y-ch/2,x+cw/2,y+ch/2],outline=(70,72,82),width=2)
    d.rectangle([fx-hw-30,top-5,fx-hw-1,bot+5],fill=TUNIC); d.rectangle([fx+hw+1,top-5,fx+hw+30,bot+5],fill=TUNIC)
    # scarf (grey-beige, bunched) + brooch
    sc=(168,160,142)
    d.polygon([(fx-hw,row(27.2)),(fx+hw,row(27.2)),(fx+hw,row(24.2)),(fx+hw*0.4,row(23.2)),(fx-hw*0.2,row(24.6)),(fx-hw,row(23.0))],fill=sc)
    for k in range(7): d.line([(fx-hw+k*hw*0.3,row(27.0)),(fx-hw*0.9+k*hw*0.3+10,row(24.0))],fill=(135,128,112),width=3)
    d.ellipse([fx-hw*0.72,row(25.0),fx-hw*0.72+14,row(25.0)+14],fill=(176,196,52)); d.ellipse([fx-hw*0.42,row(22.6),fx-hw*0.42+14,row(22.6)+14],fill=(176,196,52))
    d.line([(fx-hw*0.72+7,row(25.0)+10),(fx-hw*0.42+7,row(22.6))],fill=(176,196,52),width=3)
    # belt (all round, not on the back) + hanging strap ends
    bl,bh=row(17.1),row(14.8)
    for x0,x1 in ((0.10*W,0.90*W),): d.rectangle([x0,bl,x1,bh],fill=(28,26,28))
    d.polygon([(fx-hw*0.2,bh),(fx+hw*0.2,bh),(fx+hw*0.62,row(11.2)),(fx+hw*0.38,row(10.4)),(fx+hw*0.05,bh+20)],fill=(28,26,28))
    d.polygon([(fx+hw*0.25,bh),(fx+hw*0.55,bh),(fx+hw*0.95,row(12.0)),(fx+hw*0.7,row(11.0))],fill=(40,38,40))
    return im.filter(ImageFilter.GaussianBlur(0.6))
htex=head_tex(); ttex=torso_tex()
parts=[]; names=[]
def P(name,mesh,uv,mat): parts.append(setvis(mesh,uv,mat)); names.append(name)
# ---------------- legs + shoes -----------------------------------------------------------
for sgn,nm in ((-1,'r'),(1,'l')):
    zc=sgn*2.95
    leg,_=loft([(3.8,2.75,2.6,0,zc),(8.8,2.9,2.7,0,zc)],n=40,sup=3.0); P('leg_'+nm,leg,None,pbr(LEGB,0.4))
    shoe,_=loft([(0,3.6,2.5,-1.0,zc),(0.35,4.5,2.95,-1.0,zc),(2.0,4.5,2.95,-0.8,zc),(3.5,3.5,2.75,-0.2,zc),(4.1,2.7,2.65,0.2,zc)],n=48,sup=2.6); P('shoe_'+nm,shoe,None,pbr(SHOE,0.45))
    sole,_=loft([(0,3.65,2.55,-1.0,zc),(0.9,4.55,3.0,-1.0,zc)],n=48,sup=2.6); P('sole_'+nm,sole,None,pbr(SOLE,0.5))
# ---------------- torso (long tunic) -----------------------------------------------------
tm,tuv=loft([(7.4,4.0,6.6),(8.0,3.95,6.6),(20,3.7,6.9),(27.2,3.5,7.1),(28.2,3.1,5.6),(28.6,2.2,2.6)],n=72,sup=3.0)
P('torso',tm,tuv,pbr((255,255,255),0.55,0.0,ttex))
# ---------------- head -------------------------------------------------------------------
hm,huv=loft([(27.8,2.9,2.9),(28.3,4.3,4.3),(30.0,4.6,4.6),(36.4,4.6,4.6),(38.8,4.0,4.0)],n=72,sup=2.0)
P('head',hm,huv,pbr((255,255,255),0.45,0.0,htex))
# ---------------- helmet -----------------------------------------------------------------
BR=36.2
prof=[(-0.5,6.9),(0,6.9),(0.45,6.45),(0.8,6.0),(1.1,6.3),(1.45,6.0),(1.8,5.75),(2.6,5.6),(3.8,5.35),(5.0,4.9),(6.2,4.2),(7.2,3.4),(8.0,2.5),(8.6,1.6),(9.0,1.0),(9.5,0.75),(10.2,0.9),(10.8,1.15),(11.4,0.95),(11.9,0.5),(12.3,0.04)]
hl,_=loft([(BR+h,r,r) for h,r in prof],n=72,sup=2.0,cap_bot=False); P('helmet',hl,None,pbr(SILVER,0.28,0.85))
# cheek guards (mail flaps), curved shell with wavy lower edge
def guard(th_c):
    nth,ny=12,10; V=[];F=[]
    for j in range(ny+1):
        t=j/ny
        for i in range(nth+1):
            th=np.radians(th_c+(i/nth-0.5)*34); R=4.95+0.55*t*0.5
            hem=BR-0.4-5.6-0.9*np.sin((i/nth)*np.pi*2+0.6)
            y=(BR-0.4)+(hem-(BR-0.4))*t
            V.append([-R*np.cos(th),y,R*np.sin(th)])
    for j in range(ny):
        for i in range(nth):
            a=j*(nth+1)+i; F+=[(a,a+1,a+nth+1),(a+1,a+nth+2,a+nth+1)]
    m=trimesh.Trimesh(np.array(V),np.array(F),process=False)
    if (m.face_normals*(m.triangles_center-np.array([0,m.centroid[1],0]))).sum()<0: m.faces=m.faces[:,::-1]
    return m
for sgn,nm in ((1,'l'),(-1,'r')): P('guard_'+nm,guard(sgn*100),None,pbr(MAILC,0.4,0.6,None,True))
# ---------------- arms + C-shaped hands --------------------------------------------------
def claw(c,d,R=1.9,r=0.82,gap=50):
    d=unit(d); n=np.cross(d,[0,1,0]); n=unit(n) if np.linalg.norm(n)>0.3 else np.array([0,0,1.0]); u1=d; u2=np.cross(n,u1)
    angs=np.radians(np.linspace(gap,360-gap,26)); ph=np.linspace(0,2*np.pi,14,endpoint=False); V=[];F=[]
    for t in angs:
        e=np.cos(t)*u1+np.sin(t)*u2; Pc=c+R*e
        for p in ph: V.append(Pc+r*(np.cos(p)*e+np.sin(p)*n))
    k=len(ph)
    for i in range(len(angs)-1):
        for j in range(k):
            a=i*k+j;b=i*k+(j+1)%k;c_=a+k;d_=b+k; F+=[(a,c_,b),(b,c_,d_)]
    m=trimesh.Trimesh(np.array(V),np.array(F),process=False)
    for end in (0,len(angs)-1):
        ctr=np.mean(V[end*k:(end+1)*k],axis=0); ci=len(m.vertices)
        m=trimesh.Trimesh(np.vstack([m.vertices,ctr]),np.vstack([m.faces]+[[ (end*k+j,end*k+(j+1)%k,ci) for j in range(k)]]),process=False)
    if (m.face_normals*(m.triangles_center-m.centroid)).sum()<0: m.faces=m.faces[:,::-1]
    return m
def arm(sh,d,nm,L=9.4):
    d=unit(d); sl,_=loft([(0,2.0,2.0),(0.5,2.15,2.15),(L*0.5,2.0,2.0),(L,1.78,1.78)],n=36,sup=2.0); frame(sl,sh,d); P('sleeve_'+nm,sl,None,pbr(SLEEVE,0.35))
    sp=trimesh.creation.icosphere(subdivisions=2,radius=2.1); sp.apply_translation(sh); P('shoulder_'+nm,sp,None,pbr(SLEEVE,0.35))
    end=np.asarray(sh)+d*L; wr,_=loft([(0,1.35,1.35),(1.0,1.3,1.3)],n=24,sup=2.0); frame(wr,end,d); P('wrist_'+nm,wr,None,pbr(HAND,0.4))
    cl=claw(end+d*(1.0+1.55),d); P('hand_'+nm,cl,None,pbr(HAND,0.4))
arm([0,26.0,7.3],[-0.66,-0.74,0.12],'l'); arm([0,26.0,-7.3],[-0.16,-1,-0.08],'r')
# ---------------- cape (soft plastic, pleated) + collar ---------------------------------------
ys_=[7.4,8.0,20,27.2,28.2,28.6]; as_=[4.0,3.95,3.7,3.5,3.1,2.2]; bs_=[6.6,6.6,6.9,7.1,5.6,2.6]
nphi,nt=64,24; TOP=28.3; V=[];F=[]
for j in range(nt+1):
    t=j/nt
    for i in range(nphi+1):
        ph=np.radians(-135+270*i/nphi); a_ph=abs(np.degrees(ph))/135
        hem=12.6-4.2*a_ph**1.6
        y=TOP-t*(TOP-hem); a0=np.interp(y,ys_,as_); b0=np.interp(y,ys_,bs_)
        off=0.55+1.2*t*(1-0.5*a_ph); pl=1+0.075*np.sin(ph*11)*min(1,t*3)
        th=np.pi+ph; x,z=sup_pt(th,(a0+off)*pl,(b0+off)*pl,3.0)
        V.append([x,y,z])
for j in range(nt):
    for i in range(nphi):
        a=j*(nphi+1)+i; F+=[(a,a+1,a+nphi+1),(a+1,a+nphi+2,a+nphi+1)]
cp=trimesh.Trimesh(np.array(V),np.array(F),process=False)
if (cp.face_normals*(cp.triangles_center-np.array([0,18,0]))).sum()<0: cp.faces=cp.faces[:,::-1]
P('cape',cp,None,pbr(CAPEC,0.8,0.0,None,True))
col,_=loft([(26.9,3.95,7.65),(27.8,3.55,7.0),(28.5,3.0,5.5),(28.9,2.6,3.0)],n=64,sup=3.0,cap_bot=False,cap_top=False); P('collar',col,None,pbr(CAPEC,0.8,0.0,None,True))
# ---------------- place + export -----------------------------------------------------------
shift=np.array([COL[0],Y0,COL[1]])
scene=trimesh.Scene(); scene.add_geometry(bm,node_name='bricks',geom_name='bricks')
for nme,p in zip(names,parts):
    p.apply_scale(FS); p.apply_translation(shift); p.apply_scale(0.001); scene.add_geometry(p,node_name='fig_'+nme,geom_name='fig_'+nme)
os.makedirs('out4',exist_ok=True); scene.export('out4/lego.glb')
print('size',os.path.getsize('out4/lego.glb')/1e6,'bounds',scene.bounds, 'figure height mm',(scene.bounds[1][1]*1000-Y0))
