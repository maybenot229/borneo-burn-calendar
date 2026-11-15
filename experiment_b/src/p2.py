import sys; sys.path.insert(0, 'src')
from common import *; from match import *
pd.set_option('display.width', 220)
m, v = load_raw(); a, s = clean(m, v)
w = lambda d: d[(d.t >= '2016-03-01') & (d.t < '2016-05-01')]
a16, s16 = w(a), w(s)
print('Mar-Apr 2016: Aqua', len(a16), 'SNPP', len(s16))
s16 = add_clusters(s16)
rows = []; keep = {}
for mode, scale, lab in (('rect', 1.0, 'rect x1.0'), ('rect', 1.5, 'rect x1.5'), ('radius', 1.0, 'radius 1 km')):
    for T in (5, 15, 30, 60):
        so, ao = match(a16, s16, T=T, mode=mode, scale=scale)
        keep[(lab, T)] = (so, ao)
        for dn in ('D', 'N', 'all'):
            ss = so if dn == 'all' else so[so.daynight == dn]; aa = ao if dn == 'all' else ao[ao.daynight == dn]
            sc = ss[ss.aqua_obs]; ac = aa[aa.viirs_obs]
            rows.append(dict(rule=lab, T=T, dn=dn, n_viirs=len(ss), matched=ss.matched.sum(), match_rate=ss.matched.mean(),
                             n_viirs_aqobs=len(sc), match_rate_aqobs=sc.matched.mean() if len(sc) else np.nan,
                             n_aqua=len(aa), aqua_with_viirs=aa.has_viirs.sum(), aqua_pix_rate=aa.has_viirs.mean(),
                             n_aqua_viirsobs=len(ac), aqua_pix_rate_viirsobs=ac.has_viirs.mean() if len(ac) else np.nan,
                             aqua_only=(~aa.has_viirs).sum(), mean_viirs_per_matched_aqua=aa.loc[aa.has_viirs, 'n_viirs'].mean(),
                             ambiguous=(ss.n_cand > 1).sum()))
R = pd.DataFrame(rows); R.to_csv('intermediate/p2_match_rates.csv', index=False)
print(R.round(3).to_string(index=False))
so, ao = keep[('rect x1.0', 15)]
so.to_csv('intermediate/p2_viirs_classified_2016.csv', index=False); ao.to_csv('intermediate/p2_aqua_classified_2016.csv', index=False)

def desc(x, col):
    q = x[col].quantile([.1, .25, .5, .75, .9])
    return pd.Series({'n': len(x), 'mean': x[col].mean(), 'p10': q[.1], 'q25': q[.25], 'med': q[.5], 'q75': q[.75], 'p90': q[.9]})
for cond, lab in ((so, 'ALL VIIRS'), (so[so.aqua_obs], 'VIIRS with Aqua detection in box within 15 min')):
    for col in ('frp', 'brightness', 'cl_n', 'cl_frp'):
        t = pd.concat({(dn, 'matched' if mm else 'VIIRS-only'): desc(g, col) for (dn, mm), g in cond.groupby(['daynight', 'matched'])}, axis=1).T
        print(f'\n{lab} -- {col}'); print(t.round(2).to_string())
    print(f'\n{lab} -- confidence share')
    print(pd.crosstab([cond.daynight, cond.matched], cond.confidence, normalize='index').round(3).to_string())
    cond = cond.assign(lone=cond.cl_n == 1, cls=pd.cut(cond.cl_n, [0, 1, 2, 4, 9, 1e9], labels=['1', '2', '3-4', '5-9', '10+']))
    print('match prob by cluster size')
    print(cond.groupby(['daynight', 'cls'], observed=True).matched.agg(['size', 'mean']).round(3).to_string())
    print('share lone-pixel', cond.groupby(['daynight', 'matched']).lone.mean().round(3).to_dict())

# inspection sample (day)
smp = pd.concat([so[so.matched & (so.daynight == 'D')].sample(8, random_state=1),
                 so[(~so.matched) & so.aqua_obs & (so.daynight == 'D')].sample(8, random_state=1)])
print('\nSample (day): first 8 matched, last 8 unmatched-with-Aqua-observed')
print(smp[['latitude', 'longitude', 't', 'frp', 'confidence', 'cl_n', 'matched', 'n_cand', 'aqua_id']].to_string())
ax, ay = km_xy(ao.latitude, ao.longitude)
um = so[(~so.matched) & so.aqua_obs & (so.daynight == 'D')]
sx, sy = km_xy(um.latitude, um.longitude)
at = ao.t.values.astype('datetime64[s]').astype('int64') / 60; st = um.t.values.astype('datetime64[s]').astype('int64') / 60
dm = []
for i in range(len(um)):
    ok = np.abs(at - st[i]) <= 15
    dm.append(np.hypot(ax[ok] - sx[i], ay[ok] - sy[i]).min() if ok.any() else np.nan)
print('unmatched day VIIRS w/ Aqua obs: nearest in-time Aqua centre distance (km) q25/50/75/90:', np.nanpercentile(dm, [25, 50, 75, 90]).round(1))
print('Aqua scan/track median:', ao.scan.median(), ao.track.median())
