# Handoff — abd-context-driven-delivery (2026-08-29)

## Resume

- **Stage:** (unset)
- **Last work:** (see session progress below)
- **Next action:** defect-fix job 1 creates work session as default before start-ticket (wrong branch/worktree)
- **Next focus:** defect-fix job 1 creates work session as default before start-ticket (wrong branch/worktree)

## Turn Context

- **Noticed in:** current defect-fix / cli-agent triage session (2026-08-29)
- **Branch:** main (at time of defect — session created before start-ticket)
- **Cause window:** session attach runs before start-ticket in defect-fix job 1

## Artifacts to read

- `C:\dev\abd-context-driven-delivery\.context\context-index.md`
- `utilities/cli_agent/cli_agent.py` (`_ensure_work_session`)
- `utilities/cli_agent/job-templates/defect-fix.json`

## Request

**Focus:** defect-fix job 1 creates work session as default before start-ticket (wrong branch/worktree)

When the defect-fix template runs job 1 (triage + start-ticket), the work session is created BEFORE start-ticket runs. Since the git branch is still main at that point, `_ensure_work_session()` falls back to `default` instead of a session named after the defect/ticket. The session should be created on the correct branch, named after the defect, with its own worktree.

Repo: C:\dev\abd-context-driven-delivery
GitHub project board: abd-context-driven-delivery
This is a code + possible prompt change defect in cli-agent.


## Analysis

### Symptom
When `defect-fix` job 1 (triage + start-ticket) is launched via CliAgent, the work session is bound **before** the doer runs `/start-ticket`. At that moment HEAD is still `main` (no `session/*` branch), so `_ensure_work_session()` cannot derive a ticket session name from git and falls back to an existing/`default`-style session. The job queue, doer/judge binding, and logs therefore land under the wrong session. After start-ticket later creates the correctly named session branch and sibling worktree (`abd-cdd-<n>`), CliAgent remains attached to the premature session.

### Observed in this run
- CliAgent workspace: `C:\dev\abd-works-repo` with queue under `.context/sessions/default/`
- Defect repo: `C:\dev\abd-context-driven-delivery` / worktree `C:\dev\abd-cdd-41`
- After triage start-ticket for #41: session `defect-fix-job-1-creates-work-session-as-default-before-start-ticket-wrong-branch-worktree-41` on branch `session/...-41` in worktree `abd-cdd-41` — correct isolation, but created only by Workflow.start, not by CliAgent's first attach

### Call chain
1. `launch_next` → `launch_sessions`
2. `launch_sessions` → `_attach_cli_sessions` → `_WorkAttach.attach` → `_ensure_work_session()` **before** the doer process runs
3. `_ensure_work_session` name resolution:
   - `self._session` if set
   - else `_session_name_from_git()` — only when branch starts with `session/`
   - else sole existing work session name
   - else `_session_slug_from_folder()`
4. On `main`, step 2 returns `""`, so a leftover `default` (or folder slug) wins
5. Doer then runs backlog/start-ticket and creates the *real* ticket session + worktree — too late for CliAgent identity

### Context read
- `utilities/cli_agent/.context/module-context.md` — CliAgent owns JobQueue and spawns doer/judge; binds WorkSession for CLI identity; does not open the hanging Turn
- `utilities/cli_agent/job-templates/defect-fix.json` — job 1 requires start-ticket before analysis; does not instruct deferring session attach
- `.context/context-index.md` — workspace roots for bdd / clean_engineering / stories
- `utilities/workspace/workspace.py` — `open_work_session` / worktree isolation for non-default session branches

### History
- `db66b7fb` Add defect-fix job template
- `35a25b1a` Clarify prompt-vs-code diagnosis in defect-fix template
- `28dc95a2` Move cli-agent spawn logs into session folder
- `595ed119` Name session worktrees `abd-cdd-<n>` instead of full title
- Worksession/worktree open-close line established sibling worktrees for session branches

### Similar / related issues
- #31 Better queuing for CLI agent tasks (session identity / routing)
- #27 Immediate-fix workflow (backlog → start-ticket → fix → finish autonomy)
- #40 Attach transcripts on session close (session artifact lifecycle)
- Not duplicates — this defect is specifically premature `_ensure_work_session` on main during defect-fix job 1

### Expected
CliAgent work session for a defect-fix run should be created **on the ticket session branch**, named after the defect/ticket, with its own worktree — i.e. after (or as part of) start-ticket, not before while still on main.


## Diagnosis

### Category
**BOTH** — code failure plus prompt/template gap.

### Root cause hypothesis
`CliAgent.launch_sessions` always runs `_attach_cli_sessions()` → `_ensure_work_session()` **before** the doer process executes defect-fix job 1. Naming is:

1. explicit `session=` constructor arg
2. else `_session_name_from_git()` — only if branch starts with `session/`
3. else the sole existing work session name
4. else `_session_slug_from_folder()`

On `main` at job-1 launch, (2) is empty, so (3) reuses a leftover `default` (as seen in this run) or (4) invents a folder slug. The job queue, doer/judge PIDs, and logs bind there. `/start-ticket` then correctly creates `session/<ticket-slug>` + sibling worktree (`abd-cdd-<n>`), but CliAgent does **not** rebind to that session.

