"""Post-filter MINC=1 umbilicus diagnostics into a final umbilicus.json.
Usage: python3 -I filter_umbilicus.py IN_m1.log|json OUT.json Z_LO Z_HI
Env: UMB_N (min circles, 20), UMB_JUMP (max px jump from previous accepted, 500),
     UMB_MAD (max absolute MAD px, 450; 0332 accepted slabs had 113-408), UMB_MADF (fraction of r_med, off=10).
Rule: walk slabs from low z; accept while n>=N, MAD<=MADF*r, jump<=JUMP; stop at
first rejection (contiguous reliable range). Clamp first point to Z_LO and append a
copy of the last accepted at z_end = last_z + half slab (constant extrapolation).
Prints accepted/rejected lines and the recommended fit z range as JSON on last line."""
import json, os, sys, math
inp, out, zlo, zhi = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
N = int(os.environ.get("UMB_N", 20)); JUMP = float(os.environ.get("UMB_JUMP", 500)); MADF = float(os.environ.get("UMB_MADF", 10)); MADA = float(os.environ.get("UMB_MAD", 450))
import ast
if inp.endswith(".log"):
    pts = [ast.literal_eval(l) for l in open(inp) if l.startswith("{")]
else:
    pts = json.load(open(inp))["control_points"]
# drop the clamped duplicate first point (same xy as second) if present
if len(pts) > 1 and pts[0]["x"] == pts[1]["x"] and pts[0]["y"] == pts[1]["y"]:
    pts = pts[1:]
pts.sort(key=lambda p: p["z"])
slab = pts[1]["z"] - pts[0]["z"] if len(pts) > 1 else 0
acc = []
for p in pts:
    n, mad, r = p["_n_circles"], p["_mad_px"], p["_r_med"]
    why = []
    if n < N: why.append(f"n{n}<{N}")
    if mad > MADF * r: why.append(f"mad{mad:.0f}>{MADF}*r{r:.0f}")
    if mad > MADA: why.append(f"mad{mad:.0f}>{MADA:.0f}")
    if acc:
        q = acc[-1]; j = math.hypot(p["x"]-q["x"], p["y"]-q["y"])
        if j > JUMP: why.append(f"jump{j:.0f}>{JUMP}")
    tag = "ACCEPT" if not why else "REJECT"
    print(f"{tag} z{p['z']:.0f} ({p['x']:.1f},{p['y']:.1f}) n{n} mad{mad:.0f} r{r:.0f} {' '.join(why)}")
    if why: break
    acc.append(p)
if not acc: sys.exit("no slabs accepted")
z_end = min(zhi, acc[-1]["z"] + slab/2)
cp = [{"x": p["x"], "y": p["y"], "z": p["z"], "score": 100} for p in acc]
cp.insert(0, {**cp[0], "z": zlo})
cp.append({**cp[-1], "z": z_end})
json.dump({"control_points": cp}, open(out, "w"), indent=1)
print(json.dumps({"n_slabs": len(acc), "z_begin": zlo, "z_end": z_end, "slab": slab, "out": out}))
