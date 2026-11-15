# Borneo Burn Calendar

**One consistent monthly fire record for Sabah, Malaysia, built from NASA's MODIS and VIIRS hotspots. Team SpaceZY, NASA Space Apps Challenge 2026 (Local Event: Johor, Malaysia). Challenge: Harmonization of MODIS and VIIRS Hot Spots.**

**Live site:** https://maybenot229.github.io/borneo-burn-calendar/

For land managers and plantation staff planning their fire season. It is a planning tool, not live fire response.

## The problem
MODIS (since 2000) and VIIRS 375 m (since 2012) count fire hotspots differently. VIIRS has smaller pixels and counts about five times more. Joined directly, the record shows a fake jump at 2012.

## The result
Average hotspots per year, Sabah box, 2003–2011 against 2012–2025:

| Record | 2003–2011 | 2012–2025 | Change |
|---|---:|---:|---:|
| Raw join (MODIS, then VIIRS) | 1,267 | 2,538 | +100% |
| Harmonized (MODIS × 4.95, then VIIRS) | about 6,270 | about 2,540 | about −59% |
| MODIS alone, no ratio | 1,267 | 515 | −59% |

Joined as-is, hotspots look like they doubled. Harmonized, they fell by about 59%. MODIS alone shows the same fall. That follows from the arithmetic, so it is not an independent check of the ratio. It shows the fall comes from the MODIS record itself. The ratio puts both eras on one scale and removes the fake doubling. The 2003–2011 harmonized values are estimates. This is a change in estimated hotspot counts, not burned area.

## What the site shows
- **Status of the latest month.** Class (Low, Medium, High, Very high), hotspot count, and how it compares with the usual for that month.
- **Burning activity calendar.** Every month from January 2003 to October 2026 in one grid. Tap a month for its counts, its rank and how it was measured.
- **Critical burning windows.** How often each calendar month reached High or Very high. Two views: all years, and measured years only (2013 to 2025). The clear March to October season leans on the estimated years. In measured years only March, July and August qualify.
- **Most unusual months.** The months furthest above their usual level.
- **How sure are we.** What we tested, what held up, and what we cannot know.
- **Use this for your region.** Three steps to build your own ratio. Our ratio is for Sabah only.

Hatched cells are estimates from MODIS (before February 2012). Dashed cells are provisional (August to October 2026). The site is history for planning, not a forecast and not live data.

## Method
1. Download MODIS C6.1 and VIIRS S-NPP 375 m archive data from NASA FIRMS for the Sabah box (lat 4.0–7.5, lon 115.3–119.3).
2. Clean both: vegetation fires only (`type` = 0), MODIS confidence 30 or more, VIIRS nominal or high.
3. Count hotspots per month.
4. In the overlap years (Feb 2012 on), compute the VIIRS-to-MODIS ratio as a ratio of sums. Final value: about 4.95.
5. Scale MODIS counts by the ratio to get VIIRS-equivalent counts from 2003.
6. Compute "now vs normal" as a month against the median of the same calendar month over the previous 10 years.

The record starts in 2003. Only Terra flew before mid-2002 and its orbit changes make the early years unreliable.

## How we tested it
Learn on Feb 2012 – Dec 2018 (83 months), test on 2019–2025 (84 months).

| Check | Result |
|---|---|
| Total error on test years | about 24% |
| Same colour class (4 classes) | 86% (72 of 84 months) |
| Backward test (learn 2019–2025, test 2012–2018) | ratio 4.96, 18% error |

We also tested other methods on the same split:

| Method | Total error |
|---|---:|
| Ratio per calendar month | 31.8% |
| Power law | 25.9% |
| **Fixed ratio (used)** | **24.3%** |
| Ratio per quadrant of Sabah | 24.1% |
| Straight line | 23.5% |
| Base plus ratio | 21.7% |

None clearly beat the simple ratio. The seasonal ratio pattern does not repeat between training and test years, and the best-scoring alternative over-predicts the quietest months. The test years were used for several methods, so differences of 1 to 3 points should not be over-read. Details: `analysis/method_checks.py`.

