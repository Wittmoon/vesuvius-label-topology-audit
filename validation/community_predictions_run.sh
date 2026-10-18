#!/bin/sh
# nine community prediction volumes x two scrolls, one shared 768^3 window per scroll, 256^3 tiles
export W=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-wt/label-topology-audit/vesuvius
export PY=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa/vesuvius/.venv/bin/python
export B=https://dl.ash2txt.org/community-uploads/yupeng
export R=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/pred_audit
{
for model in m7 soc herc; do for th in 0.2 0.3 0.5; do
  echo "$model PHerc1447 $th 12288:13056,3840:4608,3584:4352"
  echo "$model PHerc0814 $th 9344:10112,2688:3456,2688:3456"
done; done
} > $R/jobs.txt
xargs -P 4 -L 1 sh -c 'model=$0; scroll=$1; th=$2; roi=$3; out=$R/${model}_${scroll}_th${th}; mkdir -p "$out"; cd "$W" && PYTHONPATH=$W/src "$PY" -m vesuvius.image_proc.run.label_topology_audit --label $B/${model}_${scroll}_th${th}.zarr --threshold 1 --roi $roi --tile 256 --out "$out" > "$out/run.log" 2>&1; echo "$model $scroll $th rc=$? $(date +%H:%M:%S)"' < $R/jobs.txt
