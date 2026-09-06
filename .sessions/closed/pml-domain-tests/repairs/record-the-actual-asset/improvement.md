# record-the-actual-asset

- **tool:** Eval (Repair)
- **error:** `faultyAsset` / `repairedAsset` were a diagnosis of the problem (and of the redraw), not the file that had the problem — e.g. a Draw.io XML.
- **rule:** (process) log the actual asset
- **what changed:**
  - **Prose — yes.** `utilities/eval/log_mistake.md`, `log_correction.md`, `repair.md`, and eval/repair module contexts: `original` / `improved` are the artifact file contents; `wrong` is the diagnosis.
  - **Code — yes.** `Repair.log_mistake` / `log_correction` copy the file at `artifact` when it exists, and ignore a one-line diagnosis in favor of that file.
  - **Detector — no.**
  - **This session:** deleted `mistakes/edges-do-not-overlap-edges` and `mistakes/edges-do-not-cross-classes` — too late to recover the Draw.io files.
