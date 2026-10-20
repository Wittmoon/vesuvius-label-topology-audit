# Label topology audit: evidence packet

**Finding:** 17% of the public Vesuvius Challenge surface-label crops (152 of
892) contain holes or handles, 571 in all: 314 interior (107 crops, 12%), 257
on a crop face, where the crop truncated the sheet. Of 14 located interior
holes in the 20 worst crops (the 13 where two AI reviewers agreed, plus one
they were unsure of; not the 14 largest), checked by hand in CT by the
submitter, 8 sit on continuous papyrus and should be filled, and 6 are pockets
between two sheets the label merged and should be cut. The existing repair
script, `fix_holes.py`, adds voxels into all 6 of those pockets
(`data/repair_tiles.csv`), which is the wrong direction; whether it fills the
8 was measured for only one of them, where `2d_hole_fill` added nothing
(`closed_k3` added one voxel).

Individual submission. Implementation, experiments and write-up were produced
with AI assistance (Claude) under the submitter's direction; the 14-hole hand
check in CT is the submitter's own.

The immediate deliverable is a prioritised proofreading queue with
human-checked examples where filling would make a merged-sheet label worse.

**Tool:** `vesuvius.label_topology_audit`, a dataset-level topology audit for
3D surface labels: it ranks a folder of crops worst first, locates the small
holes, writes the input `fix_holes.py` expects, and measures whether a repair
removed the holes or just moved them. A second tool on the same branch,
`vesuvius.surface_placement_audit`, measures where a traced mesh sits on the
papyrus sheet in the CT (Part 2).

