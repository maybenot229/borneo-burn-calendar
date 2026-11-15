# Shared parameters and loaders for Experiment B.
import os, numpy as np, pandas as pd
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data') if '__file__' in globals() else '../data'
OUT = os.path.join(DATA, '..', 'experiment_b')
INTER = os.path.join(OUT, 'intermediate'); FIG = os.path.join(OUT, 'figures')

# ---- parameters ----
BOX = dict(lat=(4.0, 7.5), lon=(115.3, 119.3))
MODIS_CONF_MIN = 30
VIIRS_CONF_KEEP = ('n', 'h')
OVERLAP_START = '2012-02-01'
ARCHIVE_END = '2026-08-01'      # common archive end (VIIRS archive ends 2026-07-31)
PRIMARY_END = '2023-01-01'      # primary period = Feb 2012 - Dec 2022 (Aqua overpass aligned with S-NPP)
T_PRIMARY = 15                  # minutes; sensitivity 5/30/60
MARGIN_KM = 0.5                 # geolocation margin added to each Aqua half-footprint
LINK_KM = 0.75                  # VIIRS cluster linking distance
KM_PER_DEG_LAT = 111.32
OKABE = ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
LS = ['-', '--', ':', '-.', (0, (5, 1)), (0, (3, 1, 1, 1, 1, 1))]

def load_raw():
    m = pd.read_csv(os.path.join(DATA, 'sabah_raw_MODIS.csv'), dtype={'version': str, 'confidence': str})
    v = pd.read_csv(os.path.join(DATA, 'sabah_raw_VIIRS.csv'), dtype={'version': str, 'confidence': str})
    for d in (m, v):
        hh, mm = d['acq_time'] // 100, d['acq_time'] % 100
        d['t'] = pd.to_datetime(d['acq_date']) + pd.to_timedelta(hh, 'h') + pd.to_timedelta(mm, 'min')
        d['nrt'] = d['type'].isna()
    m['conf_num'] = pd.to_numeric(m['confidence'], errors='coerce')
    return m, v

def clean(m, v):
    """Section-1 cleaning rules + archive only + overlap period. Aqua only for MODIS."""
    a = m[(~m.nrt) & (m.type == 0) & (m.conf_num >= MODIS_CONF_MIN) & (m.satellite == 'Aqua') & (m.t >= OVERLAP_START)].copy()
    s = v[(~v.nrt) & (v.type == 0) & (v.confidence.isin(VIIRS_CONF_KEEP)) & (v.t >= OVERLAP_START)].copy()
    return a.reset_index(drop=True), s.reset_index(drop=True)

def km_xy(lat, lon, lat0=5.75):
    """Local equirectangular projection (km). Error < 0.5% across the 3.5-degree box."""
    return (np.asarray(lon) * KM_PER_DEG_LAT * np.cos(np.radians(lat0)), np.asarray(lat) * KM_PER_DEG_LAT)

def assign_passes(df, gap_min=20):
    """Group detections of one satellite into overpasses: sorted times, new pass when gap > gap_min minutes."""
    df = df.sort_values('t')
    new = df['t'].diff().dt.total_seconds().div(60).fillna(1e9) > gap_min
    df['pass_id'] = new.cumsum()
    return df
