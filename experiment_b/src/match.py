# Spatial-temporal matching of S-NPP (VIIRS) detections to Aqua pixel footprints.
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from common import km_xy, assign_passes, T_PRIMARY, MARGIN_KM, LINK_KM

def _min(t): return t.values.astype('datetime64[s]').astype('int64') / 60.0

def match(a, s, T=T_PRIMARY, mode='rect', scale=1.0, margin=MARGIN_KM, radius=1.0):
    """a: Aqua df, s: VIIRS df (both with latitude, longitude, t, scan, track). Returns (s_out, a_out).
    mode 'rect': VIIRS centre inside rectangle scan*scale km E-W by track*scale km N-S around Aqua centre, plus margin km.
    mode 'radius': VIIRS centre within `radius` km of Aqua centre.
    Time rule: |dt| <= T minutes. Aqua pixel id = row position in the reset-index Aqua frame."""
    a = a.reset_index(drop=True); s = s.reset_index(drop=True)
    ax, ay = km_xy(a.latitude, a.longitude); sx, sy = km_xy(s.latitude, s.longitude)
    at, st = _min(a.t), _min(s.t)
    hx = a.scan.values * scale / 2 + margin; hy = a.track.values * scale / 2 + margin
    if mode == 'radius': hx = hy = np.full(len(a), radius)
    tree = cKDTree(np.c_[ax, ay])
    R = np.hypot(hx.max(), hy.max())
    cand = tree.query_ball_point(np.c_[sx, sy], R)
    si, ai, d = [], [], []
    for i, lst in enumerate(cand):
        if not lst: continue
        j = np.array(lst)
        ok = np.abs(at[j] - st[i]) <= T
        if mode == 'rect':
            ok &= (np.abs(ax[j] - sx[i]) <= hx[j]) & (np.abs(ay[j] - sy[i]) <= hy[j])
        else:
            ok &= np.hypot(ax[j] - sx[i], ay[j] - sy[i]) <= radius
        j = j[ok]
        si += [i] * len(j); ai += j.tolist(); d += np.hypot(ax[j] - sx[i], ay[j] - sy[i]).tolist()
    pairs = pd.DataFrame({'si': si, 'ai': ai, 'd': d})
    s = s.copy(); a = a.copy()
    s['n_cand'] = pairs.groupby('si').size().reindex(range(len(s))).fillna(0).astype(int).values
    s['matched'] = s.n_cand > 0
    best = pairs.sort_values('d').drop_duplicates('si').set_index('si')['ai']
    s['aqua_id'] = best.reindex(range(len(s))).values   # nearest-centre Aqua pixel among footprint-valid candidates
    a['n_viirs'] = pairs.groupby('ai').size().reindex(range(len(a))).fillna(0).astype(int).values
    a['has_viirs'] = a.n_viirs > 0
    # "observed" flags: any detection of the other sensor anywhere in the box within T minutes
    ats, sts = np.sort(at), np.sort(st)
    def near(x, ref):
        k = np.searchsorted(ref, x); lo = ref[np.clip(k - 1, 0, len(ref) - 1)]; hi = ref[np.clip(k, 0, len(ref) - 1)]
        return np.minimum(np.abs(x - lo), np.abs(x - hi)) <= T
    s['aqua_obs'] = near(st, ats); a['viirs_obs'] = near(at, sts)
    return s, a

def add_clusters(s, link_km=LINK_KM):
    """Connected groups of VIIRS detections from the same overpass (pass = detections <=20 min apart, same day/night flag)
    whose centres are within link_km of each other (chain linking)."""
    s = s.reset_index(drop=True).copy()
    s['pass_id'] = -1; off = 0
    for dn, g in s.groupby('daynight'):
        g2 = assign_passes(g, 20); s.loc[g2.index, 'pass_id'] = g2.pass_id.values + off; off += g2.pass_id.max() + 1
    x, y = km_xy(s.latitude, s.longitude)
    pr = cKDTree(np.c_[x, y]).query_pairs(link_km, output_type='ndarray')
    pr = pr[s.pass_id.values[pr[:, 0]] == s.pass_id.values[pr[:, 1]]]
    n = len(s)
    g = coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    s['cluster'] = lab
    s['cl_n'] = s.groupby('cluster').cluster.transform('size')
    s['cl_frp'] = s.groupby('cluster').frp.transform('sum')
    return s
