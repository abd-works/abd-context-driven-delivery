# edges-do-not-overlap-edges / edges-do-not-cross-other-edges

- **tool:** CleanEngineering (Drawio layout generator)
- **error:** Composition edges (Billing→Transaction, Billing→Invoice, Subscription→Bundle) shared the same horizontal highway and crossed.
- **rule:** edges-do-not-overlap-edges / edges-do-not-cross-other-edges
- **what changed:**
  - **Prose — no.** Those two routing rules were already in `drawio.md`. This repair did not add or rewrite them.
  - **Code — not in this eval loop.** `_route_waypoints` in `drawio_class_model.py` already uses 12px highway lanes and keeps edge-vs-edge checks on (`lane_sep = 12.0`, no wrap into `ROW_GAP`). That landed 2026-08-13 in commit `e9e5234`. The working tree has no further diff on that file.
  - **Product drawio — claimed, not a tool change.** The old `how` also said `domain-model.drawio` was regenerated from markdown. That is an artifact regen, not a context-tool edit.
