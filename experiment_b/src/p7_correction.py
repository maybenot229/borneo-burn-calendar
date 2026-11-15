import sys; sys.path.insert(0, 'src')
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
mc = pd.read_csv(os.path.join(DATA, 'monthly_counts.csv'))
mc['ym'] = pd.to_datetime(dict(year=mc.year, month=mc.month, day=1)).dt.to_period('M')
mc = mc[(mc.ym >= '2012-02') & (mc.ym <= '2026-10')].copy(); mc['modis'] = mc.modis_terra + mc.modis_aqua
learn = mc[mc.ym <= '2018-12']; test = mc[(mc.ym >= '2019-01') & (mc.ym <= '2025-12')]
EDGES = [74, 204, 376]
cls = lambda x: np.digitize(np.asarray(x, float), EDGES, right=False)     # 4 classes
wape = lambda p, y: np.abs(np.asarray(p, float) - y).sum() / y.sum()
agree = lambda p, y: (cls(p) == cls(y)).mean()
y = test.viirs.values.astype(float)
r = learn.viirs.sum() / learn.modis.sum()
res = {}
res['ratio of sums (baseline)'] = r * test.modis.values
b1, a1 = np.polyfit(learn.modis, learn.viirs, 1); res['straight line (baseline)'] = a1 + b1 * test.modis.values
# edge convention check for the baseline 86%
for right in (False, True):
    c = lambda x: np.digitize(np.asarray(x, float), EDGES, right=right)
    print('edge right=%s agreement of ratio-of-sums:' % right, (c(res['ratio of sums (baseline)']) == c(y)).mean().round(3))
# pre-declared correction: power law  viirs = k * modis^b  (log-log OLS on months with modis>0 and viirs>0), smearing correction
L = learn[(learn.modis > 0) & (learn.viirs > 0)]
b, la = np.polyfit(np.log(L.modis), np.log(L.viirs), 1); resid = np.log(L.viirs) - (la + b * np.log(L.modis)); smear = np.exp(resid).mean()
print(f'power law fit (learn n={len(L)}): viirs = {np.exp(la):.3f} * modis^{b:.3f}; smearing {smear:.3f}; implied ratio at modis=5: {np.exp(la)*5**(b-1):.2f}, 50: {np.exp(la)*50**(b-1):.2f}, 500: {np.exp(la)*500**(b-1):.2f}')
pl = np.where(test.modis.values > 0, smear * np.exp(la) * np.maximum(test.modis.values, 1e-9) ** b, np.nan)
res['power law (activity-dependent)'] = np.where(np.isnan(pl), r * test.modis.values, pl)    # months with 0 MODIS fall back to ratio
print('test months with modis==0:', int((test.modis == 0).sum()))
out = pd.DataFrame({k: {'WAPE (total error)': wape(v, y), 'colour-class agreement': agree(v, y), '|sum error|': abs(np.sum(v) - y.sum()) / y.sum()} for k, v in res.items()}).T
print(out.round(3).to_string()); out.round(4).to_csv('intermediate/p7_correction_holdout.csv')
print('targets to beat: WAPE < 0.243 AND class agreement > 0.86')
# class agreement by quiet class and error by quarter of test months
q = pd.qcut(test.viirs.rank(method='first'), 4, labels=['Q1', 'Q2', 'Q3', 'Q4']).values
for k, v in res.items():
    print(k, 'WAPE by test-activity quarter:', {qq: round(wape(v[q == qq], y[q == qq]), 3) for qq in ('Q1', 'Q2', 'Q3', 'Q4')}, ' signed bias (pred-actual)/actual:', {qq: round((v[q == qq].sum() - y[q == qq].sum()) / y[q == qq].sum(), 3) for qq in ('Q1', 'Q2', 'Q3', 'Q4')})
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(learn.modis, learn.viirs, s=14, color=OKABE[5], label='learn 2012-2018'); ax.scatter(test.modis, test.viirs, s=14, color=OKABE[6], marker='s', label='test 2019-2025')
xx = np.linspace(1, learn.modis.max() * 1.3, 200); ax.plot(xx, r * xx, color=OKABE[0], ls='--', lw=2, label=f'ratio {r:.2f}'); ax.plot(xx, smear * np.exp(la) * xx ** b, color=OKABE[3], ls='-', lw=2, label=f'power law b={b:.2f}')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('MODIS (Terra+Aqua) monthly count'); ax.set_ylabel('VIIRS monthly count'); ax.legend(fontsize=8); plt.tight_layout(); plt.savefig('figures/fig_correction_holdout.png', dpi=150)
