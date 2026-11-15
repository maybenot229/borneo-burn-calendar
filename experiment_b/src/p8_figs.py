import sys; sys.path.insert(0, 'src')
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 11, 'axes.grid': True, 'grid.alpha': .3})
# (1) measured Aqua-S-NPP overpass gap (Phase 1)
g = pd.read_csv('intermediate/p1_gaps.csv', parse_dates=['t'])
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, dn, ttl in zip(axs, 'DN', ('Day', 'Night')):
    for per, col, ls in (('2012-2022', OKABE[5], '-'), ('2023+', OKABE[6], '--')):
        x = g[(g.dn == dn) & (g.period == per)].gap
        if len(x): ax.hist(x, bins=np.arange(-120, 121, 10), histtype='step', lw=2, ls=ls, color=col, density=True, label=f'{per} (n={len(x)})')
    ax.axvspan(-15, 15, color='0.85', zorder=0); ax.set_xlabel('Aqua minus S-NPP pass time (min), nearest Aqua pass'); ax.set_title(f'{ttl}: gap to nearest Aqua pass'); ax.legend()
axs[0].set_ylabel('density'); plt.tight_layout(); plt.savefig('figures/fig_overpass_gap_hist.png', dpi=150); plt.close()
# (2) match rate by year (T=15), Aqua drift
yr = pd.read_csv('intermediate/p3_by_year_T15.csv')
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ok = yr.n_aqobs >= 40
ax[0].plot(yr.year, yr.match_rate, marker='s', ls='--', lw=2, color=OKABE[6], label='all VIIRS')
ax[0].plot(yr.year[ok], yr.match_rate_aqobs[ok], marker='o', ls='-', lw=2, color=OKABE[5], label='Aqua-covered VIIRS (n>=40)')
ax[0].set_ylim(0, .5); ax[0].set_ylabel('share of VIIRS matched'); ax[0].legend(); ax[0].set_title('VIIRS match rate by year (T=15 min)')
ok2 = yr.n_aqua_viirsobs >= 40
ax[1].plot(yr.year[ok2], yr.aqua_pix_rate_viirsobs[ok2], marker='o', ls='-', lw=2, color=OKABE[3], label='Aqua pixels with VIIRS (n>=40)')
a = pd.read_csv('intermediate/p1_aqua_passes.csv', parse_dates=['tmed']); d = a[a.daynight == 'D']; mm = d.groupby(d.tmed.dt.year).apply(lambda x: (x.tmed.dt.hour * 60 + x.tmed.dt.minute).median() / 60)
ax2 = ax[1].twinx(); ax2.plot(mm.index, mm.values, marker='^', ls=':', lw=2, color=OKABE[1], label='Aqua day pass, median UTC hour'); ax2.set_ylabel('UTC hour'); ax2.grid(False)
ax[1].set_ylim(0, 1.25); ax[1].set_ylabel('share of Aqua pixels'); ax[1].set_title('Aqua pixel rate and Aqua pass time'); h1, l1 = ax[1].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax[1].legend(h1 + h2, l1 + l2, fontsize=8, loc='upper center')
plt.tight_layout(); plt.savefig('figures/fig_match_by_year.png', dpi=150); plt.close(); print('ok')
