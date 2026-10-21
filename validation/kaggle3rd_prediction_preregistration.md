# Pre-registration: Kaggle 3rd-place nnU-Net predictions vs label holes (written 2026-10-21 before any prediction)

Model: arunodhayan 3rd-place Surface Detection, stage-1 checkpoint `4000epochs_iter6_checkpoint_best.pth`
(3d_fullres, nnUNetResEncUNetMPlans, Apache 2.0). Cascade stage and ridge post-processing NOT run
(pilot). Tile 192, step 0.85, no mirroring unless noted. Run on MPS, no rented GPU.

Caveat fixed in advance: dataset.json says numTraining 786, so this model was trained on most or all
of the 892 Kaggle crops, labels included. Predictions on these crops are in-sample. The test below asks
whether a topology-trained model (clDice) reproduces the labels' holes or bridges them; it cannot show
the labels are wrong, and an in-sample model will lean toward the labels.

Pilot set: the 20 errata crops (33 human-checked holes: 19 CUT, 11 FILL, 3 UNCLEAR).

Gate (stop if failed): median Dice at argmax vs label (label != 2) over the 20 crops > 0.35 (the
recto model's best on any crop). If the gate fails, no hole-level reading is made.

Primary outcome: per decided hole, fill fraction = share of the hole-mask component (same matching as
errata.csv: 26-conn, nearest centre) predicted as surface (argmax == 1). Hypothesis H1: FILL holes get
a higher fill fraction than CUT holes; one-sided Mann-Whitney U, FILL > CUT, alpha 0.05, n = 11 vs 19.
Secondary (descriptive only): count of holes with fill fraction > 0.5 per class; crop-level b1 of the
prediction vs the label from the audit tool.

Reading rule: p < 0.05 and >= 6/11 FILL above 0.5 with <= 4/19 CUT above 0.5 = "model separates the
classes in-sample"; otherwise "no separation" and the lane stops. Either way the result goes into
validation/ as one paragraph with the in-sample caveat in the first sentence.
