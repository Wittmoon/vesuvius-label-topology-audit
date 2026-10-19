"""Per model/scroll/threshold summary of the sweep: python summarise_sweep.py [out.csv]"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
import os
R = Path(os.environ.get("R", "out/pred_audit/sweep"))  # the R used by threshold_sweep_run.sh
NAMES = {"m7": "m7", "soc": "Socratic", "herc": "HercUNet"}
rows = []
for d in sorted(R.glob("*_PHerc*")):
    model, scroll = d.name.split("_", 1)
    by_t = defaultdict(list)
    for j in d.glob("*_t*.json"):
        if j.name.endswith(".delta.json"):
            continue
        by_t[int(j.stem.rsplit("_t", 1)[1])].append(json.loads(j.read_text()))
    for t, ms in sorted(by_t.items()):
        n = len(ms)
        vox = sum(m["shape"][0] * m["shape"][1] * m["shape"][2] for m in ms)
        fg = sum(m["fg_voxels"] for m in ms)
        b1 = sum(m["b1_total_big"] for m in ms)
        rows.append({"model": NAMES[model], "scroll": scroll, "cut_uint8": t, "threshold": round(t / 255, 2),
                     "tiles": n, "fg_frac": round(fg / vox, 3),
                     "components_per_tile": round(sum(m["n_components"] for m in ms) / n, 1),
                     "b1_total": b1, "b1_face": sum(m["b1_face"] for m in ms),
                     "b1_per_Mvox_fg": round(b1 / fg * 1e6, 1) if fg else 0,
                     "b2_total": sum(m["b2_total_big"] for m in ms),
                     "fused_frac": round(sum(m["fused_voxel_frac"] * m["fg_voxels"] for m in ms) / fg, 3) if fg else 0,
                     "junction_clusters": sum(m["n_junction_clusters"] for m in ms),
                     "thick_median": round((sorted(v for v in (m["thickness"].get("median") for m in ms) if v is not None) or [0])[len([1 for m in ms if m["thickness"].get("median") is not None]) // 2], 1)})
w = csv.DictWriter(open(sys.argv[1], "w", newline="") if len(sys.argv) > 1 else sys.stdout, fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
