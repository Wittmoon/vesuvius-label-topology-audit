"""Per-angle material-run count between w033 and w037 (see run_count_preregistration.md). Builds on unwrap_gap.py."""
import argparse, csv, os, sys
import numpy as np
from scipy.ndimage import gaussian_filter1d
from skimage.filters import threshold_otsu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unwrap_gap import PLACES, COL, slice_polar, crossings, UM0
from make_inputs import load_grid, umbilicus, angles, end_piece

WINDINGS = list(COL)
TOL_UM = 10.0   # amendment 2026-10-22 after the 1-px instrument check: control 90th pct crossing-to-run distance is 16 um


def load_grids(raw, umb):
    g = {}
    for w in WINDINGS:
        x, y, z, valid = load_grid(os.path.join(raw, f"{w}.tifxyz"))
        ang, rad = angles(x, y, z, valid, umb)
        end, axis, _ = end_piece(ang, rad, valid)
        g[w] = (x, y, z, valid, ang, rad, end, axis)
    return g


def winding_radius(cr, a0, th, max_gap_deg=1.5):
    """Interpolated main-piece radius (level-0 vox) per theta (deg rel. a0); nan where no crossing within max_gap_deg."""
    main = ~cr[:, 2].astype(bool)
    t = (cr[main, 0] - a0) % 360.0; r = cr[main, 1]
    o = np.argsort(t); t, r = t[o], r[o]
    if len(t) < 2:
        return np.full(len(th), np.nan)
    out = np.interp(th, t, r, left=np.nan, right=np.nan)
    near = np.min(np.abs(th[:, None] - t[None, :]), axis=1)
    out[near > max_gap_deg] = np.nan
    return out


def runs_1d(col, thr, px_um, min_um=20.0, bridge_um=10.0):
    m = col > thr
    idx = np.flatnonzero(np.diff(np.r_[0, m.astype(int), 0]))
    starts, ends = idx[::2], idx[1::2]
    out = []
    for s, e in zip(starts, ends):
        if out and (s - out[-1][1]) * px_um < bridge_um:
            out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return [(s, e) for s, e in out if (e - s) * px_um >= min_um]


def analyse_window(level, z0, a0, a1, grids, umb, cache, workers, shift=None, wide_um=None):
    """Column table for one window. shift = {winding: um} radial shift applied to the crossings (instrument check)."""
    s = 2 ** level; px_um = UM0 * s
    cr = {w: crossings(grids[w], umb, z0) for w in WINDINGS}
    th = np.arange(0.0, a1 - a0 + 1e-9, 0.05)
    R = {w: winding_radius(cr[w], a0, th) for w in WINDINGS}
    if shift:
        for w, um in shift.items():
            if isinstance(um, str) and um.startswith("onto:"):      # copy onto a neighbour's layer, 5 um inside it
                R[w] = R[um[5:]] - 5.0 / UM0
            else:
                R[w] = R[w] + um / UM0
    allr = np.concatenate([r[~np.isnan(r)] for r in R.values()])
    if not len(allr):
        return [], np.nan
    r0, r1 = allr.min() - 60 / UM0, allr.max() + 60 / UM0
    rr = np.arange(r0, r1, float(s))
    img, _ = slice_polar(level, z0, umb, a0 + th, rr, cache, workers)
    sm = gaussian_filter1d(img.astype(np.float32), 10.0 / px_um, axis=1)
    nz = sm[img > 0]
    thr = threshold_otsu(nz) if len(nz) > 100 else 255.0
    rows = []; widths = []
    tol = TOL_UM / px_um
    for i, t in enumerate(th):
        pres = {w: R[w][i] for w in WINDINGS if not np.isnan(R[w][i])}
        if len(pres) < 2:
            continue
        rl = runs_1d(sm[i], thr, px_um)
        widths += [(e - b) * px_um for b, e in rl]
        pix = {w: (r - r0) / s for w, r in pres.items()}
        lo, hi = min(pix.values()), max(pix.values())
        between = [(b, e) for b, e in rl if e > lo - tol and b < hi + tol]
        occ = {k: [] for k in range(len(between))}; status = {}
        for w, p in pix.items():
            d = [max(b - p, 0.0, p - (e - 1)) for b, e in between]
            k = int(np.argmin(d)) if d else -1
            if k < 0 or d[k] > tol:
                status[w] = "air"
            else:
                occ[k].append(w); status[w] = k
        for k, ws in occ.items():
            if len(ws) >= 2:
                wid = (between[k][1] - between[k][0]) * px_um
                lab = "amb" if (wide_um and wid > wide_um) else "same"
                for w in ws:
                    status[w] = f"{lab}:{'+'.join(ws)}@{wid:.0f}"
        order = sorted(pix, key=pix.get)
        empty = 0
        for w1, w2 in zip(order, order[1:]):
            empty += sum(1 for k, (b, e) in enumerate(between) if not occ[k] and b > pix[w1] and e - 1 < pix[w2])
        row = dict(theta=round(a0 + t, 2), n_present=len(pres), n_runs=len(between), n_empty=empty, thr=round(float(thr), 1))
        for w in WINDINGS:
            st = status.get(w, "absent")
            row[w] = "ok" if isinstance(st, int) else st
        rows.append(row)
    return rows, (np.median(widths) if widths else np.nan)


