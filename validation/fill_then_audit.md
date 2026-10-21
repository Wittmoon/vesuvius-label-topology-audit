# Fill-then-audit: repairing all 152 flagged crops, then auditing the repair

Run 2026-10-20 22:29–23:37, one laptop CPU, four shards. Every Kaggle crop the audit
flagged (`b1_total_big > 0`, 152 of 892) was repaired three ways with the Challenge's own
`scripts/fix_holes.py`, using the hole masks the audit writes (`--hole-masks`), and the
repaired labels were audited again with `--after`. Class 2 (ignore) was never filled.
Per-crop numbers: `fill_then_audit_crops.csv`. Per-hole numbers for the 33 human-checked
holes: `fill_then_audit_errata.csv`.

## What the repair does to the audit's own numbers

| method | holes before | holes after | crops left hole-free | crops made worse | new sheet fusions | voxels added |
|---|---|---|---|---|---|---|
| 2D hole fill | 571 | 408 | 27 | 0 | 0 | 9,974 |
| closing, kernel 2 | 571 | 345 | 27 | 3 | 0 | 6,682 |
| closing, kernel 3 | 571 | 409 | 22 | 5 | 0 | 10,259 |

Holes = `b1_total_big` summed over the 152 crops. No method removed a voxel, merged two
components, or raised the fusion, junction, or bridge counts. "Made worse" = a crop whose
hole count rose (closing can open a new loop while closing another).

## Where the added voxels land: the 33 human-checked holes

Fraction of each hole's voxels the method filled, grouped by the human verdict from
`errata_cutfill.md` (19 CUT = a real gap in the papyrus, 11 FILL = a labelling miss,
3 UNCLEAR).

| method | CUT holes, mean filled | CUT holes >50% filled | FILL holes, mean filled | FILL holes >50% filled |
|---|---|---|---|---|
| 2D hole fill | 0.48 | 8 of 19 | 0.48 | 5 of 11 |
| closing, kernel 2 | 0.14 | 0 of 19 | 0.58 | 6 of 11 |
| closing, kernel 3 | 0.24 | 4 of 19 | 0.60 | 6 of 11 |

2D hole fill cannot tell the two apart: it fills real gaps as readily as labelling misses,
and eight CUT holes (E07, E10, E14, E15, E17, E18, E24, E25) are filled almost completely.
Closing with a kernel of 2 fills the labelling misses at about the same rate while leaving
every real gap mostly open. That is the expected behaviour of a small closing (it bridges
gaps up to a few voxels wide and leaves wider ones), and the human verdicts happen to
separate on width. It is a post-hoc reading of 30 holes from the top of one ranking, not
a pre-registered test.

## What this does and does not show

- The audit's fusion, junction, and bridge metrics did not move under any repair, yet the
  human review found 19 of 33 ranked holes to be real gaps that a fill would weld. So the
  topology audit's `--after` check as it stands does **not** catch the welds a human sees;
  it only confirms the repair added nothing that reads as a sheet merger at this scale.
  The `--after` numbers must not be read as "the repair was safe".
- The per-hole fill fractions are a voxel count inside the audit's located hole component,
  not a judgement of whether the hole closed topologically.
- Three crops (`sample_00683`, `sample_00409`, `sample_00559`) gain holes
  under closing; they are worth a look before any closing is applied blind.

Reproduce: `scratch/label_quality/kaggle_full/fix/overnight/run.sh` and `crosstab.py`
(villa worktree at 1dc04b189; hole masks from the same audit run, not from `audit_9ae3`).
