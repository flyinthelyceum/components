"""Measurement worksheet for the lyceum's whole box of brass heat-set inserts.

Fifteen sizes, four thread families. Emits sheet.csv (one row per measurement, in
the shape worksheets/apply.py runs) and sheet.html (a bench page to type into,
which exports that same CSV).

    python worksheets/heatset_inserts/sheet.py
    # fill it in, then
    python worksheets/apply.py worksheets/heatset_inserts/sheet.csv --by JR

TWO MEASUREMENTS PER INSERT, and only two, because only two size a boss:

  OD      the diameter OVER THE KNURL - the widest the part ever is, which is what
          the plastic has to be displaced to accept. NOT the body diameter.
  LENGTH  overall, end to end.

The vendor label reads THREAD x LENGTH x OD, and its OD is the BODY, not the knurl.
Measured, the one M3 x 6 x 5 in this box is 5.461 over the knurl - 0.46 mm proud of
the number on the packet. That gap is the whole reason this worksheet exists: a boss
sized to a packet figure asked its insert for three times the interference a heat-set
wants, bowed the post outward and pushed melt up through the thread.

Part naming is thread and length, `heatset_insert_m3x6`, because within a family the
OD is common and the length is what a buyer actually chooses.
"""
from __future__ import annotations

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (thread, [lengths]), and the body OD the packet claims for that family
FAMILIES = [
    ("M2", [4, 6, 8, 10], 3.5),
    ("M3", [4, 6, 8, 10], 5.0),
    ("M4", [4, 6, 8, 10], 6.0),
    ("M5", [6, 8, 10], 7.0),
]

# what is already in the package, so the sheet does not ask for it twice
KNOWN = {"m3x6": {"OD": 5.461, "LENGTH": 6.07}}

CONSTS = [
    ("OD", "diameter over the knurl",
     "outside jaws on the widest band; rotate the insert and take the largest reading",
     "label_od"),
    ("LENGTH", "overall length",
     "outside jaws end to end, square to the axis", "label_len"),
]


def parts():
    out = []
    for thread, lengths, body_od in FAMILIES:
        for ln in lengths:
            key = f"{thread.lower()}x{ln}"
            out.append({"key": key, "part": f"heatset_insert_{key}",
                        "label": f"{thread} × {ln} × {body_od:g}",
                        "thread": thread, "len": float(ln), "body_od": body_od,
                        "known": KNOWN.get(key)})
    return out


def rows():
    out = []
    for p in parts():
        for const, what, how, which in CONSTS:
            nominal = p["body_od"] if which == "label_od" else p["len"]
            known = (p["known"] or {}).get(const)
            out.append({
                "letter": f"{p['key']}-{'D' if const == 'OD' else 'L'}",
                "part": p["part"], "const": const,
                "what": f"{p['label']} — {what}", "how": how,
                "datasheet_nominal_mm": f"{nominal:g}",
                "measured_mm": f"{known:g}" if known else "",
                "note": "already in the package, 2026-09-17" if known else "",
            })
    return out


def write_csv(path):
    r = rows()
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(r[0].keys()))
        w.writeheader()
        w.writerows(r)
    return len(r)


