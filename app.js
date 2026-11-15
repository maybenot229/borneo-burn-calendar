/* Borneo Burn Calendar - Team SpaceZY - NASA Space Apps Challenge 2026
   AI-use note: this code was drafted with Claude (Anthropic) and reviewed by the team.
   Every number on the page comes from data/sabah_harmonized_monthly.csv. */
"use strict";

const DATA_URL = "data/sabah_harmonized_monthly.csv";
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const MONTHS_LONG = ["January","February","March","April","May","June","July","August","September","October","November","December"];
// Colour classes for VIIRS-equivalent hotspots per month (edges from our analysis).
const EDGES = [74, 204, 376];
const CLASS_NAME = ["Low", "Medium", "High", "Very high"];
const CLASS_BG = ["#ffffd4", "#fed98e", "#fe9929", "#cc4c02"];   // colour-blind-safe sequential
const CLASS_FG = ["#3a2a00", "#3a2a00", "#2b1600", "#ffffff"];

let rows = [], mode = "harmonized";
const $ = id => document.getElementById(id);
const fmt = n => n == null ? "–" : Math.round(n).toLocaleString("en");
const cls = v => v < EDGES[0] ? 0 : v < EDGES[1] ? 1 : v < EDGES[2] ? 2 : 3;
const median = a => { const s = [...a].sort((x, y) => x - y), m = s.length >> 1;
  return s.length ? (s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2) : null; };

/* ---------- data ---------- */
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/).filter(l => l.trim());
  const head = lines[0].split(",").map(s => s.trim());
  return lines.slice(1).map(l => {
    const c = l.split(","), o = {};
    head.forEach((h, i) => {
      const v = (c[i] ?? "").trim();
      if (h === "provisional") o[h] = /^(1|true)$/i.test(v);
      else { const n = Number(v); o[h] = (v === "" || Number.isNaN(n)) ? null : n; }
    });
    // "estimated" = the harmonized value is scaled MODIS, not a VIIRS measurement.
    o.estimated = o.viirs == null || o.harmonized !== o.viirs;
    return o;
  }).sort((a, b) => a.year - b.year || a.month - b.month);
}
const rawJoin = r => r.estimated ? r.modis_raw : r.viirs;      // MODIS before Feb 2012, VIIRS after
const value = r => mode === "harmonized" ? r.harmonized : rawJoin(r);
function inRange() { const a = +$("from").value, b = +$("to").value; return rows.filter(r => r.year >= a && r.year <= b); }

/* ---------- summary cards ---------- */
function renderStats(sel) {
  const byMonth = MONTHS.map((_, i) => median(sel.filter(r => r.month === i + 1).map(r => r.harmonized)));
  const top = byMonth.map((v, i) => [v ?? -1, i]).sort((a, b) => b[0] - a[0]).slice(0, 3);
  const years = {};
  sel.forEach(r => { (years[r.year] ??= {t: 0, n: 0, est: false}); years[r.year].t += r.harmonized; years[r.year].n++;
                     if (r.estimated) years[r.year].est = true; });
  const worst = Object.entries(years).filter(([, o]) => o.n === 12).sort((a, b) => b[1].t - a[1].t).slice(0, 3);
  const anyEst = worst.some(([, o]) => o.est);
  $("stats").innerHTML =
    `<div class="stat"><div class="k">Months that burn most</div>
       <div class="v">${top.map(x => MONTHS[x[1]]).join(", ")}</div>
       <div class="s">Highest median hotspots per calendar month, in the years selected.</div></div>
     <div class="stat"><div class="k">Worst years</div>
       <div class="v">${worst.map(([y, o]) => y + (o.est ? "*" : "")).join(", ") || "–"}</div>
       <div class="s">Highest yearly totals, full years only.${anyEst ? " * estimated from MODIS." : ""}</div></div>
     <div class="stat"><div class="k">Months in view</div>
       <div class="v">${sel.length}</div>
       <div class="s">${sel.filter(r => r.estimated).length} estimated from MODIS, ${sel.filter(r => !r.estimated).length} measured by VIIRS.</div></div>`;
}

