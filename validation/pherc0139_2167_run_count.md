# PHerc0139 issue #2167: per-angle material-run count between w033 and w037

Date: 2026-10-22. Follows `pherc0139_2167_unwraps.md` (by-eye single slices at 12 places) and is the
"decisive version" that note said it was not: at every angle, how many separate papyrus layers (material
runs) lie between w033 and w037 in the CT, and how many of the five meshes land in one run, in no run, or
leave a run empty. Pre-registered in `pherc0139_2167/run_count_preregistration.md` before any gap window was
read, with two amendments made after the control-sector instrument check and before any gap window was read.

## Instrument

Level-1 CT (4.8 um/voxel) polar slice about the umbilicus, as in the unwrap note. Per angle column (one
level-1 voxel step): a radial profile from 60 um inside the innermost mesh crossing to 60 um outside the
outermost, Gaussian-smoothed at 10 um, thresholded by Otsu over the nonzero pixels of the window. A material
run is a contiguous above-threshold stretch of at least 20 um with gaps under 10 um bridged. Each mesh's
crossing at that angle is the linear interpolation of its main-piece crossings (end pieces excluded, see the
unwrap note for the end-piece rule), present only if a crossing lies within 1.5 deg. A crossing is in a run
if within 10 um of it, else "air" (Amendment 1: the registered 1 px / 4.8 um tolerance flagged 70-90% of
control crossings; the measured control crossing-to-run distance has 90th percentile 16 um at C1 and 39 um at
C2).

Per crossing (column x mesh), `w033`..`w037` in the crossings CSVs: `ok`; `air`; `same:<pair>@<width>` (two
meshes in one run no wider than 1.5x the control median run width, 60 um, so 90 um); `amb:<pair>@<width>`
(two meshes in one run wider than that, which may hold pressed sheets and is never counted as one sheet);
`absent`. Per column: `n_runs` between the innermost and outermost present crossings, `n_empty` runs strictly
between two present meshes holding none. Per window the summary CSVs carry `same`, `amb`, `air` (fractions of
crossings), `empty_per_gap` (empty runs per mesh-to-mesh interval) and `w034_flag` (fraction of w034 crossings
not `ok`). Script `pherc0139_2167/run_count.py` (modes `instrument`, `places`, `sweep`; imports the unwrap
script; reads the same cached level-1 chunks).

## Instrument check (controls C1 and C2, before any gap window)

The registered check was a fixed radial shift of w034 by one winding (+110 um) and half of one (+55 um).
It does not pass: the local pitch here is 100-150 um and the split plies between layers give the shifted
trace a stray run to land in. Amendment 2 replaced it with the signature the finding looks for, two meshes
in one run: w034 copied onto w035's interpolated radius, 5 um inside it. Pass rule, 90% of clean w034
crossings flagged. `data/pherc0139_2167_run_count_instrument.csv`:

| Window | clean w034 crossings | flagged at +55 um | at +110 um | copied onto w035 |
| --- | --- | --- | --- | --- |
| C1 (z 13,000, 130-170 deg) | 690 | 0.22 | 0.48 | **0.97** |
| C2 (z 22,000, 160-200 deg) | 521 | 0.73 | 0.79 | **0.96** |

So the instrument sees a mesh that sits on another mesh's layer. It does not reliably see a mesh that is one
fixed step off its own layer, and no result below claims that.

## The 14 places (`data/pherc0139_2167_run_count_places.csv`, +-20 deg, U1/U2 55-95 deg)

Fractions of crossings. `run groups` = the two sets of meshes most often found together in one run, with the
number of `same`/`amb` crossings naming each (from the crossings CSV; a group of three or four is one run
holding that many meshes).

