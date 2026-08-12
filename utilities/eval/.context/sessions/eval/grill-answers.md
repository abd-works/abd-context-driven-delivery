# Grill answers — eval

## Perspectives (HARD GATE)

- **Asked:** Which perspectives should be active?
- **Answered:** BDD only (user selected `3`)
- **Deferred:** Stories, Modules, UX — may be added if a BDD sketch raises a question only those lenses can answer

## Theme selection — first menu rejected

- **Asked:** Reconstruct-first priority among (1) action trail (2) artifact deltas (3) mistake→correction (4) attributed cause
- **Answered:** Rejected. User does not prioritize those four; they feel waterfall-like and poorly partitioned.
- **Reframe:** Want robust logging first that makes the whole trace easy to see — **to / from / with**. Want that committed in GitHub with deltas for every action so trail+delta+history are essentially done. Existing system is mostly there; smarter **placement and linking**. Prefer more interesting orthogonal breakouts, not layered build order.

## Capability maturity (user partition)

Ordered capability rings — design may look ahead, implementation depth follows this order:

1. **Logging + traceability** — capture and place the trail (to/from/with, deltas, commits)
2. **Review / observe / report** — make the whole session easy to see and summarize
3. **Tactical root cause** — quick “what went wrong here” over the trail
4. **Deeper root cause** — richer attribution across changes (prompt / context / skill / hallucination, etc.)
5. **Formalized agent eval** — durable corpus and eval practice on closed history

First deepenable theme = ring 1. Later rings are consumers of ring 1’s placement/linking choices.

## What one logged/committed step is

- **Asked:** How big is one logged/committed step? (clarified “unit” = one durable record: one commit + one to/from/with entry)
- **Answered (v1):** Log when the AI chat is **ready to show something to the user** — not finer than that. User can’t see or comment on finer increments, so logging them has little point for v1.
- **Later (not v1):** Interim staged checks, analogous to a comic pipeline (character likeness across panels → style consistency → world-space sense, …). For this system: fidelity/stage pipeline (stories → BDD → OO/clean modules → DDD, …) and drift/consistency watches. User does not yet know what those stages/checks should be; wants help designing them — **after** reveal-level logging, not instead of it.

## What “ready to show” means

- **Asked:** Chat turn boundary vs lifecycle action done vs explicit review checkpoint vs turn-now/actions-later
- **Answered:** **1 — chat turn boundary.** Whenever the agent finishes a reply to the user, that reply is one reveal (whatever it showed in that message).

## Empty / non-judgable turns

- **Asked:** Always trail vs only on change vs trail-always/commit-on-delta vs skip unless artifact/decision
- **Answered:** **2 — only when something changed.** No trail entry and no commit if the working tree is clean.

## Process note

- User called out: grill questions must include a **recommendation** and brief rationale, not bare option lists.

## Where to / from / with lives

- **Asked:** commit metadata only vs session index+commit vs extend events.log+commit vs commit-enough-for-v1
- **Recommendation:** **2 — short session-folder reveal index + git commit**
- **Answered:** Agree — **all auditing lives in the session folder of the repo where the change is made**, because that repo’s git is already tracking the deltas.

## What happens to session audit after improve/fix

- **Concern:** Keeping every improve/fix trail in the working repo may bloat it.
- **Recommendation was:** **4 — stay in place for v1; selective promotion later**
- **Answered:** **3 — dedicated archive/eval repo; promote everything (or nearly) for long-term use** (overrode recommendation)

## When / what fidelity to promote into the archive

- **Asked:** mirror product git vs session folder+commit range vs session folder only vs continuous mirror
- **Recommendation:** **2 — session folder + linked commit range (SHAs / patch set); promote at session/improve close**
- **Answered:** **2** — archive owns the audit story via session folder + commit-range refs; not a wholesale product-repo clone; not continuous turn-by-turn mirror

## After promote, what stays in the working repo

- **Asked:** keep full session vs thin pointer+prune vs delete entirely vs defer prune
- **Recommendation:** **2 — thin pointer + prune bulky session-area audit**
- **Answered:** **2** — plus: spine should **link** to what changed (also in git), name **which tool** made it, include the **tool-repo branch/version** (tool is in a different repository), and link **file + change-repo commit/branch id**. Content/deltas via those links — not a second blob store in the session area.

