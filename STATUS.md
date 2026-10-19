# Status

- 2026-10-18: branch `feat/label-topology-audit` pushed to the fork
  (https://github.com/Wittmoon/villa/tree/feat/label-topology-audit) and this
  packet published. Pull request to ScrollPrize/villa: pending (see below).
- 2026-10-18, later: zarr input landed on the branch (`a620aca9e`); the 6 hand-checked
  CUT holes filed as https://github.com/ScrollPrize/villa/issues/2144; negative-result
  notes added under `notes/`.
- 2026-10-18 17:20 local: PR opened as https://github.com/ScrollPrize/villa/pull/2147 (the earlier failures were the 3-open-PR limit for users without write access; #2131 is parked as a draft to make room).
- 2026-10-18 evening: announced in the Vesuvius Discord #show-and-tell: https://discord.com/channels/1079907749569237093/1162822163171119194/threads/1561558653746675742
- 2026-10-19: threshold sweep (nine cuts of the six probability volumes) added as `data/threshold_sweep.csv` with a README subsection; `code.patch` regenerated from the branch at 005887b3f (11 commits, now also the surface placement audit).
- 2026-10-19, later: surface placement audit run over all 255 public Scroll 1 segments, `data/scroll1_segment_placement.csv` + README subsection; `code.patch` regenerated at 49626183f (12 commits).
