# Session: cliagent-resiliency-self-managed-backlog-doer-judge-loop-stall-detection-minimal-parent-44

## Start

- **date:** 2026-08-29
- **path:** C:\dev\abd-cdd-44
- **goal:** CliAgent resiliency: self-managed backlog/doer/judge loop, stall detection, minimal parent; tools via manifest fence.
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Symptom

CliAgent defect-fix runs on `cli-agent-fixes` require the **parent** (outer agent) to babysit the pipeline: kick `complete_job` / `launch_next`, respawn after NOT TAKEN UP, recover from BOM/JSON parse failures, and notice stalls by eye. The stated contract is the opposite: **CliAgent owns** backlog → queue → tools (manifest fence) → doer → judge → complete → next → error capture → stall recovery; the parent only launches, reads the session log / CLI terminal when notified, and unblocks hard failures.

Observed failure modes (issue #44 + live `cli-agent-fixes` session log):

1. Doer finishes a job but does not call `complete_job` + `launch_next` → queue stuck; parent improvises.
2. **NOT TAKEN UP** / duplicate spawns / stale pids → parent respawns or rewrites `cli-agent.json`.
3. Judge FAIL ×3 or spawn crash → no structured recovery owned by CliAgent.
4. Parent/doer **churn discovering how to invoke tools** (PYTHONPATH grep, remanifest) instead of `python -m tools run -` fence (overlap with #45; still in scope for launch-report/docs).
5. Stall gaps invisible until a human polls — despite #42 adding `ts_ms` / `since_last_s` / duration fields that could drive detection.

Live `cli-agent-fixes` log shape under this stress: many `session_start` / `spawn` / `job_started` relative to fewer `job_finished` (e.g. started ≫ finished) — the loop starts more often than it completes.

### Designed vs actual

| Capability | Designed (#44) | Actual today |
|---|---|---|
| Backlog → jobs | `set_backlog` / `triage_backlog` / `next_backlog_item` + template without parent hand-holding | APIs exist (#46 hygiene); still agent-prompt driven; no watchdog if doer skips them |
| Tool invocation | Single pattern: yaml fence → `python -m tools run -` | File headers document it; doers still rediscover paths (#45); launch report lists monitor paths but does not make fence unmissable as the only invoke path |
| Doer ↔ judge loop | Auto advance on PASS | `complete_job` then `launch_next` are **separate** tools the doer must remember; no post-PASS auto-chain in production code |
| Stall detection | Use session log timing + optional CLI instrumentation | Log has `ts_ms` / `since_last_s` (#42) but **no reader/tool** that classifies stall or triggers recovery |
| Error capture | NOT TAKEN UP, spawn crash, FAIL×3, JSON/BOM, stale pid → session log | Pickup raises NOT TAKEN UP to parent stdout; not a first-class durable error/recovery event kind with context for later diagnose |
| Recovery | CliAgent-owned kick/relaunch | `kick` exists but is **manual**, parent/operator-triggered, and currently uses CLI `--print` — conflicts with “never drive worker with print mode” |
| Parent contract | Launch once; monitor; unblock only after CliAgent recovery fails | `launch_sessions` docs still instruct parent to **Monitor** (30s loop) and **Unblock on three FAILs** — high parent burden by design of the prompt |

### Where it lives

| Seam | Path | Role |
|------|------|------|
| Orchestrator | `utilities/cli_agent/cli_agent.py` — `CliAgent` | `enqueue_jobs`, `launch_next`, `complete_job`, `kick`, `launch_sessions`, `_session_report` |
| Session log | `_CliAgentLog` | Lifecycle + #42 header/summary/timing; no stall/error/recovery kinds |
| Pickup | `_Pickup` / NOT TAKEN UP | Fail-fast on spawn; surfaces to parent, not auto-retry |
| Job queue | `cli-agent-job-queue.json` | FIFO; advance only when something calls complete + launch_next |
| Module context | `utilities/cli_agent/.context/module-context.md` | Describes queue/backlog/isolation; does **not** state self-healing loop or stall detector |
| Templates | `job-templates/defect-fix.json` | Per-job prompts; doer must still call queue tools between jobs |

No `grill-answers.md` for this package on this ticket.

### Call chain / gap

1. Parent calls `launch_sessions` / `launch_next` → spawn doer (and judge).
2. Doer runs Turn; on success is **prompted** to call `complete_job` then `launch_next`.
3. If the doer stops without those calls, **nothing in CliAgent code** polls the log or advances the queue.
4. `kick` can nudge the doer — but only if a parent/operator invokes it; it does not watch `since_last_s`.
5. `_session_report` tells the parent which files to monitor — institutionalizing parent-as-orchestrator.

So the defect is **missing automation seams** (auto-advance, stall watchdog, structured error+recovery events, fence-first launch UX), not a single tip-commit typo. #42 observability is necessary input; #44 is the control loop that should consume it.

### History (vintage)

| Commit | Meaning |
|--------|---------|
| `25233963` / `72593a4e` | Session jsonl lifecycle log |
| `2f4ec700` / `d3ce9745` | Backlog + triage / finish-before-advance (#46) |
| `07161e7d` | Add `kick` tool (manual stall nudge) |
| `919cc997` / `046dfabf` | #42 log header, chat/queue refs, summaries, `ts_ms` / durations |

Backlog, kick, and rich logging arrived as **building blocks**. End-to-end self-management (detect stall → recover → advance without parent) was never closed.

### Similar / related issues

| Issue | Relation |
|-------|----------|
| [#44](https://github.com/abd-works/abd-context-driven-delivery/issues/44) | This ticket (canonical resiliency / minimal parent) |
| [#48](https://github.com/abd-works/abd-context-driven-delivery/issues/48) | `/loop` robust: NOT TAKEN UP, no duplicate spawn, idle-less monitor — **symptom slice**; may close as duplicate if #44 delivers platform |
| [#47](https://github.com/abd-works/abd-context-driven-delivery/issues/47) | Job-finished notifications / poll completion — parent monitoring pain; overlapping |
| [#45](https://github.com/abd-works/abd-context-driven-delivery/issues/45) | Parent/doer churn on tool invoke vs manifest path — in-scope for launch-report/docs half of #44 |
| [#42](https://github.com/abd-works/abd-context-driven-delivery/issues/42) | Session log completeness — **prerequisite observability** (shipped / in flight) |
| [#31](https://github.com/abd-works/abd-context-driven-delivery/issues/31) | Better queuing for CLI-agent tasks — adjacent queue theme |
| [#41](https://github.com/abd-works/abd-context-driven-delivery/issues/41) (closed) | Session isolation before start-ticket — adjacent hygiene |

### Context read

- Issue #44 body (expanded resiliency request)
- `utilities/cli_agent/.context/module-context.md`
- `CliAgent.launch_sessions` / `launch_next` / `complete_job` / `kick` / `_session_report`
- `_CliAgentLog` timing fields (`ts_ms`, `since_last_s`) from #42
- Live `.context/sessions/cli-agent-fixes/cli-agent-session.jsonl` kind counts
- Related issues #48, #47, #45, #42, #31
- Repo history for cli_agent.py (commits above)

### Expected

1. After judge PASS, CliAgent advances the queue (complete + launch_next) **without** requiring the doer or parent to remember both calls — or a durable watchdog does it from log/queue state.
2. Stall detector consumes session-log timing; on threshold, CliAgent runs owned recovery (`kick`/relaunch) and logs a structured error/recovery event; parent is notified only if recovery fails.
3. NOT TAKEN UP, spawn crash, FAIL×3, JSON/BOM, stale pid are **first-class log events** with enough context to diagnose.
4. Launch report + module-context state the **single** tools fence and a **minimal** parent contract (launch / read log / unblock hard fail) — not a 30s parent orchestration loop.
5. `kick` (or successor) must not rely on print-mode worker drives.

### Likely fix direction (later jobs — not applied here)

Extend CliAgent control loop rather than parent scripts: post-PASS auto-advance; background/idle stall watcher over `_CliAgentLog`; structured `error` / `recovery` kinds; harden pickup/relaunch; rewrite `launch_sessions` parent steps to minimal contract; make launch report fence-first. Pair with mechanical BDD on advance/stall/error events; agentic BDD if prompt/report text is part of the contract. Symptom tickets #48/#47 may fold in once the platform loop holds.

### Branch / session

- Issue: [#44](https://github.com/abd-works/abd-context-driven-delivery/issues/44)
- Branch: `session/cliagent-resiliency-self-managed-backlog-doer-judge-loop-stall-detection-minimal-parent-44`
- Worktree: `C:\dev\abd-cdd-44`
- Package: `utilities/cli_agent`
