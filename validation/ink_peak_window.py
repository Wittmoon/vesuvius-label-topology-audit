"""Lever 1: pick the ink model's 17-layer input window from the surface volume's density peak.

Measures the mean z profile over sampled chunks of the central half of the segment, finds the
peak layer, and places the window so the peak sits at the layer where the training corpus put it
(training peak sits at layer 8 of the 17-layer window: aligned centre 10 minus the typical -1 and
window start 2 -> 10-2 = 8; we use 8 so a centred-at-9 segment gets L1).

usage: peak_window.py ZARR CKPT OUT.tif [--peak-at 8] [--dry-run] [-- extra infer args]
Writes OUT.window.json with the profile, peak and chosen window, then runs infer.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np, zarr
from concurrent.futures import ThreadPoolExecutor

# Interpreter and source tree for `infer`: set VESUVIUS_PYTHON (default: the interpreter running this
# script) and VESUVIUS_SRC (path to villa/vesuvius/src; default: use the installed package).
VENV = os.environ.get("VESUVIUS_PYTHON", sys.executable)
SRC = os.environ.get("VESUVIUS_SRC")
WIN = 17

def profile(path, n_cells=10):
    g = zarr.open(path, mode='r')
    a = g['0'] if hasattr(g, 'keys') and '0' in g else g
    Z, Y, X = a.shape; ch = a.chunks[1]
    ys = np.arange(int(Y * .25) // ch, int(Y * .75) // ch + 1)
    xs = np.arange(int(X * .25) // ch, int(X * .75) // ch + 1)
    sel = lambda v: v[np.unique(np.linspace(0, len(v) - 1, min(len(v), n_cells)).round().astype(int))]
    cells = [(y, x) for y in sel(ys) for x in sel(xs)]
    def rd(c):
        y, x = c
        b = np.asarray(a[:, y * ch:(y + 1) * ch, x * ch:(x + 1) * ch]).astype(np.float32)
        m = (b > 0).any(0)
        return b[:, m].sum(1), int(m.sum())
    with ThreadPoolExecutor(8) as ex: rs = list(ex.map(rd, cells))
    n = sum(r[1] for r in rs)
    if n == 0: raise RuntimeError("no signal columns")
    return sum(r[0] for r in rs) / n, Z, n

p = argparse.ArgumentParser()
p.add_argument('zarr'); p.add_argument('ckpt'); p.add_argument('out')
p.add_argument('--peak-at', type=int, default=8)
p.add_argument('--dry-run', action='store_true')
a, extra = p.parse_known_args()

prof, Z, n = profile(a.zarr)
peak = int(prof.argmax())
default_start = math.ceil((Z - WIN) / 2)  # matches infer: w035 28 layers -> 6..22
start = int(np.clip(peak - a.peak_at, 0, Z - WIN))
info = dict(zarr=a.zarr, n_layers=Z, columns=n, peak_layer=peak, centre=Z // 2,
            default_window=[default_start, default_start + WIN], chosen_window=[start, start + WIN],
            shift=start - default_start, profile=[round(float(v), 2) for v in prof])
print(json.dumps({k: v for k, v in info.items() if k != 'profile'}), file=sys.stderr)
json.dump(info, open(os.path.splitext(a.out)[0] + '.window.json', 'w'), indent=1)
if a.dry_run: sys.exit(0)
cmd = [VENV, '-m', 'vesuvius.ink_detection.inference.infer', a.zarr, a.ckpt, a.out,
       '--layer-start', str(start), '--layer-end', str(start + WIN),
       '--overlap', '0.5', '--blend-mode', 'hann', '--batch-size', '4', '--no-compile'] + extra
log = open(os.path.splitext(a.out)[0] + '.log', 'w')
rc = subprocess.call(cmd, env={**os.environ, **({'PYTHONPATH': SRC} if SRC else {})}, stdout=log, stderr=subprocess.STDOUT)
print('infer rc', rc, file=sys.stderr); sys.exit(rc)
