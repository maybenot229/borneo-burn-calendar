AI use: code and draft text produced with Claude (Anthropic), directed and reviewed by the team.

# Experiment B — Why do MODIS and VIIRS hotspot counts differ in Sabah?

NASA Space Apps Challenge 2026, "Harmonization of MODIS and VIIRS Hot Spots". Study area: the Sabah box (lat 4.0–7.5, lon 115.3–119.3), a rectangle, not the state border.

> [!warning] Scope of every matching result below
> **Aqua vs S-NPP only, daytime, 2012–2022, 15-minute window.** The earlier count-level ratios (6.73 → 4.79) use **Terra + Aqua**; this experiment does not use Terra, so the two are never equated. Night results are in Appendix A as indicative only. 2023 onward is excluded from the matching conclusions (Aqua's overpass drifted, see Results 2). Every table below states its day/night scope; the original pooled day + night Section 6.2 table is kept in Appendix C.

## 1. Question
Why does VIIRS report more hotspots than MODIS, and why does the gap widen in quiet months? Specifically: can differences between individual Aqua and S-NPP detections help explain why the MODIS–VIIRS ratio changes with fire activity?

## 2. Hypothesis
VIIRS detections with no corresponding Aqua detection are disproportionately small or weak fires, and quiet months contain a larger share of them. This was a hypothesis to be tested, not assumed. Section 6 says what the data does and does not support.

## 3. Data
Three files in `data/`, none modified: raw MODIS (25,985 rows; Aqua 17,272, Terra 8,713), raw VIIRS S-NPP (50,741 rows) and `monthly_counts.csv`. Cleaning rules as in all earlier work: `type == 0`; MODIS `confidence >= 30`; VIIRS `n` or `h`; Feb 2012 onward; **archive rows only** (near-real-time rows dropped). Common archive window ends 31 Jul 2026 (the VIIRS archive ends there). Analysed (day + night pooled): **5,381 Aqua** and **36,328 S-NPP** detections (cleaned Aqua is 5,415 before the end date is applied; the 34 Aqua rows from Aug 2026 fall after the VIIRS archive ends and are excluded); primary period 2012–2022: 4,553 Aqua and 31,005 S-NPP detections **(day + night pooled)**, of which **day 4,321 Aqua and 24,823 S-NPP**, and night 232 Aqua and 6,182 S-NPP. Full window by scope: day 5,111 Aqua and 29,279 S-NPP; night 270 and 7,049.

## 4. Data quality
- Row counts, date ranges, satellite split and near-real-time counts (MODIS 69, VIIRS 647) match the earlier verified facts. No exact duplicates and no duplicates on (lat, lon, date, time, satellite) in either file (re-confirmed). Removing coordinates duplicated at 0.001° removed 134 VIIRS and 0 Aqua rows and changed no result.
- Only `type` has missing values (the near-real-time rows). The day/night flag agrees with the UTC hour. No archive and near-real-time rows share a date.
- **Aqua's overpass drifted.** Aqua's median daytime pass was 05:37–05:43 UTC in 2012–2022, then 05:54 (2023), 06:11 (2024), 06:56 (2025) and 07:28 (2026). S-NPP stayed near 05:41. The daytime signed gap (Aqua minus S-NPP) has median +1 min in 2012–2022 and +46 min after (night: +8 and +46 min, small samples). `figures/fig_overpass_gap_hist.png` shows day (left panel) and night (right panel) separately; no pooling.
- Hotspot-bearing passes last about 0–1 min within the box.

## 5. Method
**Timing first (Phase 1).** For each S-NPP pass, the gap to the nearest Aqua pass that day. An "Aqua pass" exists in FIRMS only if Aqua detected something, so this is a measurement of detected passes, not of satellite schedules. Day gap quartiles 14 / 29 / 51 min, 90th percentile 65; only 7% ≤ 5 min, 29% ≤ 15, 51% ≤ 30, 84% ≤ 60. The distribution is broad with no spike near zero, so no natural threshold exists. **Primary T = 15 min**, with 5 / 30 / 60 reported. 66.5% of S-NPP days (day) and 92.3% (night), all years, have no Aqua detection in the box at all.

**Matching.** A VIIRS detection *corresponds* to an Aqua detection if its centre lies inside a rectangle centred on the Aqua coordinate, `scan` km east–west by `track` km north–south (each detection's own FIRMS values, median 1.2 × 1.1 km), plus a **0.5 km margin** for geolocation error, and |Δt| ≤ T. `scan` and `track` are sizes, not polygons, and the true footprint is rotated with the orbit; the rectangle is an approximation. Sensitivity: footprint ×1.5, a fixed 1 km radius, margin 0 and 1 km. Each matched VIIRS detection records its (nearest-centre) Aqua pixel id; counts of "VIIRS matched" and "Aqua pixels containing ≥ 1 VIIRS" are reported separately. "Matched" means *plausible sensor correspondence*, not the same fire.

**Aqua-covered subset.** The required workaround: results are given for all VIIRS detections and for only those where Aqua detected ≥ 1 fire anywhere in the box within T. This is detection-conditioned and favours busy, clear days. It does not remove the limit in section 8.

**Clusters.** VIIRS pixels from the same overpass (detections ≤ 20 min apart) chained when centres are within 750 m; 0.5 and 1.0 km tested. A cluster is not an individual fire. Cluster-level matching (a cluster counts as matched if any member is) removes the effect of several VIIRS pixels sharing one Aqua pixel.

**Quiet vs busy.** Months Feb 2012 – Oct 2026 (177) ranked by cleaned VIIRS monthly count from `monthly_counts.csv` and split into quarters of 45/44/44/44 months. Edges: **3–56, 57–111, 113–253, 264–2,432 VIIRS per month** (the 74/204/376 values in earlier work are colour-class edges, a different thing). Matching comparisons use 2012–2022 months only (29/31/33/38 months per quarter).

## 6. Results
All numbers are day, 2012–2022, T = 15 min unless stated; each subsection heading repeats its scope. Reproducible from `experiment_b.ipynb`. (A day/night audit of Section 6.2 and the day + night original are in `src/p3_day_audit.py` and Appendix C.)

### 6.1 Sanity check, March–April 2016 (both months are extreme)
Day: Aqua 514, S-NPP 3,138 detections (day + night pooled: Aqua 591, S-NPP 4,741). Of Aqua day pixels where S-NPP also observed the box within T, **83.5% contained ≥ 1 VIIRS detection** at T = 15 (n = 158; 86% at 5 min, 79% at 30, 62% at 60). A clear majority, so the matcher works for daytime in a busy period. Night had only 2 and 8 such Aqua pixels at T = 5 and 15: insufficient to judge. This check says nothing about quiet months.

### 6.2 Full overlap (Phase 3), day only, 2012–2022, all VIIRS, T = 15
| | count |
|---|---:|
| Aqua day detections / S-NPP day detections | 4,321 / 24,823 |
| S-NPP matched (inside a contemporaneous Aqua pixel) | 1,643 (6.6%) |
| S-NPP unmatched ("VIIRS-only") | 23,180 |
| matched S-NPP with > 1 candidate Aqua footprint ("ambiguous") | 572 |
| Aqua pixels containing ≥ 1 S-NPP | 1,048 (24%), mean 2.3 S-NPP each |
| Aqua pixels with no S-NPP inside ("Aqua-only") | 3,273 |

All seven rows were recomputed from the raw data with the unchanged rules (`src/p3_day_audit.py`, `intermediate/p3_day_night_audit.csv`), and matching on day-only input gives identical counts. The 6.6% and 24% are **not detection rates**: most S-NPP day passes have no Aqua pass within 15 minutes, and most Aqua passes have no S-NPP pass. Full 2012–2026 window, day: 1,725 of 29,279 matched (5.9%); 2023 onward contributes only 82 day matches because of the drift. The original table pooled day and night (4,553 / 31,005 detections, 1,781 matched = 5.7%); it is kept unchanged in Appendix C.

Restricted to day, Aqua-covered (n = 5,859): **28% of VIIRS day pixels fell inside a contemporaneous Aqua fire pixel** (18–31% across spatial tolerances: margin 0 km 18%, ×1.5 footprint 30%, 1 km radius 25%, margin 1 km 31%; 26–28% for T = 5–60 min). Margin 0 is a diagnostic, not an alternative: it drops the share of Aqua day pixels containing a VIIRS detection to 45%, versus 70% at 0.5 km and 74% at 1.0 km, which indicates geolocation offsets of about half a MODIS pixel; the 0.5–1.0 km plateau supports 0.5 km. Absolute rates depend on the design; the contrasts below do not.

### 6.3 Aqua drifts after 2022 (Extra view), day only
Day Aqua-covered VIIRS match rate by year is 22–38% for 2012–2024 (2016 highest). The share of Aqua day pixels containing a VIIRS detection falls from 60–84% (2012–2021) to 47% (2023); in 2025 and 2026 no S-NPP day detection has an Aqua detection within 15 min. Years with Aqua-covered n < 40 (2022 for the pixel rate, n = 22) are not trend points. `figures/fig_match_by_year_day.png` (day only; Aqua pass time is the day pass). The original `figures/fig_match_by_year.png` pools **day + night** match rates with the day-pass time overlay; its values differ by at most a few points (Aqua-covered 21–38%, pixel rate 61–84%, 2022 n = 24) and it is kept for traceability.

### 6.4 Matched vs VIIRS-only characteristics (Phase 4), day, 2012–2022, Aqua-covered
| | matched (n = 1,643) | VIIRS-only (n = 4,216) |
|---|---:|---:|
| FRP median (q25–q75), MW | 9.0 (5.7–16.5) | 5.6 (3.9–8.5) |
| FRP p90 / p99, MW | 31 / 69 | 14 / 46 |
| cluster size, median pixels | 3 | 1 |
| lone-pixel share | 25% | 54% |
| summed cluster FRP, median MW | 27.7 | 8.4 |
| high-confidence share | 3.2% | 0.6% |
| acquisition time, median UTC minute | 349 | 349 |

Brightness temperatures differ little (T11 median 297.6 vs 295.9 K) and are not used as evidence. Match probability rises with FRP (< 4 MW ≈ 10%; ≥ 20 MW ≈ 59%) and with cluster size (1 pixel 15%; 5+ pixels 62–64%). Each effect persists inside bins of the other (e.g. FRP 4–6 MW: lone pixel 9% vs 5–9 pixel cluster 55%; lone pixels < 2 MW 4% vs ≥ 40 MW 60%). At cluster level the gradient survives (1 pixel 15%, 2 pixels 26%, 3–4 pixels 46%, 5+ pixels 64%), so it is not only an artefact of several VIIRS pixels sharing one Aqua pixel. With a local-coverage check (an Aqua detection within 20 km and 15 min; n = 2,805) the match rate is 59% and the same weak/isolated difference remains (FRP 9.0 vs 5.7 MW; lone 25% vs 47%). `figures/fig_frp_ecdf_matched_vs_viirsonly.png`, `fig_match_prob_frp_clustersize.png`.

### 6.5 Quiet vs busy (Phase 5), day, 2012–2022 (S-NPP pixels sum to 24,823)
| quarter | months | S-NPP pixels | lone-pixel share | FRP median (MW) | share Aqua-covered | match rate, all VIIRS | match rate, Aqua-covered (n) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q1 quietest | 29 | 781 | 64% | 4.5 | 11% | 2.9% | 26.7% (86) |
| Q2 | 31 | 2,058 | 60% | 4.8 | 12% | 3.0% | 25.3% (245) |
| Q3 | 33 | 5,303 | 54% | 5.5 | 22% | 5.8% | 26.0% (1,190) |
| Q4 busiest | 38 | 16,681 | 44% | 6.1 | 26% | 7.5% | 28.8% (4,338) |

- **Quiet months contain weaker and more isolated VIIRS detections** (lone share 64% vs 44%; FRP median 4.5 vs 6.1 MW; cluster median 1 vs 2 pixels). This held in all robustness variants (lone share 0.60–0.68 vs 0.42–0.53).
- The all-VIIRS match rate (2.9% vs 7.5%) is a **coverage artefact**: the share of VIIRS pixels with any Aqua detection nearby in time is 11% vs 26%. It must not be read as Aqua missing more fires in quiet months.
- **The Aqua-covered match rate could not be distinguished between quiet and busy quarters** (26.7%, n = 86, pass-bootstrap 95% CI 17–36%, vs 28.8%, n = 4,338, CI 25–33%). The quiet sample is small and the covered subset is the most biased exactly in quiet months, because days when Aqua passed over and saw nothing are excluded. No claim of "equal", "higher" or "lower" is made.
- A composition-only model (pooled match probability by FRP-bin × cluster-size cell, applied to each quarter's mix) *predicts* 21.9% for Q1 and 29.7% for Q4; this is a model output, not an observation.
- Aqua pixels containing a VIIRS detection (when S-NPP observed the box): 56% (n = 32) in Q1, 74% (n = 964) in Q4; the Q1 sample is too small to call a difference.

### 6.6 Count-level ratios, kept separate (not rerun, reproduced from `monthly_counts.csv`)
| quarter | ratio of sums, Terra + Aqua | mean of monthly ratios, Terra + Aqua | ratio of sums, Aqua only |
|---|---:|---:|---:|
| Q1 quietest | 6.73 | 9.46 | 8.30 |
| Q2 | 5.96 | 7.93 | 7.56 |
| Q3 | 4.83 | 5.27 | 6.05 |
| Q4 busiest | 4.79 | 4.94 | 6.85 |

**"The ratio drops with activity" is solid for Terra + Aqua (6.73 → 5.96 → 4.83 → 4.79, steady) but weaker for Aqua alone (8.30 → 7.56 → 6.05 → 6.85, which rises again in the busiest quarter).** The Aqua-only ratio is also higher than the Terra + Aqua ratio. State this wherever the ratio trend is quoted. Q1 contains 10 of 45 months with **zero Aqua detections**; monthly ratios are undefined for those, so the mean monthly ratio (9.46) and the ratio of sums (6.73) differ, and Aqua coverage or cloud is a live alternative explanation at count level too.

### 6.7 Robustness (Phase 6)
Sixteen variants (spatial rule and margin, T = 5/15/30/60, cluster link 0.5/1.0 km, dropping the top 1% FRP, Aqua confidence ≥ 50, duplicate removal, dropping sparse months with < 30 VIIRS, near-nadir Aqua only). Stable in all: matched FRP median 8.3–9.4 vs VIIRS-only 5.5–5.9 MW; lone share 15–34% vs 50–60%; match probability rising with FRP and cluster size. Not stable: the absolute match rate (18–31%), driven by the spatial tolerance. T = 5 min shifts the matched lone-pixel share (15%) because it selects dense, clear scenes. `figures/fig_match_rate_vs_time_threshold.png`. (A VIIRS-high-confidence-only variant has n = 77 and is not usable.)

### 6.8 Optional activity-dependent count correction
Hold-out as in earlier work: learn Feb 2012 – Dec 2018 (83 months), test 2019–2025 (84 months). The baseline reproduces: ratio 4.92 → total error 24.3% (sum of absolute monthly errors ÷ sum of VIIRS counts), no correction 79.8%, per-calendar-month ratios 31.8%, straight line 23.5%, colour-class agreement 85.7%. One pre-declared correction, a power law VIIRS = 12.0 × MODIS^0.776 (implied ratio 8.4 at 5 MODIS per month, 5.0 at 50, 3.0 at 500): **25.9% total error and 79.8% class agreement. This power law did not beat the baseline on this hold-out.** Its largest failure is in the quietest test quarter (+46% bias). Nothing more is concluded about count correction in general. `figures/fig_correction_holdout.png`.

## 7. Interpretation
- Which factors contribute to Aqua–S-NPP disagreement? (a) **Timing and coverage**: most S-NPP detections have no Aqua pass within 15 minutes, and Aqua's drift after 2022 removes the pairing. (b) **Detection strength as seen by VIIRS**: unmatched S-NPP detections are weaker (lower FRP) and more isolated (lone pixels), consistently across 16 variants. (c) Spatial tolerance sets the level of the match rate but not the contrasts.
- Weak, isolated VIIRS pixels being less often matched is **consistent with** three causes that this data cannot rank: (1) a 1 km pixel not exceeding the MODIS detection threshold for a small fire; (2) VIIRS false alarms, which concentrate in lone low-FRP pixels; (3) Aqua not covering the spot or cloud blocking it. A VIIRS-only detection is **not** shown to be a missed fire, and VIIRS is not ground truth.
- Quiet months do contain weaker and more isolated VIIRS detections, so the *direction* of the hypothesis is not contradicted. **This experiment cannot say how much, if any, of the 6.73 vs 4.79 difference this explains.** The conditional match rate could not be separated between quiet and busy quarters, the quiet sample is small (n = 86), the ratio itself uses Terra + Aqua (not tested here), and 10 of 45 quiet-quarter months have no Aqua detections.
- The hypothesis as stated ("explain why the gap widens in quiet months") is therefore **only qualitatively supported on composition and not tested on outcome**. Evidence is weak for the explanatory claim.

## 8. Limitations
> [!warning] Required limit
> FIRMS CSVs contain **detections only**, not where a satellite looked and found nothing. A VIIRS-only detection can mean: (1) Aqua looked and missed it; (2) Aqua's swath did not cover it; (3) cloud or conditions blocked detection; (4) the fire changed between passes; (5) matching failed. FIRMS CSVs cannot always separate these. We do **not** claim VIIRS-only detections are MODIS failures. The "Aqua-covered" subset (Aqua detected a fire somewhere in the box within the time threshold) is a weak workaround: it is detection-conditioned, favours busy clear days, and does not establish that the specific location was in swath or cloud-free. It does not remove the problem.

Also: footprints are unrotated rectangles with a 0.5 km margin; absolute match rates are design-dependent (18–31%); March–April 2016 are both extreme months and validate the matcher only; ratio and matching evidence concern different sensor sets (Terra + Aqua vs Aqua + S-NPP); the quiet-quarter match sample is small; night, 2023+ and high-confidence-only subsets are too thin to conclude from; the FRP and cluster differences are partly the 1 km detection-threshold effect and partly VIIRS-specific noise and cannot be split with this data.

## 9. Implications for harmonization
- **Keep the count-level method unchanged.** The simple ratio with the existing hold-out (24.3% total error, 86% class agreement) is not improved by the one activity-dependent correction tested here.
- **Present the ratio as activity-dependent**, not as a single constant: ratio of sums is 6.73 in the quietest quarter and 4.79 in the busiest (Terra + Aqua), and in the 2019–2025 hold-out a constant ratio (4.92) does worst in the quietest quarter of test months (total error 66%; signed bias −16%, i.e. under-predicts VIIRS). The largest signed bias is in the second-quietest quarter (−25%); the busiest quarters are within +4%. These come from this experiment's recomputation of the hold-out (`src/p7_correction.py`), not from an external table; test quarters are quarters of the 84 test months ranked by VIIRS count.
- Do **not** harmonize by dropping or down-weighting lone low-FRP VIIRS pixels on this evidence: they are not shown to be false or missed fires.
- Aqua after 2022 is not comparable with S-NPP in time of day; any harmonized series should flag 2023 onward.

## 10. Next steps
1. Test the composition idea at count level only if an independent source of quiet-month Aqua overpass coverage can be found (not available in FIRMS CSVs; no new data was added here).
2. Repeat the matching with the Terra overpass (≈ 02:30 UTC) separately, since the earlier ratio used Terra + Aqua.
3. Use a rotated footprint to narrow the 18–31% spread.

## 11. Summary for the competition project page (100 words)
We matched NASA's Aqua (MODIS) and S-NPP (VIIRS) fire detections in Sabah, 2012–2022. S-NPP detections without an Aqua partner were weaker and more often isolated single pixels, and quiet months had more of them. That fits small fires, VIIRS false alarms or missing Aqua coverage; the data cannot say which, and it does not show Aqua "missed" fires. The VIIRS-to-MODIS ratio falls steadily with activity for Terra + Aqua, but less cleanly for Aqua alone. A simple activity-based correction did not beat our fixed ratio, so we keep the ratio and report its limits.

## Appendix A — Night (indicative only, not a conclusion)
2012–2022 night, T = 15: 232 Aqua and 6,182 S-NPP detections, 138 matched (2.2%); Aqua-covered n = 327, match rate 42%; Aqua pixels containing VIIRS 92% (n = 61). Aqua-covered matched (n = 138) vs VIIRS-only (n = 189): FRP median 2.5 vs 1.1 MW; lone-pixel share 5% vs 51%. Quiet-quarter night samples are 1–25 detections. Night is not used in any conclusion.

## Appendix B — Advisor reviews
Five reviews (design, sanity check, characteristics, robustness, conclusions) are recorded in `progress.md`, with what was changed because of each. One extra readiness test of the advisor before Phase 1 is also logged there.

## Appendix C — Original Section 6.2 table, **Day + Night pooled** (kept for traceability)
This is the table as first written. It pools day and night, so its S-NPP and matched counts are not daytime figures; Section 6.2 now gives the day-only version. 2012–2022, all VIIRS, T = 15, **Day + Night**:

| | Day + Night | of which day | of which night |
|---|---:|---:|---:|
| Aqua detections / S-NPP detections | 4,553 / 31,005 | 4,321 / 24,823 | 232 / 6,182 |
| S-NPP matched | 1,781 (5.7%) | 1,643 (6.6%) | 138 (2.2%) |
| S-NPP unmatched ("VIIRS-only") | 29,224 | 23,180 | 6,044 |
| ambiguous (> 1 candidate Aqua footprint) | 637 | 572 | 65 |
| Aqua pixels containing ≥ 1 S-NPP | 1,104 (24%), mean 2.4 each | 1,048 (24%), mean 2.3 | 56 (24%), mean 3.9 |
| Aqua-only pixels | 3,449 | 3,273 | 176 |

Original sentence, Day + Night: "Full 2012–2026 window: 1,877 of 36,328 matched; 2023 onward contributes only 96 matches." By scope: day 1,725 of 29,279 and 82; night 152 of 7,049 and 14. Aqua-covered (T = 15, 2012–2022): day n = 5,859, 28.0%; night n = 327, 42.2%; pooled n = 6,186, 28.8%.
