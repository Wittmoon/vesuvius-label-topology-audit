# Optimal-surface trace refinement: negative for sheet identity

Side experiment, October 2026. Not part of the prize claim; recorded so that
nobody repeats it blind. The scripts are not released; the audit is.

## Question

Does refining a traced segment with an optimal-surface solve on raw CT
intensity (single surface, or jointly with its inner and outer neighbour sheet
under a hard ordering) keep the trace on its own sheet?

## Setup

Scroll 1 segment 20230827161847, two 320^3 CT crops (origins zyx
10929,4586,3484 and 10752,2921,3569), 82-87k cells per crop on the trace's
own parameterisation, a +-6 to +-20 voxel search window along the trace
normals. Ridge spacing along the normals: median 12 voxels. Reference: cells
where at least three other public retraces of the same sheet agree to within
3 voxels (12,173 cells in crop 1, 21,830 in crop 2). "Wrong sheet" = more
than 6 voxels from that reference.

## Results, crop 1

| method | agrees within 2 voxels | wrong sheet | median / p90 error (voxels) |
| --- | --- | --- | --- |
| traced, untouched | 87% | 0% | 0.75 / 2.5 |
| single surface, raw CT, +-10, pull 0.1 | 68% | 2.8% | 1.2 / 4.2 |
| joint 3-surface, raw CT, pull 0.1 | 66% | 2.4% | 1.4 / 4.0 |
| single surface, raw CT, no pull | 38% | 20.4% | 2.7 / 7.8 |
| single surface, learned recto cost (face-shifted), +-10, pull 0.1 | 82% | 0.0% | 0.8 / 2.7 |

- Every raw-intensity refinement moves 2-20% of consensus cells onto another
  sheet. The joint solve is slightly better than its single-surface twin, but
  still worse than leaving the trace alone. All solvers move the trace onto
  brighter material; that does not make the move right.
- A learned recto-surface cost (a public 3D U-Net checkpoint trained on other
  scrolls) is far safer, but only after a global face shift of -6.5 voxels:
  the model marks the opposite face of the sheet from the one the tracers
  followed.
- Find-and-fix: using that cost to refine the five retraces that switch
  winding inside the crop recovers 57% of switched cells with 0.05% damage on
  the traces that were right, except for one 15k-cell switch onto a real
  adjacent sheet, which a local solve cannot repair (27% recovered).

## Results, crop 2: the crop-1 fixes do not carry over

- The face shift is -0.5 voxels, not -6.5, and the model barely responds
  (mean probability flat at about 60/255 along the normals, against a peak of
  160/255 in crop 1). The learned cost is now worse than raw CT.
- Find-and-fix fails: 12-49% recovered with 23-34% damage. The "switch" set
  here also contains cells where our own trace, not the retrace, is off the
  sheet, so the metric itself is unreliable.

## What survives both crops

The disagreement audit. Overlapping public retraces of one sheet, compared
along the trace normals with mesh connectivity (is the off-sheet patch part of
the same mesh component?) and a CT section check, separate three cases:
the retrace jumped to an adjacent real sheet (a winding switch), the retrace
sits in an inter-sheet gap, or our own trace is the one off the sheet. In crop
1 it found a 15k-cell winding switch in segment 20231007101619 and three
smaller retraces cutting through gaps, and no case of our trace leaving its
sheet. In crop 2 it found cases of our own trace running in a gap. A vote
alone is misleading at the window edge and where only one retrace exists;
connectivity plus a CT look is what makes it work.

## Decision

Raw-intensity optimal-surface refinement, single or joint, is negative for
sheet identity on this segment. A learned cost is crop-specific until the
face convention is handled explicitly. Do not tune further; the useful tool is
the audit that finds where traces disagree.
