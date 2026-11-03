VERDICT: detectability control PASSES (G1 PASS on both on-sheet shifts, D = 0.46 and 0.61; G2 FAIL; G3 NOT EVALUABLE as pre-registered; shifted-sheet AUCs fall BELOW 0.5, a reversal rather than a null; PHerc0009B gives the same pattern).

## Deviations

PREREG: PREREG.md, sha256 d51f92e69ba8424c49ab8ba10930ffec0f358adb1ecbd8389a4ee82e8977a7bc (verified unchanged at the end; PREREG.md.sha256 untouched). This is a calibration of the detector, not prize evidence, and makes no letters claim. No definition in the PREREG was changed. Everything below is an implementation choice, a clarification, a fallback the PREREG itself provides, or a stop-rule event.

Stop-rule event (the only one): G3 has zero blank windows under the pre-registered definition. PREREG section 3 defines a BLANK window as 289 px, stride 144, footprint coverage >= 0.75, footprint entirely inside the blank mask. Read as a stride-144 grid from the crop origin, that gives 0 / 0 / 0 windows in phercparis4-w07 / pherc1667-w018 / phercparis4-w05 (logs/g3_exploratory_defs.txt, written before any blank ink map existed). The definition was not changed. G3 is declared NOT EVALUABLE; two exploratory variants (V1, V2) are reported and labelled as such in the G3 section. Their definitions were fixed from the masks alone, at 18:36:44Z (V1) and 18:39:14Z (V2), before the first blank-crop ink map was finished (18:39:37Z) and before any blank score existed.

1. Shift units. The task brief suggested dividing the shift by 20. The PREREG says level-0 voxels, and I checked that the tifxyz x/y/z values are level-0 voxel coordinates (the 0.05 scale only maps node index to render pixel). I applied P voxels directly and measured the written meshes: mean node displacement 24.000002 (shift_hi) and 15.999998 (shift_lo) voxels. PREREG followed.
2. High-side pitch fallback. On both surfaces no local maximum exists above the central peak within the 66 layers, so P_hi uses the 24-voxel default, as the PREREG provides. Only one side fell back on each surface, so the "state it in the first line" rule (both sides fail) does not apply; it is stated here and under Pitch.
3. Normals. The POS tifxyz has no mask file; invalid nodes are the -1 markers. 849 of 27598 valid nodes (border or next to an invalid node) have no central-difference normal and took the nearest finite normal, so the validity pattern of both shifted meshes is identical to the source and every valid node moves by exactly P. Same for 0009B (1239 of 87961 nodes). Recorded in scripts/shift_mesh.py and scripts/shift_mesh_0009b.py.
4. Step order. Contrast per window (step 6) was computed while the shifted renders were running (it reads only the existing POS render and touches no ink score). The on-sheet check (step 4) ran before any shifted ink map existed, on both surfaces. Seeds and blank-crop inference ran after the first draft of this file, as the PREREG order requires (first draft saved as logs/RESULT_first_draft_steps1-7.md). Step 10 (0009B) started at 18:45:46Z, 0.50 h after the first shifted render, inside the 2.5 h limit.
5. Sanity gate added. Before the shifted work I recomputed the POS reading-side AUC from the existing maps: AUC 0.84085, AP 0.96066, blind side 0.54073, max |S - calibration CSV| 5e-6, labels match the calibration windows. It decides nothing; it only confirms that the window grid, alignment and S rule reproduce the agreement screen. The same check on 0009B reproduced AUC 0.95514 and max |S - CSV| 5e-6.
6. Own inference driver. Inference was launched by scripts/run_infer.py (the same command and NOEXIT wrapper as the agreement screen, plus a watchdog, checkpoint md5 assertion and a free-memory settle), not the agreement screen's run_jobs.py. The brief's pgrep check for competing jobs was done by hand before launches; its output was not logged, and no process I did not start was killed.
7. Blank-crop prep. Only layer 10 of the 21-layer label and supervision arrays is non-empty, so masks are computed from that layer. Measured blank areas are 3.762 Mpx (phercparis4-w07), 6.204 Mpx (pherc1667-w018), 15.142 Mpx (phercparis4-w05), against the PREREG's disclosed label-only counts of 3.84 / 6.26 / 15.3. The mask rule (supervision > 0.5 and no ink pixel within 58 px) is as written. The first blank_crops.py run crashed after the masks on a zarr v3 API change (create_dataset to create_array); a bug fix, not a definition change. A second launch of the unfixed script started by mistake and was killed (my own process).
8. Render json window. The POS shifted renders' own window json (shift_hi [13,30], shift_lo [8,25]) was not used; the ink window is fixed at [8,25], reading side fwd, as the PREREG says.
9. 0009B interpretations (the PREREG says only "the same shifted-sheet rule"). (a) The ink window is [9,26], the window of the existing unshifted 0009B control map, so shifted and unshifted maps differ only by the sheet. (b) The shifted maps use `--direction forward` through the NOEXIT wrapper; the unshifted map came from hunt.py's plain infer with `--direction both`; model, overlap, Hann blend and batch size are identical, and only the reading side was scored (the blind side was not run). (c) The shifted renders cover the full 7040 x 5700 render frame of the existing control (hunt.py's render, 31 layers, step 1.0, scripts/render0009b.py); the 66-layer render is only the central 1000 x 4000 px used for the pitch. (d) hi and lo are signed along the render_patch +n direction. (e) On-sheet range taken literally as [11,19]. (f) Eligible windows: footprint coverage >= 0.75 on the unshifted render and on every on-sheet shifted render (0 dropped).
10. Holm. The PREREG defines no G2 p-value; the only defined secondary p-values are the within-block permutation p of AUC(shift) against chance. I applied Holm (alpha 0.05) to the two 0009B permutation p-values, an interpretation. The 0009B G1-style verdict below uses the same D >= 0.10 and bootstrap-lower-bound rule as G1 and is secondary only; it cannot change the primary verdict. I added a supplementary bootstrap share (replicates with AUC <= 0.5), labelled supplementary.
11. Blank-crop grid origin. "Window grid" for blank crops is read as the stride-144 grid from the crop origin (the crop has no POS coordinate frame). This reading, and no other, produced the zero count.

