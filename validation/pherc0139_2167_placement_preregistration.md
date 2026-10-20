# PHerc0139 issue #2167: does the placement audit see the w034/w036 gap in the CT? (pre-registered 2026-10-20 16:37)

Question (villa issue #2167, ChaseHendrick): on scan 20260102150214, w035 covers ~258 deg per grid line.
In the missing sector w036 sits at w034's radius, and geometry cannot say which mesh left its sheet.
"Checking against the CT is needed." This run asks whether `vesuvius.surface_placement_audit`,
unchanged, reads the gap sector as worse-placed than the rest of the same windings. No new check is built.

## Design, fixed before any CT sample was analysed (smoke run excepted, see below)
- Volume: open-data `20260102150214-2.399um-0.2m-78keV-masked.zarr`, OME-Zarr level 2 (9.596 um,
  coordinates divided by 4). Level 0 would read 30+ GB per winding. All offsets below are level-2 voxels.
- Inputs (`make_inputs.py`, hashes below): sector-masked copies of the published tifxyz grids of
  w033, w034, w036, w037. Angle = atan2 about the umbilicus interpolated in z (no extrapolation).
  GAP = z 9,000-27,800 (level-0) and angle 5-71 deg; OUT = same z, angle 100-210 deg. The doubly
  traced end of a winding (unwrapped angle span > 360 deg per grid row, farther-radius piece) is
  excluded from every input and kept as `w034_GAP_end` on its own. w035 has 977 points in GAP
  (0.1% of its valid grid), which is the geometry gate: it is not run.
  Positive controls: w033 shifted +6 and +12 level-2 voxels along its own normal, both sectors.
  Gates met: every run input has >= 193,597 valid points (inputs_report.jsonl).
- Run: 13 inputs x 5,000 samples, seed 2167, `--half 8 --step 0.5 --sigma 1 --min-contrast 8
  --min-prominence 0.15`, shared chunk cache.
- Endpoint per sample: **unplaced** = no accepted peak within +-8 voxels OR |offset| > 2 voxels.
  This is not a sheet-switch detector; the README's "not covered" row for sheet identity stays.
- Primary: D = [u(w034 GAP) - u(w034 OUT)] - [u(w033 GAP) - u(w033 OUT)], a difference in
  differences with w033 as the within-scroll control (`analyze.py`). 95% percentile interval from a
  block bootstrap (blocks 1,000 level-0 voxels in z x 10 deg, resampled jointly across inputs,
  2,000 draws, seed 2167). Pre-registered direction D > 0.
- Minimum effect from the smoke run: block-bootstrap SD of u(w033 OUT) at 1,000 samples = 0.017,
  so minimum effect = max(0.05, 3 x 0.017) = **0.05**. Smoke gates passed: 92.6% accepted peaks,
  contrast median 79, u = 0.414 (smoke_w033_OUT.json, smoke_analysis.csv).
- Expected result, stated up front: near null. Chase's note found w034 and w036 sharing one dense
  band at 7 of 9 gap places, which this endpoint cannot distinguish from correct placement.
- Secondaries (reported whatever the primary does): D for w036 and w037 against the same control;
  u(w034_GAP_end) - u(w034_GAP); the two positive controls in both sectors; D within pooled
  contrast quartiles (contrast is the live confound); joint measure = fraction of w036 samples
  whose snapped peak lies within 2 voxels of the snapped peak of the nearest w034 sample, GAP vs OUT.
- Kill rules: smoke gates (passed); any sector input under 20,000 valid points (none);
  w033 +12 control not unplaced on >= 80% of OUT samples -> the endpoint does not respond and the
  run is reported as a failed instrument check, no D is interpreted.
- Blinded CT look: 20 samples, row indices frozen in `blind_ids.json` (5 each from w034 GAP/OUT,
  w036 GAP/OUT), viewed at level 0 with the sector and offset hidden, each called sheet / air /
  between-sheets before unblinding. Descriptive only.
- Outcome rule: "the audit sees the gap" only if D > 0.05 with the interval excluding 0 AND the
  sign holds in at least 3 of 4 contrast quartiles. Otherwise "not seen at this resolution with
  this endpoint", reported as such, with the secondaries.

## Hashes (sha256) of the frozen code and ids
    f1fb9d69f0235a3621464264b4144342506e23ec6a60173a968fb2cd8c1c42f4  make_inputs.py
    7dd201687b85ec23baa8983cc948b6cacb3d243b6b1f8a6ed1ed719f9a5ed0ad  analyze.py
    8a2eb1c8c0f76f8d7b18c7ac627920777224433fa8a292d193f1ddb39b242c85  blind_ids.json

Raw inputs: validation/pherc0139_2167/SHA256SUMS (five tifxyz grids + umbilicus from the open-data bucket).

## Clarification 2026-10-20, after the run (frozen text above unchanged)
3 x 0.017 = 0.051 (smoke_analysis.csv: 0.0511), so the formula gives 0.051, not 0.05 as written. The
threshold applied is the explicitly frozen 0.05; the difference changes no outcome (no D reached either).
