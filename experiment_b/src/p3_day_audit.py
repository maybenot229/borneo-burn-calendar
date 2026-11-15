import sys; sys.path.insert(0, 'src')
from common import *; from match import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pd.set_option('display.width', 220)
# Day/night audit of the Phase 3 table. Same cleaning, matching and thresholds as p3.py (T = 15, rect, margin 0.5 km); only the day/night scope is made explicit.
m, v = load_raw(); a, s = clean(m, v)
a = a[a.t < ARCHIVE_END]; s = s[s.t < ARCHIVE_END]
so, ao = match(a, s, T=T_PRIMARY)
rows = []
for per, (lo, hi) in {'2012-2022': ('2012-02-01', PRIMARY_END), '2023+': (PRIMARY_END, ARCHIVE_END), 'full window': ('2012-02-01', ARCHIVE_END)}.items():
    for dn in ('D', 'N', 'D+N'):
        ss = so[(so.t >= lo) & (so.t < hi)]; aa = ao[(ao.t >= lo) & (ao.t < hi)]
        if dn != 'D+N': ss = ss[ss.daynight == dn]; aa = aa[aa.daynight == dn]
        sc = ss[ss.aqua_obs]; ac = aa[aa.viirs_obs]
        rows.append(dict(period=per, scope=dn, aqua=len(aa), snpp=len(ss), matched=int(ss.matched.sum()), match_pct=100 * ss.matched.mean(), viirs_only=int((~ss.matched).sum()),
                         ambiguous=int((ss.n_cand > 1).sum()), aqua_pix_with_viirs=int(aa.has_viirs.sum()), aqua_pix_pct=100 * aa.has_viirs.mean(),
                         mean_viirs_per_aqua_pix=aa.loc[aa.has_viirs, 'n_viirs'].mean(), aqua_only=int((~aa.has_viirs).sum()),
                         n_aqua_covered=len(sc), match_pct_aqua_covered=100 * sc.matched.mean(), n_aqua_pix_viirs_observed=len(ac), aqua_pix_pct_viirs_observed=100 * ac.has_viirs.mean()))
R = pd.DataFrame(rows); R.to_csv('intermediate/p3_day_night_audit.csv', index=False)
print(R.round(2).to_string(index=False))
# consistency: matching on day-only input must equal day rows of the joint run
sd, ad = match(a[a.daynight == 'D'], s[s.daynight == 'D'], T=T_PRIMARY)
q = lambda d: d[d.t < PRIMARY_END]
print('day-only input, 2012-2022: snpp', len(q(sd)), 'matched', int(q(sd).matched.sum()), 'ambiguous', int((q(sd).n_cand > 1).sum()), 'aqua pix with viirs', int(q(ad).has_viirs.sum()),
      ' (joint run day rows must equal these)')
# by year, day only (companion to fig_match_by_year.png, which pools day and night)
d, ad_ = so[so.daynight == 'D'].copy(), ao[ao.daynight == 'D'].copy(); d['year'] = d.t.dt.year; ad_['year'] = ad_.t.dt.year
yr = d.groupby('year').agg(n_viirs=('matched', 'size'), match_rate=('matched', 'mean'), n_aqobs=('aqua_obs', 'sum'))
yr['match_rate_aqobs'] = d[d.aqua_obs].groupby('year').matched.mean()
yr['aqua_pix_rate_viirsobs'] = ad_[ad_.viirs_obs].groupby('year').has_viirs.mean(); yr['n_aqua_viirsobs'] = ad_.groupby('year').viirs_obs.sum()
yr.to_csv('intermediate/p3_by_year_T15_day.csv'); print(yr.round(3).to_string())
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2)); ok = yr.n_aqobs >= 40
ax[0].plot(yr.index, yr.match_rate, marker='s', ls='--', lw=2, color=OKABE[6], label='all VIIRS (day)')
ax[0].plot(yr.index[ok], yr.match_rate_aqobs[ok], marker='o', ls='-', lw=2, color=OKABE[5], label='Aqua-covered VIIRS (day, n>=40)')
ax[0].set_ylim(0, .5); ax[0].set_ylabel('share of VIIRS matched'); ax[0].legend(); ax[0].set_title('Day only: VIIRS match rate by year (T=15 min)')
ok2 = yr.n_aqua_viirsobs >= 40
ax[1].plot(yr.index[ok2], yr.aqua_pix_rate_viirsobs[ok2], marker='o', ls='-', lw=2, color=OKABE[3], label='Aqua day pixels with VIIRS (n>=40)')
pa = pd.read_csv('intermediate/p1_aqua_passes.csv', parse_dates=['tmed']); pa = pa[pa.daynight == 'D']; mm = pa.groupby(pa.tmed.dt.year).apply(lambda x: (x.tmed.dt.hour * 60 + x.tmed.dt.minute).median() / 60)
ax2 = ax[1].twinx(); ax2.plot(mm.index, mm.values, marker='^', ls=':', lw=2, color=OKABE[1], label='Aqua day pass, median UTC hour'); ax2.set_ylabel('UTC hour'); ax2.grid(False)
ax[1].set_ylim(0, 1.25); ax[1].set_ylabel('share of Aqua day pixels'); ax[1].set_title('Day only: Aqua pixel rate and Aqua pass time'); h1, l1 = ax[1].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax[1].legend(h1 + h2, l1 + l2, fontsize=8, loc='upper center')
for x in ax: x.grid(True, alpha=.3)
plt.tight_layout(); plt.savefig('figures/fig_match_by_year_day.png', dpi=150); plt.close(); print('ok')
