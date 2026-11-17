"""Two interactive pages of the documentation site: the SPARQL page (rdflib under Pyodide, no endpoint) and the 3D viewer for the two GLB models (three.js).

The queries live in data/queries.json (prefixes + queries). Every query is executed against the real graph at build time; a query that returns no
rows fails the build, because an empty result is the usual symptom of a broken graph. The graph the browser queries is docs/graph.nt (ontology,
Wikidata mapping, four FDOx bundles, registry pins), written as sorted N-Triples with canonical blank node ids so that it is byte-stable.
Pyodide, rdflib and three.js are pinned; bump them on purpose, not by omission.
"""
from __future__ import annotations

import html
import json
import shutil

from rdflib import BNode
from rdflib.compare import to_canonical_graph

from lrec_utils import DATA, DOCS, ROOT

PYODIDE = "0.26.4"
RDFLIB = "7.1.1"      # pure-Python wheel that micropip installs; the build runs the queries with the pinned rdflib of requirements.txt
THREE = "0.160.0"
MAX_ROWS = 500
MODELS = [("p1", "Pyramid 1", "p1_reconstruction.glb", "Reconstruction model 1 (white stepped pyramid with column and figure)"),
          ("p2", "Pyramid 2", "p2_reconstruction.glb", "Reconstruction model 2 (stepped Maya pyramid with temple, version 4)")]


def esc(x) -> str:
    return html.escape(str(x))


def write_graph(gm) -> int:
    cg = to_canonical_graph(gm)
    lines = sorted(cg.serialize(format="nt").splitlines())
    (DOCS / "graph.nt").write_text("\n".join(l for l in lines if l.strip()) + "\n", encoding="utf-8", newline="\n")
    return len(lines)


def sparql_page(gm, report) -> str:
    cfg = json.loads((DATA / "queries.json").read_text(encoding="utf-8"))
    pre = cfg["prefixes"]
    (DOCS / "downloads" / "queries").mkdir(parents=True, exist_ok=True)
    blocks, qjs, counts = [], {}, []
    for i, q in enumerate(cfg["queries"], 1):
        n = len(list(gm.query(pre + "\n" + q["sparql"])))
        if n == 0:
            report.fail(f"query '{q['id']}' returns no rows: treat this as a defect in the graph")
        counts.append(f"{q['id']} {n}")
        (DOCS / "downloads" / "queries" / f"{q['id']}.rq").write_text(pre + "\n\n" + q["sparql"] + "\n", encoding="utf-8", newline="\n")
        qjs[q["id"]] = q["sparql"]
        rows = max(5, q["sparql"].count("\n") + 2)
        blocks.append(f'<section class=q id="q-{q["id"]}"><h2>{i}. {esc(q["title"])}</h2><p>{esc(q["intro"])}</p>'
                      f'<textarea class=sparql id="src-{q["id"]}" spellcheck=false rows={rows}>{esc(q["sparql"])}</textarea>'
                      f'<p><button type=button class=run data-q="{q["id"]}" disabled>Run</button> <button type=button class=reset data-q="{q["id"]}">Reset</button> '
                      f'<a class=muted href="downloads/queries/{q["id"]}.rq">.rq file</a> <span class=muted id="time-{q["id"]}"></span></p><div id="out-{q["id"]}"></div></section>')
    report.ok("SPARQL queries (rows): " + ", ".join(counts))
    js = (JS.replace("__PREFIXES__", json.dumps(pre)).replace("__QUERIES__", json.dumps(qjs)).replace("__MAX__", str(MAX_ROWS))
          .replace("__RDFLIB__", RDFLIB))
    body = ("<h1>Query the graph</h1><section><p>There is no SPARQL endpoint and no server. The graph is fetched as a static file (<a href=\"graph.nt\"><code>graph.nt</code></a>: ontology, "
            "Wikidata mapping, the four FDOx bundles and the registry pins) and parsed in your browser by <code>rdflib</code> under Pyodide. Edit a query and press Run; nothing you type leaves your machine. "
            "The page needs to be served over HTTP (GitHub Pages does this); opened from a local file the browser blocks the fetch.</p></section>"
            '<div class=card id=status><span id=dot class=dot></span> <span id=status-text>Loading the Python runtime (about 10 MB on first visit)&hellip;</span></div>'
            + "".join(blocks) + f"<script>{js}</script>")
    return body


