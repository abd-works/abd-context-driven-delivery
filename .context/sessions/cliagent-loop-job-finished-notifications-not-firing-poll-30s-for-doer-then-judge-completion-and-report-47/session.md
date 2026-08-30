# Session: cliagent-loop-job-finished-notifications-not-firing-poll-30s-for-doer-then-judge-completion-and-report-47

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-47
- **goal:** CliAgent /loop job-finished notifications not firing; poll ~30s for doer then judge completion and report.
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Ticket ask

Parent `/loop` should poll about every 30s for doer then judge completion and **fire job-finished notifications** (report progress) so the operator is not left in a silent/idle monitor.

Issue state when analyzed: **CLOSED**, with disposition comments folding this into **#44**.

### Symptom (historical)

Under the **legacy** parent-driven contract:

1. Parent launches CliAgent (`launch_sessions` / queue).
2. Parent is told (`IdeCli._parent_checkin`) to watch with a **30s `/loop`** (Cursor) or check doer logs the usual way.
3. Expected: loop notices doer/judge completion and surfaces **job-finished** style notifications.
4. Observed: those notifications **did not fire** — parent monitor stayed quiet or never saw a clear completion signal even when work had moved on.

That matches the old design where **completion was a side-channel**: doer contacts judge, then someone must call `complete_job` (which is what writes `_CliAgentLog.job_finished`). If the doer never ran that protocol, or the parent only watched the wrong surface (transcript / console / Cursor notify), `job_finished` never appeared where the `/loop` expected it.

### What actually writes `job_finished`

Exact seam today:

- `_CliAgentLog.job_finished(...)` appends `{kind: "job_finished", index, prompt, ...}` to the session JSONL.
- **Only** `CliAgent.complete_job()` calls it (after `JobQueue.pop`).
- `run_backlog` calls `complete_job` on PASS (and on no-judge jobs) — so under the orchestrated path, `job_finished` is a **log event**, not a Cursor toast.

There is **no** CliAgent API that pushes an OS/IDE notification on `job_finished`. Launch report text tells the parent which files to **read** (`session log`, job queue, transcripts). Preferred Steps say: notify the user on `orchestrator_stopped`, `error`, or hard stall — by **reading the log**, not by a separate notify channel.

### Design shift after #44 (`5d6ec895`)

| #47 expectation | After #44 |
|---|---|
| Parent `/loop` polls ~30s and fires job-finished notifications | **Obsolete as control-loop design** — `run_backlog` owns doer→judge→`complete_job`→next in-process |
| Parent learns completion from a notification | Parent **reads session log** kinds: `orchestrator_started`, `doer_finished`, `job_finished`, `verdict`, `orchestrator_stopped`, `error`, `recovery` |
| Idle-less monitor via `/loop` | Idle-less ownership moves into CliAgent code; parent is minimal |

Issue disposition (author): *Close as superseded by #44. … Parent contract is launch once and read that log — not a notification `/loop`. If a Cursor-side toast on log kinds is still wanted later, open a new UX ticket.*

### Stale prompt seam still present

`IdeCli._parent_checkin` **still** says:

> if this is Cursor, watch with a 30s `/loop`; …

while `launch_sessions` Preferred Steps and module context say: launch `run_backlog` once, monitor the **session log**, unblock only on hard failure.

So even after #44’s code path landed on this tree, **legacy parent guidance** can still steer operators/agents toward a `/loop` notification model that CliAgent never implemented as toasts — and that #47 filed as “notifications not firing.”

That leftover text is a **prompt/doc drift** relative to Preferred Steps; it is not proof that a new parent-`/loop` feature must be built.

### Context read

- `utilities/cli_agent/.context/module-context.md` — `run_backlog` owns loop; parent monitors session log; `_CliAgentLog` kinds include `job_finished`
- `utilities/workspace/.context/module-context.md` — session/worktree isolation; Turn.finish commits
- No `grill-answers.md` under `utilities/cli_agent/.context/`
- Issue #47 body + disposition comments; #44 REOPENED for **live** reliability of the same loop
- Related analysis on #48 (same obsolete parent-`/loop` theme for idle-less)

### History

- `919cc997` / `54f0b674` — #42 session log header, chat/queue refs, `job_finished` summary/refs (log completeness the monitor needs)
- `046dfabf` — tools/actions, `ts_ms`, durations on log records
- `5d6ec895` — #44 `run_backlog` orchestration; diagnosis: missing in-process loop was the root, not better parent `/loop` prompts
- `24447de8` — merge #44 into cli-agent-fixes backlog branch

### Similar / related issues

- **#44** (OPEN/REOPENED) — resiliency / self-managed backlog loop / stall / minimal parent. **Supersedes #47’s control-loop ask.** Remaining work is live end-to-end reliability, not a separate notification poller.
- **#42** (closed) — session log completeness (`job_finished` summaries, header links) — prerequisite observability for “read the log”
- **#48** (related) — idle-less parent monitor folded into #44; remaining spawn/pickup on #49
- **#31** — queuing / routing adjacent; not the same notification defect

### Expected (for this ticket’s original ask)

Under current design, **#47 is not a missing 30s notification implementation**. Expected behavior is:

1. Prefer `run_backlog` so `complete_job` → `job_finished` is written by CliAgent code.
2. Parent monitors the session JSONL (paths from launch report) and reports on log kinds — especially `job_finished`, `orchestrator_stopped`, `error`.
3. Do **not** reintroduce a parallel parent `/loop` as the control plane.
4. Optional follow-up: align or retire `_parent_checkin`’s “30s `/loop`” wording so it matches Preferred Steps (prompt cleanup; may land under #44 hygiene).
5. Optional UX ticket later if Cursor toasts on log kinds are desired — out of scope for CliAgent control-loop defect-fix.

### Exact seams

- `CliAgent.complete_job` → `_CliAgentLog.job_finished` (sole writer)
- `CliAgent.run_backlog` → waits doer / judge → `complete_job` (orchestrated writer)
- `IdeCli._parent_checkin` — still advertises 30s `/loop` (stale vs Preferred Steps)
- `CliAgent.launch_sessions` Preferred Steps — correct “read session log” parent contract
- No code path emits IDE/OS notifications keyed to `job_finished`
