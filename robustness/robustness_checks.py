# AI use: code and draft text produced with Claude (Anthropic), directed and reviewed by the team.
# Robustness checks for the Sabah MODIS-VIIRS harmonization (team SpaceZY, NASA Space Apps 2026).
# These checks do NOT change the method. The production ratio and the published CSV stay as they are.
#
# Run:  python robustness_checks.py sabah_raw_MODIS.csv sabah_raw_VIIRS.csv data/sabah_harmonized_monthly.csv
# Writes tables and figures to ./robustness_out/
#
# Baseline definitions (same as all earlier work):
#   area lat 4.0-7.5, lon 115.3-119.3; FIRMS archive rows (type == 0);
#   MODIS confidence >= 30 (Terra + Aqua); VIIRS S-NPP confidence n or h;
#   VIIRS used from Feb 2012 (first full month); learn Feb 2012 - Dec 2018, test Jan 2019 - Dec 2025.
import sys, os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats

RM, RV, HARM = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = "robustness_out"; os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250); pd.set_option("display.float_format", lambda x: "%.3f" % x)
NBOOT = 10000

def load():
    m, v = pd.read_csv(RM, low_memory=False), pd.read_csv(RV, low_memory=False)
    for d in (m, v):
        t = pd.to_datetime(d.acq_date); d["year"] = t.dt.year; d["month"] = t.dt.month
        d["minute"] = (d.acq_time // 100) * 60 + d.acq_time % 100
    box = lambda d: d[d.latitude.between(4.0, 7.5) & d.longitude.between(115.3, 119.3)]
    return box(m), box(v)

def monthly(m, v, mconf=30, vconf=("n", "h"), sat=None):
    m = m[(m["type"] == 0) & (m.confidence >= mconf)]
    if sat: m = m[m.satellite == sat]
    v = v[(v["type"] == 0) & v.confidence.astype(str).str.lower().isin(vconf)]
    idx = pd.MultiIndex.from_product([range(2003, 2026), range(1, 13)], names=["year", "month"])
    d = pd.DataFrame({"modis": m.groupby(["year", "month"]).size().reindex(idx, fill_value=0),
                      "viirs": v.groupby(["year", "month"]).size().reindex(idx, fill_value=0)}).reset_index()
    d["ym"] = d.year * 100 + d.month
    d.loc[d.ym < 201202, "viirs"] = np.nan
    return d

def evaluate(d, label):
    """Fixed ratio learned on Feb 2012 - Dec 2018, tested once on 2019 - 2025."""
    o = d[d.ym >= 201202]; tr, te = o[o.year <= 2018], o[o.year >= 2019]
    r = tr.viirs.sum() / tr.modis.sum(); edges = tr.viirs.quantile([.25, .5, .75]).values
    act, x = te.viirs.values, te.modis.values.astype(float); pred = x * r
    q = pd.qcut(pd.Series(act).rank(method="first"), 4, labels=False).values      # test months, quiet -> busy
    bias = [(pred[q == i].sum() - act[q == i].sum()) / act[q == i].sum() for i in range(4)]
    res = dict(label=label, modis_train=int(tr.modis.sum()), modis_test=int(te.modis.sum()),
               viirs_train=int(tr.viirs.sum()), viirs_test=int(te.viirs.sum()),
               ratio_train=r, ratio_test=te.viirs.sum() / te.modis.sum(),
               total_error=np.abs(pred - act).sum() / act.sum(), signed_bias=(pred.sum() - act.sum()) / act.sum(),
               MAE=np.abs(pred - act).mean(), RMSE=np.sqrt(((pred - act) ** 2).mean()),
               same_class_of_84=int((np.digitize(act, edges) == np.digitize(pred, edges)).sum()),
               zero_modis_months_test=int((x == 0).sum()),
               bias_q1_quiet=bias[0], bias_q2=bias[1], bias_q3=bias[2], bias_q4_busy=bias[3],
               error_q1_quiet=np.abs(pred[q == 0] - act[q == 0]).sum() / act[q == 0].sum(),
               error_q4_busy=np.abs(pred[q == 3] - act[q == 3]).sum() / act[q == 3].sum())
    for a, b, k in ((2019, 2022, "2019_2022"), (2023, 2025, "2023_2025")):
        s = te[(te.year >= a) & (te.year <= b)]; p = s.modis * r
        res["error_" + k] = np.abs(p - s.viirs).sum() / s.viirs.sum(); res["bias_" + k] = (p.sum() - s.viirs.sum()) / s.viirs.sum()
    rng = np.random.default_rng(7); V, M = tr.groupby("year").viirs.sum(), tr.groupby("year").modis.sum(); ys = V.index.values
    bs = [V[s].sum() / M[s].sum() for s in (rng.choice(ys, len(ys)) for _ in range(5000))]
    res["ratio_train_lo"], res["ratio_train_hi"] = np.percentile(bs, [2.5, 97.5])   # year-block bootstrap, 7 training years
    return res

m, v = load()
base = monthly(m, v); base["terra"] = monthly(m, v, sat="Terra").modis; base["aqua"] = monthly(m, v, sat="Aqua").modis
ov = base[base.ym >= 201202]

# ---------------------------------------------------------------- 0. baseline reproduces
b0 = evaluate(base, "Terra + Aqua (baseline)")
print("0. BASELINE CHECK  ratio %.2f  total error %.1f%%  same class %d/84  (expected 4.92, 24.3%%, 72)"
      % (b0["ratio_train"], 100 * b0["total_error"], b0["same_class_of_84"]))

# ---------------------------------------------------------------- 1. annual ratio stability
print("\n1. ANNUAL RATIO, 2012-2025 (2012 = Feb-Dec, 11 months)")
y = ov.groupby("year").agg(months=("viirs", "size"), viirs=("viirs", "sum"), modis=("modis", "sum"),
                           terra=("terra", "sum"), aqua=("aqua", "sum"))
rng = np.random.default_rng(1)
for c in ("modis", "terra", "aqua"):
    y["ratio_" + c] = y.viirs / y[c]
    y["zero_months_" + c] = ov.groupby("year")[c].apply(lambda s: int((s == 0).sum()))
    lo, hi = [], []
    for _, g in ov.groupby("year"):                       # rough range: resample that year's months
        a = g[["viirs", c]].values; n = len(a); bs = []
        for _ in range(4000):
            s = a[rng.integers(0, n, n)]
            if s[:, 1].sum() > 0: bs.append(s[:, 0].sum() / s[:, 1].sum())
        p = np.percentile(bs, [2.5, 97.5]); lo.append(p[0]); hi.append(p[1])
    y["lo_" + c], y["hi_" + c] = lo, hi
print(y[["months", "viirs", "modis", "terra", "aqua", "ratio_modis", "ratio_terra", "ratio_aqua",
         "zero_months_modis", "zero_months_terra", "zero_months_aqua"]].round(2).to_string())
y.round(3).to_csv(f"{OUT}/exp1_annual_ratio.csv")
whole = y.viirs.sum() / y.modis.sum()
print("  low-count years (MODIS Terra+Aqua < 260):", y.index[y.modis < 260].tolist())
for c, name in (("modis", "Terra + Aqua"), ("terra", "Terra only"), ("aqua", "Aqua only")):
    r = y["ratio_" + c]; w = y.viirs.sum() / y[c].sum()
    rho_t, p_t = stats.spearmanr(y.index, r); rho_a, p_a = stats.spearmanr(y.viirs, r)
    a, b = y.loc[2012:2022], y.loc[2023:2025]
    print(f"  {name:12s} whole-period {w:.2f}; annual min {r.min():.2f} max {r.max():.2f} median {r.median():.2f}; "
          f"years within 10% of whole-period: {int((abs(r / w - 1) <= 0.10).sum())}/14; "
          f"trend with year rho {rho_t:+.2f} (p {p_t:.2f}); link with annual VIIRS total rho {rho_a:+.2f} (p {p_a:.3f}); "
          f"2012-2022 {a.viirs.sum() / a[c].sum():.2f} vs 2023-2025 {b.viirs.sum() / b[c].sum():.2f}")
tr_ = ov[ov.year <= 2018]; rt = tr_.viirs.sum() / tr_.modis.sum(); ty = y.loc[2019:2025]
ye = (ty.modis * rt / ty.viirs - 1)
print("  yearly totals in test years, predicted with the training ratio %.2f: error by year " % rt
      + ", ".join("%d %+.0f%%" % (k, 100 * e) for k, e in ye.items())
      + "; mean size %.0f%%; all 7 years together %+.1f%%" % (100 * ye.abs().mean(), 100 * (ty.modis.sum() * rt / ty.viirs.sum() - 1)))
for a_, b_ in ((2003, 2011), (2012, 2022), (2023, 2025)):
    g = base[(base.year >= a_) & (base.year <= b_)]
    print("  Terra share of MODIS detections %d-%d: %.0f%%  (MODIS per year %.0f)" % (a_, b_, 100 * g.terra.sum() / g.modis.sum(), g.modis.sum() / (b_ - a_ + 1)))
day = lambda d: d[(d["type"] == 0) & (d.daynight == "D") & d.year.between(2003, 2025)]
md = day(m); md = md[md.confidence >= 30]
tm = md.groupby(["year", "satellite"]).minute.median().unstack(); tm["SNPP"] = day(v).groupby("year").minute.median()
print("  median daytime pass (UTC) of detections in the box:")
print(tm.map(lambda x: "" if pd.isna(x) else "%02d:%02d" % (x // 60, x % 60)).T.to_string())
tm.to_csv(f"{OUT}/exp1_overpass_minutes.csv")

BLUE, ORANGE, GREY, GREEN = "#2b6cb0", "#dd6b20", "#4a5568", "#2f855a"
plt.rcParams.update({"font.size": 12})
fig, ax = plt.subplots(1, 2, figsize=(15, 6), dpi=150); fig.subplots_adjust(left=.06, right=.98, top=.8, bottom=.16, wspace=.2)
a = ax[0]; yrs = y.index.values
a.axvspan(2022.5, 2025.5, color="#edf2f7", zorder=0); a.text(2024, 2.15, "Aqua and Terra\npasses drift", ha="center", va="bottom", fontsize=10, color=GREY)
for c, col, lab, off in (("modis", BLUE, "Terra + Aqua (baseline)", -.08), ("aqua", ORANGE, "Aqua only", .08)):
    a.errorbar(yrs + off, y["ratio_" + c], yerr=[y["ratio_" + c] - y["lo_" + c], y["hi_" + c] - y["ratio_" + c]],
               fmt="o-", color=col, capsize=3, lw=1.5, ms=5, label=lab, clip_on=True)
a.axhline(whole, color=BLUE, ls="--", lw=1); a.text(2016.5, 2.6, f"dashed line: whole period {whole:.2f}", color=BLUE, fontsize=10, ha="center")
a.set_ylim(2, 10); a.set_xticks(yrs); a.set_xticklabels([("2012*" if t == 2012 else str(t)) for t in yrs], rotation=45)
a.set_ylabel("VIIRS hotspots per MODIS hotspot (yearly)"); a.legend(frameon=False, loc="upper left")
a.set_title("A. Yearly ratio, 2012-2025", loc="left", fontweight="bold")
b = ax[1]
for c, col, lab in (("Aqua", ORANGE, "Aqua"), ("Terra", GREEN, "Terra"), ("SNPP", GREY, "Suomi NPP (VIIRS)")):
    b.plot(tm.index, tm[c] / 60, "o-", color=col, ms=4, lw=1.5, label=lab)
b.axvline(2011.5, color=GREY, ls=":", lw=1); b.text(2011.3, 7.25, "ratio applied here", ha="right", fontsize=10, color=GREY)
b.text(2011.7, 7.25, "ratio learned here", ha="left", fontsize=10, color=GREY)
b.set_ylim(1, 7.6); b.set_ylabel("Median daytime pass over Sabah (UTC hour)"); b.legend(frameon=False, loc="center left")
b.set_title("B. When each satellite passes, 2003-2025", loc="left", fontweight="bold")
for s in ax:
    for k in ("top", "right"): s.spines[k].set_visible(False)
fig.text(.06, .93, "Is the MODIS-to-VIIRS ratio steady over time?", fontsize=18, fontweight="bold")
fig.text(.06, .875, "Yearly ratio stays between 4.2 and 6.1 with no clear trend. The highest values fall in the quietest years. "
         "Bars: rough range from resampling that year's months.", fontsize=10.5, color=GREY)
fig.text(.06, .03, "* 2012 is February to December. Sabah box, FIRMS archive, baseline filters. Source: NASA FIRMS (MODIS C6.1, VIIRS S-NPP). "
         "Hotspots are not burned area.", fontsize=9.5, color=GREY)
fig.savefig(f"{OUT}/fig_exp1_annual_ratio.png"); plt.close(fig)

# ---------------------------------------------------------------- 2. interval for the 59% change
print("\n2. UNCERTAINTY FOR THE CHANGE IN AVERAGE YEARLY HOTSPOTS, 2003-2011 vs 2012-2025")
h = pd.read_csv(HARM); est = h[h.viirs.isna() | (h.viirs != h.harmonized)]
R = est.modis_adjusted.sum() / est.modis_raw.sum()                       # ratio in the published CSV
ya = lambda col, a, b: h[(h.year >= a) & (h.year <= b)].groupby("year")[col].sum().mean()
print("  formula: mean of yearly harmonized totals 2012-2025 / mean of yearly harmonized totals 2003-2011 - 1")
print("  published CSV: %.0f -> %.0f = %+.2f%%   (ratio in CSV %.3f; MODIS alone %+.2f%%)"
      % (ya("harmonized", 2003, 2011), ya("harmonized", 2012, 2025), 100 * (ya("harmonized", 2012, 2025) / ya("harmonized", 2003, 2011) - 1),
         R, 100 * (ya("modis_raw", 2012, 2025) / ya("modis_raw", 2003, 2011) - 1)))
pre = base[base.year <= 2011].groupby("year").modis.sum()                # 9 yearly MODIS totals
jan12 = base[(base.year == 2012) & (base.month == 1)].modis.values[0]    # Jan 2012 is estimated from MODIS
V, M = ov.groupby("year").viirs.sum(), ov.groupby("year").modis.sum()    # 14 overlap years
change = lambda r, E, Vs, n: (Vs.sum() + jan12 * r) / n / (r * E) - 1
point = change(R, pre.mean(), V, 14)
rng = np.random.default_rng(2026); A, B, RB = [], [], []
for _ in range(NBOOT):
    s = rng.choice(V.index.values, 14); r = V[s].sum() / M[s].sum(); RB.append(r)
    A.append(change(r, pre.mean(), V, 14))                               # A: only the ratio is uncertain
    p = rng.choice(pre.index.values, 9)
    B.append(change(r, pre[p].mean(), V[s], 14))                         # B: the years themselves are a sample
pc = lambda a: np.percentile(a, [2.5, 50, 97.5])
print("  recomputed from raw files: %+.2f%%" % (100 * point))
print("  ratio, year-block bootstrap: median %.2f, 95%% %.2f to %.2f" % (pc(RB)[1], pc(RB)[0], pc(RB)[2]))
print("  A. calibration only (resample the 14 overlap years to re-learn the ratio): median %+.1f%%, 95%% %+.1f%% to %+.1f%%"
      % (100 * pc(A)[1], 100 * pc(A)[0], 100 * pc(A)[2]))
print("  B. years as a sample (resample 9 early and 14 late years, ratio re-learned): median %+.1f%%, 95%% %+.1f%% to %+.1f%%; "
      "replicates showing a fall: %.1f%%" % (100 * pc(B)[1], 100 * pc(B)[0], 100 * pc(B)[2], 100 * np.mean(np.array(B) < 0)))
l1 = [(int(t), change(R, pre.drop(t).mean(), V, 14)) for t in pre.index]
l2 = [(int(t), (V.drop(t).sum() + (0 if t == 2012 else jan12 * R)) / 13 / (R * pre.mean()) - 1) for t in V.index]
f = lambda L: "%+.1f%% (drop %d) to %+.1f%% (drop %d)" % (100 * min(L, key=lambda t: t[1])[1], min(L, key=lambda t: t[1])[0],
                                                           100 * max(L, key=lambda t: t[1])[1], max(L, key=lambda t: t[1])[0])
print("  leave one early year out:", f(l1)); print("  leave one late year out: ", f(l2))
print("  yearly MODIS 2003-2011:", pre.to_dict())
print("  what if the true ratio before 2012 was different (systematic, not in the intervals):")
sc = [("lowest yearly ratio seen", y.ratio_modis.min()), ("busiest-quarter ratio", 4.79), ("baseline", R),
      ("highest yearly ratio seen", y.ratio_modis.max()), ("quietest-quarter ratio", 6.73)]
for lab, r in sc: print("    %-26s ratio %.2f -> change %+.1f%%" % (lab, r, 100 * change(r, pre.mean(), V, 14)))
P = V.sum() / 14
print("  ratio needed before 2012 for no change at all: %.2f; for a fall of only 50%%: %.2f" % (P / pre.mean(), P / pre.mean() / .5))
pd.DataFrame({"A_calibration_only": A, "B_years_as_sample": B, "ratio": RB}).round(5).to_csv(f"{OUT}/exp2_bootstrap.csv", index=False)

fig, a = plt.subplots(figsize=(11, 5.2), dpi=150); fig.subplots_adjust(left=.3, right=.96, top=.76, bottom=.2)
rowsF = [("Ratio uncertainty only\n(95%, bootstrap of overlap years)", pc(A)[0], pc(A)[2], BLUE),
         ("Leave any one year out\n(full range)", min(min(l1, key=lambda t: t[1])[1], min(l2, key=lambda t: t[1])[1]),
          max(max(l1, key=lambda t: t[1])[1], max(l2, key=lambda t: t[1])[1]), GREEN),
         ("If the pre-2012 ratio was the lowest\nor highest yearly ratio seen", change(y.ratio_modis.max(), pre.mean(), V, 14),
          change(y.ratio_modis.min(), pre.mean(), V, 14), ORANGE),
         ("Years treated as a sample\n(95%, bootstrap of early and late years)", pc(B)[0], pc(B)[2], GREY)]
for i, (lab, lo, hi, col) in enumerate(rowsF):
    yy = len(rowsF) - 1 - i; a.plot([100 * lo, 100 * hi], [yy, yy], color=col, lw=7, solid_capstyle="butt")
    a.text(100 * lo - 1, yy, "%.0f%%" % (100 * lo), ha="right", va="center", fontsize=11, color=GREY)
    a.text(100 * hi + 1, yy, "%.0f%%" % (100 * hi), ha="left", va="center", fontsize=11, color=GREY)
a.axvline(100 * point, color="#1a202c", lw=1.2, ls="--"); a.text(100 * point + 1, len(rowsF) - .45, "estimate %.0f%%" % (100 * point), ha="left", fontsize=11)
a.axvline(0, color=GREY, lw=1); a.set_yticks(range(len(rowsF))); a.set_yticklabels([r[0] for r in rowsF][::-1], fontsize=10.5)
a.set_xlim(-90, 10); a.set_ylim(-.6, len(rowsF) - .1); a.set_xlabel("Change in average yearly hotspots, 2003-2011 to 2012-2025 (%)")
for k in ("top", "right", "left"): a.spines[k].set_visible(False)
a.tick_params(axis="y", length=0)
fig.text(.04, .92, "How sure is the 59% fall?", fontsize=17, fontweight="bold")
fig.text(.04, .855, "Every check shows a fall. The size is less sure than the direction. Estimated hotspot counts, not burned area.", fontsize=10.5, color=GREY)
fig.text(.04, .03, "Sabah box. Source: NASA FIRMS (MODIS C6.1, VIIRS S-NPP).", fontsize=9.5, color=GREY)
fig.savefig(f"{OUT}/fig_exp2_change_interval.png"); plt.close(fig)

# ---------------------------------------------------------------- 3. Terra-only and Aqua-only hold-out
print("\n3. HOLD-OUT BY MODIS SATELLITE (same split, same filters)")
R3 = pd.DataFrame([b0, evaluate(monthly(m, v, sat="Terra"), "Terra only"), evaluate(monthly(m, v, sat="Aqua"), "Aqua only")]).set_index("label")
print(R3.T.to_string()); R3.round(4).to_csv(f"{OUT}/exp3_holdout_by_satellite.csv")

# ---------------------------------------------------------------- 4. confidence-filter sensitivity
print("\n4. CONFIDENCE FILTERS (set fixed before running; one sensor at a time, then both)")
t0m, t0v = m[m["type"] == 0], v[v["type"] == 0]
print("  MODIS confidence, all archive rows: <30 %d | 30-49 %d | 50-79 %d | >=80 %d"
      % ((t0m.confidence < 30).sum(), t0m.confidence.between(30, 49).sum(), t0m.confidence.between(50, 79).sum(), (t0m.confidence >= 80).sum()))
print("  VIIRS confidence, all archive rows:", t0v.confidence.value_counts().to_dict())
cfg = [("baseline: MODIS >= 30, VIIRS n+h", 30, ("n", "h")),
       ("MODIS >= 0 (keep all)", 0, ("n", "h")), ("MODIS >= 50", 50, ("n", "h")), ("MODIS >= 80 (extreme)", 80, ("n", "h")),
       ("VIIRS l+n+h (keep all)", 30, ("l", "n", "h")), ("VIIRS h only (extreme)", 30, ("h",)),
       ("both loosest: MODIS >= 0, VIIRS l+n+h", 0, ("l", "n", "h")), ("both strictest: MODIS >= 80, VIIRS h (extreme)", 80, ("h",))]
rows = []
with np.errstate(divide="ignore", invalid="ignore"):
    for lab, mc_, vc_ in cfg:
        d = monthly(m, v, mconf=mc_, vconf=vc_); res = evaluate(d, lab)
        o = d[d.ym >= 201202]; E = d[d.year <= 2011].groupby("year").modis.sum().mean(); rall = o.viirs.sum() / o.modis.sum()
        res.update(modis_kept_2003_2025=int(d.modis.sum()), viirs_kept_2012_2025=int(o.viirs.sum()),
                   zero_viirs_months_test=int((o[o.year >= 2019].viirs == 0).sum()), change_2003_11_to_2012_25=(o.viirs.sum() / 14) / (rall * E) - 1)
        rows.append(res)
R4 = pd.DataFrame(rows).set_index("label")
print(R4[["modis_kept_2003_2025", "viirs_kept_2012_2025", "ratio_train", "ratio_test", "total_error", "signed_bias", "same_class_of_84",
          "bias_q1_quiet", "bias_q4_busy", "zero_modis_months_test", "zero_viirs_months_test", "change_2003_11_to_2012_25"]].to_string())
R4.round(4).to_csv(f"{OUT}/exp4_confidence_filters.csv")
print("\nDone. Tables and figures are in", OUT)
