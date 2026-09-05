# Rule: Story traces to evidence (brownfield)

**Scanner:** Manual review

When mapping **current-state / brownfield** behavior (see delivery strategy **`brownfield-current-state`**), every **story** in scope must trace to verifiable evidence. The story map is the behavioral spec — evidence makes that spec auditable.

## DO

- Record evidence on each in-scope story using **`evidence`** in story-graph metadata and/or an **`Evidence:`** line in `story-map.md` companion notes for that story.
- Accept evidence types: **source file + locator** (`Source/Client/charselect.c:412`), **existing test** (`tests/test_enter_game.py::test_spawn`), **log excerpt** (path + pattern), **config key** (`server/bin/...`), **chunk id** from context index (`ourowiki/85-AccountServer__chunk_02`).
- Trace **failure and alternate paths** when code or logs show them — map as `or` stories or note for AC phase.
- Use **`abd-semantic-context-chunker`** report to prioritize which files to read; confirm against **code**, not wiki alone.

  **Example (pass):**

  ```
  (S) Player --> Enter Game
      Evidence: Client/charselect.c:EnterGame:412; handoffs/enter-world.md
  (S) System --> Load Character from Database
      Evidence: Source/DBServer/loadchar.c:LoadCharacter:88; ourowiki/11-Data server db servers__passthrough.md
  or (S) System --> Show Connection Error
      Evidence: Client/charselect.c:445 (error dialog on send failure)
  ```

  **Example (fail):**

  ```
  (S) Player --> Enter Game
  (S) System --> Load Character from Database
  ```

  No evidence lines. Reviewer cannot confirm stories match code.

## DO NOT

- Add stories inferred from **class or function names alone** without tracing the flow (**Story Map from Existing Code** rule).
- Leave in-scope stories with **no evidence** when source code is available in the workspace.
- Treat wiki or memory chunks as sufficient without **confirming** against code or runtime logs when code exists.
- Put **`file:line` citations in epic or sub-epic titles** — evidence belongs in metadata or companion notes, not verb–noun names.
