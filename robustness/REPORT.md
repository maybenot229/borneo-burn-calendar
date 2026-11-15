# Robustness checks for the Sabah MODIS–VIIRS harmonization

Team SpaceZY, NASA Space Apps Challenge 2026. Run on 15 November 2026.

AI use: analysis code and draft text produced with Claude (Anthropic), directed and reviewed by the team.

**Purpose.** These four checks ask how much confidence the fixed-ratio method deserves. They do not change the method. The ratio on the website and the published CSV are unchanged.

**Reproduce.** `python robustness_checks.py sabah_raw_MODIS.csv sabah_raw_VIIRS.csv data/sabah_harmonized_monthly.csv`. Tables and figures go to `robustness_out/`. The raw FIRMS files are not in the repository.

**Baseline check first.** The script rebuilt the monthly counts from the raw files. They match the earlier counts exactly, for Terra + Aqua, Terra alone and Aqua alone. The baseline reproduces: ratio 4.92, total error 24.3%, same colour class in 72 of 84 test months.

**Definitions used everywhere.** Area: latitude 4.0–7.5, longitude 115.3–119.3 (a rectangle, not the official Sabah boundary). FIRMS archive rows only (`type == 0`). MODIS confidence ≥ 30. VIIRS S-NPP confidence `n` or `h`. VIIRS is used from February 2012. Learn on February 2012 to December 2018. Test on 2019 to 2025.

## Summary

| # | Experiment | Status | Result in one line | Changes a conclusion? |
|---|---|---|---|---|
| 1 | Yearly ratio, 2012–2025 | Done | Between 4.19 and 6.08, no clear trend. Highest in the quietest years. | No. Adds one limit. |
| 2 | Uncertainty for the 59% fall | Done | Fall in every check. Ratio uncertainty alone: −57% to −61%. Size depends on which years are included. | Yes, one wording fix (see 2.7). |
| 3 | Terra-only and Aqua-only hold-out | Done | Terra + Aqua is best (24.3%). Aqua only 27.6%. Terra only 45.9%. | No. |
| 4 | Confidence filters | Done | Error stays 24–25% for reasonable filters. The ratio itself moves from 4.58 to 6.00. | No. Adds one limit. |

One negative finding and one correction came out of this work. Both are reported in full below.

---

## Experiment 1: Is the ratio steady from year to year?

**1. Question.** The method learns one ratio after 2012 and applies it to 2003–2011. Does the ratio stay steady across the 14 years where we can measure it?

**2. Method.** For each year, total cleaned VIIRS detections divided by total cleaned MODIS detections. Done for Terra + Aqua, Terra alone and Aqua alone. 2012 covers February to December only. The bars in the figure come from resampling that year's months. They are a rough guide, not a formal interval. We also took the median daytime pass time of each satellite's detections in the box, per year.

**3. Results.**

| Year | VIIRS | MODIS | Terra | Aqua | Ratio Terra + Aqua | Ratio Terra | Ratio Aqua |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2012* | 2,481 | 592 | 135 | 457 | 4.19 | 18.4 | 5.43 |
| 2013 | 2,136 | 457 | 98 | 359 | 4.67 | 21.8 | 5.95 |
| 2014 | 3,950 | 785 | 201 | 584 | 5.03 | 19.7 | 6.76 |
| 2015 | 5,335 | 1,043 | 305 | 738 | 5.12 | 17.5 | 7.23 |
| 2016 | 7,445 | 1,468 | 490 | 978 | 5.07 | 15.2 | 7.61 |
| 2017 | 1,081 | 198 | 34 | 164 | 5.46 | 31.8 | 6.59 |
| 2018 | 1,819 | 383 | 98 | 285 | 4.75 | 18.6 | 6.38 |
| 2019 | 3,070 | 593 | 195 | 398 | 5.18 | 15.7 | 7.71 |
| 2020 | 1,943 | 425 | 130 | 295 | 4.57 | 15.0 | 6.59 |
| 2021 | 1,161 | 254 | 44 | 210 | 4.57 | 26.4 | 5.53 |
| 2022 | 584 | 96 | 11 | 85 | 6.08 | 53.1 | 6.87 |
| 2023 | 1,200 | 206 | 38 | 168 | 5.83 | 31.6 | 7.14 |
| 2024 | 2,543 | 569 | 163 | 406 | 4.47 | 15.6 | 6.26 |
| 2025 | 773 | 130 | 18 | 112 | 5.95 | 42.9 | 6.90 |

