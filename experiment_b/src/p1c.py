import sys; sys.path.insert(0, 'src')
from common import *
pa = pd.read_csv('intermediate/p1_aqua_passes.csv', parse_dates=['t0','t1','tmed']); ps = pd.read_csv('intermediate/p1_snpp_passes.csv', parse_dates=['t0','t1','tmed'])
print('Aqua pass duration (min) median/p90:', ((pa.t1-pa.t0).dt.total_seconds()/60).quantile([.5,.9]).round(1).to_dict(), ' SNPP:', ((ps.t1-ps.t0).dt.total_seconds()/60).quantile([.5,.9]).round(1).to_dict())
res = []
for dn in 'DN':
    A = pa[pa.daynight==dn]; S = ps[ps.daynight==dn]
    at = A.tmed.values
    for _, r in S.iterrows():
        d = (at - r.tmed.to_datetime64())/np.timedelta64(1,'m'); d = d[np.abs(d)<=360]
        if len(d): res.append((dn, r.tmed, d[np.argmin(np.abs(d))]))
g = pd.DataFrame(res, columns=['dn','t','gap'])
g['period'] = np.where(g.t < '2023-01-01', '2012-2022', '2023+')
for (dn, per), x in g.groupby(['dn','period']):
    print(dn, per, 'n', len(x), 'signed gap (Aqua-SNPP) hist (10-min bins -60..+60):', np.histogram(x.gap, bins=np.arange(-60,61,10))[0].tolist(), 'median', x.gap.median().round(1), 'abs q25/50/75/90', np.percentile(x.gap.abs(),[25,50,75,90]).round(0).tolist())
# gap vs same-orbit: gaps within +-12 min vs beyond: bimodality (same overpass vs adjacent orbit ~ 100 min)
print(g.groupby(['dn']).gap.apply(lambda s: pd.Series({'<=5':(s.abs()<=5).mean(),'<=15':(s.abs()<=15).mean(),'<=30':(s.abs()<=30).mean(),'<=60':(s.abs()<=60).mean()})).round(3).to_string())
g.to_csv('intermediate/p1_gaps.csv', index=False)
