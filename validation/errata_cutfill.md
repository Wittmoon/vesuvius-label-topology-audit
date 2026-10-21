# Result: automatic FILL/CUT call on the errata holes (2026-10-20, night 9)

Pre-registration: `errata_cutfill_preregistration.md` (commit da7287a). Rule calls committed before the
human looked: `errata_cutfill_holdout_calls.csv` (dc09b8d). Human blind calls: `errata_cutfill_human_calls.csv`.
Script: `errata_cutfill_ct_density.py`.

## Outcome: no rule meets the bar. Ledger row, no `--call` column in ranked.csv.

The bar was 15 of 19 (79%) agreement with the blind human and at least as good as the size rule.
The human called 3 of the 19 UNCLEAR (E03, E16, E22), leaving 16 decided holes: 13 CUT, 3 FILL.

| rule (frozen) | holdout right | Wilson 95% | dev (14) | all decided (30) |
|---|---|---|---|---|
| extent_n > 4.2 -> CUT | 11/16 (0.69) | 0.44-0.86 | 13/14 | 24/30 (0.63-0.90) |
| size >= 125 -> CUT | 12/16 (0.75) | 0.51-0.90 | 13/14 | 25/30 (0.66-0.93) |
| CT density s (UNCLEAR band 0.35-0.65) | 5/16 (0.31), 2 abstain | 0.14-0.56 | 6/14 | 11/30 (0.22-0.54) |
| "always CUT" (not a rule under test) | 13/16 (0.81) | 0.57-0.93 | 6/14 | 19/30 |

Confusion on the 16 decided holdout holes (rows = human, columns = rule):

- extent: CUT -> CUT 9, CUT -> FILL 4 (E17, E10, E25, E18); FILL -> FILL 2, FILL -> CUT 1 (E12).
- size: CUT -> CUT 11, CUT -> FILL 2 (E25, E18); FILL -> FILL 1, FILL -> CUT 2 (E12, E02).
- CT: CUT -> CUT 2 (E24, E25), CUT -> FILL 8, CUT -> UNCLEAR 2 (E21, E23); FILL -> FILL 3.

The two label-only rules did well on the development set because that set was consensus-selected and the
sizes were already known when the thresholds were chosen. On fresh holes they fall to 69-75%, inside the
interval of "call everything CUT", which the human's base rate (13 of 16) makes a strong trivial rule.
Neither beats it. The CT density score is wrong more often than right: pockets between merged sheets are
dense in the CT precisely because the sheets touch there, so the score reads them as papyrus (s 0.69-1.94
on 8 human-CUT holes).

## What the human calls say about the errata list

Over all 33 holes the human verdict is now 19 CUT, 11 FILL, 3 UNCLEAR. On the holes ranked highest in the
worst crops, a blind `fix_holes` fill would weld two sheets more often than it would repair one. The list
remains a queue for an annotator, not an automatic correction.

## Limitations

- The AI verdicts for the 19 holes had been in `data/errata.csv` since 10-18 and the reviewer may have seen
  them; 18 of 19 were UNCLEAR, so the leak carries little information.
- One reviewer, not an expert annotator, who reported the task as hard; the three UNCLEAR include E22
  (118,530 voxels, a surface concavity the locator reports as a hole) and E16 (1,224 voxels).
- 16 decided holes: the intervals are wide and the rules are not shown to be worse than chance, only not
  shown to be good enough to act on.
- The holdout is one hole-rich tail of one dataset (the 20 worst-ranked Kaggle crops).