\* February to December.

- **Terra + Aqua.** Whole-period ratio 4.93. Yearly values run from 4.19 to 6.08, median 5.05. Nine of 14 years sit within 10% of 4.93.
- **Trend.** No significant trend with time (Spearman rho +0.35, p = 0.21). With 14 points this test is weak. A mild upward drift cannot be ruled out.
- **Low-count years.** The five years with the fewest MODIS detections are 2017, 2021, 2022, 2023 and 2025. The three highest ratios (2022, 2025, 2023) are all among them. 2022 has only 96 MODIS detections and three months with zero.
- **Drift years.** 2012–2022 gives 4.93. 2023–2025 gives 4.99. Aqua alone gives 6.81 and 6.58. There is no visible step.
- **Pass times.** Aqua's median daytime pass moved from about 05:40 UTC to 05:54 (2023), 06:11 (2024) and 06:56 (2025). **Terra drifted too**, the other way: from about 02:55 to 02:27 (2023), 02:12 (2024) and 01:43 (2025). Suomi NPP stayed near 05:41. In 2003–2011 both MODIS satellites passed at the same times as in 2012–2022.
- **Mix of satellites.** Terra supplied 27% of MODIS detections in 2003–2011 and 28% in 2012–2022.
- **Terra alone** is unstable: 15.0 to 53.1. Its yearly ratio rises strongly in quiet years (rho −0.78 with the yearly VIIRS total, p = 0.001).
- **Yearly totals.** With the training ratio (4.92), yearly totals in the test years were off by −19% to +10%, 12% on average. All seven test years together were off by −0.8%.

Figure: `robustness_out/fig_exp1_annual_ratio.png`.

**4. Against the baseline.** The whole-period ratio (4.93) matches the baseline (4.92 learned, 4.95 in the published CSV). Training years give 4.92 and test years 4.96.

**5. Limits.**
- This covers 2012–2025 only. The ratio in 2003–2011 cannot be measured, because VIIRS did not exist.
- Fourteen yearly values are few. Small trends would be missed.
- The quiet years and the drift years overlap (2022, 2023, 2025). The two effects cannot be separated. 2024 was a busier drift year and has a low ratio (4.47), but one year proves nothing.
- A yearly association is not a cause.

**6. Interpretation.** At the yearly scale the ratio is fairly steady, and yearly totals are predicted much better than single months. The largest swings fall in low-count years, which fits the earlier finding that the ratio is higher in quiet months. For Terra + Aqua this yearly link is not statistically significant (rho −0.38, p = 0.18). The conditions we can check were the same in 2003–2011 as in the learning years: pass times and the Terra–Aqua mix. One condition was different: 2003–2011 had more hotspots per year. If the activity pattern also held then, the ratio before 2012 would be slightly below 4.95, not above it. That is a hypothesis, not a result. Experiment 2 shows what it would do.

**7. Does it change a conclusion?** No. It adds one limit: Terra's pass time also drifted after 2022. The website lists only Aqua.

---

## Experiment 2: How sure is the 59% fall?

**1. Question.** The harmonized record shows average yearly hotspots falling by about 59% between 2003–2011 and 2012–2025. How uncertain is that number?

**2. Method.**

Exact formula, as the website computes it:

> change = (mean of yearly harmonized totals, 2012–2025) ÷ (mean of yearly harmonized totals, 2003–2011) − 1

From the published CSV: 6,269 → 2,540, which is −59.49%. Recomputed from the raw files: −59.49%. The ratio inside the published CSV is 4.947.

Three kinds of check, 10,000 bootstrap replicates each where a bootstrap is used. Whole years are resampled, never single months. That keeps each year's seasonal shape intact.

- **A. Ratio uncertainty only.** Resample the 14 overlap years, re-learn the ratio, recompute the change. The yearly totals themselves stay fixed.
- **B. Years as a sample.** Resample the 9 early years and the 14 late years, re-learn the ratio from the resampled late years, recompute the change. This asks a different question: if these years are a sample of two fire regimes, how different are the regimes?
- **Leave one year out.** Drop each year in turn.
- **Ratio scenarios.** Recompute the change if the true ratio before 2012 was different. This is systematic and sits outside both intervals.

