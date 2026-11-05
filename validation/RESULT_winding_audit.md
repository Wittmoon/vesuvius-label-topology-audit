# RESULT: relative-winding annotation audit, PHerc. Paris. 4 (PREREG_winding_audit.md, sealed 2026-11-04)

Outcome: **H1**. 100 of 1677 scorable consecutive pairs disagree with the fitted mesh. They are listed below and in `winding_audit_disagreeing_pairs.csv`. This is an audit, not a reading, and (PREREG s.0 caveat 2, s.9) the mesh was fitted to the annotations being audited, so agreement is not evidence that an annotation is right and a disagreement is a flag for a human, not a verdict on either side.

## Primary (s.4), one run, no rerun

| statistic | value |
|---|---|
| exact_step_share | 0.9404 |
| CI95 (bootstrap over collections, 2000 replicates, seed 343) | [0.9228, 0.9563] |
| n_pairs scorable | 1677 |
| n_exact | 1577 |
| n_disagreeing | 100 |
| n_unlinked points (farther than 10 vox from every mesh) | 219 of 2173 |
| n_excluded | 0 |
| collections | 300 (227 with at least one scorable pair; 64 of those carry a disagreeing pair) |
| tolerance | 10 vox |

Kill rule s.8 (more than 50 percent unlinked or excluded): not triggered (10.1 percent of points unlinked).

## Direction rule (s.5)

Among scorable pairs with d_pred != 0 and d_true != 0 (n = 1635), the share with d_pred * d_true < 0 is r = 0 / 1635 = 0. The original run is primary; no negated copy was made.

Every scorable pair has d_pred = +1: the Challenge annotation chains step one winding per point. d_true is 1 in 1577 pairs, 0 in 42, 2 in 52 and 3 in 6. Every disagreement is therefore the mesh placing two consecutive points on the same winding, or two or three windings apart, where the annotation says one.

## Disagreeing pairs (s.4; every pair, none dropped, re-linked or reinterpreted)

Columns: collection id, point ids in creation_time order, wind_a values, winding ids of the nearest mesh, projection distance (vox) of each point to that mesh, d_pred, d_true. The share and its interval are the ones in the table above.

