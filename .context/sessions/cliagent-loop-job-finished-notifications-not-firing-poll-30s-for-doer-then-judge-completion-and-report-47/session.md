# Session: cliagent-loop-job-finished-notifications-not-firing-poll-30s-for-doer-then-judge-completion-and-report-47

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-47
- **goal:** CliAgent /loop job-finished notifications not firing; poll ~30s for doer then judge completion and report.
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Ticket ask

Original (one-line) ask: CliAgent **parent `/loop`** should poll ~**30s** for **doer then judge** completion and **fire job-finished notifications** / report. Symptom framed as those notifications “not firing.”

### Disposition already on the ticket (post-#44)

Issue comments close #47 as **superseded by #44**:

> After #44, `run_backlog` owns doer→judge→advance and writes `job_finished` / `orchestrator_*` / `verdict` to the session log. The parent contract is launch once and read that log — not a notification `/loop`.
>
> If a Cursor-side toast/notification on log kinds is still wanted later, open a new UX ticket; it is not a CliAgent control-loop defect.

So the product intent moved: **completion signal = session-log event**, not a parent-side notify/poll loop.

### Old design (what #47 was written against)

`IdeCli._parent_checkin` (still present in `cli_agent.py`) encodes the pre-`run_backlog` parent contract:

- After jobs are queued, **if Cursor, watch with a 30s `/loop`**; otherwise check the doer without `notify_on_output`
- Periodically inspect logs / transcript / hanging Turn / artifacts
- Stop on NOT TAKEN UP; on three judge FAILs revise prompt and one continue resume
- Parent must **not** drive the judge; doer runs the judge and waits

Under that model, “job-finished notifications not firing” means: the **parent monitor** never got a reliable completion signal when doer/judge finished — so the 30s loop stayed silent or never reported. There was no first-class CliAgent API that pushed a toast; completion was supposed to be inferred by the parent from logs/transcripts, and that inference was unreliable or undocumented.

### New design (after #44 / `5d6ec895`)

