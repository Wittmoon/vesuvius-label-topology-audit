# Pre-registration: 3rd-place surface model vs labels on ALL 892 Kaggle crops (written 2026-10-21 22:30 before any new prediction)

Why: the Challenge's 2026 open-problems page asks for active learning ("the model identifies the most
uncertain or valuable regions and asks humans to correct only those"). Our topology audit only queues
the 152 crops with holes; the other 740 are never looked at. This run builds the queue for all 892.

Model: same as kaggle3rd_prediction_preregistration.md (arunodhayan 3rd-place stage-1 `4000epochs_iter6_checkpoint_best.pth`,
tile 192, step 0.85, no mirroring, MPS). Same in-sample caveat: trained on most of these crops, so it
leans toward the labels. Disagreements that survive in-sample are the strong ones.

Outputs (disagreement.csv, candidates.csv (scratch; not shipped)):
- per crop: dice, label voxels, pred voxels, pred_far = pred voxels > 3 vox from any label voxel,
  label_far = label voxels > 3 vox from any pred voxel, both as counts and fractions, plus
  n_components and the largest component of pred_far; holed = in the 152 flagged set.
- per candidate: connected components of pred_far >= 200 vox, centre zyx, size, crop (the
  "model draws sheet here, label does not" spots).

What we read in the morning (descriptive, no hypothesis test):
1. the ranked queue: crops ordered by pred_far fraction; how many of the top 50 are NOT in the
   152-crop holed set (if ~0, the topology audit already found everything the model sees).
2. how concentrated the candidates are (crops with >= 1 candidate; candidates per crop).
3. a spot check of 10 candidates by eye in CT the next day, by the human, before any claim.

What this is NOT: evidence the labels are wrong. It is a proofreading order, same wording as the PR.
