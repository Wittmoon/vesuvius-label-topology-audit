"""Derive umbilicus.json control points from a tracks DBM by circle fitting.
Method (fixed before any fit): use only horizontal tracks. For each horizontal
track with >= 40 points, fit a circle (Kasa algebraic fit) to its (x, y)
points; keep the fit if radius is within [R_MIN, R_MAX] px, the RMS radial
residual is < 0.05 * radius, and the track subtends >= MIN_ARC_DEG of arc.
Per z slab, the axis estimate is the coordinate-wise median of the kept circle
centres (each track assigned to the slab of its median z). Output is in the
same full-resolution voxel frame as the tracks.
usage: python -I derive_umbilicus_circ.py SPIRAL_FITTING_DIR DBM OUT.json Z_LO Z_HI [SLAB]
"""
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from tracks import _iter_tracks_from_dbm
dbm, out, z_lo, z_hi = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
slab = int(sys.argv[6]) if len(sys.argv) > 6 else 250
import os
R_MIN, R_MAX, MIN_PTS = 60.0, 4000.0, 40
MIN_ARC_DEG = float(os.environ.get('UMB_ARC', 25))
RES_FRAC = float(os.environ.get('UMB_RES', 0.05))
MIN_CIRC = int(os.environ.get('UMB_MINC', 20))
edges = np.arange(z_lo, z_hi + slab, slab)
bins = [[] for _ in range(len(edges) - 1)]
n_h = n_kept = 0
def kasa(xy):
    x, y = xy[:, 0], xy[:, 1]
    A = np.column_stack([x, y, np.ones_like(x)])
    b = x * x + y * y
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0] / 2, sol[1] / 2
    r2 = sol[2] + cx * cx + cy * cy
    if r2 <= 0: return None
    r = np.sqrt(r2)
    res = np.sqrt(np.mean((np.hypot(x - cx, y - cy) - r) ** 2))
    ang = np.arctan2(y - cy, x - cx)
    arc = np.degrees(np.ptp(np.unwrap(np.sort(ang))))
    return cx, cy, r, res, arc
for entry, family, _sid in _iter_tracks_from_dbm(dbm, show_progress=False):
    if family != 'horizontal' or len(entry) < MIN_PTS: continue
    n_h += 1
    xy = entry[:, [2, 1]].astype(np.float64)
    f = kasa(xy)
    if f is None: continue
    cx, cy, r, res, arc = f
    if not (R_MIN <= r <= R_MAX) or res > RES_FRAC * r or arc < MIN_ARC_DEG: continue
    zm = float(np.median(entry[:, 0]))
    b = int(np.clip((zm - z_lo) // slab, 0, len(bins) - 1))
    bins[b].append((cx, cy, r)); n_kept += 1
pts = []
for b, chunk in enumerate(bins):
    if len(chunk) < MIN_CIRC: continue
    c = np.array(chunk)
    med = np.median(c[:, :2], axis=0)
    mad = np.median(np.hypot(*(c[:, :2] - med).T))
    pts.append({"x": round(float(med[0]), 2), "y": round(float(med[1]), 2), "z": float(edges[b] + slab / 2), "score": 100,
                "_n_circles": int(len(c)), "_mad_px": round(float(mad), 1), "_r_med": round(float(np.median(c[:, 2])), 0)})
if pts:
    # constant (not linear) extrapolation: clamp the ends to the fit range
    if pts[0]["z"] > z_lo: pts.insert(0, {**pts[0], "z": float(z_lo)})
    if pts[-1]["z"] < z_hi: pts.append({**pts[-1], "z": float(z_hi)})
print(f"horizontal tracks {n_h} kept circles {n_kept} slabs {len(pts)}/{len(bins)}")
for p in pts: print(p)
json.dump({"control_points": [{k: v for k, v in p.items() if not k.startswith('_')} for p in pts]}, open(out, "w"), indent=1)