## Pitch

POS (PHerc343) source: repro343_20261027/render66.zarr, 66 layers 1 voxel apart, layer 33 = surface; 5,851,435 columns valid in all 66 layers (88.6 percent); profile smoothed by a 3-point moving mean. Output: out/pitch.json. Local maxima of the smoothed profile: layers 2, 20, 36. Central peak = layer 36 (nearest to layer 33 within 4). Mean intensity at the peak 94.8; at layer 20 90.6; at layer 2 88.7.

- POS: P_lo = 36 - 20 = 16 voxels (measured). P_hi = 24 voxels (FALLBACK: no local maximum above layer 36 within the 66 layers).

PHerc0009B source: out/b0009/render66_0009B.zarr, 66 layers, central 1000 x 4000 px of the render frame; 3,999,025 valid columns (99.98 percent). Local maxima: layers 19 and 34; central peak = layer 34. Output: out/b0009/pitch_0009B.json.

- 0009B: P_lo = 34 - 19 = 15 voxels (measured). P_hi = 24 voxels (FALLBACK: no local maximum at least 12 layers above the central peak; the profile rises toward layer 65).

Direction on POS, from the umbilicus file (descriptive): the node normal points away from the umbilicus (mean n . unit-to-umbilicus in xy = -0.784; only 0.26 percent of nodes have it pointing toward). shift_hi (X + 24 n) therefore moves the sampled sheet away from the umbilicus (mean displacement . to-umbilicus = -18.8 voxels); shift_lo (X - 16 n) moves it toward the umbilicus (+12.5). No umbilicus file was used for 0009B.

## On-sheet check (step 4, decided before any shifted ink map was read)

Rule: the shifted render's sheet_stats peak_layer_median must lie in [11, 19].

| surface | shift | peak_layer_median | contrast (tile) | on-sheet |
|---|---|---|---|---|
| POS | shift_hi (+24 n) | 17 | 1.0277 | yes |
| POS | shift_lo (-16 n) | 12 | 1.0373 | yes |
| 0009B | shift_hi (+24 n) | 13 | 1.0276 | yes |
| 0009B | shift_lo (-15 n) | 14 | 1.1309 | yes |

