# Site upgrade: Borneo Burn Calendar

Read `CLAUDE.md` in this folder first and follow every rule in it. This prompt adds to it. Where they disagree, stop and ask me.

## 0. Ground rules for this job

- Work on a new git branch called `site-upgrade`. Do not touch `main`. Do not push. When done, show me a local preview and the list of changed files, then wait.
- Time: stop building 180 minutes after you start. Write the start time in `progress.md` and check the clock after every card. If a card will not fit, leave it undone and say so. Do not squeeze it in half-finished.
- Plain HTML, CSS and JavaScript. No framework, no build step, no outside scripts or fonts. The site must still work from GitHub Pages with no server.
- Every number on the page comes from `data/sabah_harmonized_monthly.csv`, computed in `app.js`. Do not hard-code counts, years or months. The only fixed numbers allowed are the colour edges already in `app.js` (74, 204, 376) and the verified figures in section 7 of `CLAUDE.md`.
- Do not change the CSV, the colour edges, the ratio or the existing proof charts. Add to the page. Do not remove the headline block, the Proof 1 and Proof 2 sections, the Limits list or any AI-use note.
- Wording: say hotspot counts, never fires or burned area. Say "about 59%". Say that values before February 2012 are estimates. Never write a forecast. The season view is history.
- From the first card on, build everything phone first (360 px wide), usable with a keyboard (Tab, Enter, Space, Escape), with a visible focus ring, and never let colour alone carry the class. Always show the class word too (Low, Medium, High, Very high). This covers the phone and accessibility work, so those need no separate card until the final pass.
- Respect `prefers-reduced-motion`.

## 1. Who the page is for

Two groups equally: judges who skim for a minute, and land managers and fire crew leads who plan a season. The first screen must answer one question: how is this month? That is the status banner. The finding (raw join doubles, harmonized falls about 59%) stays directly under it.

Page order after the change:
1. Header
2. **Status banner** (new, card 5)
3. Existing headline finding block
4. Controls and summary cards
5. Calendar, now with tap-for-details (card 2)
6. **Critical burning windows** (new, card 4)
7. **Unusual months** (new, card 3)
8. Now vs normal (existing)
9. Proof 1, Proof 2 (existing), plus the sensors figure (card 13)
10. **How sure are we** (new, card 12)
11. Results, How it works, Limits (existing)
12. Footer

## 2. Build order (stop at the time limit)

| Order | Card | What | Time |
|---|---|---|---:|
| 1 | 5 | Status banner | 25 |
| 2 | 2 | Tap a month for details | 35 |
| 3 | look | Calendar matrix look pass, see section 4 | 30 |
| 4 | 4 | Critical burning windows | 40 |
| 5 | 3 | Unusual months | 30 |
| 6 | 12 | How sure are we | 30 |
| 7 | 13 | Why the sensors differ figure | 15 |
| | | Subtotal | 205 |
| 8 | 15 | Glossary tips (only if time is left) | 20 |
| 9 | 1 | Use this for your region (only if time is left) | 25 |
| 10 | final pass | Phone test at 360 px, keyboard test, colour-blind check, console clean | 20 |
| Last | 9 | Bahasa Malaysia labels, see section 5 | 60 |

The subtotal is over the limit on purpose. Work down the list in order and stop at the limit. Rows 1 to 3 matter most.

Do the final pass (row 10) even if it means dropping rows 4 to 9. Reserve its 20 minutes inside the time limit. Quality of what exists beats quantity.

## 3. Card specs

### Card 5: Status banner

A card at the top of `<main>` showing the latest month in the CSV.

- Line 1, large: month and year, for example `October 2026`.
- Class word with a colour chip using the existing class colours: Low, Medium, High or Very high.
- One sentence about the usual level, using `now_vs_normal` (the 10-year normal). If `normal_10yr` is empty use `normal_all_years` and say "all-years normal". Wording by ratio: below 0.75 "below usual", 0.75 to 1.25 "close to usual", above 1.25 up to 2 "above usual", 2 or more "well above usual". Always add the number, for example `about 0.8 times the usual for October`.
- A status chip: `Provisional, may change` if `provisional` is true, else `Measured by VIIRS`. If the month is estimated from MODIS, say `Estimated from MODIS`.
- Under it, the last three months as small chips with the same class word and ratio, each marked provisional where it applies.
- A one-line note: `Hotspot counts for the whole Sabah box. A planning tool, not live fire response.`

