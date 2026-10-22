"""Prediction-vs-label disagreement for every crop with a prediction in PRED_DIR.
usage: disagree_all.py PRED_DIR [--workers 4] -> PRED_DIR/disagreement.csv, PRED_DIR/candidates.csv
pred_far = pred voxels > TOL from any label voxel; label_far = label voxels > TOL from any pred voxel
(label != 2 only). Candidates = components of pred_far >= MIN_VOX."""
import csv, sys, argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np, tifffile
from scipy import ndimage
HERE = Path(__file__).resolve().parent
KF = HERE.parent / 'kaggle_full'
TOL, MIN_VOX = 3.0, 200
holed = {l.strip() for l in open(HERE / 'holed_crops.txt') if l.strip()}

def one(args):
    pred_dir, crop = args
    p = tifffile.imread(pred_dir / f'{crop}.tif') == 1
    l = tifffile.imread(KF / f'labels/{crop}.tif')
    v = l != 2; a = p & v; b = (l == 1) & v
    d = 2 * (a & b).sum() / max(1, a.sum() + b.sum())
    dl = ndimage.distance_transform_edt(~b) if b.any() else np.full(b.shape, 1e3, np.float32)
    dp = ndimage.distance_transform_edt(~a) if a.any() else np.full(a.shape, 1e3, np.float32)
    pf = a & (dl > TOL); lf = b & (dp > TOL)
    lab, n = ndimage.label(pf, structure=np.ones((3, 3, 3)))
    sizes = ndimage.sum(pf, lab, range(1, n + 1)) if n else []
    cands = []
    for k, s in enumerate(sizes, 1):
        if s >= MIN_VOX:
            c = ndimage.center_of_mass(lab == k)
            cands.append(dict(crop=crop, size=int(s), center_zyx='[%d,%d,%d]' % tuple(int(round(x)) for x in c)))
    row = dict(crop=crop, holed=int(crop in holed), dice=round(float(d), 3), label_vox=int(b.sum()), pred_vox=int(a.sum()),
               pred_far=int(pf.sum()), pred_far_frac=round(float(pf.sum() / max(1, a.sum())), 4),
               label_far=int(lf.sum()), label_far_frac=round(float(lf.sum() / max(1, b.sum())), 4),
               n_comp=int(n), n_cand=len(cands), largest_comp=int(max(sizes)) if n else 0)
    return row, cands

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('pred_dir'); ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args(); pred_dir = HERE / a.pred_dir
    crops = sorted(p.stem for p in pred_dir.glob('sample_*.tif'))
    rows, cands = [], []
    with ProcessPoolExecutor(a.workers) as ex:
        for r, c in ex.map(one, [(pred_dir, x) for x in crops]):
            rows.append(r); cands.extend(c); print(r['crop'], r['pred_far_frac'], r['n_cand'], flush=True)
    rows.sort(key=lambda r: -r['pred_far_frac']); cands.sort(key=lambda r: -r['size'])
    for name, rs in (('disagreement.csv', rows), ('candidates.csv', cands)):
        if rs:
            w = csv.DictWriter(open(pred_dir / name, 'w'), fieldnames=rs[0].keys()); w.writeheader(); w.writerows(rs)
    top = rows[:50]
    print(f'crops {len(rows)} | top-50 by pred_far_frac not in holed set: {sum(1 for r in top if not r["holed"])} | '
          f'candidates {len(cands)} in {len({c["crop"] for c in cands})} crops | median pred_far_frac {np.median([r["pred_far_frac"] for r in rows]):.3f}')