| Place | z | angle | same | amb | air | empty per gap | run groups (crossings) | by-eye read (unwrap note) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 control | 13,000 | 150 | 0.002 | 0.071 | 0.16 | 0.36 | w036+w037 (120), w035+w036 (92) | five layers, one trace each |
| C2 control | 22,000 | 180 | 0.045 | 0.128 | 0.27 | 0.24 | w036+w037 (422), w035+w036 (150) | one trace each |
| E1 | 14,856 | 35 | 0.157 | 0.471 | 0.14 | 0.05 | w033+w034+w036 (618), w033+w034+w036+w037 (536) | w034 and w036 on one layer |
| E2 | 17,995 | 360 | 0.100 | 0.127 | 0.32 | 0.29 | w036+w037 (334), w033+w034 (204) | layers well separated |
| E3 | 21,500 | 267 | 0.193 | 0.340 | 0.23 | 0.03 | w036+w037 (360), w033+w034+w035 (276) | w034 on w035's layer |
| E4 | 10,437 | 355 | 0.058 | 0.469 | 0.16 | 0.11 | w033+w034+w036 (750), w034+w036 (540) | w034 and w036 in one dense band |
| E5 | 13,741 | 4 | 0.049 | 0.284 | 0.14 | 0.17 | w034+w036+w037 (312), w034+w036 (294) | w034 and w036 share a layer |
| E6 | 14,109 | 19 | 0.145 | 0.372 | 0.17 | 0.11 | w033+w034+w036 (630), w034+w036 (570) | w034 and w036 share a layer |
| G1 | 11,000 | 50 | 0.183 | 0.276 | 0.29 | 0.02 | w033+w034+w036 (402), w034+w037 (378) | w034 and w037 on one layer |
| G2 | 19,500 | 15 | 0.026 | 0.033 | 0.35 | 0.32 | w036+w037 (104), w034+w036 (82) | w034 changes layer inside the slice |
| G3 | 23,000 | 60 | 0.098 | 0.100 | 0.43 | 0.16 | w033+w034 (230), w034+w037 (228) | w034 changes layer; w037 crosses air |
| G4 | 26,800 | 35 | 0.085 | 0.040 | 0.39 | 0.32 | w034+w037 (232), w034+w036 (82) | w034 and w037 on one layer |
| U1 | 14,856 | 55-95 | 0.070 | 0.199 | 0.14 | 0.10 | w033+w034+w036 (279), w034+w036 (210) | w034 and w036 on one band to 80 deg |
| U2 | 19,500 | 55-95 | 0.161 | 0.172 | 0.29 | 0.14 | w034+w036+w037 (540), w036+w037 (340) | w034, w036, w037 in one band to 75 deg |

Reading. Two meshes in one run (`same` + `amb`) is 0.07 at C1 and 0.17 at C2; at the gap places it is 0.06
(G2) to 0.63 (E1), eight of the twelve above 0.25. In the controls the groups are mostly w036+w037 and
w035+w036, the pressed pairs the unwrap note describes, in `amb` (wide) runs; w034+w035 (58 and 94 crossings)
and a few three-mesh groups also occur there. In the gap the
groups contain w034 with w036 (E1, E4, E5, E6, G1, U1, U2), w034 with w035 (E3), w034 with w037 (G1, G3,
G4), and at many E places w033 as well, i.e. three or four meshes in one run. That matches the by-eye read
where it named a pair (w034+w036 at E1, E4, E5, E6, U1; w034+w035 at E3; w034+w037 at G1, G3, G4) and adds
that w033 is often in the same run as w034 at the lower heights. G2, where the by-eye read saw w034 move
between layers inside the slice, shows the lowest sharing of the E and G places (its second group, w034+w036, does not occur in the
controls) and `air` 0.35 (controls 0.16 and 0.27); G3 and
G4 show `air` 0.43 and 0.39. E2, which the by-eye read called well separated, is the lowest-sharing E place
and its top group is the w036/w037 pressed pair also seen in the controls.

What did not hold up: the registered expectation was also "more empty layers in the gap" (a layer between
w033 and the band carrying no mesh). `empty_per_gap` is lower in the gap (0.02-0.32) than in the controls
(0.36, 0.24). Split plies give every window runs with no mesh in them, so this count does not separate an
unlabelled winding from a ply, and the "empty layer" part of the by-eye reading is not supported by this
instrument. Only the sharing part is.

## z sweep (`data/pherc0139_2167_run_count_sweep.csv`)

Nineteen heights, z 9,000 to 27,000 in steps of 1,000, three fixed sectors: gap 5-71 deg, control A 130-170
deg, control B 160-200 deg (the two control sectors of the placement note). Same instrument, same cut.

