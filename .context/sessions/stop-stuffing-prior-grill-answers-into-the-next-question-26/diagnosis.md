## Diagnosis

### Hypothesis (concrete)
The defect is **instructional**, not a bug in `write_grill_answer` or AskQuestion tooling.

**Exact underlying issue:** `GrillContext.grill_with_context` Step 3a (`grill_context.py` ~L110) tells the agent to frame each question by **"state what is already agreed"**. That phrase is interpreted as a mandate to recap prior interview answers. Step 2 simultaneously requires prove-reading `grill-answers.md`, so the prior answers are in-context on the same turn. Nothing in Steps 3 / 3a / 3b says "cite the path only; do not paste answer bodies into AskQuestion." Agents therefore accumulate the whole interview into every next question prompt.

### Why not elsewhere
- Persistence path (`.context/grill-answers.md`) is correct and desired.
- AskQuestion itself does not auto-inject history — the agent authors the frame from Step 3a.
- Sketch/iterate wrappers call into this same `grill_with_context` body, so the defect appears under `/grill`, `/sketch`, and `/iterate`.
- `sketch.md` Frame step echoes “restate what is already agreed in the sketch,” amplifying the same habit.

### Confidence
High — root cause is unambiguous from the Step 3a source text + observed agent behavior. `/diagnose` not required (cause is not ambiguous).

### Fix target for later jobs
Change Step 3a (agent instructions) so framing names the design-tree branch and concepts from files **just read**, points at `grill-answers.md` when needed, and **explicitly forbids** restating prior grill answers in the question text. Mirror the forbid in sketch Frame. Add failing BDD/agentic coverage that treats prior-answer paste as a defect.