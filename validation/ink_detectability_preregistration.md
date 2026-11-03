# PREREG: ink-detectability positive control with a shifted-sheet negative and a contrast covariate (2026-11-03)

Written and sha256-hashed BEFORE any pitch value was read, any shifted-sheet mesh or render existed, any
per-window contrast value was computed, any blank-crop ink map existed, and before any G1/G2/G3 statistic
was computed. Calibration only; no letters claim; not prize evidence on its own.

## 0. What was already known when this was written (disclosed)
- Agreement screen (RESULT_agreement_screen.md, prereg sha 8304a3ea): on the PHerc343 POS control, dense_native
  reading-side label AUC 0.841 (AP 0.9607, n 114 letter / 28 off-text windows, chance AP 0.803); blind side
  AUC 0.541. On PHerc0009B: AUC 0.955 (AP 0.9901, n 123/29); blind 0.671. On PHerc0841: AUC 0.911 (n 61/17).
  seed42/seed43 AP 0.92-0.97 on the same windows. Mean S off-text / letters: 343 0.074 / 0.252; 0009B 0.055 / 0.296.
- So the reading-side AUC of the positive control is NOT a new quantity. This file gates on quantities that do
  not exist yet: the AUC on shifted-sheet re-renders, the AUC within contrast tertiles, and the blank false-positive
  rate. A gate on the known AUC would be circular and is not used.
- The agreement screen's own stated gap: "What a usable test would need: a calibration with verified blank papyrus."
- POS <-> repro343 alignment: POS row = raw_y - 1, POS col = raw_x - 120 (corr 0.986); vc layer 15+k pairs with
  render66 layer 33-k, so POS 'fwd' = reading side and the two renders have the same 1-voxel layer spacing.
- POS t000 tile statistics (sheet_stats): contrast 1.0781, peak_layer_median 12, frac_mid_third 0.35,
  full_column_frac 0.7101, inner_side 'high' (outward_frac 0.0027), window [8,25]. Screened-tile contrast medians:
  0800mid 1.091 (n 55), 0211CW 1.075 (n 69), 0125CW 1.026 (n 38); 0009B control 1.146.
