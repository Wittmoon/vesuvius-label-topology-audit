"""Pre-registered analysis of the PHerc0139 issue-#2167 placement run (see the pre-registration file).

unplaced(sample) = no accepted peak within +-half voxels OR |offset| > 2 (level-2 voxels).
Blocks = 1,000 level-0 voxels in z x 10 degrees of angle about the umbilicus; the block set is resampled jointly
across inputs (2,000 draws, seed 2167) so co-located blocks of different windings move together.
Primary: D = [u(w034_GAP) - u(w034_OUT)] - [u(w033_GAP) - u(w033_OUT)], 95% percentile interval, pre-registered D > 0.
"""
import argparse, csv, glob, json, os, sys
import numpy as np
from make_inputs import umbilicus

DIV, HALF, SEED, DRAWS = 4.0, 8.0, 2167, 2000
OFF_LIMIT = 2.0


def load(path, umb):
    r = np.genfromtxt(path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    z, y, x = (r[c].astype(float) * DIV for c in ("z", "y", "x"))
    uz, ux, uy = umb
    ang = np.degrees(np.arctan2(y - np.interp(z, uz, uy), x - np.interp(z, uz, ux))) % 360.0
    off = r["offset"].astype(float) if r["offset"].dtype.kind == "f" else np.array(
        [float(v) if v not in ("", "nan") else np.nan for v in r["offset"]])
    valid = r["valid"].astype(int) == 1
    unplaced = (~valid) | (np.abs(np.nan_to_num(off, nan=np.inf)) > OFF_LIMIT)
    block = (np.floor(z / 1000.0).astype(int) * 1000 + np.floor(ang / 10.0).astype(int))
    return dict(z=z, y=y, x=x, ang=ang, off=off, valid=valid, unplaced=unplaced, block=block,
                contrast=r["contrast"].astype(float), n=len(r),
                nz=r["nz"].astype(float), ny=r["ny"].astype(float), nx=r["nx"].astype(float),
                zl=r["z"].astype(float), yl=r["y"].astype(float), xl=r["x"].astype(float))


def block_weights(inputs, rng):
    """One joint draw: weight per block key (multinomial over the union of blocks)."""
    keys = np.unique(np.concatenate([d["block"] for d in inputs.values()]))
    counts = rng.multinomial(len(keys), np.full(len(keys), 1.0 / len(keys)))
    return dict(zip(keys.tolist(), counts.tolist()))


def wmean(d, w, mask=None):
    ww = np.array([w.get(b, 0) for b in d["block"].tolist()], float)
    v = d["unplaced"].astype(float)
    if mask is not None:
        ww = ww * mask
    s = ww.sum()
    return float((ww * v).sum() / s) if s > 0 else np.nan


def boot(inputs, stat, draws=DRAWS, seed=SEED):
    rng = np.random.default_rng(seed)
    vals = np.array([stat(block_weights(inputs, rng)) for _ in range(draws)])
    vals = vals[np.isfinite(vals)]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)), float(np.mean(vals <= 0)), float(np.std(vals))


def point(d, mask=None):
    v = d["unplaced"].astype(float)
    return float(v.mean()) if mask is None else float(v[mask].mean()) if mask.any() else np.nan


def did(inputs, test, ctrl="w033", mask=None):
    def stat(w):
        return (wmean(inputs[f"{test}_GAP"], w, None if mask is None else mask[f"{test}_GAP"])
                - wmean(inputs[f"{test}_OUT"], w, None if mask is None else mask[f"{test}_OUT"])
                - wmean(inputs[f"{ctrl}_GAP"], w, None if mask is None else mask[f"{ctrl}_GAP"])
                + wmean(inputs[f"{ctrl}_OUT"], w, None if mask is None else mask[f"{ctrl}_OUT"]))
    pt = (point(inputs[f"{test}_GAP"], None if mask is None else mask[f"{test}_GAP"])
          - point(inputs[f"{test}_OUT"], None if mask is None else mask[f"{test}_OUT"])
          - point(inputs[f"{ctrl}_GAP"], None if mask is None else mask[f"{ctrl}_GAP"])
          + point(inputs[f"{ctrl}_OUT"], None if mask is None else mask[f"{ctrl}_OUT"]))
    return pt, boot(inputs, stat)


