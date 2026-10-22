# The Challenge's surface prediction as a one-run-per-winding target: not usable (2026-10-22)

Question: the open-data browser publishes a volume-level surface prediction for
PHerc0139 scan 20260102150214
(`representations/predictions/surfaces/20260102150214-surface-20260203205514-surface-recto-2um-ps192-L0-th0.5.zarr`,
uint8 0/255, 8 levels). Could it stand in for the hand trace the layer tracker
needs, by giving one predicted-sheet run per winding in each polar column?

Method: the `unwrap_gap.py` geometry from `validation/pherc0139_2167/` (same
umbilicus, 14 places E1-E6, G1-G4, C1, C2, U1, U2, same polar grid) applied to
level 1 of the prediction (4.8 um per voxel, values binarised at 128). Per
column: count the runs of predicted sheet inside the band spanned by the
w033-w037 crossings plus 4 voxels either side, and measure each mesh crossing's
distance to the nearest run centre within 10 voxels. Raw rows in
`validation/negative_results/predsurf/runs.csv` (one per place and column),
summary in `summary.txt`. The script is not released; it imports the shipped
`unwrap_gap.py` and a scratch helper.

Result (summary.txt):

- Gap places (E, G) have a median of 3 runs per column where 5 meshes cross;
  exactly 5 runs in 4% of 13,321 columns. The controls C1/C2 have a median of 5
  and exactly 5 in 47% of 3,843 columns. So the prediction merges neighbouring
  sheets where the meshes are pressed, which is exactly where a target is
  needed.
- Mesh crossing to nearest run centre, pooled: median 11.5 um, p90 35 um, 44%
  within 2 voxels. Per mesh: w034 best (median 7.2 um, 60% within 2 voxels),
  w036 and w037 worst (32% and 36%); w035 has no run within 10 voxels in 73% of
  its columns. The ridge-peak baseline from the run-count check is worse
  (median 15.3 um), so the prediction does sit closer to the meshes than raw CT
  ridges, but not at the one-run-per-sheet resolution a tracker needs.

Conclusion: negative as a tracker target. The volume can serve as a soft
prior (where sheet is likely) but never as the identity signal that says which
winding a column position belongs to. The hand trace stays the unblock for the
tracker. Not re-proposed.

Also checked on the same browser page: the "lasagna" level-2 volume is a
normals field (cos, gradient magnitude, nx, ny), not winding numbers, and the
two level-1 rows labelled lasagna are fibre predictions (presence, nx, ny).
Neither gives winding identity either.
