# Session: cliagent-loop-robust-not-taken-up-no-duplicate-spawn-idle-less-monitor-48

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-48
- **goal:** CliAgent /loop robust: NOT TAKEN UP, no duplicate spawn, idle-less monitor
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Ticket ask (three requirements)

1. **Robust live-doer detection** — before spawning again, detect that a doer (or judge) is already live for the session resume ID.
2. **Failure-preventive status** — when spawn actually succeeded, do not surface `NOT TAKEN UP` / open a duplicate-doer window; return a clear status instead.
3. **Idle-less monitor** — parent `/loop` must not go silent/stuck; poll session log, job queue, transcripts; report job-finished and unblock (kick) when the doer stops advancing.

Related ticket: **#49** (duplicate doer when `NOT TAKEN UP` fires). Prior disposition (issue comments) folded (3) into **#44** and left (1)+(2) on **#49**, then closed #48. This session reopened #48 for defect-fix analysis because the backlog still carries it as `in_progress`.

### Symptom (still reproducible)

`launch_sessions` / `launch_next` → `_spawn_worker` always `Popen`s a new console, then `_await_pickup` polls the doer transcript for a new `"role":"user"` mark within `pickup_seconds` (default 12s). If the transcript does not grow in time — even when the new process started and is live — CliAgent raises:

`NOT TAKEN UP: the doer did not accept the new job. Do not wait. A live pid is not proof the Turn started.`

Callers (parent monitor, tool retry, or a second `launch_sessions`) treat that as “spawn failed” and launch again → **second console** for the same resume ID.

**Live evidence in this run** (same resume `1b35d2ae-…`, workspace `abd-cdd-cli-agent-fixes`):

- `cli-agent-doer.log` spawn `2026-08-30 00:42:44`
- second spawn `2026-08-30 00:43:03` (~19s later, same `--resume`)

That is exactly the false-negative pickup → retry → duplicate window failure mode.

### Call chain

1. `launch_sessions` / `launch_next` / `run_backlog` → `_spawn_worker`
2. `_spawn_worker` records `before = pickup.user_count(transcript)` for `work.cli_doer`
3. `IdeCli._launch_all` → `_spawn` → `_CliSpawner.start(..., existing_pid=...)`
4. **`_CliSpawner.start` ignores `existing_pid`** and always `subprocess.Popen(argv)` (new console on Windows via `CREATE_NEW_CONSOLE`)
5. `_record_cli_binding` stores the **new** pid over any prior pid
6. `_await_pickup(resume, before)` → `_Pickup.accepted` loops until `user_count > before` or deadline
7. On timeout → `RuntimeError(NOT TAKEN UP)` — no check that `results[0].pid` is alive, no check that an older doer pid is still the live session

### Why pickup false-negatives

`_Pickup.accepted` only watches transcript JSONL growth (`"role":"user"` count). It does **not** consider:

- process liveness of the just-spawned pid
- process liveness of `work.cli_doer_pid` / `existing_pid`
- session log `spawn` / `job_started` events
- whether the IDE attached the resume chat late (slow agent start, task-file read, Windows console focus)

So “spawn succeeded” and “pickup accepted” are decoupled. Spec text even encodes the inject-always policy: *“a CLI spawn when a doer pid is already alive … should still Popen so the new job is injected”* (`cli_agent_spec.py`). That intentional always-Popen plus a strict transcript gate is the flake.

### Requirement split vs #44 / #49

| #48 requirement | Status after #44 (`5d6ec895` `run_backlog`) | Where it lives now |
|---|---|---|
| Idle-less parent monitor / kick when doer stops | Largely **addressed in design**: `run_backlog` owns doer→judge→`complete_job`→next in-process; parent monitors session log (`orchestrator_*`, `doer_finished`, `verdict`, stall/`error`). `kick` remains for legacy doer-driven queues. | #44 (done on ticket branch; still “REOPENED” for live reliability) |
| Detect already-live doer before respawn | **Open** — `existing_pid` accepted on `_CliSpawner.start` / `_spawn` / `_launch_all` / judge spawn path, but **never read**; always `Popen` | #49 (and this ticket’s remaining surface) |
| NOT TAKEN UP when spawn actually succeeded | **Open** — same failure mode: false-negative `_await_pickup` → retry → second window | #49 |

