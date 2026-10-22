# Pre-registration: per-angle material-run count between w033 and w037 (2026-10-22, before any run)

Question. In PHerc0139 volume 20260102150214, do the Kaggle-era meshes w033-w037 occupy five distinct
material layers (one winding each) in the gap sector (theta 5-71 deg, z 9,000-27,800), as they do in the
control sectors (theta 130-170, 160-200)?

Instrument. Level-1 CT (4.8 um) polar slice about the umbilicus; per angle column a radial profile from
60 um inside the innermost crossing to 60 um outside the outermost; Gaussian smooth sigma 10 um; threshold =
Otsu over the nonzero pixels of the window; a material run = contiguous above-threshold stretch >= 20 um
(gaps < 10 um bridged). Each winding's crossing at that angle = linear interpolation of its main-piece
crossings (end pieces excluded), present only if a crossing lies within 1.5 deg. A crossing is "in" a run
if within 1 px (4.8 um) of it, else "air".

Per column: n_runs between the innermost and outermost present crossings inclusive; same_sheet = two
windings in one run of width <= 1.5 x the control median run width; ambiguous = two windings in one run
wider than that (may hold pressed sheets; never counted as same-sheet); empty = a run strictly between two
present windings holding no winding; air = a winding in no run.

Instrument check (must pass before the finding is read). In C1 and C2, shift w034 radially by +110 um
(one winding) and by +55 um, recompute. Pass: >= 90% of columns that were clean unshifted become flagged
(same_sheet, ambiguous, empty or air) at +110 um. If the instrument fails, report the failure and stop.

Finding. Fraction of columns flagged (same_sheet + empty + air, and ambiguous separately) per window, gap
sector vs control sectors, by height. Pre-stated expectation from the by-eye unwraps: gap >> control for
same_sheet and empty. No threshold is set for "confirmed"; the result is reported as measured with the
control baseline alongside.

Amendment 1 (2026-10-22, after the instrument check, before any gap window was read). The 1 px (4.8 um)
"in run" tolerance flagged 70-90% of control crossings as air; the measured crossing-to-nearest-run distance
in C1/C2 has median 0, 90th percentile 16 um (C1) / 39 um (C2). Tolerance set to 10 um. Metrics are now
per crossing (column x winding), not per column, since any-of-five per column inflates every rate.
Instrument pass rule unchanged in spirit: >= 90% of w034 crossings that are "ok" unshifted become flagged
(air, same, amb, or a changed empty-run count) at +110 um.

Amendment 2 (2026-10-22, still before any gap window). The fixed +110 um shift flags only 48% (C1) / 79%
(C2) of clean w034 crossings: the local pitch is 100-150 um and split plies between layers give the shifted
trace a stray run. The signature the finding looks for is "two meshes in one run" + "a run with no mesh", so
the instrument check is now: copy w034 onto w035's interpolated radius (5 um inside it). Pass: >= 90% of
clean w034 crossings flagged. The +55/+110 um results are kept and reported as what they are.