/* ---------- heatmap ---------- */
let cells = [];                                   // [{td, r}]
function buildHeat(sel) {
  const map = new Map(sel.map(r => [r.year + "-" + r.month, r]));
  const ys = [...new Set(sel.map(r => r.year))];
  const t = $("heat"); t.innerHTML = ""; cells = [];
  const thead = t.createTHead().insertRow();
  thead.appendChild(document.createElement("th"));
  MONTHS.forEach(m => { const th = document.createElement("th"); th.textContent = m; th.scope = "col"; thead.appendChild(th); });
  const body = t.createTBody();
  for (const y of ys) {
    const tr = body.insertRow();
    const th = document.createElement("th"); th.className = "y"; th.scope = "row"; th.textContent = y; tr.appendChild(th);
    for (let m = 1; m <= 12; m++) {
      const td = tr.insertCell(), r = map.get(y + "-" + m);
      if (!r) { td.className = "none"; td.title = `${MONTHS_LONG[m - 1]} ${y}: no data`; continue; }
      cells.push({td, r});
    }
  }
  paintHeat();
}
function paintHeat() {
  for (const {td, r} of cells) {
    const v = value(r), c = cls(v);
    td.style.backgroundColor = CLASS_BG[c]; td.style.color = CLASS_FG[c];
    td.textContent = fmt(v);
    const est = mode === "harmonized" && r.estimated;
    td.className = (est ? "est " : "") + (r.provisional ? "prov" : "");
    const kind = mode === "harmonized" ? (r.estimated ? "estimated from MODIS" : "measured by VIIRS")
                                       : (r.estimated ? "MODIS raw count" : "VIIRS raw count");
    td.title = `${MONTHS_LONG[r.month - 1]} ${r.year}: ${fmt(v)} hotspots, ${CLASS_NAME[c].toLowerCase()} (${kind}${r.provisional ? ", provisional" : ""})`;
  }
  $("heatHint").textContent = mode === "harmonized"
    ? "Harmonized: every month is in VIIRS-equivalent hotspots, so years can be compared fairly. Hover or tap a cell for details."
    : "Raw join: MODIS counts before February 2012, VIIRS counts after. Early years look quiet only because the older sensor saw less.";
}
function renderLegend() {
  const range = ["under " + EDGES[0], `${EDGES[0]}–${EDGES[1] - 1}`, `${EDGES[1]}–${EDGES[2] - 1}`, EDGES[2] + " or more"];
  $("legend").innerHTML = CLASS_NAME.map((n, i) =>
      `<span><span class="sw" style="background:${CLASS_BG[i]}"></span>${n} (${range[i]})</span>`).join("") +
    `<span><span class="sw est"></span>estimated from MODIS</span>
     <span><span class="sw prov"></span>provisional</span>
     <span><span class="sw" style="background:#eef0f3"></span>no data</span>`;
}

/* ---------- now vs normal ---------- */
function renderNow() {
  const r = rows[+$("nowMonth").value];
  if (!r) return;
  const x = r.now_vs_normal;
  const word = x < 0.75 ? ["below", "Below normal"] : x > 1.25 ? ["above", "Above normal"] : ["near", "Near normal"];
  $("nowBox").innerHTML =
    `<span class="big">${x.toFixed(2)}× normal</span>
     <span class="word ${word[0]}">${word[1]}</span>
     ${r.provisional ? '<span class="badge">Provisional</span>' : ""}
     ${r.estimated ? '<span class="badge">Estimated from MODIS</span>' : ""}
     <p>${MONTHS_LONG[r.month - 1]} ${r.year}: ${fmt(r.harmonized)} hotspots.
        Normal for ${MONTHS_LONG[r.month - 1]}: ${fmt(r.normal_10yr)}.
        "Near normal" means between 0.75 and 1.25 times the median.</p>`;
}

