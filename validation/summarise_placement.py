"""One row per audited public segment + a summary.

usage: python summarise_placement.py out.csv [RESULTS_DIR]
RESULTS_DIR holds one <segment>.json per segment (default: $R/all from placement_run_all.sh,
i.e. ./out/placement/all).
"""
import csv, json, math, os, sys
from pathlib import Path
R = Path(sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get("R", "out/placement"), "all"))
COLS = ["surface", "n_vertices", "n_samples", "n_valid", "no_peak_frac", "off_sheet_frac",
        "offset_median", "offset_q25", "offset_q75", "offset_mean_abs", "offset_abs_gt_2_frac",
        "sheet_fwhm_median", "contrast_median", "snap_remeasure_sd",
        "tangent_absdiff_median_2", "tangent_absdiff_median_4", "tangent_absdiff_median_8",
        "tangent_corr_2", "tangent_corr_4", "tangent_corr_8"]
rows = []
for j in sorted(R.glob("*.json")):
    m = json.loads(j.read_text())
    rows.append({c: m.get(c) for c in COLS})
w = csv.DictWriter(open(sys.argv[1], "w", newline=""), fieldnames=COLS)
w.writeheader(); w.writerows(rows)
def q(vals, p):
    v = sorted(x for x in vals if x is not None and not math.isnan(x))
    return v[int(p * (len(v) - 1))] if v else float("nan")
big = [r for r in rows if r["n_valid"] >= 1000]
print(f"segments {len(rows)}, with >=1000 valid samples {len(big)}")
for c in COLS[4:]:
    vals = [r[c] for r in big]
    print(f"{c:28s} q10 {q(vals,.1):7.2f}  median {q(vals,.5):7.2f}  q90 {q(vals,.9):7.2f}")