| collection | point a | point b | wind_a a | wind_a b | winding a | winding b | dist a | dist b | d_pred | d_true |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 43 | 44 | 40 | 41 | 61 | 61 | 4.44 | 3.33 | 1 | 0 |
| 102 | 1455 | 1456 | 3 | 4 | 61 | 63 | 0.67 | 1.89 | 1 | 2 |
| 102 | 1456 | 1457 | 4 | 5 | 63 | 63 | 1.89 | 5.54 | 1 | 0 |
| 105 | 1475 | 1476 | 1 | 2 | 56 | 58 | 4.01 | 1.58 | 1 | 2 |
| 109 | 1495 | 1496 | 2 | 3 | 91 | 91 | 3.16 | 8.26 | 1 | 0 |
| 120 | 1604 | 1605 | 5 | 6 | 61 | 63 | 6.62 | 6.13 | 1 | 2 |
| 125 | 1665 | 1666 | 7 | 8 | 37 | 37 | 5.76 | 8.47 | 1 | 0 |
| 125 | 1666 | 1667 | 8 | 9 | 37 | 39 | 8.47 | 0.00 | 1 | 2 |
| 136 | 1734 | 1735 | 2 | 3 | 92 | 92 | 9.80 | 3.82 | 1 | 0 |
| 143 | 1778 | 1779 | 10 | 11 | 40 | 40 | 3.70 | 5.51 | 1 | 0 |
| 143 | 1779 | 1780 | 11 | 12 | 40 | 42 | 5.51 | 7.28 | 1 | 2 |
| 144 | 1796 | 1797 | 6 | 7 | 62 | 64 | 0.84 | 4.22 | 1 | 2 |
| 147 | 1814 | 2930 | 4 | 5 | 84 | 84 | 5.08 | 8.66 | 1 | 0 |
| 154 | 1881 | 1882 | 2 | 3 | 50 | 52 | 3.38 | 7.24 | 1 | 2 |
| 164 | 2010 | 2011 | 3 | 4 | 61 | 61 | 7.46 | 7.36 | 1 | 0 |
| 168 | 2030 | 2031 | 2 | 3 | 82 | 82 | 8.54 | 4.76 | 1 | 0 |
| 174 | 2067 | 2068 | 3 | 4 | 14 | 16 | 2.54 | 5.03 | 1 | 2 |
| 174 | 2068 | 2069 | 4 | 5 | 16 | 16 | 5.03 | 3.63 | 1 | 0 |
| 178 | 2101 | 2102 | 3 | 4 | 59 | 61 | 7.22 | 7.89 | 1 | 2 |
| 178 | 2102 | 2103 | 4 | 5 | 61 | 61 | 7.89 | 5.67 | 1 | 0 |
| 178 | 2106 | 2107 | 8 | 9 | 64 | 66 | 0.92 | 2.14 | 1 | 2 |
| 179 | 2116 | 2117 | 8 | 9 | 58 | 60 | 0.39 | 5.10 | 1 | 2 |
| 183 | 2161 | 2162 | 2 | 3 | 115 | 115 | 2.10 | 8.20 | 1 | 0 |
| 188 | 2179 | 2180 | 1 | 2 | 107 | 107 | 4.67 | 2.88 | 1 | 0 |
| 190 | 2185 | 2186 | 1 | 2 | 104 | 107 | 5.83 | 3.23 | 1 | 3 |
| 191 | 2187 | 2188 | 1 | 2 | 123 | 125 | 6.98 | 4.10 | 1 | 2 |
| 191 | 2188 | 2189 | 2 | 3 | 125 | 125 | 4.10 | 6.26 | 1 | 0 |
| 194 | 2199 | 2200 | 1 | 2 | 54 | 54 | 2.77 | 6.53 | 1 | 0 |
| 194 | 2200 | 2201 | 2 | 3 | 54 | 56 | 6.53 | 2.03 | 1 | 2 |
| 201 | 2253 | 2254 | 2 | 3 | 92 | 92 | 6.29 | 2.65 | 1 | 0 |
| 220 | 2396 | 2397 | 3 | 4 | 43 | 45 | 5.38 | 0.06 | 1 | 2 |
| 222 | 2416 | 2417 | 2 | 3 | 60 | 60 | 0.63 | 8.58 | 1 | 0 |
| 229 | 2472 | 2473 | 1 | 2 | 54 | 56 | 2.69 | 2.84 | 1 | 2 |
| 229 | 2473 | 2474 | 2 | 3 | 56 | 58 | 2.84 | 8.33 | 1 | 2 |
| 235 | 2504 | 2505 | 5 | 6 | 104 | 104 | 5.31 | 5.98 | 1 | 0 |
| 244 | 2559 | 2560 | 2 | 3 | 62 | 64 | 3.44 | 1.87 | 1 | 2 |
| 244 | 2561 | 2562 | 4 | 5 | 65 | 67 | 8.34 | 8.78 | 1 | 2 |
| 246 | 2573 | 2574 | 4 | 5 | 47 | 50 | 1.30 | 2.01 | 1 | 3 |
| 247 | 2575 | 2576 | 1 | 2 | 44 | 44 | 6.14 | 9.33 | 1 | 0 |
| 247 | 2580 | 2581 | 6 | 7 | 48 | 50 | 3.37 | 2.88 | 1 | 2 |
| 249 | 2598 | 2599 | 1 | 2 | 61 | 63 | 0.26 | 7.32 | 1 | 2 |
| 249 | 2599 | 2600 | 2 | 3 | 63 | 63 | 7.32 | 7.25 | 1 | 0 |
| 249 | 2600 | 2601 | 3 | 4 | 63 | 65 | 7.25 | 2.58 | 1 | 2 |
| 250 | 2608 | 2609 | 7 | 8 | 63 | 65 | 2.15 | 0.92 | 1 | 2 |
| 250 | 2609 | 2610 | 8 | 9 | 65 | 67 | 0.92 | 2.96 | 1 | 2 |
| 251 | 2613 | 2614 | 2 | 3 | 68 | 70 | 2.26 | 1.53 | 1 | 2 |
| 251 | 2615 | 2616 | 4 | 5 | 71 | 73 | 4.44 | 2.90 | 1 | 2 |
| 251 | 2616 | 2617 | 5 | 6 | 73 | 73 | 2.90 | 3.70 | 1 | 0 |
| 252 | 2618 | 2619 | 1 | 2 | 74 | 76 | 5.94 | 6.30 | 1 | 2 |
| 253 | 2629 | 2630 | 1 | 2 | 84 | 84 | 5.95 | 2.76 | 1 | 0 |
| 26 | 459 | 460 | 2 | 3 | 59 | 59 | 4.91 | 5.96 | 1 | 0 |
| 264 | 2688 | 2689 | 1 | 2 | 47 | 49 | 1.82 | 5.15 | 1 | 2 |
| 264 | 2689 | 2690 | 2 | 3 | 49 | 51 | 5.15 | 2.00 | 1 | 2 |
| 264 | 2692 | 2693 | 5 | 6 | 53 | 56 | 0.62 | 2.02 | 1 | 3 |
| 265 | 2696 | 2697 | 1 | 2 | 52 | 55 | 0.73 | 3.29 | 1 | 3 |
| 265 | 2707 | 2708 | 12 | 13 | 65 | 67 | 2.02 | 5.25 | 1 | 2 |
| 265 | 2708 | 2709 | 13 | 14 | 67 | 67 | 5.25 | 2.10 | 1 | 0 |
| 265 | 2709 | 2710 | 14 | 15 | 67 | 70 | 2.10 | 2.22 | 1 | 3 |
| 269 | 2755 | 2756 | 5 | 6 | 73 | 75 | 4.79 | 4.70 | 1 | 2 |
| 272 | 2769 | 2770 | 1 | 2 | 85 | 85 | 8.52 | 7.29 | 1 | 0 |
| 272 | 2808 | 2809 | 4 | 5 | 87 | 89 | 3.65 | 1.90 | 1 | 2 |
| 276 | 2824 | 2825 | 5 | 6 | 62 | 64 | 3.50 | 7.02 | 1 | 2 |
| 277 | 2826 | 2827 | 1 | 2 | 62 | 65 | 1.36 | 7.65 | 1 | 3 |
| 277 | 2830 | 2831 | 5 | 6 | 68 | 70 | 1.71 | 0.50 | 1 | 2 |
| 280 | 2856 | 2857 | 4 | 5 | 40 | 42 | 1.98 | 2.32 | 1 | 2 |
| 280 | 2860 | 2861 | 8 | 9 | 45 | 47 | 0.38 | 2.94 | 1 | 2 |
| 280 | 2861 | 2862 | 9 | 10 | 47 | 49 | 2.94 | 3.73 | 1 | 2 |
| 280 | 2862 | 2863 | 10 | 11 | 49 | 49 | 3.73 | 5.54 | 1 | 0 |
| 281 | 2879 | 2880 | 7 | 8 | 63 | 65 | 0.42 | 0.79 | 1 | 2 |
| 286 | 2907 | 2915 | 1 | 2 | 57 | 59 | 0.51 | 0.49 | 1 | 2 |
| 288 | 2946 | 2947 | 8 | 9 | 61 | 63 | 0.54 | 4.50 | 1 | 2 |
| 295 | 3003 | 3004 | 6 | 7 | 82 | 84 | 1.12 | 6.45 | 1 | 2 |
| 295 | 3004 | 3005 | 7 | 8 | 84 | 84 | 6.45 | 5.74 | 1 | 0 |
| 296 | 3009 | 3010 | 2 | 3 | 86 | 88 | 0.63 | 0.13 | 1 | 2 |
| 300 | 3043 | 3044 | 7 | 8 | 108 | 108 | 6.59 | 7.64 | 1 | 0 |
| 301 | 3051 | 3052 | 3 | 4 | 92 | 92 | 2.75 | 9.32 | 1 | 0 |
| 303 | 3064 | 3065 | 4 | 5 | 99 | 101 | 1.61 | 0.40 | 1 | 2 |
| 31 | 511 | 512 | 6 | 7 | 58 | 60 | 4.64 | 6.44 | 1 | 2 |
| 31 | 512 | 513 | 7 | 8 | 60 | 60 | 6.44 | 6.00 | 1 | 0 |
| 31 | 516 | 517 | 11 | 12 | 63 | 65 | 0.90 | 4.35 | 1 | 2 |
| 35 | 595 | 596 | 1 | 2 | 52 | 54 | 9.92 | 5.20 | 1 | 2 |
| 36 | 610 | 611 | 9 | 10 | 25 | 25 | 2.63 | 8.14 | 1 | 0 |
| 36 | 611 | 612 | 10 | 11 | 25 | 27 | 8.14 | 5.05 | 1 | 2 |
| 37 | 650 | 651 | 2 | 3 | 90 | 92 | 4.12 | 2.77 | 1 | 2 |
| 39 | 668 | 669 | 4 | 5 | 86 | 86 | 5.90 | 7.21 | 1 | 0 |
| 40 | 677 | 678 | 3 | 4 | 86 | 86 | 1.04 | 8.49 | 1 | 0 |
| 44 | 717 | 718 | 4 | 5 | 86 | 86 | 1.01 | 6.75 | 1 | 0 |
| 54 | 812 | 813 | 1 | 2 | 96 | 96 | 1.92 | 1.54 | 1 | 0 |
| 54 | 813 | 814 | 2 | 3 | 96 | 96 | 1.54 | 0.07 | 1 | 0 |
| 54 | 814 | 815 | 3 | 4 | 96 | 98 | 0.07 | 0.88 | 1 | 2 |
| 54 | 825 | 826 | 14 | 15 | 107 | 107 | 5.98 | 3.95 | 1 | 0 |
| 75 | 1153 | 1154 | 1 | 2 | 82 | 84 | 1.69 | 3.55 | 1 | 2 |
| 75 | 1156 | 1157 | 4 | 5 | 86 | 86 | 7.08 | 5.37 | 1 | 0 |
| 75 | 1157 | 1158 | 5 | 6 | 86 | 88 | 5.37 | 2.51 | 1 | 2 |
| 77 | 1169 | 1170 | 6 | 7 | 54 | 56 | 0.66 | 3.39 | 1 | 2 |
| 83 | 1225 | 1226 | 3 | 4 | 60 | 62 | 0.93 | 2.74 | 1 | 2 |
| 83 | 1227 | 1228 | 5 | 6 | 63 | 63 | 2.65 | 4.84 | 1 | 0 |
| 9 | 168 | 169 | 1 | 2 | 15 | 15 | 8.87 | 1.40 | 1 | 0 |
| 96 | 1406 | 1407 | 5 | 6 | 90 | 90 | 1.83 | 6.55 | 1 | 0 |
| 99 | 1422 | 1423 | 1 | 2 | 15 | 15 | 9.77 | 3.36 | 1 | 0 |

