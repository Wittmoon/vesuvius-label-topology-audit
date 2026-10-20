# Pre-registration: automatic FILL/CUT call on the errata holes (2026-10-20)

Script: scratch/label_quality/cutfill/ct_density.py, sha256 prefix ba0cd0aaeb8be920 (copied to this folder as errata_cutfill_ct_density.py). Written before any of the 19 holdout holes was scored.

## What was already done (development set, not confirmatory)
The 14 holes with a human verdict in data/errata.csv (8 FILL, 6 CUT, consensus-selected) were scored first. Results, ct_density_dev.csv:
- CT density score s = (CT_hole - CT_air) / (CT_papyrus - CT_air): 6 of 14 right (CUT holes E04, E05, E06, E08 read as papyrus, s 0.85-1.20; FILL holes E28, E29 read as air). The pockets between two sheets are dense in the CT because the sheets touch there, which is why they are pockets. NEGATIVE on the development set.
- Synthetic controls, 5 per crop over the 20 crops: holes punched into intact label read FILL 29/40 (72%); balls placed in unlabelled space 6-8 voxels from label read CUT 17/40 (42%). The second fails because unlabelled space in these crops is often unlabelled papyrus, not air. Both are below the 90% bar fixed in the plan, so the CT score is declared uninformative and is carried to the holdout only as a pre-declared negative.
- Hole extent along the local sheet normal (extent_n, labels only): CUT 3.7-11.6, FILL 1.8-4.0; threshold 4.2 puts 13 of 14 right (misses E14 at 3.7; gets E01 right, which the size rule misses).
- Size rule (errata hole_voxels >= 125 -> CUT): 13 of 14 (misses E01).

## Frozen for the holdout
- Holdout = the 19 holes in data/errata.csv with no human verdict: E02 E03 E09 E10 E11 E12 E13 E15 E16 E17 E18 E19 E20 E21 E22 E23 E24 E25 E30 (18 consensus UNCLEAR + E24 consensus CUT). Development holes are excluded.
- Three calls per hole, committed in errata_cutfill_holdout_calls.csv before the human looks: extent_n > 4.2 -> CUT else FILL; size >= 125 -> CUT else FILL; CT s with the 0.35-0.65 UNCLEAR band.
- Blind protocol: the human sees, in a random order under codes B01-B19, three orthogonal CT slices through the hole centre with the label outlined and nothing else (no id, no size, no call). They record FILL, CUT or UNCLEAR per code to errata_cutfill_human_calls.csv. Only then is the code-to-id key opened. Limitation: the AI verdicts for these holes have been in errata.csv since 10-18 and the human may have seen them; they were UNCLEAR for 18 of 19.
- Scoring: human UNCLEAR holes are dropped from the denominator and counted. Report a confusion matrix per rule, the Wilson 95% interval, and the two label-only rules on the identical holes.
- Success for a PR change: a rule agrees with the human on at least 15 of 19 (or the same fraction of the non-UNCLEAR holes) AND does at least as well as the size rule. Then ranked.csv gains a --call column from that rule, with a test. Otherwise a ledger row and no PR change.
- Nothing about the thresholds changes after this commit.
