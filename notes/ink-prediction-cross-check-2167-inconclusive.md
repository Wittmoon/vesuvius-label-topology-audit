# Ink predictions as a sheet-identity check for the #2167 gap: inconclusive (2026-10-22)

Question: the Challenge publishes ink predictions for w033-w037 on PHerc0139
(recipe 20260417190342, full-resolution tif, 1 px = 1 level-0 voxel). If two
meshes lie on the same papyrus in the disputed 55-95 degree sector, their ink
should correlate there once both are mapped to (angle, z). Can that settle
which gap meshes share a sheet, without a hand trace?

Method, fixed before any gap-sector number was read
(`validation/negative_results/ink_xcheck_2167/PREREG.md`): ink averaged into
the tifxyz grid cells, each cell mapped to angle about the umbilicus and z with
the `unwrap_gap.py` conventions, rastered at 0.25 degrees by 100 um; per pair
the peak Pearson r over shifts of +-1 degree and +-200 um; regions gap 55-95,
rest, and the two control windows 130-170 and 160-200; z bands low, mid, high.
Nulls: different-winding pairs outside the gap, a shuffled-z and rolled-z
null, and an even/odd grid-row split of one mesh as a ceiling. Decision rule:
"shares" if the gap peak beats both the shuffled null 95th percentile and the
best different-winding control pair.

Result (`verdict_table.txt`, `pairs.csv`):

- Different windings outside the gap sit at r 0.00-0.16; the shuffled null
  95th percentile is 0.05-0.12.
- w034-w035 reads 0.20-0.47 everywhere, gap and controls alike, so it behaves
  like a same or overlapping layer and was dropped from the null after the
  fact (stated, not pre-registered).
- In the gap, w034-w036 (0.22), w036-w037 (0.20) and w035-w036 (0.18) rise
  above their own outside-gap values (0.11-0.14) and pass the rule;
  w034-w037 (0.10) does not.
- w033-w036 also passes the rule in the gap (0.17 vs 0.04 outside), although
  w033 is the readable mesh and surely a different winding from w036. So the
  rule admits a pair it should reject, and the rise is not specific to "same
  sheet".
- No gap pair reaches the w034-w035 level.

Conclusion: inconclusive. The check neither shows w034, w036 and w037 on one
sheet nor separates them. The pre-registered rule fails its own
discrimination test (w033-w036), so its passes carry no weight. Likely causes:
one ink model across all meshes, text lines periodic in z so different
windings correlate once shifted, w035 covering about half the angles, and the
even/odd ceiling (0.98) comparing adjacent interpolated cells rather than
independent papyrus. Do not re-run this as a replacement for the hand trace;
a version with a per-mesh independent ink read and a same-sheet ceiling from a
control pair known to overlap would be needed first.

Files shipped: pre-registration, summary, per-pair rows, coverage and
ceiling tables. Pair images and the script are not shipped (the script
imports scratch helpers).