Expected for the current CSV: October 2026, Medium (89 hotspots), about 0.8 times the usual for October, close to usual, provisional. The chips show August 2026 High (about 1.4), September 2026 Medium (about 1.3), October 2026 Medium (about 0.8).

### Card 2: Tap a month for details

Make every calendar cell a real button (or `role="button"` with `tabindex="0"`) that opens a details panel below the calendar. Enter and Space open it. Escape closes it. The panel gets focus and `aria-live="polite"`. On a phone it must not cover the calendar permanently.

Panel content, in this order:
1. One plain sentence, for example `March 2016: Very high. About 8.7 times the usual March.`
2. Hotspots shown (the harmonized value) and the class word.
3. Status chip: Measured by VIIRS, Estimated from MODIS, or Provisional.
4. Counts behind it: MODIS count, and the VIIRS count where it exists.
5. The normal used and which one (10-year or all-years).
6. Rank among the same calendar month across the record, with the number of years, for example `2nd highest of 24 Marches`.
7. For estimated months add: `Estimated: scaled from MODIS. Less certain, especially in quiet months.`

Expected: March 2016 = 2,432, Very high, 8.7 times the 10-year normal (normal 280), rank 2 of 24 Marches. March 2010 = 2,948.5, rank 1 of 24. October 2026 = 89, Medium, provisional, rank 20 of 24 Octobers. Cross-check the ranks with a quick script.

### Card 4: Critical burning windows

A strip of 12 bars, one per calendar month. Each bar shows how many years that month reached High or Very high (value 204 or more), as `n of N years`, plus the median hotspots. Two views, one toggle:

- `All years, 2003 to 2025` (default). Use complete years only (2003 to 2025). Ignore 2026 and all provisional months. The 2003 to 2011 values are estimates. Say so in a visible note.
- `Measured years only, 2013 to 2025`. Excludes every estimated month.

Under the bars, one sentence built from the data, not typed in. Rule: a month counts as a likely window if it reached High or Very high in at least half of the years in the view. List those months as runs (for example `March to October`). If none, say so. Add a fixed line: `This is history, not a forecast.`

Expected counts (High or Very high):

| Month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All years, of 23 | 4 | 10 | 14 | 12 | 14 | 12 | 16 | 17 | 15 | 13 | 3 | 1 |
| Measured years, of 13 | 1 | 5 | 7 | 6 | 5 | 4 | 7 | 7 | 5 | 4 | 0 | 0 |

So the all-years sentence lists March to October. The measured-years sentence lists only March, July and August. That difference is real and must show. It means the clear seasonal pattern leans on estimated years. Do not smooth it over.

### Card 3: Unusual months

A ranked list of the months furthest above normal, for the year range chosen in the existing controls.

- Use `now_vs_normal` (10-year normal). Skip months with no 10-year normal (before 2008) and say so in one line.
- Skip provisional months.
- Only include months with at least 74 hotspots (Medium or above), so a jump from 2 to 20 does not top the list.
- Show the top 8: month and year, class chip with word, hotspots, `x times usual`, and a Measured or Estimated chip. Each row is a button that scrolls to and opens that month in the details panel (card 2).
- Heading: `Most unusual months`. Sub line: `Hotspot counts compared with the usual for that calendar month.`

Expected for the full range: 2016-04 (9.7), 2016-03 (8.7), 2016-01 (7.1), 2019-02 (6.1), 2010-03 (5.8), 2016-02 (5.5), 2010-02 (4.6), 2024-05 (3.8). Note that 2010 months are estimates.

### Card 12: How sure are we

A new section in plain words. Use only these verified numbers:

- Test: learn Feb 2012 to Dec 2018, test 2019 to 2025. About 24% total error. Same colour class in 72 of 84 months.
- Five other methods tested on the same split; none clearly beat the fixed ratio.
- The 59% fall: ratio uncertainty alone gives about -57% to -61%. Dropping any one year gives about -56% to -66%. Treating the years as a sample gives a wide range, about -35% to -75%, because only nine early years exist. Every check shows a fall.
- The ratio before 2012 cannot be tested. It would have to be 2.0 for the fall to vanish. The lowest yearly ratio we measured is 4.2.
- MODIS alone shows the same fall. That follows from the arithmetic, so it is not an independent check of the ratio.
- The ratio of about 4.95 holds only for our confidence filters and only for Sabah.
- Link to `robustness/REPORT.md` and `experiment_b/REPORT.md` in the repository.

