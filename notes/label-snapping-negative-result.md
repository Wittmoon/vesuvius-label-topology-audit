# Label snapping: prototype with a negative real-data result

Side experiment, October 2026. Not part of the prize claim; recorded so that
nobody repeats it blind. The scripts are not released; the topology audit is.

## Question

Can a surface label be "snapped" to the CT edge it should follow, so that a
label or trace that has drifted a few voxels off the sheet is pulled back?

## What was built

- **v1:** per-voxel normals from the structure tensor of the smoothed label,
  oriented toward the denser side by a neighbourhood vote; a CT profile along
  each normal (+-3 voxels); target = strongest rising gradient; dense offset
  field; backward warp. Result: on the Kaggle crops the labels already sit on
  the rising edge (median -0.5 voxel from the strongest edge, consistent with
  "labels on the recto face"), so there is little to fix, and repeated passes
  do not converge: b1 climbs to 466-1108 after three passes. Neighbouring
  sheets are 4-8 voxels apart, so a +-3 search often finds the next sheet's
  edge, and a per-voxel field lets parts of a sheet move independently and
  tears it. Negative.
- **v2:** one robust (Huber-IRLS) offset field per connected sheet, a recto
  direction prior (sign only), a displacement cap at pinch points, an
  interpolating warp, a topology gate using `vesuvius.label_topology_audit`
  (b1 and b2 may not rise), and a contact gate so a moved sheet cannot touch
  another. On the 8 Kaggle crops with synthetic perturbations (rigid +-2 voxel
  shift, 2.5 voxel smooth drift) it recovers 39-52% of the perturbation
  (median), never raises b1, and 23 of 24 cases end closer to the original
  label. Without the prior it is negative on 2 of 2 crops tested: the CT-only
  orientation vote flips 8-63% of normals.
- **Real traced segment** (Scroll 1 segment 20230827161847, one 320^3 crop,
  prior = the mesh's own vertex normals): does not transfer. Shift +2 improves
  distance to the reference slightly (0.95 to 0.83), shift -2 gets worse
  (0.81 to 0.93), drift gets further from the as-traced surface (0.31 to 0.54).
  Only one sheet is labelled, so neighbouring layers give no gap cap, and the
  mesh and the CT disagree on which way is into the sheet for 30-39% of cells.

## What survives

- The prior is the load-bearing piece and has to come from something real
  (consistent mesh normals). A CT-only orientation vote is not enough.
- Whole-voxel forward moves tear 2-3 voxel sheets (about 1,300 handles per
  sheet); an interpolating backward warp does not.
- Handle blow-ups in early runs were sheets fusing, not tearing. A contact gate
  is needed for any refinement that moves labels.
- The topology audit's b1/b2 gate caught every one of these failures, which is
  why the audit, not the snapper, is the deliverable.

## If retried

Test on traced segments that actually drift, with mesh normals as the prior,
and score against independent retraces of the same sheet rather than against
synthetic perturbations.
