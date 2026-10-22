# Ink cross-check of #2167 gap meshes (scratch, not for commit). Written before any gap-sector computation.

Question: do w034/w036/w037 (and w035) lie on the same papyrus in the disputed 55-95 deg sector, judged by the
Challenge's ink predictions (recipe 20260417190342, full-res tif, 1 px = 1 level-0 voxel = 2.399 um; tifxyz grid step = 20 vox,
ink shape == 20 x grid shape for all five meshes, so ink (v,u) -> grid (v/20,u/20)).

Method (fixed now):
1. Ink -> grid cells by 20x20 block mean. Each valid, non-end-piece grid cell -> (angle about the umbilicus, z) with
   unwrap_gap/make_inputs conventions (umbilicus interpolated in z). Raster per mesh: angle 0.25 deg x z 100 um
   (41.684 vox); value = mean block-mean ink over cells in the bin (0..1); empty bin = NaN.
2. Pair statistic over bins both cover: Pearson r at zero shift, and peak Pearson over shifts of B within +-1 deg (+-4 bins)
   and +-200 um (+-2 bins). Minimum overlap 200 bins else NaN. Regions: gap 55-95 deg; rest = all other angles;
   control windows ctlA 130-170, ctlB 160-200 (the sweep's windows). Each split by z band: low 9000-15000, mid 15000-22000,
   high 22000-27800 vox, plus all.
3. Nulls: (a) different-winding control pairs, w033 vs w034..w037 outside the gap, and all pairs in ctlA/ctlB;
   (b) ceiling: one mesh, even vs odd grid rows split (same sheet, independent cells), zero shift;
   (c) shuffled-z: B's z rows randomly permuted (20 permutations) and B rolled in z by 3-10 mm (24 offsets), same shift search; report mean, 95th pct.
4. Coverage: fraction of covered bins with ink > 0.5, per mesh per region.
Decision rule (set now): a pair "shares ink" in the gap if its gap peak r exceeds the 95th pct of the shuffled-z null AND
exceeds the max peak r among different-winding control pairs in the same band; "does not" if below both control-pair mean+... i.e. within
the different-winding range. Anything between = indeterminate. Controls "separate" if the self-split ceiling is clearly above the
different-winding pair range.
Caveats stated in advance: ink model shared across meshes; ink prob on air/foreign sheet may be ~0 (low variance -> r unreliable, flagged by coverage); text lines are z-periodic so z-aligned structure can correlate across different windings (the z-roll null tests this).
