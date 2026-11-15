import sys; sys.path.insert(0, 'src')
from common import *
from scipy.spatial import cKDTree
pd.set_option('display.width', 220)
so = pd.read_csv('intermediate/p3_viirs_classified_T15.csv', parse_dates=['t']); so = so[so.t < '2023-01-01'].copy()
ao = pd.read_csv('intermediate/p3_aqua_classified_T15.csv', parse_dates=['t']); ao = ao[ao.t < '2023-01-01'].copy()
# ---- cluster-level matching: cluster matched if any member matched ----
cl = so.groupby('cluster').agg(daynight=('daynight', 'first'), n=('cl_n', 'first'), frp_sum=('cl_frp', 'first'), frp_max=('frp', 'max'),
                              matched=('matched', 'max'), covered=('aqua_obs', 'max'), t=('t', 'first'))
print('clusters 2012-2022:', len(cl), ' matched', int(cl.matched.sum()), f'({cl.matched.mean():.3f})')
FB = [0, 4, 8, 20, 1e9]; FL = ['<4', '4-8', '8-20', '20+']; CB = [0, 1, 2, 4, 1e9]; CL = ['1 px', '2 px', '3-4 px', '5+ px']
for dn in 'DN':
    c = cl[(cl.daynight == dn) & cl.covered].assign(fb=lambda d: pd.cut(d.frp_max, FB, labels=FL), cb=lambda d: pd.cut(d.n, CB, labels=CL))
    print(f'\n[{dn}] Aqua-covered clusters n={len(c)}, matched {c.matched.mean():.3f}')
    print('by cluster size:'); print(c.groupby('cb', observed=True).matched.agg(['size', 'mean']).round(3).T.to_string())
    print('by max FRP in cluster:'); print(c.groupby('fb', observed=True).matched.agg(['size', 'mean']).round(3).T.to_string())
    if dn == 'D':
        t = c.groupby(['fb', 'cb'], observed=True).matched.agg(['size', 'mean']).reset_index()
        print('cluster-level match prob, max-FRP bin (rows) x cluster size (cols); n<15 blanked')
        p = t.pivot(index='fb', columns='cb', values='mean').round(2); n = t.pivot(index='fb', columns='cb', values='size')
        print(p.where(n >= 15).to_string()); print(n.to_string()); p.where(n >= 15).to_csv('intermediate/p4b_cluster_level_day.csv')
        print('cluster-level lone share: matched vs VIIRS-only', c.groupby('matched').n.apply(lambda s: (s == 1).mean()).round(3).to_dict(), ' median max-FRP', c.groupby('matched').frp_max.median().round(2).to_dict())
# ---- local-coverage check: VIIRS-only pixels with any Aqua detection within 15 min AND within 20 km ----
sx, sy = km_xy(so.latitude, so.longitude); ax, ay = km_xy(ao.latitude, ao.longitude)
tree = cKDTree(np.c_[ax, ay]); at = ao.t.values.astype('datetime64[s]').astype('int64') / 60; st = so.t.values.astype('datetime64[s]').astype('int64') / 60
near = tree.query_ball_point(np.c_[sx, sy], 20.0)
so['local_cov20'] = [bool(len(j) and (np.abs(at[j] - st[i]) <= 15).any()) for i, j in enumerate(near)]
so['cl_lone'] = so.cl_n == 1
for dn in 'DN':
    g = so[so.daynight == dn]; vo = g[~g.matched]
    print(f'\n[{dn}] all VIIRS n={len(g)}; VIIRS-only n={len(vo)}')
    print('  VIIRS-only with ANY Aqua detection in box within 15 min (covered):', vo.aqua_obs.mean().round(3), ' with Aqua detection within 20 km AND 15 min:', vo.local_cov20.mean().round(3))
    l = g[g.local_cov20]
    print(f'  local-covered (<=20 km, <=15 min): n={len(l)}, match rate {l.matched.mean():.3f}; lone share matched/VIIRS-only:', l.groupby('matched').cl_lone.mean().round(3).to_dict(), ' FRP median matched/VIIRS-only:', l.groupby('matched').frp.median().round(2).to_dict())
so[['latitude', 'longitude', 't', 'daynight', 'matched', 'aqua_obs', 'local_cov20', 'cl_n', 'frp']].to_csv('intermediate/p4b_viirs_local_cov.csv', index=False)
print('\nfootprint uses each detection own scan x track (FIRMS fields): Aqua day scan/track median', ao.scan.median(), ao.track.median(), ' p90', ao.scan.quantile(.9), ao.track.quantile(.9))