| Concern | Mechanism now |
|---|---|
| Who advances the queue | `CliAgent.run_backlog()` in-process (not parent `/loop`, not doer `complete_job`/`launch_next` prompts) |
| Doer done | `_wait_until_doer_turn_ends` → log `doer_finished` |
| Judge done | `_wait_for_verdict` → log `verdict` |
| Job complete | `complete_job()` → log **`job_finished`** (with optional summary/refs/tools/actions/duration from #42) |
| Orchestrator lifecycle | `orchestrator_started` / `orchestrator_stopped` (+ `recovery` / `error` on FAIL×N / stall) |
| Parent duty | Launch `run_backlog` **once**; **read the session log** paths from the launch report; unblock only on hard failure after orchestrator stops |

Preferred Steps on `launch_sessions` docstring match that: notify the **user** on `orchestrator_stopped` / `error` / hard stall by **reading the log** — not a 30s notify_on_output `/loop`.

### Where `job_finished` actually fires

Call chain on the preferred path:

1. `run_backlog` → `launch_next` → `job_started` + `launch_sessions` / `_spawn_worker`
2. Wait for doer turn end → `doer_finished`
3. If judge needed: write judge prompt, spawn judge, wait verdict → `verdict`
4. On PASS (or no-judge): `complete_job()` → **`_CliAgentLog.job_finished(...)`** then pop queue head
5. Loop until queue/backlog empty → `orchestrator_stopped`

On the **legacy** path (single `launch_sessions` without `run_backlog`), `job_finished` only appears if something calls `complete_job` (doer or parent). If the parent only polled and never completed the job, or never read the JSONL, “notifications” never appeared — even when the doer finished work.

`_CliAgentLog.job_finished` itself is solid (covered by #42 specs: summary, refs, tools/actions, `duration_s`). The gap #47 named was **not** “JSONL writer broken”; it was **parent observation / notify UX** under the old `/loop` contract.

### Why the old 30s `/loop` felt broken

1. **No push notification API** in CliAgent — only append-only session log + launch-report paths. A Cursor `/loop` with `notify_on_output` only fires if watched stdout matches; session JSONL growth is not that stream unless the parent explicitly tails the log file.
2. **`_parent_checkin` still says “30s /loop”** while Preferred Steps say “launch `run_backlog` once and monitor the session log” — leftover prompt text from the superseded design, which can still mis-steer a parent agent toward waiting for notify_on_output that never comes.
3. **Legacy doer-driven advance** required the doer to call `complete_job`; if the doer stopped without that, no `job_finished` row → parent poll saw silence (“notifications not firing”).
4. Related flake cluster (#48 / #49): NOT TAKEN UP / duplicate spawn can abort the parent monitor before any job_finished ever appears.

### Context read

- `utilities/cli_agent/.context/module-context.md` — `run_backlog` owns loop; parent monitors session log; `_CliAgentLog` kinds include `job_finished`
- `utilities/workspace/.context/module-context.md` — session folder / Turn finish; no grill-answers under cli_agent
- No `grill-answers.md` for cli_agent (none present)
- Issue #47 body + disposition comments; #44 body (resiliency / run_backlog); #42 session-log completeness; #48 idle-less fold notes

### History

- `5d6ec895` Own backlog orchestration in CliAgent code (#44) — `run_backlog`, `doer_finished`, orchestrator log kinds
- `919cc997` Fix #42 — session log header, chat/queue refs, `job_finished` summary/refs
- `_parent_checkin` 30s `/loop` text predates #44 and remains as legacy guidance string

### Similar / related issues

| Issue | Relation |
|---|---|
| **#44** (open / reopened for live reliability) | **Supersedes** this ticket’s control-loop ask; owns doer→judge→advance + log events |
| **#42** (closed) | Makes `job_finished` / header / refs observable enough for a parent that *reads* the log |
| **#48** (closed) | Idle-less parent monitor slice folded into #44; same obsolete `/loop` theme |
| **#49** (open) | Duplicate doer / NOT TAKEN UP — can prevent ever reaching `job_finished` |
| **#31** (open) | Broader queuing / routing — adjacent, not the notify defect |

### Expected (for this ticket’s remaining meaning)

Under current design, **#47 as a CliAgent control-loop defect is already addressed by #44 + #42**: completion is `job_finished` (and related kinds) on the session log; parent does not run a 30s notification `/loop`.

Residual work, if any, is **out of scope for this ticket’s original defect framing**:

1. **Prompt hygiene:** trim or relegate `_parent_checkin`’s “30s `/loop` / notify_on_output” so parents are not steered back to the superseded contract when using `run_backlog`.
2. **Optional UX:** Cursor toast on `job_finished` log kinds — new ticket, not CliAgent loop correctness.
3. **Live reliability of `run_backlog` / pickup** — tracked on **#44** / **#49**, not by reintroducing parent poll notifications.

### Exact seams (for later jobs)

- `_CliAgentLog.job_finished` / `complete_job` — writer path (already works when complete_job runs)
- `run_backlog` — preferred producer of doer_finished → verdict → job_finished
- `IdeCli._parent_checkin` — stale 30s `/loop` instructions vs Preferred Steps
- Launch report “Monitor with these files” — the actual parent observation surface
- No CliAgent API today that “fires” an IDE notification on job_finished

## Diagnosis

### Category
**BOTH** — a shipped code redesign (#44) plus leftover prompt/AI guidance that still steers parents into the superseded contract.

### Root cause hypothesis
The framed symptom (“job-finished notifications not firing” under a parent **30s `/loop`**) was never a broken `_CliAgentLog.job_finished` writer. That writer works when `complete_job()` runs (#42 coverage). The failure mode was **wrong completion observation surface**:

1. **Code / design (addressed by #44, not by a parent notify API):** There is no CliAgent path that pushes a Cursor toast/notify on job completion. Preferred completion signals are session-log kinds (`job_finished`, `doer_finished`, `verdict`, `orchestrator_*`) produced by `run_backlog` → `complete_job`. Under the old doer-driven path, if `complete_job` never ran, no `job_finished` row appeared — so a parent poll saw silence. After #44, the in-process orchestrator owns that chain; the parent contract is launch once and **read the log**, not poll for notify_on_output.

2. **Prompt / AI (still present):** `IdeCli._parent_checkin` still tells Cursor parents to “watch with a **30s `/loop`**” and contrasts that with “without `notify_on_output`” for non-Cursor — while `launch_sessions` Preferred Steps and module-context require monitoring the **session log**. That leftover instruction is the remaining defect on this ticket: it mis-steers parent agents to wait for a notification channel that CliAgent does not emit, so “notifications not firing” persists as an operator experience even when `job_finished` rows are written correctly.

### What is not the root cause
- `_CliAgentLog.job_finished` implementation bugs (writer is fine when invoked).
- Need to reintroduce a production-grade parent notification `/loop` as CliAgent control-loop correctness (ticket disposition: superseded by #44; optional Cursor UX toast is a separate ticket).

### Diagnose tool
Not used — cause is unambiguous from the analysis call chain, disposition comments, and the contradiction between `_parent_checkin` and Preferred Steps / `run_backlog`.

### Fix emphasis for later suites
- **Prompt/AI emphasis:** update or relegate `_parent_checkin` (and any matching parent docs) so `run_backlog` parents are told to read session-log kinds — not a 30s notify `/loop`.
- **Code emphasis (already largely shipped):** do not re-litigate `job_finished` writer; mechanical/agentic tests should lock the parent-guidance contract and that completion is observed via log kinds under `run_backlog`.
