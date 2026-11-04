# PREREG: title-template test, PHerc. Paris. 4, segment 20260623141924-w010-027

Sealed 2026-11-04 (sha256 sidecar PREREG_title.md.sha256; byte-identical copy in the evidence repo validation/). After sealing nothing here changes; deviations go in RESULT_title.md. Supersedes PREREG_title_DRAFT.md (unsealed; kept for the record).
This test can end in "control failed" or "uninformative, no title claimed". Both are acceptable outcomes and the expected ones if the region holds no ink signal the model can see.

## 0. Prior knowledge in hand (disclosure; none of it is a prediction)
- Ink map I: PHercParis4-20260623141924-2.4um-...-new_canon_autoresearch_recipe-tile256-stride128.tif, 44960 x 170160 uint8, 2.4 um/px (rows = v, 0-107.9 mm; columns = u, 0-408.4 mm; u = 0 outer end w027, right end inner w010; top edge ragged, 0.5-16 mm missing). sha256 in MANIFEST.md. Seen by eye at 16x overview only (ink_overview_16x_LOCAL_ONLY.png).
- Pyramids built by area average, hashed: I4 (9.6 um/px, u 0-217 mm only, 11240 x 22604) sha256 9f57ba4310337b68d3f9f3f08287e6b0f9fd81b08587aa4d440ce152eab6c8f6; I16 (38.4 um/px, full, 2810 x 10635) sha256 cce8e16d2f4b529045366160dfe6b00d33d7bf782f21364c8d46f8134acb4da9.
- Measured BEFORE sealing, on columns and gaps only (u < 207 mm); the search region R was never read at any resolution finer than the 16x overview and no template was ever rendered onto it:
  - Column edges (half-max rule, s.2): C1 u 3.23-43.40 mm, C2 u 58.68-119.58, C3 u 136.22-199.35. Gaps: G12 u 43.40-58.68 (15.27 mm), G23 u 119.58-136.22 (16.65 mm). Bottom band B: last text row at v 106.88 mm, B is 1.02 mm tall, too short for any window; B is dropped as a null region. There is no measurable gap G34 inside the analysed u range (the partial column 4 starts beyond 207 mm); G34 is dropped.
  - Deviation from the draft: the draft's 25%-of-median edge rule failed (gap floor is 55-60% of the column median, so no column splits); the rule actually used is half-max between the column median and the local floor of the adjacent gap, edges walked inward from the floor minimum. Both outputs are in out/preseal/edges.json.
  - Line pitch P (autocorrelation of the 5 mm high-passed row profile, v 20-100 mm, lags 1-8 mm, first peak with prominence > 0.2): C1 6.816, C2 6.730, C3 6.845 mm; one peak per column, prominence 0.71-0.81; no half-pitch peak above 0.02. Median P = 6.816 mm. Hence h = 0.6 P = 4.09 mm = 426 px at I4 = 106.5 px at I16; a = 0.75 h = 80 px at I16.
  - Seam: the 128-native-px (0.307 mm) inference seam is strongly present in the gaps (spectral power ratio at the seam period vs neighbouring frequencies: 59-260 along u, 61-80 along v). Correlation length L_corr (autocorrelation < 0.1): G12 0.528 mm, G23 0.826 mm, median 0.677 mm.
  - Exemplar bank (s.3.3) cut from C1 and C2 only: 785 components, 180 passed the size filter, 96 assigned. Letters with exemplars (n used): Ι 8 (64 assigned), Ρ 5, Υ 5, Γ 4, Χ 4, Η 3, Κ 2, Τ 2. The other 15 letters (Α Β Δ Ε Ζ Θ Λ Μ Ν Ξ Ο Π Σ Φ Ψ Ω) are FONT_FALLBACK. Ι absorbs 64 of 96 assignments, i.e. vertical strokes match it; this is a known weakness of the bank and is why the positive control is a gate. sha256 exemplar_bank.npz ce152bb6cec2a1e10da9e4ac68adc2391cc7077e58b17d4ba58fee7fbda0510d.
- Lane B: blank-papyrus FPR of this map = 0.763 (in-sample, CI 0.744-0.782). Lane C: morphology AUC 0.474 (CI 0.42-0.53). The map alone cannot be trusted; the positive control is mandatory.
- Prize page: the expected title region has shown no detectable ink so far, possibly a different ink, top rows physically missing (TITLE_PRIOR s.1). A null here is weak evidence against a title.
- Winding mapping (GP_COLUMNS_WINDING.md): the Grand Prize columns sit at windings 28-37; the end-title lies inward of them, i.e. in w010-027 (this segment) or in windings 0-9, which have no exported mesh. If the title sits in 0-9 this segment cannot contain it and a null here says nothing.
- Decoy titles of other Philodemus works were checked against published subscriptiones (s.5); one draft decoy (ΠΕΡΙΣΗΜΕΙΩΝ) was not attested in that form and was replaced.
- Overview-level layout: three full-height columns, a partial column 4 at u ~217-278 mm covering the top ~25 mm, a nearly empty region u 207-407 mm, v 27-106 mm. R (s.2) is declared with that knowledge, deliberately wide, not tuned to any feature.

