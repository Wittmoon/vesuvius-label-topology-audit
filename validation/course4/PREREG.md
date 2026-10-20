# Course 4 pre-registration: does off-sheet placement predict ink-model error?

Written 2026-10-20 before any analysis code. Committed with its hash before the first run.

## Question
On a rendered ink_9um segment, is the released ink model worse where the papyrus density
peak sits further from the render's centre layer?

## Data (all already on disk, nothing new downloaded)
- Renders: `scratch/ink/data/<seg>/pooled9.zarr` (21 layers), the exact inference inputs.
- Labels + masks: `scratch/ink/data/<seg>/labels/*_{inklabels,validation_mask}.zarr`, middle z slice.
- Predictions: `scratch/ink/predictions/<seg>_default.tif` = released hybrid_3d2d seed42 step-075000,
  layers 2-18 (the released default window). Same shape as the labels (checked 2026-10-20:
  w016 7020x7220, 0814-46527 2130x3455, 1667-w029 9500x7830). Any shape mismatch aborts.
- Segments: `pherc0814-46527` and `pherc1667-w029` are the CONFIRMATORY pair.
  `pherc0139-w016` is EXPLORATORY: the 0.84-0.88 vs 0.65-0.84 split in FINETUNE-DESIGN.md
  was read off it, so it cannot confirm the hypothesis it suggested.
  None of the three is an unseen segment (window sweeps were scored on all three; PR #2126
  overlap caveat applies). The default-window prediction was never selected by us, it is the
  released setting. Tier of any claim: within-segment, released model, released window.

## Offset (per column, from the render itself)
- Profile = gaussian sigma 1 along z of pooled9 (as in recenter.py). peak = argmax.
- Offset = peak - 10 (centre layer, 21 layers). Signed; analysis uses |offset|.
- Weak columns (profile range < 10) are MISSING, not set to the centre (Codex 4.2 fix).
- Per tile: median |offset| over the tile's eligible pixels only.

## Tiling and eligibility (frozen)
- 256x256 tiles on a grid from origin (0,0). Eligible pixel = validation mask > 0 and column not weak.
- Tile eligible if >= 50 ink pixels and >= 50 background pixels among eligible pixels AND
  >= 50% of its validation-mask pixels are non-weak. Report counts of tiles and exclusions.
- Per tile: AUC (primary) and AP (secondary) of the prediction on its eligible pixels, no stride.

## Primary test (one, frozen)
- Spearman rho between tile median |offset| and tile AUC, per segment, no pooling.
- Predicted direction: negative. Minimum meaningful effect: rho <= -0.20.
- Interval: spatial block bootstrap, blocks = 4x4 tiles (1024 px), 1000 resamples, 95% percentile CI.
  Sensitivity: blocks of 2x2 and 8x8 tiles reported alongside.
- Null: 1000 toroidal shifts of the tile offset grid by random whole-tile (dy, dx), both non-zero
  modulo grid, recompute rho; p = fraction of |rho_null| >= |rho_obs|. Keeps spatial structure.
- POSITIVE if BOTH confirmatory segments have rho <= -0.20 with 95% CI excluding 0 and p < 0.05,
  AND the partial test below keeps a negative sign with CI excluding 0 in both.
- NEGATIVE if either confirmatory segment fails any of those.
- UNINFORMATIVE if a confirmatory segment has fewer than 30 eligible tiles.

## Confounder control (part of the primary verdict)
- Per tile also: mean centre-layer CT intensity over eligible pixels (contrast), median profile
  range (prominence), ink prevalence, median distance to the validation-mask edge.
- Partial Spearman: rank-regress AUC and |offset| on the four covariates (per segment), correlate
  residuals. Same block bootstrap CI.
- Also reported: Spearman of each covariate with AUC, so a reader sees what else moves the score.

## Secondary (reported, never selected on)
- AP in place of AUC. Tiles 128 and 512, and the 256 grid shifted by 128 px.
- Windows L0, L1, L3, L4 (seed42-075000) and seed43 L2 predictions where they exist.
- Offset bins (<=1, 1-2, >=2 voxels) with tile counts, for the README table only.
- w016 results, labelled exploratory.

## Not done
- No selection among windows, checkpoints, tile sizes or thresholds for the verdict.
- No training, no new tools, no intervention.

## Output
`scratch/ink/course4/results.json` (every number above), `tiles_<seg>.csv` (one row per tile),
`REVIEWED` written only by the user after reading. Verdict copied to the negative-results ledger
if NEGATIVE.

## Amendment 1 (2026-10-20 03:40, after the first run, before any tile-64 result was seen)
The registered 256-px tiling cannot reach 30 eligible tiles on any segment: the validation masks
are 161k px (0814-46527), 382k px (1667-w029) and 178k px (w016), i.e. 2.5-6 tiles of 256^2.
The registered verdict is therefore UNINFORMATIVE on every segment, and that stands as the
pre-registered result. As a declared exploratory follow-up only, the same analysis is rerun with
64-px tiles (block bootstrap 4x4 = 256 px), eligibility and tests unchanged. Its result cannot
be POSITIVE under this registration; it can only motivate a future registered test on a
segment with a larger held-out mask.