## What the finished chat turn must have changed (XXX)

- **Answered:** the **working area** — `session.path` (durable tool root). Docs → `{path}/.context/` via `docs_dir`; modules → `{path}/`. Architecture triad: working area / session area (`session.folder`) / context index. Durable context-tool output changes the **working area**; the **session area** holds sprint/audit files and is not the change trigger.
- **Note:** Was wrongly left open — already specified in `utilities/workspace` module context + `session_guidance` + `docs_dir`.

## @log coverage on BaseContextTool (implemented, not sketched)

- First-order actions/tools now carry `@log`: `partition`, `grill`, `sketch`, `generate` (already), `document`, `iterate`, `validate`, `scan`, `satisfy`, `repair`, `improve`, `log_mistake`, `log_correction`.
- Left without `@log` (helpers / internals): `generate_fixes_from_validate`, `generate_output`, `add_generate_header_to_generated`, `verify_regression`, `archive_mistakes`.

## Language corrections

- Not “context-tool host” — a session is **started through a context tool** (`ensure_session` / `open` on that tool’s `Session`).
- Not a new top-level “a mistake recorded…” — **reuse `a session`** across themes; nest `that a mistake is pointed out` under it so themes connect.

## Tool-repo identity on the spine

- **Asked:** branch name vs commit SHA vs both vs semver for the tool repository
- **Recommendation:** **3 — tool-repo branch name + commit SHA**
- **Answered:** **3**

## Change-repo branch strategy

- **Asked:** stay on current vs one branch per session vs session+delta branches vs no policy
- **Recommendation:** **2 — one branch per session; corrections are more commits on that branch**
- **Answered:** **2**

## Which change-repo commit a mistake attaches

- **Asked:** HEAD vs artifact-blaming commit vs always pass commit vs HEAD+override
- **User:** Unclear what that meant — **mistakes go on the same branch / commit / session identity as the session itself** (not a separate blame puzzle).
- **Locked:** Mistake lives on the Turn / Session identity (same branch/commit world). No separate “pick an older commit” policy for v1.

## Cohesion — one Session hierarchy (supersedes parallel trail files)

- **User:** Prefer integrate over parallel activity; worried about dangling pieces; simpler is better; optimize later.
- **Locked:** Domain is hierarchical `Session → Turn → (tool call, context, mistake, prompt, result)`; correction links to a **later Turn**. Persist as **one YAML**. Drop separate spine / events.log / mistakes.log as the domain model (existing code may migrate).
- **Packages for this seam:** **`utilities/workspace`** + **`utilities/eval`**. Repair belongs under `eval/` if it only serves Session/Turn mistakes — modules must earn a separate package.

## Package placement (dependency analysis)

- **Locked:**
  - **workspace:** path / folder / open / ContextIndex / docs_dir
  - **eval:** Session YAML, Turn, ToolCall, Mistake, Correction, WorkspaceRepo, CDDRepo, ArchivePromoter, absorb repair
  - **leave:** record_decisions, scanners
  - **edges:** `eval → workspace` only
  - **names:** `workspace.Session` = locations; `eval.Session` = domain; Base: `self.workspace` + `self.eval`

## Open Turn / finish Turn (theme close)

- **Locked:** While the chat reply is in progress, Session holds one **open Turn**. Tool calls and mistakes attach there. On finish: dirty working area → commit, append Turn, save `{folder}/session.yaml`; clean → discard open Turn (no commit).
- **YAML path:** `{workspace.folder}/session.yaml`
- **Base attribute:** `self.eval`

## Theme status

- **Ring 1 capture + placement:** ready to code (see CE “First coding slice”)
- Archive promote, rings 2–5: scaffold

## Notes from ask (pre-theme)

- Complete traceability of changes without operator memory; context-tool runs should log automatically and track deltas
- Traceability across improve / correct / error lifecycle
- Root cause over the set of changes; failure may be skill, prompt, missing context, or hallucination — needs a failure taxonomy / attribution for evals
- Git/branch-per-session (and delta branches for corrections) proposed as cheap incremental history — open design path, not decided
- Long-term: robust corpus for evals and system improvement; short-term: considered integrated logging for quicker root cause
- Explicit: grill deliberately different design paths; high-level solution only after understanding; no code; no long dumps
