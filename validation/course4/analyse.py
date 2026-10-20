"""Course 4 analysis, written after PREREG.md (commit c6c7284). usage: analyse.py SEG [--tile 256] [--shift 0] [--pred NAME]"""
import argparse, json, os, sys, numpy as np, zarr, tifffile
from scipy.ndimage import gaussian_filter1d, distance_transform_edt
from scipy.stats import spearmanr, rankdata
from sklearn.metrics import roc_auc_score, average_precision_score
D = '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/ink'
PFX = {'w016': 'pherc0139-w016', '0814-46527': 'pherc0814-46527', '1667-w029': 'pherc1667-w029'}
p = argparse.ArgumentParser(); p.add_argument('seg'); p.add_argument('--tile', type=int, default=256)
p.add_argument('--shift', type=int, default=0); p.add_argument('--pred', default='default')
p.add_argument('--nboot', type=int, default=1000); p.add_argument('--seed', type=int, default=0)
a = p.parse_args(); seg = a.seg; T = a.tile; rng = np.random.default_rng(a.seed)
tag = f'{seg}_{a.pred}_t{T}_s{a.shift}'
cache = f'offset_{seg}.npz'
if os.path.exists(cache):
    c = np.load(cache); peak, prange, ct = c['peak'], c['prange'], c['ct']
else:
    g = zarr.open(f'{D}/data/{seg}/pooled9.zarr', mode='r'); arr = g['0'] if '0' in g else g
    Z, Y, X = arr.shape; assert Z == 21
    peak = np.zeros((Y, X), np.int8); prange = np.zeros((Y, X), np.float32); ct = np.zeros((Y, X), np.uint8)
    for y0 in range(0, Y, 256):
        v = np.asarray(arr[:, y0:y0 + 256]).astype(np.float32)
        pr = gaussian_filter1d(v, 1.0, axis=0)
        peak[y0:y0 + 256] = pr.argmax(0) - 10; prange[y0:y0 + 256] = pr.max(0) - pr.min(0); ct[y0:y0 + 256] = v[10].astype(np.uint8)
        print('profile rows', y0, file=sys.stderr, flush=True)
    np.savez_compressed(cache, peak=peak, prange=prange, ct=ct)
weak = prange < 10
pfx = PFX[seg]
L = np.asarray(zarr.open(f'{D}/data/{seg}/labels/{pfx}_inklabels.zarr', mode='r')['0'][10]) > 0
M = np.asarray(zarr.open(f'{D}/data/{seg}/labels/{pfx}_validation_mask.zarr', mode='r')['0'][10]) > 0
P = tifffile.imread(f'{D}/predictions/{seg}_{a.pred}.tif').astype(np.float32)
if P.ndim == 3: P = P[0]
assert P.shape == L.shape == M.shape == peak.shape, (P.shape, L.shape, M.shape, peak.shape)
edge = distance_transform_edt(M)
Y, X = L.shape; rows = []
for ti, y0 in enumerate(range(a.shift, Y - T + 1, T)):
    for tj, x0 in enumerate(range(a.shift, X - T + 1, T)):
        s = (slice(y0, y0 + T), slice(x0, x0 + T))
        m = M[s]; nm = int(m.sum())
        if nm == 0: continue
        e = m & ~weak[s]; l = L[s][e]; ni, nb = int(l.sum()), int((~l).sum())
        row = dict(ti=ti, tj=tj, y0=y0, x0=x0, n_mask=nm, nonweak_frac=float(e.sum() / nm), n_ink=ni, n_bg=nb)
        row['eligible'] = bool(ni >= 50 and nb >= 50 and row['nonweak_frac'] >= 0.5)
        if row['eligible']:
            pr = P[s][e]; o = np.abs(peak[s][e].astype(np.float32))
            row.update(auc=float(roc_auc_score(l, pr)), ap=float(average_precision_score(l, pr)),
                       offset=float(np.median(o)), offset_signed=float(np.median(peak[s][e])),
                       frac_ge2=float((o >= 2).mean()), contrast=float(ct[s][e].mean()),
                       prominence=float(np.median(prange[s][e])), prevalence=float(ni / (ni + nb)),
                       edge_dist=float(np.median(edge[s][e])))
        rows.append(row)
