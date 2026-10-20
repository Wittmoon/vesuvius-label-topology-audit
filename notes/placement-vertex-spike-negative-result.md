# Placement audit vs villa PR #2067 vertex spikes: not detected (2026-10-20)

Question: does the surface placement audit catch a known tracing defect that
someone else found independently? [villa PR #2067](https://github.com/ScrollPrize/villa/pull/2067)
shows that resampling a tifxyz grid in `repair_tifxyz_spacing.py` on main keeps
vertices interpolated from a missing neighbour, which land hundreds to
thousands of voxels off the surface.

Data: the published tifxyz of segment 20231007101619
(`PHercParis4/segments/20231007101619/mesh/20231007101619-on-20260310170716-45.532um.tifxyz`
on the open-data bucket, 137 x 285 grid, 4,593 missing vertices) and the
7.91 um Scroll 1 volume.

Reproduction of the PR's defect, `repair_tifxyz_spacing.py --target-spacing 40`
(factor 0.4957): on main 8,113 output vertices kept as valid, 23 of them
interpolated from a missing input, median 1,065 and max 2,110 voxels from their
valid inputs; with the PR's fix 7,877 kept, 0 interpolated (the PR reports 7,876).

Placement audit (seed 0, every valid point sampled) on the input grid, the main
output and the fixed output: `data/placement_pr2067_spike_check.csv`. The
metrics of the main and fixed outputs are the same within noise (no-peak 0.405
vs 0.409, abs offset > 2 voxels 0.554 vs 0.555), and 0 of the 23 spikes were
sampled. All 23 sit at hole edges, where the grid has no computable normal, and
the sampler skipped every such point without reporting it (388 of 8,113 on
main, 381 of 7,877 on the fix).

Result: negative. The placement audit measures CT placement at points it can
sample; it does not see vertex-level geometry defects at hole edges, and a
geometry check such as the PR's own footprint test is the right tool for
those. Branch `fa2b1046d` adds `n_no_normal` to the JSON and a warning so the
skip is visible; it does not make the spikes detectable.

Side observation: the same segment audited through its tifxyz grid (20-voxel
spacing) reads worse than through its obj in `data/scroll1_segment_placement.csv`
(no-peak 0.40 vs 0.31, contrast median 74 vs 132, tangent correlation at 4
voxels 0.32 vs 0.71). Grid normals at that spacing are noisier than mesh vertex
normals, so tifxyz and obj rows should not be compared directly.
