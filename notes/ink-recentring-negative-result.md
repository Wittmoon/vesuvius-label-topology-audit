# Negative result: per-column re-centring of ink renders at inference

Idea: the sheet sits at a different depth in each column of a rendered surface
volume, so shift every column by an integer so its density peak lands on the
centre layer, then run the released ink model unchanged.

Done 2026-10-19 (`scratch/ink/recenter.py` in the tools repo: gaussian-smoothed
z profile per column, 15-px median-filtered depth map, shift clipped to ±8).

| segment | pixels scored | default render AUC / AP | re-centred AUC / AP |
| --- | --- | --- | --- |
| w035 (training) | supervision | 0.999 / 0.998 | 0.677 / — |
| w029 public (= `pherc0139-w016` labels) | validation | 0.775 / 0.622 | 0.498 / 0.25 |

Why it fails: the model was trained on renders whose sheet depth varies
smoothly across a patch; per-column integer shifts break that continuity and
the 3D stem reads the seams as structure. A whole-segment window shift (the
peak-chosen window in the README) keeps the render intact and does help.
Training with per-patch centring is untested and is a different experiment.