JS = r"""
const PREFIXES = __PREFIXES__, QUERIES = __QUERIES__, MAX_ROWS = __MAX__;
const st = document.getElementById('status-text'), dot = document.getElementById('dot');
let pyodide = null;
function setStatus(t, s) { st.textContent = t; dot.className = 'dot ' + (s || ''); }
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function table(cols, rows, id, total) {
  const out = document.getElementById(id);
  if (!rows.length) { out.innerHTML = '<p class="muted">No results. The query is valid but matched nothing.</p>'; return; }
  let h = '<div style="overflow-x:auto"><table><tr>' + cols.map(c => '<th>' + esc(c) + '</th>').join('') + '</tr>';
  for (const r of rows) h += '<tr>' + cols.map(c => { const v = r[c]; if (v === null || v === undefined) return '<td class="muted">&mdash;</td>';
    const s = String(v); return /^https?:\/\//.test(s) ? '<td><a href="' + esc(s) + '" target="_blank" rel="noopener">' + esc(s) + '</a></td>' : '<td>' + esc(s) + '</td>'; }).join('') + '</tr>';
  out.innerHTML = h + '</table></div><p class="muted">' + (total > rows.length ? 'Showing the first ' + rows.length + ' of ' + total + ' rows.' : rows.length + ' row' + (rows.length === 1 ? '' : 's') + '.') + '</p>';
}
async function boot() {
  try {
    pyodide = await loadPyodide();
    setStatus('Installing rdflib…', 'busy');
    await pyodide.loadPackage('micropip');
    await pyodide.runPythonAsync('import micropip\nawait micropip.install("rdflib==__RDFLIB__")');
    setStatus('Loading the graph…', 'busy');
    await pyodide.runPythonAsync(`
from pyodide.http import pyfetch
from rdflib import Graph
resp = await pyfetch("graph.nt")
if resp.status != 200:
    raise RuntimeError("graph.nt -> HTTP " + str(resp.status))
base = Graph()
base.parse(data=await resp.string(), format="nt")
n_base = len(base)
`);
    setStatus('Ready — ' + pyodide.globals.get('n_base') + ' triples loaded. Edit a query and press Run.', 'ok');
    document.querySelectorAll('button.run').forEach(b => b.disabled = false);
  } catch (e) { setStatus('Could not start: ' + e.message, 'err'); console.error(e); }
}
async function run(id) {
  const btn = document.querySelector('button.run[data-q="' + id + '"]'), tm = document.getElementById('time-' + id), out = document.getElementById('out-' + id);
  btn.disabled = true; tm.textContent = 'running…'; out.innerHTML = '';
  const t0 = performance.now();
  try {
    pyodide.globals.set('_q', PREFIXES + '\n' + document.getElementById('src-' + id).value);
    const json = await pyodide.runPythonAsync(`
import json
res = base.query(_q)
cols = [str(v) for v in res.vars]
_all = list(res)
rows = [{c: (None if r[i] is None else str(r[i])) for i, c in enumerate(cols)} for r in _all[:${MAX_ROWS}]]
json.dumps({"cols": cols, "rows": rows, "total": len(_all)})
`);
    const d = JSON.parse(json);
    table(d.cols, d.rows, 'out-' + id, d.total);
    tm.textContent = ((performance.now() - t0) / 1000).toFixed(1) + ' s';
  } catch (e) { out.innerHTML = '<pre style="white-space:pre-wrap;color:#9a3412">' + esc(e.message) + '</pre>'; tm.textContent = ''; }
  btn.disabled = false;
}
document.querySelectorAll('button.run').forEach(b => b.addEventListener('click', () => run(b.dataset.q)));
document.querySelectorAll('button.reset').forEach(b => b.addEventListener('click', () => { const id = b.dataset.q;
  document.getElementById('src-' + id).value = QUERIES[id]; document.getElementById('out-' + id).innerHTML = ''; document.getElementById('time-' + id).textContent = ''; }));
boot();
"""