# ------------------------------------------------------------------- the page ----
HTML = """<title>Heat-Set Insert Stock</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{--ground:#EFEBE3;--panel:#F8F6F1;--ink:#1A1C1E;--ink2:#4A463F;--muted:#6F6960;
  --rule:#D3CCBF;--soft:#E2DCD1;--ok:#1B6E93;--warn:#A2571B;--bad:#93321B;--brass:#8A6A2F;
  --sans:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  --nar:"Archivo Narrow","IBM Plex Sans",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#131417;--panel:#1B1D20;--ink:#EAE6DD;--ink2:#BDB7AC;--muted:#8C867C;
  --rule:#34373B;--soft:#26292C;--ok:#6EC6EA;--warn:#D79A55;--bad:#E0765A;--brass:#C7A35E}}
:root[data-theme="dark"]{--ground:#131417;--panel:#1B1D20;--ink:#EAE6DD;--ink2:#BDB7AC;
  --muted:#8C867C;--rule:#34373B;--soft:#26292C;--ok:#6EC6EA;--warn:#D79A55;
  --bad:#E0765A;--brass:#C7A35E}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.5;padding:0 20px;padding-block:24px 48px;
  -webkit-text-size-adjust:100%}
.wrap{max-width:980px;margin:0 auto;display:grid;gap:20px}
h1{font-family:var(--nar);text-transform:uppercase;letter-spacing:.12em;font-size:19px;
  font-weight:700;margin:0 0 6px;text-wrap:balance}
header p{margin:0;color:var(--ink2);max-width:64ch;font-size:14px}
.top{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-start;
  justify-content:space-between}
.units{display:flex;border:1px solid var(--rule);flex:none}
.units button{font-family:var(--nar);text-transform:uppercase;letter-spacing:.09em;
  font-size:11.5px;font-weight:700;padding:8px 14px;border:0;background:var(--panel);
  color:var(--muted);cursor:pointer}
.units button[aria-pressed="true"]{background:var(--ink);color:var(--ground)}
figure{margin:0;background:var(--panel);border:1px solid var(--rule);padding:14px}
figure figcaption{font-size:12.5px;color:var(--muted);margin-top:8px;max-width:62ch}
section{background:var(--panel);border:1px solid var(--rule)}
h2{font-family:var(--nar);text-transform:uppercase;letter-spacing:.13em;font-size:11.5px;
  color:var(--muted);font-weight:700;margin:0;padding:11px 14px 9px;
  border-bottom:1px solid var(--rule);display:flex;gap:10px;align-items:baseline}
h2 em{font-style:normal;text-transform:none;letter-spacing:0;font-family:var(--sans);
  font-weight:400}
h2 .od{margin-left:auto;font-family:var(--mono);font-size:11.5px;text-transform:none;
  letter-spacing:0}
.row{display:grid;grid-template-columns:118px repeat(2,minmax(0,1fr)) 96px;gap:10px;
  align-items:center;padding:7px 14px;border-bottom:1px solid var(--soft)}
.row:last-child{border-bottom:0}
.row.head{border-bottom:1px solid var(--rule);padding-top:9px;padding-bottom:9px}
.row.head span{font-family:var(--nar);text-transform:uppercase;letter-spacing:.09em;
  font-size:10.5px;font-weight:700;color:var(--muted)}
.name{font-family:var(--mono);font-size:13px;font-variant-numeric:tabular-nums}
.name b{font-weight:600}
.name i{display:block;font-style:normal;font-size:11px;color:var(--muted);
  font-family:var(--sans)}
.cell{position:relative}
input{font-family:var(--mono);font-size:14px;width:100%;background:var(--ground);
  color:var(--ink);border:1px solid var(--rule);padding:6px 8px;border-radius:0;
  font-variant-numeric:tabular-nums}
input:focus{outline:2px solid var(--ok);outline-offset:-1px}
input.done{border-color:var(--ok)}
.alt{font-family:var(--mono);font-size:10.5px;color:var(--muted);
  position:absolute;right:8px;top:50%;transform:translateY(-50%);pointer-events:none;
  background:var(--ground);padding-left:4px}
.flag{font-family:var(--mono);font-size:11px;text-align:right;color:var(--muted);
  font-variant-numeric:tabular-nums}
.flag.w{color:var(--warn)}.flag.b{color:var(--bad)}.flag.k{color:var(--ok)}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:12px 14px}
button.act{font-family:var(--nar);text-transform:uppercase;letter-spacing:.09em;
  font-size:11.5px;font-weight:700;padding:9px 14px;border:1px solid var(--rule);
  background:var(--ground);color:var(--ink);cursor:pointer}
button.act:hover{background:var(--soft)}
button.act:focus-visible{outline:2px solid var(--ok);outline-offset:1px}
#save{margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.calc{padding:13px 14px;display:grid;gap:9px}
.calc p{margin:0;font-size:13px;color:var(--ink2);max-width:64ch}
.calc p b{font-family:var(--mono);font-weight:600}
.meter{height:5px;background:var(--soft);overflow:hidden}
.meter i{display:block;height:100%;background:var(--ok);width:0}
dialog{background:var(--panel);color:var(--ink);border:1px solid var(--rule);
  max-width:min(94vw,860px);width:100%;padding:0}
dialog::backdrop{background:rgba(0,0,0,.45)}
dialog textarea{width:100%;border:0;border-top:1px solid var(--rule);min-height:54vh;
  font-family:var(--mono);font-size:11.5px;background:var(--ground);color:var(--ink);
  padding:12px;resize:vertical}
@media (max-width:640px){.row{grid-template-columns:1fr 1fr;row-gap:6px}
  .row .name{grid-column:1/-1}.row .flag{grid-column:1/-1;text-align:left}
  .row.head{display:none}}
</style>
<div class="wrap">
<header class="top">
  <div>
    <h1>Heat-Set Insert Stock</h1>
    <p>Fifteen sizes, two numbers each. Type what the caliper says in whichever unit
    it is set to; the sheet keeps millimetres, because that is what the components
    package stores. The M3 × 6 is already in the package and comes filled in — re-measure
    it if you like, it is a useful check on your own repeatability.</p>
  </div>
  <div class="units" role="group" aria-label="Units">
    <button id="uMM" aria-pressed="false">mm</button>
    <button id="uIN" aria-pressed="true">inch</button>
  </div>
</header>

<figure>
__SVG__
  <figcaption><b>Measure over the knurl, not the body.</b> The packet reads
  thread × length × <i>body</i> diameter, and the knurl stands proud of it — the one
  insert measured so far is 5.461 mm over the knurl against a packet figure of 5. A
  boss sized to the packet asked three times the interference a heat-set wants and
  bowed the post outward. Rotate each insert in the jaws and keep the largest
  reading.</figcaption>
</figure>

<div id="form"></div>

<section>
  <h2>Progress</h2>
  <div class="meter"><i id="meter"></i></div>
  <div class="calc" id="calc"></div>
  <div class="bar">
    <button class="act" id="exp">Copy CSV</button>
    <button class="act" id="expcmd">Copy commands</button>
    <button class="act" id="clr">Clear</button>
    <span id="save">not saved</span>
  </div>
</section>
<footer style="font-size:12.5px;color:var(--muted);border-top:1px solid var(--rule);
  padding-top:11px">Generated by
  <code style="font-family:var(--mono);font-size:12px">worksheets/heatset_inserts/sheet.py</code>.
  Paste the CSV over <code style="font-family:var(--mono);font-size:12px">sheet.csv</code>,
  then run <code style="font-family:var(--mono);font-size:12px">worksheets/apply.py</code>.</footer>
</div>
<dialog id="dlg"><h2 id="dlgt">Copy</h2><textarea id="dlga" readonly></textarea>
<div class="bar"><button class="act" id="cp">Copy</button>
<button class="act" id="cl">Close</button></div></dialog>
<script>
const PARTS = __PARTS__;
const state = {};
let unit = "in", db = null, timer = null;
const MM = 25.4;
const num = v => { const n = parseFloat(String(v ?? "").replace(",", ".")); return isFinite(n) ? n : null; };
const toMM = v => unit === "in" ? v * MM : v;
const fromMM = v => unit === "in" ? v / MM : v;
const fmt = v => unit === "in" ? v.toFixed(4) : v.toFixed(3);

/* ------------------------------------------------------------------- build */
const form = document.getElementById("form");
const fams = [...new Set(PARTS.map(p => p.thread))];
for (const th of fams) {
  const mine = PARTS.filter(p => p.thread === th);
  const sec = document.createElement("section");
  const h = document.createElement("h2");
  h.innerHTML = `${th} <em>— ${mine.length} lengths</em>`;
  const od = document.createElement("span");
  od.className = "od"; od.id = "fam_" + th;
  h.appendChild(od); sec.appendChild(h);
  const head = document.createElement("div");
  head.className = "row head";
  head.innerHTML = "<span>size</span><span>Ø over knurl</span><span>length</span><span></span>";
  sec.appendChild(head);
  for (const p of mine) {
    const row = document.createElement("div");
    row.className = "row";
    const nm = document.createElement("div");
    nm.className = "name";
    nm.innerHTML = `<b>${p.label}</b><i>${p.part}</i>`;
    row.appendChild(nm);
    for (const c of ["OD", "LENGTH"]) {
      const cell = document.createElement("div"); cell.className = "cell";
      const el = document.createElement("input");
      el.type = "text"; el.inputMode = "decimal";
      el.id = `f_${p.key}_${c}`;
      el.setAttribute("aria-label", `${p.label} ${c}`);
      if (p.known) { el.value = ""; state[`${p.key}_${c}`] = String(p.known[c]); }
      const alt = document.createElement("span");
      alt.className = "alt"; alt.id = `a_${p.key}_${c}`;
      cell.append(el, alt); row.appendChild(cell);
      el.addEventListener("input", () => {
        const v = num(el.value);
        state[`${p.key}_${c}`] = v == null ? "" : String(+toMM(v).toFixed(3));
        recompute(); queueSave();
      });
    }
    const flag = document.createElement("div");
    flag.className = "flag"; flag.id = `g_${p.key}`;
    row.appendChild(flag);
    sec.appendChild(row);
  }
  form.appendChild(sec);
}

/* ------------------------------------------------------------------ units */
function setUnit(u) {
  unit = u;
  document.getElementById("uMM").setAttribute("aria-pressed", u === "mm");
  document.getElementById("uIN").setAttribute("aria-pressed", u === "in");
  for (const p of PARTS) for (const c of ["OD", "LENGTH"]) {
    const el = document.getElementById(`f_${p.key}_${c}`);
    const mm = num(state[`${p.key}_${c}`]);
    if (el && mm != null && document.activeElement !== el) el.value = fmt(fromMM(mm));
  }
  for (const el of document.querySelectorAll("input")) el.placeholder = unit;
  recompute();
  try { localStorage.setItem("hsi-unit", u); } catch (e) {}
}
document.getElementById("uMM").onclick = () => setUnit("mm");
document.getElementById("uIN").onclick = () => setUnit("in");

/* -------------------------------------------------------------- recompute */
function recompute() {
  let filled = 0;
  for (const p of PARTS) {
    for (const c of ["OD", "LENGTH"]) {
      const mm = num(state[`${p.key}_${c}`]);
      const el = document.getElementById(`f_${p.key}_${c}`);
      const alt = document.getElementById(`a_${p.key}_${c}`);
      if (el) el.classList.toggle("done", mm != null);
      if (alt) alt.textContent = mm == null ? ""
        : (unit === "in" ? mm.toFixed(2) + " mm" : (mm / MM).toFixed(3) + " in");
      if (mm != null) filled++;
    }
    const flag = document.getElementById(`g_${p.key}`);
    const od = num(state[`${p.key}_OD`]), len = num(state[`${p.key}_LENGTH`]);
    let txt = "", cls = "flag";
    if (p.known) { txt = "in package"; cls = "flag k"; }
    else if (len != null && Math.abs(len - p.len) > 0.4) {
      txt = `length ${(len - p.len >= 0 ? "+" : "\\u2212")}${Math.abs(len - p.len).toFixed(2)}`;
      cls = "flag " + (Math.abs(len - p.len) > 1 ? "b" : "w");
    } else if (od != null && od < p.body_od) {
      txt = "under body Ø"; cls = "flag b";
    } else if (od != null) {
      txt = `+${(od - p.body_od).toFixed(2)} over body`;
    }
    if (flag) { flag.textContent = txt; flag.className = cls; }
  }
  // within a family the knurl Ø should be one number
  for (const th of fams) {
    const ods = PARTS.filter(p => p.thread === th)
      .map(p => num(state[`${p.key}_OD`])).filter(v => v != null);
    const box = document.getElementById("fam_" + th);
    if (!box) continue;
    if (ods.length < 2) { box.textContent = ""; box.style.color = ""; continue; }
    const spread = Math.max(...ods) - Math.min(...ods);
    const mean = ods.reduce((a, b) => a + b, 0) / ods.length;
    box.textContent = `Ø ${mean.toFixed(2)} · spread ${spread.toFixed(2)}`;
    box.style.color = spread > 0.15 ? "var(--bad)" : spread > 0.08 ? "var(--warn)" : "var(--muted)";
  }
  const total = PARTS.length * 2;
  document.getElementById("meter").style.width = (100 * filled / total) + "%";
  const calc = document.getElementById("calc");
  calc.textContent = "";
  const p1 = document.createElement("p");
  p1.innerHTML = `<b>${filled}</b> of <b>${total}</b> measured.`;
  calc.appendChild(p1);
  const bad = fams.filter(th => {
    const ods = PARTS.filter(p => p.thread === th)
      .map(p => num(state[`${p.key}_OD`])).filter(v => v != null);
    return ods.length > 1 && Math.max(...ods) - Math.min(...ods) > 0.15;
  });
  const p2 = document.createElement("p");
  p2.textContent = bad.length
    ? `Knurl Ø disagrees within ${bad.join(", ")} by more than 0.15 mm. Inserts of one thread usually share an outside diameter, so check those rows — most likely a row typed against the wrong size, or a genuinely mixed bag worth knowing about.`
    : "Inserts of one thread usually share an outside diameter. Fill a family and this checks it for you.";
  calc.appendChild(p2);
}

/* ------------------------------------------------------------- persistence */
const setSaved = t => document.getElementById("save").textContent = t;
function queueSave() {
  try { localStorage.setItem("hsi-sheet", JSON.stringify(state)); } catch (e) {}
  setSaved(db ? "saving\\u2026" : "saved on this device");
  if (!db) return;
  clearTimeout(timer);
  timer = setTimeout(async () => {
    try { await db.doc("stock/heatset").set({...state, at: new Date().toISOString()});
          setSaved("saved"); }
    catch (e) { setSaved("save failed \\u2014 kept on this device"); }
  }, 600);
}
function apply(obj) {
  for (const k in obj) if (k !== "at") state[k] = obj[k];
  setUnit(unit);
}
try { const raw = localStorage.getItem("hsi-sheet"); if (raw) apply(JSON.parse(raw)); } catch (e) {}
try { const u = localStorage.getItem("hsi-unit"); if (u) unit = u; } catch (e) {}
setUnit(unit);
(async () => {
  if (!(window.claude && window.claude.use)) { setSaved("saved on this device"); return; }
  try {
    db = await window.claude.use("db");
    if (!db) { setSaved("saved on this device"); return; }
    const snap = await db.doc("stock/heatset").get();
    if (snap && snap.data) { apply(snap.data); setSaved("loaded"); }
    else setSaved("ready");
  } catch (e) { setSaved("saved on this device"); }
})();

/* ------------------------------------------------------------------ export */
function csv() {
  const head = "letter,part,const,what,how,datasheet_nominal_mm,measured_mm,note";
  const q = s => /[",]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  const out = [head];
  for (const p of PARTS) for (const c of ["OD", "LENGTH"]) {
    const r = p.rows[c], v = state[`${p.key}_${c}`] ?? "";
    out.push([`${p.key}-${c === "OD" ? "D" : "L"}`, p.part, c, q(r.what), q(r.how),
              r.nominal, v, q(p.known ? "already in the package, 2026-09-17" : "")].join(","));
  }
  return out.join("\\n");
}
function cmds() {
  const out = [];
  for (const p of PARTS) for (const c of ["OD", "LENGTH"]) {
    const v = state[`${p.key}_${c}`];
    if (!v || p.known) continue;
    out.push(`python -m components measure ${p.part} ${c} ${v} --by JR`);
  }
  return out.length ? out.join("\\n")
    : "# nothing measured yet that is not already in the package";
}
const dlg = document.getElementById("dlg");
function show(title, text) {
  document.getElementById("dlgt").textContent = title;
  document.getElementById("dlga").value = text;
  dlg.showModal();
}
document.getElementById("exp").onclick = () => show("Paste over sheet.csv", csv());
document.getElementById("expcmd").onclick = () => show("One per measurement", cmds());
document.getElementById("cl").onclick = () => dlg.close();
document.getElementById("cp").onclick = async () => {
  const t = document.getElementById("dlga"); t.select();
  try { await navigator.clipboard.writeText(t.value);
        document.getElementById("cp").textContent = "Copied"; }
  catch (e) { document.execCommand("copy"); }
};
document.getElementById("clr").onclick = () => {
  if (!confirm("Clear every value typed here?")) return;
  for (const k in state) delete state[k];
  for (const p of PARTS) if (p.known)
    for (const c of ["OD", "LENGTH"]) state[`${p.key}_${c}`] = String(p.known[c]);
  for (const el of document.querySelectorAll("input")) el.value = "";
  setUnit(unit); queueSave();
};
recompute();
</script>
"""