All four shifts are on-sheet, so all enter their G1. POS: valid-node fraction 0.7336 and full-column fraction 0.71 are identical to the POS render; all 142 labelled windows are eligible on both shifted renders. POS itself: peak_layer_median 12, tile contrast 1.0781. 0009B unshifted control: peak_layer_median 13, contrast 1.1467. The check is coarse (a median of the per-column peak layer only), as the PREREG notes. On 0009B it cannot tell a shifted sheet from the original, since the shifted medians (13, 14) sit where the unshifted one does; it shows only that a bright layer sits near the middle of the window, which is also what a neighbouring wrap would give.

## G1 (primary): dense_native, reading side, PHerc343 POS, 114 positive and 28 off-text windows (53 spatial blocks)

| map | AUC | 95% CI (block bootstrap) | AP | mean S letters | mean S off-text |
|---|---|---|---|---|---|
| POS (existing map, unshifted) | 0.8409 | 0.768 to 0.906 | 0.9607 | 0.252 | 0.074 |
| shift_hi | 0.3797 | 0.228 to 0.539 | 0.7697 | 0.147 | 0.187 |
| shift_lo | 0.2331 | 0.134 to 0.346 | 0.7215 | 0.101 | 0.170 |

Chance AP is 0.803. Blind-side (reverse) AUC: POS 0.541, shift_hi 0.436, shift_lo 0.556.

| shift | D = AUC(POS) - AUC(shift) | paired 95% CI | rule (D >= 0.10 and lower bound > 0) |
|---|---|---|---|
| shift_hi | 0.4612 | 0.289 to 0.610 | PASS |
| shift_lo | 0.6078 | 0.488 to 0.720 | PASS |

G1 PASSES. Label-aligned discrimination does not survive moving the sampled sheet.

Read this carefully: the shifted AUCs are not near 0.5, they are below it (shift_lo upper bound 0.346; shift_hi interval 0.228 to 0.539 reaches 0.5). On the shifted sheets the off-text windows score higher than the letter windows. A pure null would give about 0.5 and a D near 0.34, so the D values are inflated by a reversal that the pre-registered G1 cannot tell apart from a null. Something other than a flat null is going on, and I have not tested why. The PREREG caveat (a one-pitch shift can land on a neighbouring wrap with its own unlabelled text, which need not sit under the 18 winner boxes) is a candidate but untested. The S-versus-contrast Spearman on the shifted maps is near zero (-0.08, -0.06) against +0.45 on POS, so the reversal is not a contrast effect. Mean S over letter windows falls from 0.252 to 0.147 and 0.101, while mean S over off-text windows rises from 0.074 to 0.187 and 0.170.

Permutation p-values (as pre-registered: within-block, 10000 draws, seed 343, AUC against chance): shift_hi 0.756, shift_lo 1.000. These carry no information: the within-block permutation has essentially no power on this layout, because the text region and the off-text region are spatially separate and most 2 x 2 blocks hold a single label class. Even the unshifted POS AUC of 0.841 gets p = 0.501. A supplementary unrestricted label permutation (not pre-registered) gives POS p = 0.0001 (the floor for 10000 draws) and p = 0.974 and 1.000 for the two shifts under the same one-sided direction, which says nothing about whether a below-chance AUC is itself significant; the bootstrap intervals above are the better guide.

## G2 (secondary): contrast tertiles, dense_native, reading side, POS windows with a covariate (n = 142)

| tertile | contrast range | n pos / off | mean S letters / off | AUC | 95% CI | evaluable |
|---|---|---|---|---|---|---|
| 1 (lowest) | 1.0557 to 1.1539 | 31 / 17 | 0.182 / 0.082 | 0.7192 | 0.558 to 0.859 | yes |
| 2 | 1.1549 to 1.2296 | 39 / 8 | 0.214 / 0.066 | 0.8494 | 0.709 to 0.949 | yes |
| 3 | 1.2301 to 1.6204 | 44 / 3 | 0.335 / 0.046 | not evaluable (3 off-text) | | no |

G2 FAILS: the lowest evaluable tertile has AUC 0.719 (>= 0.70) but its bootstrap lower bound is 0.558, below the required 0.60.

Contrast is a strong covariate of the labels: AUC of contrast alone as a label predictor is 0.764; correlation of contrast with the label is 0.316. OLS slope of S on contrast within positives is 0.630 (95% CI 0.251 to 0.975, r 0.441, n 114); within off-text it is -0.153 (95% CI -0.468 to 0.056, r -0.182, n 28). So letter-window S rises with contrast; off-text S does not. Tertile 3 is not evaluable, so the high-contrast range cannot be assessed against off-text windows from this surface.

