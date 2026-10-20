#!/bin/sh

cd /Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/label_quality/public_surfaces && PYTHONPATH=/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-wt/label-topology-audit/vesuvius/src /Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa/vesuvius/.venv/bin/python -m vesuvius.image_proc.run.label_topology_audit --batch /Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/label_quality/public_surfaces --out /Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/label_quality/public_surfaces/out
