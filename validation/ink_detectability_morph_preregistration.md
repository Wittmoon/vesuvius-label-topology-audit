# PREREG: stroke-morphology detectability control (lane C), sealed before any M value is computed

Date written: 2026-11-04. This is a detectability control. It makes no claim that any letter is read anywhere.

## 0. What was already known when this was written (disclosure)
Exploratory facts from lane 1 and lane B, known to the author before fixing M:
- Lane 1 G3: hit-fraction statistic S_abs (fraction of footprint pixels with z_abs >= 0.885), tau = 0.04398295 (5th percentile of S_abs over the 114 PHerc343 POS letter windows).
- Lane B (G3 v2, sealed PREREG_G3v2.md): pooled blank-papyrus FPR at tau = 0.763 (CI 0.744 to 0.782), verdict FAIL, over 4500 R1 blank windows in five in-sample crops.
- Exploratory, not pre-registered then: AUC of S_abs, letters(114) vs blank(4500) = 0.674; 0/114 letters exceed the blank maximum; blank p95 of S_abs = 0.574; on a top-20 contact sheet the blank maps looked like smooth low-frequency washes dipping over voids, with no stroke-like structure.
- Hit fraction therefore does not separate letters from in-sample blank papyrus. This lane asks whether a morphology statistic does. The author has NOT looked at the shape (component size, solidity, elongation) of hits in any letter or blank window; the thresholds below come from letter geometry at 8.64 um (letter about 2 to 4 mm = 230 to 460 px, strokes about 5 to 10 px wide), not from data.

## 1. Data (reused, read-only, no inference)
- Letters: 114 windows with label == 1 in lane-1 out/windows_base.csv (identical (r,c) set to out/windows_pos343.csv label == 1). Window 289 px, stride 144, 8.64 um. Ink map: the reading-side ("fwd") dense_native map of the POS render, scratch/trace_0800/prod/controls/ink_0800POS/t000.tif, footprint from render_0800POS t000.vc.zarr (exactly the g3.py construction).
- Blank: 4500 windows of windows_g3v2.csv (lane B, R1, five crops c0..c4, 30x30 windows each), ink maps crops/<key>/crop_dn.tif and footprints from crops/<key>/crop.vc.zarr, exactly as g3v2_stats.py.
- z rule: v = clip((u8 - 64)/128, 0, 1); z_abs = (v - 0.227156)/0.163374; hit = z_abs >= 0.885.

## 2. Primary statistic M (fixed)
Per window (289x289, footprint F restricted to the window):
1. H = (z_abs >= 0.885) AND F, within the window only (components are cut at the window border; nothing outside the window is used).
2. Label H with 8-connectivity (scipy.ndimage.label, 3x3 structure of ones).
3. For each component compute area A (px), solidity = A / convex-hull area (skimage.measure.regionprops, area_convex), and axis ratio q = axis_minor_length / axis_major_length (skimage regionprops, ellipse with the same second moments).
4. A component QUALIFIES iff 30 <= A <= 3000 AND (solidity <= 0.6 OR q <= 0.5).
5. M = (sum of areas of qualifying components) / (number of footprint pixels in the window). Range 0 to 1; larger = more stroke-like.
Specks (< 30 px) and washes (> 3000 px) never count. No parameter is tuned; there is no second attempt.

## 3. Primary test
AUC of M, 114 letter windows (positives) against 4500 blank windows (negatives); ties by midrank (statlib.auc). Direction fixed: larger M = letter.
Bootstrap: 2x2 window-grid blocks, block id = (floor(i/2), floor(j/2)) with i = r/144, j = c/144 (statlib.block_ids for letters; blank blocks are keyed by crop as in windows_g3v2.csv column block, 1125 blocks). In each of 2000 replicates (numpy default_rng(343), one generator: letter blocks drawn first, then blank blocks), blocks are resampled with replacement independently within each set; the AUC is recomputed; 95% CI = percentile 2.5 and 97.5 of finite replicates.
Decision: PASS iff CI lower bound >= 0.80; FAIL iff CI upper bound < 0.70; otherwise INCONCLUSIVE.

## 4. Secondary (one)
tau_M = 5th percentile (numpy linear) of M over the 114 letter windows (the lane-1 G3 construction). FPR_M = fraction of the 4500 blank windows with M >= tau_M, 95% CI by blank-block bootstrap with tau_M held at its point value (2000 reps, seed 343, percentile). If tau_M == 0 the FPR is reported as computed and flagged as degenerate (every window satisfies M >= 0). No pass/fail threshold is attached to the secondary; it is reported next to lane B's 0.763 for S_abs.

## 5. Exploratory (labelled exploratory in RESULT, no decision weight)
Per-crop AUC; letters vs the 28 POS off-text windows; median component counts (all and qualifying) per window; alternative bands (area 30 to 1500, 60 to 3000), solidity-only and axis-ratio-only variants; fraction of letters/blanks with M > 0; a local contact sheet of top letter and top blank windows by M (out/ only, never in the evidence repo).

## 6. Rules
Lane-1 and lane-B directories are read-only. winlib.py and statlib.py are copied unmodified. This file is sealed (sha256 sidecar) before any M value exists; any deviation is recorded in RESULT_morph.md, never by editing this file. The definition of M and the decision rule above do not change after sealing.