Transfer rule (reported, not gated): c_min = 1.0557, the smallest window contrast in a tertile with AUC >= 0.70 (tertile 1). Median tile contrast of the screened segments: 0800mid 1.091 (inside), 0211CW 1.075 (inside), 0125CW 1.026 (outside, below c_min). Caveat from the PREREG: tile contrast and window contrast use the same formula at different footprints, so this comparison is approximate. Also c_min rests on a tertile whose lower AUC bound (0.558) does not clear the G2 bar; the transfer rule as written looks only at the point AUC.

## Seeds on the shifted POS renders (hybrid_3d2d seed42 and seed43, reading side, descriptive, same 114 / 28 windows)

| seed | map | AUC | 95% CI | AP | mean S letters / off | D vs POS (paired 95% CI) |
|---|---|---|---|---|---|---|
| 42 | POS | 0.7497 | 0.635 to 0.856 | 0.9336 | 0.216 / 0.117 | |
| 42 | shift_hi | 0.3020 | 0.167 to 0.474 | 0.7456 | 0.109 / 0.156 | 0.448 (0.221 to 0.631) |
| 42 | shift_lo | 0.4066 | 0.300 to 0.523 | 0.7712 | 0.101 / 0.124 | 0.343 (0.217 to 0.472) |
| 43 | POS | 0.7594 | 0.662 to 0.854 | 0.9371 | 0.193 / 0.099 | |
| 43 | shift_hi | 0.4383 | 0.271 to 0.632 | 0.8047 | 0.111 / 0.117 | 0.321 (0.112 to 0.511) |
| 43 | shift_lo | 0.5954 | 0.387 to 0.780 | 0.8317 | 0.114 / 0.093 | 0.164 (-0.010 to 0.384) |

Chance AP 0.803. Under the G1 rule applied descriptively, three of the four seed-by-shift cells pass; seed43 shift_lo has D 0.164 but a lower bound of -0.010 and would not. Both seeds sit below dense_native on the unshifted POS (AUC 0.75 and 0.76 against 0.84), and both place the shifted maps at or below 0.5 on every cell except seed43 shift_lo (0.595, interval 0.387 to 0.780, containing 0.5). So the direction of the effect (letter windows lose their edge, off-text windows keep or gain score) is shared by three models, but the size of the reversal is model-dependent and seed43 shift_lo looks like a null instead. Not gated.

## G3 (exploratory, no pass/fail): blank-papyrus false-positive rate

Status: NOT EVALUABLE as pre-registered. The pre-registered count of BLANK windows (stride-144 grid from the crop origin, coverage >= 0.75, footprint entirely inside the blank mask) is 0 / 0 / 0 for phercparis4-w07 / pherc1667-w018 / phercparis4-w05. No definition was changed (see Deviations).

