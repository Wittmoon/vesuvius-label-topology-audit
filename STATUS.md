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
- 2026-10-19 13:10 local: placement follow-up posted as PR #2147 comment (https://github.com/ScrollPrize/villa/pull/2147#issuecomment-6272805754) and in the Discord thread.
- 2026-10-19, later: `--cache DIR` chunk cache on the placement tool; `code.patch` regenerated at 1f0508001 (13 commits).
- 2026-10-19 ~15:00 local: ink render depth over all 29 ink_9um training segments (data/ink_render_depth.csv) and the peak-chosen inference window (validation/ink_peak_window.py): public w029 held-out AUC 0.775 -> 0.823 with no retraining; README subsection + negative-result note on per-column re-centring.
- 2026-10-19 ~16:00 local: peak-chosen window tested on the two other validation-mask segments (pherc0814-46527, pherc1667-w029): helps on one of three, hurts on 0814 where the best window is in the opposite direction; README subsection rewritten as a window-sensitivity finding plus a negative result for the one-read rule. Overnight queue running (all 29 renders default vs peak, 5-window sweeps, seed43 and step-050000 checkpoints, placement cache timing).
