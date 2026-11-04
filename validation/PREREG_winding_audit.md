# PREREG: relative-winding annotation audit, PHerc. Paris. 4, Challenge relative_windings.json vs the spiral-fit native mesh

Sealed 2026-11-04 (sha256 sidecar PREREG_winding_audit.md.sha256; code and input hashes in PREREG_winding_audit_code.sha256). After sealing nothing here changes; deviations go in RESULT_winding_audit.md.
This is an audit, not a reading. Its deliverable is a list of annotation chains whose winding steps disagree with the fitted mesh, with an interval on the agreement rate. "No disagreement found" and "control failed, stopped" are both acceptable outcomes.

## 0. Prior knowledge in hand (disclosure)
- Evaluator: spiral-fitting/eval_relative_windings.py on villa branch feat/winding-eval (PR #2448, draft), commit a274161e009bc4a6d622416c80e614bbef1dfeaa. It was built and tested on PHerc. 0139 only (scratch/winding_eval_20261103/RESULT.md: positive control exact_step_share 1.000, negative control 0.907 [0.873, 0.940]). It has never been run on any Paris 4 data.
- Truth meshes: one tifxyz patch per winding, cut from the Challenge spiral-fit native mesh for PHerc. Paris. 4 (scan 20260411134726, 2.4 um level 2 = 9.6 um frame, grid 956 x 56913, step 20 vox) by split_windings.py using windings.tif. 126 windings, ids 10..135, 43,204,693 valid vertices in all, 32,844 to 658,955 per winding.
- Two caveats on those meshes, both known before sealing and both stated here so they cannot be discovered later as an excuse:
  1. windings.tif is, by the mesh's own meta.json (winding_id_map_info), a "conservative reconstruction from source winding_bounds; original per-pixel label map was unavailable", complete: False. A vertex carries a winding id only where exactly one winding's bounding box covers it; 3,821,913 ambiguous (-2) and 7,382,222 invalid (-1) vertices were dropped. Annotation points that fall only on dropped vertices will be unlinked and are counted, not scored.
  2. The spiral fit was trained on the files being audited: FIT_NOTES lists abs_winding.json and relative_windings.json among the fit inputs (loss weights 6 and 4). Agreement is therefore expected and is not evidence that the annotations are right. Disagreement is the informative outcome: it marks chains the fit could not honour, i.e. an annotation error, a fit error, or a mesh region the label reconstruction dropped. This test cannot tell those apart; it can only list them.
- Annotations (9.6 um frame, same as the mesh): relative_windings.json, 300 collections, 2173 points, z 6528 to 17253, wind_a 1 to 52, 1873 consecutive pairs; collections with fewer than 2 points contribute no pair. abs_winding.json, 6 collections, 59 points, winding_is_absolute true (exploratory only, s.7). umbilicus.json, 146 control points, z 563 to 18240.
- I have not looked at any per-collection wind_a sequence beside the mesh. I have not projected any annotation point onto any Paris 4 mesh. The only Paris 4 projection run so far was a timing run of all 2173 points against winding w050 alone (14.0 s CPU), whose output was discarded unread beyond the wall time.
- Unknowns stated as unknowns: whether wind_a increases inward or outward relative to the winding ids in windings.tif (s.5 fixes the rule); whether the evaluator's theta convention matches VC3D (not used by the primary statistic); the radial sheet spacing in this region relative to the 10 vox tolerance.

## 1. Hypothesis
H1 (audit outcome): at least one annotation collection has a consecutive pair whose wind_a step differs from the step between the windings its two points lie on in the fitted mesh. Those pairs are reported for human review.
H0: every scorable pair agrees (exact_step_share = 1 with an interval that reaches 1).
Given s.0 caveat 2, H0 is the expected result. The test is still worth running because the fit used these annotations as a soft loss, not a hard constraint, and because the label reconstruction drops regions; a chain the fit could not honour is exactly the kind of annotation the Challenge asks contributors to check.

## 2. Data (read only; no manual annotation; no edits to any input)
- inputs/relative_windings.json sha256 a3243511d4eb91387a9b32f4dbff11514b08c3ae36e9b2a2b8222607b4883ac1
- inputs/umbilicus.json sha256 c5f30b0d135c1d333f8170e592079a3d5a636e0071c0dcce560eecebb0ee2602 (passed to the evaluator for theta; not used by the primary statistic)
- inputs/abs_winding.json sha256 4e566731f7cbaf8f5ec843de687b3f72f4a784c40b587ebbaf544550902172c1 (exploratory, s.7)
- Spiral-fit native mesh: meta.json 0af32a21bf0d759a96b8d6b8b170b8f50693632c92fd87487eb666bf12d1a7bc, windings.tif 0c24817c67f6c8590146e14f029bd42c31780c9655fc1facc5941907c4e3ffcc, x.tif 44efd92dabb63f6f03a026eb95335f59cb1929a6a3fc63dc8a9fe1dd3fd3b679, y.tif 49ceeb606b8e6ece0aee71e9bcf084025f67fb911b913837aaad7a5a097b8db3, z.tif fda1e08b3558412debbe87caa4cbe5b3242f71633d03f8ff1fdd284041a1b8ba.
- Per-winding meshes: output of split_windings.py on the files above, no z window (--z-min and --z-max unset). split_summary.json in the meshes directory records vertex counts per winding.
- Frame: both annotations and mesh are in the 9.6 um (level 2) voxel frame of scan 20260411134726. No rescaling is applied.

## 3. Positive and negative controls (GATE; both run and read before any real-annotation number exists)
- Positive: `--make-control positive --n-per-mesh 20` (seed as fixed in the evaluator), chains of 4 to 6 vertices drawn from consecutive windings, wind_a steps equal to winding-id steps by construction. Required: exact_step_share = 1.000 with interval [1, 1], sign_violations = 0, n_unlinked = 0. Any other value means the mesh split, the linker, or the tolerance is broken: STOP, fix, re-seal with a new code hash, state it in RESULT.
- Negative: `--make-control negative --n-per-mesh 20`, same chains with a +1 inserted after a random position in 30 percent of chains. Required: exact_step_share bootstrap interval upper bound below 1.000 and point estimate below 0.95 (expected about 0.90 to 0.93 from the chain-length mix). If the negative control is not separated from the positive one the statistic cannot see a one-winding error and the audit is uninformative: STOP.
- Both controls use the same meshes, tolerance and bootstrap settings as the real run (s.4).

## 4. Statistic and decision (primary)
- Linking: every annotation point is projected to every per-winding mesh (Patch.project, CPU); the nearest mesh within tolerance 10 vox (96 um) is its winding; farther than 10 vox from all meshes = unlinked, pair excluded.
- Primary statistic: exact_step_share = share of consecutive pairs (ordered by creation_time within a collection, both points linked) with d_pred = wind_a(j) - wind_a(i) equal to d_true = winding(j) - winding(i) after the direction rule of s.5.
- Interval: bootstrap over collections, 2000 replicates, seed 343, as implemented in pooled_with_interval; 2.5 / 97.5 percentiles. One primary number, one interval, nothing else decides.
- Decision:
  - exact_step_share = 1 and the interval's lower bound = 1: H0, no disagreement found; report n_unlinked and n_excluded so the reader can see how much of the set was actually scorable.
  - any disagreeing pair exists: H1, list every disagreeing pair (collection id, point ids, wind_a values, winding ids, projection distances) in RESULT_winding_audit.md and in a CSV in the evidence repo. The share and its interval are reported beside the list. No pair is dropped, re-linked or reinterpreted after the run.
- The real run happens once. If it crashes it is re-launched unchanged; the crash is noted.

## 5. Direction rule (fixed now, applied mechanically)
Among scorable pairs with d_pred != 0 and d_true != 0, let r = share with d_pred * d_true < 0. If r > 0.5 the wind_a axis runs opposite to the winding-id axis: negate wind_a in a copy of relative_windings.json (sha256 of the copy recorded), rerun the evaluator on the copy, and report both runs with the negated one as primary. If r <= 0.5 the original run is primary. r itself is reported either way.

## 6. Compute plan
- Machine: this Mac, villa venv python (torch 2.15.0), CPU only (MPS fails inside Patch.project with a device mismatch). `-I` on every invocation because the inputs are downloaded files.
- Timing from the w050 run: 14.0 s for 2173 points against 241K vertices, so about 45 min per full run against 43.2M vertices. Three runs (positive, negative, real), controls in parallel first, real only after s.3 passes.
- Outputs: control_winding_positive.json, control_winding_negative.json, winding_audit_result.json, copied into validation/ with sha256 sidecars.

## 7. Secondary and exploratory (reported, no PASS bar, no claim)
- mean_abs_err, sign_violations, n_unlinked, n_excluded from the same run.
- Breakdown of exact_step_share by winding-id band (ids 10-39, 40-69, 70-99, 100-135) and by z third, counts only, no intervals.
- abs_winding.json: for its 59 points, the offset winding_id - wind_a per collection; a constant offset within a collection is the expected pattern, anything else is listed. Exploratory because 6 collections cannot carry an interval.
- Distribution of projection distances for linked points (median, 90th percentile), to say whether 10 vox was a loose or tight tolerance here.

## 8. Kill rules
- Either control fails s.3: STOP, no real run, RESULT says so.
- More than 50 percent of pairs unlinked or excluded: the audit is reported as uninformative for this mesh (label reconstruction too sparse), with the share still printed, no claim.
- The evaluator crashes on the real annotations in a way that needs a code change: the change is made, hashed, stated in RESULT, and the controls are rerun before the real run.

## 9. What this does not test
- Whether the annotations are correct relative to the scroll. The mesh was fitted to them (s.0 caveat 2).
- Whether the spiral fit is correct. A disagreeing pair is a flag for a human, not a verdict on either side.
- Theta or the evaluator's angular convention; absolute winding numbers; anything about ink.
- Windings 0-9 (no mesh exported) and any annotation point outside the mesh's bounding box.

## 10. Decisions closed at seal
- Tolerance 10 vox, bootstrap 2000 / seed 343, controls at --n-per-mesh 20, no z window, no exclusion sectors, nearest-mesh linking. None of these is tuned after a number is seen.
- Nothing from this run goes into a PR body, the November form or any public text before RESULT_winding_audit.md is sealed and pushed.

## 11. Code frozen at seal (sha256 in PREREG_winding_audit_code.sha256)
eval_relative_windings.py cd193c08754ea98dfe7b5f308999c4d089cc0e592514c652610f6f2145993027
tifxyz.py 7c9d2a561550e3ecdc75f72e2f1c5dc0eeaba9580714db19a5631a3d8197b993
split_windings.py 2d92750ab6ff542ec35112c96a6a442b5169c88deafb5077e7129c3274664790
