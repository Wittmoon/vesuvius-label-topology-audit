VERDICT FAIL: stroke-morphology statistic M does not separate letters from blank papyrus; AUC letters(114) vs blank(4500) = 0.474, 95% block-bootstrap CI 0.422 to 0.528 (upper bound < 0.70); secondary tau_M = 0 so FPR = 1.000 (degenerate).

Detectability control only; no claim that any letter is read. PREREG_morph.md (sha256 d5869df6...e66c, pushed as 73fbf4f before any M value existed) was followed exactly.

## Reading
- M (fraction of footprint covered by 8-connected hit components of 30 to 3000 px that are either low-solidity <= 0.6 or elongated, minor/major <= 0.5) is zero for most windows in both sets: nonzero in 43.0% of letter windows and 46.7% of blank windows. Median qualifying components per window is 0 for letters and blanks.
- Letter M: mean 0.0046, p95 0.027, max 0.039. Blank M: mean 0.0058, p95 0.029, max 0.078. No letter exceeds the blank maximum; 4.4% exceed the blank p95 (about chance, 5%).
- AUC slightly below 0.5 in every crop (0.449 to 0.486). The effect is null, not a reversal: the CI includes 0.5.
- The 5th percentile of letter M is 0, so the lane-1 G3 construction is degenerate for M (every blank window satisfies M >= 0). No usable FPR; compare lane B S_abs FPR 0.763.
- Exploratory (no decision weight): variants all null, band 30-1500 AUC 0.488 (0.434 to 0.542), band 60-3000 0.473 (0.421 to 0.526), solidity-only 0.491 (0.474 to 0.512), axis-ratio-only 0.472 (0.421 to 0.527). Letters vs the 28 POS off-text windows: AUC 0.369 (off-text windows have more components, median 30.5 vs 12 for letters, and more M). Median components per window: letters 12, blank 7, off-text 30.5.
- Interpretation limit: the dense_native hit mask at z_abs >= 0.885 carries no stroke morphology that this statistic can use, in this letter set against these in-sample blanks. This does not exclude other morphology statistics, other thresholds, or other maps; those were not tried.

## Deviations
None from PREREG_morph.md. Implementation notes: blank block ids are the lane-B column "block" (crop-keyed, 1125 blocks); letter blocks via statlib.block_ids (43 blocks); letters read from windows_base.csv label == 1 (same 114 (r,c) as windows_pos343.csv). The pre-announced local contact sheet was not produced (low value given the null). Lane B exploratory facts were known when the PREREG was written (disclosed in PREREG section 0).

## Tables
| quantity | value |
|---|---|
| AUC letters vs blank (primary) | 0.4740 (0.4221 to 0.5284), 2000 reps, seed 343 |
| decision | FAIL (upper < 0.70) |
| tau_M (letter p5) | 0.0 (degenerate) |
| FPR_M at tau_M | 1.000 (1.000 to 1.000), 4500/4500 |
| lane B FPR for S_abs at tau 0.04398 | 0.763 |
| per-crop AUC c0..c4 | 0.485, 0.486, 0.467, 0.483, 0.449 |

Files: out/windows_morph.csv, out/metrics_morph.json, scripts/morph.py (winlib.py, statlib.py unmodified copies).
