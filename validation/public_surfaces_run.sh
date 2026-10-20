#!/bin/sh
# Topology audit of the PHerc0139 prediction crops pulled by public_surfaces_pull.py.
# W = patched villa checkout (vesuvius/), PY = its python, R = folder holding the pulled crops.
set -e
W=${W:?path to the patched villa vesuvius/ checkout}
PY=${PY:-python}
R=${R:-$PWD/public_surfaces}
cd "$R" && PYTHONPATH="$W/src" "$PY" -m vesuvius.image_proc.run.label_topology_audit --batch "$R" --out "$R/out"
