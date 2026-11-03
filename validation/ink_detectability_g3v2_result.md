FAIL: pooled FPR 0.763 (3434/4500 blank windows at S_abs >= tau = 0.04398), 95% CI 0.744 to 0.782 (2x2 block bootstrap, 2000 reps, seed 343); max per-crop FPR 0.848 (c0, PHercParis4). The pooled lower bound 0.744 is above 0.20, so the pre-registered rule returns FAIL.

# RESULT: G3 v2, false-positive rate of dense_native on blank papyrus (2026-11-03)

Contract: `PREREG_G3v2.md` (sha256 b2feeddab9738a564fa8ed98413afa2a0d6739be99c986b3b313b386f48c3997, re-verified unchanged at the end of the run). Checkpoint: dense_native-016000.rebuilt, md5 187bd2da760f5158c70c0e925efb906f (verified; each job log shows `ckpt_md5 187bd2da`). tau was read from lane-1 `out/metrics_g3.json` and equals the PREREG value; it was not recomputed for any decision (the POS 5th percentile was recomputed only as a consistency check and matches to 1e-12).

Rule applied (PREREG sec 7): PASS iff pooled 95% upper <= 0.20 and max per-crop point FPR <= 0.30; FAIL iff pooled lower > 0.20; else INCONCLUSIVE. Pooled lower = 0.744 > 0.20 -> FAIL. All five per-crop CIs also sit far above 0.20 (lowest lower bound 0.541, c1).

## Reading the verdict (caveats from PREREG sec 9)
- All five segments are in dense_native's training set, so a PASS would have been weak evidence. A FAIL is strong: even on training segments, with unlabelled ink as the only excuse, the model fires S_abs >= tau on about three blank windows in four.
- Unlabelled ink would bias FPR upward. The R2 sensitivity (2.5 mm clear of any label) gives the same pooled FPR (0.763), and the inspection below shows no letter-like structure in the top windows, so unlabelled ink does not look like the explanation.
- tau is permissive by construction (5th percentile of the 114 POS positives), which is why the FPR is high. This result says that blank papyrus clears the lane-1 detectability bar, not that the model marks letters on blank papyrus.

## Deviations from PREREG_G3v2.md
1. Task-text versus PREREG wording: the task text listed 900/900/900/892/886 as the R1 counts. The PREREG says R1 = 900 in all five crops; 900/900/900/892/886 are the R2 counts. The PREREG wins. Guards gate on R1 = 900 and R2 = 900/900/900/892/886; both hold, with 0 mismatches against the survey grids.
2. `scripts/run_infer.py` is the lane-1 driver with two edits only: the WORK path and the exclusion string `ink_detect_ctrl_g3v2_20261103`. The NOEXIT runpy + `os._exit` pattern and the no-kill/wait behaviour are unchanged.
3. Budget overrun (no outcome effect): about 30 min of Mac wall time was budgeted from the first crop cut (22:38:15Z). Inference alone took 38.2 min (22:44:56Z to 23:23:09Z; 437 to 486 s per crop versus about 100 s per crop in lane 1), and the whole run about 50 min. Swap was near full (13.8 of 14.3 GiB used) and free memory was 33 to 53%, which is the likely cause (not separately verified). No retries: all five jobs succeeded on attempt 1 (rc 0), same checkpoint and flags as lane 1.
4. A `--smoke` run of `g3v2_stats.py` on c0 was done once c0 finished and before c1 to c4 existed, to catch code bugs. It printed only the S_abs summary for c0. No code, definition, threshold, window or crop was changed afterwards, and no bug fix was needed.
5. New scripts written for this run: `g3v2_crops.py` (cutter plus guards), `g3v2_stats.py`, `g3v2_contact.py`. `winlib.py` and `statlib.py` are unmodified lane-1 copies.
6. Nothing else deviated. No guard failed, no crop was substituted.

