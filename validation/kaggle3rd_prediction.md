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