def summarise(rows):
    n = len(rows)
    if not n:
        return dict(n_cols=0)
    pairs = [(r, w) for r in rows for w in WINDINGS if r[w] != "absent"]
    rate = lambda pred: round(sum(1 for r, w in pairs if pred(r[w])) / len(pairs), 3)
    gaps = sum(r["n_present"] - 1 for r in rows)
    return dict(n_cols=n, n_pairs=len(pairs), air=rate(lambda v: v == "air"), same=rate(lambda v: v.startswith("same")),
                amb=rate(lambda v: v.startswith("amb")), empty_per_gap=round(sum(r["n_empty"] for r in rows) / gaps, 3),
                mean_runs=round(float(np.mean([r["n_runs"] for r in rows])), 2),
                w034_flag=round(sum(1 for r in rows if r["w034"] not in ("ok", "absent")) / max(1, sum(1 for r in rows if r["w034"] != "absent")), 3))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw"); ap.add_argument("--out", default="run_count")
    ap.add_argument("--cache", default="unwrap/cache1"); ap.add_argument("--level", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--half-deg", type=float, default=20.0)
    ap.add_argument("--mode", choices=["places", "sweep", "instrument"], default="places")
    ap.add_argument("--z-step", type=int, default=1000); ap.add_argument("--z-range", nargs=2, type=int, default=[9000, 27800])
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    umb = umbilicus(os.path.join(a.raw, "umbilicus.json")); grids = load_grids(a.raw, umb)
    windows = []
    if a.mode in ("places", "instrument"):
        for name, z0, am, _ in PLACES:
            if a.mode == "instrument" and not name.startswith("C"):
                continue
            windows.append((name, z0, 55.0, 95.0) if name.startswith("U") else (name, z0, am - a.half_deg, am + a.half_deg))
    else:
        for z0 in range(a.z_range[0], a.z_range[1] + 1, a.z_step):
            windows += [(f"gap_z{z0}", z0, 5.0, 71.0), (f"ctlA_z{z0}", z0, 130.0, 170.0), (f"ctlB_z{z0}", z0, 160.0, 200.0)]
    # control median run width sets the "wide" cut (1.5x), measured first on C1/C2
    wid = []
    for name, z0, am, _ in PLACES:
        if name.startswith("C"):
            _, mw = analyse_window(a.level, z0, am - a.half_deg, am + a.half_deg, grids, umb, a.cache, a.workers)
            wid.append(mw)
    wide_um = 1.5 * float(np.nanmedian(wid)); print(f"control median run width {np.nanmedian(wid):.1f} um -> wide cut {wide_um:.1f} um")
    shifts = [None] if a.mode != "instrument" else [None, {"w034": 55.0}, {"w034": 110.0}, {"w034": "onto:w035"}]
    summ = []; cols = []
    for name, z0, a0, a1 in windows:
        base = None
        for sh in shifts:
            rows, _ = analyse_window(a.level, z0, a0, a1, grids, umb, a.cache, a.workers, shift=sh, wide_um=wide_um)
            tag = name if not sh else f"{name}_w034_{sh['w034'] if isinstance(sh['w034'], str) else '+%dum' % sh['w034']}"
            sm = summarise(rows); sm.update(window=tag, z=z0, a0=a0, a1=a1)
            if sh and base is not None:
                clean = {r["theta"] for r in base if r["w034"] == "ok"}
                emp0 = {r["theta"]: r["n_empty"] for r in base}
                flagged = sum(1 for r in rows if r["theta"] in clean and (r["w034"] != "ok" or r["n_empty"] != emp0.get(r["theta"])))
                sm["w034_clean_unshifted"] = len(clean); sm["flagged_after_shift"] = round(flagged / len(clean), 3) if clean else np.nan
            if not sh:
                base = rows
            for r in rows:
                r["window"] = tag; cols.append(r)
            print(tag, sm, flush=True); summ.append(sm)
    keys = sorted({k for s_ in summ for k in s_}, key=lambda k: (k != "window", k))
    with open(os.path.join(a.out, f"summary_{a.mode}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(summ)
    with open(os.path.join(a.out, f"columns_{a.mode}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cols[0])); w.writeheader(); w.writerows(cols)


if __name__ == "__main__":
    main()
