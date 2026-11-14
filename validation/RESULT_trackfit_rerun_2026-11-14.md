# RESULT: tracks-only spiral fits, rerun under the sealed amendment (2026-11-14)

Pre-registration: `PREREG_trackfit_2026-11-08.md` (commit ad7fe09), not edited.
First result: `RESULT_trackfit_2026-11-08.md` (commit 6a65a56), not edited.
Amendment: `PREREG_trackfit_AMENDMENT_2026-11-14.md` (commit 78b5987), sealed and pushed before the rerun started.
Wrapper: `trackfit_chain2.sh`. Full wrapper log: `trackfit_chain2.log`.

## Verdict

All four scrolls are INCOMPLETE again. No run reached 30000 steps, so the primary
ratio R is not evaluable for any scroll. I make no claim about surface quality.

Every rerun was stopped by the amended rule s.8d: the physical memory footprint of the
fitter process reached 30 GB on two consecutive 30 s samples.

## Both attempts side by side

track_radius (tr) values are the printed loss terms. "Partial ratio" is tr at the last
logged step divided by tr at step 200. It is exploratory only and is not R.

| Scroll | Attempt | tr step 0 | tr step 200 | Last step | tr there | Partial ratio | Stopped by | Verdict |
|---|---|---|---|---|---|---|---|---|
| PHerc0343P_20260304131111 | first (11-08) | | 884.0 | 15000 | 14.5 | 0.016 | original s.8c | INCOMPLETE |
| PHerc0343P_20260304131111 | rerun (11-14) | 2742.7 | 883.4 | 1400 | 80.7 | 0.091 | amended s.8d, 30 GB | INCOMPLETE |
| PHerc0500P2_20250526151718 | first | | 3147.8 | 2000 | 151.6 | 0.048 | original s.8d | INCOMPLETE |
| PHerc0500P2_20250526151718 | rerun | 11731.3 | 3146.0 | 400 | 849.5 | 0.270 | amended s.8d, 30 GB | INCOMPLETE |
| PHerc0500P2_20250820143440 | first | | none | 0 | | none | original s.8d | INCOMPLETE |
| PHerc0500P2_20250820143440 | rerun | 11945.5 | none | 0 | 11945.5 | none | amended s.8d, 31 GB | INCOMPLETE |
| PHerc0009B_20260319104112 | first | | none | 0 | | none | original s.8d | INCOMPLETE |
| PHerc0009B_20260319104112 | rerun | 7784.6 | none | 0 | 7784.6 | none | amended s.8d, 42 GB | INCOMPLETE |

Empty first-attempt cells are values I did not carry into this file; they are in the first RESULT and its logs.

## What the rerun measured

The amended s.8d samples the fitter's own physical footprint (`top -stats mem`), which
counts MPS unified-memory allocations. On this 36 GB Mac:

- 0343P (the smallest target): 5.9 GB at step 0, 23 GB at step 1000, 30 GB near step 1400.
- 0500P2 0526: 18 GB at step 0, 30 GB before step 600.
- 0500P2 0820: 7.2 GB at step 0, 31 GB about 17 minutes later, with no step past 0 logged.
- 0009B: 42 GB within 2.5 minutes of launch.

So the fitter itself outgrows this machine. The low machine-wide free memory that stopped
three runs in the first attempt was at least largely the fitter, not only other jobs.
The first attempt of 0343P reached step 15000 only because the original rule did not
measure the fitter footprint; it presumably ran on compressed memory and swap.

## Limits

- The 30 GB cap was my choice, made after seeing first-attempt data. A higher cap might
  have let 0343P run longer on swap. I did not test that and I will not relaunch under this
  amendment, which allowed one rerun only.
- Footprint growth with step count may be a leak, a cache, or expected behaviour of the
  fitter on MPS. I did not investigate which.
- Partial ratios from different step counts are not comparable with each other or with R.

## What would be needed

A completed test needs a machine with more memory (or a CUDA GPU with enough VRAM) and a
new sealed pre-registration. Nothing further is run under this one.
