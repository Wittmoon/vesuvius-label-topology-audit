# Pre-registration: precision of the disagreement queue by rank, with decoy tiles (written 2026-10-22, after staging, before any call)

Why: the first blind check (`kaggle3rd_prediction.md`) read 10 tiles from the top of the queue
with one reader and no control tiles. It says the top of the queue is real; it says nothing about
how deep the queue stays real, and nothing about whether the reader says NOT when NOT is right.

Staging (done 2026-10-22, `review_disagreements.py --stage-only --ranks 50,200,500 --limit 3
--decoys 1 --seed 20261022`, villa `da96928b8`): three crops from each of queue ranks 50, 200 and
500 (positions 50-52, 200-202, 500-502 of the 892-crop queue after excluding the 152 holed crops
and the 20 crops of the first two sittings), one candidate tile per crop, plus one decoy tile per
crop. Decoy kinds alternate across crops: `decoy_covered` = a point where label and model both say
sheet (truth: papyrus); `decoy_off` = a point farther than 3 vox from both (truth: not papyrus).
18 tiles, 9 candidates, 5 covered decoys, 4 off decoys, codes shuffled, no label or prediction
outlines on any tile. The reader sees `tiles/` and `contact_S01_S18.png` only; `key.csv` is withheld.

Question per tile: does the yellow marker sit on papyrus? Answers s (sheet) / n (not) / u (unclear).

What is read after the sitting (`review_disagreements.py --out spotcheck3`, tally per kind and rank):
1. Decoy accuracy: covered decoys called s, off decoys called n. Kill rule: if fewer than 7 of the
   9 decoys are called correctly, the reader's calls on this tile format carry no weight and the
   candidate results are reported as uninterpretable, not as precision.
2. Candidate precision per rank band (3 tiles each): count of s among scorable tiles at ranks ~50,
   ~200, ~500. With 3 tiles per band this is a trend read, not an estimate; it is reported as
   counts (x of 3), never as a percentage.
3. Unscorable (u, or marker visibly off the component) tiles are counted and excluded from the
   precision counts, as in the first sitting.

What this does NOT do: it does not change the shipped queue, it does not train anything, and the
reader is still the author. A second reader is the next step if the decoy rule passes.