## Crops and guards
| crop | segment | scroll | crop md5 | footprint | label / supervised px | R1 / R2 windows | min distance to label |
|---|---|---|---|---|---|---|---|
| c0 | phercparis4-w09 | PHercParis4 | c46cdd47672fb4f56a3b4734bd0981e4 | 0.9991 | 0 / 0 | 900 / 900 | 5.18 mm |
| c1 | pherc1667-w023 | PHerc1667 | 14a7dbadb23540b1a4cb569f9425b4df | 0.9989 | 0 / 0 | 900 / 900 | 5.18 mm |
| c2 | pherc1667-w013 | PHerc1667 | 801b23c1299a97880df6cf3087e7cd72 | 0.9986 | 0 / 0 | 900 / 900 | 5.18 mm |
| c3 | pherc0139-w016 | PHerc0139 | 20bbd4c108b5173ad125e38e835ad1d3 | 0.9984 | 0 / 0 | 900 / 892 | 2.44 mm |
| c4 | pherc0139-w041 | PHerc0139 | 2b04b600a5089d7a9a6bf19b7776dc7c | 0.9994 | 0 / 0 | 900 / 886 | 1.61 mm |

Inference wall per crop (s): c0 485.5, c1 442.9, c2 456.0, c3 462.1, c4 437.5.

## Primary (R1, all 900 windows per crop)
| set | windows | hits (S_abs >= tau) | FPR | 95% CI (block bootstrap) | blocks |
|---|---|---|---|---|---|
| POOLED (primary) | 4500 | 3434 | 0.763 | 0.744 to 0.782 | 1125 |
| c0 phercparis4-w09 | 900 | 763 | 0.848 | 0.810 to 0.883 | 225 |
| c1 pherc1667-w023 | 900 | 530 | 0.589 | 0.541 to 0.637 | 225 |
| c2 pherc1667-w013 | 900 | 643 | 0.714 | 0.669 to 0.758 | 225 |
| c3 pherc0139-w016 | 900 | 744 | 0.827 | 0.784 to 0.866 | 225 |
| c4 pherc0139-w041 | 900 | 754 | 0.838 | 0.800 to 0.872 | 225 |
| scroll PHercParis4 | 900 | 763 | 0.848 | 0.810 to 0.883 | 225 |
| scroll PHerc1667 | 1800 | 1173 | 0.652 | 0.618 to 0.684 | 450 |
| scroll PHerc0139 | 1800 | 1498 | 0.832 | 0.806 to 0.858 | 450 |
| leave out c0 | 3600 | 2671 | 0.742 | 0.720 to 0.764 | 900 |
| leave out c1 | 3600 | 2904 | 0.807 | 0.786 to 0.826 | 900 |
| leave out c2 | 3600 | 2791 | 0.775 | 0.754 to 0.797 | 900 |
| leave out c3 | 3600 | 2690 | 0.747 | 0.726 to 0.769 | 900 |
| leave out c4 | 3600 | 2680 | 0.744 | 0.723 to 0.766 | 900 |

## Sensitivity: R2 windows only (2.5 mm clear of any label)
| set | windows | hits (S_abs >= tau) | FPR | 95% CI (block bootstrap) | blocks |
|---|---|---|---|---|---|
| R2 pooled | 4478 | 3418 | 0.763 | 0.744 to 0.783 | 1125 |
| R2 c0 | 900 | 763 | 0.848 | 0.810 to 0.883 | 225 |
| R2 c1 | 900 | 530 | 0.589 | 0.541 to 0.637 | 225 |
| R2 c2 | 900 | 643 | 0.714 | 0.669 to 0.758 | 225 |
| R2 c3 | 892 | 742 | 0.832 | 0.789 to 0.869 | 225 |
| R2 c4 | 886 | 740 | 0.835 | 0.798 to 0.870 | 225 |

## Crop-edge effect: outer ring dropped (i or j in {0,29}); interior = 784 windows per crop
| set | windows | hits (S_abs >= tau) | FPR | 95% CI (block bootstrap) | blocks |
|---|---|---|---|---|---|
| interior pooled | 3920 | 2990 | 0.763 | 0.743 to 0.782 | 1125 |
| ring pooled (464 windows) | 580 | 444 | 0.766 | 0.723 to 0.806 | 280 |
| interior c0 | 784 | 654 | 0.834 | 0.794 to 0.873 | 225 |
| interior c1 | 784 | 453 | 0.578 | 0.528 to 0.627 | 225 |
| interior c2 | 784 | 558 | 0.712 | 0.664 to 0.754 | 225 |
| interior c3 | 784 | 666 | 0.849 | 0.807 to 0.885 | 225 |
| interior c4 | 784 | 659 | 0.841 | 0.803 to 0.874 | 225 |

