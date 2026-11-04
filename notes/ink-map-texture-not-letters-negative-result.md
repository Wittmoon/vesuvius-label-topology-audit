# The dense_native ink map on PHerc Paris 4 reads texture, not letters (negative result)

Three pre-registered tests, run 2026-11-03 and 2026-11-04, ask the same question from three
directions: does the Challenge's dense_native 2D ink map carry letter shape, or only image texture
(contrast, energy, spatial frequency)? All three fail the same way. I record them together because a
reader who sees one of them in isolation might treat it as a tuning problem. It is not.

Every number below has a spatial-block bootstrap interval; the one primary statistic of each test was
sealed (sha256 sidecar, committed and pushed) before any held-out number existed. Pre-registrations,
result files and rows are in `validation/`.

## The three tests

| test | statistic | bar | result | verdict |
|---|---|---|---|---|
| B: blank-papyrus null (`ink_detectability_g3v2_*`) | hit fraction at tau 0.044 on blank papyrus windows | FPR well below the letter hit rate | FPR 0.763 (0.744 to 0.782), per crop 0.59 to 0.85 | FAIL |
| C: stroke morphology (`ink_detectability_morph_*`) | footprint fraction under stroke-shaped hit components | AUC letters vs blank, lower bound at least 0.80 | AUC 0.474 (0.422 to 0.528); tau_M = 0, so FPR 1.000 | FAIL |
| Title template control (`PREREG_title.md`, `RESULT_title.md`) | exemplar-bank match, column 3 letters vs intercolumn gaps | lower bound of AUC at least 0.80 and true bank beats a phase-scrambled bank | AUC 0.928 (0.866 to 0.989); scrambled bank 0.975; difference -0.047 (-0.107 to +0.013) | FAIL |

Lane B and lane C are in-sample on the training crops, which makes their failures strong: the map
flags intact papyrus as ink at the threshold that catches letters (B), and the hit components have no
stroke-like shape beyond chance (C). The title control is at template level: a bank with the same power
spectrum as the letter exemplars and no letter shapes separates letters from gaps better than the real
bank. What separates letter windows from gap windows is texture, and texture is what the map carries.

## What this rules out

- Any hit-fraction, morphology or template threshold on dense_native as a letter-versus-blank test.
- Any 0/N "no title here" claim from that map. A screen of the title region with this score would be
  uninterpretable, because the score cannot tell "letters here" from "ink-like texture here".
- Re-tuning the threshold, the window, the bank or the stride. Each pre-registration says one attempt;
  the title control was rerun once only to compute its interval correctly (blocking fixed per the sealed
  pre-registration, scores byte-identical), and the verdict did not move.

## What would be needed instead

A different signal: ink inference on the raw CT with a contrast control built in, or a map whose
blank-papyrus false-positive rate is measured out of sample at the title region's own resolution before
any letter claim. I have not run either; both cost the compute these tests were designed to avoid.
