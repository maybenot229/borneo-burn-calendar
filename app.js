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
  const full = Object.entries(years).filter(([, o]) => o.n === 12).sort((a, b) => b[1].t - a[1].t);
  const top3 = est => full.filter(([, o]) => o.est === est).slice(0, 3)
    .map(([y]) => y + (est ? "*" : "")).join(", ") || "–";
  $("stats").innerHTML =
    `<div class="stat"><div class="k">Months that burn most</div>
       <div class="v">${top.map(x => MONTHS[x[1]]).join(", ")}</div>
       <div class="s">Highest median hotspots per calendar month, in the years selected.</div></div>
     <div class="stat"><div class="k">Worst years</div>
       <div class="v2"><span class="lbl">Measured (VIIRS):</span> ${top3(false)}</div>
       <div class="v2"><span class="lbl">Estimated from MODIS*:</span> ${top3(true)}</div>
       <div class="s">Highest yearly totals, full years only. * estimated from MODIS, less certain.</div></div>
     <div class="stat"><div class="k">Months in view</div>
       <div class="v">${sel.length}</div>
       <div class="s">${sel.filter(r => r.estimated).length} estimated from MODIS, ${sel.filter(r => !r.estimated).length} measured by VIIRS.</div></div>`;
}

/* ---------- helpers for the new cards ---------- */
const r1 = x => (Math.round(x * 10 + 1e-9) / 10).toFixed(1);
const ordinal = n => { const t = ["th", "st", "nd", "rd"], v = n % 100; return n + (t[(v - 20) % 10] || t[v] || t[0]); };
const classChip = c => `<span class="chip cls" style="background:${CLASS_BG[c]};color:${CLASS_FG[c]}">${CLASS_NAME[c]}</span>`;
const countWord = n => ["zero", "one", "two", "three", "four", "five", "six"][n] ?? String(n);
const monthYear = r => `${MONTHS_LONG[r.month - 1]} ${r.year}`;
const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function ratioOf(r) {                              // value compared with the usual for that calendar month
  const tenYr = r.normal_10yr != null, n = tenYr ? r.normal_10yr : r.normal_all_years;
  if (n == null || !n) return null;
  const x = tenYr && r.now_vs_normal != null ? r.now_vs_normal : r.harmonized / n;
  return {x, n, label: tenYr ? "10-year" : "all-years"};
}
const usualWord = x => x < 0.75 ? "below usual" : x <= 1.25 ? "close to usual" : x < 2 ? "above usual" : "well above usual";
const kindChip = (r, short) => r.provisional ? `<span class="chip badge">${short ? "Provisional" : "Provisional, may change"}</span>`
  : r.estimated ? '<span class="chip badge">Estimated from MODIS</span>' : '<span class="chip badge">Measured by VIIRS</span>';

/* ---------- status banner, date stamp ---------- */
function renderStatus() {
  const r = rows[rows.length - 1], c = cls(r.harmonized), q = ratioOf(r), last3 = rows.slice(-3);
  const uw = q ? usualWord(q.x) : "";
  const sentence = q ? `${uw[0].toUpperCase() + uw.slice(1)}: about ${r1(q.x)} times the usual for ${MONTHS_LONG[r.month - 1]} (${q.label} normal).`
                     : "No normal is available for this month.";
  $("status").innerHTML =
    `<p class="k">How is this month?</p>
     <h2 class="big">${monthYear(r)}</h2>
     <p class="line">${classChip(c)} <b>${fmt(r.harmonized)} hotspots</b> ${kindChip(r)}</p>
     <p>${sentence}</p>
     <p class="k">Last three months</p>
     <ul class="chips">${last3.map(m => { const mq = ratioOf(m), mc = cls(m.harmonized);
       return `<li class="chip cls" style="background:${CLASS_BG[mc]};color:${CLASS_FG[mc]}">${MONTHS[m.month - 1]} ${m.year}: ${CLASS_NAME[mc]}${mq ? `, about ${r1(mq.x)}× usual` : ""}${m.provisional ? ", provisional" : ""}</li>`; }).join("")}</ul>
     <p class="hint">Hotspot counts for the whole Sabah box. A planning tool, not live fire response.</p>`;
  let np = 0; for (let i = rows.length - 1; i >= 0 && rows[i].provisional; i--) np++;
  $("stamp").innerHTML =
    `<p class="big">Data through: ${monthYear(r)}</p>` +
    (np ? `<p>Latest ${countWord(np)} months are provisional</p>` : "") +
    `<p>${rows.length} months in the record, ${rows.filter(x => x.estimated).length} of them estimated from MODIS, from ${monthYear(rows[0])} to ${monthYear(r)}.</p>`;
}

