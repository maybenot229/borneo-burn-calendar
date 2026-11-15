import sys; sys.path.insert(0, 'src')
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pd.set_option('display.width', 230)
plt.rcParams.update({'font.size': 11, 'axes.grid': True, 'grid.alpha': .3})
mc = pd.read_csv(os.path.join(DATA, 'monthly_counts.csv'))
mc['ym'] = pd.to_datetime(dict(year=mc.year, month=mc.month, day=1)).dt.to_period('M')
mc = mc[(mc.ym >= '2012-02') & (mc.ym <= '2026-10')].copy()
mc['viirs'] = mc.viirs.fillna(0)
print('months Feb 2012-Oct 2026:', len(mc), ' VIIRS NaN-filled:', mc.viirs.isna().sum())
# quarters by rank of cleaned VIIRS count (ties broken by order)
mc['rank'] = mc.viirs.rank(method='first')
mc['quarter'] = pd.qcut(mc['rank'], 4, labels=['Q1 quietest', 'Q2', 'Q3', 'Q4 busiest'])
edges = mc.groupby('quarter', observed=True).viirs.agg(['min', 'max', 'count', 'sum', 'median'])
print(edges.to_string())
mc['ratio_terra_aqua'] = mc.viirs / (mc.modis_terra + mc.modis_aqua).replace(0, np.nan)
mc['ratio_aqua'] = mc.viirs / mc.modis_aqua.replace(0, np.nan)
mc.to_csv('intermediate/p5_month_quarters.csv', index=False)
# ratios kept separate
rr = mc.groupby('quarter', observed=True).apply(lambda g: pd.Series({
    'ratio_of_sums_TerraAqua': g.viirs.sum() / (g.modis_terra + g.modis_aqua).sum(),
    'mean_monthly_ratio_TerraAqua': g.ratio_terra_aqua.mean(),
    'ratio_of_sums_AquaOnly': g.viirs.sum() / g.modis_aqua.sum(),
    'mean_monthly_ratio_AquaOnly': g.ratio_aqua.mean(), 'months_with_zero_aqua': int((g.modis_aqua == 0).sum())}))
print('\nRATIOS (count level; separate definitions)'); print(rr.round(2).to_string()); rr.to_csv('intermediate/p5_ratios_by_quarter.csv')

so = pd.read_csv('intermediate/p3_viirs_classified_T15.csv', parse_dates=['t']); so['ym'] = so.t.dt.to_period('M')
so = so.merge(mc[['ym', 'quarter']], on='ym', how='left')
so = so[so.t < '2023-01-01']                       # drift period excluded from the comparison
print('\nVIIRS detections in primary period:', len(so), ' months per quarter (<=2022):', mc[mc.ym < '2023-01'].groupby('quarter', observed=True).size().to_dict())
Q = so.assign(lone=so.cl_n == 1)
rows = []
for dn in ('D', 'N'):
    for q, g in Q[Q.daynight == dn].groupby('quarter', observed=True):
        c = g[g.aqua_obs]
        rows.append(dict(dn=dn, quarter=q, n_viirs=len(g), match_rate_all=g.matched.mean(), share_aqua_covered=g.aqua_obs.mean(), n_covered=len(c),
                         match_rate_covered=c.matched.mean() if len(c) else np.nan, viirs_only_share_covered=(1 - c.matched.mean()) if len(c) else np.nan,
                         frp_q25=g.frp.quantile(.25), frp_med=g.frp.median(), frp_q75=g.frp.quantile(.75), lone_share=g.lone.mean(), cl_med=g.cl_n.median(),
                         frp_med_cov=c.frp.median() if len(c) else np.nan, lone_cov=c.lone.mean() if len(c) else np.nan, cl_med_cov=c.cl_n.median() if len(c) else np.nan))
T5 = pd.DataFrame(rows); T5.to_csv('intermediate/p5_quiet_busy_table.csv', index=False)
print('\nQUIET vs BUSY (2012-2022, T=15; covered = Aqua detected something in box within 15 min)'); print(T5.round(3).to_string(index=False))
# Aqua-side: share of Aqua pixels with VIIRS (when VIIRS-covered), by quarter
ao = pd.read_csv('intermediate/p3_aqua_classified_T15.csv', parse_dates=['t']); ao['ym'] = ao.t.dt.to_period('M'); ao = ao.merge(mc[['ym', 'quarter']], on='ym', how='left'); ao = ao[ao.t < '2023-01-01']
A = ao[ao.viirs_obs].groupby(['daynight', 'quarter'], observed=True).has_viirs.agg(['size', 'mean']).round(3); print('\nAqua pixels containing VIIRS | VIIRS covered, by quarter'); print(A.to_string())
print('all Aqua detections by quarter (<=2022):', ao.groupby('quarter', observed=True).size().to_dict())