## Robustness checks
On 15 November 2026 we ran four extra checks. They do not change the method or the numbers on the website. Details, tables and figures: `robustness/REPORT.md`.

| Check | Result |
|---|---|
| Ratio year by year, 2012–2025 | Between 4.2 and 6.1, no clear trend. Highest in the quietest years. |
| How sure is the 59% fall | A fall in every check. Ratio uncertainty alone gives −57% to −61%. Dropping any one year gives −56% to −66%. |
| Terra only, Aqua only | Terra + Aqua is best (24% error). Aqua only 28%. Terra only 46%. |
| Other confidence filters | Error stays at 24–25%. The ratio itself moves from 4.6 to 6.0. |

What these checks tell us:
- The direction of the fall is robust. Its size is less certain. Treating the years as a sample gives a wide range, about −35% to −75%, and it rests on only nine early years.
- The ratio before 2012 cannot be tested. It would have to be 2.0 for the fall to vanish. The lowest yearly ratio we measured is 4.2.
- The ratio of about 4.95 holds only for our confidence filters.

## Why the sensors differ (Experiment B)
We matched Aqua and Suomi NPP detections, 2012–2022, daytime. VIIRS detections with no Aqua partner are weaker (median power 5.6 MW against 9.0 MW) and more often single pixels (54% against 25%). Quiet months have more of them. This fits small fires, VIIRS false alarms or missing Aqua coverage. The data cannot say which, and it does not show that MODIS "missed" fires. Full report: `experiment_b/REPORT.md`.

## Limits
- FIRMS lists detections only. It cannot show where a satellite looked and saw nothing.
- Hotspots are not burned area.
- Values before Feb 2012 are estimates from MODIS. The method is reliable for colour class, ranking and season shape, not for exact single-month counts.
- Quiet months are less certain: the ratio under-predicts VIIRS there by about 16%.
- Aqua's overpass drifted after 2022 (about 05:40 to 07:28 UTC by 2026), so the two sensors see fires at different times of day. Terra drifted too, the other way (about 02:55 to 01:43 UTC by 2025).
- The size of the 59% fall depends on which years are included, and the pre-2012 ratio cannot be tested. The ratio of about 4.95 holds only for our confidence filters.
- The ratio is proven for the Sabah box only, which also covers parts of neighbouring regions. A region cut in four showed ratios between about 4.4 and 6.1, so the ratio is not the same everywhere.
- August to October 2026 uses near-real-time data and is provisional.

## Repository
| Path | What |
|---|---|
| `index.html`, `app.js`, `style.css` | The website (plain HTML and JavaScript, no build step) |
| `data/sabah_harmonized_monthly.csv` | The monthly record, with "now vs normal" |
| `notebooks/` | Google Colab notebooks: Steps 2–5 (load, clean, count, overlap) and Steps 6–9 (ratios, hold-out test, charts, final CSV) |
| `analysis/method_checks.py` | Reruns the method comparison, seasonal, quiet-month and regional checks |
| `experiment_b/` | Aqua against S-NPP detection-level experiment: notebook and report |
| `robustness/` | Four robustness checks: script, report, tables and figures |

To rerun: download the raw files from NASA FIRMS (https://firms.modaps.eosdis.nasa.gov/download/) with the Sabah box and the products above, then run the notebooks in order. The raw files are not included in this repository.

## Data
NASA FIRMS: MODIS Collection 6.1 (Terra and Aqua) and VIIRS 375 m Collection 2 (Suomi NPP). Sabah box, Nov 2000 to Oct 2026. No other data.

## AI use
We used Claude (Anthropic) to explain methods step by step, write and run analysis code in Google Colab and Claude Code, check results, and draft text and website code. A second AI model reviewed some experiments. The team ran the code on our own data and reviewed the results.
The project idea and direction were chosen by Kang Juwon with team SpaceZY.

## Team
SpaceZY. NASA Space Apps Challenge 2026.
Kang Juwon: harmonization, analysis and website. Two teammates: slides and design.
