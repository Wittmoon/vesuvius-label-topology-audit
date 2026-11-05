"""PREREG s.7 exploratory: link the 59 abs_winding.json points to the sealed
meshes (same linking code as dump_pairs.py) and write winding_id - wind_a per
point. No tolerance change, no claim."""
import csv
import json
import sys

sys.path.insert(0, '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-wt/winding-eval/spiral-fitting')
sys.path.insert(0, '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/winding_audit_20261104')
from eval_relative_windings import load_truth_meshes  # noqa: E402
from point_collection import load_point_collection  # noqa: E402
from dump_pairs import link_with_dist, W, TOL  # noqa: E402

meshes = load_truth_meshes(f'{W}/meshes')
cols = load_point_collection(f'{W}/inputs/abs_winding.json')
rows = []
for cid, col in cols.items():
    pids = list(col['points'].keys())
    pts = list(col['points'].values())
    for pid, p, (t, bw, bd) in zip(pids, pts, link_with_dist([p['p'] for p in pts], meshes, TOL) if pts else []):
        rows.append({'collection_id': cid, 'point_id': pid, 'z': p['p'][2], 'wind_a': p['winding_annotation'],
                     'linked_winding': '' if t is None else t, 'nearest_winding': bw, 'nearest_dist': round(bd, 4),
                     'offset': '' if t is None else int(t - p['winding_annotation'])})
with open(f'{W}/runs/abs_winding_points.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
print(json.dumps({'n_points': len(rows), 'n_unlinked': sum(1 for r in rows if r['offset'] == '')}))