- Contrast is the live confound for placement-vs-accuracy claims (Discord #ink-detection 2026-10-18). It is a covariate
  here, not a claim.
- Candidate blank-margin segments in ink_9um (blank supervision pixels > 0.5 mm from any ink label):
  phercparis4-w05 15.3 Mpx, pherc1667-w018 6.26 Mpx, phercparis4-w07 3.84 Mpx. Counted from labels only; no ink map
  exists for any of them.

## 1. Question
Does the ink pipeline used in our screens (november_lib render -> dense_native) recover ink BECAUSE the labelled
sheet is rendered, and does that recovery survive the low-contrast end of the surfaces we actually screen? A 0/N screen
is only interpretable if (a) the same pipeline reads a known-ink sheet, (b) the signal disappears when the sampled
sheet is moved off the labelled one, and (c) the signal is not driven by contrast alone.

## 2. Inputs (fixed)
- Models: dense_native-016000.rebuilt (md5 187bd2da) primary; hybrid_3d2d seed42 step-075000 (md5 5cc9558c) and
  seed43 step-075000 (md5 37a1215d) secondary. Same files as the agreement screen.
- Inference command (unchanged): `vesuvius.ink_detection.inference.infer <vc.zarr> <ckpt> <out.tif> --overlap 0.5
  --blend-mode hann --batch-size 4 --no-compile --direction both --layer-start 8 --layer-end 25`, launched through the
  NOEXIT runpy wrapper (survivors.py) with PYTHONPATH = pherc0211_trace/inkvilla/vesuvius/src (the tree used for the
  POS dense_native map). Existing POS maps (trace_0800/prod/controls/ink_0800POS t000.tif / t000_reverse.tif and the
  agree_screen seed maps) are reused unchanged; nothing is re-inferred on the unshifted POS surface.
- Positive control surface: PHerc343 POS tile trace_0800/prod/controls/render_0800POS t000 (rows [0,2280],
  cols [120,6720], 31 layers, window [8,25], reading side = fwd). Mesh
  pherc0211_trace/controls/pos/concat_w047-w048_R5B2_z9500-11000.tifxyz (scale 0.05 = level-0 coordinates on a
  20-voxel grid), umbilicus controls/pos/umbilicus_PHerc0343.json, CT
  PHerc0343/volumes/20250521140437-8.640um-1.2m-116keV-masked.zarr (open-data bucket).
- Negative control = shifted-sheet re-render of the SAME mesh:
  - Pitch P is measured first, from repro343_20261027/render66.zarr (66 layers, 1 voxel apart, layer 33 = surface),
    restricted to the repro343 crop (raw rows 484-1777, cols 532-5641) and to columns valid in all 66 layers:
    prof(j) = mean intensity of layer j over those columns, smoothed by a 3-point moving mean. The central peak is the
    local maximum nearest layer 33 within +/-4. P_lo = distance in layers from the central peak to the nearest local
    maximum at >= 12 layers below it; P_hi likewise above it. A local maximum is a sample strictly above both
    neighbours. If a side has no such maximum within the 66 layers, that side uses P = 24 voxels and this is logged.
  - Node normal n = normalised cross(d/dcol, d/drow) of the level-0 node positions by central differences on the
    tifxyz grid (render_patch's convention; invalid nodes excluded). Two meshes are written with the same grid, mask
    and meta: `shift_hi` with X += P_hi * n and `shift_lo` with X -= P_lo * n (level-0 voxels). The implementation
    (an adaptor of placement_2167/make_inputs.py normals/write) is not a definition; it is logged with its sha256.
    Which of hi/lo is toward the umbilicus is reported from the umbilicus file, descriptively.
  - Each shifted mesh is rendered with the frozen command, from cwd pherc0211_trace/down, PYS interpreter:
    `november_lib.py render <shift_mesh.tifxyz> <out_render_dir> <umbilicus_PHerc0343.json> <CT_ZARR_URL> 8`
    (november_lib.py md5 0e852045e9942c51cc6618d80bb7a0f7). The tile plan is identical because the grid is identical.
    The ink window is FIXED at [8,25] and the reading side at fwd for the shifted renders; the render's own
    `window` json is not used.
  - On-sheet validity (per shift, decided before any ink map of that shift is read): the shifted render's
    sheet_stats peak_layer_median must lie in [11, 19]. A shift outside that range is declared OFF-SHEET; it is still
    inferred and reported, but it does not enter G1. If both shifts are off-sheet, G1 is NOT EVALUABLE.
- Contrast covariate per window: the sheet_stats formula applied to the window footprint of the POS render:
  v = vc[:, r0+4:r1:8, c0+4:c1:8]; full columns = all 31 layers > 0; if fewer than 100 full columns the window has no
  covariate and is excluded from G2; prof = mean over full columns; contrast = prof.max() / max(prof.min(), 1e-6).
- Blank calibration crops (exploratory G3): for each of phercparis4-w05, pherc1667-w018, phercparis4-w07
  (scratch/ink/data/<seg>/pooled9.zarr, labels/<seg>_inklabels.zarr, <seg>_supervision_mask.zarr, 21 layers), the
  blank mask = supervision > 0.5 AND no ink-label pixel within 58 px. Crop = the axis-aligned box of at most
  4472 x 4472 px (20 Mpx) centred on the centroid of the largest 8-connected blank component, clipped to the array.
  Inference: dense_native, same command with `--layer-start 2 --layer-end 19` on the 21-layer crop, forward only.

## 3. Windows and labels
- Window = 289 px square (2.5 mm at 8.64 um), stride 144. Eligible if footprint coverage (any of 31 layers > 0)
  >= 0.75 on the POS render. For the paired G1 comparison a window must also be eligible on every on-sheet shifted
  render; windows failing that are dropped from all three and the count is reported.
- PHerc343 labels: the 18 winner letter boxes (repro343/letter_boxes.json, raw frame) mapped by the alignment above.
  Positive window: box union covers >= 25% of the footprint. Off-text: no footprint pixel within 58 px of any box.
  Others excluded. At stride 144 this is the agreement screen's set: 114 positive, 28 off-text. The same window
  coordinates and labels are applied unchanged to the shifted renders (same grid, same flat frame).
- Blank crops: a window is BLANK if its footprint lies entirely in the blank mask. No positives there.
- Spatial blocks for the bootstrap: block id = (floor(i / 2), floor(j / 2)) over the window-grid indices (i, j)
  (2 x 2 windows, 433 px span). Blocks are resampled with replacement, 2000 replicates, seed 343, percentile 95%
  interval. For differences the same block resample is applied to both maps (paired).

## 4. Signals
- Per map: v = clip((u8 - 64)/128, 0, 1). Rank statistic (G1, G2): z = (v - mean_F)/max(sd_F, 1e-6) over the map's
  own footprint F, S(w) = fraction of footprint pixels in w with z >= 0.885 (the agreement screen's rule, so the
  POS reading-side AUC reproduces 0.841 by construction).
- Absolute statistic (G3 only): z_abs = (v - 0.227156)/0.163374 (the winner's absolute display stats),
  S_abs(w) = fraction with z_abs >= 0.885. Per-footprint standardisation cannot be used on a crop that is all blank,
  because it would force a fixed fraction of pixels above threshold.
- AUC = roc_auc_score(label, S) over positive vs off-text windows; AP reported alongside, never gated.

## 5. Gates
- G1 (PRIMARY, decides the verdict), PHerc343 POS, dense_native, reading side:
  D_s = AUC(POS) - AUC(shift_s) for each on-sheet shift s. PASS iff for every on-sheet shift D_s >= 0.10 AND the
  paired block-bootstrap 95% interval of D_s has lower bound > 0. Exact permutation p-value of AUC(shift_s) against
  chance (labels permuted within blocks, 10000 draws, seed 343) is reported, not gated.
- G2 (secondary), PHerc343 POS, dense_native, reading side: labelled windows with a covariate are split into
  contrast tertiles by equal count. A tertile is evaluable if it holds >= 5 positive and >= 5 off-text windows.
  PASS iff AUC in the lowest evaluable tertile >= 0.70 with bootstrap lower bound >= 0.60. If the lowest tertile is
  not evaluable, G2 is NOT EVALUABLE and only the regression below is reported. Reported with it: OLS slope of S on
  contrast within positives and within off-text windows, each with a block-bootstrap interval.
- G3 (exploratory, no pass/fail): tau = 5th percentile of S_abs over POS positive windows (reading side).
  FPR = fraction of BLANK windows with S_abs >= tau, per crop and pooled, with block-bootstrap intervals.
- Secondary surfaces: PHerc0009B with the same shifted-sheet rule only if a 66-layer render of the central
  1000 x 4000 px of its render frame is produced within budget (render_patch --layers 66 --step 1, as render66.zarr
  was made); otherwise declared NOT RUN. seed42/seed43 on the shifted POS renders, reading side only, descriptive.
- Secondary gate p-values (G2, 0009B G1 if run) are Holm-adjusted at alpha 0.05 across those secondary tests; they
  never change the primary verdict.
- VERDICT: "detectability control PASSES" iff G1 PASSES. G2 and G3 qualify how far the control transfers.
- Transfer rule for screened segments (reported, not gated): c_min = the smallest POS window contrast inside any
  tertile whose AUC >= 0.70. A screened segment (0800mid, 0211CW, 0125CW) is "inside the calibrated contrast range"
  iff its median tile contrast >= c_min. Tile contrast and window contrast use the same formula at different
  footprints; this is a caveat on the comparison, stated with the numbers.

## 6. Stop rules
No threshold, window, normalisation, C, point or group definition is changed after any score is seen. Bug fixes that
do not change a definition are allowed and logged in the result. Any other analysis is labelled exploratory.
If the pitch measurement fails on both sides, the 24-voxel fallback is used on both and the result says so in its
first line.

## 7. Budget and order
~4 h of Mac wall time from the first shifted render. Order: (1) pitch; (2) shifted meshes; (3) shift_hi and shift_lo
renders; (4) on-sheet check from each render's sheet_stats; (5) dense_native both directions on both shifted renders;
(6) per-window contrast on POS; (7) G1, G2 -> RESULT first draft; (8) seeds on shifted renders, reading side;
(9) blank crops and G3; (10) 0009B only if elapsed < 2.5 h at its start. Items not run are declared in the result.

## 8. Known caveats (stated now)
- Off-text windows are scarce (28) and the POS region is text-dense, so AUC intervals will be wide; that is why G1 is
  a difference with a bootstrap bound, not a threshold on a single AUC.
- A one-pitch shift may land on a neighbouring wrap that carries its own, unlabelled, text. The test is that
  LABEL-ALIGNED discrimination collapses, not that the shifted map is empty. The shifted map's mean S is reported.
- The winner's letter boxes are locations, not ground-truth ink masks; ink_9um "validation" overlaps training crops
  (villa PR #2126, 233 of 282); the blank crops come from other scrolls than PHerc343, so G3 is about blank papyrus
  in general, not this surface.
- Contrast is measured on the labelled render and is both a covariate and a possible cause; G2 cannot separate "model
  needs contrast" from "contrast marks a better surface". It bounds the usable range only.
- Pitch varies across the crop; a single P per side is an approximation and the on-sheet check is coarse (median only).
- Mac inference exits with a torch MPS segfault; outputs are complete before exit (NOEXIT wrapper).