/* ---------- calendar matrix (years down, months across) ---------- */
let cells = [], selected = null, tabCell = null;   // cells: [{b, r}]
const cellAt = new Map();
function buildHeat(sel) {
  const map = new Map(sel.map(r => [r.year + "-" + r.month, r]));
  const ys = [...new Set(sel.map(r => r.year))].reverse();      // newest on top
  const v0 = rows.find(r => !r.estimated), t = $("heat"); t.innerHTML = ""; cells = []; cellAt.clear();
  t.setAttribute("aria-label", "Hotspot class for each month, years down and months across");
  const thead = t.createTHead().insertRow();
  const corner = document.createElement("th"); corner.className = "y"; corner.textContent = "Year"; corner.scope = "col"; thead.appendChild(corner);
  MONTHS.forEach(m => { const th = document.createElement("th"); th.textContent = m; th.scope = "col"; thead.appendChild(th); });
  const body = t.createTBody();
  for (const y of ys) {
    const tr = body.insertRow(), th = document.createElement("th");
    th.className = "y"; th.scope = "row"; th.textContent = y; tr.appendChild(th);
    for (let m = 1; m <= 12; m++) {
      const td = tr.insertCell(), r = map.get(y + "-" + m);
      if (!r) { td.className = "none"; td.title = `${MONTHS_LONG[m - 1]} ${y}: no data`; continue; }
      const b = document.createElement("button");
      b.type = "button"; b.className = "cell"; b.tabIndex = -1; b.dataset.y = y; b.dataset.m = m;
      td.appendChild(b); cells.push({b, r}); cellAt.set(y + "-" + m, b);
    }
    if (v0 && y === v0.year && ys.includes(y - 1)) {              // line where VIIRS starts
      const dr = body.insertRow(); dr.className = "divider";
      const dc = dr.insertCell(); dc.colSpan = 13; dc.textContent = `VIIRS starts, ${MONTHS[v0.month - 1]} ${v0.year}`;
    }
  }
  const keep = selected && cells.find(c => c.r === selected);
  if (!keep) { selected = null; $("details").hidden = true; }
  tabCell = keep ? keep.b : (cells[0] && cells[0].b);
  if (tabCell) tabCell.tabIndex = 0;
  paintHeat();
}
function paintHeat() {
  for (const {b, r} of cells) {
    const v = value(r), c = cls(v), est = mode === "harmonized" && r.estimated;
    b.style.backgroundColor = CLASS_BG[c]; b.style.color = CLASS_FG[c];
    b.textContent = CLASS_NAME[c][0];
    b.className = "cell" + (est ? " est" : "") + (r.provisional ? " prov" : "") + (r === selected ? " sel" : "");
    const kind = mode === "harmonized" ? (r.estimated ? "estimated from MODIS" : "measured by VIIRS")
                                       : (r.estimated ? "MODIS raw count" : "VIIRS raw count");
    b.setAttribute("aria-label", `${monthYear(r)}: ${CLASS_NAME[c]}, ${fmt(v)} hotspots (${kind}${r.provisional ? ", provisional" : ""})`);
    b.title = b.getAttribute("aria-label");
  }
  $("heatHint").textContent = mode === "harmonized"
    ? "Harmonized: every month is in VIIRS-equivalent hotspots, so years can be compared fairly. Each cell shows its class letter (L, M, H, V). Tap a cell for details."
    : "Raw join: MODIS counts before February 2012, VIIRS counts after. Early years look quiet only because the older sensor saw less. Tap a cell for details.";
}
function renderLegend() {
  const range = ["under " + EDGES[0], `${EDGES[0]}–${EDGES[1] - 1}`, `${EDGES[1]}–${EDGES[2] - 1}`, EDGES[2] + " or more"];
  $("legend").innerHTML = CLASS_NAME.map((n, i) =>
      `<span class="li"><span class="sw" style="background:${CLASS_BG[i]};color:${CLASS_FG[i]}">${n[0]}</span>${n} (${range[i]})</span>`).join("") +
    `<span class="li"><span class="sw est"></span>Estimated from MODIS</span>
     <span class="li"><span class="sw prov"></span>Provisional</span>
     <span class="li"><span class="sw none"></span>No data</span>`;
}

