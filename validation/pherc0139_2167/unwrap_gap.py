"""Polar unwraps of the PHerc0139 CT at ChaseHendrick's 12 places (issue #2167), with the w033-w037 crossings overlaid.

For each place: one z slice of the 20260102150214 CT at level L (default 1, 4.8 um) resampled on a polar grid
(theta, r) about the umbilicus at that z: theta over [a0, a1] deg, r over the radii of the five windings +- margin.
The tifxyz grids (2.399 um frame) are cut at the slice: along each grid column the rows bracketing z are linearly
interpolated, giving one (theta, r) point per column crossing. Coordinates: angle = atan2(y - y_u(z), x - x_u(z)),
umbilicus interpolated in z (same as make_inputs.py). Chunks are read raw (zarr v2 uint8 uncompressed) over HTTP
and cached in --cache. Output: <out>/<place>.png + <out>/crossings.csv (segment, place, theta, r_um, end_piece).
"""
import argparse, csv, json, os, sys, urllib.request, concurrent.futures as cf
import numpy as np
from make_inputs import load_grid, umbilicus, angles, end_piece

BASE = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHerc0139/volumes/20260102150214-2.399um-0.2m-78keV-masked.zarr"
UM0 = 2.399
PLACES = [  # name, z (level-0), angle deg, note
    ("E1", 14856, 35, "w034 534/285: one dense band w033..w037"),
    ("E2", 17995, 360, "three layers; w034 end on inner face of w036 layer"),
    ("E3", 21500, 267, "w034 on w035 layer"),
    ("E4", 10437, 355, "w034+w036 one band; w037 in air"),
    ("E5", 13741, 4, "w036 30um outside w034, same band"),
    ("E6", 14109, 19, "w034+w036 one layer"),
    ("G1", 11000, 50, "w034,w036,w037 on one layer"),
    ("G2", 19500, 15, "w034 crosses onto w036 layer"),
    ("G3", 23000, 60, "w034/w036 cross through air"),
    ("G4", 26800, 35, "w034 on w037 layer"),
    ("C1", 13000, 150, "control: five layers"),
    ("C2", 22000, 180, "control: w036+w037 compressed"),
    ("U1", 14856, 75, "Chase unwrap 55-95"),
    ("U2", 19500, 75, "Chase unwrap 55-95"),
]
COL = {"w033": "#1f77b4", "w034": "#d62728", "w035": "#2ca02c", "w036": "#ff7f0e", "w037": "#9467bd"}


def chunk(level, cz, cy, cx, cache):
    p = os.path.join(cache, f"{level}_{cz}_{cy}_{cx}.npy")
    if os.path.exists(p):
        return np.load(p)
    url = f"{BASE}/{level}/{cz}/{cy}/{cx}"
    for i in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                b = r.read()
            a = np.frombuffer(b, np.uint8).reshape(128, 128, 128)
            break
        except Exception as e:
            if getattr(e, "code", None) == 404:
                a = np.zeros((128, 128, 128), np.uint8); break
            if i == 3:
                raise
    np.save(p, a)
    return a


