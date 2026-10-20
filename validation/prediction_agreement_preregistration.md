# Flagged vs unflagged crops: does the surface model disagree more with flagged labels? (pre-registered 2026-10-20 07:30)

Question (from the independent review): do labels the topology audit flags disagree more with an
independent surface prediction than labels it does not flag? If yes, the flags carry a downstream
signal. If no, say so.

## Design, fixed before any prediction on the new crops
- Model: local `surface_recto_3dunet` checkpoint (ps256, epoch 3504), the same one the 10-17
  prediction audit used. Known caveat from that audit: it transfers poorly to Kaggle crops
  (Dice 0.10-0.33), so this test has low power. A null here does not show the flags are useless.
- Crops: every Kaggle crop with an image on disk (45 in kaggle_full/images, chosen earlier for the
  errata and top-ranked work, so flagged crops are over-represented) plus the 8 crops already
  predicted on 10-17. No new downloads.
  - Flagged = `b1_interior > 0` in kaggle_audit_all.csv: 27 crops.
  - Clean = b1_interior 0, b2_total_big 0, n_fused_components 0: 15 + 8 = 23 crops.
  - 3 crops flagged only by cavity or fusion are reported but excluded from the two groups.
- Prediction: predict_crops.py, MPS, per-crop z-score, 256^3 tiles overlap-averaged (same as 10-17).
- Metrics from eval_predictions.py, masked to label != 2: primary = Dice at threshold 0.5;
  secondary = tolerant recall at 0.5 (labelled voxels within 2 vox of a prediction), Dice at 0.3.
- Test: one-sided Mann-Whitney U, flagged < clean, alpha 0.05, on the primary. Spearman between
  b1_interior and Dice over all 50 crops as a dose check.
- Confound: flagged crops have more foreground (fg_frac median 0.052 vs 0.037). Report Spearman
  of Dice vs fg_frac; if |rho| > 0.3, add a rank regression of Dice on group + fg_frac.
- Outcome rule: "signal" only if the primary test is significant AND the sign survives the
  fg_frac control. Otherwise "no signal with this model", reported as such.

## Protocol amendment 08:20, before any result was seen
Compute: the machine is swapping (41 GB swap used by other processes) and a 256^3 tile takes
~190 s on MPS, so 8 overlapping tiles per crop (the 10-17 protocol) would take ~18 h for 53
crops, and one 320^3 tile runs out of MPS memory. Amended protocol: ONE centred 256^3 tile per
crop (`predict_crops.py --center`), metrics restricted to that tile (prob = -1 outside, excluded
from the mask). The 8 crops predicted on 10-17 are re-predicted the same way so every crop is
treated alike. Holes within 32 voxels of a crop face are outside the scored region; b1_interior
is still the crop-level flag. Nothing else in the design changes.

## Secondary, hole-local (added 09:05, before any prediction was inspected)
`hole_local.py`: for each errata hole that lies inside the predicted tile, mean probability inside
the hole voxels, on its 2-voxel label rim, and on label 20-40 voxels away. Descriptive only:
report FILL vs CUT vs UNCLEAR medians of p_hole_mean and p_hole / p_rim. With n <= 7 per class no
test is planned; the question is whether the model predicts sheet through FILL gaps more than
through CUT pockets.

## Protocol check (09:20)
On sample_00001-3, Dice@0.5 inside the centre tile: 8-tile (10-17) 0.257 / 0.263 / 0.143 vs
single centre tile 0.225 / 0.291 / 0.164; voxel correlation of the two probability maps 0.61-0.79.
The single-tile protocol gives the same crop-level numbers to within 0.03.

## Run notes (11:30)
The first run (PID 33826) was reaped at 49/53 crops by the machine's low-memory guard; the 4
missing crops (sample_00890, 00895, 00902, 00910) were re-run with the same `--center --only`
command (`relaunch.sh`). All 53 `pred/*_prob.tif` present before any metric was computed.

## Hole-local result (descriptive, pre-registered 09:05)
`hole_local.csv`: 10 of the 33 errata holes lie inside the centred 256^3 tile (the other 23 are
within 32 voxels of a crop face or outside the tile). Mean probability inside the hole vs on its
2-voxel label rim:

| class (consensus) | n in tile | p_hole median | p_rim median | hole/rim median |
| --- | --- | --- | --- | --- |
| FILL | 2 | 0.565 | 0.591 | 0.91 |
| CUT | 1 | 0.147 | 0.181 | 0.81 |
| UNCLEAR | 7 | 0.390 | 0.350 | 0.93 |

In every hole the probability inside the gap tracks the rim (ratio 0.8-0.9): the model neither
bridges FILL gaps more than CUT pockets nor leaves them empty. The two FILL holes (E28, E29, both
sample_00895) are 4 and 9 voxels and sit on rims at 0.88 and 0.31. With n = 1 and 2 this says
nothing about cut vs fill; it does say the local probability map is not a usable cut/fill
oracle for this checkpoint on these crops. The human verdicts agree with the consensus on the 3
holes that have one (E14 CUT, E28/E29 FILL).

## Result (11:55, all 53 crops, single centred tile)
`agreement.csv` (from `eval/prediction_audit.csv`, pred_masked rows). Groups: flagged 27, clean
23, other 3 (cavity/fusion-only flags, excluded from the test).

| metric | flagged median [range] | clean median [range] | MWU one-sided flagged < clean, p |
| --- | --- | --- | --- |
| Dice @0.5 (primary) | 0.226 [0.028-0.349] | 0.211 [0.105-0.343] | 0.737 |
| tolerant recall @0.5 | 0.430 [0.095-0.891] | 0.372 [0.115-0.733] | 0.740 |
| tolerant precision @0.5 | 0.416 [0.043-0.593] | 0.429 [0.236-0.550] | 0.461 |
| Dice @0.3 | 0.265 [0.029-0.339] | 0.266 [0.179-0.319] | 0.523 |
| tolerant recall @0.3 | 0.703 [0.377-0.956] | 0.708 [0.536-0.978] | 0.423 |

Dose check: Spearman b1_interior vs Dice@0.5 rho = 0.04 (p = 0.77). Confound check: Spearman
fg_frac vs Dice@0.5 rho = -0.05 (|rho| < 0.3, so the rank regression is not required; run anyway:
flagged coefficient +2.67 ranks, t = 0.64, one-sided p = 0.74).

**Outcome under the pre-registered rule: no signal with this model.** The primary test is not
significant and the point estimate has the opposite sign (flagged crops agree slightly better).
This is the low-power case named in the design: the checkpoint reaches Dice 0.03-0.35 on every
crop, so crop-level disagreement is dominated by the model's transfer failure, not by label
defects that affect under 1% of label voxels. A null here does not show the flags are useless;
it shows that crop-level agreement with this checkpoint cannot detect them. A model trained on
Scroll 1 labels, or a hole-local metric on a model that reaches Dice > 0.7, is the test that
could.
