# Label topology audit: evidence packet

**Finding:** 17% of the public Vesuvius Challenge surface-label crops (152 of
892) contain holes or handles, 571 in all. Of the 14 largest interior holes in
the 20 worst crops, checked by hand in CT, 8 sit on continuous papyrus and
should be filled, and 6 are pockets between two sheets the label merged and
should be cut. The existing repair script, `fix_holes.py`, would fill all 14.

**Tool:** `vesuvius.label_topology_audit`, a dataset-level topology audit for
3D surface labels: it ranks a folder of crops worst first, locates the small
holes, writes the input `fix_holes.py` expects, and measures whether a repair
removed the holes or just moved them.

- Code: [ScrollPrize/villa](https://github.com/ScrollPrize/villa) branch
  [`feat/label-topology-audit`](https://github.com/Wittmoon/villa/tree/feat/label-topology-audit)
  on the fork, also here as [code.patch](code.patch). Pull request:
  [ScrollPrize/villa#2147](https://github.com/ScrollPrize/villa/pull/2147).
- Data: result tables in `data/`, the hand-checked errata list in
  [data/errata.csv](data/errata.csv) (the 6 CUT holes are also filed as
  [ScrollPrize/villa#2144](https://github.com/ScrollPrize/villa/issues/2144)), a synthetic example in `figures/`, test
  and reproduction records in `validation/`.
- Progress Prize entry for October 2026.

**Open problem addressed:** label quality for surface prediction. The
[2026 open problems](https://scrollprize.org/2026_open_problems) post asks for
"datasets with labels better localized on the papyrus' recto" and for "a high
level of topologic accuracy". It names holes and mergers among the failure
modes that send a traced mesh onto the wrong wrap. This tool measures those
failure modes in the training labels, ranks the crops so a person knows which
to inspect first, and checks whether a repair actually removed them.

## What it is

`vesuvius.label_topology_audit` is a dataset-level QA pass for 3D surface labels.
It runs before training, ranks a folder of label crops worst first, and reports
candidate locations for small holes. It feeds the existing per-crop repair tool (`scripts/fix_holes.py`)
and checks its output.

Compared with what the repo already has:

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

## Code

- Repo `ScrollPrize/villa`, branch `feat/label-topology-audit`, based on `3d56d06ec`.
- Commits: `6e4a88154`, `941cd5c89`, `392a29117`, `b8bb45319`, `ace26f2fc`, `605e9d222`,
  `a620aca9e` (zarr input: `--roi`, `--tile`, `--threshold`, `--level`; local path or URL).
- Files: `vesuvius/src/vesuvius/image_proc/run/label_topology_audit.py`,
  `vesuvius/src/vesuvius/image_proc/topology.py`, `vesuvius/src/vesuvius/scripts/detect_holes.py`
  (CPU path now uses the shared helper), `vesuvius/tests/test_label_topology_audit.py`
  (35 tests), `vesuvius/docs/label-topology-audit.md`.
- Environment for the numbers below: macOS arm64, Python 3.14.8, numpy 2.4.6,
  scipy 1.18.0, scikit-image 0.26.0, connected-components-3d 4.0.0,
  tifffile 2026.6.1, matplotlib 3.11.0. CPU only.

Code review added input and pairing checks, a bounded thickness proxy at crop
faces, support for singleton axes and clearer ranking text. All 31 audit tests
passed on the branch and on a fresh export of current upstream with the patch
applied ([test record](validation/upstream-source-tests.json)); with the zarr
input commit the branch has 35 tests, all passing
([record](validation/branch-tests-a620aca9e.json)). The full
892-crop audit was rerun at `605e9d222`: every metric matches the earlier run,
thickness included. The labels are 2-3 voxel sheets, so the crop-face
correction does not change them. Three real-data cases are also recorded in
[validation/real-data-review.json](validation/real-data-review.json).

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
```

`figures/make_synthetic.py` builds the synthetic example below; no scroll data
is needed.

## Results (Kaggle surface labels, 892 crops)

| finding | crops | total |
| --- | --- | --- |
| holes/handles | 152 (17%) | 571 |
| located, interior | 74 | 237 |
| located, on a crop face | 71 | 257 |
| not located (too wide) | 49 | 77 |
| interior (located interior + not located) | 107 (12%) | 314 |
| cavities | 69 (8%) | 206 |
| junction clusters | 281 (32%) | 651 |
| fused components | 22 (2%) | |

- Holes concentrate in the later crops: 1% of crops 0-99 have one, compared with
  82% of crops 900+.
- None are explained by ignore voxels.
- Provisional AI spot check of 29 located holes: 12 judged apparent label defects,
  0 judged real tears, 17 unclear (mostly at crop faces); 10 clean controls were
  also inspected. These judgments are not an expert precision estimate. Interior
  holes rank first to prioritize inspection.

### fix_holes before/after, 10 worst crops

| method | b1 | b2 | voxels added | CT check (20 tiles): on papyrus / false add / no change / unclear |
| --- | --- | --- | --- | --- |
| `2d_hole_fill` | 111 → 49 | 19 → 12 | 3,731 | 5 / 3 / 5 / 7 |
| `close` k2 | 111 → 73 | 19 → 12 | 1,997 | 1 / 4 / 8 / 7 |
| `close` k3 | 111 → 67 | 19 → 12 | 4,689 | 1 / 6 / 8 / 5 |

- A lower Betti count is not the same as a correct repair. Provisional AI
  inspection suggests some additions fill an inter-sheet wedge and join sheets.
- Some unchanged holes appear to be pockets between merged sheets. If confirmed,
  these would require separating the sheets rather than filling the pocket;
  that operation is outside the repair methods evaluated here.

### Errata list: 33 holes in the 20 worst crops (AI-reviewed, 14 human-checked)

`data/errata.csv` lists the up-to-3 largest located interior holes in each of
the 20 top-ranked crops that have one, with crop ID and hole centre (zyx). Two
AI reviewers judged each hole independently from CT slices with the label
overlaid. The verdicts were FILL (the hole sits on continuous papyrus),
CUT (a pocket between two sheets the label merged) or UNCLEAR.

| | count |
| --- | --- |
| reviewers agree | 21 / 33 |
| consensus FILL | 7 (3 crops) |
| consensus CUT | 7 (5 crops) |
| disagreement or both UNCLEAR | 19 |

A human then checked 14 holes in a local slice viewer, scrolling through the CT
in three planes with the overlay on and off. The viewer hid the AI verdicts by
default, and the reviewer judged each hole before seeing them. The check covered 13 of the 14
consensus holes plus E01. The human agreed with all 13 consensus verdicts:
6 CUT, 7 FILL. They judged E01, where both AI reviewers were unsure, to be FILL.
The `human_verdict` column records this. The reviewer is the submitter, not an
expert annotator. The 19 rows without a verdict remain unchecked.

The CUT rows matter most. These holes are pockets between sheets the label
merged, so `fix_holes` would fill them with the wrong answer. The list is a
starting point for an annotator, not a correction.

### Audit on model predictions

The same audit, run on a binarised surface prediction (probability > 0.5),
looks at prediction topology rather than label topology. The model is a local
recto-surface 3D U-Net checkpoint trained on other scrolls, not Scroll 1. The
volumes are two 320³ Scroll 1 CT crops around segment `20230827161847`. No
labels exist for these crops.

| | crop 1 | crop 2 | Kaggle labels, worst crop |
| --- | --- | --- | --- |
| foreground | 23% | 15% | |
| b1 (holes/handles), big components | 955 | 2,754 | 34 |
| b2 (cavities) | 195 | 779 | 13 |
| fused voxel fraction | 44% | 90% | 22% |
| junction clusters | 176 | 310 | 13 |
| thickness median / p95 (voxels) | 8.4 / 11.8 | 1.0 / 11.0 | 1.8 / 3.0 (median crop) |

- Binarised at 0.5, this checkpoint's output on Scroll 1 has 30-80x the worst
  label crop's hole count and fuses most sheets. Thresholding a prediction
  like this and tracing it would hit the failure modes the open-problems post names.
- Caveats: one checkpoint, one threshold, two crops (mean probability 0.28 and
  0.29), and the model was not trained on this scroll. This shows the audit works as a prediction check; it is not a
  benchmark of the model.

### Community prediction volumes (zarr, read in place)

With the zarr input landed, the same audit was run on nine binarised
surface-prediction volumes published by Yupeng Li at
`https://dl.ash2txt.org/community-uploads/yupeng/` (three models: m7, Socratic,
HercUNet; two scrolls: PHerc1447, PHerc0814; thresholds 0.2, 0.3, 0.5, using
the published `_thX.zarr` masks). One 768³ window per scroll, deep inside the
scroll (PHerc1447 `12288:13056,3840:4608,3584:4352`; PHerc0814
`9344:10112,2688:3456,2688:3456`), split into 27 tiles of 256³, read over
HTTP without downloading or converting the volumes. Full table:
[data/community_predictions_audit.csv](data/community_predictions_audit.csv);
the exact command list is
[validation/community_predictions_run.sh](validation/community_predictions_run.sh).

| model | scroll | thr | fg | b1 total | b1 per Mvox fg | b2 total | fused frac | thick median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m7 | PHerc1447 | 0.3 | 15% | 2,686 | 40 | 123 | 0.45 | 3.0 |
| m7 | PHerc0814 | 0.3 | 19% | 5,770 | 66 | 90 | 0.71 | 3.0 |
| Socratic | PHerc1447 | 0.3 | 21% | 5,767 | 61 | 521 | 0.38 | 3.5 |
| Socratic | PHerc0814 | 0.3 | 27% | 13,211 | 110 | 824 | 0.64 | 3.0 |
| HercUNet | PHerc1447 | 0.3 | 29% | 26,207 | 199 | 38,335 | 0.60 | 3.5 |
| HercUNet | PHerc0814 | 0.3 | 39% | 35,882 | 203 | 223,487 | 0.69 | 5.0 |

- Per foreground voxel, m7 has the fewest holes and handles, Socratic 1.5-2x
  more, HercUNet 3-5x more, on both scrolls and at every threshold.
- Threshold matters in the same way for every model: 0.5 fragments the sheets
  (b1 per Mvox rises 1.4-3x over 0.3, components per tile rise) while 0.2 adds
  cavities (b2 rises 3-10x over 0.3). Of the three, 0.3 has the lowest hole
  density for m7 and Socratic.
- HercUNet's output is thicker (median 3.5-5 voxels) and carries tens to
  hundreds of thousands of cavities per window, so it behaves like a volume
  label rather than a thin sheet; the numbers are not comparable to the other
  two as a surface model, and the table reports them as measured.
- PHerc0814 is harder for every model: more fused voxels and more holes than
  PHerc1447 at the same threshold.
- Caveats: one window per scroll, chosen deep in the volume and not by any
  label; tile faces count as crop faces (b1 face is 1-4% of b1); no ground
  truth exists for these windows, so this ranks prediction topology, it does
  not score accuracy. The m7 and Socratic groups publish only pyramid level 0.

#### Threshold sweep on the probability volumes

The same windows cut at nine thresholds (0.1 to 0.9, uint8 cut `ceil(t*255)`)
from the published probability volumes (`m7_PHerc1447`, `soc_PHerc0814`, ...),
every cut from one read with `--threshold 26,51,...,230`. Full table:
[data/threshold_sweep.csv](data/threshold_sweep.csv) (54 rows: model x
scroll x threshold); commands in
[validation/threshold_sweep_run.sh](validation/threshold_sweep_run.sh).

| model | scroll | lowest b1 per Mvox fg at | b1 per Mvox at 0.1 / best / 0.7 | b2 at 0.2 / 0.4 / 0.6 |
| --- | --- | --- | --- | --- |
| m7 | PHerc1447 | 0.4 | 69 / 39 / 100 | 1,261 / 14 / 2 |
| m7 | PHerc0814 | 0.3 | 73 / 66 / 222 | 466 / 18 / 0 |
| Socratic | PHerc1447 | 0.4 | 97 / 56 / 1,041 | 3,652 / 102 / 9 |
| Socratic | PHerc0814 | 0.3 | 130 / 110 / 1,761 | 5,108 / 139 / 10 |
| HercUNet | PHerc1447 | 0.3 | 298 / 199 / 474 | 33,197 / 78,969 / 112,552 |
| HercUNet | PHerc0814 | 0.3 | 267 / 203 / 1,051 | 167,541 / 323,748 / 469,453 |

- For m7 and Socratic the hole density has a single minimum at 0.3-0.4 and
  cavities fall by one to two orders of magnitude between 0.2 and 0.4, then
  reach zero by 0.7. Cuts above 0.5 fragment the sheets: hole density rises
  5-30x by 0.7 for Socratic, 2-3x for m7.
- The hole minimum and the cavity collapse sit on the same cut, so the sweep
  picks a threshold without a labelled reference: 0.3 to 0.4 for both models,
  on both scrolls.
- HercUNet's cavity count rises with the threshold up to 0.5-0.6, the opposite
  of the other two. Its probability volume is thick (median thickness 3.5-5 at
  0.3), and a higher cut hollows the thick sheets instead of separating them.
  No cut in the sweep makes it behave like a surface model.
- Caveats as above: one window per scroll, no ground truth, a cut's topology
  ranks it against other cuts of the same model only.

## Files

- `data/kaggle_audit_all.csv`: one row per crop, all metrics, from one run at `605e9d222`.
- `data/kaggle_ranked.csv`: 353 crops with any finding, worst first, with a reason.
- `data/fix_holes_before_after.csv`: per crop and method.
- `data/repair_tiles.csv`, `data/repair_review.csv`: tile index and per-tile
  judgments.
- `data/errata.csv`: 33 holes with crop ID, centre, both AI verdicts,
  consensus, human verdict (14 rows) and a suggested action.
- `data/threshold_sweep.csv`: one row per model, scroll and threshold (54) of
  the sweep on the probability volumes; `validation/threshold_sweep_run.sh` and
  `validation/summarise_threshold_sweep.py` produce it
- `data/community_predictions_audit.csv`: one row per community prediction
  volume and threshold (18 rows), 27 tiles each.
- `figures/out/synthetic_label.holes.png`, `figures/out/synthetic_label.png`:
  the synthetic example. It has two sheets with a gap through both, a hole at
  a crop face, and two bridges that make one handle. The audit reports
  b1 = 5: 3 interior (2 located, 1 unlocated, the handle) and 2 on the face.

Not included: crop images, label crops, and tiles rendered from them.
The source data is licensed CC BY-NC 4.0; this packet links it rather than
redistributing it. The tile
sheets used for the spot checks are kept locally for the same reason.

## Notes: what did not work

Two side experiments on label and trace refinement are recorded in `notes/`
as negative results, so they are not repeated blind. Neither is part of the
prize claim.

- [notes/label-snapping-negative-result.md](notes/label-snapping-negative-result.md):
  snapping labels to the CT edge works on synthetic perturbations of the
  Kaggle crops only with a direction prior taken from the clean labels, and
  does not transfer to a real traced segment.
- [notes/trace-refinement-negative-result.md](notes/trace-refinement-negative-result.md):
  optimal-surface refinement on raw CT moves 2-20% of a trace's cells onto a
  neighbouring sheet; a learned cost helps on one crop and not on the next.
  What survives is an audit of where overlapping traces disagree.

## Limitations

- **Judging:** the spot check and the repair check were judged by an AI
  reviewer at thumbnail resolution, not by an expert annotator. The counts
  are indicative.
- **Hole location:** holes wider than a 3-step closing (about 6 voxels) are
  counted but not located.
- **Thresholds:** tiny 100, thick 7, piece 500 and junction ratio 0.3 are
  heuristics, not tuned on reviewed data.
- **Inspection only:** the audit flags topology findings and measures changes. It does not repair
  merged sheets.

## License

The code patch carries the villa repository's license. Everything else in this
packet (tables, figures, scripts, text) is MIT, see [LICENSE](LICENSE). The
numbers in `data/` were computed from the CC BY-NC 4.0 surface labels; the
labels themselves are not redistributed.