Reference quantities (these use only the existing POS map and the three blank crops):
- tau (5th percentile of S_abs over the 114 POS positive windows, reading side) = 0.04398. S_abs over positives: min 0.0001, median 0.274, max 0.770. S_abs is the PREREG absolute statistic: z_abs = (v - 0.227156)/0.163374, S_abs = fraction of footprint pixels with z_abs >= 0.885.
- POS off-text windows (n 28): mean S_abs 0.133; 82.1 percent (95% CI 65.2 to 96.3) are at or above tau. So tau sits at roughly the off-text level on the true sheet, which makes any FPR hard to read: a tau this low is exceeded by most windows that carry no label on the true sheet.
- Blank-pixel statistics (all pixels of each crop's blank mask): mean v 0.0462 (w07), 0.0533 (w018), 0.0256 (w05); fraction of blank pixels with z_abs >= 0.885: 0.0152, 0.0283, 0.0078.

Exploratory variants (definitions fixed from the masks only, before any blank map was read; neither is the PREREG G3):
- V1: stride-144 grid shifted by the offset in {0,16,...,128}^2 that maximises the number of entirely-blank windows. Result: w07 0, w018 5 (offset 80, 64), w05 0.
- V2: crop-origin stride-144 grid, footprint coverage >= 0.75, blank-mask fraction of the footprint >= 0.80. Result by mask: w07 0, w018 19, w05 14.
- Statistic in both: S_abs over the window's blank-mask pixels only; FPR = fraction of windows with S_abs >= tau; blocks floor(i/2), floor(j/2) of the crop-grid indices; 2000 replicates, seed 343.

| variant | crop | n windows | FPR | 95% CI | blocks | mean S_abs | max S_abs |
|---|---|---|---|---|---|---|---|
| V1 | w018 | 5 | 0.80 | 0.0 to 1.0 | 3 | 0.0762 | 0.1237 |
| V1 | pooled | 5 | 0.80 | 0.0 to 1.0 | 3 | 0.0762 | 0.1237 |
| V2 | w07 | 0 | | | | | |
| V2 | w018 | 19 | 0.684 | 0.333 to 0.909 | 6 | 0.0688 | 0.1537 |
| V2 | w05 | 14 | 0.0 | 0.0 to 0.0 | 9 | 0.000007 | 0.0001 |
| V2 | pooled | 33 | 0.394 | 0.095 to 0.634 | 15 | 0.0396 | 0.1537 |

Extras (exploratory): V1: 81.6 percent of the 114 POS positives score above the highest blank window (0.1237), and AUC of POS positives against V1 blank windows is 0.896; 50 percent of POS off-text windows are above that highest blank window. V2: 71.9 percent of positives score above the highest blank window (0.1537), 100 percent above the median blank window, AUC 0.940; 35.7 percent of POS off-text windows are above the highest blank window.

What this does and does not say. The pooled V2 FPR of 0.39 comes entirely from w018 (0.68); w05 gives 0 and w07 contributes no windows, so the pooled figure is a mix of one noisy crop and one clean crop, not an estimate for blank papyrus in general. Only 15 blocks stand behind it (3 behind V1), and the intervals are wide. Most letter windows do score above every blank window, but about a third to a half of the true-sheet off-text windows also do, so on this model the S statistic at tau does not separate "no ink" from "no labelled ink". The G3 gate is not met in the pre-registered form and I draw no FPR conclusion for transfer to other segments.

## PHerc0009B shifted-sheet (step 10, secondary, RAN)

Pitch P_lo = 15 (measured), P_hi = 24 (fallback). Both shifts on-sheet (peak 13 and 14). dense_native, reading side, window [9,26], 152 labelled windows (123 positive, 29 off-text, 45 blocks), 0 dropped for shifted-render coverage. The existing unshifted map reproduces AUC 0.9551 exactly.

| map | AUC | 95% CI | AP | mean S letters / off | perm p vs chance (Holm) |
|---|---|---|---|---|---|
| unshifted | 0.9551 | 0.905 to 0.988 | 0.9901 | 0.296 / 0.055 | |
| shift_hi (+24 n) | 0.4651 | 0.318 to 0.620 | 0.8020 | 0.270 / 0.288 | 0.952 (1.000) |
| shift_lo (-15 n) | 0.2820 | 0.173 to 0.398 | 0.7590 | 0.200 / 0.283 | 0.9997 (1.000) |

Chance AP 0.809.

| shift | D = AUC(unshifted) - AUC(shift) | paired 95% CI | G1-style rule |
|---|---|---|---|
| shift_hi | 0.4900 | 0.344 to 0.631 | PASS |
| shift_lo | 0.6731 | 0.547 to 0.792 | PASS |

Secondary G1-style result on 0009B: PASS, and it does not touch the primary verdict. The pattern matches POS. shift_hi is consistent with a null (interval contains 0.5; supplementary bootstrap share with AUC <= 0.5 is 0.67); shift_lo is a reversal (interval entirely below 0.5; share 1.00). One feature differs from POS and deserves a flag: on 0009B the shifted maps fire strongly on both classes. Mean S over off-text windows goes from 0.055 on the true sheet to 0.288 and 0.283 on the shifted sheets, and letter windows keep most of their score (0.296 to 0.270 and 0.200). So the shifted-sheet score is not low; it is simply no longer aligned with the labels, and it is higher than the unshifted off-text level. The Holm-adjusted permutation p-values are 1.0 for both (they test AUC above chance, and the shifted AUCs are at or below it).

## Wall-clock per step (UTC, 2026-11-03; first shifted render started 18:15:54Z, last step ended 19:01:26Z, 45.5 min of the ~4 h budget)

Source: logs/timeline.tsv (launcher rows carry wall_s; rows without one, such as onsheet_check and contrast_windows, have start times approximated from neighbouring steps or file mtimes, as their note column says; the file's row order is not chronological).

| step | start | end | seconds |
|---|---|---|---|
| pitch (POS) | 18:10:56 | 18:10:58 | 2 |
| sanity gate | 18:14:55 | 18:14:55 | under 1 |
| shifted meshes (POS) | 18:15:36 | 18:15:36 | under 1 |
| render shift_hi (POS) | 18:15:54 | 18:17:44 | 110 |
| contrast per window (POS) | 18:16:47 | 18:16:47 | under 1 |
| render shift_lo (POS) | 18:17:44 | 18:19:21 | 97 |
| on-sheet check (POS) | 18:19:21 | 18:20:04 | 43 |
| dense_native shift_hi (POS) | 18:20:12 | 18:22:37 | 145 |
| dense_native shift_lo (POS) | 18:22:37 | 18:25:15 | 158 |
| G1 and G2 | 18:25:54 | 18:26:55 | 61 |
| blank-crop prep | 18:27:17 | 18:29:09 | 112 |
| seed42 shift_hi / shift_lo | 18:31:47 | 18:34:09 | 70 / 71 |
| seed43 shift_hi / shift_lo | 18:34:09 | 18:36:38 | 71 / 78 |
| seeds analysis | 18:38:02 | 18:38:11 | 9 |
| blank dense_native w07 / w018 / w05 | 18:38:03 | 18:43:02 | 94 / 104 / 100 |
| G3 analysis | 18:43:37 | 18:43:58 | 21 |
| 0009B 66-layer render | 18:45:51 | 18:46:52 | 61 |
| 0009B pitch | 18:46:52 | 18:47:04 | 12 |
| 0009B shifted meshes | 18:47:35 | 18:47:35 | under 1 |
| 0009B render shift_hi / shift_lo | 18:47:48 | 18:55:26 | 226 / 232 |
| 0009B on-sheet check | 18:55:40 | 18:55:47 | 7 |
| 0009B dense_native shift_hi / shift_lo | 18:55:48 | 19:01:00 | 158 / 154 |
| 0009B G1 | 19:01:17 | 19:01:26 | 9 |

## Not run

- G3 as pre-registered (0 blank windows; exploratory V1 and V2 reported instead).
- 0009B blind side (reverse direction) and the 0009B seed models; the PREREG asks for neither.
- No test of why the shifted AUCs fall below 0.5 (neighbouring-wrap text, a model artefact, or something else). Untested.

## Files

All under /Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/ink_detect_ctrl_20261103/
- RESULT.md (this file); PREREG.md and PREREG.md.sha256 (unchanged).
- out/windows_pos343.csv, out/windows_blank.csv, out/windows_0009B.csv, out/windows_base.csv: window-level scores.
- out/metrics.json (merge of metrics_g1g2.json, metrics_seeds.json, metrics_g3.json, metrics_0009B.json, pitch, on-sheet and mesh records); the four per-step files sit beside it.
- out/pitch.json, out/onsheet.json, out/shift_meshes.json, out/shift_hi.tifxyz, out/shift_lo.tifxyz (POS); out/blank_windows_def.json, out/blank_v2_windows_def.json.
- out/b0009/: pitch_0009B.json, onsheet_0009B.json, shift_meshes_0009B.json, shift_hi.tifxyz, shift_lo.tifxyz, render66_0009B.zarr, render_shift_hi and render_shift_lo (vol.zarr, footprint.npy, stats.json), ink_shift_hi and ink_shift_lo (t000_dn.tif).
- render_shift_hi/, render_shift_lo/ (POS renders) and ink/ (POS shifted ink maps, seed maps, blank-crop maps), in the work dir root.
- logs/timeline.tsv, logs/g1_0009b.log, per-job inference logs, logs/RESULT_first_draft_steps1-7.md, logs/g3_exploratory_defs.txt.
- scripts/: pitch.py, shift_mesh.py, run_render.sh, winlib.py, statlib.py, build_windows.py, onsheet.py, run_infer.py, g1g2.py, seeds.py, blank_crops.py, blank_windows.py, blank_v2_defs.py, g3.py, merge_metrics.py, pitch0009b.py, shift_mesh_0009b.py, render0009b.py, onsheet0009b.py, g1_0009b.py and the jobs_*.json files.
- No crop-derived images were written. Nothing was posted, committed or opened as a PR.
