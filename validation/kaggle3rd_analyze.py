"""Pilot analysis per PREREG_pilot.md: Dice per crop, fill fraction per errata hole, MWU FILL vs CUT."""
import csv, glob, json, sys
import numpy as np, tifffile
from scipy import ndimage, stats

HERE = __import__('pathlib').Path(__file__).resolve().parent
KF = HERE.parent / 'kaggle_full'
pred_dir = HERE / (sys.argv[1] if len(sys.argv) > 1 else 'pilot')
errata = list(csv.DictReader(open(HERE.parent.parent.parent / 'submission/label-topology-audit/data/errata.csv')))
masks = {p.split('/')[-1].split('.')[0]: p for p in glob.glob(str(KF / 'errata/out*/*.hole_mask.tif'))}
dice, rows = {}, []
for crop in sorted({r['crop'] for r in errata}):
    p = tifffile.imread(pred_dir / f'{crop}.tif') == 1
    l = tifffile.imread(KF / f'labels/{crop}.tif')
    v = l != 2; a = p & v; b = (l == 1) & v
    dice[crop] = 2 * (a & b).sum() / (a.sum() + b.sum())
    hm = tifffile.imread(masks[crop]).astype(bool)
    lab, n = ndimage.label(hm, structure=np.ones((3, 3, 3)))
    cents = ndimage.center_of_mass(hm, lab, range(1, n + 1))
    for r in [e for e in errata if e['crop'] == crop]:
        c = np.array(json.loads(r['center_zyx']), float)
        sizes = ndimage.sum(hm, lab, range(1, n + 1)); hv = float(r['hole_voxels'])
        ok = [i for i in range(n) if hv / 3 <= sizes[i] <= hv * 3] or list(range(n))   # size-aware: within 3x of the errata hole
        k = min(ok, key=lambda i: np.linalg.norm(np.array(cents[i]) - c)) + 1
        comp = lab == k
        rows.append(dict(id=r['id'], crop=crop, verdict=r['human_verdict'], hole_vox=int(comp.sum()),
                         fill_frac=float(p[comp].mean()), dice=round(float(dice[crop]), 3)))
w = csv.DictWriter(open(pred_dir / 'pilot_holes.csv', 'w'), fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
d = np.array(list(dice.values()))
print(f'crops {len(d)} dice median {np.median(d):.3f} min {d.min():.3f} max {d.max():.3f}  gate(>0.35): {"PASS" if np.median(d) > 0.35 else "FAIL"}')
F = [r['fill_frac'] for r in rows if r['verdict'] == 'FILL']; C = [r['fill_frac'] for r in rows if r['verdict'] == 'CUT']
u = stats.mannwhitneyu(F, C, alternative='greater')
print(f'FILL n={len(F)} median {np.median(F):.2f} >0.5: {sum(x > 0.5 for x in F)} | CUT n={len(C)} median {np.median(C):.2f} >0.5: {sum(x > 0.5 for x in C)} | MWU p={u.pvalue:.3f}')
for r in rows: print(r['id'], r['crop'], r['verdict'], r['hole_vox'], f"{r['fill_frac']:.2f}", r['dice'])
