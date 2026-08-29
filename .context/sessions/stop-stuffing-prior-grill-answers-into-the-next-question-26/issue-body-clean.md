# Handoff — abd-context-driven-delivery (2026-08-27)

## Resume

- **Stage:** (unset)
- **Last work:** (see session progress below)
- **Next action:** Stop stuffing prior grill answers into the next question
- **Next focus:** Stop stuffing prior grill answers into the next question

## Artifacts to read

- `C:\dev\abd-context-driven-delivery\.context\context-index.md`

## Request

**Focus:** Stop stuffing prior grill answers into the next question
Package: context_tools/actions/grill_context (used by /grill, /sketch, and /iterate).

When running /sketch then grill, or /grill alone, each next question restates all previous answers. That recap is extremely confusing. Persist answers in grill-answers.md as today; do not accumulate the whole interview into the next AskQuestion prompt.

grill_with_context Step 3a currently says to "state what is already agreed" in the 2-5 sentence frame. Combined with the prove-read of session grill-answers, the agent dumps the history into every question. Ask one focused question. Point at grill-answers.md if needed; do not paste the prior answers into the question.

## Analysis

### Symptom
When running `/sketch` then grill, or `/grill` alone (and iterate’s grill loop), each next AskQuestion restates all previous answers. That recap confuses the operator. Answers already live in durable `{path}/.context/grill-answers.md`.

### Package / seam
- **Package:** `context_tools/actions/grill_context` (`GrillContext`)
- **Used by:** `/grill`, `/sketch`, `/iterate` (host grill body runs `grill_with_context`)
- **Primary instructions:** `grill_with_context` agent steps in `grill_context.py`
- **Echo in sketch:** `context_tools/actions/sketch/sketch.md` — Frame step also says “restate what is already agreed in the sketch”

### What the guidance says today
1. **Step 2** — prove-read before asking, including **grill-answers** (and sketches, module-context, etc.).
2. **Step 3a** — frame the decision in 2–5 sentences: name the design-tree branch, **"state what is already agreed"**, name source files just read, ground options in those concepts (`grill_context.py` ~L110).
3. **Step 5** — `write_grill_answer` immediately after each insight (persistence is correct and should stay).
4. Behavior is **`@agent_instructions` only** — no mechanical guard against stuffing answer text into AskQuestion.

### Why agents dump history into every question
- Step 3a’s **"state what is already agreed"** is read as “recap the interview so far.”
- Step 2’s prove-read of `grill-answers.md` supplies that history into the same turn.
- Sketch’s Frame wording reinforces the same recap habit when sketch owns the loop.
- There is **no counter-instruction** such as: point at `grill-answers.md`; do not paste prior answers into AskQuestion.
- Result: framing + prove-read → full answer dump in every question prompt.

### Persistence vs prompt (not a storage bug)
- Durable file location (`docs_dir` → `{path}/.context/grill-answers.md`) is intentional (see commits `21ec43cd`, `ef2b1af2`).
- Defect is **agent framing guidance**, not where answers are written.

### Repo history (grill_context)
- `2f0b3871` (2026-07-31) — Step 3a “state what is already agreed” introduced (then under `utilities/grill_context`).
- `5149156a` (2026-08-12) — package moved to `context_tools/actions/grill_context`; wording unchanged.
- `21ec43cd` — Keep sketches, generate, and grill-answers in `.context` (session.md/handoff stay under sessions).
- `ef2b1af2` — Retire consumed handoff; Step 2 wording still lists grill-answers as prove-read material.

### Similar / related issues
- [#26](https://github.com/abd-works/abd-context-driven-delivery/issues/26) — this defect (theme:grill-context)
- [#14](https://github.com/abd-works/abd-context-driven-delivery/issues/14) — sketch/grill pause for review before next question (theme:sketch)
- [#29](https://github.com/abd-works/abd-context-driven-delivery/issues/29) — sketch/grill should create a turn after every tick (theme:workspace)
- [#32](https://github.com/abd-works/abd-context-driven-delivery/issues/32) — sketch rough after refactor (theme:sketch)
- [#34](https://github.com/abd-works/abd-context-driven-delivery/issues/34) — rename grill helper (theme:dummy-job2 / grill-adjacent)

### Likely fix direction (for later jobs — not applied here)
Tighten Step 3a (and sketch Frame / optionally Step 2 framing): keep grounding in *concepts from files just read*; **do not** restate prior grill answers in the question; cite `grill-answers.md` by path/heading if needed. Add a mechanical/agentic BDD that fails when AskQuestion text contains prior answer bodies from grill-answers.

### Branch / session
- Branch: `session/stop-stuffing-prior-grill-answers-into-the-next-question-26`
- Worktree: `C:\dev\abd-cdd-26`
- Local copy: `.context/sessions/stop-stuffing-prior-grill-answers-into-the-next-question-26/analysis.md`

## Diagnosis

### Hypothesis (concrete)
The defect is **instructional**, not a bug in `write_grill_answer` or AskQuestion tooling.

**Exact underlying issue:** `GrillContext.grill_with_context` Step 3a (`grill_context.py` ~L110) tells the agent to frame each question by **"state what is already agreed"**. That phrase is interpreted as a mandate to recap prior interview answers. Step 2 simultaneously requires prove-reading `grill-answers.md`, so the prior answers are in-context on the same turn. Nothing in Steps 3 / 3a / 3b says "cite the path only; do not paste answer bodies into AskQuestion." Agents therefore accumulate the whole interview into every next question prompt.

### Why not elsewhere
- Persistence path (`.context/grill-answers.md`) is correct and desired.
- AskQuestion itself does not auto-inject history â€” the agent authors the frame from Step 3a.
- Sketch/iterate wrappers call into this same `grill_with_context` body, so the defect appears under `/grill`, `/sketch`, and `/iterate`.
- `sketch.md` Frame step echoes â€œrestate what is already agreed in the sketch,â€ amplifying the same habit.

### Confidence
High â€” root cause is unambiguous from the Step 3a source text + observed agent behavior. `/diagnose` not required (cause is not ambiguous).

### Fix target for later jobs
Change Step 3a (agent instructions) so framing names the design-tree branch and concepts from files **just read**, points at `grill-answers.md` when needed, and **explicitly forbids** restating prior grill answers in the question text. Mirror the forbid in sketch Frame. Add failing BDD/agentic coverage that treats prior-answer paste as a defect.
