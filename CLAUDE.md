# CLAUDE.md

Instructions for Claude Code in this repository. Read this fully before changing anything.

## 1. What this project is

**Borneo Burn Calendar**, by team **SpaceZY**, for the NASA Space Apps Challenge 2026.
Challenge: *Harmonization of MODIS and VIIRS Hot Spots*.

It joins two NASA fire-hotspot records for Sabah, Malaysia into one monthly record, 2003 to 2026, so the years before and after 2012 can be compared fairly. MODIS and VIIRS count fires differently. Joined as-is, the record shows a fake jump at 2012.

- Live site: https://maybenot229.github.io/borneo-burn-calendar/
- Repo: https://github.com/maybenot229/borneo-burn-calendar (public)
- Hosting: GitHub Pages serves the `main` branch root. **Every push to `main` changes the live site within about 2 minutes.**
- Submission deadline: Sunday 15 November 2026, 23:59 Malaysia time. Before it, make small safe changes only. After it, ask before changing anything.

## 2. How to work with the team

- Give the result first. Then the reason, only if needed.
- Use short, plain sentences. The team are students and new to git.
- Give git and terminal steps one at a time, with the exact command.
- Say clearly when you are not sure. Never state a guess as a fact.
- Never invent a source, a number or a quote.
- Before a change bigger than about 30 lines, say what you plan and wait for a yes.

## 3. Hard rules

1. **Do not change the method or any verified number** (section 7) unless asked. If a number looks wrong, stop and report it. Do not "fix" it.
2. **No raw FIRMS files, no API keys (FIRMS MAP_KEY), no backups** in the repo. Raw data stays on the laptop.
3. **No photos, video or voices of people.** Team members are under 18.
4. **Keep the AI-use notes.** They are in `README.md`, the `index.html` comment and footer, and the `app.js` header. Keep them accurate. Do not remove or soften them.
5. **No build step, no framework, no npm, no CDN.** The site is plain HTML, CSS and JavaScript.
6. **Numbers on the page come from the CSV at run time.** Do not hard-code a number that the CSV can supply.
7. **Ask before `git push`.** Never force-push. Never rewrite history.
8. **Do not edit `data/sabah_harmonized_monthly.csv` by hand.** The notebooks produce it.
9. Stay inside this folder. Do not touch other folders, notes apps or settings.

## 4. Repository map

| Path | What it is |
|---|---|
| `index.html` | The one page. Sections: headline, controls, summary cards, calendar, now vs normal, Proof 1, Proof 2, results, how it works, limits. |
| `app.js` | All logic. Loads the CSV, draws everything. About 220 lines. |
| `style.css` | All styling. |
| `data/sabah_harmonized_monthly.csv` | The harmonized record. The only data the site reads. |
| `img/` | `chart_raw_vs_harmonized.png`, `chart_holdout_test.png`. Charts only. |
| `notebooks/` | `harmonization_steps_2_to_5.ipynb`, `harmonization_steps_6_to_9.ipynb`. They build the CSV and the charts from raw FIRMS files. |
| `analysis/method_checks.py` | Tests of other methods against the fixed ratio. Needs the raw files, which are not in the repo. |
| `analysis/fig_three_panel.py` | Draws the "why the sensors differ" figure. |
| `experiment_b/` | `REPORT.md` and `experiment_b.ipynb`. Detection-level study of Aqua vs Suomi NPP. |
| `README.md` | Project summary, method, limits, AI use. |

## 5. Website internals (`app.js`)

- `parseCSV(text)` reads the CSV. It adds `estimated` to each row: true when `viirs` is empty or `harmonized !== viirs`. So `estimated` means "scaled MODIS, not a VIIRS measurement".
- `value(r)` returns `harmonized`, or the raw join when the toggle is on "Raw join". Raw join = MODIS when estimated, VIIRS otherwise.
- `EDGES = [74, 204, 376]` are the colour-class edges (Low, Medium, High, Very high). They come from the analysis. Do not change them.
- `renderStats(sel)` draws the three summary cards for the selected year range.
- `buildHeat` / `paintHeat` draw the calendar. `renderNow` draws "Now vs normal". `renderLine` draws the Proof 1 chart as inline SVG.
- `headlineStats()` / `renderHeadline()` compute the headline from the CSV. If any number is not finite, the headline hides itself. Keep that behaviour.
- The page fails safely: if the CSV cannot load, it shows an error line.

**Run it locally.** Opening `index.html` by double-click does not work, because `fetch` needs a server.

```
python -m http.server 8000
```

Then open http://localhost:8000 and check the browser console for errors.

## 6. Data contract (`data/sabah_harmonized_monthly.csv`)

286 rows, January 2003 to October 2026, one row per month.

| Column | Meaning |
|---|---|
| `year`, `month` | Calendar month. |
| `modis_raw` | Cleaned MODIS count (Terra + Aqua). |
| `viirs` | Cleaned VIIRS S-NPP count. Empty before 2012. |
| `modis_adjusted` | `modis_raw` × ratio (about 4.947). |
| `harmonized` | `viirs` from February 2012, `modis_adjusted` before. |
| `normal_10yr` | Median of the same calendar month over up to 10 earlier years. |
| `now_vs_normal` | `harmonized` ÷ `normal_10yr`. |
| `normal_all_years` | Median of the same calendar month, all years. |
| `provisional` | `True` for near-real-time months (August to October 2026). |

Cleaning rules used upstream: FIRMS archive data, `type == 0`, MODIS confidence ≥ 30, VIIRS confidence `n` or `h`. Area: latitude 4.0 to 7.5, longitude 115.3 to 119.3.

