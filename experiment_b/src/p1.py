# Phase 1 — integrity and acquisition timing
import sys; sys.path.insert(0, 'src')
from common import *
m, v = load_raw()
print('rows MODIS', len(m), m.satellite.value_counts().to_dict(), m.acq_date.min(), m.acq_date.max())
print('rows VIIRS', len(v), v.satellite.value_counts().to_dict(), v.acq_date.min(), v.acq_date.max())
for n, d in (('MODIS', m), ('VIIRS', v)):
    print(n, 'exact dups', d.duplicated().sum(), 'key dups', d.duplicated(['latitude','longitude','acq_date','acq_time','satellite']).sum())
    print(n, 'dtypes', d.dtypes.to_dict())
    print(n, 'missing', d.isna().sum()[d.isna().sum() > 0].to_dict())
    print(n, 'NRT rows', d.nrt.sum(), d.loc[d.nrt, 'acq_date'].min(), d.loc[d.nrt, 'acq_date'].max())
    print(n, 'version', d.version.value_counts().to_dict(), 'type', d.type.value_counts(dropna=False).to_dict())
    print(n, 'daynight', d.daynight.value_counts().to_dict(), 'instrument', d.instrument.unique())
    print(n, 'scan', d.scan.min(), d.scan.max(), 'track', d.track.min(), d.track.max(), 'frp<0', (d.frp < 0).sum(), 'frp max', d.frp.max())
    print(n, 'lat', d.latitude.min(), d.latitude.max(), 'lon', d.longitude.min(), d.longitude.max())
    print(n, 'date==acq_date', (d['date'] == d['acq_date']).all())
    # conflicting records: same pixel & time, differing attributes -> none if no key dups
    # day/night flag vs time-of-day
    print(n, pd.crosstab(d.daynight, (d.acq_time // 100)).to_string())
print('MODIS conf non-numeric', m.conf_num.isna().sum(), 'VIIRS conf', v.confidence.value_counts().to_dict())
print('VIIRS type 3', (v.type == 3).sum())
# version vs nrt overlap: any archive/NRT on same date?
for n, d in (('MODIS', m), ('VIIRS', v)):
    both = set(d.loc[d.nrt, 'acq_date']) & set(d.loc[~d.nrt, 'acq_date'])
    print(n, 'dates with both archive and NRT rows', len(both), 'last archive date', d.loc[~d.nrt, 'acq_date'].max())
