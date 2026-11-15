# AI use: code and draft text produced with Claude (Anthropic), directed and reviewed by the team.
# Method checks for the Sabah MODIS-VIIRS harmonization (team SpaceZY, NASA Space Apps 2026).
# Run:  python method_checks.py monthly_counts.csv sabah_raw_MODIS.csv sabah_raw_VIIRS.csv
# Split used everywhere: learn Feb 2012 - Dec 2018, test Jan 2019 - Dec 2025.
import sys, numpy as np, pandas as pd
from scipy.optimize import minimize

mc = pd.read_csv(sys.argv[1]); mc["ym"] = mc.year * 100 + mc.month
both = mc[(mc.ym >= 201202) & (mc.year <= 2025)].dropna(subset=["modis_raw", "viirs"])
tr, te = both[both.year <= 2018], both[both.year >= 2019].copy()
edges = tr.viirs.quantile([.25, .5, .75]).values          # colour-class edges (74, 204, 376)

def lad(d):  # "base + ratio" line, fitted by least absolute error
    x, y = d.modis_raw.values.astype(float), d.viirs.values.astype(float)
    return minimize(lambda p: np.abs(y - (p[0] * x + p[1])).sum(), [y.sum() / x.sum(), 0],
                    method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-6, maxiter=20000)).x

r = tr.viirs.sum() / tr.modis_raw.sum(); a, b = lad(tr)
act, x = te.viirs.values, te.modis_raw.values.astype(float)
q = pd.qcut(pd.Series(act).rank(method="first"), 4, labels=False).values   # test months ranked quiet -> busy

print(f"A. SECOND METHOD. fixed ratio {r:.2f};  base + ratio: viirs = {a:.2f} x modis + {b:.1f}")
for name, pred in [("fixed ratio", x * r), ("base + ratio", np.clip(a * x + b, 0, None))]:
    same = (np.digitize(act, edges) == np.digitize(pred, edges)).sum()
    bias = [(pred[q == i].sum() - act[q == i].sum()) / act[q == i].sum() for i in range(4)]
    print(f"  {name:12s} total error {np.abs(pred - act).sum() / act.sum():.1%}   same colour class {same}/{len(act)}"
          f"   bias by quarter, quiet to busy: " + " ".join(f"{v:+.0%}" for v in bias))

allov = both; R = allov.viirs.sum() / allov.modis_raw.sum(); A, B = lad(allov)
pre = mc[(mc.year >= 2003) & (mc.year <= 2011)]; xp = pre.modis_raw.values.astype(float)
late = mc[(mc.year >= 2012) & (mc.year <= 2025)].groupby("year").viirs.sum().mean()
print(f"  refit on all overlap years: ratio {R:.2f};  base + ratio {A:.2f} x modis + {B:.1f}")
print(f"  months 2003-2011: {len(pre)}; with zero MODIS: {(xp == 0).sum()}; colour differs between the two methods in "
      f"{(np.digitize(xp * R, edges) != np.digitize(A * xp + B, edges)).sum()} months")
for name, p in [("fixed ratio", xp * R), ("base + ratio", A * xp + B)]:
    early = pd.Series(p, index=pre.year.values).groupby(level=0).sum().mean()
    print(f"  {name:12s} average per year 2003-2011 {early:.0f} -> 2012-2025 {late:.0f}  ({late / early - 1:+.0%})")

print("\nB. ERRORS AND RATIO BY CALENDAR MONTH (test years, fixed ratio)")
te["pred"] = te.modis_raw * r; te["ae"] = (te.pred - te.viirs).abs()
g = te.groupby("month").agg(real=("viirs", "sum"), pred=("pred", "sum"), ae=("ae", "sum"))
g["bias_%"] = ((g.pred - g.real) / g.real * 100).round(0); g["abs_err_%"] = (g.ae / g.real * 100).round(0)
g["ratio_train"] = (tr.groupby("month").viirs.sum() / tr.groupby("month").modis_raw.sum()).round(2)
g["ratio_test"] = (te.groupby("month").viirs.sum() / te.groupby("month").modis_raw.sum()).round(2)
print(g[["real", "bias_%", "abs_err_%", "ratio_train", "ratio_test"]].to_string())
print(f"  does the month-by-month ratio pattern repeat? correlation train vs test: {g.ratio_train.corr(g.ratio_test):.2f} (1 = repeats, 0 = noise)")
y = te.groupby("year").agg(real=("viirs", "sum"), modis=("modis_raw", "sum")); y["ratio"] = (y.real / y.modis).round(2)
print("  ratio by test year:", y.ratio.to_dict())

print("\nC. GEOGRAPHY. Sabah box cut into 4 at its midpoints (lat 5.75, lon 117.3)")
def clean(path, modis):
    d = pd.read_csv(path, low_memory=False); d = d[d["type"] == 0]
    d = d[pd.to_numeric(d.confidence, errors="coerce") >= 30] if modis else d[d.confidence.astype(str).str.lower().isin(["n", "h"])]
    t = pd.to_datetime(d.acq_date); d = d.assign(year=t.dt.year, month=t.dt.month)
    d = d[d.latitude.between(4.0, 7.5) & d.longitude.between(115.3, 119.3) & (d.year * 100 + d.month >= 201202) & (d.year <= 2025)]
    return d.assign(q=np.where(d.latitude >= 5.75, "N", "S") + np.where(d.longitude >= 117.3, "E", "W"))
idx = pd.MultiIndex.from_product([range(2012, 2026), range(1, 13), ["NE", "NW", "SE", "SW"]], names=["year", "month", "q"])
mm = pd.concat([clean(sys.argv[2], True).groupby(["year", "month", "q"]).size().reindex(idx, fill_value=0).rename("m"),
                clean(sys.argv[3], False).groupby(["year", "month", "q"]).size().reindex(idx, fill_value=0).rename("v")], axis=1).reset_index()
mm = mm[mm.year * 100 + mm.month >= 201202]; trq, teq = mm[mm.year <= 2018], mm[mm.year >= 2019].copy()
rq = trq.groupby("q").v.sum() / trq.groupby("q").m.sum()
geo = pd.DataFrame({"ratio_train": rq.round(2), "ratio_test": (teq.groupby("q").v.sum() / teq.groupby("q").m.sum()).round(2),
                    "share_of_viirs_%": (mm.groupby("q").v.sum() / mm.v.sum() * 100).round(0)})
teq["p_one"] = teq.m * r; teq["p_own"] = teq.m * teq.q.map(rq)
geo["err_one_ratio_%"] = teq.groupby("q").apply(lambda d: (d.p_one - d.v).abs().sum() / d.v.sum() * 100, include_groups=False).round(0)
geo["bias_one_ratio_%"] = teq.groupby("q").apply(lambda d: (d.p_one.sum() - d.v.sum()) / d.v.sum() * 100, include_groups=False).round(0)
print(geo.to_string())
tot = teq.groupby(["year", "month"])[["v", "p_one", "p_own"]].sum()
for k, name in [("p_one", "one ratio for all Sabah"), ("p_own", "own ratio per quadrant ")]:
    print(f"  {name}: Sabah-wide total error {(tot[k] - tot.v).abs().sum() / tot.v.sum():.1%}, "
          f"same colour class {(np.digitize(tot.v, edges) == np.digitize(tot[k], edges)).sum()}/{len(tot)}")
