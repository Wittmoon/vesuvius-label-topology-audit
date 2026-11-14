# Amendment to the track-fit pre-registration (sealed 2026-11-14, before any rerun)

This file amends `validation/PREREG_trackfit_2026-11-08.md` (sha256 5572b49d...154d, commit ad7fe09).
That file and `validation/RESULT_trackfit_2026-11-08.md` (sha256 e8f91934...37a7, commit 6a65a56) are not
edited. The four INCOMPLETE verdicts recorded there stand as the outcome of the first attempt.

## 1. Why I am amending

All four first-attempt runs were stopped by my own kill rules, not by the fitter:

- s.8c compared one printed loss value against one printed loss value 5000 steps earlier. The printed loss is
  noisy from line to line, so the rule fired on a run that had already converged.
- s.8d watched machine-wide free memory. Other jobs on the same machine pushed it under 2 GB while the fitter
  itself held 0.3 GB resident.

Neither rule measured what it was written to measure. The sealed RESULT already said that a rerun needs a
separately sealed pre-registration. This is that document.

## 2. What I have already seen (full disclosure)

This is a second attempt on the same four scrolls, and I write the amended rules after seeing first-attempt data.

| scroll | step-0 track_radius | step-200 track_radius | stopped at | track_radius there | rule |
|---|---|---|---|---|---|
| PHerc0343P_20260304131111 | 2742.7 | 884.0 | 15000 | 14.5 | s.8c |
| PHerc0500P2_20250526151718 | 11731.2 | 3147.8 | 2000 | 151.6 | s.8d |
| PHerc0500P2_20250820143440 | 11945.5 | not reached | 0 | 11945.5 | s.8d |
| PHerc0009B_20260319104112 | 7784.6 | not reached | 0 | 7784.6 | s.8d |

PHerc0343P total loss on the five printed lines ending at each checkpoint:
5000: 38.1, 27.0, 37.3, 38.8, 29.0 (mean 34.04). 10000: 9.3, 12.1, 17.6, 28.4, 15.5 (mean 16.58).
15000: 13.7, 23.1, 9.2, 7.4, 22.1 (mean 15.10).

Consequences I state up front:

- For PHerc0343P the partial ratio at step 15000 was 14.5 / 884.0 = 0.016, far under the 0.5 threshold. I expect
  that run to pass if it completes. Its rerun is a completion of a run whose direction I already know, not a
  blind test.
- For PHerc0500P2_20250526151718 I have seen 2000 steps (151.6 / 3147.8 = 0.048). Same caveat, weaker.
- For the other two scrolls I have seen only the step-0 line.
- The factor 2 in the amended s.8c and the 30 GB cap in the amended s.8d were chosen after seeing these numbers.
  On the PHerc0343P first-attempt log the amended s.8c would not have fired at 10000 (16.58 against 2 x 34.04)
  or at 15000 (15.10 against 2 x 16.58).

## 3. What changes (two kill rules, nothing else)

**s.8c (amended).** At every N that is a multiple of 5000 with N >= 10000, let M(N) be the mean total loss over
the five printed lines at steps N-800, N-600, N-400, N-200 and N. Kill if M(N) >= 2 x M(N-5000). This stops a
diverging run and does not stop a plateau.

**s.8d (amended).** Every 30 s, read the physical memory footprint of the fitter Python process (the MEM column
of `top -l 1 -pid <pid> -stats mem`; the process is the child of the `/usr/bin/time` wrapper). Kill if it is
at or above 30 GB on two consecutive samples. The machine has 36 GB. Machine-wide free memory is no longer a
kill condition. A machine that is thrashing still stops the run through s.8a (no new step line for 30 minutes).

## 4. What does not change

Primary measure R = track_radius at the last logged step / track_radius at step 200. A run must complete all
30000 steps. PASS R <= 0.5, FAIL R > 0.5, anything that does not complete is INCOMPLETE. Gate s.3, kill rules
s.8a and s.8b, the z ranges, the track inputs, every config override, the default step count, the MPS device,
the fitter (villa spiral-fitting at commit 2144fdd3f, unmodified), the dataset files (hashes in
`PREREG_trackfit_2026-11-08_code.sha256`), and the order (0343P, 0500P2_0526, 0500P2_0820, 0009B, sequential,
chain stops at the first gate failure) are all as sealed on 2026-11-08.

## 5. How the rerun is run

- Every run starts from step 0. No resume: `FIT_SPIRAL_RESUME_PATH` is not set, and each run writes to fresh
  `out_run2/` and `cache_run2/` directories and to `fit_run2.log`. First-attempt logs and outputs are kept.
- `run2.sh` for each scroll is the first-attempt `run.sh` with only those two directory names changed.
- The wrapper is `validation/trackfit_chain2.sh`. It logs the fitter footprint and swap use every 1000 steps.
- One rerun only. A run killed or failed under this amendment is INCOMPLETE and is not relaunched under it.
- Machine state at sealing: 36 GB RAM, swap 9.1 of 10.2 GB in use by other jobs I do not control. Slow or
  stalled runs on the larger scrolls are a real possibility and would be reported as INCOMPLETE (s.8a).

## 6. Reporting

Results go to a new file, `validation/RESULT_trackfit_rerun_<date>.md`, which reports both attempts side by
side. Even four passes would show only that the unmodified fitter converges on tracks alone for these scrolls
on this machine; it would say nothing about the quality of the resulting surfaces.

Hashes of the wrapper and the four `run2.sh` files are in `PREREG_trackfit_AMENDMENT_2026-11-14_code.sha256`.
