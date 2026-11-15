# Phase 1b — Aqua vs S-NPP overpass time gaps (archive rows, Aqua only)
import sys; sys.path.insert(0, 'src')
from common import *
m, v = load_raw()
def passes(df):
    out = []
    for dn, g in df.groupby('daynight'):
        g = assign_passes(g, 20)
        p = g.groupby('pass_id').agg(t0=('t','min'), t1=('t','max'), tmed=('t','median'), n=('t','size')).reset_index()
        p['daynight'] = dn; out.append(p)
    return pd.concat(out)
def run(label, a, s):
    pa, ps = passes(a), passes(s)
    print(f'\n== {label}: Aqua passes {len(pa)}, SNPP passes {len(ps)}; Aqua detections {len(a)}, SNPP {len(s)}')
    rows = []
    for dn in 'DN':
        A = pa[pa.daynight == dn].sort_values('tmed'); S = ps[ps.daynight == dn].sort_values('tmed')
        at = A.tmed.values
        gaps = []
        for tm in S.tmed.values:
            d = (at - tm) / np.timedelta64(1, 'm')
            d = d[np.abs(d) <= 12*60]
            gaps.append(d[np.argmin(np.abs(d))] if len(d) else np.nan)   # signed: Aqua - SNPP, minutes
        gaps = np.array(gaps); ok = ~np.isnan(gaps)
        ab = np.abs(gaps[ok])
        q = np.percentile(ab, [25, 50, 75, 90, 95, 99]) if ok.any() else []
        print(dn, f'SNPP passes {len(S)}, with Aqua same day-window {ok.sum()} ({ok.mean():.1%}), no Aqua {(~ok).mean():.1%}')
        print('  |gap| min quartiles/p90/p95/p99:', np.round(q, 1), ' signed median', np.round(np.median(gaps[ok]), 1))
        print('  share |gap|<=5:', (ab <= 5).mean().round(3), '<=15:', (ab <= 15).mean().round(3), '<=30:', (ab <= 30).mean().round(3), '<=60:', (ab<=60).mean().round(3))
        print('  SNPP pass median clock (UTC):', pd.to_datetime(S.tmed).dt.strftime('%H:%M').describe()[['top']].values, ' Aqua:', pd.to_datetime(A.tmed).dt.hour.value_counts().sort_index().to_dict())
        print('  SNPP hour dist:', pd.to_datetime(S.tmed).dt.hour.value_counts().sort_index().to_dict())
    # per-day: share of days (in overlap) with SNPP pass but no Aqua pass at all, by daynight
    ds = ps.assign(d=pd.to_datetime(ps.tmed).dt.date); da = pa.assign(d=pd.to_datetime(pa.tmed).dt.date)
    for dn in 'DN':
        sd = set(ds[ds.daynight == dn].d); ad = set(da[da.daynight == dn].d)
        print(dn, 'days with SNPP pass', len(sd), 'days with Aqua pass', len(ad), 'SNPP days w/o Aqua', len(sd - ad), f'({len(sd-ad)/len(sd):.1%})')
    return pa, ps
ov = lambda d: d[(d.t >= OVERLAP_START)]
a_all = ov(m[(~m.nrt) & (m.satellite == 'Aqua')]); s_all = ov(v[~v.nrt])
run('ALL archive detections (any type/conf)', a_all, s_all)
a, s = clean(m, v)
pa, ps = run('CLEANED (type0, conf rules)', a, s)
# time-of-day drift by year for Aqua day and SNPP day (median acq_time in minutes)
for n, d in (('Aqua', a), ('SNPP', s)):
    d = d.assign(mins=d.t.dt.hour*60 + d.t.dt.minute, yr=d.t.dt.year)
    print(n, 'median UTC minute-of-day by year (day / night):')
    print(d.groupby(['yr', 'daynight']).mins.median().unstack().round(0).T.to_string())
# per-month detection counts available for matching
print(a.groupby(a.t.dt.year).size().to_dict()); print(s.groupby(s.t.dt.year).size().to_dict())
pa.to_csv('intermediate/p1_aqua_passes.csv', index=False); ps.to_csv('intermediate/p1_snpp_passes.csv', index=False)
