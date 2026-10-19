# Negative result: per-column re-centring of ink renders at inference

Idea: the sheet sits at a different depth in each column of a rendered surface
volume, so shift every column by an integer so its density peak lands on the
centre layer, then run the released ink model unchanged.

Done 2026-10-19 (`scratch/ink/recenter.py` in the tools repo: gaussian-smoothed
z profile per column, 15-px median-filtered depth map, shift clipped to ±8).

| segment | pixels scored | default render AUC / AP | re-centred AUC / AP | result file |
| --- | --- | --- | --- | --- |
| w035 (training) | supervision | 0.999 / 0.997 | 0.677 / - | none in the packet (default row: `data/ink_supervision_and_validation_scores_overnight.csv`) |
| w029 public (= `pherc0139-w016` labels) | validation | 0.775 / 0.622 | 0.498 / 0.252 | `data/ink_validation_scores.csv` (`w016,recentered`) |

Single runs, no interval. The w035 re-centred score has no result file here.

Hypothesis, not tested: the model was trained on renders whose sheet depth varies
smoothly across a patch, and per-column integer shifts break that continuity, so
the 3D stem may read the seams as structure. No experiment isolates this (for
instance a smoothed depth map, or re-centring with seams hidden). A
whole-segment window shift (the peak-chosen window in the README) keeps the
render intact; its effect on validation AUC is mixed (see README). Training
with per-patch centring is untested and is a different experiment.
