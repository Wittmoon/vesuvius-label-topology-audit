#!/bin/sh
# Score ink predictions on the validation (held-out-pixel) mask and write one CSV row each.
# usage: INK_ROOT=/path/to/ink_work PY=python ./ink_score_table.sh > ink_validation_scores.csv
# INK_ROOT holds predictions/<segment>_<variant>.tif and data/<dir>/labels/<prefix>_*.zarr
# (labels: hf://buckets/scrollprize/datasets/ink_9um/labels/aligned-scrollprizeorg-21slices/<prefix>/).
# Predictions are written by validation/ink_peak_window.py (window runs) or the released
# `vesuvius.ink_detection.inference.infer` (default window). Scoring: validation/ink_score.py.
: "${INK_ROOT:?set INK_ROOT}"; PY=${PY:-python3}
HERE=$(cd "$(dirname "$0")" && pwd)
echo "segment,variant,mask,auc,ap"
for spec in "w016 w016 pherc0139-w016" "0814-46527 0814-46527 pherc0814-46527" "1667-w029 1667-w029 pherc1667-w029"; do
  set -- $spec; seg=$1; dir=$2; prefix=$3
  for f in "$INK_ROOT"/predictions/${seg}_*.tif; do
    v=$(basename "$f" .tif); v=${v#${seg}_}
    out=$($PY "$HERE/ink_score.py" "$f" "$INK_ROOT/data/$dir/labels" "$prefix" --mask validation 2>&1 | tail -1)
    case "$out" in
      *AUC*) echo "$seg,$v,validation,$(echo "$out" | awk '{print $2","$4}')";;
      *) echo "$seg,$v,validation,NA,NA  # $out" >&2;;
    esac
  done
done