## Secondary and exploratory (s.7; counts only, no claim)

- mean_abs_err 0.0632 [0.0458, 0.0818]; sign_violations 0; n_unlinked 219; n_excluded 0.
- exact_step_share by winding-id band of point a: 10-39: 785/793 (0.990); 40-69: 595/651 (0.914); 70-99: 138/166 (0.831); 100-135: 59/67 (0.881).
- By z third of point a (cuts at z 10235 and 13189 from the point distribution): low 594/619 (0.960); mid 478/538 (0.889); high 505/520 (0.971).
- Projection distance of linked points: median 1.56 vox, 90th percentile 4.91 vox, so 10 vox was a loose tolerance for the points that linked. Unlinked points: median 57 vox, 90th percentile 150 vox, maximum 196 vox; they sit far from every exported winding, consistent with the dropped (-1/-2) regions of windings.tif or with windings 0-9, which have no mesh. Unlinked points by nearest winding band: 10-39: 51; 40-69: 113; 70-99: 46; 100-135: 9.
- Disagreeing pairs sit farther from the mesh than exact ones: max of the two projection distances has median 5.68 vox (p90 8.52) for disagreeing pairs against 2.21 vox (p90 5.48) for exact pairs. Read as an observation, not a test: a point several voxels from its nearest exported winding may be on a sheet region the reconstruction dropped.
- abs_winding.json (59 points, 6 collections, `winding_audit_abs_winding_points.csv`): collection 1, 48 points, offset winding_id - wind_a = 0 for all 48; collection 5, 8 points, offset 0 for all; collection 6, 1 point, offset 0; collection 2, 1 point, offset +2 (distance 4.2 vox); collection 3, 1 point, unlinked (12.0 vox from the nearest mesh, winding id shown in the CSV); collection 4 has no points. So the wind_a axis of abs_winding.json coincides with the windings.tif ids where it links, and one single-point collection is off by two.

