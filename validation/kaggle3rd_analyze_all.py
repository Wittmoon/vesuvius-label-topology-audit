"""All 152 holed crops: Dice(pred, label) and prediction fill fraction per located label hole (flag2 hole masks).
usage: analyze_all.py PRED_DIR -> PRED_DIR/all_holes.csv, PRED_DIR/all_dice.csv"""
import csv, glob, sys
import numpy as np, tifffile
from scipy import ndimage
HERE = __import__('pathlib').Path(__file__).resolve().parent
KF = HERE.parent / 'kaggle_full'
pred_dir = HERE / sys.argv[1]
masks = {p.split('/')[-1].split('.')[0]: p for p in glob.glob(str(KF / 'flag2/out*/*.hole_mask.tif'))}
crops = [l.strip() for l in open(HERE / 'holed_crops.txt') if l.strip()]
holes, dice = [], []
for crop in crops:
    p = tifffile.imread(pred_dir / f'{crop}.tif') == 1
    l = tifffile.imread(KF / f'labels/{crop}.tif')
    v = l != 2; a = p & v; b = (l == 1) & v
    d = 2 * (a & b).sum() / max(1, a.sum() + b.sum())
    dice.append(dict(crop=crop, dice=round(float(d), 3), label_vox=int(b.sum()), pred_vox=int(a.sum())))
    if crop not in masks: continue
    hm = tifffile.imread(masks[crop]).astype(bool)
    lab, n = ndimage.label(hm, structure=np.ones((3, 3, 3)))
    for k in range(1, n + 1):
        comp = lab == k; c = ndimage.center_of_mass(comp)
        holes.append(dict(crop=crop, hole=k, center_zyx='[%d,%d,%d]' % tuple(int(round(x)) for x in c),
                          hole_vox=int(comp.sum()), fill_frac=round(float(p[comp].mean()), 3), dice=round(float(d), 3)))
for name, rows in (('all_holes.csv', holes), ('all_dice.csv', dice)):
    w = csv.DictWriter(open(pred_dir / name, 'w'), fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
dd = np.array([r['dice'] for r in dice]); ff = np.array([r['fill_frac'] for r in holes])
print(f'crops {len(dd)} dice median {np.median(dd):.3f} q1 {np.percentile(dd,25):.3f} q3 {np.percentile(dd,75):.3f} min {dd.min():.3f}')
print(f'located holes {len(ff)} in {len({r["crop"] for r in holes})} crops | fill>0.5: {(ff>0.5).sum()} ({(ff>0.5).mean():.0%}) | fill<0.1: {(ff<0.1).sum()} ({(ff<0.1).mean():.0%}) | median {np.median(ff):.2f}')
