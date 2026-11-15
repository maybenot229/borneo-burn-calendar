import sys; sys.path.insert(0, 'src')
from common import *; from match import *
pd.set_option('display.width', 220)
m, v = load_raw(); a, s = clean(m, v)
# archive ends: MODIS 2026-08-31, VIIRS 2026-07-31 -> common archive window ends 2026-07-31
END = '2026-08-01'
a = a[a.t < END]; s = s[s.t < END]
print('Full overlap Feb 2012 - Jul 2026: Aqua', len(a), 'SNPP', len(s))
s = add_clusters(s)
print('VIIRS clusters', s.cluster.nunique(), 'lone share of detections', (s.cl_n == 1).mean().round(3))
rows = []; keep = {}
for mode, scale, lab in (('rect', 1.0, 'rect x1.0'), ('rect', 1.5, 'rect x1.5'), ('radius', 1.0, 'radius 1 km')):
    for T in (5, 15, 30, 60):
        so, ao = match(a, s, T=T, mode=mode, scale=scale); keep[(lab, T)] = (so, ao)
        for per, (lo, hi) in {'2012-2022': ('2012-02-01', '2023-01-01'), '2023+': ('2023-01-01', END), 'all': ('2012-02-01', END)}.items():
            for dn in ('D', 'N', 'all'):
                ss = so[(so.t >= lo) & (so.t < hi)]; aa = ao[(ao.t >= lo) & (ao.t < hi)]
                if dn != 'all': ss = ss[ss.daynight == dn]; aa = aa[aa.daynight == dn]
                sc = ss[ss.aqua_obs]; ac = aa[aa.viirs_obs]
                rows.append(dict(rule=lab, T=T, period=per, dn=dn, n_aqua=len(aa), n_viirs=len(ss), viirs_matched=int(ss.matched.sum()),
                                 viirs_only=int((~ss.matched).sum()), ambiguous=int((ss.n_cand > 1).sum()),
                                 aqua_pix_with_viirs=int(aa.has_viirs.sum()), aqua_only=int((~aa.has_viirs).sum()),
                                 mean_viirs_per_aqua_pix=aa.loc[aa.has_viirs, 'n_viirs'].mean(),
                                 match_rate=ss.matched.mean(), n_aqobs=len(sc), match_rate_aqobs=sc.matched.mean() if len(sc) else np.nan,
                                 n_aqua_viirsobs=len(ac), aqua_pix_rate_viirsobs=ac.has_viirs.mean() if len(ac) else np.nan,
                                 aqua_only_share_viirsobs=(1 - ac.has_viirs.mean()) if len(ac) else np.nan))
R = pd.DataFrame(rows); R.to_csv('intermediate/p3_match_summary.csv', index=False)
print(R[(R.rule == 'rect x1.0')].round(3).to_string(index=False))
print(R[(R['T'] == 15) & (R.period == '2012-2022') & (R.dn != 'all')][['rule', 'dn', 'n_viirs', 'match_rate', 'n_aqobs', 'match_rate_aqobs', 'n_aqua_viirsobs', 'aqua_pix_rate_viirsobs']].round(3).to_string(index=False))
so, ao = keep[('rect x1.0', 15)]
so.to_csv('intermediate/p3_viirs_classified_T15.csv', index=False); ao.to_csv('intermediate/p3_aqua_classified_T15.csv', index=False)
for T in (5, 30, 60):
    keep[('rect x1.0', T)][0][['latitude', 'longitude', 't', 'matched', 'n_cand', 'aqua_id', 'aqua_obs']].to_csv(f'intermediate/p3_viirs_classified_T{T}.csv', index=False)
# by year (Extra-1 style, T=15)
so['year'] = so.t.dt.year; ao['year'] = ao.t.dt.year
yr = so.groupby('year').agg(n_viirs=('matched', 'size'), match_rate=('matched', 'mean'), n_aqobs=('aqua_obs', 'sum'))
yr['match_rate_aqobs'] = so[so.aqua_obs].groupby('year').matched.mean()
yr['aqua_pix_rate_viirsobs'] = ao[ao.viirs_obs].groupby('year').has_viirs.mean(); yr['n_aqua_viirsobs'] = ao.groupby('year').viirs_obs.sum()
print(yr.round(3).to_string()); yr.to_csv('intermediate/p3_by_year_T15.csv')
