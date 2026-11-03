# PREREG: G3 v2, false-positive rate of dense_native on blank papyrus (2026-11-03)

STATUS: SEALED 2026-11-03 (sha256 in `PREREG_G3v2.md.sha256`, byte-identical copy committed to the evidence repo as `validation/ink_detectability_g3v2_preregistration.md`) before any crop was cut and before any inference was started. The section 10 decisions were made by the agent on 2026-11-03 without user review (the user had not replied); they are recorded as the agent's choices, not the user's. Nothing in this file was written after a dense_native score exists on any of the five crops below. Calibration only; no letters claim; not prize evidence on its own.

Label-only basis: `survey/SURVEY.md`, `survey/survey.csv`. The lane-1 directory `scratch/ink_detect_ctrl_20261103` is read-only and is not modified by this study.

## 0. What was already seen (disclosure)
- Lane 1 (PREREG sha256 d51f92e6...) pre-registered G3 with the blank rule "footprint entirely inside the supervision mask and no ink-label pixel within 58 px". That rule gave 0 windows on all three crops (phercparis4-w05, pherc1667-w018, phercparis4-w07), because supervision is the label dilated by up to about 3 mm (survey section 4). G3 was reported NOT EVALUABLE.
- Lane 1 then ran two exploratory variants on those three crops (V1 shifted grid, V2 blank fraction >= 0.80) after looking only at masks. Results, seen by the user and by me: pooled V2 FPR 0.394 (95% CI 0.095 to 0.634; 33 windows, 15 blocks), from w018 0.684 and w05 0.0, w07 no windows; V1 w018 only 0.80 on 5 windows. Same lane: tau = 0.04398295 sits near the off-text level on the true sheet (82.1 percent of the 28 POS off-text windows have S_abs >= tau, CI 65.2 to 96.3), so tau is a permissive threshold and a high FPR is the a-priori likely outcome.
- Consequence: phercparis4-w05, pherc1667-w018 and phercparis4-w07 were touched by exploratory rules and are NOT used for the primary statistic here. They may only be a labelled-confirmatory addition.
- The pass thresholds in section 7 were chosen after the user knew the lane-1 number 0.394. They are set from the sensitivity argument in section 7, not to guarantee a pass.
- No dense_native output of any kind exists for the five crops below. The crop boxes were chosen from label, supervision and footprint arrays only (survey section 6).
- Read before sealing (no scores involved): the checkpoint's training record `scratch/repro343_20261027/ckpt/train_dense_native.json`. It lists every segment on this disk, including all five crop segments, in its training datasets (`public_2p4_level2_zmean4` families 0139, 1667, Paris4); `patch_min_labeled_coverage` is 0.0 and the loss uses BCE label smoothing 0.5, so blank regions of these segments could be sampled as negatives during training. Its "held out forever" segments (title, w024, w047, w053) are not on this disk. See caveat 2.

## 1. Question
On papyrus that carries no ink label anywhere near it, how often does dense_native, thresholded at the value that keeps 95 percent of labelled-letter windows, still fire? G3 v2 estimates that blank-window false-positive rate (FPR) on segments and crops fixed in advance.

## 2. Inputs (fixed, mirrored from lane 1)
- Model: dense_native-016000.rebuilt, `scratch/repro343_20261027/ckpt/dense_native-016000.rebuilt.pth`, md5 187bd2da760f5158c70c0e925efb906f (checked 2026-11-03).
- Inference command (unchanged from lane 1 G3 jobs): `vesuvius.ink_detection.inference.infer <crop.vc.zarr> <ckpt> <out.tif> --overlap 0.5 --blend-mode hann --batch-size 4 --no-compile --direction forward --layer-start 2 --layer-end 19`, launched through the NOEXIT runpy wrapper (survivors.py) with PYTHONPATH = `pherc0211_trace/inkvilla/vesuvius/src`, via a copy of lane-1 `scripts/run_infer.py` (same memory-pressure and foreign-process waits). No other model, no seeds.
- Crop input: `scratch/ink/data/<seg>/pooled9.zarr` (21 layers, uint8), cut to the box in section 4, written like lane 1 (`blank_crops.py`): zarr group, array `0`, 21 layers, chunks (21, 256, 256), zarr_format 2. No context ring, no resampling.
- Signal: v = clip((u8 - 64) / 128, 0, 1); z_abs = (v - 0.227156) / 0.163374; S_abs(w) = fraction of the window's footprint pixels with z_abs >= 0.885, footprint = any of the 21 crop layers > 0 (lane-1 `winlib.footprint`, `winlib.S_abs_values`).
- tau = 0.04398295039570887, copied from lane-1 `out/metrics_g3.json` (5th percentile of S_abs over the 114 PHerc343 POS positive windows, reading side). tau is NOT recomputed and not changed.