**3. Results.**

| Check | Result |
|---|---|
| Estimate | −59.5% |
| Ratio, bootstrap of overlap years | median 4.94, 95% interval 4.71 to 5.12 |
| A. Ratio uncertainty only | median −59.4%, 95% interval **−60.8% to −57.5%** |
| B. Years as a sample | median −59.7%, 95% interval **−75.2% to −35.1%** |
| B. Share of replicates showing a fall | 100% |
| Leave one early year out | −62.7% (without 2011) to −55.9% (without 2005) |
| Leave one late year out | −65.5% (without 2016) to −57.1% (without 2022) |

| If the ratio before 2012 was really… | Ratio | Change |
|---|---:|---:|
| the lowest yearly ratio seen | 4.19 | −52.2% |
| the busiest-quarter ratio | 4.79 | −58.2% |
| the baseline | 4.95 | −59.5% |
| the highest yearly ratio seen | 6.08 | −67.0% |
| the quietest-quarter ratio | 6.73 | −70.2% |

For the fall to vanish, the ratio before 2012 would have to be **2.0**. For a fall of only 50% it would have to be 4.0. No year in the overlap is below 4.19.

Figure: `robustness_out/fig_exp2_change_interval.png`.

**4. Against the baseline.** The estimate is unchanged at about 59%.

**5. Limits.**
- **Only nine early years.** Two of them, 2004 and 2005, hold 36% of all early MODIS detections. A bootstrap on nine values tends to give intervals that are too narrow. Treat interval B as a rough guide.
- Year blocks assume years are independent. Dry spells linked to El Niño can span two years, so they are not fully independent.
- Interval A covers only how well the ratio is estimated from the overlap years.
- Interval B adds year-to-year variation in fire activity.
- **Outside both intervals:** whether the ratio before 2012 equalled the ratio after (not testable); the choice of confidence filter and of the area; MODIS sensor ageing; cloud and smoke hiding fires; and the fact that hotspot counts are not fires or burned area.

**6. Interpretation.** The direction is robust. Every check shows a fall. The size is less certain than "59%" suggests. The ratio contributes little uncertainty (about ±2 points). Which years are included matters far more: one strong year moves the answer by several points. This is a change in **estimated yearly hotspot counts**. It is not a measured change in fire activity, and it is not burned area.

**7. Does it change a conclusion? Yes, one wording fix.**

MODIS alone, with no ratio, falls by −59.4%. We had described that as an independent check of the ratio. **It is not.** The harmonized change is `VIIRS_late ÷ (ratio × MODIS_early) − 1`. The ratio is itself `VIIRS ÷ MODIS` over almost the same late years. So the VIIRS terms cancel, and what is left is `MODIS_late ÷ MODIS_early − 1`. The two numbers agree by arithmetic.

What is true, and what we should say instead:
- The 59% fall comes from the MODIS record, one instrument design observed across the whole period.
- Harmonization does not create the fall. It puts both eras on one scale, and removes the fake doubling in the raw join.
- The ratio matters for the level of each month, the colour classes and "now vs normal". It hardly matters for this percentage.

---

## Experiment 3: Terra alone and Aqua alone

**1. Question.** Is Terra + Aqua the right MODIS input, or would one satellite do as well?

**2. Method.** Same split, filters and dates as the baseline. One ratio learned on February 2012 to December 2018, tested once on 2019 to 2025. Test months are ranked by real VIIRS count and cut into four equal groups, quiet to busy. The ratio's range comes from a year-block bootstrap of the seven training years.

**3. Results.**