## 7. Verified numbers (source of truth)

Use these exact values and this exact wording. If the site and a document disagree, the site wins, because it computes from the CSV.

**Method**
- Ratio: VIIRS sees about **4.95** times more hotspots than MODIS in Sabah.
- Learned on February 2012 to December 2018 (83 months). Tested on 2019 to 2025 (84 months).
- Test result: about **24%** total error (24.3%). Colour class agrees **86%** of the time (72 of 84 months).
- With no correction the error is about 80%.
- Quiet months: the ratio under-predicts VIIRS by about **16%** in the quietest quarter.

**Headline (average hotspots per year, 2003–2011 against 2012–2025)**

| Record | 2003–2011 | 2012–2025 | Change |
|---|---:|---:|---:|
| Raw join (MODIS then VIIRS) | 1,267 | 2,538 | +100% ("doubled") |
| Harmonized | about 6,270 | about 2,540 | **about −59%** |
| MODIS alone, no ratio | 1,267 | 515 | −59% |

Always write "**about 59%**". Never 60%.

**Other methods tested (same split) and rejected**
- Per-calendar-month ratio 31.8% error. Power law 25.9%. Straight line 23.5%. Per-region ratio 24.1%.
- Base + ratio 21.7% error, but it over-predicts quiet months by 56%, so it failed the rule set in advance.
- Decision: **keep the fixed ratio**. Do not reopen this.

**Experiment B (Aqua vs Suomi NPP, daytime, 2012–2022, within 15 minutes)**
- 4,321 Aqua and 24,823 S-NPP detections. 1,643 S-NPP matched (6.6%). This is not a detection rate.
- Where Aqua saw a fire: matched VIIRS pixels have median fire power 9.0 MW, VIIRS-only 5.6 MW. Lone-pixel share 25% against 54%.
- Quietest months have 64% lone VIIRS pixels, busiest 44%.
- Match rate in quiet against busy months could not be told apart (n = 86). Make no claim either way.
- Aqua's overpass drifted from about 05:40 to 07:28 UTC after 2022.

## 8. Wording rules

- Hotspots are **not** burned area. Never say "area burned" or "fires fell". Say "hotspots" or "detections".
- Values before February 2012 are **estimates**. Mark them where they appear.
- FIRMS lists detections only. "VIIRS-only" does **not** mean MODIS failed. Do not write "MODIS misses small fires" as a fact. Write "VIIRS detects more small, isolated fires".
- The ratio is shown for **Sabah only**. Do not claim it works elsewhere.
- The record starts in 2003, because only one MODIS satellite flew before mid-2002.
- This is a planning tool, not live fire response.
- August to October 2026 is provisional.
- Keep the "Limits" list on the page. Add to it, never trim it.

## 9. Checking your work

Before you say a change is done:

1. Run the local server and load the page. No console errors.
2. The headline reads "doubled" and "fell by about 59%".
3. The calendar, the toggle, the year range and the CSV download still work.
4. Check a narrow screen (360 px wide). Nothing overflows.
5. Text stays readable without colour. Do not carry meaning by colour alone.
6. Run `git status` and `git diff`. Show the list of changed files.

## 10. Git

- Branch: `main`. A push to `main` is a deploy.
- Small, clear commit messages. One change per commit.
- Steps to give the team:

```
git add .
git commit -m "Short message"
git push
```

- After a push, tell the team to wait 2 minutes, then hard refresh the site (Ctrl+F5) in a private window.

## 11. Open task: fix the "Worst years" card

**Status:** not done. Do it only when asked.

**Where:** `renderStats(sel)` in `app.js`, the second summary card. Small CSS additions in `style.css` if needed.

**Problem:** the card ranks all full years by harmonized total. For the full range it shows `2005*, 2004*, 2003*`. All three are estimates from MODIS. A reader may take them as measured, and the measured record is hidden.

**Change:** show two short lines in the same card.

1. **Measured (VIIRS):** top 3 full years where no month is estimated.
2. **Estimated from MODIS\*:** top 3 full years where at least one month is estimated.

Rules:
- A "full year" has 12 rows in the selected range. 2026 is never a full year.
- Rank by the sum of `harmonized`, as now. The Harmonized / Raw join toggle does not affect this card.
- 2012 counts as estimated, because January 2012 is estimated.
- If a group has no full year in the selected range, show `–` for that line.
- Caption: `Highest yearly totals, full years only. * estimated from MODIS, less certain.`
- Compute everything from the rows. Hard-code no year.
- Do not change the other two cards, the headline or the CSV.

**Expected results (use these to test):**

| Selected range | Measured line | Estimated line |
|---|---|---|
| 2003–2026 (default) | 2016, 2015, 2014 | 2005*, 2004*, 2003* |
| 2013–2025 | 2016, 2015, 2014 | – |
| 2003–2011 | – | 2005*, 2004*, 2003* |

Yearly totals behind this: 2016 = 7,445; 2015 = 5,335; 2014 = 3,950; 2005 = 10,384; 2004 = 9,934; 2003 = 7,930; 2012 = 2,516.

**Done when:** the three test ranges match the table, the card fits at 360 px width, the console is clean, and section 9 passes. Then show the diff and wait. Do not push.

## 12. Out of scope

Do not start these unless asked:
- Other regions or a global version. The ratio is not tested outside Sabah.
- A new harmonization method.
- Live FIRMS API calls from the page.
- Redesigning the page.
