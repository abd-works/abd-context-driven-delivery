
## Analysis

### Symptom
When running `/sketch` then grill, or `/grill` alone, each next AskQuestion restates all previous answers. That recap confuses the operator. Answers already live in durable `{path}/.context/grill-answers.md`.

### Package / seam
- **Package:** `context_tools/actions/grill_context` (`GrillContext`)
- **Used by:** `/grill`, `/sketch`, `/iterate` (host grill body runs `grill_with_context`)
- **Primary instructions:** `grill_with_context` agent steps in `grill_context.py`

### What the guidance says today
1. **Step 2** — prove-read before asking, including **grill-answers** (and sketches, module-context, etc.).
2. **Step 3a** — frame the decision in 2–5 sentences: name the design-tree branch, **"state what is already agreed"**, name source files just read, ground options in those concepts.
3. **Step 5** — `write_grill_answer` immediately after each insight (persistence is correct and should stay).

### Why agents dump history into every question
- Step 3a’s **"state what is already agreed"** is read as “recap the interview so far.”
- Step 2’s prove-read of `grill-answers.md` supplies that history into the same turn.
- There is **no counter-instruction** such as: point at `grill-answers.md`; do not paste prior answers into AskQuestion.
- Result: framing + prove-read → full answer dump in every question prompt.

### Persistence vs prompt (not a storage bug)
- Durable file location (`docs_dir` → `{path}/.context/grill-answers.md`) is intentional (see commits `21ec43cd`, `ef2b1af2`).
- Defect is **agent framing guidance**, not where answers are written.

### Repo history (grill_context)
- `21ec43cd` — Keep sketches, generate, and grill-answers in `.context` (session.md/handoff stay under sessions).
- `ef2b1af2` — Retire consumed handoff; Step 2 wording still lists grill-answers as prove-read material.
- Step 3a “state what is already agreed” predates those moves and remains the smoking gun in current source (`grill_context.py` ~L110).

### Similar / related issues
- [#26](https://github.com/abd-works/abd-context-driven-delivery/issues/26) — this defect (theme:grill-context)
- [#14](https://github.com/abd-works/abd-context-driven-delivery/issues/14) — sketch/grill pause for review before next question (theme:sketch)
- [#29](https://github.com/abd-works/abd-context-driven-delivery/issues/29) — sketch/grill should create a turn after every tick (theme:workspace)
- [#32](https://github.com/abd-works/abd-context-driven-delivery/issues/32) — sketch rough after refactor (theme:sketch)

### Likely fix direction (for later jobs — not applied here)
Tighten Step 3a (and optionally Step 2 framing): keep grounding in *concepts from files just read*; **do not** restate prior grill answers in the question; cite `grill-answers.md` by path if needed. Add a mechanical/agentic BDD that fails when AskQuestion text contains prior answer bodies from grill-answers.

### Branch / session
- Branch: `session/stop-stuffing-prior-grill-answers-into-the-next-question-26`
- Worktree: `C:\dev\abd-cdd-26`