Layout: three short blocks (What we tested, What held up, What we cannot know) and one small table. No long paragraphs.

### Card 13: Why the sensors differ

Under Proof 2 add the figure `img/slide6_three_panel.png` (I will copy it into `img/`; if it is missing, leave a clear TODO and skip) with alt text and two sentences: `VIIRS-only detections are weaker and more often single pixels. This is a pattern in daytime Aqua against Suomi NPP data, not proof of why. It does not show that MODIS missed fires.`

### Card 15 (if time): Glossary tips

Tap or focus a term for a one-line meaning: hotspot, MODIS, VIIRS, ratio, colour class, provisional, estimated. Works by keyboard and touch, closes with Escape. Max one short sentence each.

### Card 1 (if time): Use this for your region

A short section with three steps: get FIRMS data for your own box; find the years where both sensors overlap and compute your own ratio; test it on years you held back before trusting it. Link to the notebooks and `analysis/method_checks.py`. State plainly: `Our ratio of about 4.95 is for Sabah only. Do not reuse it elsewhere.`

## 4. Look and feel

Look chosen: **the calendar matrix is the hero.** Do this as a 30-minute look pass straight after card 2, before card 4. If it runs over 30 minutes, stop and keep what works.

The matrix
- One grid: years down, months across (Jan to Dec). All years visible, newest at the top.
- Cells are square, with no gaps wider than 2 px, so the pattern reads at a glance. On a phone each cell is at least 24 px, and the grid scrolls inside its own box if needed. The year column and month header stay sticky.
- Keep the existing class colours and edges. Do not invent a new scale.
- Estimated months (before Feb 2012) get a diagonal hatch over the colour. Provisional months get a dashed outline. A small legend under the grid shows: the four class words with colours, the hatch, the dashed outline.
- A thin line across the grid between 2011 and 2012, labelled `VIIRS starts, Feb 2012`.
- The selected cell gets a thick dark outline. It must be clear in sunlight.

The page around it
- Light page background (near white), dark text. This is for reading on a phone outdoors. No dark mode.
- One dark navy band for the header only, with the title in a serif system font (`Georgia, 'Times New Roman', serif`). Body text stays in the system sans font. No outside fonts.
- Under the status banner, a date stamp in large plain type: `Data through: <latest month>` and, if provisional, `Latest three months are provisional`. Compute both from the CSV.
- A row of 3 or 4 small stat chips under the stamp, computed from the CSV: number of months, number of estimated months, first and last month.
- Body text at least 16 px. Tap targets at least 44 px, except matrix cells. Contrast of text against its background at least 4.5 to 1.
- Hot colours are used only for hotspot classes. Buttons, links and chips use navy or grey, so warm colour always means hotspots.
- No photos, no carousels, no animation beyond a 150 ms fade on the details panel.

Keep new components consistent with each other: same card edges, spacing and type.

## 5. Bahasa Malaysia (last, and only with my say-so)

After everything else, build a language switch (English, Bahasa Malaysia) for headings, the class legend, the status banner sentence and the season sentence. Put every string in one file, `i18n/ms.json`, each marked `"review": "NEEDS REVIEW"`. Do not wire the switch into `index.html` on the branch until I confirm in chat that a Malay speaker checked every string. If I have not confirmed, stop after writing the file and tell me.

## 6. Test checklist (run before you report)

1. Serve locally (`python -m http.server 8000`). Console shows no errors.
2. The headline still says about 59% and the raw join doubled.
3. Status banner shows the expected values above.
4. Tab to a calendar cell, press Enter, details open; Escape closes. March 2016 and October 2026 match the expected values.
5. Season strip counts match both rows of the table. Toggle works.
6. Unusual list matches the expected eight.
7. At 360 px wide nothing scrolls sideways except the calendar, which scrolls inside its own box.
8. Every chip also shows its word (colour is never the only signal).
9. Change the year range: the summary cards, the calendar and the unusual list update.
10. Disable JavaScript for a second: the page still shows the title and a clear message, not a blank screen. (CSV failure keeps the existing error line.)
11. Run `git status` and `git diff --stat`. Only `index.html`, `app.js`, `style.css`, `img/` and `i18n/` may change. No CSV change.

## 7. Report back

When you stop, send me:
- Which cards are done, which are not, and the time used.
- Anything that did not match the expected values, with the numbers.
- The list of changed files and the command to preview.
- One screenshot each: desktop and 360 px phone.
- Anything you decided on your own.

Do not push. Wait for my approval.