## S_abs of blank windows (descriptive)
| crop | n | mean | median | p95 | max |
|---|---|---|---|---|---|
| c0 | 900 | 0.2331 | 0.2014 | 0.5592 | 0.9875 |
| c1 | 900 | 0.1308 | 0.0685 | 0.4930 | 0.9699 |
| c2 | 900 | 0.1443 | 0.1006 | 0.4198 | 0.8035 |
| c3 | 900 | 0.2638 | 0.2019 | 0.7288 | 1.0000 |
| c4 | 900 | 0.2088 | 0.1742 | 0.5317 | 0.7888 |
| pooled | 4500 | 0.1962 | 0.1404 | 0.5742 | 1.0000 |

## POS positives (n=114) versus blank windows (descriptive)
- blank S_abs: median 0.1404, p95 0.5742, max 1.0000; POS S_abs: min 0.0001, median 0.2740, max 0.7701
- share of 114 POS above blank max: 0.000; above blank p95: 0.070; above blank median: 0.746
- share of 28 POS off-text windows above blank max: 0.000; above blank p95: 0.000; share at S_abs >= tau: 0.821
- AUC POS(114) versus blank(4500) = 0.6735 (95% CI over blank blocks 0.6580 to 0.6893); AUC POS off-text(28) versus blank = 0.4495
- check: 5th percentile of POS S_abs recomputed = 0.04398295039570887 (equals stored tau)

## Post-verdict inspection (exploratory, cannot change the verdict)
Contact sheet: `out/top20_S_abs_contact_sheet.png` (20 highest-S_abs blank windows; left panel CT layer 10, right panel the dense_native v map with hit pixels, z_abs >= 0.885, in red). List with coordinates: `out/top20_windows.csv`.

What it shows:
- The top-20 are dominated by c3 (13 of 20, many adjacent: i 8 to 15, j 13 to 17, one contiguous region around array rows 1440 to 2448, cols 2304 to 2880), then c1 (4: i 20 to 21, j 26 to 27, and i 5 j 29) and c0 (3: i 14 j 1 and 2, and i 7 j 0). None sit on the outer ring except two edge windows (c0 i7 j0 and c1 i5 j29). All but those are interior and all 20 are R2.
- The v map in every one of them is a smooth, low-frequency wash covering most of the window, not stroke-scale structure. The red hit field is a nearly solid plateau with soft dips; the dips line up with dark voids or dark gaps in the CT layer. Nothing in the v map looks like a letter or a line of letters.
- The CT panels show ordinary papyrus fibres (horizontal and vertical weave), dark gaps, cracks, a few bright specks. I see no ink-like marks and no visible surface artefact such as a seam or a rendering defect that would explain the hits. The model responds to the presence of intact fibrous papyrus and goes low over voids, so the behaviour looks like a papyrus-versus-void detector at this threshold.
- This supports reading the FAIL as a property of the model plus the permissive tau, not as unlabelled ink or crop artefacts. It does not prove the absence of faint unlabelled ink in individual windows.

## Files (all under `scratch/ink_detect_ctrl_g3v2_20261103/`)
- `RESULT_G3v2.md` (this file); `out/metrics_g3v2.json`, `out/windows_g3v2.csv` (4500 rows), `out/tables_g3v2.md`, `out/top20_windows.csv`, `out/top20_S_abs_contact_sheet.png`
- `crops/GUARDS.json`, `crops/<k>/crop.vc.zarr`, `crops/<k>/crop_dn.tif`, `crops/<k>/windows_R1_R2.npz`
- `scripts/` (g3v2_crops.py, g3v2_stats.py, g3v2_contact.py, run_infer.py, jobs_g3v2.json, winlib.py, statlib.py), `logs/` (infer/driver.log, per-crop infer and watchdog logs, timeline.tsv, stats_run.log)
