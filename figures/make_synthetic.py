"""Synthetic example for the docs (no scroll data): two curved sheets with an interior gap
through both, a hole at a crop face, and two bridges joining the sheets (one handle)."""
import numpy as np, tifffile
z, y, x = np.mgrid[:64, :96, :96]
s1 = np.abs(z - (24 + 4 * np.sin(x / 15))) < 1.5
s2 = np.abs(z - (36 + 4 * np.sin(x / 15))) < 1.5
lab = (s1 | s2).astype(np.uint8)
lab[:, 40:44, 40:44] = 0                                   # gap in both sheets
for cy, cx in [(70, 60), (70, 76)]:                        # two bridges -> one handle
    zc = 24 + 4 * np.sin(x / 15)
    lab[(z > zc) & (z < zc + 12) & (np.hypot(y - cy, x - cx) < 3)] = 1
lab[:, 2:5, 60:63] = 0                                     # hole at a crop face
img = np.clip(lab * 170 + np.random.default_rng(0).normal(40, 12, lab.shape), 0, 255).astype(np.uint8)
tifffile.imwrite('figures/synthetic_label.tif', lab)
tifffile.imwrite('figures/synthetic_image.tif', img)
