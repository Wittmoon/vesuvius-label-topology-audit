# PHerc0139 issue #2167: polar unwraps at ChaseHendrick's 12 places, with the w033-w037 crossings

Date: 2026-10-22. Follows the placement-audit negative in `pherc0139_2167_placement.md`.
Asked for in https://github.com/ScrollPrize/villa/issues/2167 (ChaseHendrick, 2026-10-21): follow the
layers into the gap from where they are still separate, at more heights, to see which mesh is on which winding.

## What was made

For each of the 12 places in Chase's log (E1-E6, G1-G4, C1, C2; section "A look at the CT (Interpretation,
12 places)" of https://github.com/ChaseHendrick/Scrolls/blob/1243518dae102dd334ff1d7a63995f323c1095e4/docs/logs/2026-10-14-pherc0139-segment-defects.md)
plus his two unwrap heights (U1 = z 14,856, U2 = z 19,500, 55-95 deg), one z slice of the 2.399 um CT of
volume 20260102150214 read at level 1 (4.8 um/voxel, raw zarr v2 chunks over HTTP) and resampled on a polar
grid about the umbilicus (`20260102150214-umbilicus-20260826112529.json`, interpolated in z): angle over
place +-20 deg (U1/U2: 55-95 deg), one level-1 voxel per step in both axes.

Two renderings per place, `figures/pherc0139_2167_unwraps/<place>.png` and `<place>_rel.png`:
- absolute: rows = radius from the umbilicus (um);
- relative: rows = radius minus the radius of w033's crossing at that angle, -200 to +700 um, so the
  papyrus layers run roughly horizontal and the expected winding steps (about 100-115 um here) can be counted.

The five tifxyz grids (2.399 um copies of w033-w037) are cut at the slice: along each grid column the two
rows bracketing z are linearly interpolated, giving one point per column (about 48 um apart). Dots = the
main piece, crosses = the doubly traced end piece (same rule as `pherc0139_2167/make_inputs.py`: along the
circumferential grid axis the unwrapped angle exceeds 360 deg, and the farther-out overlap is the end).
Crossings are tabulated in `data/pherc0139_2167_unwrap_crossings.csv` (place, segment, theta_deg, r_um,
end_piece). Script: `validation/pherc0139_2167/unwrap_gap.py` (one CPU minute for all 14 at level 1, 1.6 GB
of chunks cached).

## What the figures show (read by eye on the relative renderings; one slice each)

| Place | What the slice shows |
| --- | --- |
| C1 (z 13,000, 150 deg, control) | Five traces on five separate layers, steps of 100-150 um, each trace on its own layer across the whole 40 deg. |
| C2 (z 22,000, 180 deg, control) | Each trace on its own layer; w036 and w037 ride a pressed pair at 170-200 deg. A 200 um void lies between w033 and w034. |
| U1 (z 14,856, 55-95 deg) | At 55-80 deg w034 and w036 lie on one band 100-200 um above w033, with w037 on the next layer 50-100 um further out. The end pieces of w036 and w037 (70-80 deg) lie on two separate layers 300-500 um out, and those are the layers the main w036/w037 traces run onto past 85 deg, where w035 appears between w034 and w036. |
| U2 (z 19,500, 55-95 deg) | At 55-75 deg w034, w036 and w037 all lie within one 100 um band about 450-600 um above w033, and the 400 um between w033 and that band is empty (no papyrus in the slice). Past 80 deg w035 appears on the band's outer face and w036/w037 climb onto their own layers, which continue back into the gap as their end pieces. |
| E1 (z 14,856, 35 deg) | w034 and w036 on one layer 100-150 um above w033; w037 on the next layer out; one layer between w033 and w034 carries no trace. |
| E2 (z 17,995, 360 deg) | Layers well separated. w034's main trace and w033 lie on neighbouring layers; w034's end piece runs along the inner face of the layer carrying w036; w037 on the layer outside w036. |
| E3 (z 21,500, 267 deg) | w034 lies on w035's layer (near its outer face) from 258 to 275 deg; w036 and w037 on their own layers outside. |
| E4 (z 10,437, 355 deg) | w034 and w036 share one dense band 80-200 um above w033 across 350-375 deg; w037 at 355 deg sits in the dark interval between two layers (air). |
| E5 (z 13,741, 4 deg) | w036 runs 30-50 um outside w034 in one band 150-250 um above w033; w037 on the next layer; a layer at about +100 um carries no trace. |
| E6 (z 14,109, 19 deg) | w034 and w036 on one layer; w037 on the next; the band between w033 and w034 carries no trace. |
| G1 (z 11,000, 50 deg) | w034 and w037 on one layer 120-150 um above w033; w036 on the layer just above w033 and at 52-58 deg on w033's own layer. |
| G2 (z 19,500, 15 deg) | w034 crosses from the layer next to w033 (at -5 to 5 deg) up onto w036's layer by 15-20 deg, and from there w034 and w036 run together; two layers between w033 and that band carry no trace from 10 to 35 deg. |
| G3 (z 23,000, 60 deg) | w034 and w037 on one layer at 40-58 deg; w036 on the layer at w033 (0-50 um); at 58-66 deg w036 and w037 both climb through air across one or two layers onto layers 300-600 um out, where w035 appears. |
| G4 (z 26,800, 35 deg) | w034's end piece runs just inside w037's layer (450-520 um) for 15-35 deg; w034's main trace and w033's end piece share the band 100-250 um; w036 in between at 300-350 um. |

Reading across the places: outside the gap (C1, C2) each trace has its own layer. Inside the gap the traces
w034, w036 and w037 crowd onto one or two layers while one or two layers between w033 and that band carry no
trace (E1, E5, E6, G2, U1, U2), the end pieces of w036/w037 at the gap's edge lie on the layers that their main
traces leave (U1, U2), w034 changes layer within a slice (G2, G3), and w037 runs through air (E4, G3). This is
the same picture Chase drew from his 12 places and two unwraps; it is produced here by independent code at
4.8 um, and it extends his two unwraps to all 12 heights.

## Limits

One z slice per place, layers counted by eye, 4.8 um voxels; thin strands may be split plies; the trace
points are 48 um apart so offsets under about 12 um are within their accuracy; the relative rendering
follows w033, so where w033 itself wanders (G4 after 35.5 deg, where the w033 reference switches piece) the
rows jump. No layer was tracked continuously from the control sector into the gap; that would be the
decisive version (a per-angle count of material runs between w033 and w037 against the four expected steps,
over every height), and it is not done here.
