"""Re-link every point of relative_windings.json to the sealed meshes with the
evaluator's own code and dump per-point and per-pair records (PREREG s.4/s.5
need pair detail; eval_relative_windings.py writes aggregates only).

Linking is identical to eval_relative_windings.link_points (same Patch.project
call, same min over meshes, same tolerance rule); the only addition is that the
best distance and best mesh are kept. Pair ordering is identical to
score_collection. Aggregates are recomputed and printed so they can be checked
against the sealed winding_audit_result.json.
"""
import csv
import json
import sys

import numpy as np
import torch

EVAL_DIR = '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-wt/winding-eval/spiral-fitting'
sys.path.insert(0, EVAL_DIR)
from eval_relative_windings import load_truth_meshes  # noqa: E402
from point_collection import load_point_collection  # noqa: E402

W = '/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/winding_audit_20261104'
TOL = 10.0


def link_with_dist(points, meshes, tolerance, chunk_size=8):
    zyx = torch.as_tensor(np.asarray(points, dtype=np.float32).reshape(-1, 3)[:, ::-1].copy())
    dists = torch.stack([m.project(zyx, chunk_size=chunk_size)[1] for _, m in meshes])
    best_d, best_i = dists.min(dim=0)
    out = []
    for d, i in zip(best_d, best_i):
        w = meshes[int(i)][0]
        out.append((w if float(d) <= tolerance else None, w, float(d)))
    return out


def main():
    meshes = load_truth_meshes(f'{W}/meshes')
    cols = load_point_collection(f'{W}/inputs/relative_windings.json')
    pt_rows, pair_rows = [], []
    n_pairs = n_exact = n_unlinked = 0
    for cid, col in cols.items():
        pids = list(col['points'].keys())
        pts = [dict(p) for p in col['points'].values()]
        links = link_with_dist([p['p'] for p in pts], meshes, TOL) if pts else []
        for pid, p, (t, bw, bd) in zip(pids, pts, links):
            p['truth'], p['best_w'], p['best_d'], p['pid'] = t, bw, bd, pid
            if t is None:
                n_unlinked += 1
            pt_rows.append({'collection_id': cid, 'point_id': pid, 'x': p['p'][0], 'y': p['p'][1], 'z': p['p'][2],
                            'wind_a': p['winding_annotation'], 'creation_time': p.get('creation_time', 0),
                            'linked_winding': '' if t is None else t, 'nearest_winding': bw,
                            'nearest_dist': round(bd, 4)})
        order = sorted(range(len(pts)), key=lambda i: (pts[i].get('creation_time', 0), i))
        spts = [pts[i] for i in order]
        ok = [p['truth'] is not None and np.isfinite(p['winding_annotation']) for p in spts]
        for a, b, oa, ob in zip(spts, spts[1:], ok, ok[1:]):
            if not (oa and ob):
                continue
            d_pred = int(b['winding_annotation'] - a['winding_annotation'])
            d_true = b['truth'] - a['truth']
            n_pairs += 1
            n_exact += d_pred == d_true
            pair_rows.append({'collection_id': cid, 'point_id_a': a['pid'], 'point_id_b': b['pid'],
                              'wind_a_a': a['winding_annotation'], 'wind_a_b': b['winding_annotation'],
                              'winding_a': a['truth'], 'winding_b': b['truth'],
                              'dist_a': round(a['best_d'], 4), 'dist_b': round(b['best_d'], 4),
                              'd_pred': d_pred, 'd_true': d_true, 'exact': int(d_pred == d_true)})
    for name, rows in (('points_all.csv', pt_rows), ('pairs_all.csv', pair_rows)):
        with open(f'{W}/runs/{name}', 'w', newline='') as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            wr.writerows(rows)
    print(json.dumps({'n_pairs': n_pairs, 'n_exact': n_exact, 'exact_step_share': n_exact / n_pairs,
                      'n_unlinked': n_unlinked, 'n_points': len(pt_rows), 'n_collections': len(cols)}))


if __name__ == '__main__':
    main()
