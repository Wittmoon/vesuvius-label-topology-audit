#!/bin/zsh
# Rerun chain per PREREG_trackfit_AMENDMENT_2026-11-14 (amended s.8c, s.8d; everything else as PREREG_trackfit_2026-11-08).
# Usage: nohup zsh chain2.sh > chain2.log 2>&1 &
F="/Volumes/Mac OS/vesuvius-scratch/fits_20261108"
TARGETS=(PHerc0343P_20260304131111 PHerc0500P2_20250526151718 PHerc0500P2_20250820143440 PHerc0009B_20260319104112)
ts(){ date "+%Y-%m-%d %H:%M:%S"; }
# mean total loss over the five printed lines at steps N-800..N (step lines print every 200)
mean5(){ local log="$1" n="$2" s=0 c=0 v k
  for k in 800 600 400 200 0; do
    v=$(grep -E "^step $((n-k)):" "$log" | tail -1 | sed -E 's/.*loss = ([0-9.eE+-]+).*/\1/')
    [[ -z "$v" ]] && return 1
    s=$(awk -v s="$s" -v v="$v" 'BEGIN{print s+v}'); c=$((c+1))
  done
  awk -v s="$s" 'BEGIN{printf "%.3f", s/5}'; }
# fitter physical footprint in GB (top MEM column; on Apple silicon this includes the process's MPS allocations)
foot_gb(){ top -l 1 -pid "$1" -stats mem 2>/dev/null | tail -1 | awk '{v=$1; gsub(/[^0-9A-Za-z.]/,"",v); u=substr(v,length(v)); n=v+0; if(u=="G")print n; else if(u=="M")print n/1024; else if(u=="K")print n/1048576; else print 0}'; }
# the launched pid is the /usr/bin/time wrapper; the fitter is its child
pypid(){ pgrep -P "$1" | head -1; }
killfit(){ pkill -TERM -f "fit_spiral.py --dataset ${1}/dataset"; kill "$2" 2>/dev/null; }
watch(){
  local log="$1" pid="$2" D="${1:h}" t0=$(date +%s) lastn=-1 lastt=$(date +%s) over=0 checked=0 peak=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 30
    local now=$(date +%s)
    local last=$(grep -E "^step [0-9]+:" "$log" | tail -1)
    local n=${last#step }; n=${n%%:*}
    local pp=$(pypid "$pid") fg=0
    [[ -n "$pp" ]] && fg=$(foot_gb "$pp")
    [[ -z "$fg" ]] && fg=0
    if awk -v g="$fg" -v p="$peak" 'BEGIN{exit !(g>p)}'; then peak=$fg; fi
    if awk -v g="$fg" 'BEGIN{exit !(g>=30.0)}'; then over=$((over+1)); else over=0; fi
    if (( over >= 2 )); then echo "$(ts) KILL s.8d(amended): fitter footprint ${fg} GB >= 30 GB on two consecutive samples"; killfit "$D" "$pid"; return 1; fi
    if [[ -z "$last" ]]; then
      if (( now - t0 > 1800 )); then echo "$(ts) GATE FAIL: no step 0 within 30 min"; killfit "$D" "$pid"; return 2; fi
      continue
    fi
    if [[ "$n" != "$lastn" ]]; then lastn=$n; lastt=$now
      (( n % 1000 == 0 )) && echo "$(ts) progress step $n footprint ${fg} GB peak ${peak} GB swap $(sysctl -n vm.swapusage | awk '{print $6}')"
    fi
    if (( now - lastt > 1800 )); then echo "$(ts) KILL s.8a: no new step line for 30 min (last step $n)"; killfit "$D" "$pid"; return 1; fi
    if echo "$last" | grep -qiE "nan|inf"; then echo "$(ts) KILL s.8b: non-finite: $last"; killfit "$D" "$pid"; return 1; fi
    if (( n >= 10000 )) && (( n % 5000 == 0 )) && (( n != checked )); then
      checked=$n
      local a=$(mean5 "$log" $n) b=$(mean5 "$log" $((n-5000)))
      echo "$(ts) s.8c(amended) check at $n: M=$a, M(-5000)=$b"
      if [[ -n "$a" && -n "$b" ]] && awk -v a="$a" -v b="$b" 'BEGIN{exit !(a>=2*b)}'; then
        echo "$(ts) KILL s.8c(amended): mean loss at $n ($a) >= 2 x mean loss at $((n-5000)) ($b)"; killfit "$D" "$pid"; return 1; fi
    fi
  done
  wait "$pid" 2>/dev/null
  echo "$(ts) peak fitter footprint ${peak} GB"
  if grep -qE "^step 29800:" "$log" && grep -q "maximum resident set size" "$log" && ! grep -q "Traceback" "$log"; then echo "$(ts) COMPLETED"; return 0; fi
  echo "$(ts) EXITED EARLY (process ended before step 30000)"; return 1
}
for t in $TARGETS; do
  D="$F/$t"; log="$D/fit_run2.log"
  if grep -qE "^step 29800:" "$log" 2>/dev/null; then echo "$(ts) $t: already complete, skipping"; continue; fi
  echo "$(ts) $t: launching"
  (cd "$D" && nohup zsh run2.sh > fit_run2.log 2>&1 &)
  sleep 15
  pid=$(pgrep -f "fit_spiral.py --dataset $D/dataset" | head -1)
  [[ -z "$pid" ]] && { echo "$(ts) $t: GATE FAIL: process not found after launch"; tail -5 "$log"; break; }
  watch "$log" "$pid"; rc=$?
  echo "$(ts) $t: rc=$rc; last: $(grep -E '^step' "$log" | tail -1)"
  if (( rc == 2 )); then echo "$(ts) chain stopped at first gate failure (s.6)"; break; fi
done
echo "$(ts) chain done"
