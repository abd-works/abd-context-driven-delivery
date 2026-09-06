# Rule: Document observed quirks until fix slice

**Scanner:** Manual review

On **brownfield / current-state** engagements, acceptance criteria describe **what the system does today**, including known defects. A quirk is **observed behavior** until a **change slice** explicitly approves a different outcome.

## DO

- Tag brownfield AC that encode legacy quirks with **`intent: observed`** in graph metadata or a leading comment in markdown export.
- Use **WHEN/THEN/BUT** for error and quirk paths traced from code — e.g. `BUT the client does not disconnect when SQLSTATE 24000 is ignored`.
- Separate **characterization AC** (must pass on current system) from **change AC** (must pass only after approved fix) — different stories or explicit slice labels.
- When a quirk is fixed in a change slice, **update or supersede** the observed AC — do not leave contradictory AC on the same story.

  **Example (pass):**

  ```
  WHEN the player enters game with a valid character slot
  THEN the system loads the character from the database
  AND forwards spawn to MapServer
  BUT SQLCloseCursor may return SQLSTATE 24000 without failing the flow (observed)

  --- change slice (separate story) ---
  WHEN DBServer closes the cursor after character load
  THEN no SQL error is logged for SQLSTATE 24000
  ```

  **Example (fail):**

  ```
  WHEN the player enters game with a valid character slot
  THEN the system loads the character from the database
  AND no SQL errors are raised
  ```

  Describes target behavior but claims to document current state. The 24000 quirk is silently "fixed" in the AC.

## DO NOT

- Write AC that describe **desired** behavior while claiming to document current state without labeling the slice as **change**.
- Silently "fix" legacy behavior in AC text during exploration on a characterize-only slice.
- Drop failure paths that code implements because they are inconvenient to test — note test gap in AC or war-room blocker instead.
- Use brownfield as excuse to skip **`use-but-for-negative-conditions`** — quirks still need explicit BUT/negative outcomes where relevant.
