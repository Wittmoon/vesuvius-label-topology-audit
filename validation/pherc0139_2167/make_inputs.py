"""Derive sector-masked, level-scaled tifxyz inputs for the placement audit (issue #2167 CT check).

For each PHerc0139 winding grid (2.399 um frame of volume 20260102150214):
  angle(deg) = atan2(y - y_u(z), x - x_u(z)) with the umbilicus interpolated in z (sorted, no extrapolation)
  GAP = z in [9000, 27800] and angle in [5, 71];  OUT = z in [9000, 27800] and angle in [100, 210]
  end = the doubly traced piece: along the circumferential grid axis the unwrapped angle spans more than
        360 deg; of the two overlapping pieces the one farther from the umbilicus (Chase's rule).
Outputs <out>/<name>/{x,y,z,mask}.tif + meta.json with coordinates divided by --div (4 = level 2), -1 markers kept,
mask.tif = the sector membership (end excluded except for the *_end outputs). --shift S moves the points S level-2
voxels along the grid normal (positive control). Prints one json line per output with the counts (the gates).
"""
import argparse, json, os, sys
import numpy as np, tifffile

Z0, Z1 = 9000.0, 27800.0
SECTORS = {"GAP": (5.0, 71.0), "OUT": (100.0, 210.0)}


def load_grid(d):
    x, y, z = (tifffile.imread(os.path.join(d, f)).astype(np.float32) for f in ("x.tif", "y.tif", "z.tif"))
    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(z) & (x > 0) & (y > 0) & (z > 0)
    mp = os.path.join(d, "mask.tif")
    if os.path.exists(mp):
        m = tifffile.imread(mp)
        if m.shape == x.shape:
            valid &= m.astype(bool)
    return x, y, z, valid


def umbilicus(path):
    cp = json.load(open(path))["control_points"]
    a = np.array(sorted([(c["z"], c["x"], c["y"]) for c in cp]), dtype=np.float64)
    return a[:, 0], a[:, 1], a[:, 2]


def angles(x, y, z, valid, umb):
    uz, ux, uy = umb
    ang = np.full(x.shape, np.nan, dtype=np.float64)
    inside = valid & (z >= uz[0]) & (z <= uz[-1])
    zx = np.interp(z[inside], uz, ux); zy = np.interp(z[inside], uz, uy)
    ang[inside] = np.degrees(np.arctan2(y[inside] - zy, x[inside] - zx)) % 360.0
    rad = np.full(x.shape, np.nan)
    rad[inside] = np.hypot(x[inside] - zx, y[inside] - zy)
    return ang, rad


def end_piece(ang, rad, valid):
    """Boolean mask of the doubly traced piece. Axis = the grid axis with the larger median unwrapped span."""
    best = None
    for axis in (0, 1):
        A = ang if axis == 1 else ang.T
        V = valid if axis == 1 else valid.T
        spans, pieces = [], np.zeros(A.shape, bool)
        for i in range(A.shape[0]):
            idx = np.flatnonzero(V[i] & np.isfinite(A[i]))
            if len(idx) < 3:
                continue
            u = np.degrees(np.unwrap(np.radians(A[i, idx])))
            spans.append(u.max() - u.min())
            if u.max() - u.min() > 360.0:
                lo = u <= u.max() - 360.0          # piece A (first turn)
                hi = u >= u.min() + 360.0          # piece B (past one turn)
                R = rad if axis == 1 else rad.T
                ra, rb = np.nanmedian(R[i, idx[lo]]), np.nanmedian(R[i, idx[hi]])
                pieces[i, idx[hi if rb >= ra else lo]] = True
        med = float(np.median(spans)) if spans else 0.0
        if best is None or med > best[0]:
            best = (med, axis, pieces if axis == 1 else pieces.T)
    return best[2], best[1], best[0]


def normals(x, y, z, valid):
    """Unit normals from grid-neighbour cross products (same construction as the tool's tifxyz reader)."""
    P = np.stack([x, y, z], -1).astype(np.float64)
    P[~valid] = np.nan
    du = np.full_like(P, np.nan); dv = np.full_like(P, np.nan)
    du[:, 1:-1] = P[:, 2:] - P[:, :-2]
    dv[1:-1] = P[2:] - P[:-2]
    n = np.cross(du, dv)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12
    return n


def write(out, name, x, y, z, mask, div, shift, meta):
    d = os.path.join(out, name); os.makedirs(d, exist_ok=True)
    X, Y, Z = x.copy(), y.copy(), z.copy()
    v = mask
    if shift:
        n = normals(x, y, z, v)
        ok = v & np.isfinite(n[..., 0])
        X[ok] += (shift * div) * n[ok, 0]; Y[ok] += (shift * div) * n[ok, 1]; Z[ok] += (shift * div) * n[ok, 2]
        v = ok
    for arr, f in ((X, "x.tif"), (Y, "y.tif"), (Z, "z.tif")):
        a = arr.astype(np.float32)
        a[v] = a[v] / div
        a[~v] = -1.0
        tifffile.imwrite(os.path.join(d, f), a)
    tifffile.imwrite(os.path.join(d, "mask.tif"), (v.astype(np.uint8) * 255))
    m = dict(meta)
    m["bbox"] = [[float(X[v].min() / div), float(Y[v].min() / div), float(Z[v].min() / div)],
                 [float(X[v].max() / div), float(Y[v].max() / div), float(Z[v].max() / div)]] if v.any() else meta.get("bbox")
    m["derived"] = {"from": meta.get("uuid"), "div": div, "shift_level_vox": shift, "sector": name}
    json.dump(m, open(os.path.join(d, "meta.json"), "w"), indent=1)
    return int(v.sum())


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True); p.add_argument("--umbilicus", required=True); p.add_argument("--out", required=True)
    p.add_argument("--div", type=float, default=4.0)
    p.add_argument("--segments", nargs="+", default=["w033", "w034", "w035", "w036", "w037"])
    p.add_argument("--shifts", nargs="+", type=float, default=[0.0], help="level voxels along the normal (w033 only)")
    p.add_argument("--no-write", action="store_true")
    a = p.parse_args(argv)
    umb = umbilicus(a.umbilicus)
    for w in a.segments:
        d = os.path.join(a.raw, f"{w}.tifxyz")
        x, y, z, valid = load_grid(d)
        meta = json.load(open(os.path.join(d, "meta.json")))
        ang, rad = angles(x, y, z, valid, umb)
        end, axis, span = end_piece(ang, rad, valid)
        inz = valid & np.isfinite(ang) & (z >= Z0) & (z <= Z1)
        rep = {"segment": w, "valid": int(valid.sum()), "circ_axis": axis, "median_span_deg": round(span, 1),
               "end_points": int(end.sum())}
        for s, (a0, a1) in SECTORS.items():
            sec = inz & (ang >= a0) & (ang <= a1)
            rep[f"{s}_all"] = int(sec.sum()); rep[f"{s}_end"] = int((sec & end).sum()); rep[f"{s}_main"] = int((sec & ~end).sum())
            rep[f"{s}_frac_of_valid"] = round(float(sec.sum() / max(1, valid.sum())), 4)
            if a.no_write or w == "w035":
                continue
            shifts = a.shifts if w == "w033" else [0.0]
            for sh in shifts:
                name = f"{w}_{s}" + (f"_s{int(sh)}" if sh else "")
                rep[name] = write(a.out, name, x, y, z, sec & ~end, a.div, sh, meta)
            if w == "w034" and s == "GAP":
                rep["w034_GAP_end"] = write(a.out, "w034_GAP_end", x, y, z, sec & end, a.div, 0.0, meta)
        print(json.dumps(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
