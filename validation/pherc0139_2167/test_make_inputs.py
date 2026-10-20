"""Synthetic check: a 1.15-turn spiral grid; the end piece must be the outer overlap; shift moves points by S*div."""
import numpy as np, tifffile, json, os, tempfile, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_inputs as M
rows, cols = 40, 300
th = np.linspace(0, 2*np.pi*1.15, cols)            # circumferential axis = 1
r = 1000 + 50*th/(2*np.pi)                          # radius grows with turn -> second turn is outer
x = 5000 + r[None, :]*np.cos(th)[None, :] + 0*np.arange(rows)[:, None]
y = 5000 + r[None, :]*np.sin(th)[None, :] + 0*np.arange(rows)[:, None]
z = 10000 + 100*np.arange(rows)[:, None] + 0*th[None, :]
x, y, z = (a.astype(np.float32) for a in (x, y, z))
valid = np.ones_like(x, bool)
umb = (np.array([0., 80000.]), np.array([5000., 5000.]), np.array([5000., 5000.]))
ang, rad = M.angles(x, y, z, valid, umb)
end, axis, span = M.end_piece(ang, rad, valid)
assert axis == 1, axis
assert 410 < span < 420, span
# end = columns past one turn (theta > 2pi), i.e. the outer piece
expect = np.zeros_like(valid); expect[:, th > 2*np.pi - 1e-9] = True
# unwrap on wrapped angles: pieces defined relative to min/max, allow one-column slack
assert abs(end.sum() - expect.sum()) <= rows, (end.sum(), expect.sum())
assert end[:, -1].all() and not end[:, 0].any()
with tempfile.TemporaryDirectory() as d:
    n0 = M.write(d, "s0", x, y, z, valid, 4.0, 0.0, {"uuid": "t"})
    n6 = M.write(d, "s6", x, y, z, valid, 4.0, 6.0, {"uuid": "t"})
    a = np.stack([tifffile.imread(f"{d}/s0/{c}.tif") for c in "xyz"], -1)
    b = np.stack([tifffile.imread(f"{d}/s6/{c}.tif") for c in "xyz"], -1)
    m6 = tifffile.imread(f"{d}/s6/mask.tif") > 0
    assert m6.sum() == n6 and n0 == valid.sum()
    dist = np.linalg.norm(b[m6] - a[m6], axis=-1)
    assert np.allclose(dist, 6.0, atol=0.05), (dist.min(), dist.max())
    assert (b[~m6] == -1).all() and (a != -1).all()   # shifted drops border rows (no normal); unshifted keeps all
    assert np.allclose(a[m6]*4, np.stack([x, y, z], -1)[m6], atol=0.01)
    meta = json.load(open(f"{d}/s6/meta.json")); assert meta["derived"]["shift_level_vox"] == 6.0
print("synthetic check OK: end piece =", int(end.sum()), "cols past one turn =", int(expect.sum()), "shift dist", float(dist.mean()))
