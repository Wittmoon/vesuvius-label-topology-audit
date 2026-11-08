# PREREG: tracks-only spiral fits on MPS for four public scrolls with no organiser fit inputs (PHerc. 0343P, 0500P2 x2, 0009B)

Sealed 2026-11-08 (sha256 sidecar PREREG_trackfit_2026-11-08.md.sha256; input hashes in PREREG_trackfit_2026-11-08_code.sha256). After sealing nothing here changes; deviations go in RESULT_trackfit_2026-11-08.md.
This is a fit, not a reading and not an audit tool. Its deliverable is, per scroll, a derived umbilicus.json, a spiral-scroll.json, and a spiral-fitting run with the organisers' own fitter (ScrollPrize/villa spiral-fitting, main 2144fdd3f) on the organisers' own published tracks, plus the fitter's own quality numbers. "Fit did not converge" and "umbilicus derivation failed the gate" are both acceptable outcomes and are reported as such.

## 0. Prior knowledge in hand (disclosure)
- The public data folders for these four scrolls carry tracks (`*_surface_m7_L{0,2}_th0.2.dbm` with `.crossings.npz` and `.extract.json`) but no umbilicus.json and no spiral-scroll.json, so the organisers' fitter cannot be run on them as published. This lane supplies the two missing files and runs the fitter. No organiser fit, mesh, or winding annotation exists for any of the four, so there is no truth set to compare against and none is constructed.
- Pilot (not scored, disclosed): PHerc. 0846A, scan 20250728152254 L0 tracks, z 8760 to 9760, villa spiral-fitting at d8f22478 (PR #2393 branch), MPS, tracks-only, run 2026-11-07 and stopped by hand at step 800 of 30000 for timing. Logged: step 0 loss 2521.2 (track_radius 2520.0, umbilicus 1.0); step 200 loss 1430.4 (track_radius 1426.3); step 800 loss 665.1 (track_radius 646.0, umbilicus 0.1, sym_dirichlet 19.0). Speed about 1.2 it/s. non_liftable_patches.txt was empty (0 bytes) because no patches were used. Those numbers set the pass thresholds of s.4 and are the only fit numbers seen before sealing.
- Umbilicus derivation method (circle fit): for each horizontal track in a z slab, a Kasa least-squares circle; the slab umbilicus is the median circle centre over circles with arc span >= 60 degrees, residual <= 0.02 of radius (UMB_ARC=60, UMB_RES=0.02, UMB_MINC=1). Slabs are accepted while circle count n >= 20, centre MAD <= 450 px (800 px for 0009B, whose tracks are sparser and whose circles are wider, r 431 to 1537), and the centre jump from the previous slab <= 500 px; the walk stops at the first rejected slab. The first point is clamped to z_lo; a copy of the last accepted point is appended at last_z + slab/2 so the fitter's linear extrapolation (json_umbilicus_z_to_yx) becomes constant beyond the data. The method was validated once, on PHerc. 0332 against the organisers' published umbilicus.json: median 58.2 px, max 124.8 px over the compared z range. No other validation exists. In the fitter the umbilicus is a soft loss (loss_weight_umbilicus 1.25), not a hard constraint.
- Scale rule applied: dbm name "L2" means 4x downsampled tracks, so voxel_size_um = scan pixel size x 4 and base_shape_zyx = scan shape / 4; "L0" means native. 0343P: 2.215 um scan -> 8.86 um, base [5179, 3289, 3289]. 0500P2 20250526151718: 8.86 um L2, base_shape left unset. 0500P2 20250820143440: L0 9.362 um, base_shape left unset. 0009B: 2.401 um scan -> 9.604 um, base [7278, 7065, 7065]. spiral_outward_sense: 0343P "ACW" from the track crossing sense in extract.json; the other three come from the fitter's catalog if present, else the run fails at load and is reported.
- 0009B is flagged lower confidence before any fit: its accepted slabs have centre MAD 296 to 774 px, above the 450 px cap used for the other three. It runs last and its result is labelled accordingly whatever the numbers.
- Unknowns stated as unknowns: whether a tracks-only fit with no verified patches, fibers, or normals converges to a usable spiral at all on these scrolls (the pilot ran 800 of 30000 steps); whether 30000 steps on MPS finishes in the overnight window (ETA from the pilot speed: about 7 h per 1000 z); whether the fitter's catalog has a sense for 0500P2 and 0009B.

## 1. Hypothesis
H1: with the derived umbilicus and spiral-scroll.json, the organisers' fitter runs to completion on the published tracks and its track_radius loss falls by the same proportion seen in the pilot (s.4), i.e. the tracks alone constrain a spiral on these scrolls.
H0: the fit does not complete, diverges, or its track loss does not fall as in the pilot. Then the deliverable is the two input files plus the log showing where it stops, so whoever runs it next with more inputs starts from a known state.

## 2. Data (read only; no edits to any published file)
All under /Volumes/Mac OS/vesuvius-scratch/fits_20261108/<target>/dataset/. Tracks are hardlinks of the downloaded originals. sha256 of every input file is in PREREG_trackfit_2026-11-08_code.sha256.
- PHerc0343P_20260304131111: tracks PHerc0343P_20260304131111_surface_m7_L2_th0.2.dbm (16.7 MB) + .crossings.npz + .extract.json; umbilicus.json 5 points z 4500 to 5010; fit z [4500, 5010).
- PHerc0500P2_20250526151718: dbm (168 MB) + sidecars; umbilicus.json 6 points z 4500 to 5500; fit z [4500, 5500).
- PHerc0500P2_20250820143440: dbm (184 MB) + sidecars; umbilicus.json 7 points z 4500 to 5750; fit z [4500, 5750).
- PHerc0009B_20260319104112: dbm (468 MB, with -shm and -wal) + sidecars; umbilicus.json 12 points z 4500 to 7000; fit z [4500, 7000).
- Rule that fixed every fit z range before sealing: fit z range = the contiguous range of accepted umbilicus slabs, starting at 4500. Nothing else chose the ranges.
- Accepted umbilicus slabs (z centre, (y, x), n circles, MAD px): 0343P slab 170: 4585 (2214.8, 1396.5) 37, 127; 4755 (2308.3, 1104.7) 54, 59; 4925 (2311.5, 1077.1) 24, 86; rejected 5095 (jump 1709). 0500P2 0526 slab 250: 4625 (3197.6, 2784.2) 131, 132; 4875 (3229.8, 2872.2) 173, 146; 5125 (3438.2, 2838.3) 329, 215; 5375 (3643.8, 2675.8) 57, 161; rejected 5625 (MAD 572). 0500P2 0820 slab 250: 4625 (1316.5, 1067.7) 188, 126; 4875 (1227.2, 1184.5) 162, 109; 5125 (1201.5, 1215.6) 153, 185; 5375 (969.4, 1264.0) 176, 244; 5625 (966.2, 1078.1) 55, 233; rejected 5875 (MAD 538, jump 512). 0009B slab 250, cap 800: ten slabs 4625 (3655.5, 3306.0) 258, 669 through 6875 (4160.8, 2409.6) 114, 296; rejected 7125 (jump 627).
- Fitter: villa main-fit worktree, spiral-fitting at commit 2144fdd3f, unmodified. Python venv at /Volumes/Mac OS/vesuvius-scratch/mps_trackfit_20261107/venv (py3.14, torch MPS).

## 3. Gate (before any fit number is read)
- Each run must print "loading tracks from" and a "step 0:" line within 30 min of launch. If not, the run is killed and that target is reported as "did not start", with the log.
- step 0 track_radius must be finite and positive. NaN or inf at step 0 = input scale error: STOP that target, report, do not retune.

## 4. Statistic and decision (primary, per scroll)
- Inputs to the fitter: FIT_SPIRAL_CONFIG_OVERRIDES with z_begin, z_end as in s.2, input_use_tracks true, every other input_use_* false (verified_patches, fibers, fiber_directions, pcl_absolute, pcl_relative, pcl_same_winding, pcl_drawn_control_points, normals, gradient_magnitude, winding_inference, outer_shell). Default optimizer_num_training_steps 30000. FIT_SPIRAL_DEVICE mps. No other override. If a run is restarted it restarts from scratch with the same overrides; no resume, no tuning.
- Primary statistic: R = track_radius loss at the last logged step / track_radius loss at step 200 (the first logged step after the warm start, as in the pilot). Read from the fitter's own log line "step N: loss = ..., track_radius = ...". No code of ours touches it.
- Decision, read in this order:
  - run did not reach step 30000 (crash, kill rule s.8, or wall clock): INCOMPLETE; report last step, last loss line, and the reason. No pass/fail is claimed.
  - run completed and R <= 0.5 (pilot reached 0.45 by step 800 of 30000, so a completed run that cannot halve the step-200 loss did not fit the tracks): PASS on H1 for that scroll.
  - run completed and R > 0.5: FAIL for that scroll; the input files are still delivered with the log.
- Also reported beside R, from the same final log line, with no threshold: umbilicus, sym_dirichlet, min_spacing, track_dt, total loss; and the fitter's own end-of-run outputs (out dir listing, non_liftable_patches.txt byte count, which is expected 0 with no patches).
- One number per scroll, four scrolls, no pooling across scrolls, no interval claimed (a single deterministic fit has no sampling distribution to bootstrap; this is why the deliverable is the fit and the files, not a score).

## 5. Direction rule
Not applicable: there is no sign to decide. spiral_outward_sense is fixed in spiral-scroll.json before the run from extract.json (0343P) or the fitter's catalog (others). If the fitter rejects a sense at load time the run is reported as "did not start", not rerun with the other sense.

## 6. Compute plan
Sequential, smallest z range first, one fit at a time (36 GB RAM, MPS): 0343P (510 z), 0500P2 0526 (1000 z), 0500P2 0820 (1250 z), 0009B (2500 z). Each launched by its own run.sh under nohup with /usr/bin/time -l, log to fit.log beside the dataset. Expected speed about 1.2 it/s, so about 7 h for 30000 steps regardless of z (the step count, not z, sets the wall clock; memory scales with z). The chain stops at the first target whose gate (s.3) fails and the rest are reported as not run.

## 7. Secondary and exploratory (labelled, not deciding)
- Umbilicus residual check: after a completed fit, the fitter's umbilicus loss term at the last step compared with step 200. Direction only, no threshold.
- Visual: if a mesh or spiral sample is written to the out dir, one image per scroll for the RESULT, labelled exploratory. No letter, no ink, no winding count is claimed from it.
- 0846A (pilot scroll) rerun from main-fit with a sense probe is NOT part of this PREREG; if run it gets its own PREREG.

## 8. Kill rules
- No "step" line for 30 min after the last one: kill, INCOMPLETE.
- Any loss term NaN or inf after step 0: kill, INCOMPLETE, report the step.
- Total loss at step N >= total loss at step N-5000 for N >= 10000 (no fall over 5000 steps): kill, INCOMPLETE. Checked by eye from the log at the next look, not by a watcher.
- Machine falls below 2 GB free memory with the fit running: kill, INCOMPLETE, do not start the next target.
- Nothing from a killed run is retuned and relaunched under this PREREG.