So #48 is not “fully fixed by #44”; only the idle-less / ownership-of-loop slice moved. The pickup/duplicate spawn seam is unchanged on this worktree’s `utilities/cli_agent/cli_agent.py`.

### Context read

- `utilities/cli_agent/.context/module-context.md` — CliAgent owns JobQueue; `run_backlog` is preferred orchestrator; parent monitors session log; CliAgent does not open the hanging Turn; session==branch==worktree + `rebind_to_worktree` after start-ticket
- `utilities/cli_agent/job-templates/defect-fix.json` — job 1 start-ticket + rebind; job 2 analysis → session notes `## Analysis`
- `utilities/workspace/.context/module-context.md` — sibling worktree policy; Turn.finish commits
- `utilities/workflow/.context/module-context.md` — `/backlog` `/start-ticket` `/finish-ticket`
- No `grill-answers.md` under `utilities/cli_agent/.context/` (none present for this module)
- Issue #48 body + disposition comments; #49 open duplicate-doer ticket; #44 resiliency / `run_backlog`

### History

- `5d6ec895` Own backlog orchestration in CliAgent code (#44) — `run_backlog`, stall waits, judge-in-code
- Spec around `_Pickup` / `NOT TAKEN UP` and “still Popen when existing_pid alive” predate #44 and remain
- `07161e7d` Add kick tool — legacy unblock path still present
- Related merges: #41 session bind before start-ticket; #42 session log header/refs; #46 backlog hygiene / finish-ticket before advance

### Similar / related issues

- **#49** — duplicate doer when `NOT TAKEN UP` fires; `existing_pid` ignored — **same remaining code defect** as #48 requirements (1)+(2)
- **#44** — resiliency / self-managed loop / stall detection / minimal parent — covers idle-less ownership; still reopened for live reliability
- **#41** — premature `default` session bind before start-ticket (session identity; not pickup)
- **#31** — better queuing for CLI agent tasks (routing / identity adjacent)
- **#42** — session log completeness (observability the monitor should read)

Not duplicates of each other in title, but **#48 and #49 share one mechanical seam**: always-Popen + transcript-only pickup with no live-pid guard.

### Expected (for remaining defect)

Before opening another console for a resume ID:

1. If a doer/judge process for that session is already live (or the just-spawned pid is live and the job was injected), **do not** raise `NOT TAKEN UP` as a hard failure that invites immediate respawn — surface a distinct status (e.g. already-running / injected / pickup-pending).
2. `existing_pid` (and/or `work.cli_doer_pid`) must be consulted — either skip `Popen`, or inject without a second window, per an explicit policy that matches production IDE behavior.
3. Idle-less behavior for orchestrated runs continues to rely on `run_backlog` + session log (already landed under #44); do not reintroduce a parallel parent-`/loop` design unless live gaps in #44 remain after the spawn guard lands.

### Exact seams

- `_CliSpawner.start` — `existing_pid` unused; always `Popen`
- `CliAgent._await_pickup` / `_Pickup.accepted` — transcript-only gate; no pid/status synthesis
- `CliAgent._spawn_worker` — records binding then awaits pickup; failure path has no “pid alive ⇒ not a miss” branch
- Spec `cli_agent_spec.py` “should still Popen so the new job is injected” — documents current inject-always behavior; any fix must update that contract deliberately (code + tests), not only prompts
- Prompt/docs (`launch_sessions` Legacy Steps: “If NOT TAKEN UP, stop immediately”) — correct for true misses, but currently fires on false negatives and pushes callers toward retry/duplicate