/* ---------- details panel ---------- */
function showDetails(r, scroll) {
  selected = r;
  const c = cls(r.harmonized), q = ratioOf(r), same = rows.filter(x => x.month === r.month);
  const rank = 1 + same.filter(x => x.harmonized > r.harmonized).length;
  const mName = MONTHS_LONG[r.month - 1];
  const sentence = `${monthYear(r)}: ${CLASS_NAME[c]}.` + (q ? ` About ${r1(q.x)} times the usual ${mName}.` : "");
  const p = $("details");
  p.innerHTML =
    `<div class="dhead"><p class="dsent">${sentence}</p><button type="button" class="close" id="dClose">Close (Esc)</button></div>
     <p><b>${fmt(r.harmonized)} hotspots</b> ${classChip(c)} ${kindChip(r, true)}</p>
     <ul>
       <li>MODIS count: ${fmt(r.modis_raw)}${r.viirs != null ? `. VIIRS count: ${fmt(r.viirs)}` : ". VIIRS count: none (before VIIRS started)"}.</li>
       <li>${q ? `Normal used: ${fmt(q.n)} hotspots (${q.label} normal${q.label === "all-years" ? ", because there is no 10-year normal for this month" : ""}).` : "No normal available."}</li>
       <li>${rank === 1 ? "Highest" : ordinal(rank) + " highest"} of ${same.length} ${mName}${mName.endsWith("h") ? "es" : "s"} in the record.</li>
       ${r.estimated ? "<li>Estimated: scaled from MODIS. Less certain, especially in quiet months.</li>" : ""}
     </ul>`;
  p.hidden = false;
  p.classList.remove("fade"); void p.offsetWidth; p.classList.add("fade");
  $("dClose").onclick = closeDetails;
  paintHeat();
  const hit = cells.find(x => x.r === r);
  if (hit) { if (tabCell) tabCell.tabIndex = -1; tabCell = hit.b; hit.b.tabIndex = 0;
    if (scroll) hit.b.scrollIntoView({block: "center", inline: "center", behavior: reduceMotion() ? "auto" : "smooth"}); }
  p.focus({preventScroll: true});
  if (!scroll) p.scrollIntoView({block: "nearest", behavior: reduceMotion() ? "auto" : "smooth"});
}
function closeDetails() {
  const r = selected; selected = null; $("details").hidden = true; paintHeat();
  const hit = r && cells.find(x => x.r === r); if (hit) hit.b.focus();
}
function wireHeat() {
  $("heat").addEventListener("click", e => {
    const b = e.target.closest("button.cell"); if (!b) return;
    const hit = cells.find(x => x.b === b); if (hit) showDetails(hit.r, false);
  });
  $("heat").addEventListener("keydown", e => {            // arrow keys move between cells
    const b = e.target.closest("button.cell"); if (!b) return;
    let y = +b.dataset.y, m = +b.dataset.m;
    if (e.key === "ArrowLeft") m--; else if (e.key === "ArrowRight") m++;
    else if (e.key === "ArrowUp") y++; else if (e.key === "ArrowDown") y--;
    else if (e.key === "Home") m = 1; else if (e.key === "End") m = 12; else return;
    e.preventDefault();
    const nb = cellAt.get(y + "-" + m);
    if (nb) { b.tabIndex = -1; nb.tabIndex = 0; tabCell = nb; nb.focus(); }
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { if (!$("details").hidden) closeDetails(); $("termOut").textContent = "";
      $("terms").querySelectorAll("button.term").forEach(x => x.setAttribute("aria-expanded", "false")); }
  });
}