## 3. Blank-window rule
- Primary: R1. A window is BLANK iff its footprint coverage is >= 0.75 AND there is no ink-label pixel (max over the 21 layers of `labels/<seg>_inklabels.zarr`) inside the window enlarged by 116 px (1 mm) on every side. No supervision requirement.
- Sensitivity (reported, not gated): R2 (same with 290 px = 2.5 mm margin).
- Why R1: the survey found the lane-1 rule (R0) gives 0 windows on 23 of 24 segments and the supervision-conditioned rule R3 gives at most 10 windows on any whole new segment, while R1 gives a complete 900-window 30 x 30 block on five new segments, each verified by an independent brute-force recount from raw labels (0 mismatches). R2 loses at most 14 windows in those blocks, so R1 and R2 are almost the same set.
- What "blank" means: unlabelled and at least 1 mm from any label, not verified ink-free. See section 9.

## 4. Segments and crop boxes (fixed)
Half-open array slices `[rows, cols]`, origin a multiple of 144 (crop-local window grid = array grid), 4465 x 4465 px = 19.936 Mpx. In every box: 0 label px, 0 supervised px, 900 windows with coverage >= 0.75, all 900 satisfy R1.

| key | segment | rows | cols | R2 in box | nearest label | segment in dense_native training datasets |
|---|---|---|---|---|---|---|
| c0 | phercparis4-w09 | 576:5041 | 1008:5473 | 900 | >= 5.18 mm | yes |
| c1 | pherc1667-w023 | 1008:5473 | 19440:23905 | 900 | >= 5.18 mm | yes |
| c2 | pherc1667-w013 | 576:5041 | 8352:12817 | 900 | >= 5.18 mm | yes |
| c3 | pherc0139-w016 (array dir `w016`) | 288:4753 | 432:4897 | 892 | 2.44 mm | yes |
| c4 | pherc0139-w041 | 432:4897 | 2448:6913 | 886 | 1.61 mm | yes (also in the native 9.362 um family) |

- There is no out-of-sample stratum: all five segments are in the checkpoint's training datasets (train_dense_native.json), so the draft's listed/unlisted split from `letterfit_A_20261103/PREREG_letterfit_A.md` is dropped. Per-scroll FPR is reported instead (descriptive).
- Scrolls: PHercParis4 (c0), PHerc1667 (c1, c2), PHerc0139 (c3, c4). Crops within a scroll are not independent draws of "blank papyrus".
- Guards before inference (fail loud): each cut crop has shape (21, 4465, 4465), footprint fraction >= 0.99, and re-counting from raw labels gives 0 label px and 900 R1 windows; md5 of each crop array is recorded. Any violation stops the run; no crop is swapped after a score is seen.
- Compute: 5 x 19.936 Mpx = 99.7 Mpx, about 14.5 min of inference at 0.115 Mpx/s, plus waits.

## 5. Windows and blocks
- Window = 289 px square, stride 144, crop-local indices i, j in 0..29, origin (144 i, 144 j). 900 windows per crop, 4500 in total; all are blank by section 3.
- Block id = (crop key, floor(i / 2), floor(j / 2)): 225 blocks per crop, 1125 in total, each with exactly 4 windows (2 x 2 windows, 433 px span).

## 6. Primary statistic
- FPR_pooled = fraction of the 4500 windows with S_abs >= tau.
- Interval: spatial block bootstrap exactly as lane-1 `statlib.boot_draws`: blocks (keyed by crop) resampled with replacement from the pooled 1125, 2000 replicates, `numpy.random.default_rng(343)`, percentile 2.5 / 97.5 (95 percent). Because blocks are drawn from the pooled set, the number of blocks per crop varies by replicate, so crop-to-crop spread enters the interval; with five crops it is still a weak guard, hence the per-crop condition below.
- Also reported with the same bootstrap: FPR per crop, FPR per scroll, leave-one-crop-out pooled FPR.

