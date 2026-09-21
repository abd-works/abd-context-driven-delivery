## Language

*Actions* are first-order kits. You pass *Guidance* (or a string) and they run once per item — generate, document, scan, grill — so each practice does not reimplement the prelude.

### GuidanceAction

- Bind the list, optionally open a work session, run the operation, inject rules when that kit should. Subclass this; do not copy `run` / `open_workspace` onto the practice.

### GuidanceArg

- A list of Guidance, one Guidance (ref or `{toolset, …}`), or a string to act on directly.

Build order: `actions/scan` → `actions/document` → `actions/generate` → `actions/validate` → `actions/satisfy` → `actions/render` → `actions/partition` → `actions/grill_context` → `actions/sketch` → `actions/iterate` → `actions/improvement`

---

# actions
- **Purpose:** Give every practice the same slash kits (`/generate`, `/document`, `/scan`, …) so the practice owns words, not session plumbing.
- **Seam (terms):** GuidanceAction, GuidanceArg
- **Dependencies (one-way):** `harness/guidance_actions`

## Constraint

Slash names match the operation (`/grill`, not `/grill-context`). Inner helpers stay `@agent_instructions` only — they are not slash files. Echo and handoff live under `tools/`.

---

# actions/scan
- **Purpose:** Run a Guidance’s scanners over paths so rules fire on disk, not only in chat.
- **Seam (terms):** Scan, Scanner, ScannerCollection, RulesCollection, Rule
- **Dependencies (one-way):** `harness/guidance_actions`

## Constraint

`Scan` needs Guidance (or a collection bound from it) to know which scanners run. `/scan` lists Guidance; hosts call `self.scanner.scan(paths)`.

---

# actions/document
- **Purpose:** Record what already exists for listed Guidance without correcting it.
- **Seam (terms):** Document
- **Dependencies (one-way):** `harness/guidance_actions`, `actions/scan`

## Constraint

Flag violations; do not fix them. Write under the session (or the path the caller named).

---

# actions/generate
- **Purpose:** Write each listed Guidance’s artifact at its current fidelity.
- **Seam (terms):** Generate
- **Dependencies (one-way):** `harness/guidance_actions`

---

# actions/validate
- **Purpose:** Check artifacts against rules, or add a named rule from a failed example.
- **Seam (terms):** Validate, createRule
- **Dependencies (one-way):** `harness/guidance_actions`, `actions/scan`

---

# actions/satisfy
- **Purpose:** Validate, apply the implied fixes, validate again.
- **Seam (terms):** Satisfy
- **Dependencies (one-way):** `actions/validate`, `harness/guidance_actions`

---

# actions/render
- **Purpose:** Turn already-generated content into another format on that Guidance.
- **Seam (terms):** Render
- **Dependencies (one-way):** `harness/guidance_actions`

## Constraint

Bind hosts and convert. Do not open a session or commit a turn.

---

# actions/partition
- **Purpose:** Split source into an index plus verbatim segments, and fail a chunk that drops a named entry.
- **Seam (terms):** Partition, PartitionIndex, Segment
- **Dependencies (one-way):** `harness/guidance_actions`

---

# actions/grill_context
- **Purpose:** Interview the plan against files you have actually read, and persist each answer.
- **Seam (terms):** GrillContext
- **Dependencies (one-way):** `harness/guidance_actions`

## Constraint

Do not offer options until the cited context files are read. Answers go to `{path}/.context/grill-answers.md`.

---

# actions/sketch
- **Purpose:** Persist a rough draft through grill before generate, so the sketch is a file, not chat.
- **Seam (terms):** Sketch
- **Dependencies (one-way):** `actions/grill_context`

---

# actions/iterate
- **Purpose:** Grill, then generate one small validated slice per tick — not the whole artifact.
- **Seam (terms):** Iterate
- **Dependencies (one-way):** `actions/grill_context`, `actions/generate`, `actions/validate`

---

# actions/improvement
- **Purpose:** Open a repair on a Guidance and re-check the same scanner theme after the fix.
- **Seam (terms):** Improvement, repair, verify_fix
- **Dependencies (one-way):** `harness/guidance_actions`, `actions/scan`

## Constraint

`/repair` does not finish the session turn. Domain *Repair* on a work session is workspace, not this kit.
