# cli_agent — module context

## Purpose

CliAgent is the interactive CLI worker for listed context tools and actions. Plan and Swarm Agents launch through CliAgent. Judge is a separate CLI session on the same WorkSession (doer-judge). CliAgent describes hanging Turn shape; the CLI opens and finishes the Turn.

## Seam

CliAgent, IdeCli, CursorCli, VscodeCli, JobQueue

`job_queue` is a CliAgent property (list of jobs on the WorkSession).
`launch_next` sends the oldest item. One send at a time — do not stack resumes.

## Dependencies

- `sub_agent` (one-way)
- `workspace` — WorkSession for doer and judge identity (one-way)
- `harness.harness_tool` (one-way)
- `primitives.actions` (one-way)

## Constraint

Callers inject `IdeCli` into `CliAgent(ide=...)`. CliAgent does not open the hanging Turn; the CLI does. Never drive the worker with print mode. Judge only when the launch lists a context tool, action, or utility.
