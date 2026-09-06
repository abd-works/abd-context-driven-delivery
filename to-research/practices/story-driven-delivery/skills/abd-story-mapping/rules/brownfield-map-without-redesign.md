# Rule: Brownfield map without redesign

**Scanner:** Manual review

During **brownfield current-state** story mapping, the job is to **describe what runs today**, not to improve it. Refactors, renames, and target-state design belong in **change slices** after characterization tests exist.

## DO

- Map **observed** behavior only — including defects and quirks as stories or notes for AC (`observed` intent).
- Split **characterize** slices from **change** slices in narrative or thin-slicing — e.g. "Enter Game (as-built)" before "Enter Game (fix SQL cursor)".
- Stop and hand off quirks to **`abd-story-acceptance-criteria`** with explicit observed wording.
- Follow delivery strategy **`brownfield-current-state`** checkpoint: reviewer **`brownfield-boundary-gate`** before AC work.

  **Example (pass):** Map includes `(S) System --> Spawn Hero on Map` with note "MapServer cold start 1–2 min on tutorial zone (observed)" — fix deferred to change slice.

  **Example (fail):** Map says `(S) System --> Spawn Hero on Map Instantly` when current behavior takes 1–2 minutes — describes target, not reality.

## DO NOT

- Rename concepts in the map to "clean" domain language that does not match current UI/logs/code — use **`abd-domain-glossary`** if vocabulary needs curation.
- Omit known bugs because they are embarrassing — they are **documented behavior** until a change slice approves a delta.
- Combine **mapping** and **implementation fix** in one executor slot.
- Add stories that describe **target architecture** ("should use event bus") when the codebase does not do that today.