def slice_polar(level, z0, umb, th, rr, cache, workers, rbase=None):
    """Sample the CT at level-0 z0 on the polar grid (theta deg x radius level-0 vox). Nearest voxel at level L.
    rbase (per theta, level-0 vox) is added to rr so rows follow a reference winding instead of circles."""
    s = 2 ** level
    uz, ux, uy = umb
    xu, yu = np.interp(z0, uz, ux), np.interp(z0, uz, uy)
    T, R = np.meshgrid(np.radians(th), rr, indexing="ij")
    if rbase is not None:
        R = R + rbase[:, None]
    X = (xu + R * np.cos(T)) / s; Y = (yu + R * np.sin(T)) / s
    zi = int(round(z0 / s)); yi = np.rint(Y).astype(int); xi = np.rint(X).astype(int)
    cz = zi // 128; keys = sorted(set(zip((yi // 128).ravel().tolist(), (xi // 128).ravel().tolist())))
    with cf.ThreadPoolExecutor(workers) as ex:
        blocks = dict(zip(keys, ex.map(lambda k: chunk(level, cz, k[0], k[1], cache)[zi % 128], keys)))
    out = np.zeros(T.shape, np.uint8)
    for (ky, kx), b in blocks.items():
        m = (yi // 128 == ky) & (xi // 128 == kx)
        out[m] = b[yi[m] % 128, xi[m] % 128]
    return out, len(keys)


def crossings(grid, umb, z0, dz=400.0):
    """(theta, r) of the grid's crossings of plane z=z0 (level-0 frame). One point per column with a sign change."""
    x, y, z, valid, ang, rad, end, axis = grid
    P = [x, y, z, valid, end]
    if axis == 0:                       # make the circumferential axis the column axis
        P = [p.T for p in P]
    x, y, z, valid, end = P
    pts = []
    for j in range(x.shape[1]):
        v = valid[:, j] & (np.abs(z[:, j] - z0) < dz)
        idx = np.flatnonzero(v)
        if len(idx) < 2:
            continue
        zz = z[idx, j]
        for k in range(len(idx) - 1):
            a, b = idx[k], idx[k + 1]
            if b - a != 1 or (zz[k] - z0) * (zz[k + 1] - z0) > 0:
                continue
            t = (z0 - zz[k]) / (zz[k + 1] - zz[k]) if zz[k + 1] != zz[k] else 0.0
            pts.append((x[a, j] + t * (x[b, j] - x[a, j]), y[a, j] + t * (y[b, j] - y[a, j]), bool(end[a, j] or end[b, j])))
    if not pts:
        return np.zeros((0, 3))
    p = np.array(pts, dtype=np.float64)
    uz, ux, uy = umb
    xu, yu = np.interp(z0, uz, ux), np.interp(z0, uz, uy)
    th = np.degrees(np.arctan2(p[:, 1] - yu, p[:, 0] - xu)) % 360.0
    r = np.hypot(p[:, 0] - xu, p[:, 1] - yu)
    return np.column_stack([th, r, p[:, 2]])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw"); ap.add_argument("--out", default="unwrap")
    ap.add_argument("--level", type=int, default=1); ap.add_argument("--half-deg", type=float, default=20.0)
    ap.add_argument("--margin-um", type=float, default=150.0); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--places", nargs="*"); ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--rel", action="store_true", help="rows = radius minus the w033 crossing radius (layer-parallel)")
    ap.add_argument("--rel-range-um", nargs=2, type=float, default=[-200.0, 700.0])
    a = ap.parse_args(argv)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    cache = os.path.join(a.out, f"cache{a.level}"); os.makedirs(cache, exist_ok=True)
    umb = umbilicus(os.path.join(a.raw, "umbilicus.json"))
    grids = {}
    for w in COL:
        x, y, z, valid = load_grid(os.path.join(a.raw, f"{w}.tifxyz"))
        ang, rad = angles(x, y, z, valid, umb)
        end, axis, _ = end_piece(ang, rad, valid)
        grids[w] = (x, y, z, valid, ang, rad, end, axis)
    s = 2 ** a.level; um = UM0 * s
    rows = []
    for name, z0, a_mid, note in PLACES:
        if a.places and name not in a.places:
            continue
        half = a.half_deg
        if name.startswith("U"):
            a0, a1 = 55.0, 95.0
        else:
            a0, a1 = a_mid - half, a_mid + half
        cr = {w: crossings(grids[w], umb, z0) for w in COL}
        # keep the crossings in the angular window (angles taken mod 360 relative to a0)
        rel = {w: (c[:, 0] - a0) % 360.0 for w, c in cr.items()}
        inwin = {w: cr[w][rel[w] <= (a1 - a0)] for w in COL}
        rel = {w: rel[w][rel[w] <= (a1 - a0)] for w in COL}
        rs = np.concatenate([c[:, 1] for c in inwin.values() if len(c)])
        if not len(rs):
            print(name, "no crossings in window; skipped"); continue
        r0, r1 = rs.min() - a.margin_um / UM0, rs.max() + a.margin_um / UM0
        th = np.arange(0.0, a1 - a0 + 1e-9, np.degrees(s / r1))          # ~1 level-L voxel per step at the outer radius
        rbase = None
        if a.rel:
            ref = inwin["w033"]; refm = ~ref[:, 2].astype(bool)
            if refm.sum() < 5:
                print(name, "no w033 reference; skipped"); continue
            o = np.argsort(rel["w033"][refm])
            rbase = np.interp(th, rel["w033"][refm][o], ref[refm, 1][o])
            r0, r1 = a.rel_range_um[0] / UM0, a.rel_range_um[1] / UM0
        rr = np.arange(r0, r1, float(s))
        img, nchunks = slice_polar(a.level, z0, umb, a0 + th, rr, cache, a.workers, rbase)
        if a.rel:                                   # express every crossing relative to the w033 radius at its angle
            for w in COL:
                if len(inwin[w]):
                    inwin[w] = inwin[w].copy(); inwin[w][:, 1] -= np.interp(rel[w], th, rbase)
        fig, ax = plt.subplots(figsize=(max(8, len(th) / 120), max(4, len(rr) / 120)))
        ax.imshow(img.T, cmap="gray", origin="lower", aspect="auto", vmin=0, vmax=255,
                  extent=[a0, a1, r0 * UM0, r1 * UM0])
        for w in COL:
            c, t = inwin[w], rel[w]
            if not len(c):
                continue
            main_ = ~c[:, 2].astype(bool)
            ax.plot(a0 + t[main_], c[main_, 1] * UM0, ".", ms=3, color=COL[w], label=w)
            if (~main_).any():
                ax.plot(a0 + t[~main_], c[~main_, 1] * UM0, "x", ms=4, color=COL[w], label=f"{w} end piece")
            for ti, ri, e in zip(t, c[:, 1], c[:, 2]):
                rows.append([name, w, round(a0 + ti, 3), round(ri * UM0, 1), int(e)])
        if not name.startswith("U"):
            ax.axvline(a_mid, color="w", lw=0.6, ls=":")
        ax.set_xlabel("angle about umbilicus (deg)"); ax.set_ylabel("radius - w033 radius (um)" if a.rel else "radius (um)")
        ax.set_title(f"{name}: z={z0} (2.399 um frame), CT level {a.level} ({um:.1f} um/vox) — {note}", fontsize=9)
        ax.legend(loc="upper right", fontsize=7, markerscale=2, framealpha=0.6)
        fig.tight_layout(); fig.savefig(os.path.join(a.out, f"{name}{'_rel' if a.rel else ''}.png"), dpi=a.dpi); plt.close(fig)
        print(f"{name} z={z0} theta=[{a0},{a1}] r=[{r0*UM0:.0f},{r1*UM0:.0f}] um img={img.shape} chunks={nchunks} "
              + " ".join(f"{w}:{len(inwin[w])}" for w in COL), flush=True)
    with open(os.path.join(a.out, "crossings_rel.csv" if a.rel else "crossings.csv"), "w", newline="") as fh:
        wr = csv.writer(fh); wr.writerow(["place", "segment", "theta_deg", "r_um", "end_piece"]); wr.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