def viewer_page(report) -> str:
    (DOCS / "models").mkdir(exist_ok=True)
    opts, info = "", {}
    for key, name, f, desc in MODELS:
        src = ROOT / "dist" / "models" / f
        if not src.exists():
            report.fail(f"{src.name} missing; run the reconstruct step first")
            continue
        shutil.copyfile(src, DOCS / "models" / f)
        info[key] = {"file": "models/" + f, "text": desc, "mb": round(src.stat().st_size / 1e6, 1)}
        opts += f'<option value="{key}">{esc(name)}</option>'
    mod = (VIEWER.replace("__MODELS__", json.dumps(info)).replace("__THREE__", THREE))
    return ("<h1>3D viewer</h1><section><p>The two brick reconstructions as GLB files (glTF 2.0), rebuilt by <code>main.py</code> from the reconstruction scripts and compared with a recorded checksum. "
            "Drag to turn, scroll to zoom, right-drag to pan. The models are 3 to 4 MB each and load when selected.</p>"
            f'<p><label>Model <select id=sel>{opts}</select></label> <button type=button id=reset>Reset view</button> <span class=muted id=info></span></p>'
            '<div id=view style="width:100%;height:560px;background:#eef0f3;border-radius:8px;position:relative"><span class=muted id=msg style="position:absolute;left:12px;top:10px">Loading three.js&hellip;</span></div>'
            '<p class=muted>Download: <a href="models/p1_reconstruction.glb">pyramid 1 (GLB)</a> &middot; <a href="models/p2_reconstruction.glb">pyramid 2 (GLB)</a>. '
            'The published records are on the <a href="fdox.html">FDOx page</a>.</p></section>'
            '<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@' + THREE + '/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@' + THREE + '/examples/jsm/"}}</script>'
            f'<script type="module">{mod}</script>')


VIEWER = r"""
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const MODELS = __MODELS__;
const box = document.getElementById('view'), msg = document.getElementById('msg'), sel = document.getElementById('sel'), info = document.getElementById('info');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
box.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeef0f3);
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
let current = null, home = null;
function resize() { const w = box.clientWidth, h = box.clientHeight; renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize();
function frame(obj) {
  const b = new THREE.Box3().setFromObject(obj), c = b.getCenter(new THREE.Vector3()), s = b.getSize(new THREE.Vector3()).length();
  controls.target.copy(c);
  camera.position.copy(c).add(new THREE.Vector3(0.9, 0.6, 1.1).normalize().multiplyScalar(s * 1.3));
  camera.near = s / 100; camera.far = s * 20; camera.updateProjectionMatrix(); controls.update();
  home = { p: camera.position.clone(), t: controls.target.clone() };
}
const loader = new GLTFLoader();
function load(key) {
  const m = MODELS[key]; msg.textContent = 'Loading ' + m.file + ' (' + m.mb + ' MB)…'; msg.hidden = false;
  loader.load(m.file, g => {
    if (current) scene.remove(current);
    current = g.scene; scene.add(current); frame(current); msg.hidden = true; info.textContent = m.text;
  }, undefined, e => { msg.textContent = 'Could not load the model: ' + (e.message || e); });
}
sel.addEventListener('change', () => load(sel.value));
document.getElementById('reset').addEventListener('click', () => { if (home) { camera.position.copy(home.p); controls.target.copy(home.t); controls.update(); } });
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
load(sel.value);
"""