| z | gap same | gap amb | gap air | ctl A same | ctl A amb | ctl A air | ctl B same | ctl B amb | ctl B air |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9,000 | 0.19 | 0.43 | 0.16 | 0.01 | 0.19 | 0.15 | 0.00 | 0.08 | 0.30 |
| 10,000 | 0.24 | 0.41 | 0.17 | 0.03 | 0.31 | 0.13 | 0.02 | 0.13 | 0.22 |
| 11,000 | 0.17 | 0.35 | 0.21 | 0.01 | 0.17 | 0.16 | 0.02 | 0.21 | 0.21 |
| 12,000 | 0.14 | 0.31 | 0.32 | 0.00 | 0.13 | 0.13 | 0.00 | 0.17 | 0.17 |
| 13,000 | 0.03 | 0.24 | 0.25 | 0.00 | 0.07 | 0.16 | 0.00 | 0.07 | 0.16 |
| 14,000 | 0.19 | 0.31 | 0.16 | 0.01 | 0.11 | 0.24 | 0.01 | 0.07 | 0.23 |
| 15,000 | 0.19 | 0.45 | 0.14 | 0.01 | 0.04 | 0.23 | 0.04 | 0.13 | 0.24 |
| 16,000 | 0.00 | 0.10 | 0.28 | 0.01 | 0.05 | 0.27 | 0.00 | 0.05 | 0.23 |
| 17,000 | 0.02 | 0.12 | 0.27 | 0.03 | 0.10 | 0.20 | 0.01 | 0.09 | 0.21 |
| 18,000 | 0.04 | 0.03 | 0.23 | 0.01 | 0.14 | 0.27 | 0.01 | 0.07 | 0.28 |
| 19,000 | 0.08 | 0.32 | 0.18 | 0.02 | 0.14 | 0.24 | 0.01 | 0.06 | 0.25 |
| 20,000 | 0.06 | 0.21 | 0.30 | 0.00 | 0.04 | 0.32 | 0.01 | 0.08 | 0.28 |
| 21,000 | 0.11 | 0.34 | 0.29 | 0.05 | 0.10 | 0.32 | 0.01 | 0.08 | 0.36 |
| 22,000 | 0.09 | 0.29 | 0.23 | 0.03 | 0.07 | 0.44 | 0.04 | 0.13 | 0.27 |
| 23,000 | 0.10 | 0.10 | 0.48 | 0.03 | 0.24 | 0.25 | 0.01 | 0.13 | 0.28 |
| 24,000 | 0.22 | 0.18 | 0.39 | 0.11 | 0.11 | 0.29 | 0.05 | 0.14 | 0.32 |
| 25,000 | 0.16 | 0.05 | 0.41 | 0.02 | 0.05 | 0.33 | 0.04 | 0.12 | 0.17 |
| 26,000 | 0.06 | 0.14 | 0.34 | 0.03 | 0.04 | 0.26 | 0.04 | 0.03 | 0.33 |
| 27,000 | 0.12 | 0.19 | 0.29 | 0.04 | 0.17 | 0.23 | 0.01 | 0.08 | 0.26 |

Medians over the 19 heights: gap `same` 0.11, `amb` 0.25, `air` 0.27, `empty_per_gap` 0.15; control A
0.02 / 0.11 / 0.25 / 0.26; control B 0.01 / 0.08 / 0.25 / 0.26. `air` is the same inside and outside the
gap at the median (it exceeds both controls at 12,000 and at 23,000-25,000), so what differs in the gap over
most heights is meshes sharing a run, not meshes off the papyrus. The
sharing is not uniform in z: from 16,000 to 18,000 the gap sector reads like a control sector (`same` 0.00
to 0.04, `amb` 0.03 to 0.12), which agrees with the by-eye read of E2 (z 17,995, well separated) and with
the narrower w034-w036 sharing in the unwraps there; it is strongest at 9,000-15,000 and again at 19,000-
27,000, with `air` rising past 23,000 where G3 and G4 showed w034 crossing between layers.

## What this is and is not

- It is a per-angle count at every height in the gap, against the same count in two sectors where the meshes
  are known to sit one per layer, with an instrument that was shown (0.97 / 0.96) to flag the signature it is
  asked about. It says: in the gap sector, over most of its height, two of the five Kaggle-era meshes lie on
  one papyrus layer more often than outside it (sweep medians: `same` 0.11 against 0.02 and 0.01, `same`
  plus `amb` 0.37 against 0.14 and 0.09, so about 3-4x combined and 5-11x on the narrow-run class), and the mesh involved is w034, with w036 at E1, E4,
  E5, E6 and both unwrap heights and with w037 at G1, G3, G4, often with w033 in the same run.
- A run is not a winding. A single run can hold several pressed sheets (the `amb` class exists for that, and
  the w036/w037 pressed pair at C2 shows a control doing it). So the numbers above are a lower bound on
  layers and say nothing about how many windings are missing from the label set, only that two labels share
  one.
- The instrument is blind to a mesh that sits one layer off on its own (the +110 um check), so a winding
  that is simply mis-numbered but alone on its layer is not counted here either way.
- Level 1 (4.8 um), Otsu per window, one slice per height, a 10 um tolerance chosen on the controls: all
  fixed before the gap was read, none tuned on it. The controls are the baseline, not an absolute scale.
- The "empty layer" part of the by-eye reading is not supported by this count (see above).
- Still not done: tracking one layer continuously from a control sector into the gap (the reviewers' Viterbi
  / banded-DP suggestion); that would turn "share a layer" into "which winding each mesh is on".
