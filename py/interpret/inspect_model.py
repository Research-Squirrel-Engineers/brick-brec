#!/usr/bin/env python
"""inspect_model.py: objective facts + standard views for ANY 3D model (OBJ, GLB/GLTF, PLY, STL, OFF ...).
Output: <stem>_facts.json and <stem>_views.png  (input for the 'incognito' interpretation, see README).
Windows cmd (one line): pip install trimesh numpy scipy matplotlib pillow && python inspect_model.py model.glb"""
import argparse, json, os, sys
import numpy as np, trimesh
from scipy.spatial import cKDTree
from scipy.cluster.vq import kmeans2
from PIL import Image

AX = 'xyz'

def geom_rgb(g):
    """per-face RGB (0..1) of one geometry; texture is sampled via UV when present, otherwise material/vertex colour, else grey"""
    try:
        c = np.asarray(g.visual.to_color().face_colors, float)[:, :3] / 255.0
        if c.shape[0] == len(g.faces): return c
    except Exception: pass
    try:
        m = g.visual.material; f = getattr(m, 'baseColorFactor', None)
        if f is None: f = getattr(m, 'main_color', None)
        if f is not None: return np.tile(np.asarray(f, float)[:3] / (255.0 if np.max(f) > 1 else 1.0), (len(g.faces), 1))
    except Exception: pass
    return np.full((len(g.faces), 3), 0.75)

def load(path):
    obj = trimesh.load(path, process=False)
    geoms = obj.dump() if isinstance(obj, trimesh.Scene) else [obj]
    geoms = [g for g in geoms if isinstance(g, trimesh.Trimesh) and len(g.faces)]
    if not geoms: sys.exit('no triangle mesh found in ' + path)
    mats, cols, parts = [], [], []
    for g in geoms:
        info = {'visual_kind': getattr(g.visual, 'kind', None)}
        m = getattr(g.visual, 'material', None)
        if m is not None:
            info['material_name'] = getattr(m, 'name', None)
            img = getattr(m, 'image', None) or getattr(m, 'baseColorTexture', None)
            if img is not None: info['texture_size'] = list(img.size)
        mats.append(info); cols.append(geom_rgb(g)); parts.append(trimesh.Trimesh(g.vertices, g.faces, process=False))
    return trimesh.util.concatenate(parts), mats, len(geoms), np.concatenate(cols)

def up_estimate(mesh, ext, path):
    if os.path.splitext(path)[1].lower() in ('.glb', '.gltf'):
        return dict(axis='y', sign='+', method='glTF specification (Y up)', confidence=0.9, scores=None)
    n = mesh.face_normals; ar = mesh.area_faces; cen = mesh.triangles_center
    lo, hi = mesh.bounds; sc = {}
    for i in range(3):
        j, k = [q for q in range(3) if q != i]; proj = max(ext[j] * ext[k], 1e-12)
        for s in (-1, 1):
            near = (np.abs(cen[:, i] - (lo[i] if s < 0 else hi[i])) < 0.02 * ext[i]) & (n[:, i] * s > 0.966)
            sc[f'{AX[i]}{"-" if s < 0 else "+"}'] = round(float(ar[near].sum() / proj), 3)
    best = max(sc, key=sc.get); srt = sorted(sc.values(), reverse=True)
    conf = 0.25 if srt[0] < 0.15 else round(min(0.9, 0.4 + (srt[0] - srt[1])), 2)
    return dict(axis=best[0], sign=best[1], method='largest flat face at an extreme (base heuristic)', confidence=conf, scores=sc)

