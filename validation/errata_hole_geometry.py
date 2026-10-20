"""Automatic cut/fill signal for located holes: label thickness and density around the hole.
A pocket between merged sheets (CUT) should sit inside thick, dense label; a gap in one sheet (FILL)
should have a thin rim. Measured on the 33 errata holes, compared with the consensus / human verdicts.
Usage: errata_hole_geometry.py OUT.csv
Env: KAGGLE_AUDIT_DIR = folder holding labels/<crop>.tif and errata/out*/<crop>.hole_mask.tif
(the audit's locate_holes output); ERRATA_CSV = path to data/errata.csv (default: next to this file)."""
import csv, glob, json, os, sys
import numpy as np, tifffile
from scipy import ndimage as ndi
if len(sys.argv) != 2 or 'KAGGLE_AUDIT_DIR' not in os.environ:
    sys.exit('usage: KAGGLE_AUDIT_DIR=<dir> errata_hole_geometry.py OUT.csv')
K = os.environ['KAGGLE_AUDIT_DIR'].rstrip('/') + '/'
E = csv.DictReader(open(os.environ.get('ERRATA_CSV', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'errata.csv'))))
rows, cache = [], {}
for e in E:
    c = e['crop']
    if c not in cache:
        lab = tifffile.imread(f'{K}labels/{c}.tif'); fg = lab == 1
        masks = glob.glob(f'{K}errata/out*/{c}.hole_mask.tif')
        if not masks: sys.exit(f'no hole mask for {c} under {K}errata/')
        hm = tifffile.imread(masks[0]) > 0
        edt = ndi.distance_transform_edt(fg)
        cache = {c: (fg, hm, edt, ndi.label(hm)[0])}
    fg, hm, edt, hl = cache[c]
    z, y, x = json.loads(e['center_zyx'])
    # the hole component nearest the recorded centre
    ids = np.unique(hl[max(z-6,0):z+7, max(y-6,0):y+7, max(x-6,0):x+7]); ids = ids[ids > 0]
    if len(ids) == 0: print('no hole near', e['id'], '(row omitted)', file=sys.stderr); continue
    best = min(ids, key=lambda i: abs(int((hl == i).sum()) - int(e['hole_voxels'])))
    hole = hl == best; n = int(hole.sum())
    rim = ndi.binary_dilation(hole, iterations=2) & fg & ~hole
    far = ndi.binary_dilation(hole, iterations=8) & fg & ~ndi.binary_dilation(hole, iterations=3)
    th_rim = 2 * edt[rim] - 1; th_far = 2 * edt[far] - 1
    ball = ndi.binary_dilation(hole, iterations=10)
    dens = float(fg[ball].sum() / ball.sum())
    pts = np.argwhere(hole); ev = np.linalg.eigvalsh(np.cov(pts.T)) if n > 3 else np.zeros(3)
    rows.append(dict(id=e['id'], crop=c, consensus=e['consensus'], human=e['human_verdict'], hole_voxels=n, hole_voxels_errata=e['hole_voxels'],
                     rim_vox=int(rim.sum()), rim_thick_median=round(float(np.median(th_rim)), 2), rim_thick_p90=round(float(np.percentile(th_rim, 90)), 2),
                     rim_frac_ge5=round(float((th_rim >= 5).mean()), 3), far_thick_median=round(float(np.median(th_far)), 2),
                     label_density_r10=round(dens, 3), extent_min=round(float(np.sqrt(max(ev[0], 0)) * 2), 1), extent_max=round(float(np.sqrt(max(ev[-1], 0)) * 2), 1)))
    print(rows[-1], flush=True)
if not rows: sys.exit('no holes matched')
with open(sys.argv[1], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