## 1. Hypothesis
H1: the title region of w010-027 holds a Greek end-title whose letter pattern matches one of the pre-declared real candidate strings in I better than it matches any pre-declared decoy, and better than blank papyrus matches them.
H0: any real-vs-decoy difference is what texture alone gives.
Gate: s.3. Primary test and claim rule: s.6.

## 2. Data and regions (read only; no manual annotation)
- All scoring at I16 (38.4 um/px). The exemplar bank exists at I16 only; the draft's I4 refinement stage is dropped. Full resolution is read only for the final figure (s.8).
- Regions in mm (u, v), converted to I16 px by floor/ceil to whole pixels:
  - Columns: C1, C2, C3 as in s.0, v 20-100 mm.
  - Null regions N: G12 and G23 as in s.0, v 20-100 mm. (B and G34 dropped, s.0.)
  - Search region R: u 207-407 mm, v 0-107.9 mm minus the partial column-4 box u 217-278, v 0-25 mm.
- Held-out (secondary, reported beside the primary, no PASS bar): none available from the downloaded data (surface volumes are 45.5 um only). A different scan or model of the same segment with the candidate listing unchanged is required by the prize rules for any claim and is not part of this test.

## 3. Positive control (GATE; computed before any score in R exists)
1. P, h, a as measured in s.0 (median P = 6.816 mm; h = 106.5 px, a = 80 px at I16).
2. Bank T_bank = exemplar_bank.npz: 24 Greek capitals; where >= 2 exemplars exist the template is the mean of the top-K (K = 8) aligned exemplars, else the DejaVuSans letter blurred with sigma = h/20 (FONT_FALLBACK). Exemplar cut rule (run on I4, matched at I16): columns C1 and C2 only, v 20-100 mm; Gaussian smooth sigma h/20, threshold at the 80th percentile of column pixels, 8-connected components with bbox height in [0.5h, 1.4h] and width in [0.3h, 1.6h]; each component patch (bbox padded to h x 1.2h) scored by NCC against the 24 DejaVuSans letters at cap height h over translations +-h/8 and scales {0.9, 1.0, 1.1}; assigned iff NCC >= 0.45 and margin over the second-best letter >= 0.05; top K = 8 by NCC per letter; templates zero-mean, unit-norm, footprint = ink bbox + 0.1h margin. DejaVuSans.ttf sha256 3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22 (bootstrap classifier and fallback only).
3. Window score: for a window W (3P x 4a = 532 x 320 px at I16), per-letter NCC maps over W for every letter at rotations {-3, -1.5, 0, 1.5, 3} deg and scales {0.90, 0.95, 1.00, 1.05, 1.10}; max over letters, rotations and scales; greedy non-maximum suppression into non-overlapping h x 1.2h patches; score = mean of the best 12 patches.
4. Windows: positives = windows tiled at stride W/2 inside C3 ONLY (>= 60% of area inside the column box); C1 and C2 are excluded because the bank was cut from them. Negatives = windows wholly inside G12 and G23 at the same stride. With gap widths 15.3-16.7 mm and window width 12.3 mm each gap yields one column of about 7 windows, so n_neg is about 14; this is small and is stated here, not adjusted.
5. Statistic: AUC (Mann-Whitney) of window scores, positives vs negatives. Block bootstrap: a window's block id = (region, floor(v_centre / 3P)), i.e. non-overlapping 3P-tall bands per region; blocks resampled with replacement within positives and within negatives independently; 2000 replicates, seed 20261104, one generator; CI = 2.5/97.5 percentiles. Sensitivity: the same with 1.5P-tall bands, reported only.
6. Shape-specificity check: the same windows and score with a phase-scrambled bank (each letter's array phase-randomised in Fourier space with Hermitian symmetry, power spectrum kept, then zero-mean unit-norm; seed 20261104). Paired difference D = AUC_true - AUC_scrambled, same windows, same block resampling, same 2000 replicates.
Gate: PASS iff lower bound of AUC_true >= 0.80 AND lower bound of D > 0. Otherwise STOP: no score in R, RESULT_title.md records "control failed", no title claimed, no second attempt, no re-tuning of h, bank, window or stride.

## 4. Null for the title region (out of sample; not R, not lane B crops)
Chunked statistic (draft option i), identical on R and on N. Null tiles: non-overlapping tiles of 3P (v) x 4a (u) = 532 x 320 px wholly inside G12 and G23 (v 20-100 mm); about 7 per gap, 14 in all. R tiles: the same size, non-overlapping, wholly inside R. Null score per (string, layout, variant) per tile = the s.6.1 statistic maximised over anchors inside the tile. Pooled null = all null tile scores over all strings (RS and DS), layouts and variants.

## 5. Candidate set, decoys, layouts, grid (frozen; listing sha256 part of the seal)
Listing: out/listing/candidates_v1.json, sha256 4ff8c4058d996bb80e89f56ca16251ddf8b62cb3df1f090d784fd3b9bdbb1aec, generated by scripts/make_listing.py with numpy default_rng(20261104). Greek majuscule, no spaces, no diacritics, one sigma class.
Real set RS, 7 base strings x 2 variants (bare; numbered = one trailing free overlined letter slot scored as the best of the 24 letters plus an overline stroke of length a at 0.3h above the cap line):
 r1 ΦΙΛΟΔΗΜΟΥΠΕΡΙΜΟΥΣΙΚΗΣ (21), r2 ΦΙΛΟΔΗΜΟΥΠΕΡΙΚΑΚΙΩΝ (19), r3 ΦΙΛΟΔΗΜΟΥΠΕΡΙΡΗΤΟΡΙΚΗΣ (22), r4 ΦΙΛΟΔΗΜΟΥΠΕΡΙΠΟΙΗΜΑΤΩΝ (22), r5 ΦΙΛΟΔΗΜΟΥΠΕΡΙΘΕΩΝ (17), r6 ΦΙΛΟΔΗΜΟΥΠΕΡΙΘΑΝΑΤΟΥ (20), r7 ΕΠΙΚΟΥΡΟΥΠΕΡΙΦΥΣΕΩΣ (19).
 Probability mass outside RS (other Philodemus title, Chrysippus, other) is about 0.45 (TITLE_PRIOR s.5); a claim speaks only to RS.
Decoy set DS, 14 = 7 + 4 permutation decoys + 3 attested other-work titles:
 - permutations p1_r1..p1_r7 (one per base) and p2_r3, p2_r4, p2_r1, p2_r6 (second draw, four longest): rejected and redrawn if equal to the original or sharing any 3-gram with any RS string. Strings as listed in candidates_v1.json.
 - other-work titles (author + ΠΕΡΙ + topic, same convention as RS; real subscriptiones sometimes add ὑπόμνημα or τοῦ + book number, which RS does not model):
   d_orges ΦΙΛΟΔΗΜΟΥΠΕΡΙΟΡΓΗΣ (PHerc. 182 subscriptio, Indelli; Armstrong and McOsker SBL ed.),
   d_parrh ΦΙΛΟΔΗΜΟΥΠΕΡΙΠΑΡΡΗΣΙΑΣ (PHerc. 1471, Olivieri 1914; DCLP 62476),
   d_euseb ΦΙΛΟΔΗΜΟΥΠΕΡΙΕΥΣΕΒΕΙΑΣ (PHerc. 1428 subscriptio, Obbink 1996). Replaces the draft's ΠΕΡΙΣΗΜΕΙΩΝ, whose attested form is Περὶ σημείων καὶ σημειώσεων (PHerc. 1065).
 Decoys get the same two variants. |DS| = |RS| per variant and layout.
Layouts: L1 one line; L2 two lines split before ΠΕΡΙ (decoys split at the same index), left-aligned; L3 the same split, each line centred. Line spacing P.
Grid A: anchor translation step h/8; rotation {-3, -1.5, 0, 1.5, 3} deg; scale {0.90, 0.95, 1.00, 1.05, 1.10}; chunk slack +-0.5a. h is the only scale source.

## 6. Statistic and decision
1. Chunked NCC: a string in a layout is split into consecutive chunks of 3 letters (last chunk 1-3). Each chunk is rendered from T_bank (advance a, rotation and scale from A) as a zero-mean unit-norm template; its NCC map over the image is computed by FFT with local patch normalisation. For an anchor x, chunk score = max of the chunk's NCC map within +-0.5a of its nominal position relative to x, over rotation and scale. S(x) = mean over chunks of the chunk scores. The numbered variant adds the free slot as one extra chunk whose score is the max over the 24 letters with the overline.
2. Tile score t(string, layout, variant) = max over anchors x inside the tile of S(x); R score = max over R tiles and layouts, per variant. Null scores: s.4.
3. Null criterion: let Z = max of the pooled null (all strings, layouts, variants, null tiles; about 14 x 42 x 3 = 1764 values). A string "beats the null" iff its R score > Z. This is the strictest empirical quantile available; the implied family-wise chance of the best-of-n_R-tiles exceeding Z under H0 is about n_R_tiles / (n_pooled + 1), reported. The pooled p99 and the fraction of R tiles above it are reported as secondary only.
4. Margin M = (max over RS of R score) - (max over DS of R score), same layouts, grid and tiles.
5. Margin bootstrap: at the winning alignments of the best real c* and best decoy d*, the union of their chunk footprints is partitioned into L x L blocks (s.7); blocks resampled with replacement, S(c*) and S(d*) recomputed on the resampled pixels with alignments fixed; 2000 replicates, seed 20261104; M_boot = S(c*) - S(d*); 95% percentile CI. Fewer than 8 blocks in the union footprint: bootstrap inapplicable, result "uninformative".
6. CLAIM iff (a) the control PASSED, (b) lower bound of M > 0 at both block sides of s.7, (c) best real R score > Z, (d) no decoy R score >= best real and no decoy R score > Z. Otherwise "uninformative, no title claimed". There is no verdict stronger than "uninformative" against a title.
7. A claim is a lead only; it does not satisfy the prize (needs a low-distortion flattened surface, a programmatic image with scale bar, false-positive mitigation at large window, held-out validation on another scan or model with the listing unchanged).

## 7. Block side (fixed before any R pixel is read)
Primary L = 0.7 mm = 18.2 px at I16, used as 20 px (about twice the 0.307 mm seam period, as approved). Flag: 3 x L_corr = 2.03 mm exceeds L, so the primary interval may be too narrow; therefore a second block side L2 = 3 x L_corr = 53 px, used as 56 px, is also run and the claim rule (s.6.6b) requires the margin lower bound > 0 at BOTH. Chunk footprints are about 106 x 240 px, so a single chunk holds about 60 blocks at L and 8 at L2; the union footprint of a 17-22 letter string holds well over 8 blocks at either side.

## 8. Compute plan (Mac, no GPU, nice 10)
1. Control (s.3) on I16; scrambled-bank control on the same windows. Write control_result.json and the control section of RESULT_title.md. STOP if FAIL.
2. Only after PASS: chunk NCC maps on the I16 crop of R and on the null tiles for every distinct chunk x rotation x scale (chunks shared across strings are computed once); tile scores; Z; R scores; M and its bootstrap at L and L2.
3. Full resolution (2.4 um) read only at the winning alignment, one window of at most 5 x the template footprint, for the figure; no scoring change.

## 9. Secondary and exploratory (no decision weight)
Per-string, per-layout and per-variant R scores; per-tile maps; control AUC at the 1.5P block side; pooled p99 and R-tile exceedance fraction; score versus rotation; how often a decoy beats a real string per tile; the bank's per-letter exemplar counts versus which letters each string uses (RS strings lean on Φ Λ Ο Δ Μ Π Ε, all FONT_FALLBACK; this is disclosed, not corrected).

## 10. Kill rules
- Control FAIL: STOP, no R score, no second attempt.
- Any decoy >= best real, best real <= Z, M lower bound <= 0 at either block side, or < 8 footprint blocks: uninformative.
- Any deviation from this file is recorded in RESULT_title.md, never by editing this file.

## 11. What this does not test
Whether a title exists; whether the ink model can see the title ink; strings outside RS; layouts outside L1-L3; a hand different from this scribe's C1/C2 letters and the DejaVu fallbacks; windings 0-9 (no mesh). A null keeps the title question open.

## 12. Decisions closed (from the draft's DECIDE list)
A seam measured, not masked, blocks span two periods. B half-max edges (25% rule failed), B band and G34 dropped. C h/P = 0.6 fixed. D exemplar bank from C1+C2, DejaVu fallback, control on C3 only. E chunked statistic. F decoys verified, one replaced. G tile 3P x 4a, null max Z binding, p99 secondary. H L = 0.7 mm plus L2 = 3 L_corr, both must pass. I title inward of windings 28-37, may be unexported. J no held-out source available in this test. K numbered variant = one free overlined letter. L seed 20261104, listing candidates_v1.json, seal by sha256 sidecar then evidence-repo commit before any number.

## 13. Code frozen at seal
scripts/titlecore.py and scripts/control.py sha256 are listed in PREREG_title_code.sha256 beside this file and in the evidence repo; the versions hashed there are the ones run. Title-scoring code (s.6, s.8.2) is written only after the control result exists and its sha256 goes in RESULT_title.md; it must implement s.6 as written.