### Why this is not "just" a prompt bug
Even with a perfect job-1 prompt ("run start-ticket first"), CliAgent has already opened a WorkSession in-process before the doer can call Workflow.start. Prompt/template text cannot undo that attach order.

### Why this is also a prompt/template gap
`defect-fix.json` job 1 assumes start-ticket defines the session identity for later jobs, but does not state that CliAgent must defer session bind (or re-open on the new worktree) after start-ticket. `launch_next` also does not pass the job's `judge: false` into `launch_sessions`, so judge boilerplate is still appended when tools are listed.

### Exact seam to change
- Code: `CliAgent._ensure_work_session` / `_attach_cli_sessions` / `launch_sessions` ordering relative to start-ticket; possibly re-attach when git becomes `session/*` or when Workflow.start returns a new session path.
- Prompt: defect-fix job 1 (and CliAgent docs) should make deferred/rebind session semantics explicit for triage.

### Diagnose tool
Not used — cause is unambiguous from the call chain and reproducible naming rules; no ambiguous runtime signal remaining.

## Analysis

*(Added 2026-08-29 — session `fix-work-session-branch-isolation` / backlog FIRST isolation item. Separated from the earlier Analysis above.)*

### Scope of this backlog item

The required invariant is: **work session == `session/<name>` branch == own worktree**, for **CliAgent**, **SubAgent**, and **no-agent** flows — not only IDE CLI spawn. Opening or starting a work session must bind that triple **before any job runs**. After `/start-ticket`, the workspace root must **rebind** to the ticket worktree. Implementing on the current branch first; later backlog items depend on it.

Observed failure mode: open/start can leave doers on **main/parent** (e.g. `C:\dev\abd-works-repo`) so agents read/write the wrong tree.

### Context read

| Source | Takeaway |
| --- | --- |
| `utilities/cli_agent/.context/module-context.md` | CliAgent owns JobQueue, binds WorkSession for identity, does not open the hanging Turn. Constraint: do not bind durable session to leftover `default` on main before start-ticket; after start-ticket, rebind to `session/<ticket>` + own worktree. `_ensure_work_session` skips sole-session fallback when that session is named `default`. |
| `utilities/cli_agent/job-templates/defect-fix.json` | Job 1 (triage) requires `/start-ticket` then rebind, then stop. Prompt forbids durable bind on main / leftover `default`. Does **not** encode a mechanical defer of `_attach_cli_sessions` or an automatic post-start rebind of CliAgent workspace root. |
| `utilities/workspace/.context/module-context.md` | Non-default session branches isolate in sibling worktrees (`{abbrev}-{ticket}`). `start-work-session` must not be called from a `/cli-agent` parent — CliAgent opens session, switches path, binds doer/judge. |
| `utilities/workflow` `/start-ticket` (`start` → `open_ticket_session`) | Creates ticket-named WorkSession + session branch/worktree via Workspace. Correct isolation **for the ticket session**, but callers (CliAgent) may already be bound elsewhere. |
| `utilities/sub_agent` | SubAgent wraps context-tool work in `performTurn` when no actions; does not itself enforce ticket worktree rebind. Isolation depends on Workspace/Workflow/CliAgent seams. |
| Grill answers (workspace eval-consolidate; workflow package) | Workspace open/worktree policy and workflow backlog→start→finish lifecycle are locked separately; neither grill thread documents CliAgent pre-start bind / post-start rebind. |
| `.context/context-index.md` | Active roots for bdd / clean_engineering / stories — no extra isolation policy. |

No `grill-answers.md` under `utilities/cli_agent/`.

### Code seams (current checkout)

1. **`CliAgent._ensure_work_session`** (`utilities/cli_agent/cli_agent.py`): name = explicit session → `_session_name_from_git()` (only if branch starts with `session/`) → sole existing session **except** when named `default` → else folder slug. Then `open_work_session(name)`.
2. **`CliAgent.launch_sessions` / `launch_next`**: always `_attach_cli_sessions()` → `_ensure_work_session()` **before** the doer runs. On main at defect-fix job 1, git-derived name is empty → premature bind (historically `default`; now often folder slug).
3. **No rebind API**: after Workflow.start returns ticket session + worktree path, CliAgent does not retarget `_workspace` / session / doer cwd to that worktree.
4. **`WorkSession._ensure_session_worktree`**: correctly creates/attaches sibling worktrees for non-default session branches — isolation works **once** the right session is opened on the right branch.
5. **Partial fix already merged** (`afd51dd8` / `006fcfe1`): skip sole-session fallback for `default`; pass `judge: false` from job into `launch_sessions`. Specs: `cli_agent_spec.py` (not bind to `default`), `cli_agent_session_bind_agent_spec.py` (prompt/AI half). **Gap remains:** premature bind still happens (slug/`other`); **rebind after start-ticket** still missing; SubAgent/no-agent paths not covered by that CliAgent-only patch.

### Call chain (CliAgent defect-fix job 1)