- Code: [ScrollPrize/villa](https://github.com/ScrollPrize/villa) branch
  [`feat/label-topology-audit`](https://github.com/Wittmoon/villa/tree/feat/label-topology-audit)
  on the fork, also here as [code.patch](code.patch). Pull request:
  [ScrollPrize/villa#2147](https://github.com/ScrollPrize/villa/pull/2147).
- Data: result tables in `data/`, the hand-checked errata list in
  [data/errata.csv](data/errata.csv) (the 6 CUT holes are also filed as
  [ScrollPrize/villa#2144](https://github.com/ScrollPrize/villa/issues/2144)),
  a synthetic example in `figures/`, test and reproduction records in
  `validation/`.
- Progress Prize entry for October 2026.

**Open problem addressed:** the
[2026 open problems](https://scrollprize.org/2026_open_problems) post asks for
"datasets with labels better localized on the papyrus' recto" and for "a high
level of topologic accuracy", and names holes and mergers among the failure
modes that send a traced mesh onto the wrong wrap. This tool measures those
failure modes in the training labels, ranks the crops so a person knows which
to inspect first, and checks whether a repair actually removed them.

## Part 1: label topology audit (main result)

### What it is

A dataset-level QA pass for 3D surface labels. It runs before training, ranks
a folder of label crops worst first, reports candidate locations for small
holes, feeds the existing per-crop repair tool (`scripts/fix_holes.py`) and
checks its output. Compared with what the repo already has:

| | `detect_holes.py` | this audit |
| --- | --- | --- |
| Betti numbers per component | yes | yes (shared helper, `vesuvius/image_proc/topology.py`) |
| hole locations | persistent homology (`cripser`) | closing + Euler screen, no extra dependency |
| crop-face vs interior holes | no | yes |
| cavities, fused sheets, junctions, thickness | no | yes |
| whole-dataset ranking (`ranked.csv`) | no | yes |
| before/after deltas, `--fail-on` for CI | no | yes |
| writes `fix_holes.py` input masks | n/a | yes (`--hole-masks`) |
| zarr / OME-Zarr input, local or URL, windowed and tiled | no | yes (`--roi`, `--tile`, `--threshold`) |

### Results (Kaggle surface labels, 892 crops)

| finding | crops | total |
| --- | --- | --- |
| holes/handles | 152 (17%) | 571 |
| located, interior | 74 | 237 |
| located, on a crop face | 71 | 257 |
| not located (too wide) | 49 | 77 |
| interior (237 located interior + 77 not located, location unknown) | 107 (12%) | 314 |
| cavities | 69 (8%) | 206 |
| junction clusters | 281 (32%) | 651 |
| fused components | 22 (2%) | |

- Holes concentrate in the later crops: 1% of crops 0-99 have one (1 of 98),
  compared with 82% of crops 900+ (14 of 17). None is explained by ignore
  voxels.
- Provisional AI spot check of 29 located holes: 12 judged apparent label
  defects, 0 judged real tears, 17 unclear (mostly at crop faces); 10 clean
  controls were also inspected. Not an expert precision estimate.

#### fix_holes before/after, 10 worst crops

| method | b1 | b2 | voxels added | CT check (20 tiles): on papyrus / false add / no change / unclear |
| --- | --- | --- | --- | --- |
| `2d_hole_fill` | 111 → 49 | 19 → 12 | 3,731 | 5 / 3 / 5 / 7 (one of the 5, tile 2D15 = E14, is a hole the human check calls a pocket to cut) |
| `close` k2 | 111 → 73 | 19 → 12 | 1,997 | 1 / 4 / 8 / 7 |
| `close` k3 | 111 → 67 | 19 → 12 | 4,689 | 1 / 6 / 8 / 5 |

A lower Betti count is not the same as a correct repair: some additions fill
an inter-sheet wedge and join sheets, and some unchanged holes are pockets
between merged sheets, which need separating rather than filling. That
operation is outside the repair methods evaluated here.

#### Errata list: 33 holes in the 20 worst crops (AI-reviewed, 14 human-checked)

`data/errata.csv` lists the up-to-3 largest located interior holes in each of
the 20 top-ranked crops that have one, with crop ID and hole centre (zyx). Two
AI reviewers judged each hole independently from CT slices with the label
overlaid: FILL (the hole sits on continuous papyrus), CUT (a pocket between
two sheets the label merged) or UNCLEAR. They agree on 21 of 33: 7 consensus
FILL (3 crops), 7 consensus CUT (5 crops), 19 disagreement or both UNCLEAR.

The submitter then checked 14 holes in a local slice viewer, scrolling
through the CT in three planes with the overlay on and off, with the AI
verdicts hidden until after each judgment: 13 of the 14 consensus holes
(E24, crop 687, consensus CUT, was skipped by oversight) plus E01, where both
reviewers were unsure. The human agreed with all 13 consensus verdicts (6
CUT, 7 FILL) and judged E01 FILL (`human_verdict` column). The reviewer is not
an expert annotator and the 13 were chosen because the AI reviewers agreed,
so 13 of 13 is not an independent precision estimate. The 19 rows without a
verdict remain unchecked; one of them, E22 (118,530 voxels), is a surface
concavity the locator reports as a hole (`locate_holes` has no upper volume
cap).

The CUT rows matter most: `fix_holes` would fill them with the wrong answer.
The list is a starting point for an annotator, not a correction.

**Automatic cut/fill signal (labels only, no CT): thickness is negative, size
is suggestive.** `validation/errata_hole_geometry.py` measures rim and shell
thickness, local label density and principal-axis extents for each of the 33
holes (`data/errata_hole_geometry.csv`). Rim thickness is 1.0 on 30 of 33
holes: the Kaggle labels are one voxel thin, so a pocket between merged sheets
is two thin sheets joined at their edges, and neither thickness nor density
(CUT 0.17-0.35, FILL 0.22-0.32) separates the classes. Size does, on the
reviewed holes: the 7 consensus CUT holes are 133-5,167 voxels, the 7
consensus FILL holes 14-120, E01 (human FILL) 164; a cut at about 125 voxels
puts 14 of these 15 on the right side. This is an observation on 15 holes
from the top of the ranking, not a validated classifier; 13 of the 18 UNCLEAR
holes are above 125 voxels. The script's nearest-component match recounts
E01, E21 and E28 differently from `errata.csv`; the ranges above use the
errata counts.

#### Audit on model predictions

The same audit on a binarised surface prediction (probability > 0.5) looks at
prediction topology rather than label topology. The model is a local
recto-surface 3D U-Net checkpoint trained on other scrolls, not Scroll 1; the
volumes are two 320³ Scroll 1 CT crops around segment `20230827161847`, with
no labels.

| | crop 1 | crop 2 | Kaggle labels, worst crop |
| --- | --- | --- | --- |
| foreground | 23% | 15% | |
| b1 (holes/handles), big components | 955 | 2,754 | 34 |
| b2 (cavities) | 195 | 779 | 13 |
| fused voxel fraction | 44% | 90% | 22% |
| junction clusters | 176 | 310 | 13 |
| thickness median / p95 (voxels) | 8.4 / 11.8 | 1.0 / 11.0 | 1.8 / 3.0 (median crop) |

Binarised at 0.5, this checkpoint's output on Scroll 1 has 28-81x the worst
label crop's hole count and fuses most sheets. One checkpoint, one threshold,
two crops, a model not trained on this scroll: this shows the audit works as
a prediction check, not a benchmark of the model.

**Do flagged labels disagree more with an independent prediction? Not
detectably with this checkpoint (pre-registered, null).** The same checkpoint
(local, patch 256, epoch 3504; not shipped) was run on 53 Kaggle crops (one centred 256³ tile per crop): 27 the audit
flags with an interior hole, 23 it finds clean, 3 flagged only by a cavity or
fusion (excluded). Dice at 0.5 against the label is 0.226 median on flagged
crops and 0.211 on clean ones; the one-sided Mann-Whitney test fixed in
advance (flagged < clean) gives p = 0.74, the secondary metrics agree, and
foreground fraction does not explain it (Spearman -0.05 over all 53 crops,
-0.10 over the 50 tested). Per-crop rows:
[data/prediction_agreement_flagged_vs_clean.csv](data/prediction_agreement_flagged_vs_clean.csv);
pre-registration, amendments and run notes:
[validation/prediction_agreement_preregistration.md](validation/prediction_agreement_preregistration.md).
This is the low-power case the design named: the checkpoint reaches Dice 0.35
at best on any Scroll 1 crop, so crop-level agreement is set by the model's
transfer failure, not by defects that touch under 1% of label voxels. The null
does not show the flags are useless; it shows no association was detectable in
this experiment, and without the checkpoint the test can only be repeated with
another surface model.
Probability inside the 10 errata holes that fall in the predicted tiles tracks
the rim (ratio 0.8-0.9) for FILL, CUT and UNCLEAR alike
([data/prediction_agreement_hole_local.csv](data/prediction_agreement_hole_local.csv)), so the map is not a
cut/fill oracle either. A model trained on Scroll 1 labels is the test that
could carry a signal.

#### Community prediction volumes (zarr, read in place)

With the zarr input landed, the audit was run on 18 binarised
surface-prediction volumes published by Yupeng Li at
`https://dl.ash2txt.org/community-uploads/yupeng/` (m7, Socratic, HercUNet;
PHerc1447, PHerc0814; thresholds 0.2, 0.3, 0.5, the published `_thX.zarr`
masks). One 768³ window per scroll, deep inside the scroll, split into 27
tiles of 256³, read over HTTP. Full table:
[data/community_predictions_audit.csv](data/community_predictions_audit.csv);
commands: [validation/community_predictions_run.sh](validation/community_predictions_run.sh).

| model | scroll | thr | fg | b1 total | b1 per Mvox fg | b2 total | fused frac | thick median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m7 | PHerc1447 | 0.3 | 15% | 2,686 | 40 | 123 | 0.45 | 3.0 |
| m7 | PHerc0814 | 0.3 | 19% | 5,770 | 66 | 90 | 0.71 | 3.0 |
| Socratic | PHerc1447 | 0.3 | 21% | 5,767 | 61 | 521 | 0.38 | 3.5 |
| Socratic | PHerc0814 | 0.3 | 27% | 13,211 | 110 | 824 | 0.64 | 3.0 |
| HercUNet | PHerc1447 | 0.3 | 29% | 26,207 | 199 | 38,335 | 0.60 | 3.5 |
| HercUNet | PHerc0814 | 0.3 | 39% | 35,882 | 203 | 223,487 | 0.69 | 5.0 |

- Per foreground voxel, m7 has the fewest holes and handles, Socratic
  1.5-2.3x more, HercUNet 3.1-8.7x more, on both scrolls and at every
  threshold.
- Of the three published cuts, 0.3 has the lowest hole density for every
  model: 0.5 raises it 1.13-2.99x, 0.2 raises cavities 5-10x for m7 and
  Socratic. A nine-threshold sweep of the probability volumes
  ([data/threshold_sweep.csv](data/threshold_sweep.csv), 54 rows,
  [validation/threshold_sweep_run.sh](validation/threshold_sweep_run.sh))
  puts the hole-density minimum at 0.3-0.4 for m7 and Socratic on both
  scrolls; cavities have already fallen to a few hundred or fewer there and
  keep falling above it. So the sweep suggests a threshold without a labelled
  reference, as a heuristic, not a validated rule. The sweep cuts the
  probability volumes itself (uint8 cut = ceil(t x 255)), so its rows differ a
  little from the published masks (Socratic on PHerc1447 at 0.2: fused
  fraction 0.43 published, 0.49 sweep). Cuts above 0.5 fragment: at 0.7 hole density is 16-19x
  its minimum for Socratic and 2.6-3.4x for m7.
- HercUNet's output is thicker (median 3.5-5 voxels) and carries tens to
  hundreds of thousands of cavities per window, so it behaves like a volume
  label rather than a thin sheet; its cavities rise with the threshold up to
  0.5, the opposite of the other two, and no cut gives it the hole density of
  m7 or Socratic.
- PHerc0814 has a higher fused fraction than PHerc1447 for every model at
  every threshold.
- Caveats: one window per scroll, not chosen by any label; tile faces count
  as crop faces (1-5% of b1 on the published masks, up to 8% in the sweep); no ground truth, so this ranks prediction
  topology, it does not score accuracy.

#### A scroll with recovered text: two generations of the public PHerc0139 prediction

PHerc0139 is a scroll the Challenge has recovered text from (title and author
evidence, Angelotti et al. 2026, arXiv 2606.29085). Which prediction that
reading used is not stated, so nothing here rates either generation as
readable. The scroll that paper reads in full, PHerc1667, has no
`predictions/surfaces/` folder in the open-data bucket, only a
`predictions/lasagna/` one (listing of 2026-10-20:
`validation/open_data_surface_predictions_listing_2026-10-20.txt`). The bucket
holds three surface predictions for PHerc0139
(`PHerc0139/representations/predictions/surfaces/`); the audit compares the
oldest and the newest, `recto-090` from 2025-07 and `m7-L0-th0.2` from
2026-04, uint8 probabilities on the same grid (the third,
`recto-2um-ps192-L0-th0.5` from 2026-02, was not run). The
audit was run on 40 matched 256³ crops (random, seed 0, where the older volume
has at least 3% foreground, tested on its 1/8-scale level; one crop is 1.8%
at full scale), binarised at > 127, read over HTTPS. Rows:
[data/public_surfaces_pherc0139_generations.csv](data/public_surfaces_pherc0139_generations.csv);
`validation/public_surfaces_pull.py`, `public_surfaces_run.sh`,
`public_surfaces_crops.json` produce them.

| median per crop | recto-090 (2025-07) | m7-L0 (2026-04) | newer is lower in N of 40 |
| --- | --- | --- | --- |
| foreground fraction | 0.32 | 0.19 | 35 |
| thickness median / p95 (voxels) | 4.7 / 7.0 | 3.0 / 3.5 | 36 / 34 |
| b1 (holes/handles), big components | 436 | 232 | 33 |
| b2 (cavities) | 82 | 18 | 35 |
| components (all / big) | 49 / 9 | 95 / 21 | 7 / 1 |
| largest component share of foreground | 0.80 | 0.54 | 36 |
| closed big components | 0 | 3 | 6 |
| fused voxel fraction | 0.03 | 0.37 | 16 |
| junction clusters | 76 | 104 | 9 |

- The newer volume is thinner with fewer holes and cavities on most crops,
  and more fragmented: twice the components, a smaller largest component,
  more closed pieces and more junction clusters. A thinner surface has fewer
  holes partly by construction, so the fragmentation and fusion rows are the
  comparable part.
- As a yardstick: the newest public prediction for a scroll with recovered
  text still carries a median of 232 holes per 256³ crop at this cut, against a maximum of 34 in
  any 320³ Kaggle label crop. The audit separates the two generations on every
  row, which is what it is for; which generation traces better is not decided
  here. One scroll, 40 crops, one threshold, no labelled reference.

### What would help next, and what we are asking the community

1. **Cut or fill, adjudicated.** Six of the 14 hand-checked holes in #2144
   are cuts, judged by one person. A second annotator on those 14 and on the
   19 unreviewed rows of `data/errata.csv` would test the 125-voxel size rule
   above; a crop where `fix_holes.py` joined two sheets would make the case
   directly.
2. **Paired-mesh validation.** #1845 and #1912 each have a pair of meshes for
   the same segment with a measured ink difference. Running the placement
   audit on both members of each pair and checking whether its offset row
   orders them as the ink score does is the cheapest downstream test. The
   2026-10-20 comment on #1912 published 206 mesh pairs (52 held out, 154
   applied; snapshot `validation/issue1912_comment_2026-10-20.md`) with a fine-to-coarse
   pixel map (github.com/slchicoineau-creator/tifxyz-canvas-map); that is the
   natural source.
3. **Sheet switch.** The most asked-for check (#1641, #1621, the Open
   Problems list) and the one neither audit does. A peak index is not a
   winding identity, so this needs a segment with a known switch before it is
   worth building; #1641's planted-winding example has not been run against
   our output. Measured on PHerc0139 for issue #2167 (w034/w036 gap sector,
   [validation/pherc0139_2167_placement.md](validation/pherc0139_2167_placement.md)):
   w033 pushed 115 um off its sheet still reads as placed one time in three at
   9.6 um, so the pre-registered check failed its own instrument gate and the
   gap question stays open.
4. **Catalog sweep.** The placement audit has been run on every public
   Scroll 1 segment, the topology audit on both PHerc0139 generations. Running it on a schedule
   with `aggregate.csv` published would turn single findings into a trend; the
   question is whether maintainers want the rows.

The one feature we would build next, if the first ask gets a second annotator:
a reviewable correction bundle per crop (CT and label review crops,
CUT / FILL / UNCLEAR decisions, reversible deltas, before and after Betti
numbers) so a reviewed repair can be checked and applied, not just ranked.

## Part 2: surface placement audit and ink experiments (secondary)

Controls and side results, not the main deliverable.

### Where the two audits sit in the villa pipeline

Both are modules of villa's `vesuvius` package on the same branch, listed in
the tools table in `vesuvius/README.md`. The tracing branch (trace, preflight,
flatten, render) and the label branch (labels, audit, repair, train) meet at
the ink model:

| step | villa tool | check that runs here |
| --- | --- | --- |
| trace a segment | `vc_grow_seg_from_seed` | |
| gate the surface file | `vesuvius.surface_preflight` (PRs #1463, #1840) | files present, stated scale vs measured step, bbox, CT support |
| measure the trace | **`vesuvius.surface_placement_audit`** | offset to the nearest density peak, its repeatability and variation along the surface; grid spikes, interior grid holes, wrong-frame warnings |
| flatten and render | `vc_flatten`, `vc_render_tifxyz` | |
| gate the labels | **`vesuvius.label_topology_audit`** | holes, cavities, fused sheets, thickness, ranked worst first, hole masks |
| repair | `scripts/fix_holes.py` | topology audit `--after`: did the repair close holes without adding handles |
| train and predict | `vesuvius.train`, `vesuvius.predict` | topology audit on predictions |
| ink model | `ink-detection/` | experiment only: does the render depth sample the sheet |

Preflight fails closed; the placement audit never fails by default and
`--fail-on` turns any metric into a gate (its outside-volume and
empty-profile warnings go to stderr and exit 0). For tifxyz, run
`surface_preflight --volume` first; for obj, which preflight does not read,
the audit's warnings are the only frame check.

Relation to villa changes: preflight (#1463, #1840) and the audit's
empty-profile warning both catch a surface in empty space (both verified on
the #2112 case below); the audit's own ground is a surface with CT under it
that sits off the sheet, and it does not repeat preflight's scale check
(#2151, #2056, #1985). The grid spike check is PR #2067's footprint test run
on any tifxyz input and finds all 23 affected vertices on segment
20231007101619. `n_grid_holes` is motivated by #2128's dropped flattening
triangles, not a demonstrated catch. The outside-volume and empty-profile
warnings answer #2112 and #2137. The half-cell shift of #2150 is not covered.

### What this responds to

Villa issues that asked for, or ran into, what the two audits measure (filed
by others unless marked):

| issue | asked or reported | what the packet gives |
| --- | --- | --- |
| #1640 (closed) | labels sit about 2.3 voxels off the sheet's density maximum | the same quantity on traced meshes, with snap and tangent controls; 255 segments in `data/scroll1_segment_placement.csv`. It does not say why the offset is there |
| #1912 | PHerc0139 on-scan meshes up to 100 um off the inked surface | motivates: offset to the density peak is not offset to the inked surface; that issue's five-window depth sweep is the closer tool |
| #1549 | a mesh row rides about 97 voxels of dark CT with no sheet | the empty-profile warning and `no_peak_frac` |
| #1845 | the coarser published mesh costs 0.04 AUC, nothing says which mesh to pick | motivates; the audit has not been run on that pair |
| #2144 (ours) | 6 of 14 hand-checked holes are pockets to cut, not fill | the errata list; the hole mask carries no cut/fill hint yet |
| #1641, #1621 | sheet-switch detector; whole-winding displacement scores zero | **not covered**: distance to the nearest peak reads a clean jump to the neighbouring sheet as well placed |
| #1675 | cross-cutting, non-sheet surfaces | potentially measurable (high `no_peak_frac`, low tangent agreement), not demonstrated |
| #1522, #1727, #1977 | declared scale does not match the grid on hundreds of segments | preflight's gate; not repeated |
| #1660 | a frame mismatch renders a black strip and exits 0 | the outside-volume and empty-profile warnings |
| #1547 | two surfaces trace the same sheet | not covered |
| #2167 | w035 covers ~258 deg; in the gap w036 sits at w034's radius, "checking against the CT is needed" | pre-registered run of the placement audit on the gap vs outside sectors: instrument check failed (a one-sheet shift reads as placed 1 in 3 at level 2), no answer; `data/pherc0139_2167_placement.csv` |

### Surface placement on the public Scroll 1 segments

`vesuvius.surface_placement_audit` samples a mesh (obj or tifxyz, local or
URL), reads a short CT profile along each stored normal, and reports the
signed offset to the nearest density peak, with a snap-and-remeasure control
(precision of the peak location) and tangent-neighbour controls at 2, 4 and 8
voxels (the scale over which the offset is a property of the surface).

Run on all 255 public Scroll 1 segments that have an obj (20230514182829 is
points only), 20000 samples each against `54keV_7.91um_Scroll1A`; 224 have
1000 or more valid samples. Quantiles across those segments:

| metric | 10th | median | 90th |
| --- | --- | --- | --- |
| offset median (vox) | −1.5 | −0.5 | +1.5 |
| share of points > 2 vox from the sheet peak | 0.32 | 0.48 | 0.58 |
| off-sheet fraction | 0.12 | 0.25 | 0.37 |
| snap remeasure sd (vox) | 0.25 | 0.34 | 0.42 |
| tangent median abs. diff. at 2 / 4 / 8 vox | 0.5 / 0.5 / 0.58 | 0.5 / 0.5 / 1.0 | 0.5 / 0.5 / 1.0 |
| tangent correlation at 2 / 4 / 8 vox | 0.79 / 0.62 / 0.41 | 0.85 / 0.72 / 0.54 | 0.89 / 0.79 / 0.66 |

The median offset is small, but a median of 48% of sampled points per segment
sit more than 2 voxels (16 µm) from the sheet peak (the 0.48 is the median of
per-segment fractions, not a pooled fraction). The snap sd shows the peak
location is repeatable to about 0.3 voxels; the tangent correlation falls from
0.85 at 2 voxels to 0.54 at 8, so the offset varies along the surface on a
scale of a few voxels, within one triangle of a mesh with about 18 voxels
between vertices. Neither control shows that the detected peak is the correct
papyrus surface, and neither identifies the cause; the mesh-resolution reading
was not tested (for instance against a finer mesh). The method assumes
isotropic voxels. Per-segment rows: `data/scroll1_segment_placement.csv`.

What it does not catch: the 23 vertex spikes of villa PR #2067 on segment
20231007101619 (median 1,065 voxels off) sit at hole edges with no computable
normal and are never sampled, so the CT metrics are identical with and without
them (`notes/placement-vertex-spike-negative-result.md`). The JSON now reports
the skipped count (`n_no_normal`), and a grid check with no CT read catches
the class: adjacent grid points are joined when their step is at most 4x the
median, and a small group tied to the surface by a long step is a spike
(`n_grid_spikes`). It flags exactly the PR's 23 vertices and nothing on the
input or fixed grids (`data/placement_pr2067_grid_checks.csv`). Two more
grid-side reports: `n_grid_holes` (interior holes of the grid) and
`outside_volume_frac` with a warning above 0.1. On a real PR #2112 case
(PHerc0139 segment 20260422000000 without its factor-4 downscale) the
quarter-scale mesh stays inside the large volume, in empty space, so the
bounds warning does not fire but the profiles do: no peak at any of 3,000
samples against no-peak 0.45 for the published mesh, so the audit also warns
when fewer than 5% of inside points find a peak
(`notes/placement-outside-volume-pr2112.md`). Grid and obj rows of the same
segment are not directly comparable (no-peak 0.40 vs 0.31,
`data/placement_pr2067_spike_check.csv`).

### Render depth and the ink model's window (negative result)

If the mesh is off the sheet, the render puts the papyrus at the wrong depth,
and the ink model reads a fixed 17-layer window around the render's centre.
The same profile measurement on all 29 `ink_9um` training renders
(`validation/ink_render_depth.py`, `data/ink_render_depth.csv`) shows the
sheet is never above centre and often below it:

| peak minus centre layer | aligned 2.4 µm renders (centre 10) | native 9 µm renders (centre 14) |
| --- | --- | --- |
| 0 | 4 (PHerc0139 w028, w029, w041, w043) | 0 |
| -1 | 11 | 0 |
| -2 | 3 | 5 (all) |
| -3 | 4 (PHerc1667 w018, PHercParis4 w02, w07, w09) | 0 |
| -4 | 2 (PHercParis4 w00, w03) | 0 |

`validation/ink_peak_window.py` shifts the 17-layer window so the measured
peak lands at in-window layer 8 and runs the released `infer`; scored with
`validation/ink_score.py` on the dataset's validation-mask pixels (released
hybrid_3d2d seed42 step-075000) on the three `ink_9um` segments that ship a
mask. All scores: [data/ink_validation_scores.csv](data/ink_validation_scores.csv)
and, for the five-window sweeps and checkpoint comparison,
[data/ink_supervision_and_validation_scores_overnight.csv](data/ink_supervision_and_validation_scores_overnight.csv);
checkpoint hashes in `validation/ink_checkpoints.sha256`.

| segment (labels) | profile peak | default window (layers 2-18) AUC / AP | peak-chosen window AUC / AP | best window in a 5-window sweep |
| --- | --- | --- | --- | --- |
| `pherc0139-w016` (the public PHerc0139 segment w029 at 2.4 µm, pooled to 9 µm) | 9 | 0.775 / 0.622 | 0.823 / 0.676 (layers 1-17) | 0.828 / 0.689 (layers 0-16) |
| `pherc0814-46527` | 9 | 0.874 / 0.839 | 0.817 / 0.785 (layers 1-17) | 0.896 / 0.872 (layers 4-20) |
| `pherc1667-w029` | 9 | 0.870 / 0.735 | 0.881 / 0.753 (layers 1-17) | 0.887 / 0.756 (layers 0-16) |

These are within-segment scores, not unseen-scroll results: villa
[PR #2126](https://github.com/ScrollPrize/villa/pull/2126) reports that 233 of
282 validation crops share image voxels with training crops. With that caveat,
the window moves the score by 0.05 to 0.10 AUC on w016 and 0814-46527 (0.017
on 1667-w029), but the one-read peak rule raises AUC on two segments and lowers
it on the third, where the best window lies in the opposite direction; there
are no intervals. The best window also depends on the checkpoint (seed43 and
seed42-050000 rows of the overnight CSV), so a fixed rule would need
re-deriving per checkpoint. Other variables move the score more: seed43 scores
0.936 on w016 and 0.931 on 1667-w029, mirror TTA 0.891 on w016. Per-column
re-centring at inference is also negative (w016 AUC 0.775 to 0.498;
`notes/ink-recentring-negative-result.md`). Whether the per-column offset
predicts where the model scores worse was tested under a pre-registration and
is uninformative at the mask sizes available (Notes). Run records:
`validation/ink_*_peak_window.json`.

## Code

- Repo `ScrollPrize/villa`, branch `feat/label-topology-audit`, based on
  `3d56d06ec`. Release revision `1dc04b189` (code.patch =
  `git format-patch 3d56d06ec..1dc04b189`, 23 commits).
- Files: `vesuvius/src/vesuvius/image_proc/run/label_topology_audit.py`,
  `.../image_proc/run/surface_placement_audit.py`,
  `.../image_proc/topology.py`, `.../scripts/detect_holes.py` (CPU path uses
  the shared helper), `vesuvius/tests/test_label_topology_audit.py`,
  `vesuvius/tests/test_surface_placement_audit.py`,
  `vesuvius/docs/label-topology-audit.md`, `vesuvius/docs/surface-placement-audit.md`.
- Tests: at `1dc04b189` the two test files hold 41 + 31 test functions, 80
  cases, all passing ([record](validation/pytest_1dc04b189.junit.xml)).
  Earlier records: 31 audit tests on a fresh export of upstream with the patch
  applied ([record](validation/upstream-source-tests.json)), 35 at `a620aca9e`
  ([record](validation/branch-tests-a620aca9e.json)).
- Reruns: the 892-crop audit was rerun at `605e9d222` (every metric matches)
  and at `9ae381299` after two review fixes (a fill the sheet never touches is
  not a repair; ignore contact tested at 26-connectivity): every total is
  unchanged and one crop, `sample_00205`, moves from closed to open. Later
  commits touch the placement tool, input handling and docs, not the topology
  arithmetic. Three real-data cases: [validation/real-data-review.json](validation/real-data-review.json).
- Environment: macOS arm64, Python 3.14.8, numpy 2.4.6, scipy 1.18.0,
  scikit-image 0.26.0, connected-components-3d 4.0.0, tifffile 2026.6.1. CPU
  only.

## Reproduce

```bash
# data: the public surface labels (CC BY-NC 4.0), 892 crops
#   hf://buckets/scrollprize/datasets/surfaces/kaggle/{labels,images}/
# e.g. https://huggingface.co/buckets/scrollprize/datasets/resolve/surfaces/kaggle/labels/sample_00001.tif

vesuvius.label_topology_audit --batch DATA_DIR --out audit_out          # all crops, ~44 min with 4 shards
vesuvius.label_topology_audit --batch FLAGGED --plot --hole-masks --out flag_out

# repair + check (see the docs' Workflow section for the folder layout fix_holes expects)
python src/vesuvius/scripts/fix_holes.py --in-dir fix_in --ignore-value 2 --method 2d_hole_fill
vesuvius.label_topology_audit --batch BEFORE --after AFTER --out fix_out

# synthetic example, no scroll data: reproduces figures/out exactly
python figures/make_synthetic.py
vesuvius.label_topology_audit --label figures/synthetic_label.tif --image figures/synthetic_image.tif --plot --hole-masks --out figures/out
```

Install: a fresh venv (Python 3.14) with `pip install -e vesuvius` from the
patched villa checkout plus `tifffile zarr scipy scikit-image
connected-components-3d opencv-python-headless numba imagecodecs matplotlib
tqdm` runs both CLIs and passes all 80 tests (2026-10-20). The `models` extra
also covers these but pulls in a C++ build (`volume-cartographer`).

The scripts in `validation/` take their paths from environment
variables (`W`, `PY`, `R`; `INK_ROOT`, `INK_DATA`, `VESUVIUS_PYTHON`,
`VESUVIUS_SRC` for the ink scripts), documented at the top of each script.

Inputs this packet does not ship:

- Every ink result needs the `ink_9um` labels, the surface volumes and the
  released `hybrid_3d2d` checkpoints (hashes in `validation/ink_checkpoints.sha256`).
  The AUC/AP tables are recorded, not recomputed: the prediction tifs are not
  included, and predictions are not bitwise reproducible across machines.
- The placement tables need the public Scroll 1 meshes and volume over HTTP
  (`validation/placement_run_all.sh`, `validation/scroll1_segments.txt`); the
  per-segment CSV is the recorded output.
- The render-depth table reads 29 surface volumes over HTTP plus two local
  native 9 µm copies; only its output CSV is included.
- The provisional 29-hole AI spot check has only its tile list
  (`data/spot_check_tiles.csv`), not per-hole verdicts; the tiles are withheld
  (CC BY-NC).
- The two-crop prediction audit and the agreement test ran on a local
  checkpoint that is not released; their outputs are
  `data/prediction_audit_scroll1_crops.csv` and
  `data/prediction_agreement_flagged_vs_clean.csv`.

## Files

- `data/kaggle_audit_all.csv`: one row per crop, all metrics, from the run at
  `9ae381299`.
- `data/kaggle_ranked.csv`: 353 crops with any finding, worst first, with a reason.
- `data/fix_holes_before_after.csv`: per crop and method.
- `data/repair_tiles.csv`, `data/repair_review.csv`: tile index and per-tile
  judgments.
- `data/errata.csv`: 33 holes with crop ID, centre, both AI verdicts,
  consensus, human verdict (14 rows) and a suggested action.
- `data/errata_hole_geometry.csv`: per errata hole, rim and shell thickness,
  density and principal-axis extents (`validation/errata_hole_geometry.py`).
- `data/prediction_agreement_hole_local.csv`: the 10 errata holes inside the
  predicted tiles, mean probability in the hole, on its rim and 20-40 voxels
  away.
- `data/prediction_agreement_flagged_vs_clean.csv`: one row per crop (53) of
  the flagged-vs-clean test: group, `b1_interior`, foreground fraction, Dice
  and tolerant recall/precision at 0.3, 0.5 and on the skeleton.
- `data/prediction_audit_scroll1_crops.csv`: the two aggregate rows of the
  two-crop prediction audit.
- `data/community_predictions_audit.csv`: one row per community prediction
  volume and threshold (18 rows), 27 tiles each.
- `data/threshold_sweep.csv`: one row per model, scroll and threshold (54);
  `validation/threshold_sweep_run.sh`, `validation/summarise_threshold_sweep.py`.
- `data/public_surfaces_pherc0139_generations.csv`: one row per crop and
  generation (80) of the PHerc0139 comparison.
- `data/scroll1_segment_placement.csv`: one row per public Scroll 1 segment
  (255), 20000 samples each; `validation/placement_run_all.sh`,
  `validation/summarise_placement.py`.
- `data/placement_pr2067_grid_checks.csv`, `data/placement_pr2067_spike_check.csv`:
  grid checks and placement metrics on the three PR #2067 grids.
- `data/placement_pr2112_outside_volume.csv`: placement audit rows for the two
  PR #2112 meshes; `data/placement_pr2112_preflight_normalized.json`,
  `..._published.json`: villa `surface_preflight --volume` reports on the same
  two meshes (FAIL on CT support, PASS).
- `data/ink_render_depth.csv`, `data/ink_validation_scores.csv` (31 rows),
  `data/ink_supervision_and_validation_scores_overnight.csv` (144 rows): the
  ink tables above, from `validation/ink_score_table.sh`.
- `data/spot_check_tiles.csv`: the 39 tiles of the provisional AI spot check.
- `validation/prediction_agreement_preregistration.md`: the agreement test's
  design, amendments and results as written before and during the run.
- `data/pherc0139_2167_placement.csv`, `validation/pherc0139_2167_placement.md`,
  `validation/pherc0139_2167_placement_preregistration.md`, `validation/pherc0139_2167/`:
  the issue #2167 gap-sector run (13 sector inputs, bootstrap CIs, positive
  controls, blind sheets, frozen code and ids).
- `validation/open_data_surface_predictions_listing_2026-10-20.txt`,
  `validation/issue1912_comment_2026-10-20.md`: dated snapshots of the S3
  listing and the #1912 comment cited above.
- `validation/negative_results/`: raw JSON of the label-snapping and
  trace-refinement experiments.
- `figures/out/synthetic_label.holes.png`, `figures/out/synthetic_label.png`:
  the synthetic example (two sheets with a gap through both, a hole at a crop
  face, two bridges making one handle; the audit reports b1 = 5: 3 interior,
  2 on the face).

Not included: crop images, label crops, and tiles rendered from them. The
source data is CC BY-NC 4.0; this packet links it rather than redistributing
it.

## Notes: what did not work

Side experiments recorded in `notes/` as negative results so they are not
repeated blind. None is part of the prize claim; their scripts are not
released, their raw outputs are in `validation/negative_results/`.

- [label-snapping](notes/label-snapping-negative-result.md): snapping labels
  to the CT edge works on synthetic perturbations only with a direction prior
  from the clean labels, and does not transfer to a real traced segment.
- [trace-refinement](notes/trace-refinement-negative-result.md):
  optimal-surface refinement on raw CT moves 2-20% of a trace's cells onto a
  neighbouring sheet; a learned cost helps on one crop and not the next.
- [ink-placement-offset](notes/ink-placement-offset-negative-result.md): a
  pre-registered test of whether the per-column off-sheet offset predicts
  where the ink model scores worse is uninformative (the validation masks are
  2.5-6 tiles of 256 px); an exploratory 64-px rerun finds no signal.
  Pre-registration and rows in `validation/course4/`.
- [ink-recentring](notes/ink-recentring-negative-result.md): per-column
  re-centring at inference drops w016 AUC from 0.775 to 0.498.
- [placement-outside-volume-pr2112](notes/placement-outside-volume-pr2112.md)
  and [placement-vertex-spike](notes/placement-vertex-spike-negative-result.md):
  the two placement cases described in Part 2.

## Limitations

- **Judging:** the spot check and the repair check were judged by an AI
  reviewer at thumbnail resolution, not by an expert annotator; the 14-hole
  check is the submitter's.
- **Hole location:** holes wider than a 3-step closing (about 6 voxels) are
  counted but not located; `locate_holes` has no upper volume cap.
- **Thresholds:** tiny 100, thick 7, piece 500 and junction ratio 0.3 are
  heuristics, not tuned on reviewed data.
- **Cut/fill size rule:** the ~125-voxel split was read off 15 reviewed holes
  and has not been tested on holes nobody reviewed.
- **Isotropic grids:** both audits assume isotropic voxels.
- **Grid points without a normal:** on tifxyz input, points at hole edges and
  the grid border are not sampled (`n_no_normal`). The grid spike check does
  not cover a vertex wrong by less than 4x the grid step; `n_grid_holes` has
  no baseline, since the 255 Scroll 1 segments were audited as obj.
- **Sheet switch:** neither audit detects a trace that jumps cleanly to the
  neighbouring sheet; on PHerc0139 at 9.6 um a 115 um shift reads as placed
  one time in three (the #2167 run).
- **Inspection only:** the audit flags findings and measures changes; it does
  not separate merged sheets.

## License

The code patch carries the villa repository's license. Everything else in
this packet (tables, figures, scripts, text) is MIT, see [LICENSE](LICENSE).
The numbers in `data/` were computed from the CC BY-NC 4.0 surface labels;
the labels themselves are not redistributed; the per-crop metrics and hole
coordinates derived from them are.
