#!/bin/sh
# audit every public Scroll 1 segment; one process per segment, 4 at a time
# Environment variables (defaults in brackets):
#   R   output directory; results go in $R/all           [$PWD/out/placement]
#   W   villa checkout's vesuvius/src (PYTHONPATH)       [$PWD/villa/vesuvius/src]
#   PY  python with the branch's dependencies            [python3]
#   SEGMENTS  list of segment ids, one per line          [validation/scroll1_segments.txt next to this script]
R=${R:-$PWD/out/placement}
W=${W:-$PWD/villa/vesuvius/src}
PY=${PY:-python3}
SEGMENTS=${SEGMENTS:-$(cd "$(dirname "$0")" && pwd)/scroll1_segments.txt}
VOL=https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/volumes_zarr_standardized/54keV_7.91um_Scroll1A.zarr
mkdir -p $R/all
one() {
  id=$1
  [ -s $R/all/$id.json ] && return 0
  try=0; rc=1
  while [ $try -lt 3 ] && [ $rc -ne 0 ]; do
    [ $try -gt 0 ] && sleep 90
    PYTHONPATH=$W $PY -m vesuvius.image_proc.run.surface_placement_audit \
      --surface https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/paths/$id/$id.obj \
      --volume $VOL --samples 20000 --workers 4 --out $R/all/_$id > $R/all/$id.log 2>&1
    rc=$?; try=$((try+1))
  done
  if [ -s $R/all/_$id/$id.json ]; then
    mv $R/all/_$id/$id.json $R/all/$id.json
    mv $R/all/_$id/$id.samples.csv $R/all/$id.samples.csv
  fi
  rm -rf $R/all/_$id
  echo "$id rc=$rc $(date +%H:%M:%S)" >> $R/all/run_all.log
}
n=0
while read id; do
  [ -z "$id" ] && continue
  one "$id" &
  n=$((n+1))
  if [ $n -ge 2 ]; then wait; n=0; fi
done < "$SEGMENTS"
wait
echo "ALL DONE $(date +%H:%M:%S)" >> $R/all/run_all.log
