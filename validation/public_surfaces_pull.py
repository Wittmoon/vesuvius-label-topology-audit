"""Pull matched 256^3 crops from PHerc0139's two published surface-prediction zarrs,
threshold at 127, write labels/<name>.tif (0/1 uint8) for the topology audit."""
import json, sys, numpy as np, zarr, tifffile
B = "https://vesuvius-challenge-open-data.s3.amazonaws.com/PHerc0139/representations/predictions/surfaces/"
GEN = {"recto090": "20250728140407-surface-20250701154204-surface-recto-090.zarr",
       "m7L0": "20250728140407-surface-20260413222639-surface-m7-L0-th0.2.zarr"}
N, C = int(sys.argv[1]), 256
rng = np.random.default_rng(0)
arrs = {k: zarr.open(B + v, mode="r") for k, v in GEN.items()}
lo = {k: a["3"] for k, a in arrs.items()}  # 1/8 scale for region picking
full = {k: a["0"] for k, a in arrs.items()}
shape = full["recto090"].shape; print("shape", shape, {k: v.shape for k, v in lo.items()}, flush=True)
import os; os.makedirs("labels", exist_ok=True)
picked = []
while len(picked) < N:
    z, y, x = [int(rng.integers(C, s - 2 * C) // 128 * 128) for s in shape]
    s = lo["recto090"][z // 8:(z + C) // 8, y // 8:(y + C) // 8, x // 8:(x + C) // 8]
    frac = (np.asarray(s) > 127).mean()
    if frac < 0.03: continue
    name = f"z{z:05d}_y{y:04d}_x{x:04d}"
    for k, a in full.items():
        v = np.asarray(a[z:z + C, y:y + C, x:x + C])
        tifffile.imwrite(f"labels/{name}_{k}.tif", (v > 127).astype(np.uint8))
    picked.append(dict(name=name, z=z, y=y, x=x, lo_frac=float(frac)))
    print(len(picked), name, round(frac, 3), flush=True)
json.dump(picked, open("crops.json", "w"), indent=1)
