"""Blinded CT look: level-0 slab through each frozen sample in the plane (normal x tangent), +-48 vox (115 um).
Panels get shuffled codes; the key is written to blind_key.json and must not be read before the calls."""
import json, numpy as np, zarr, random
from PIL import Image, ImageDraw
from analyze import load
from make_inputs import umbilicus
URL = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHerc0139/volumes/20260102150214-2.399um-0.2m-78keV-masked.zarr"
g = zarr.open(URL, mode="r"); vol = g["0"]
umb = umbilicus("raw/umbilicus.json"); ids = json.load(open("blind_ids.json"))["ids"]
H = 48
items = []
for k, rows in ids.items():
    d = load(f"out/full/{k}.samples.csv", umb)
    for r in rows:
        P = np.array([d["zl"][r], d["yl"][r], d["xl"][r]]) * 4.0 + 1.5   # level-0 voxel centre of the level-2 sample
        N = np.array([d["nz"][r], d["ny"][r], d["nx"][r]]); N /= np.linalg.norm(N)
        T = np.cross(N, [0, 0, 1.0]);
        if np.linalg.norm(T) < 0.3: T = np.cross(N, [0, 1.0, 0])
        T /= np.linalg.norm(T)
        lo = np.floor(P - H * 1.8).astype(int); hi = np.ceil(P + H * 1.8).astype(int) + 1
        lo = np.maximum(lo, 0); hi = np.minimum(hi, vol.shape)
        sub = vol[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]].astype(np.float32)
        u, v = np.meshgrid(np.arange(-H, H + 1), np.arange(-H, H + 1), indexing="ij")   # u along normal, v tangent
        Q = P[None, None, :] + u[..., None] * N + v[..., None] * T - lo
        Qi = np.clip(np.round(Q).astype(int), 0, np.array(sub.shape) - 1)
        img = sub[Qi[..., 0], Qi[..., 1], Qi[..., 2]]
        items.append((k, r, img, float(d["off"][r]) if np.isfinite(d["off"][r]) else None, bool(d["valid"][r])))
random.Random(2167).shuffle(items)
codes = [f"B{i+1:02d}" for i in range(len(items))]
key = [{"code": c, "input": k, "row": r, "offset_l2": off, "valid": v} for c, (k, r, _, off, v) in zip(codes, items)]
json.dump(key, open("blind_key.json", "w"), indent=1)
S = 3; W = (2 * H + 1) * S
for sheet in range(2):
    canvas = Image.new("L", (5 * W + 4 * 6, 2 * W + 6), 40); dr = ImageDraw.Draw(canvas)
    for j in range(10):
        c, (_, _, img, _, _) = codes[sheet * 10 + j], items[sheet * 10 + j]
        a = np.clip((img - np.percentile(img, 1)) / (np.percentile(img, 99) - np.percentile(img, 1) + 1e-6) * 255, 0, 255).astype(np.uint8)
        im = Image.fromarray(a).resize((W, W), Image.NEAREST)
        x0, y0 = (j % 5) * (W + 6), (j // 5) * (W + 6)
        canvas.paste(im, (x0, y0)); d2 = ImageDraw.Draw(canvas)
        cx, cy = x0 + W // 2, y0 + W // 2
        d2.line([(cx - 12, cy), (cx - 4, cy)], fill=255, width=2); d2.line([(cx + 4, cy), (cx + 12, cy)], fill=255, width=2)
        d2.line([(cx, cy - 12), (cx, cy - 4)], fill=255, width=2); d2.line([(cx, cy + 4), (cx, cy + 12)], fill=255, width=2)
        d2.text((x0 + 4, y0 + 4), c, fill=255)
    canvas.save(f"out/blind_sheet{sheet+1}.png")
print("rendered", len(items), "panels; vertical axis = normal (up = +N), horizontal = tangent; centre cross = sample point")
