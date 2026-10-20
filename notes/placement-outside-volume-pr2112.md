# Does the placement audit catch a surface with a missing downscale factor? Partly (2026-10-20)

Villa PR #2112 reports that 112 of 323 published segments lack an
`original_volume_downscale` entry in the bucket catalog, so a consumer that
reads the intermediate normalized mesh without the factor places it at
1/4 (PHerc.Paris.4, PHerc0139) or 1/2 (PHerc0500P2) of its true coordinates.

## Setup

PHerc0139 segment `20260422000000-title_2026042222_zmid_flatboi`, two meshes
from the open-data bucket under `mesh/`:

| mesh | bbox x | bbox z | note |
|---|---|---|---|
| `intermediate/tifxyz_normalized/` | 2,291 to 3,771 | 8,233 to 9,893 | factor 4 missing |
| `20260422000000-on-20260102150214-2.399um.tifxyz` | 9,172 to 15,078 | 32,938 to 39,564 | published, factor applied |

Volume `20260102150214-2.399um-0.2m-78keV-masked.zarr` level 0, shape
76,953 x 26,511 x 26,511. Audit: 3,000 samples, seed 0, defaults otherwise.

## Result

| mesh | inside volume | no peak | contrast median | valid | offset median | abs > 2 | snap sd |
|---|---|---|---|---|---|---|---|
| normalized (wrong frame) | 3,000 of 3,000 | **1.00** | **0** | 0 | - | - | - |
| published | 3,000 of 3,000 | 0.45 | 84 | 1,645 | -0.5 | 0.55 | 0.44 |

The wrong-frame mesh is **not** outside the volume. The volume is large enough
that quarter-scale coordinates still fall inside its bounds, in masked empty
space. So `outside_volume_frac` is 0 for both and the outside-volume warning
never fires. What does fire is the profile itself: every sample reads a flat
zero profile, no peak anywhere, contrast 0.

Branch `30db2ad5a` adds the matching warning: when fewer than 5% of inside
points find a sheet peak, the audit says the surface is probably in the wrong
coordinate frame or paired with the wrong volume, with a test. The
outside-volume warning stays for smaller volumes, where the same mistake does
leave the bounds.

The published mesh shows the usual signature seen on Scroll 1: half the
samples more than 2 voxels off the sheet, snap sd 0.44.

Raw: `data/placement_pr2112_outside_volume.csv`.
