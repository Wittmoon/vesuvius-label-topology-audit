# RESULT_title — positive control (gate, PREREG_title.md s.3)

Date run: 2026-11-04. Prereg sealed first: PREREG_title.md sha256 in PREREG_title.md.sha256,
evidence repo commit 8ea6d8c (pushed before this run started). Code hashes verified against
PREREG_title_code.sha256 immediately before launch (titlecore.py OK, control.py OK).

## Verdict: FAIL. Lane stopped. No title-region score was computed.

Gate: PASS iff lo(AUC_true) >= 0.80 AND lo(AUC_true - AUC_scrambled) > 0 under both block sides.

| quantity | value | 95% interval |
|---|---|---|
| AUC_true (C3 letters vs G12/G23 gaps) | 0.928 | 0.864 - 0.975 |
| AUC_scrambled (phase-scrambled bank) | 0.975 | 0.940 - 0.998 |
| diff true - scrambled | -0.047 | -0.117 - +0.006 |

Windows: 69 positive (C3), 12 negative (G12, G23), 0 NaN. Score medians: letters true 0.472, gaps true 0.412;
letters scrambled 0.441, gaps scrambled 0.351.

Reading: the exemplar bank separates letter windows from gap windows, but a bank with the same power
spectrum and no letter shapes separates them better. The separation is image texture (energy, contrast,
spatial frequency), not letter form. The score therefore cannot distinguish "letters here" from "ink-like
texture here", and a title-region score built on it would be uninterpretable. This is the same failure
class as lanes B and C on dense_native, now shown at template level.

## Run
Command (from scripts/, data paths as args, python -I, nice 10):
control.py I16_full.npy exemplar_bank.npz edges.json pitch.json out/control_20261104
--px_mm 0.0384 --L_px 20 --L_px2 56 --columns C3 --gaps G12,G23 --rots -3,-1.5,0,1.5,3
--scales 0.90,0.95,1.00,1.05,1.10 --v_mm 20,100 --n_boot 2000 --workers 8
Wall time about 3 min on 4 busy workers.

Outputs (scratch/title_region_data_20261104/out/control_20261104/):
- control_result.json  1d261baa7c8d8a00a9eea3f41eeb4622d50370e141a47b85c5988775d82d9d43
- control_scores.csv   631bb63434b24b13e9a65caa1ce68a8d996545a64b98ba435fa62e9a1ee379f2
- run.log              5e7876e909d3bf8794c62b186fc749e966d4d33cc512d0303715b2f7e231009a
- control_LOCAL_ONLY.png (crop-derived, stays local)

## Deviations and observations (recorded here, prereg untouched)
1. Block bootstrap degenerated to a per-window bootstrap: 81 windows produced 81 distinct block ids under
   L=20 px, and the L=56 px run returned intervals identical to L=20. The window stride (160 px) exceeds
   both block sides, so no two windows shared a block. The intervals above are therefore narrower than a
   true spatial-block interval would be. A wider interval cannot turn this FAIL into a PASS (lo(diff) only
   falls), so the verdict stands; the prereg's "3P-tall bands" blocking was not what control.py implemented
   and this must be fixed before any future use of control.py.
2. control.py's command-line defaults for rotations, scales and gaps differ from the prereg; the prereg
   values were passed explicitly (see command above).
3. n_neg = 12 is small; the gaps are 9-13 mm wide against a 12.3 mm window, as the prereg anticipated.

## Consequence
Per PREREG_title.md s.3 and s.10: STOP. No scoring of the candidate region, no decoy comparison, no R.
The candidate list, bank and I16 image remain frozen and unused for scoring. Anything further (a better
exemplar bank, a contrast-matched null, a different detector) is a new pre-registration, not a rerun.

## Addendum 2026-11-04: blocking fixed, rerun. Verdict unchanged: FAIL.
User instruction: "fix and rerun". Fix: control.py block id is now (region, floor(v_centre / 3P)) exactly as
PREREG_title.md s.3.5 states, with 1.5P bands as the reported-only sensitivity; the L_px / L_px2 options
(which belonged to the s.7 margin bootstrap, not the control) were removed. titlecore.py unchanged
(57775813…, matches PREREG_title_code.sha256); control.py v2 sha256
3f3b4e6f390d7d22c10461e5bebc7af70bad274d14bb4659392c0ec3a4c4a1a1 (v1 ebf28307… kept in the first section).
Window scores are byte-identical to the first run (81 of 81 windows, both true and scrambled), so this is
the same test with the interval computed correctly, not a second attempt and not a re-tuning (s.3 gate text).

| quantity | value | 95% interval (3P bands) | 1.5P bands, reported only |
|---|---|---|---|
| AUC_true | 0.928 | 0.866 - 0.989 | 0.864 - 0.975 |
| AUC_scrambled | 0.975 | 0.934 - 1.000 | |
| diff true - scrambled | -0.047 | -0.107 - +0.013 | -0.101 - -0.001 |

Blocks: positives 4 (C3, 3P bands), negatives 6 (G12 and G23, 3 bands each). lo(diff) < 0 under both
bandings. Gate FAIL. Lane remains stopped; no title score computed.

Outputs (scratch/title_region_data_20261104/out/control_20261104_v2/):
- control_result.json  6b54b8a2904ea8ebf7e81ddb928cd08bdcea6740d8c772be2eece826635d5dbf
- control_scores.csv   7b1f441e326dcfce6f843413504d86af5df28876f679f98f190d618d59952489
- code_v2.sha256 (both scripts)