/* ---------- critical burning windows ---------- */
let winView = "all";
function windowYears(measuredOnly) {
  const by = {};
  rows.forEach(r => (by[r.year] ??= []).push(r));
  return Object.entries(by).filter(([, a]) => a.length === 12 && !a.some(r => r.provisional) && (!measuredOnly || !a.some(r => r.estimated)))
    .map(([y]) => +y);
}
function runsText(ms) {                                   // [3,4,5,6,7,8,9,10] -> "March to October"
  const runs = []; ms.forEach(m => { const l = runs[runs.length - 1]; if (l && l[1] === m - 1) l[1] = m; else runs.push([m, m]); });
  const t = runs.map(([a, b]) => a === b ? [MONTHS_LONG[a - 1]] : b === a + 1 ? [MONTHS_LONG[a - 1], MONTHS_LONG[b - 1]] : [`${MONTHS_LONG[a - 1]} to ${MONTHS_LONG[b - 1]}`]).flat();
  return t.length > 1 ? t.slice(0, -1).join(", ") + " and " + t[t.length - 1] : t[0];
}
function renderWindows() {
  const all = windowYears(false), meas = windowYears(true);
  const rng = a => a.length ? `${Math.min(...a)} to ${Math.max(...a)}` : "none";
  const labels = {all: `All years, ${rng(all)}`, meas: `Measured years only, ${rng(meas)}`};
  $("winToggle").innerHTML = ["all", "meas"].map(k => `<button type="button" data-v="${k}" aria-pressed="${winView === k}">${labels[k]}</button>`).join("");
  $("winToggle").querySelectorAll("button").forEach(bt => bt.onclick = () => { winView = bt.dataset.v; renderWindows(); });
  const ys = new Set(winView === "all" ? all : meas), N = ys.size;
  $("winNote").textContent = winView === "all"
    ? `Complete years only; 2026 and provisional months are left out. Years before ${rows.find(r => !r.estimated).year} are estimates from MODIS.`
    : "Measured years only: every estimated month is left out. Compare with the all-years view: fewer months qualify.";
  const stat = MONTHS.map((_, i) => { const v = rows.filter(r => ys.has(r.year) && r.month === i + 1).map(r => r.harmonized);
    return {n: v.filter(x => x >= EDGES[1]).length, med: median(v)}; });
  $("winBars").innerHTML = stat.map((s, i) => { const win = N && s.n * 2 >= N;
    return `<li class="${win ? "win" : ""}"><span class="m">${MONTHS[i]}</span>
      <span class="track"><span class="fill" style="--p:${N ? s.n / N * 100 : 0}%"></span></span>
      <span class="n">${s.n} of ${N} years</span><span class="med">median ${fmt(s.med)}</span>${win ? '<span class="tag">window</span>' : ""}</li>`; }).join("");
  const wm = stat.map((s, i) => N && s.n * 2 >= N ? i + 1 : 0).filter(Boolean);
  $("winSentence").textContent = wm.length
    ? `Likely burning window: ${runsText(wm)}. These months reached High or Very high (${EDGES[1]} or more hotspots) in at least half of the years.`
    : "No month reached High or Very high in at least half of the years.";
}

/* ---------- unusual months ---------- */
function renderUnusual(sel) {
  const list = sel.filter(r => !r.provisional && r.normal_10yr != null && r.now_vs_normal != null && r.harmonized >= EDGES[0])
    .sort((a, b) => b.now_vs_normal - a.now_vs_normal).slice(0, 8);
  $("unusualList").innerHTML = list.length ? list.map(r =>
    `<li><button type="button" class="row" data-i="${rows.indexOf(r)}"><span class="when">${MONTHS[r.month - 1]} ${r.year}</span>
       ${classChip(cls(r.harmonized))}<span>${fmt(r.harmonized)} hotspots</span><span><b>${r1(r.now_vs_normal)}</b> times usual</span>
       <span class="chip badge">${r.estimated ? "Estimated" : "Measured"}</span></button></li>`).join("")
    : "<li>No months match in this range.</li>";
  $("unusualList").querySelectorAll("button.row").forEach(bt => bt.onclick = () => showDetails(rows[+bt.dataset.i], true));
  $("unusualNote").textContent = "Months with no 10-year normal (the first years of the record), provisional months and months under " +
    EDGES[0] + " hotspots are left out. Estimated months are less certain.";
}

/* ---------- glossary ---------- */
const TERMS = {
  "hotspot": "A satellite detection of heat on the ground. It is not burned area.",
  "MODIS": "The older NASA sensors (Terra and Aqua), in our record from 2003.",
  "VIIRS": "The newer sensor on Suomi NPP. It sees more small, isolated hotspots.",
  "ratio": "About 4.95: how many more hotspots VIIRS counts than MODIS in Sabah.",
  "colour class": "Low, Medium, High or Very high, set by the number of hotspots in a month.",
  "provisional": "Near-real-time data that may still change.",
  "estimated": "Scaled up from MODIS using the ratio, not measured by VIIRS."
};
function renderTerms() {
  $("terms").innerHTML = "<span class=\"lbl\">Terms:</span> " + Object.keys(TERMS).map(t =>
    `<button type="button" class="term" aria-expanded="false" data-t="${t}">${t}</button>`).join(" ");
  $("terms").onclick = e => { const b = e.target.closest("button.term"); if (!b) return;
    const open = b.getAttribute("aria-expanded") === "true";
    $("terms").querySelectorAll("button.term").forEach(x => x.setAttribute("aria-expanded", "false"));
    b.setAttribute("aria-expanded", String(!open));
    $("termOut").textContent = open ? "" : `${b.dataset.t}: ${TERMS[b.dataset.t]}`; };
}