SVG = """  <svg viewBox="0 0 520 132" width="100%" style="max-width:520px;display:block"
       role="img" aria-label="An insert in section, with the knurl diameter and the
       overall length marked">
    <defs><marker id="a" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="5"
      markerHeight="5" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="currentColor"/>
      </marker></defs>
    <g fill="none" stroke="currentColor" stroke-width="1.4" color="var(--brass)">
      <rect x="150" y="34" width="150" height="64" fill="var(--brass)" opacity="0.14"/>
      <path d="M150 34 h150 v64 h-150 z"/>
      <path d="M150 46 h150 M150 58 h150 M150 74 h150 M150 86 h150" opacity="0.5"/>
      <path d="M176 34 v64 M300 34 v64" opacity="0"/>
      <path d="M176 40 h98 M176 52 h98 M176 68 h98 M176 80 h98 M176 92 h98"
            stroke-dasharray="3 5" opacity="0.65"/>
    </g>
    <g fill="none" stroke="currentColor" stroke-width="1.2" color="var(--muted)">
      <path d="M128 34 v64" marker-start="url(#a)" marker-end="url(#a)"/>
      <path d="M150 116 h150" marker-start="url(#a)" marker-end="url(#a)"/>
      <path d="M150 34 h-28 M150 98 h-28" stroke-dasharray="2 4"/>
      <path d="M150 98 v22 M300 98 v22" stroke-dasharray="2 4"/>
    </g>
    <g font-family="IBM Plex Mono, monospace" font-size="12" fill="currentColor"
       color="var(--ink)">
      <text x="10" y="62">Ø over</text><text x="10" y="78">the knurl</text>
      <text x="212" y="130" text-anchor="middle">LENGTH</text>
      <text x="322" y="52" fill="var(--muted)">knurl bands stand</text>
      <text x="322" y="68" fill="var(--muted)">proud of the body:</text>
      <text x="322" y="84" fill="var(--muted)">measure the ridges</text>
    </g>
  </svg>"""


def write_html(path):
    ps = []
    for p in parts():
        r = {}
        for const, what, how, which in CONSTS:
            r[const] = {"what": f"{p['label']} — {what}", "how": how,
                        "nominal": f"{p['body_od'] if which == 'label_od' else p['len']:g}"}
        ps.append({"key": p["key"], "part": p["part"], "label": p["label"],
                   "thread": p["thread"], "len": p["len"], "body_od": p["body_od"],
                   "known": p["known"], "rows": r})
    html = HTML.replace("__PARTS__", json.dumps(ps, separators=(",", ":"))) \
               .replace("__SVG__", SVG)
    with open(path, "w") as f:
        f.write(html)
    return len(ps)


if __name__ == "__main__":
    n = write_csv(os.path.join(HERE, "sheet.csv"))
    m = write_html(os.path.join(HERE, "sheet.html"))
    print(f"sheet.csv   {n} rows ({m} inserts x {len(CONSTS)} measurements)")
    print(f"sheet.html  {os.path.getsize(os.path.join(HERE, 'sheet.html'))/1024:.0f} KB")
