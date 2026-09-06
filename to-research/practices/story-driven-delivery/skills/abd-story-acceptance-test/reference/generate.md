# Generate — abd-story-acceptance-test

## Before writing code

1. **Declare structure first** — file / class / method hierarchy from story tree. See `reference/concepts.md` **Test organization**.
2. **Confirm language and framework** — ask if unstated. Defaults: pytest (Python), `node:test` (JS/TS), JUnit 5 (Java).
3. Pick matching file from `templates/` (`.py`, `.js`, or `.java`).

## Build order

One file per area, one class per story, one method per scenario. GWT helpers (`given_*`, `when_*`, `then_*`) match step text verbatim. Shared helpers → `tests/<epic>/<epic>_helper.py` when reused.

## Diagnose flip

After **2 consecutive failed fix attempts** on the same test — stop. Read `reference/diagnose.md` and run the full diagnose discipline before touching production code again. Do not proceed to the next story until resolved.