/* ---------- now vs normal ---------- */
function renderNow() {
  const r = rows[+$("nowMonth").value];
  if (!r) return;
  const x = r.now_vs_normal;
  const uw = usualWord(x), word = [x < 0.75 ? "below" : x <= 1.25 ? "near" : "above", uw[0].toUpperCase() + uw.slice(1)];
  $("nowBox").innerHTML =
    `<span class="big">${x.toFixed(2)}× normal</span>
     <span class="word ${word[0]}">${word[1]}</span>
     ${r.provisional ? '<span class="badge">Provisional</span>' : ""}
     ${r.estimated ? '<span class="badge">Estimated from MODIS</span>' : ""}
     <p>${MONTHS_LONG[r.month - 1]} ${r.year}: ${fmt(r.harmonized)} hotspots.
        Normal for ${MONTHS_LONG[r.month - 1]}: ${fmt(r.normal_10yr)}.
        "Close to usual" means between 0.75 and 1.25 times the median.</p>`;
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

/* ---------- headline finding (all numbers computed from the CSV) ---------- */
function yearlyAvg(fn, a, b) {                    // average of yearly totals, full years only
  const t = {};
  rows.forEach(r => { if (r.year >= a && r.year <= b) { const v = fn(r);
    (t[r.year] ??= {s: 0, n: 0, bad: false}); if (v == null) t[r.year].bad = true; else t[r.year].s += v; t[r.year].n++; } });
  const ys = []; for (let y = a; y <= b; y++) ys.push(t[y]);
  if (ys.some(o => !o || o.n !== 12 || o.bad)) return NaN;   // missing/partial year: refuse to guess
  return ys.reduce((s, o) => s + o.s, 0) / ys.length;
}
function headlineStats() {
  const chg = (late, early) => (yearlyAvg(late, 2012, 2025) / yearlyAvg(early, 2003, 2011) - 1) * 100;
  return {
    raw: Math.round(chg(r => r.viirs, r => r.modis_raw)),
    harm: Math.round(chg(r => r.harmonized, r => r.harmonized)),
    modis: Math.round(chg(r => r.modis_raw, r => r.modis_raw))
  };
}
function renderHeadline() {
  const box = $("headline");
  try {
    const s = headlineStats();
    if (![s.raw, s.harm, s.modis].every(Number.isFinite)) throw new Error("bad numbers");
    const rawWord = (s.raw >= 90 && s.raw <= 110) ? "doubled"
                  : s.raw >= 0 ? `rose by ${s.raw}%` : `fell by ${Math.abs(s.raw)}%`;
    const harmWord = s.harm < 0 ? `fell by about ${Math.abs(s.harm)}%` : `rose by about ${s.harm}%`;
    const modisTxt = (s.modis > 0 ? "+" : s.modis < 0 ? "−" : "") + Math.abs(s.modis) + "%";
    const modisWord = s.modis < 0 ? "the same fall" : "a different result";
    const l1 = `Joined as-is, the two satellites say Sabah's fire hotspots ${rawWord} after 2012. Harmonized, they ${harmWord}.`;
    const l2 = `Average per year, 2003-2011 against 2012-2025. MODIS alone, with no ratio, shows ${modisWord} (${modisTxt}).${s.modis < 0 ? " This follows from the arithmetic, so it is not an independent check of the ratio." : ""} Pre-2012 values are estimates.`;
    $("headLine1").textContent = l1; $("headLine2").textContent = l2;
    $("headAlt1").textContent = l1; $("headAlt2").textContent = l2;
    const sg = v => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v) + "%";
    $("headTable").innerHTML = "<tr><th>Measure</th><th>Change, 2003-2011 to 2012-2025 (average per year)</th></tr>" +
      `<tr><td>Raw join</td><td>${sg(s.raw)}</td></tr><tr><td>Harmonized</td><td>${sg(s.harm)}</td></tr><tr><td>MODIS alone</td><td>${sg(s.modis)}</td></tr>`;
    $("headTextAlt").hidden = false;
    box.hidden = false;
    window.HEADLINE_STATS = s;
  } catch (e) { box.hidden = true; $("headTextAlt").hidden = true; }
}

/* ---------- wiring ---------- */
function renderRange() { const sel = inRange(); renderStats(sel); buildHeat(sel); renderLine(sel); renderUnusual(sel); }
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

  renderLegend(); renderStatus(); wireHeat(); renderTerms(); renderWindows(); renderRange(); renderNow(); renderHeadline();
}
fetch(DATA_URL, {cache: "no-store"})
  .then(res => { if (!res.ok) throw new Error(res.status); return res.text(); })
  .then(text => { rows = parseCSV(text); if (!rows.length) throw new Error("empty"); init(); })
  .catch(() => { const e = $("error"); e.hidden = false;
    e.textContent = "Could not load " + DATA_URL + ". Open this page from GitHub Pages or a local web server, not by double-clicking the file."; });
