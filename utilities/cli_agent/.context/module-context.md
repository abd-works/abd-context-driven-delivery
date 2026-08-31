# cli_agent - module context

## Purpose

CliAgent is the orchestrator for a multi-job CLI session. It owns the job queue and launches doer and judge turns through `IdeCli`. Plan and Swarm Agents launch through CliAgent. CliAgent describes the hanging Turn shape; the CLI opens and finishes the Turn.

A backlog is an ordered collection of items (ticket refs or free-text) assigned to one CliAgent session. One work session covers the whole backlog; each item is run through the active job queue or a named job template.

## Seam

CliAgent, IdeCli, CursorCli, VscodeCli, IdeCliResult, JobQueue, CliBacklog, CliBacklogItem

- `CliAgent` — orchestrator: owns `JobQueue`, manages backlogs and job templates, launches doer/judge turns.
- `IdeCli` / `CursorCli` / `VscodeCli` / `IdeCliResult` — public IDE CLI invocation surface (model, mode, timeouts, resume ID). When `model` is empty, `SessionModel.resolve_for_launch` supplies `composer-2.5` (session file → `sessions/default` → default). When `mode` is empty, `medium` (non-fast: `composer-2.5[fast=false]` on cursor-agent). Use `cursor-grok-4.6-medium` only when the orchestrator judges the job long and very complex — a rare escalation, not the default.
- `JobQueue` — ordered FIFO of jobs; head is in progress while not yet completed.
- `CliBacklog` / `CliBacklogItem` — ordered backlog for one session (`pending | in_progress | done`).

## Public API

- `launch_next` — send the head job to the doer. One send at a time; do not stack resumes.
- `run_backlog` — in-process orchestrator: launch doer, wait for the Turn to end, then either human-check, judge, or complete and start the next. Parent launches once and monitors the session log.
- `resolve_human_check` — when a job has `human: true`, record **looks_good** or **needs_fixing** (with feedback) so `run_backlog` can complete or redo that job.
- `set_backlog` / `triage_backlog` / `next_backlog_item` — assign items; triage the whole backlog up front (map free-text to `#N` or `capture_backlog`, register with **theme:cli-agent**); advance to the next item. When leaving a ticket item, **finish-ticket runs before `next_backlog_item` advances**.

Jobs may set optional `human: true` (alias `human_check`). After the doer finishes such a job, `run_backlog` logs `human_check_needed`, fires an IDE/OS notification (logged as `human_notified`), and waits for parent/human resolution — no second AI agent. `human` replaces `judge` for that job when both are set.

## Constraint

`IdeCli` carries only CLI invocation config. Job and session state live on `CliAgent`, not on `IdeCli`. CliAgent does not open the hanging Turn; the CLI does. Never drive the worker with print mode. Judge only when the launch lists a context tool, action, or the user explicitly requests one. `cleanup` / `cleanup_session` remove temps this kit wrote. One work session per backlog — never a new session per backlog item.

Do not bind a durable CliAgent work session to leftover `default` while HEAD is still on main before `/start-ticket`. Ticket work must land on `session/<ticket>` with its own worktree. After start-ticket, call `rebind_to_worktree`. The same isolation contract — session == `session/<name>` branch == own worktree before jobs, then rebind after start-ticket — applies to **CliAgent**, **SubAgent**, and **no-agent** flows.

## Extend

Register named job templates under the project templates root (default `utilities/cli_agent/job-templates/`). Callers select a template by name when running backlog items; do not treat template store internals as the seam.

## Dependencies

- `sub_agent` (one-way)
- `workspace` — WorkSession for doer and judge identity (one-way)
- `harness.harness_tool` (one-way)
- `primitives.actions` (one-way)