`launch_next` → `launch_sessions` → `_attach_cli_sessions` → `_ensure_work_session` **before doer** → doer later `/start-ticket` → Workflow opens real `session/<ticket>` + `abd-cdd-<n>` → CliAgent stays on premature session/path.

### Broader than CliAgent-only

| Flow | Isolation risk |
| --- | --- |
| CliAgent | Premature `_ensure_work_session` on main; no post-start rebind of workspace root. |
| SubAgent | Relies on ambient workspace/session; no ticket worktree rebind of its own. |
| no-agent | Manual `/start-ticket` / `open_work_session` can still leave primary clone on main if session open does not retarget; operators can edit parent tree. |

Fix belongs at **work-session / start-ticket layer** so all three flows inherit the same bind+worktree+rebind contract — not only CliAgent spawn prompts.

### History

- `db66b7fb` Add defect-fix job template
- `35a25b1a` Clarify prompt-vs-code diagnosis in defect-fix
- `28dc95a2` Move cli-agent spawn logs into session folder
- `595ed119` Name session worktrees `abd-cdd-<n>`
- Worksession/worktree open-close line — sibling worktrees for session branches
- `006fcfe1` / `afd51dd8` — skip `default` sole-session fallback + judge:false pass-through (#41 partial)

### Similar / related issues

- **#41** — this ticket (premature default bind before start-ticket) — partial fix landed; broader isolation/rebind still open under this backlog framing
- **#31** — better CLI agent task queuing (session identity / routing)
- **#27** — immediate-fix autonomy (backlog → start-ticket → fix → finish)
- **#40** — attach transcripts on session close
- **#42 / #43** — CliAgent session log incomplete vs design (downstream of session identity)

Not duplicates of #31/#27/#40 — those are adjacent. This item is specifically **session==branch==worktree before jobs + rebind after start-ticket** across CliAgent/SubAgent/no-agent.

### Expected

Every new work session binds to `session/<name>` with its own worktree **before any job runs**. After start-ticket, workspace root rebinds to that worktree. Doers never remain on parent/main for ticket work. Holds for CliAgent, SubAgent, and no-agent.

### Residual gaps after #41 partial fix

1. Attach still runs before start-ticket (binds folder slug instead of `default`).
2. No automatic CliAgent (or shared) rebind to ticket worktree after start-ticket.
3. SubAgent / no-agent not covered by CliAgent-only prompt+`_ensure_work_session` tweak.
4. Prompt says "rebind" but there is no durable tool/API the doer can call that retargets CliAgent workspace root for subsequent jobs.


## Diagnosis

*(Added 2026-08-29 — session `fix-work-session-branch-isolation`. Separated from Analysis above. Supersedes the narrower pre-partial-fix Diagnosis for residual scope.)*

### Category

**BOTH** — production-code failure plus prompt/instruction gap.

### Root cause hypothesis

1. **Code (primary):** `CliAgent.launch_sessions` / `launch_next` always call `_attach_cli_sessions()` → `_ensure_work_session()` **before** the doer runs `/start-ticket`. On `main`, `_session_name_from_git()` returns empty. After the #41 partial fix, sole-session fallback skips leftover `default`, but naming still falls through to **folder slug** (or any non-`default` sole session). That opens a durable WorkSession in the **parent** checkout. `WorkSession._ensure_session_worktree` only isolates when the session branch is non-default — a premature session opened while HEAD is `main` does not move the doer onto `session/<ticket>` / `abd-cdd-<n>`.

2. **Code (missing rebind):** After `Workflow.start` / `open_ticket_session` correctly creates `session/<ticket>` + sibling worktree, **nothing retargets** CliAgent’s `_workspace` / bound session / subsequent job cwd to that worktree. Prompt text says “rebind”; there is no durable tool that performs it for the orchestrator.

3. **Prompt/template (secondary):** `defect-fix.json` job 1 and module-context tell the doer not to rely on leftover `default` and to rebind after start-ticket, but cannot undo in-process attach order, and do not define a mechanical rebind step shared by **CliAgent, SubAgent, and no-agent**.

4. **Cross-flow:** SubAgent and no-agent inherit isolation only via Workspace/Workflow. Without a work-session/start-ticket layer contract (bind `session/<name>` + worktree before jobs; rebind root after start-ticket), those flows can also remain on parent/main.

### Why not prompt-only

Even a perfect job-1 prompt cannot prevent `_ensure_work_session` from running before the doer process exists. The attach order is in production code.

### Why not code-only

Docs/templates already partially describe the desired policy; without explicit deferred-bind / rebind instructions (and tests for SubAgent/no-agent), agents will keep treating “session already open on main” as success.

### `/diagnose` tool

Not used — root cause is unambiguous from the call chain, `_ensure_work_session` naming rules, missing rebind path, and the residual behavior after the #41 partial fix.

### Exact seam to change (for later fix jobs)

- **Code:** Defer durable CliAgent session bind until after start-ticket (or bind only ephemerally); after start-ticket, rebind workspace root to the ticket worktree. Prefer implementing at work-session / start-ticket so SubAgent and no-agent share the contract.
- **Prompt:** Keep/extend defect-fix + module-context deferred/rebind language once the code seam exists; cover non-CliAgent entry points.

