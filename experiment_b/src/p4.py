import sys; sys.path.insert(0, 'src')
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pd.set_option('display.width', 220)
plt.rcParams.update({'font.size': 11, 'axes.grid': True, 'grid.alpha': .3})
so = pd.read_csv('intermediate/p3_viirs_classified_T15.csv', parse_dates=['t'])
so['year'] = so.t.dt.year
P = so[so.year <= 2022]                       # primary period (Aqua overpass aligned)
C = P[P.aqua_obs]                             # Aqua-covered: Aqua detected a fire somewhere in the box within 15 min
FRP_BINS = [0, 2, 3, 4, 6, 8, 12, 20, 40, 1e9]; FRP_LAB = ['<2', '2-3', '3-4', '4-6', '6-8', '8-12', '12-20', '20-40', '40+']
CL_BINS = [0, 1, 2, 4, 9, 1e9]; CL_LAB = ['1', '2', '3-4', '5-9', '10+']

def desc(x, col):
    q = x[col].quantile([.1, .25, .5, .75, .9, .99])
    return pd.Series({'n': len(x), 'mean': x[col].mean(), 'p10': q[.1], 'q25': q[.25], 'med': q[.5], 'q75': q[.75], 'p90': q[.9], 'p99': q[.99]})

out = []
for samp, cond in (('all VIIRS', P), ('Aqua-covered', C)):
    for dn in 'DN':
        for col in ('frp', 'brightness', 'bright_t31', 'cl_n', 'cl_frp'):
            for mm, g in cond[cond.daynight == dn].groupby('matched'):
                r = desc(g, col); r['sample'] = samp; r['dn'] = dn; r['var'] = col; r['group'] = 'matched' if mm else 'VIIRS-only'; out.append(r)
D = pd.DataFrame(out); D.to_csv('intermediate/p4_distribution_stats.csv', index=False)
print(D[D['sample'] == 'Aqua-covered'].round(2)[['dn', 'var', 'group', 'n', 'mean', 'p10', 'q25', 'med', 'q75', 'p90', 'p99']].to_string(index=False))
print('\nALL VIIRS FRP/cl_n medians'); print(D[(D['sample'] == 'all VIIRS') & D['var'].isin(['frp', 'cl_n'])].round(2)[['dn', 'var', 'group', 'n', 'q25', 'med', 'q75', 'p90']].to_string(index=False))

# confidence, lone share, acquisition time
for samp, cond in (('all VIIRS', P), ('Aqua-covered', C)):
    print(f'\n[{samp}] confidence h share / lone-pixel share / median UTC minute-of-day')
    cond = cond.assign(lone=cond.cl_n == 1, mins=cond.t.dt.hour * 60 + cond.t.dt.minute)
    print(cond.groupby(['daynight', 'matched']).agg(n=('lone', 'size'), h_share=('confidence', lambda s: (s == 'h').mean()), lone=('lone', 'mean'), mins=('mins', 'median')).round(3).to_string())

# match probability by FRP bin and by cluster size (Aqua-covered, primary period)
for dn in 'DN':
    g = C[C.daynight == dn].assign(fb=lambda d: pd.cut(d.frp, FRP_BINS, labels=FRP_LAB), cb=lambda d: pd.cut(d.cl_n, CL_BINS, labels=CL_LAB))
    print(f'\n[{dn}] match prob by FRP bin'); print(g.groupby('fb', observed=True).matched.agg(['size', 'mean']).round(3).T.to_string())
    print(f'[{dn}] match prob by cluster size'); print(g.groupby('cb', observed=True).matched.agg(['size', 'mean']).round(3).T.to_string())
    if dn == 'D':
        t = g.groupby(['fb', 'cb'], observed=True).matched.agg(['size', 'mean']).reset_index()
        piv = t.pivot(index='fb', columns='cb', values='mean').round(2); nn = t.pivot(index='fb', columns='cb', values='size')
        print('\n[D] match prob: FRP bin (rows) x cluster size (cols); cells with n<20 blanked'); print(piv.where(nn >= 20).to_string())
        print('n per cell'); print(nn.to_string())
        piv.where(nn >= 20).to_csv('intermediate/p4_match_prob_frp_by_cluster_day.csv')
        # cluster-FRP (sum) too
        g2 = g.assign(sb=pd.cut(g.cl_frp, [0, 5, 10, 20, 50, 100, 200, 1e9], labels=['<5', '5-10', '10-20', '20-50', '50-100', '100-200', '200+']))
        print('[D] match prob by summed cluster FRP'); print(g2.groupby('sb', observed=True).matched.agg(['size', 'mean']).round(3).T.to_string())
