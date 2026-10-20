"""POST HOC (not pre-registered): joint measure projected on the normal. For each valid w036 sample with a valid w034
sample within 3 grid steps, d = ((P_a + off_a N_a) - (P_b + off_b N_b)) . N_b, i.e. the separation of the two snapped
peaks measured along w036's normal. Same band -> |d| small. Also the raw point separation along the normal."""
import sys, numpy as np
from analyze import load
from make_inputs import umbilicus
from scipy.spatial import cKDTree
umb = umbilicus("raw/umbilicus.json")
for s in ("GAP", "OUT"):
    a = load(f"out/full/w034_{s}.samples.csv", umb); b = load(f"out/full/w036_{s}.samples.csv", umb)
    Pa = np.stack([a["zl"], a["yl"], a["xl"]], -1); Na = np.stack([a["nz"], a["ny"], a["nx"]], -1)
    Pb = np.stack([b["zl"], b["yl"], b["xl"]], -1); Nb = np.stack([b["nz"], b["ny"], b["nx"]], -1)
    va, vb = a["valid"], b["valid"]
    d, i = cKDTree(Pa[va]).query(Pb[vb]); near = d <= 15.0
    A = Pa[va][i] + a["off"][va][i][:, None] * Na[va][i]; B = Pb[vb] + b["off"][vb][:, None] * Nb[vb]
    dn = np.einsum("ij,ij->i", A - B, Nb[vb])[near]
    raw = np.einsum("ij,ij->i", Pa[va][i] - Pb[vb], Nb[vb])[near]
    print(s, "pairs", int(near.sum()), "peak sep along normal: median", round(float(np.median(np.abs(dn))), 2),
          "|d|<=2 frac", round(float(np.mean(np.abs(dn) <= 2)), 3), "|d|<=4", round(float(np.mean(np.abs(dn) <= 4)), 3),
          "| raw point sep along normal median", round(float(np.median(np.abs(raw))), 2), "q25/q75", np.round(np.percentile(np.abs(raw), [25, 75]), 2).tolist())
