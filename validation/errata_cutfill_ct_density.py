"""FILL/CUT call for located label holes from the CT (plan Night 9, frozen 2026-10-20).

Per errata hole H (26-connected hole-mask component nearest the recorded centre):
  ball  = voxels within 10 of H;  L = label voxels in ball (not H);  B = non-label, non-ignore voxels in ball
          farther than 2 from label or H.
  CT_L = median CT over L (papyrus level); CT_B = 10th percentile over B (air level, low percentile so a
          neighbouring sheet inside the ball does not lift it); CT_H = median over H; CT_Hlo = 10th pct over H.
  s = (CT_H - CT_B) / (CT_L - CT_B);  s_lo likewise with CT_Hlo.  Continuous papyrus under the hole -> s near 1
  (FILL); air -> near 0 (CUT).  UNCLEAR when CT_L - CT_B < 8 or 0.35 <= s <= 0.65.
  M3 (labels only): extent_n = spread of H along the local sheet normal (smallest PCA axis of L); tears are flat,
  pockets reach across the inter-sheet gap.
Controls per crop: --controls N punches N synthetic holes (radius 2-5) into intact label (must read FILL) and
  places N same-radius balls in air 6-8 voxels from the nearest label (must read CUT).
Usage: ct_density.py OUT.csv [--set dev|holdout|all] [--controls N] [--seed S]
  dev = the 14 human-checked holes; holdout = the 19 unchecked (scored only after the pre-registration commit).
"""
import argparse, csv, glob, json, sys
import numpy as np, tifffile
from scipy import ndimage as ndi

K = '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/label_quality/kaggle_full/'
ERR = '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/submission/label-topology-audit/data/errata.csv'
S26 = np.ones((3, 3, 3), bool)
SIZE_RULE = 125  # frozen comparator: errata hole_voxels >= 125 -> CUT


def load(c):
    lab = tifffile.imread(f'{K}labels/{c}.tif'); img = tifffile.imread(f'{K}images/{c}.tif').astype(np.float32)
    hm = tifffile.imread(glob.glob(f'{K}errata/out*/{c}.hole_mask.tif')[0]) > 0
    return lab == 1, lab == 2, img, ndi.label(hm, structure=S26)[0]


def nearest_component(hl, zyx):
    z, y, x = zyx
    ids = np.unique(hl[max(z-8, 0):z+9, max(y-8, 0):y+9, max(x-8, 0):x+9]); ids = ids[ids > 0]
    if len(ids) == 0:
        return None
    best = min(ids, key=lambda i: np.linalg.norm(np.argwhere(hl == i).mean(0) - zyx))
    return hl == best


def score(fg, ign, img, H):
    dH = ndi.distance_transform_edt(~H)
    ball = dH <= 10
    L = fg & ball & ~H
    near = ndi.distance_transform_edt(~(fg | H)) <= 2
    B = ball & ~fg & ~ign & ~H & ~near
    if L.sum() < 20 or B.sum() < 20:
        return dict(n_H=int(H.sum()), n_L=int(L.sum()), n_B=int(B.sum()), ct_L='', ct_B='', ct_H='', ct_Hlo='', s='', s_lo='', extent_n='', call='UNCLEAR', why='too few L or B voxels')
    ctL, ctB = float(np.median(img[L])), float(np.percentile(img[B], 10))
    ctH, ctHlo = float(np.median(img[H])), float(np.percentile(img[H], 10))
    contrast = ctL - ctB
    pts = np.argwhere(L); w, v = np.linalg.eigh(np.cov(pts.T)); nrm = v[:, 0]
    proj = np.argwhere(H) @ nrm
    ext = float(np.percentile(proj, 95) - np.percentile(proj, 5) + 1) if H.sum() > 3 else 1.0
    r = dict(n_H=int(H.sum()), n_L=int(L.sum()), n_B=int(B.sum()), ct_L=round(ctL, 1), ct_B=round(ctB, 1), ct_H=round(ctH, 1), ct_Hlo=round(ctHlo, 1), extent_n=round(ext, 1))
    if contrast < 8:
        r.update(s='', s_lo='', call='UNCLEAR', why=f'contrast {contrast:.1f} < 8'); return r
    s, slo = (ctH - ctB) / contrast, (ctHlo - ctB) / contrast
    r.update(s=round(s, 3), s_lo=round(slo, 3), call='UNCLEAR' if 0.35 <= s <= 0.65 else ('FILL' if s > 0.65 else 'CUT'), why='')
    return r


def controls(fg, ign, img, n, rng):
    out = []
    dfg = ndi.distance_transform_edt(~fg)
    cand_fg = np.argwhere(fg); cand_air = np.argwhere((dfg > 6) & (dfg <= 8) & ~ign)  # ball still holds label, H sits in air
    zz, yy, xx = np.indices(fg.shape, sparse=True)
    for kind, cand in (('syn_fill', cand_fg), ('syn_cut', cand_air)):
        for _ in range(n):
            r = int(rng.integers(2, 6)); p = cand[rng.integers(len(cand))]
            ball = (zz - p[0])**2 + (yy - p[1])**2 + (xx - p[2])**2 <= r * r
            H = (ball & fg) if kind == 'syn_fill' else ball
            if H.sum() < 5:
                continue
            fg2 = fg & ~H if kind == 'syn_fill' else fg
            d = score(fg2, ign, img, H); d.update(id=f'{kind}_{len(out)}', kind=kind, radius=r, center_zyx=p.tolist()); out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--set', default='dev', choices=['dev', 'holdout', 'all'])
    ap.add_argument('--controls', type=int, default=0); ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args(); rng = np.random.default_rng(a.seed)
    rows, cache = [], {}
    for e in csv.DictReader(open(ERR)):
        is_dev = bool(e['human_verdict'])
        if a.set == 'dev' and not is_dev or a.set == 'holdout' and is_dev:
            continue
        c = e['crop']
        if c not in cache:
            cache = {c: load(c)}
        fg, ign, img, hl = cache[c]
        H = nearest_component(hl, json.loads(e['center_zyx']))
        if H is None:
            print('no hole near', e['id']); continue
        d = score(fg, ign, img, H)
        d.update(id=e['id'], kind='errata', crop=c, consensus=e['consensus'], human=e['human_verdict'] if a.set != 'holdout' else '',
                 hole_voxels_errata=int(e['hole_voxels']), size_call='CUT' if int(e['hole_voxels']) >= SIZE_RULE else 'FILL')
        rows.append(d); print({k: d[k] for k in ('id', 'n_H', 'hole_voxels_errata', 'ct_L', 'ct_B', 'ct_H', 's', 's_lo', 'extent_n', 'call', 'size_call', 'human')}, flush=True)
        if a.controls and not any(r.get('crop') == c and r['kind'] != 'errata' for r in rows):
            for d in controls(fg, ign, img, a.controls, rng):
                d['crop'] = c; rows.append(d)
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k != 'id', k))
    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    ctl = [r for r in rows if r['kind'] != 'errata']
    for kind, want in (('syn_fill', 'FILL'), ('syn_cut', 'CUT')):
        g = [r for r in ctl if r['kind'] == kind]
        if g:
            ok = sum(r['call'] == want for r in g); print(f'control {kind}: {ok}/{len(g)} read {want} ({ok/len(g):.0%}); UNCLEAR {sum(r["call"]=="UNCLEAR" for r in g)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
