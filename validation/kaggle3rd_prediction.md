# Kaggle 3rd-place surface model vs the errata holes (2026-10-21)

**Caveat first.** The model (arunodhayan, 3rd place, Vesuvius Surface Detection, Apache 2.0; nnU-Net
ResEnc-M 3d_fullres checkpoint `4000epochs_iter6_checkpoint_best.pth`) was trained on 786 of the
Kaggle crops, so its predictions on these crops are in-sample. The test asks whether a model trained on
these labels with a topology loss (clDice) reproduces the labels' holes or bridges them. It cannot show
that a label is wrong. Pre-registered before any prediction in
`kaggle3rd_prediction_preregistration.md`.

**Setup.** Stage 1 only (no cascade, no ridge thinning), tile 192, step 0.85, no mirroring, nnunetv2
2.5.1 on Apple MPS (32 s per 320^3 crop). `kaggle3rd_predict.py`, `kaggle3rd_analyze.py`.
20 errata crops, 33 human-checked holes (19 CUT, 11 FILL, 3 UNCLEAR).

**Gate.** Dice at argmax vs label (label != 2): median 0.49, range 0.17 to 0.70. Passes the 0.35 gate
(the recto model's best crop). Predictions are thick (about 1.7x the label's voxels) because the ridge
thinning step was not run; Dice would rise with it.

**Result.** Fill fraction of each errata hole (share of its 26-connected hole component predicted as
surface), `kaggle3rd_prediction_holes.csv`:

| class | n | median fill | holes > 0.5 |
|---|---|---|---|
| FILL (human: should be closed) | 11 | 0.67 | 8 |
| CUT (human: real gap) | 19 | 0.03 | 1 |

One-sided Mann-Whitney, FILL > CUT: p < 0.001. By the pre-registered reading rule (p < 0.05, >= 6/11
FILL above 0.5, <= 4/19 CUT above 0.5) the model separates the two classes in-sample. The three FILL
holes it did not bridge are E01, E02 (sample_00226, 164 and 137 voxels) and E12 (sample_00374).

**What this does and does not say.** A topology-trained model that saw these labels still leaves the
human-CUT holes open and closes most of the human-FILL ones, so the human CUT/FILL calls are not
idiosyncratic: the gaps the audit ranks as defects split the same way for an independent reader of the
CT that was trained toward connectedness. It does not make the model an oracle for the 538 unchecked
holes, because on an in-sample crop a FILL verdict from the model may just be the training label's
neighbourhood. A held-out reading needs the crops the model never saw, which the public plans file does
not identify.

## Follow-ups (2026-10-21, same day)

**Variants on the 20 pilot crops.** Second stage-1 checkpoint (`4000epochs_org_prob0.8_checkpoint_best.pth`),
the 0.65/0.35 ensemble the 3rd-place kernel uses (`kaggle3rd_ensemble.py`), and the kernel's ridge
thinning (`kaggle3rd_post.py`, extracted verbatim from the public notebook: closing, EDT dilation 1,
3D Hessian ridge at 0.20). Same holes, same scoring.

| run | Dice median | FILL > 0.5 (of 11) | CUT > 0.5 (of 19) | MWU p |
|---|---|---|---|---|
| ckpt A (above) | 0.490 | 8 | 1 | < 0.001 |
| ckpt A + ridge | 0.498 | 8 | 1 | 0.001 |
| ckpt B | 0.495 | 8 | 0 | < 0.001 |
| A/B ensemble | 0.495 | 9 | 1 | < 0.001 |
| A/B ensemble + ridge | 0.503 | 9 | 1 | < 0.001 |
| 1st-place m7 nnU-Net alone | 0.709 | 6 | 3 | 0.011 |
| A/B ensemble + m7 (0.5/0.5) | 0.674 | 7 | 2 | 0.003 |

The 1st-place model is the nnU-Net component Scroll Prize re-hosts as `scrollprize/surface_m7_nnunet`
(ResEnc-L, fold 0; the card says it is a partial component of the winning ensemble). It matches the
labels far more closely (Dice 0.71, 30 of 33 crops above 0.6) and is the worse judge of the errata:
it bridges three human-CUT holes (E05 sample_00379, E09 and E10 sample_00137) that every 3rd-place
run leaves open. Adding it to the ensemble does not help, so the 3rd-place pair stays the instrument.
The 2nd-place weights were never published. Ridge thinning raises every fill fraction slightly (CUT
median 0.03 to 0.12) because the dilation step widens the prediction before thinning.

Per-hole, the three FILL holes ckpt A did not bridge: E01 reads 0.15 / 0.73 / 0.51 / 0.65 (A / B /
ensemble / ensemble+ridge) and E02 0.00 / 0.61 / 0.05 / 0.13, so both depend on the checkpoint; E12
(sample_00374) stays below 0.3 in all seven runs and deserves a second look in the CT.

**All 152 flagged crops, ckpt A** (`kaggle3rd_analyze_all.py`; the 117 CT crops not held locally were
pulled from `hf://buckets/scrollprize/datasets/surfaces/kaggle/images`). Dice vs label: median 0.604,
quartiles 0.466 to 0.690, minimum 0.168 (`data/kaggle3rd_prediction_all_dice.csv`). Of the 296
located label holes in 129 of these crops (the `--hole-masks` output), the model bridges 81 (27%,
fill fraction above 0.5) and leaves 137 open (46%, below 0.1); the rest are partial
(`data/kaggle3rd_prediction_all_holes.csv`, one row per hole with its centre). Read with the
33-hole calibration above, the 81 are the fill candidates and the 137 the likely real gaps, which is a
proofreading order for the unchecked holes, not a verdict on any one of them (in-sample, same caveat).

**The predictions' own topology.** Running the audit on the 152 argmax predictions (`--batch`, four
shards) counts 34,305 holes against the labels' 571 (median 96 per crop against 2; 26,499 junction
clusters against 297; 340 fused components against 11). A raw argmax surface prediction is two orders
of magnitude noisier topologically than the hand-corrected label it was trained on, which is the
number behind the earlier two-crop recto comparison (955 and 2,754 against 34) and the reason the
Kaggle kernels all post-process before scoring.