# ambiguous (multi-Aqua) share and multiple VIIRS per Aqua pixel (Phase 3 requirement)
M = P[P.matched]; print('\nmatched VIIRS with >1 Aqua candidate:', (M.n_cand > 1).mean().round(3), ' of n', len(M))

# ---------- figures ----------
def ecdf(ax, x, **k):
    x = np.sort(x.values); ax.plot(x, np.arange(1, len(x) + 1) / len(x), **k)
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, dn, ttl in zip(axs, 'DN', ('Day', 'Night')):
    for (samp, cond, col, ls) in (('Aqua-covered', C, OKABE[5], '-'), ('all VIIRS', P, OKABE[6], '--')):
        g = cond[cond.daynight == dn]
        ecdf(ax, g[g.matched].frp, color=col, ls=ls if samp == 'Aqua-covered' else ':', lw=2, label=f'matched ({samp}) n={int(g.matched.sum())}' if samp == 'Aqua-covered' else None)
        ecdf(ax, g[~g.matched].frp, color=OKABE[1] if samp == 'Aqua-covered' else OKABE[7], ls='--' if samp == 'Aqua-covered' else '-.', lw=2, label=f'VIIRS-only ({samp}) n={int((~g.matched).sum())}')
    ax.set_xscale('log'); ax.set_xlabel('VIIRS FRP (MW, log)'); ax.set_ylabel('cumulative share'); ax.set_title(f'{ttl}, 2012-2022, T=15 min'); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('figures/fig_frp_ecdf_matched_vs_viirsonly.png', dpi=150); plt.close()

fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
for dn, col, ls, mk in (('D', OKABE[5], '-', 'o'), ('N', OKABE[6], '--', 's')):
    g = C[C.daynight == dn].assign(fb=lambda d: pd.cut(d.frp, FRP_BINS, labels=FRP_LAB), cb=lambda d: pd.cut(d.cl_n, CL_BINS, labels=CL_LAB))
    for ax, key, labs in ((axs[0], 'fb', FRP_LAB), (axs[1], 'cb', CL_LAB)):
        r = g.groupby(key, observed=True).matched.agg(['size', 'mean']).reindex(labs)
        ok = r['size'] >= 20
        se = np.sqrt(r['mean'] * (1 - r['mean']) / r['size'])
        ax.errorbar(np.arange(len(labs))[ok.values], r['mean'][ok], yerr=1.96 * se[ok], color=col, ls=ls, marker=mk, lw=2, capsize=3, label={'D': 'Day', 'N': 'Night (bins with n>=20)'}[dn])
        ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs)
axs[0].set_xlabel('VIIRS FRP (MW)'); axs[1].set_xlabel('VIIRS pixels in cluster');
for ax in axs[:2]: ax.set_ylabel('share matched to an Aqua pixel'); ax.set_ylim(0, 1); ax.legend()
axs[0].set_title('Match probability vs FRP'); axs[1].set_title('Match probability vs cluster size')
g = C[C.daynight == 'D'].assign(fb=lambda d: pd.cut(d.frp, [0, 4, 8, 20, 1e9], labels=['<4', '4-8', '8-20', '20+']), cb=lambda d: pd.cut(d.cl_n, [0, 1, 4, 1e9], labels=['1 px', '2-4 px', '5+ px']))
for k, (lab, grp) in enumerate(g.groupby('cb', observed=True)):
    r = grp.groupby('fb', observed=True).matched.agg(['size', 'mean']); r = r[r['size'] >= 20]
    axs[2].plot([['<4', '4-8', '8-20', '20+'].index(i) for i in r.index], r['mean'], marker='o', lw=2, ls=LS[k], color=[OKABE[5], OKABE[3], OKABE[6]][k], label=f'cluster {lab}')
axs[2].set_xticks(range(4)); axs[2].set_xticklabels(['<4', '4-8', '8-20', '20+']); axs[2].set_xlabel('VIIRS FRP (MW)'); axs[2].set_ylabel('share matched'); axs[2].set_ylim(0, 1)
axs[2].set_title('Day: FRP effect within cluster size'); axs[2].legend()
plt.tight_layout(); plt.savefig('figures/fig_match_prob_frp_clustersize.png', dpi=150); plt.close()
print('figures written')