def joint(a, b, tol=2.0):
    """Fraction of b's valid samples whose snapped peak lies within tol of the snapped peak of the nearest a sample."""
    from scipy.spatial import cKDTree
    def snapped(d):
        P = np.stack([d["zl"], d["yl"], d["xl"]], -1); N = np.stack([d["nz"], d["ny"], d["nx"]], -1)
        return P, P + np.nan_to_num(d["off"], nan=0.0)[:, None] * N
    Pa, Sa = snapped(a); Pb, Sb = snapped(b)
    va, vb = a["valid"], b["valid"]
    tree = cKDTree(Pa[va]); dist, idx = tree.query(Pb[vb])
    near = dist <= 3.0 * 5.0            # nearest a sample within 3 grid steps (level-2 voxels), else no pair
    dd = np.linalg.norm(Sa[va][idx] - Sb[vb], axis=-1)
    return float(np.mean(dd[near] <= tol)) if near.any() else np.nan, int(near.sum()), int(vb.sum())


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True, help="dir with <name>.samples.csv")
    p.add_argument("--umbilicus", required=True)
    p.add_argument("--out", required=True, help="csv of results")
    p.add_argument("--smoke", action="store_true", help="only the block-bootstrap SD of unplaced for each input")
    a = p.parse_args(argv)
    umb = umbilicus(a.umbilicus)
    inputs = {os.path.basename(f)[:-len(".samples.csv")]: load(f, umb) for f in sorted(glob.glob(os.path.join(a.run, "*.samples.csv")))}
    rows = []
    for k, d in inputs.items():
        lo, hi, _, sd = boot({k: d}, lambda w, d=d: wmean(d, w))
        rows.append(dict(measure="unplaced", input=k, value=point(d), ci_lo=lo, ci_hi=hi, sd=sd, n=d["n"],
                         n_valid=int(d["valid"].sum()), n_blocks=len(np.unique(d["block"]))))
    if a.smoke:
        for r in rows:
            r["min_effect"] = max(0.05, 3 * r["sd"])
    else:
        for t in ("w034", "w036", "w037"):
            if f"{t}_GAP" in inputs:
                pt, (lo, hi, p0, sd) = did(inputs, t)
                rows.append(dict(measure="D_primary" if t == "w034" else "D_secondary", input=t, value=pt, ci_lo=lo, ci_hi=hi, sd=sd, p_le_0=p0))
        # contrast quartile strata (pooled quartiles), D per stratum
        allc = np.concatenate([d["contrast"] for d in inputs.values()]); allc = allc[np.isfinite(allc)]
        q = np.percentile(allc, [25, 50, 75])
        for i, (lo_c, hi_c) in enumerate(zip([-np.inf, *q], [*q, np.inf])):
            mask = {k: (np.nan_to_num(d["contrast"], nan=-1) > lo_c) & (np.nan_to_num(d["contrast"], nan=-1) <= hi_c) for k, d in inputs.items()}
            for t in ("w034", "w036", "w037"):
                if f"{t}_GAP" in inputs:
                    pt, (lo, hi, p0, sd) = did(inputs, t, mask=mask)
                    rows.append(dict(measure=f"D_contrast_q{i+1}", input=t, value=pt, ci_lo=lo, ci_hi=hi, sd=sd, p_le_0=p0,
                                     n=int(sum(m.sum() for m in mask.values()))))
        if "w034_GAP_end" in inputs:
            rows.append(dict(measure="end_minus_main", input="w034_GAP", value=point(inputs["w034_GAP_end"]) - point(inputs["w034_GAP"])))
        for s in ("GAP", "OUT"):
            for sh in (6, 12):
                k = f"w033_{s}_s{sh}"
                if k in inputs:
                    rows.append(dict(measure=f"positive_control_s{sh}", input=k, value=point(inputs[k]), n_valid=int(inputs[k]["valid"].sum())))
            if "w034_%s" % s in inputs and "w036_%s" % s in inputs:
                f, npair, nb = joint(inputs[f"w034_{s}"], inputs[f"w036_{s}"])
                rows.append(dict(measure="joint_w036_on_w034_peak", input=s, value=f, n=npair, n_valid=nb))
    keys = sorted({k for r in rows for k in r})
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
