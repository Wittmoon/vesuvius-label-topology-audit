# Placement offset vs ink-model error: pre-registered test, uninformative (2026-10-20)

## Registered verdict: UNINFORMATIVE (all three segments)
256-px tiles: 0814-46527 5 eligible tiles, 1667-w029 and w016 fewer than 30. The ink_9um
validation masks are 161k-382k px, too small for the registered tile-level test.

## Exploratory (amendment 1, 64-px tiles, same tests): no signal, direction opposite to prediction
| segment | eligible tiles | rho(|offset|, AUC) | 95% CI (4x4 blocks) | toroidal p | partial rho (4 covariates) |
| --- | --- | --- | --- | --- | --- |
| 0814-46527 | 30 of 53 | +0.13 | [-0.46, +0.59] | 0.67 | +0.18 [-0.80, +0.67] |
| 1667-w029 | 47 of 127 | +0.08 | [-0.30, +0.43] | 0.75 | +0.02 [-0.34, +0.47] |
| w016 | 28 (below 30) | not computed | | | |

- Predicted rho <= -0.20. Observed positive, intervals span zero, null p > 0.6. Not a negative
  with power: 6-8 bootstrap blocks per segment.
- Every eligible tile has median |offset| >= 2 (quartiles 3-6 voxels), so the <=1 and 1-2 bins
  are empty; the comparison the FINETUNE-DESIGN.md split made on w016 (<=1 vs >=2) cannot be
  repeated on the validation masks. The large per-column offsets are consistent with
  recenter.py's w016 stats (58% of columns > 2) but have not been checked by eye on these tiles.
- Covariates with AUC: contrast -0.27 and prominence -0.18 on 1667-w029; +0.11 / +0.23 on 0814.
  Nothing clears zero either.

## Consequence
The claim "the placement audit's off-sheet measure predicts where the released ink model is
worse" is not supported at the available power and is not made in the packet. Course 4 ends
here; a future test needs a segment with a held-out mask of several Mpx, or many segments.
Files: `validation/course4/` (PREREG.md with amendment, analyse.py, results_*.json, tiles_*.csv).
