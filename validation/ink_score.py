"""Score an ink prediction tif against ink_9um labels.

usage: score.py PRED.tif LABELS_DIR PREFIX [--mask supervision|validation] [--stride 4]
Labels live on the middle z slice of <PREFIX>_inklabels.zarr; the mask picks which
pixels count (supervision = training pixels, validation = held-out pixels).
"""
import argparse, numpy as np, zarr, tifffile
from sklearn.metrics import roc_auc_score, average_precision_score

p = argparse.ArgumentParser()
p.add_argument('pred'); p.add_argument('labels'); p.add_argument('prefix')
p.add_argument('--mask', default='supervision'); p.add_argument('--stride', type=int, default=4)
a = p.parse_args()

pred = tifffile.imread(a.pred).astype(np.float32)
if pred.ndim == 3: pred = pred[0]
lab = zarr.open(f'{a.labels}/{a.prefix}_inklabels.zarr', mode='r')['0']
msk = zarr.open(f'{a.labels}/{a.prefix}_{a.mask}_mask.zarr', mode='r')['0']
zc = lab.shape[0] // 2
L = np.asarray(lab[zc]); M = np.asarray(msk[zc])
h = min(pred.shape[0], L.shape[0]); w = min(pred.shape[1], L.shape[1])
s = a.stride
pp = pred[:h:s, :w:s]; ll = L[:h:s, :w:s] > 0; mm = M[:h:s, :w:s] > 0
print(f'{a.pred}: pred {pred.shape} labels {L.shape} mask={a.mask} covers {mm.mean():.3f}, ink frac in mask {ll[mm].mean():.4f}')
if ll[mm].any() and (~ll[mm]).any():
    print(f'  AUC {roc_auc_score(ll[mm], pp[mm]):.3f}  AP {average_precision_score(ll[mm], pp[mm]):.3f}  mean pred ink {pp[mm & ll].mean():.1f} bg {pp[mm & ~ll].mean():.1f}')
else:
    print('  mask has only one class on this slice')