import csv
keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ('ti', 'tj'), k))
with open(f'tiles_{tag}.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=keys, lineterminator='\n'); w.writeheader(); w.writerows(rows)
el = [r for r in rows if r['eligible']]
res = dict(segment=seg, pred=a.pred, tile=T, shift=a.shift, n_tiles_with_mask=len(rows), n_eligible=len(el),
           excluded_few_ink=sum(1 for r in rows if r['n_ink'] < 50), excluded_few_bg=sum(1 for r in rows if r['n_bg'] < 50),
           excluded_weak=sum(1 for r in rows if r['nonweak_frac'] < 0.5))
if len(el) < 30:
    res['verdict'] = 'UNINFORMATIVE'; json.dump(res, open(f'results_{tag}.json', 'w'), indent=1); print(json.dumps(res, indent=1)); sys.exit()
ti = np.array([r['ti'] for r in el]); tj = np.array([r['tj'] for r in el])
auc = np.array([r['auc'] for r in el]); ap = np.array([r['ap'] for r in el]); off = np.array([r['offset'] for r in el])
cov = np.column_stack([[r[k] for r in el] for k in ('contrast', 'prominence', 'prevalence', 'edge_dist')])
def rho(x, y): return float(spearmanr(x, y).correlation)
def partial(x, y, C):
    rx, ry = rankdata(x), rankdata(y); RC = np.column_stack([np.ones(len(x))] + [rankdata(c) for c in C.T])
    bx = np.linalg.lstsq(RC, rx, rcond=None)[0]; by = np.linalg.lstsq(RC, ry, rcond=None)[0]
    return rho(rx - RC @ bx, ry - RC @ by)
def block_boot(stat, B):
    bid = (ti // B) * 10000 + (tj // B); ub = np.unique(bid); idx = {b: np.flatnonzero(bid == b) for b in ub}; out = []
    for _ in range(a.nboot):
        pick = rng.choice(ub, len(ub), replace=True); ii = np.concatenate([idx[b] for b in pick])
        try: out.append(stat(ii))
        except Exception: pass
    return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))]
res['rho_offset_auc'] = rho(off, auc)
res['ci_block4'] = block_boot(lambda ii: rho(off[ii], auc[ii]), 4)
res['ci_block2'] = block_boot(lambda ii: rho(off[ii], auc[ii]), 2)
res['ci_block8'] = block_boot(lambda ii: rho(off[ii], auc[ii]), 8)
res['partial_rho'] = partial(off, auc, cov)
res['partial_ci_block4'] = block_boot(lambda ii: partial(off[ii], auc[ii], cov[ii]), 4)
# toroidal null on the tile grid
H, W = ti.max() + 1, tj.max() + 1; grid = np.full((H, W), np.nan); grid[ti, tj] = off
null = []
for _ in range(a.nboot):
    dy, dx = rng.integers(1, H), rng.integers(1, W); sh = np.roll(np.roll(grid, dy, 0), dx, 1)[ti, tj]
    ok = ~np.isnan(sh)
    if ok.sum() >= 10: null.append(rho(sh[ok], auc[ok]))
null = np.array(null); res['toroidal_p'] = float((np.abs(null) >= abs(res['rho_offset_auc'])).mean()); res['n_null'] = len(null)
res['rho_offset_ap'] = rho(off, ap)
res['covariate_rho_auc'] = {k: rho(cov[:, i], auc) for i, k in enumerate(('contrast', 'prominence', 'prevalence', 'edge_dist'))}
res['covariate_rho_offset'] = {k: rho(cov[:, i], off) for i, k in enumerate(('contrast', 'prominence', 'prevalence', 'edge_dist'))}
bins = {'<=1': off <= 1, '1-2': (off > 1) & (off < 2), '>=2': off >= 2}
res['bins'] = {k: dict(n=int(v.sum()), auc_median=float(np.median(auc[v])) if v.any() else None, auc_mean=float(auc[v].mean()) if v.any() else None) for k, v in bins.items()}
res['offset_quartiles'] = [float(q) for q in np.percentile(off, [25, 50, 75])]
res['auc_quartiles'] = [float(q) for q in np.percentile(auc, [25, 50, 75])]
json.dump(res, open(f'results_{tag}.json', 'w'), indent=1); print(json.dumps(res, indent=1))
