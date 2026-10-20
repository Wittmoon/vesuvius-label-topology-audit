# PHerc0139 issue #2167: the placement audit run on the w034/w036 gap sector (2026-10-20)

Pre-registration: [pherc0139_2167_placement_preregistration.md](pherc0139_2167_placement_preregistration.md)
(packet commit 08b8ce2, pushed before the run read a sample). Code, ids, logs and the blind sheets:
`validation/pherc0139_2167/`. Results table: `data/pherc0139_2167_placement.csv`.

## Result: failed instrument check, no primary read

The pre-registered kill rule fired. w033 moved +12 level-2 voxels (115 um) along its own normal is
"unplaced" on 63% of its outside-sector samples, and +6 voxels on 63%; the rule required 80%. At this
resolution the sheet pitch outside the gap is about 14 level-2 voxels (Chase's 561 um over four
windings), so a surface pushed one window-length off its sheet lands within reach of the next sheet
and reads as placed about a third of the time. That is the README's "not covered" row (a clean jump
to the neighbouring sheet reads as well placed) measured directly on this scroll. By the rule fixed in
advance, D is not interpreted.

| input | unplaced | 95% block CI | valid peaks |
| --- | --- | --- | --- |
| w033 OUT | 0.401 | 0.384-0.420 | 4,697 / 5,000 |
| w033 OUT +6 | 0.634 | 0.613-0.656 | 4,214 |
| w033 OUT +12 | 0.633 | 0.612-0.655 | 3,709 |
| w033 GAP | 0.428 | 0.407-0.448 | 4,619 |
| w034 OUT / GAP | 0.373 / 0.418 | 0.355-0.391 / 0.394-0.439 | 4,776 / 4,627 |
| w036 OUT / GAP | 0.362 / 0.429 | 0.344-0.381 / 0.409-0.448 | 4,747 / 4,695 |
| w037 OUT / GAP | 0.342 / 0.409 | 0.322-0.362 / 0.385-0.434 | 4,749 / 4,730 |
| w034 GAP, doubly traced end | 0.459 | 0.403-0.521 (29 blocks) | 4,509 |

Recorded, not interpreted: D(w034) = +0.018 (CI -0.017 to +0.050, below the 0.05 minimum effect);
D(w036) = +0.040 (0.005 to 0.078); D(w037) = +0.040 (0.001 to 0.080). Every winding, w033 included,
is 3-7 points more often unplaced in the gap than outside, which is why the difference against w033
is small. The sign holds in only 2 of 4 contrast quartiles for w034 and w036. Contrast is the live
confound and nothing here separates it from placement.

## Secondaries

- **Joint measure (pre-registered form):** of 4,695 valid w036 gap samples, 1,459 have a valid w034
  sample within 3 grid steps; 0.8% of those pairs have snapped peaks within 2 voxels in 3D. Outside the
  gap only 28 pairs exist, as expected when the windings are a sheet apart. The 3D form is dominated by
  the lateral separation of the two sample points, so it does not answer the same-band question.
- **Post hoc, not pre-registered (`joint_posthoc.py`):** the same pairs with the peak separation
  projected on w036's normal. Gap: median 4.2 voxels (40 um) between the two snapped peaks, 34% within
  2 voxels, 49% within 4. Outside: median 8.7 voxels, 11% within 2 (28 pairs). The paired points
  themselves are a median 4.2 voxels apart along the normal in the gap. The sheet's measured width at
  this level is 5.5 voxels (FWHM), so one band and two adjacent bands are not separable at level 2.
- **Blinded CT look** (`blind_ids.json`, `blind_calls.json`, `blind_sheet1.png`, `blind_sheet2.png`):
  20 frozen samples rendered at level 0 in the normal-tangent plane, called by the submitter with the
  sector and offset hidden. Gap: 6 sheet, 3 between sheets, 1 air. Outside: 4 sheet, 3 sheet edge,
  1 between, 2 air. No gap-specific pattern at n = 20. Three gap samples with |offset| of 3-6 voxels
  were called "sheet" by eye, consistent with the window reaching a neighbouring band.

## What this changes

Nothing in the audit. Issue #2167's question (which of w034/w036 left its sheet in the gap) is not
answered by nearest-peak distance at 9.6 um; it needs winding identity, which is ask #3 in the README.
The run adds one number to that ask: on this scroll a one-sheet jump is invisible to the endpoint
about one time in three at level 2. A level-0 rerun of the same inputs (window 32 vox = 77 um, sheet
pitch 140 um outside, 63 um in the gap) would test whether the finer scale restores the control; it
costs about 30 GB of chunk reads per winding and was not run.

## Run record

13 inputs x 5,000 samples, seed 2167, level 2 of `20260102150214-2.399um-0.2m-78keV-masked.zarr`,
`--half 8 --step 0.5 --sigma 1 --min-contrast 8 --min-prominence 0.15`, 6.5 GB chunk cache,
`full_run.log`, `full_aggregate.csv`. Inputs derived by `make_inputs.py` (sha256 in the
pre-registration) from the five published tifxyz grids and the umbilicus (`SHA256SUMS`); the derived
grids (310 MB) are not shipped and rebuild from the script. Sector counts: `inputs_report.jsonl`.