| | Terra + Aqua (baseline) | Terra only | Aqua only |
|---|---:|---:|---:|
| MODIS detections, training / test | 4,926 / 2,273 | 1,361 / 599 | 3,565 / 1,674 |
| Ratio learned on training years | 4.92 | 17.82 | 6.80 |
| Ratio in test years | 4.96 | 18.82 | 6.73 |
| Rough 95% range of the learned ratio | 4.62 to 5.09 | 16.3 to 20.9 | 6.05 to 7.28 |
| Total error | **24.3%** | 45.9% | 27.6% |
| Signed bias | −0.8% | −5.3% | +1.0% |
| MAE (hotspots per month) | 32.6 | 61.6 | 37.1 |
| RMSE (hotspots per month) | 45.4 | 98.7 | 53.2 |
| Same colour class, of 84 | **72** | 62 | 66 |
| Test months with zero MODIS | 7 | 20 | 8 |
| Bias, quietest group | −16% | −60% | +1% |
| Bias, second group | −25% | −46% | −17% |
| Bias, third group | 0% | −46% | +18% |
| Bias, busiest group | +4% | +17% | −1% |
| Error, quietest group | 66% | 91% | 78% |
| Error, busiest group | 18% | 40% | 19% |
| Error 2019–2022 / 2023–2025 | 27.3% / 19.7% | 47.1% / 44.2% | 29.9% / 24.2% |
| Bias 2019–2022 / 2023–2025 | −0.4% / −1.4% | +0.2% / −13.6% | −0.6% / +3.3% |

**4. Against the baseline.** Terra + Aqua wins on total error, MAE, RMSE and colour class. Aqua alone is close behind. Terra alone is much worse.

**5. Limits.**
- Terra has few detections here (599 in seven test years) and 20 test months with zero. Its results are noisy.
- Aqua alone shows almost no bias in the quietest group (+1%, against −16%). Its error there is higher (78%, against 66%), so it is not better. The small bias is over- and under-predictions cancelling.
- Error in 2023–2025 is lower than in 2019–2022 for all three. That period holds only three years, one of them busy (2024). It does not show that drift is harmless.
- Terra alone under-predicts by 13.6% in 2023–2025, the years its pass time moved. That is an association from 219 Terra detections, not a cause.

**6. Interpretation.** Using both MODIS satellites gives more detections and a steadier ratio. In each case the ratio in the test years falls inside the range learned from the training years, so each ratio is stable. They differ in how noisy the monthly predictions are.

**7. Does it change a conclusion?** No. No new production model is chosen from this.

---

## Experiment 4: Does the confidence filter drive the result?

**1. Question.** The baseline keeps MODIS confidence ≥ 30 and VIIRS `n` or `h`. Would other reasonable filters change the conclusions?

**2. Method.** The set of filters was fixed before running. One sensor changed at a time, then both. Each configuration gets its own ratio, learned on the same training months, and its own colour-class edges. Three configurations are marked **extreme**: they keep so few detections that they are not reasonable choices. They are reported for completeness.

Detections by confidence in the archive: MODIS < 30: 1,424; 30–49: 3,443; 50–79: 12,406; ≥ 80: 4,310. VIIRS: `n` 35,367; `l` 1,702; `h` 967.

**3. Results.**

| Filter | MODIS kept, 2003–2025 | VIIRS kept, 2012–2025 | Ratio learned | Ratio in test | Total error | Signed bias | Same class, of 84 | Bias, quietest | Change 2003–11 to 2012–25 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Baseline: MODIS ≥ 30, VIIRS n+h** | 18,611 | 35,521 | 4.92 | 4.96 | 24.3% | −0.8% | 72 | −16% | −59.4% |
| MODIS ≥ 0 (keep all) | 19,923 | 35,521 | 4.58 | 4.65 | 24.0% | −1.5% | 71 | −12% | −59.3% |
| MODIS ≥ 50 | 15,424 | 35,521 | 6.00 | 5.96 | 25.3% | +0.7% | 69 | −19% | −59.8% |
| VIIRS l+n+h (keep all) | 18,611 | 37,190 | 5.13 | 5.25 | 23.9% | −2.2% | 71 | −16% | −59.4% |
| Both loosest: MODIS ≥ 0, VIIRS l+n+h | 19,923 | 37,190 | 4.77 | 4.91 | 24.0% | −2.9% | 71 | −11% | −59.3% |
| MODIS ≥ 80 (extreme) | 4,006 | 35,521 | 24.10 | 28.33 | 46.0% | −14.9% | 55 | −46% | −65.3% |
| VIIRS h only (extreme) | 18,611 | 941 | 0.14 | 0.11 | 60.9% | +24.1% | 53 | not defined | −59.4% |
| Both strictest: MODIS ≥ 80, VIIRS h (extreme) | 4,006 | 941 | 0.68 | 0.64 | 63.4% | +6.4% | 54 | not defined | −65.3% |