## 7. Pass rule
- PASS iff the pooled 95 percent upper bound is <= 0.20 AND the largest per-crop point FPR is <= 0.30.
- FAIL iff the pooled 95 percent lower bound is > 0.20.
- Otherwise INCONCLUSIVE (including a clean pooled bound with one dirty crop, which is reported as such).
- Rationale: tau is set at 95 percent sensitivity on the POS positives, so an FPR of 0.20 corresponds to a likelihood ratio LR+ = 0.95 / 0.20 = 4.75 for "this window carries ink" versus "this window is blank". Above that, a window-level hit says little. The per-crop cap stops one dirty crop being averaged away. The numbers 0.20 and 0.30 are fixed here (section 10).
- A FAIL is a statement about window-level detection at tau, not a verdict on the model overall, and is read together with caveat 1 in section 9. A PASS is read together with caveat 2: on in-sample blank papyrus it is a necessary condition, not sufficient evidence that the model is quiet on blank papyrus it has never seen.

## 8. Descriptive outputs (not gated)
- Mean, median, p95, max of S_abs per crop; share of windows at S_abs >= tau under R2 only; FPR after dropping the outer ring of windows (i or j in {0, 29}) to show the crop-edge effect of having no context ring.
- Share of the 114 POS positives above the max and above the p95 of blank S_abs; AUC of POS positives versus blank windows (as in lane-1 extras).
- After the verdict is computed (exploratory, cannot change it): inspect the 20 highest-S_abs blank windows for unlabelled ink or surface artefacts.

## 9. Caveats (stated now)
1. Unlabelled ink biases FPR upward. These segments are labelled sparsely (0.35 to 4.3 percent of footprint), so R1 windows can contain real, unlabelled ink. That makes a PASS conservative and a FAIL ambiguous.
2. In-sample bias downward, now confirmed at segment level. All five segments are in dense_native's training datasets (train_dense_native.json). With `patch_min_labeled_coverage` 0.0 the sampler was free to draw patches from these blank regions, and with BCE label smoothing 0.5 those patches were trained toward the smoothed negative, so the model may have learned these exact textures as "not ink". The FPR measured here is therefore a lower bound on the out-of-sample FPR, and a PASS is weak; a FAIL is strong. Whether these particular patches were drawn is not recoverable from the record. The checkpoint's held-out segments (title, w024, w047, w053) are the right material for an out-of-sample G3 v3 and would need their surface volumes and labels downloaded first.
3. tau is permissive (section 0), so the expected FPR is not small and the FAIL branch is plausible.
4. The crops come from three scrolls and five segments; the bootstrap treats blocks within a crop as exchangeable units and does not model scroll-level variation.
5. No context ring: windows near the crop edge see zero padding in the model; section 8 reports the effect, the primary uses all 900 windows.
6. Lane-1 caveats on the absolute statistic apply (display stats come from the winner's render, not from these crops).

## 10. Decisions (made by the agent on 2026-11-03 before sealing; the user had not reviewed the draft)
- Pass thresholds: 0.20 (pooled 95 percent upper bound) and 0.30 (largest per-crop point FPR), as drafted. Reason: 0.20 is LR+ 4.75 at the 95 percent sensitivity operating point; a looser 0.30 (LR+ 3.2) would let a window-level hit carry almost no weight, which defeats the purpose of the control.
- Primary on all five crops (4500 windows, 1125 blocks). Reason: the draft's alternative (c0 and c4 only, as a no-in-sample-doubt set) no longer exists, since all five are in-sample (section 4); the larger set gives the tighter interval.
- No extra crops and no labelled-confirmatory arm in this study. Reason: more in-sample crops do not remove caveat 2; the three lane-1 segments were touched by exploratory rules. The out-of-sample follow-up is the held-out segments named in caveat 2, as a separate G3 v3 PREREG.
- R1 stays primary, R2 is the sensitivity check, as drafted. Reason: they differ by at most 14 of 4500 windows.

## 11. Order, stop rules, budget
Order: (1) seal this file; (2) cut crops and run the guards; (3) inference for c0 to c4; (4) S_abs and statistics with copies of lane-1 `winlib.py` and `statlib.py`; (5) RESULT with the verdict in its first line; (6) exploratory window inspection. No threshold, window, rule, crop or tau is changed after any score is seen; bug fixes that do not change a definition are logged in the result; anything else is labelled exploratory. A crop that fails a guard stops the run and is reported, not replaced. Budget about 30 min of Mac wall time from the first crop cut.