## Controls (s.3, gate passed before the real run; files control_winding_positive.json / control_winding_negative.json)

Positive: exact_step_share 1.000 [1, 1], sign_violations 0, n_unlinked 0. Negative: exact_step_share 0.918 [0.906, 0.930], below the s.3 bar (point estimate below 0.95, upper bound below 1). Recorded in commit fd52a21 before the real run.

## Deviations and notes

1. The sealed evaluator writes per-collection aggregates only, so the pair detail PREREG s.4 requires did not exist in `winding_audit_result.json`. The links were reproduced by `winding_audit_dump_pairs.py`, which imports the sealed `load_truth_meshes` and `load_point_collection` and repeats `link_points` line for line (same Patch.project call, same min over meshes, same tolerance), keeping the nearest mesh and distance, with the pair ordering of `score_collection`. Its recomputed aggregates (n_pairs 1677, n_exact 1577, n_unlinked 219, share 0.94036971) match the sealed run exactly. Nothing was re-linked with different settings. `winding_audit_dump_abs.py` does the same for abs_winding.json.
2. PREREG s.11 prose carries a typo in the tifxyz.py hash ("cd75f72e"); the sidecar `PREREG_winding_audit_code.sha256` is authoritative and matches the code that ran.
3. The real run was launched once and did not crash.

## What this does not show (s.9)

Whether any annotation or the spiral fit is right relative to the scroll. Johannes (villa Discord, #unrolling-vc3d, 2026-11-03/04) reports an independent spiralfiteval check in which label points were about 97 percent right and, on gappy fits, 18 of 38 were one winding off. The 94 percent here is the same kind of number on a mesh fitted to these very annotations, and should be read beside his, not instead of it. The Challenge team has said it is done with Paris 4 for the moment (Paul, 2026-10-26) and that it does not generally read externally produced benchmarks (Paul, 2026-11-03); this list is offered as a review aid, nothing more.

Hashes of the files in this directory are in `winding_audit_result.sha256`.
