import sys; sys.path.insert(0, 'src')
from common import *; from match import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pd.set_option('display.width', 240)
m, v = load_raw(); a0, s0 = clean(m, v)
END = '2023-01-01'                                   # primary period only
a0 = a0[a0.t < END]; s0 = s0[s0.t < END]
mc = pd.read_csv('intermediate/p5_month_quarters.csv'); mc['ym'] = pd.PeriodIndex(mc.ym, freq='M'); qmap = mc.set_index('ym').quarter

def metrics(a, s, T=15, mode='rect', scale=1.0, margin=0.5, link=0.75, label=''):
    s = add_clusters(s, link); so, ao = match(a, s, T=T, mode=mode, scale=scale, margin=margin)
    so['q'] = so.t.dt.to_period('M').map(qmap); d = so[so.daynight == 'D']; c = d[d.aqua_obs]; lone = c.cl_n == 1
    mm, vo = c[c.matched], c[~c.matched]
    r = dict(variant=label, n_day_viirs=len(d), n_covered=len(c), match_cov=c.matched.mean(),
             frp_med_matched=mm.frp.median(), frp_med_only=vo.frp.median(), lone_matched=(mm.cl_n == 1).mean(), lone_only=(vo.cl_n == 1).mean(),
             p_frp_lt4=c[c.frp < 4].matched.mean(), p_frp_ge20=c[c.frp >= 20].matched.mean(),
             p_lone=c[lone].matched.mean(), p_5plus=c[c.cl_n >= 5].matched.mean())
    for q, tag in (('Q1 quietest', 'Q1'), ('Q4 busiest', 'Q4')):
        dq = d[d.q == q]; r[f'lone_all_{tag}'] = (dq.cl_n == 1).mean(); r[f'frp_med_all_{tag}'] = dq.frp.median()
        cq = dq[dq.aqua_obs]; r[f'match_cov_{tag}'] = cq.matched.mean(); r[f'n_cov_{tag}'] = len(cq)
        r[f'match_all_{tag}'] = dq.matched.mean(); r[f'share_cov_{tag}'] = dq.aqua_obs.mean()
    ao_d = ao[(ao.daynight == 'D') & ao.viirs_obs]; r['aqua_pix_rate_viirsobs'] = ao_d.has_viirs.mean()
    return r

rows = [metrics(a0, s0, label='BASE (T15, rect, margin .5, link .75)')]
rows += [metrics(a0, s0, scale=1.5, label='footprint x1.5'), metrics(a0, s0, mode='radius', label='fixed radius 1 km'),
         metrics(a0, s0, margin=0.0, label='margin 0 km'), metrics(a0, s0, margin=1.0, label='margin 1.0 km')]
rows += [metrics(a0, s0, T=T, label=f'T={T} min') for T in (5, 30, 60)]
rows += [metrics(a0, s0, link=l, label=f'cluster link {l} km') for l in (0.5, 1.0)]
# FRP outliers: drop top 1% FRP of each sensor
rows.append(metrics(a0[a0.frp <= a0.frp.quantile(.99)], s0[s0.frp <= s0.frp.quantile(.99)], label='drop top 1% FRP (both)'))
# stricter confidence
rows.append(metrics(a0[a0.conf_num >= 50], s0, label='Aqua conf >= 50'))
rows.append(metrics(a0, s0[s0.confidence == 'h'], label='VIIRS conf h only'))
# duplicate removal: collapse same-pass VIIRS detections at identical rounded (0.001 deg) coordinates; Aqua same
s_dd = s0.drop_duplicates(['acq_date', 'acq_time', s0.latitude.round(3).rename('la'), s0.longitude.round(3).rename('lo')]) if False else s0.assign(la=s0.latitude.round(3), lo=s0.longitude.round(3)).drop_duplicates(['acq_date', 'acq_time', 'la', 'lo'])
a_dd = a0.assign(la=a0.latitude.round(3), lo=a0.longitude.round(3)).drop_duplicates(['acq_date', 'acq_time', 'la', 'lo'])
print('rounded-coordinate duplicates removed: VIIRS', len(s0) - len(s_dd), 'Aqua', len(a0) - len(a_dd))
rows.append(metrics(a_dd, s_dd, label='duplicates removed (0.001 deg)'))
# sparse months: drop months with <30 VIIRS detections
cnt = s0.groupby(s0.t.dt.to_period('M')).size(); ok = cnt[cnt >= 30].index
rows.append(metrics(a0[a0.t.dt.to_period('M').isin(ok)], s0[s0.t.dt.to_period('M').isin(ok)], label='drop months with <30 VIIRS (sparse)'))
# swath-scan-angle: keep only Aqua pixels with scan<=1.5 km (near nadir)
rows.append(metrics(a0[a0.scan <= 1.5], s0, label='Aqua scan <= 1.5 km (near nadir)'))
R = pd.DataFrame(rows); R.to_csv('intermediate/p6_robustness.csv', index=False)
cols1 = ['variant', 'n_covered', 'match_cov', 'frp_med_matched', 'frp_med_only', 'lone_matched', 'lone_only', 'p_frp_lt4', 'p_frp_ge20', 'p_lone', 'p_5plus', 'aqua_pix_rate_viirsobs']
cols2 = ['variant', 'lone_all_Q1', 'lone_all_Q4', 'frp_med_all_Q1', 'frp_med_all_Q4', 'match_cov_Q1', 'n_cov_Q1', 'match_cov_Q4', 'match_all_Q1', 'match_all_Q4', 'share_cov_Q1', 'share_cov_Q4']
print(R[cols1].round(3).to_string(index=False)); print(); print(R[cols2].round(3).to_string(index=False))
# figure: match rate vs time threshold (rect/x1.5/radius, day covered, primary period)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
sc = add_clusters(s0, 0.75)
for k, (mode, scale, lab, col) in enumerate((('rect', 1.0, 'rect x1.0', OKABE[5]), ('rect', 1.5, 'rect x1.5', OKABE[3]), ('radius', 1.0, 'radius 1 km', OKABE[6]))):
    xs, y1, y2 = [], [], []
    for T in (5, 15, 30, 60):
        so, ao = match(a0, sc, T=T, mode=mode, scale=scale); d = so[so.daynight == 'D']
        xs.append(T); y1.append(d[d.aqua_obs].matched.mean()); y2.append(ao[(ao.daynight == 'D') & ao.viirs_obs].has_viirs.mean())
    ax[0].plot(xs, y1, marker='o', lw=2, ls=LS[k], color=col, label=lab); ax[1].plot(xs, y2, marker='o', lw=2, ls=LS[k], color=col, label=lab)
ax[0].set_title('Day: share of Aqua-covered VIIRS matched'); ax[1].set_title('Day: share of Aqua pixels containing VIIRS\n(S-NPP observed box within T)')
for x in ax: x.set_xlabel('time threshold T (min)'); x.set_ylim(0, 1); x.set_xticks([5, 15, 30, 60]); x.legend()
plt.tight_layout(); plt.savefig('figures/fig_match_rate_vs_time_threshold.png', dpi=150); plt.close(); print('figure written')
