# cli_agent - module context

## Purpose

CliAgent is the orchestrator for a multi-job CLI session. It owns the job queue and spawns two participants - a doer and a judge - each with their own `IdeCli` invocation instance. Plan and Swarm Agents launch through CliAgent. CliAgent describes the hanging Turn shape; the CLI opens and finishes the Turn.

A backlog is an ordered collection of items (ticket refs or free-text) assigned to one CliAgent session. One work session covers the whole backlog; each item is run through the active job queue or a named job template.

## Seam

CliAgent, CliParticipant, CliDoer, CliJudge, IdeCli, CursorCli, VscodeCli, JobQueue, CliJob, CliBacklog, CliBacklogItem, CliJobTemplate, CliJobTemplateStore, _CliAgentLog

- `CliAgent` - orchestrator: owns `JobQueue`, spawns `CliDoer` and `CliJudge`. Also manages job templates and backlogs.
- `CliJob` - a unit of work: `prompt`, `tools`, `actions`, `status` (`backlog | in_progress | done`).
- `JobQueue` - ordered FIFO list of `CliJob`; head is `in_progress` while not yet completed.
- `CliBacklog` - ordered collection of `CliBacklogItem` for one session. One work session for the whole backlog; each item runs through the job queue or a named template (e.g. defect-fix).
- `CliBacklogItem` - ticket reference (issue number/URL) or free-text that may create a ticket when no match exists. Status: `pending | in_progress | done`.
- `CliParticipant` - abstract base for doer and judge; each holds exactly one `IdeCli` instance and owns its own state (prompt, resume_id).
- `CliDoer` - participant that executes the current job; has a `current_job` reference.
- `CliJudge` - participant that evaluates results; holds criteria/instructions.
- `IdeCli` - thin, nearly stateless invocation layer: model, mode, agent_mode, resume ID, timeouts only. One `IdeCli` per participant.
- `_CliAgentLog` - append-only JSONL event log: session_start, spawn, jobs_defined, job_started, job_finished, verdict.
- `CliJobTemplate` - named, reusable list of jobs. Shape is identical to a job queue.
- `CliJobTemplateStore` - persists and retrieves templates. Default root: `utilities/cli_agent/job-templates/`; overridable per project.

`launch_next` sends the head job to the doer. One send at a time - do not stack resumes. **`run_backlog` is the in-process orchestrator**: it launches the doer, waits for the Turn to end, spawns/resumes the judge in code (not via doer prompt), and on PASS calls `complete_job` then the next job. The doer only executes the job Turn — it must not contact the judge or advance the queue. Parent launches `run_backlog` once and monitors the session log. `set_backlog` assigns items; **`triage_backlog` scans the entire backlog up front** (map free-text to existing `#N` or `capture_backlog`, register on the board with **theme:cli-agent**); `next_backlog_item` advances to the next item and reloads the template/queue for it. When leaving a ticket item, **finish-ticket runs before `next_backlog_item` advances** (merge, Project Done, close).

## Dependencies

- `sub_agent` (one-way)
- `workspace` - WorkSession for doer and judge identity (one-way)
- `harness.harness_tool` (one-way)
- `primitives.actions` (one-way)

## Constraint

`IdeCli` carries only CLI invocation config (model, mode, timeouts, resume ID). Job and session state (`current_job`, `turn_task`, session name) live on `CliAgent` and `CliParticipant`, not on `IdeCli`. CliAgent does not open the hanging Turn; the CLI does. Never drive the worker with print mode. Judge only when the launch lists a context tool, action, or the user explicitly requests one. `cleanup` / `cleanup_session` remove temps this kit wrote; WorkSession does not list those files. One work session per backlog - never a new session per backlog item.

Do not bind a durable CliAgent work session to leftover ``default`` (or a folder-slug stand-in) while HEAD is still on main before `/start-ticket`. Ticket work must land on ``session/<ticket>`` with its own worktree. After start-ticket, call ``rebind_to_worktree`` so the workspace root is that worktree. The same isolation contract — session == ``session/<name>`` branch == own worktree before jobs, then rebind after start-ticket — applies to **CliAgent**, **SubAgent**, and **no-agent** flows, not only CLI spawn. `_ensure_work_session` skips sole-session fallback when that session is named ``default``, and does not invent a folder-slug durable session on main; it defers bind until start-ticket / rebind.