def to_up_frame(P, u, sign):
    a, b = (u + 1) % 3, (u + 2) % 3
    Q = np.stack([P[:, a], P[:, b], P[:, u]], 1)
    if sign == '-': Q[:, 2] *= -1; Q[:, 1] *= -1
    return Q

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--out', default='.')
    ap.add_argument('--up', help='force up axis, e.g. y+ or z-'); ap.add_argument('--max-faces', type=int, default=120000)
    A = ap.parse_args(); os.makedirs(A.out, exist_ok=True); stem = os.path.splitext(os.path.basename(A.model))[0]
    rng = np.random.default_rng(0)
    mesh, mats, ngeo, FRGB = load(A.model); V, F = mesh.vertices, mesh.faces
    lo, hi = mesh.bounds; ext = hi - lo; diag = float(np.linalg.norm(ext))
    up = up_estimate(mesh, ext, A.model)
    if A.up: up = dict(axis=A.up[0], sign=A.up[1], method='forced by user', confidence=1.0, scores=up['scores'])
    u = AX.index(up['axis'])
    pts, fi = trimesh.sample.sample_surface(mesh, 120000, seed=0); frgb = FRGB
    Q = to_up_frame(pts, u, up['sign']); Vq = to_up_frame(V, u, up['sign'])
    qlo, qhi = Vq.min(0), Vq.max(0); qext = qhi - qlo; qc = (qlo + qhi) / 2
    # --- profile along up axis
    N = 48; edges = np.linspace(qlo[2], qhi[2], N + 1); prof = []
    for s in range(N):
        m = (Q[:, 2] >= edges[s]) & (Q[:, 2] <= edges[s + 1])
        if m.sum() < 30: prof.append(None); continue
        wa = np.percentile(Q[m, 0], 99.5) - np.percentile(Q[m, 0], 0.5); wb = np.percentile(Q[m, 1], 99.5) - np.percentile(Q[m, 1], 0.5)
        prof.append(dict(z_rel=round(float((edges[s] - qlo[2]) / qext[2]), 3), width_a=round(float(wa), 4), width_b=round(float(wb), 4)))
    fp = np.array([p['width_a'] * p['width_b'] for p in prof if p]); fpn = fp / fp.max() if len(fp) else fp
    plateaus = []
    for f in fpn:
        if not plateaus or abs(f - np.mean(plateaus[-1])) > 0.06: plateaus.append([f])
        else: plateaus[-1].append(f)
    monotone = bool(np.all(np.diff([np.mean(p) for p in plateaus]) <= 0.03)) if len(plateaus) > 1 else False
    ptype = 'prismatic' if len(plateaus) == 1 else 'stepped_taper' if (monotone and len(plateaus) >= 3) else 'taper' if monotone else 'irregular'
    # --- horizontal surface levels (flat upward faces)
    n_up = mesh.face_normals[:, u] * (1 if up['sign'] == '+' else -1); hz = n_up > 0.966
    zc = (mesh.triangles_center[:, u] * (1 if up['sign'] == '+' else -1)); zc = zc - zc.min()
    levels = []
    if hz.any() and qext[2] > 0:
        H, be = np.histogram(zc[hz] / qext[2], bins=200, range=(0, 1), weights=mesh.area_faces[hz]); H = H / H.sum()
        i = 0
        while i < 200:
            if H[i] > 0.004:
                j = i
                while j + 1 < 200 and H[j + 1] > 0.004: j += 1
                levels.append(dict(height_rel=round(float((be[i] + be[j + 1]) / 2), 3), area_share=round(float(H[i:j + 1].sum()), 3))); i = j + 1
            else: i += 1
        levels = [l for l in levels if l['area_share'] >= 0.015]
    # terraces: drop small levels lying just above a larger one (stud tops), then find the longest run of equally spaced levels (steps)
    terr = []
    for l in levels:
        if terr and l['area_share'] < 0.02 and l['height_rel'] - terr[-1]['height_rel'] < 0.03: continue
        terr.append(l)
    hs = [l['height_rel'] for l in terr]; best = []
    for i in range(len(hs)):
        for j in range(i + 1, len(hs)):
            sp = hs[j] - hs[i]; run = [hs[i], hs[j]]
            while True:
                nxt = [h for h in hs if abs(h - (run[-1] + sp)) < 0.15 * sp]
                if not nxt: break
                run.append(nxt[0])
            if len(run) > len(best): best = run
    regular = dict(count=len(best), spacing_rel=round(float(np.mean(np.diff(best))), 3) if len(best) > 1 else None) if len(best) >= 3 else dict(count=0, spacing_rel=None)
    # --- symmetry
    P0 = Q[:40000] - qc; T = cKDTree(P0); sym = {}
    for name, M in (('mirror_a', [-1, 1, 1]), ('mirror_b', [1, -1, 1]), ('mirror_up', [1, 1, -1]), ('rot90_about_up', None)):
        R = P0 * M if M else np.stack([-P0[:, 1], P0[:, 0], P0[:, 2]], 1)
        d = float(T.query(R)[0].mean() / diag * 1000); sym[name] = dict(permille_of_diagonal=round(d, 2), rating='high' if d < 5 else 'medium' if d < 15 else 'low')
    # --- periodic pattern in top-down height map
    G = 256; ia = np.clip(((Q[:, 0] - qlo[0]) / max(qext[0], 1e-9) * (G - 1)).astype(int), 0, G - 1); ib = np.clip(((Q[:, 1] - qlo[1]) / max(qext[1], 1e-9) * (G - 1)).astype(int), 0, G - 1)
    hm = np.full((G, G), np.nan); np.fmax.at(hm, (ia, ib), Q[:, 2]); hm = np.where(np.isnan(hm), np.nanmin(hm), hm); from scipy.ndimage import gaussian_filter
    hm = hm - gaussian_filter(hm, G / 25); hm = hm - hm.mean()
    ac = np.fft.irfft2(np.abs(np.fft.rfft2(hm)) ** 2, s=hm.shape); ac = np.fft.fftshift(ac / ac[0, 0])
    from scipy.ndimage import maximum_filter
    yy, xx = np.mgrid[:G, :G]; r = np.hypot(yy - G // 2, xx - G // 2); locmax = (ac == maximum_filter(ac, size=7)) & (r >= 4) & (r < G / 4)
    ac2 = np.where(locmax, ac, -1); py, px = np.unravel_index(np.argmax(ac2), ac2.shape)
    strength = float(ac2[py, px]); pitch_cells = float(np.hypot(py - G // 2, px - G // 2))
    periodic = dict(detected=bool(strength > 0.10), strength=round(strength, 3), pitch_cells=round(pitch_cells, 1) if strength > 0.10 else None,
                    pitch_rel_to_extent_a=round(pitch_cells / G, 4) if strength > 0.10 else None, note='heuristic: strongest repeat distance of the top-down height map (relative to bbox, grid 256, high-pass filtered)')
    # --- colours
    w = mesh.area_faces / mesh.area_faces.sum(); idx = rng.choice(len(F), 20000, p=w); C = frgb[idx]
    k = 6; cent, lab = kmeans2(C, k, minit='++', seed=1); share = np.bincount(lab, minlength=k) / len(lab)
    pal = [dict(hex='#%02x%02x%02x' % tuple(int(255 * c) for c in cent[i]), share=round(float(share[i]), 3)) for i in np.argsort(-share)]
    mx, mn = C.max(1), C.min(1); sat = float(np.mean(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)))
    # --- mesh quality
    mw = mesh.copy(); mw.merge_vertices(); el = mw.edges_unique_length; boundary = int(np.sum(np.bincount(mw.edges_unique_inverse) == 1))
    comps = len(mw.split(only_watertight=False)) if len(F) < 300000 else None
    ext_all = float(ext.max()); fmt = os.path.splitext(A.model)[1].lower()
    unit_hint = 'metres (glTF specification)' if fmt in ('.glb', '.gltf') else 'unknown; largest extent %.4g: %s' % (ext_all, 'metres or arbitrary' if ext_all < 10 else 'centimetres or millimetres likely' if ext_all < 2000 else 'millimetres or arbitrary scan units')
    facts = dict(schema='lrec-model-facts/1.0', model_id=stem, file=dict(name=os.path.basename(A.model), format=fmt.strip('.'), bytes=os.path.getsize(A.model)),
        counts=dict(vertices=int(len(V)), vertices_after_merge=int(len(mw.vertices)), faces=int(len(F)), geometries=ngeo, connected_components=comps, watertight=bool(mw.is_watertight), boundary_edges=boundary),
        bounding_box=dict(min=[round(float(x), 5) for x in lo], max=[round(float(x), 5) for x in hi], extents=[round(float(x), 5) for x in ext], diagonal=round(diag, 5), axes_original='x,y,z as in file'),
        up_axis_estimate=up, units_hint=unit_hint,
        frame_used_for_analysis='a,b = the two horizontal axes, z = up (derived from up_axis_estimate; views use this frame). Front view looks along +b.',
        extents_in_analysis_frame=dict(a=round(float(qext[0]), 5), b=round(float(qext[1]), 5), up=round(float(qext[2]), 5)),
        footprint_profile=dict(slices=N, plateaus_detected=len(plateaus), type=ptype, base_footprint_ratio=round(float(fpn[0]), 3) if len(fpn) else None, top_footprint_ratio=round(float(fpn[-1]), 3) if len(fpn) else None, note='plateaus = distinct footprint sizes along the height (robust 0.5-99.5 percentile widths)', data=[p for p in prof if p][::4]),
        horizontal_surface_levels=dict(count_raw=len(levels), count_without_stud_tops=len(terr), levels=levels, regular_steps=regular,
            note='height_rel = 0 base .. 1 top; area_share = share of upward-facing flat area. count_raw INCLUDES small stud-top levels and is NOT a number of steps. count_without_stud_tops drops small levels just above a larger one. regular_steps = longest run of equally spaced levels (heuristic; may include a base plate or exclude a top element). The views decide the real step count.'),
        symmetry=sym, periodic_pattern=periodic,
        appearance=dict(dominant_colours=pal, mean_saturation=round(sat, 3), grayscale_like=bool(sat < 0.08), visual_kind=mats[0].get('visual_kind'), materials=mats[:6]),
        mesh_quality=dict(edge_length_median=round(float(np.median(el)), 6), edge_length_p95_over_median=round(float(np.percentile(el, 95) / max(np.median(el), 1e-12)), 2), degenerate_faces=int((mesh.area_faces < 1e-12 * diag ** 2).sum())),
        heuristics_note='Fields marked heuristic are computed by simple rules and can be wrong; the images are authoritative for shape.')
    jpath = os.path.join(A.out, stem + '_facts.json'); json.dump(facts, open(jpath, 'w'), indent=2); print('wrote', jpath)
    # --- views
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib.collections import PolyCollection
    Fi = np.arange(len(F)); 
    if len(F) > A.max_faces: Fi = rng.choice(len(F), A.max_faces, replace=False)
    Vc = (Vq - qc) / qext.max(); tri = Vc[F[Fi]]; fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12); col = frgb[Fi]
    views = [('Front', 0, 25), ('Right', 90, 25), ('Back', 180, 25), ('Left', 270, 25), ('Top', 0, 89.9), ('3/4 view', 35, 35)]
    fig, axs = plt.subplots(2, 3, figsize=(15, 10.4), dpi=80); fig.patch.set_facecolor('white')
    for axx, (nm, az, el_) in zip(axs.ravel(), views):
        az_, el__ = np.radians(az), np.radians(el_); cam = np.array([np.sin(az_) * np.cos(el__), -np.cos(az_) * np.cos(el__), np.sin(el__)]); v = -cam
        rr = np.cross(v, [0, 0, 1]); rr /= np.linalg.norm(rr); uu = np.cross(rr, v)
        xy = np.stack([tri @ rr, tri @ uu], -1); dep = (tri @ v).mean(1); order = np.argsort(-dep)
        sh = 0.35 + 0.65 * np.clip(fn @ cam, 0, 1); cc = np.clip(col * sh[:, None], 0, 1)
        axx.add_collection(PolyCollection(xy[order], facecolors=cc[order], edgecolors='none', linewidths=0)); axx.set_xlim(-0.8, 0.8); axx.set_ylim(-0.8, 0.8)
        axx.set_aspect('equal'); axx.axis('off'); axx.set_title(nm, fontsize=14)
    fig.suptitle(f'{stem}: extents a x b x up = {qext[0]:.4g} x {qext[1]:.4g} x {qext[2]:.4g} (file units); up axis {up["sign"]}{up["axis"]} ({up["method"]}, conf. {up["confidence"]})', fontsize=11)
    plt.tight_layout(); ipath = os.path.join(A.out, stem + '_views.png'); fig.savefig(ipath); print('wrote', ipath)

if __name__ == '__main__': main()