/* ---------- line chart (plain SVG) ---------- */
function renderLine(sel) {
  const W = 960, H = 300, L = 56, R = 16, T = 12, B = 30, n = sel.length;
  if (!n) { $("lineChart").innerHTML = '<p class="hint">No data in this range.</p>'; return; }
  const max = Math.max(1, ...sel.map(r => Math.max(r.harmonized, rawJoin(r))));
  const X = i => L + (n > 1 ? i * (W - L - R) / (n - 1) : 0), Y = v => H - B - v / max * (H - T - B);
  let g = "";
  for (let k = 0; k <= 4; k++) { const v = max * k / 4, y = Y(v);
    g += `<line x1="${L}" x2="${W - R}" y1="${y}" y2="${y}" stroke="#e3e6ec"/>
          <text x="${L - 6}" y="${y + 4}" text-anchor="end" font-size="12" fill="#566074">${fmt(v)}</text>`; }
  const nYears = new Set(sel.map(r => r.year)).size, step = Math.max(1, Math.ceil(nYears / 12));
  sel.forEach((r, i) => { if (r.month === 1 && (r.year - sel[0].year) % step === 0)
    g += `<text x="${X(i)}" y="${H - 9}" text-anchor="middle" font-size="12" fill="#566074">${r.year}</text>`; });
  const i0 = sel.findIndex(r => !r.estimated);
  if (i0 > 0) g += `<line x1="${X(i0)}" x2="${X(i0)}" y1="${T}" y2="${H - B}" stroke="#555" stroke-width="1.5" stroke-dasharray="2 4"/>`;
  const path = f => sel.map((r, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(f(r)).toFixed(1)).join("");
  g += `<path d="${path(rawJoin)}" fill="none" stroke="#D55E00" stroke-width="2" stroke-dasharray="6 4"/>`;
  g += `<path d="${path(r => r.harmonized)}" fill="none" stroke="#0072B2" stroke-width="2"/>`;
  $("lineChart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img"
     aria-label="Monthly hotspots in Sabah. Before February 2012 the raw join line sits far below the harmonized line. After that the two lines are the same.">${g}</svg>`;

  const ys = [...new Set(sel.map(r => r.year))];
  $("yearTable").innerHTML = "<tr><th>Year</th><th>Months</th><th>Raw join</th><th>Harmonized</th></tr>" + ys.map(y => {
    const m = sel.filter(r => r.year === y), s = f => m.reduce((a, r) => a + f(r), 0);
    return `<tr><td>${y}</td><td>${m.length}</td><td>${fmt(s(rawJoin))}</td><td>${fmt(s(r => r.harmonized))}</td></tr>`; }).join("");
}

/* ---------- wiring ---------- */
function renderRange() { const sel = inRange(); renderStats(sel); buildHeat(sel); renderLine(sel); }
function setMode(m) {
  mode = m;
  $("btnHarm").setAttribute("aria-pressed", m === "harmonized");
  $("btnRaw").setAttribute("aria-pressed", m === "raw");
  paintHeat();
}
function init() {
  const ys = [...new Set(rows.map(r => r.year))], opts = ys.map(y => `<option>${y}</option>`).join("");
  $("from").innerHTML = opts; $("to").innerHTML = opts;
  $("from").value = ys[0]; $("to").value = ys[ys.length - 1];
  $("from").onchange = () => { if (+$("from").value > +$("to").value) $("to").value = $("from").value; renderRange(); };
  $("to").onchange = () => { if (+$("to").value < +$("from").value) $("from").value = $("to").value; renderRange(); };
  $("btnHarm").onclick = () => setMode("harmonized");
  $("btnRaw").onclick = () => setMode("raw");

  const latest = rows[rows.length - 1];
  $("latestTag").textContent = `Latest complete month: ${MONTHS_LONG[latest.month - 1]} ${latest.year}`;
  $("nowMonth").innerHTML = rows.map((r, i) => [r, i]).filter(([r]) => r.now_vs_normal != null && r.normal_10yr != null).reverse()
    .map(([r, i]) => `<option value="${i}">${MONTHS_LONG[r.month - 1]} ${r.year}${r.provisional ? " (provisional)" : ""}</option>`).join("");
  $("nowMonth").onchange = renderNow;

  renderLegend(); renderRange(); renderNow();
}
fetch(DATA_URL, {cache: "no-store"})
  .then(res => { if (!res.ok) throw new Error(res.status); return res.text(); })
  .then(text => { rows = parseCSV(text); if (!rows.length) throw new Error("empty"); init(); })
  .catch(() => { const e = $("error"); e.hidden = false;
    e.textContent = "Could not load " + DATA_URL + ". Open this page from GitHub Pages or a local web server, not by double-clicking the file."; });
