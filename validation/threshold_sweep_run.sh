#!/bin/sh
# threshold sweep on Yupeng's probability volumes: uint8 cut = ceil(t*255) for t = 0.1..0.9
export W=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-wt/label-topology-audit/vesuvius/src
export PY=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa/vesuvius/.venv/bin/python
export B=https://dl.ash2txt.org/community-uploads/yupeng
export R=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/pred_audit/sweep
export TH=26,51,77,102,128,153,179,204,230
mkdir -p $R
cat > $R/jobs.txt <<J
m7 PHerc1447 12288:13056,3840:4608,3584:4352
soc PHerc1447 12288:13056,3840:4608,3584:4352
herc PHerc1447 12288:13056,3840:4608,3584:4352
m7 PHerc0814 9344:10112,2688:3456,2688:3456
soc PHerc0814 9344:10112,2688:3456,2688:3456
herc PHerc0814 9344:10112,2688:3456,2688:3456
J
xargs -P 3 -L 1 sh -c 'model=$0; scroll=$1; roi=$2; out=$R/${model}_${scroll}; mkdir -p $out; PYTHONPATH=$W $PY -m vesuvius.image_proc.run.label_topology_audit --label $B/${model}_${scroll} --threshold $TH --roi $roi --tile 256 --out $out > $out/run.log 2>&1; echo "$model $scroll rc=$? $(date +%H:%M:%S)" >> $R/run_sweep.log' < $R/jobs.txt
