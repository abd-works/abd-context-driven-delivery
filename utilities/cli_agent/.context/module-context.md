# cli_agent — module context

## Purpose

CliAgent is the orchestrator for a multi-job CLI session. It owns the job queue and spawns two participants — a doer and a judge — each with their own `IdeCli` invocation instance. Plan and Swarm Agents launch through CliAgent. CliAgent describes the hanging Turn shape; the CLI opens and finishes the Turn.

## Seam

CliAgent, CliParticipant, CliDoer, CliJudge, IdeCli, CursorCli, VscodeCli, JobQueue, CliJob, _CliAgentLog

- `CliAgent` — orchestrator: owns `JobQueue`, spawns `CliDoer` and `CliJudge`. Also manages job templates.
- `CliJob` — a unit of work: `prompt`, `tools`, `actions`, `status` (`backlog | in_progress | done`).
- `JobQueue` — ordered FIFO list of `CliJob`; head is `in_progress` while not yet completed.
- `CliParticipant` — abstract base for doer and judge; each holds exactly one `IdeCli` instance and owns its own state (prompt, resume_id).
- `CliDoer` — participant that executes the current job; has a `current_job` reference.
- `CliJudge` — participant that evaluates results; holds criteria/instructions.
- `IdeCli` — thin, nearly stateless invocation layer: model, mode, agent_mode, resume ID, timeouts only. One `IdeCli` per participant.
- `_CliAgentLog` — append-only JSONL event log: session_start, spawn, jobs_defined, job_started, job_finished, verdict.
- `CliJobTemplate` — named, reusable list of jobs. Shape is identical to a job queue.
- `CliJobTemplateStore` — persists and retrieves templates. Default root: `utilities/cli_agent/job-templates/`; overridable per project.

`launch_next` sends the head job to the doer. One send at a time — do not stack resumes.

## Dependencies

- `sub_agent` (one-way)
- `workspace` — WorkSession for doer and judge identity (one-way)
- `harness.harness_tool` (one-way)
- `primitives.actions` (one-way)

## Constraint

`IdeCli` carries only CLI invocation config (model, mode, timeouts, resume ID). Job and session state (`current_job`, `turn_task`, session name) live on `CliAgent` and `CliParticipant`, not on `IdeCli`. CliAgent does not open the hanging Turn; the CLI does. Never drive the worker with print mode. Judge only when the launch lists a context tool, action, or the user explicitly requests one. `cleanup` / `cleanup_session` remove temps this kit wrote; WorkSession does not list those files.
