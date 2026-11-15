import sys; sys.path.insert(0, 'src')
from common import *
pd.set_option('display.width', 200)
mc = pd.read_csv(os.path.join(DATA, 'monthly_counts.csv'))
mc['ym'] = pd.to_datetime(dict(year=mc.year, month=mc.month, day=1)).dt.to_period('M')
mc = mc[(mc.ym >= '2012-02') & (mc.ym <= '2026-10')].copy()
mc['modis'] = mc.modis_terra + mc.modis_aqua
learn = mc[(mc.ym >= '2012-02') & (mc.ym <= '2018-12')]; test = mc[(mc.ym >= '2019-01') & (mc.ym <= '2025-12')]
print('learn months', len(learn), 'test months', len(test), 'test viirs NaN', test.viirs.isna().sum(), 'modis_raw vs terra+aqua equal:', (mc.modis_raw == mc.modis).mean().round(3))
r = learn.viirs.sum() / learn.modis.sum(); print('learned ratio of sums (Terra+Aqua)', round(r, 3))
def defs(pred, y, tag):
    y = y.values.astype(float); p = np.asarray(pred, float)
    print(f'{tag:34s} WAPE {np.abs(p - y).sum() / y.sum():.3f} | |sum err| {abs(p.sum() - y.sum()) / y.sum():.3f} | median APE {np.median(np.abs(p - y) / np.maximum(y, 1)):.3f} | mean APE {np.mean(np.abs(p - y) / np.maximum(y, 1)):.3f}')
defs(r * test.modis, test.viirs, 'ratio of sums x MODIS')
defs(test.modis, test.viirs, 'no correction (VIIRS=MODIS)')
# per-calendar-month ratio
cm = learn.groupby('month').apply(lambda g: g.viirs.sum() / g.modis.sum()); defs(test.month.map(cm) * test.modis, test.viirs, 'per-calendar-month ratio')
# straight-line fit viirs ~ a + b*modis
b, a_ = np.polyfit(learn.modis, learn.viirs, 1); defs(a_ + b * test.modis, test.viirs, 'straight-line fit')
print('test: sum viirs', test.viirs.sum(), 'sum modis', test.modis.sum(), 'test ratio of sums', round(test.viirs.sum() / test.modis.sum(), 3))
