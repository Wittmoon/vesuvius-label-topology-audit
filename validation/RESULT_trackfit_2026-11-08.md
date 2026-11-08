# RESULT: tracks-only spiral fits on MPS, four public scrolls (2026-11-08)

Pre-registration: `PREREG_trackfit_2026-11-08.md` (sha256 in `.md.sha256`, sealed at commit ad7fe09, unedited).
Inputs: as hashed in `PREREG_trackfit_2026-11-08_code.sha256`. Fitter: villa `spiral-fitting` at main-fit commit 2144fdd3f, unmodified.
Machine: Apple silicon, 14 cores, 36 GB unified memory, device `mps`. Runs were sequential and unattended under
`chain.sh` (sha256 01458d111b1ea7223fed90ef94023f3a988c194ab907197836be9c4e705630e0), which implemented the s.3 gate and the s.8 kill rules.

## Outcome in one line

All four fits are **INCOMPLETE** under s.4. None reached 30 000 steps. No PASS or FAIL is claimed for any scroll.
Not one run was stopped by a fit failure: every stop was a pre-registered kill rule firing on something other than the fit (see s.8 notes).

## Per scroll (s.4 reporting items)

| scroll | gate s.3 | step 0 track_radius | step 200 track_radius | last step | last track_radius | stop | verdict |
|---|---|---|---|---|---|---|---|
| PHerc0343P (z 4500–5010) | pass | 2742.7 | 884.0 | 15000 | 14.5 | kill s.8c | INCOMPLETE |
| PHerc0500P2_20250526 (z 4500–5500) | pass | 11731.2 | 3147.8 | 2000 | 151.6 | kill s.8d | INCOMPLETE |
| PHerc0500P2_20250820 (z 4500–5750) | pass | 11945.5 | — | 0 | 11945.5 | kill s.8d | INCOMPLETE |
| PHerc0009B (z 4500–7000) | pass | 7784.6 | — | 0 | 7784.6 | kill s.8d | INCOMPLETE |

Last metric lines, verbatim:

- 0343P: `step 15000: loss = 22.1, umbilicus = 0.0, sym_dirichlet = 7.6, min_spacing = 0.0, track_radius = 14.5, track_dt = 0.0`
- 0500P2_0526: `step 2000: loss = 166.2, umbilicus = 0.0, sym_dirichlet = 14.5, min_spacing = 0.0, track_radius = 151.6, track_dt = 0.0`
- 0500P2_0820: `step 0: loss = 11954.8, umbilicus = 6.6, sym_dirichlet = 2.7, min_spacing = 0.0, track_radius = 11945.5, track_dt = 0.0`
- 0009B: `step 0: loss = 7801.2, umbilicus = 10.2, sym_dirichlet = 6.4, min_spacing = 0.0, track_radius = 7784.6, track_dt = 0.0`

R (s.4) is not computed because no run completed. For the record only, 0343P's last/step-200 ratio is 14.5/884.0 = 0.016; this is **not** a PASS, the rule requires completion.

Out directories (`FIT_SPIRAL_OUT_DIR/<date>_<scroll>_slice-<z0>-<z1>_0-patch/`):

| scroll | files | non_liftable_patches.txt |
|---|---|---|
| 0343P | checkpoint_fitted.ckpt 607 777 233 B, non_liftable_patches.txt | 0 B |
| 0500P2_0526 | checkpoint_fitted.ckpt 977 409 297 B, non_liftable_patches.txt | 0 B |
| 0500P2_0820 | non_liftable_patches.txt | 0 B |
| 0009B | non_liftable_patches.txt | 0 B |

The checkpoints are periodic headless saves written before the kill; they are partial fits, not deliverables.

fit.log sha256: 0343P e56ceb90ab6c484e75e50da9057ea6649e893a892869a38e5847797cdb70e66d · 0500P2_0526 1ed64c6c606c7d16d8201a110e80be966bc0d0d37b62e46a7197a7ad5f34a052 · 0500P2_0820 5c36d4ea645e1cd90dbbca6901285130d480af6a7da3badf4383b93c29ad8103 · 0009B fe7718729e9bb5dc49d82821b7bcc01881df7c31369cee52bf842245f71342ba. chain.log sha256 7036fefe6bc1ee08301099abd0d12d993b6c26f8c6f3f7272d10376c97ed9155. Logs are kept locally under `/Volumes/Mac OS/vesuvius-scratch/fits_20261108/` and are available on request.

## Deviations from the PREREG, disclosed

1. **Crossings cache not used.** For all four scrolls the fitter printed that the published `.crossings.npz` was invalid ("tracks DBM has changed since the cache was built") and recomputed crossings natively. The PREREG described the published sidecars as inputs; in effect only the `.dbm` tracks were used. The recompute is the fitter's own code path, nothing of ours.
2. **s.8c implementation.** "Total loss at N ≥ at N−5000 for N ≥ 10000" was implemented as a comparison of the two single printed values at steps N and N−5000, checked at every multiple of 5000. This is what the PREREG says, and it is what fired.
3. **s.8d implementation.** "Free RAM < 2 GB" was implemented as macOS `vm_stat` free + inactive pages, sampled every 30 s. The PREREG did not define "free RAM"; this definition was chosen before any run started and is in `chain.sh`.

## Notes on the kill rules (observation, not a re-analysis)

- **s.8c fired on plateau noise.** Between steps 10 000 and 15 000 the 0343P total loss moved 15.5 → 14.4 → 12.5 → 17.9 → 11.7 → 22.1 at 1000-step samples; track_radius 8.9 → 4.7 → 5.2 → 7.7 → 4.2 → 14.5. The fit had converged by a factor of about 60 from step 200 and was oscillating; the rule compared two single samples and read the oscillation as divergence.
- **s.8d fired on machine-wide memory, not the fitter.** At the three s.8d stops the fitter process RSS was about 0.3 GB; other resident processes (a backup client at 3.4 GB, an indexer at 1.7 GB) and 17–18 GB of swap in use dominated. Unified-memory MPS allocations are not visible in RSS, so the fitter's true footprint during dataset load is unknown and may have contributed. Throughput fell with scroll size and pressure: 0343P averaged 1.1 it/s over 3 h 49 m, 0500P2_0526 0.6 it/s, 0500P2_0820 0.1 it/s, 0009B 0.0 it/s over its first 4 minutes.
- Neither rule distinguishes a broken fit from a noisy or busy machine. Any rerun needs a new, separately sealed pre-registration with rules that do (for example a 1000-step mean for s.8c and the fitter's own memory for s.8d). This file does not authorise one and nothing was relaunched.

## Secondary (s.7)

- Umbilicus loss direction: fell monotonically in every run that got past step 0 (0343P 13.5 → 0.2 → 0.0; 0500P2_0526 6.3 → 0.1 → 0.0). Consistent with the derived umbilicus being compatible with the tracks, exploratory only.
- No exploratory image was produced.

## Kill-rule and gate accounting

- Gate s.3: 4/4 passed (tracks loaded, finite step 0, all within 30 min).
- s.8a (no step line 30 min): 0 fires. s.8b (NaN/inf): 0 fires. s.8c: 1 fire. s.8d: 3 fires.
- Chain stop rule s.6 (first gate failure): not triggered; all four were launched.