# standardisation (day, covered): predicted match rate if each quarter's (FRP bin x cluster class) mix had the pooled match probabilities
FB = [0, 2, 3, 4, 6, 8, 12, 20, 40, 1e9]; CB = [0, 1, 2, 4, 9, 1e9]
g = Q[(Q.daynight == 'D') & Q.aqua_obs].copy()
g['cell'] = pd.cut(g.frp, FB).astype(str) + '|' + pd.cut(g.cl_n, CB).astype(str)
pool = g.groupby('cell').matched.mean(); g['pred'] = g.cell.map(pool)
S = g.groupby('quarter', observed=True).agg(n=('matched', 'size'), observed=('matched', 'mean'), predicted_from_mix=('pred', 'mean'))
print('\nSTANDARDISATION day covered: observed vs rate predicted from FRPxcluster mix alone'); print(S.round(3).to_string()); S.to_csv('intermediate/p5_standardisation_day.csv')
# bootstrap CI on observed per-quarter covered match rate (resampling clusters would be better; resample passes)
rng = np.random.default_rng(0); ci = {}
for q, gq in g.groupby('quarter', observed=True):
    pid = gq.groupby('pass_id').matched.agg(['sum', 'size']); b = []
    for _ in range(500):
        k = pid.sample(len(pid), replace=True, random_state=int(rng.integers(1e9))); b.append(k['sum'].sum() / k['size'].sum())
    ci[q] = np.percentile(b, [2.5, 97.5]).round(3)
print('pass-bootstrap 95% CI, day covered match rate:', {k: v.tolist() for k, v in ci.items()})
# ECDF of FRP by quarter (day, all VIIRS)
fig, axs = plt.subplots(1, 3, figsize=(15, 4.2)); cols = [OKABE[5], OKABE[3], OKABE[1], OKABE[6]]
for k, (q, gq) in enumerate(Q[Q.daynight == 'D'].groupby('quarter', observed=True)):
    x = np.sort(gq.frp.values); axs[0].plot(x, np.arange(1, len(x) + 1) / len(x), color=cols[k], ls=LS[k], lw=2, label=f'{q} (n={len(x)})')
axs[0].set_xscale('log'); axs[0].set_xlabel('VIIRS FRP (MW, log)'); axs[0].set_ylabel('cumulative share'); axs[0].set_title('Day FRP by activity quarter'); axs[0].legend(fontsize=8)
d = T5[T5.dn == 'D']; x = np.arange(4)
axs[1].plot(x, d.match_rate_covered, marker='o', color=OKABE[5], ls='-', lw=2, label='Aqua-covered VIIRS')
axs[1].plot(x, d.match_rate_all, marker='s', color=OKABE[6], ls='--', lw=2, label='all VIIRS')
axs[1].plot(x, S.predicted_from_mix.values, marker='^', color=OKABE[3], ls=':', lw=2, label='predicted from FRPxcluster mix (covered)')
axs[1].set_xticks(x); axs[1].set_xticklabels(['Q1\nquietest', 'Q2', 'Q3', 'Q4\nbusiest']); axs[1].set_ylabel('match rate'); axs[1].set_ylim(0, .6); axs[1].legend(fontsize=8); axs[1].set_title('Day match rate by quarter (2012-2022)')
axs[2].plot(x, d.lone_share, marker='o', color=OKABE[5], ls='-', lw=2, label='lone-pixel share'); axs[2].plot(x, d.share_aqua_covered, marker='s', color=OKABE[1], ls='--', lw=2, label='share Aqua-covered')
axs[2].set_xticks(x); axs[2].set_xticklabels(['Q1\nquietest', 'Q2', 'Q3', 'Q4\nbusiest']); axs[2].set_ylim(0, 1); axs[2].legend(fontsize=8); axs[2].set_title('Day: isolation and coverage by quarter')
plt.tight_layout(); plt.savefig('figures/fig_quiet_vs_busy.png', dpi=150); plt.close(); print('figure written')