"Not defined": with VIIRS `h` only, 36 of 84 test months have zero VIIRS detections, so the quietest group sums to zero.

**4. Against the baseline.** For the four reasonable alternatives, total error stays between 23.9% and 25.3%, colour-class agreement between 69 and 72 of 84, and the quiet-month bias between −11% and −19%. The baseline is not the best row on every measure, and we do not switch to another row.

**5. Limits.**
- **The ratio depends on the filter.** It is 4.58 with all MODIS detections, 4.92 at the baseline, and 6.00 at MODIS ≥ 50. "About 4.95" is correct only for this pair of filters.
- The extreme filters fail because they leave too few detections, not because the method fails.
- Only confidence was varied. The area, the dates and the `type == 0` rule were not.
- The last column uses each configuration's own ratio, learned on all overlap months to 2025. It changes little by construction (see 2.7). It reflects the MODIS record under each filter. The baseline row reads −59.4% here and −59.5% on the website, because the website's ratio is 4.947 and this one is 4.934.

**6. Interpretation.** The conclusions are robust to reasonable filter choices: the accuracy of the method, the quiet-month under-prediction and the fall of about 59% all hold. The value of the ratio is not robust to the filter. That is expected. A stricter MODIS filter removes MODIS detections, so each remaining one stands for more VIIRS detections.

**7. Does it change a conclusion?** No. It adds one limit: the ratio must not be reused with different confidence filters.

---

## README addition

```markdown
## Robustness checks

We ran four extra checks on 15 November 2026. They do not change the method. Details: `robustness/REPORT.md`.

| Check | Result |
|---|---|
| Ratio year by year, 2012–2025 | Between 4.2 and 6.1, no clear trend. Highest in the quietest years. |
| How sure is the 59% fall | A fall in every check. Ratio uncertainty alone gives −57% to −61%. Dropping any one year gives −56% to −66%. |
| Terra only, Aqua only | Terra + Aqua is best (24% error). Aqua only 28%. Terra only 46%. |
| Other confidence filters | Error stays at 24–25%. The ratio itself moves from 4.6 to 6.0. |

New limits from these checks:
- The fall is in estimated yearly hotspot counts. Its size depends on which years are included. Treating the years as a sample gives a wide range, about −35% to −75%.
- MODIS alone shows the same fall. That follows from the arithmetic and is not an independent check of the ratio. The fall comes from the MODIS record. The ratio puts both eras on one scale.
- The ratio of about 4.95 holds only for our confidence filters.
- Terra's overpass also drifted after 2022 (about 02:55 to 01:43 UTC by 2025).
- The ratio before 2012 cannot be tested. It would need to be 2.0 for the fall to vanish. The lowest yearly ratio we measured is 4.2.
```

**One sentence in the current README must change.** It says: "MODIS alone agrees with the harmonized fall, which checks the ratio independently." Replace it with: "MODIS alone shows the same fall. That follows from the arithmetic, so it is not an independent check of the ratio. It shows the fall comes from the MODIS record itself."

## Slide update (one line for the Test or Limits slide)

> **Checked four more ways.** The yearly ratio stays between 4.2 and 6.1. Other filters and single satellites do not beat the method. Every check shows a fall. The ratio would need to be 2.0, not 4.95, for the fall to vanish.

Shorter version: **"The fall survives every check we ran. Its exact size is less certain than its direction."**

## Files

| File | What it is |
|---|---|
| `robustness_checks.py` | Runs all four experiments from the raw files. |
| `robustness_out/exp1_annual_ratio.csv` | Yearly totals and ratios. |
| `robustness_out/exp1_overpass_minutes.csv` | Median daytime pass per satellite and year (minutes after 00:00 UTC). |
| `robustness_out/exp2_bootstrap.csv` | The 10,000 bootstrap replicates. |
| `robustness_out/exp3_holdout_by_satellite.csv` | Hold-out results per satellite. |
| `robustness_out/exp4_confidence_filters.csv` | Hold-out results per filter. |
| `robustness_out/fig_exp1_annual_ratio.png` | Yearly ratio and pass times. |
| `robustness_out/fig_exp2_change_interval.png` | Ranges for the 59% fall. |
