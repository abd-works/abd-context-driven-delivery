# Session: defect-fix-job-1-creates-work-session-as-default-before-start-ticket-wrong-branch-worktree-41

## Start

- **date:** 2026-08-29
- **path:** C:\dev\abd-cdd-41
- **goal:** defect-fix job 1: work session created as default before start-ticket; should be named after defect on correct branch with own worktree
- **fidelities:** (unset)
- **contexts:** (unset)

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
