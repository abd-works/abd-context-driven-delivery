# cli_agent — module context

## Purpose

CliAgent is the interactive CLI worker for listed context tools and actions. Plan and Swarm Agents launch through CliAgent. Judge is a separate CLI session on the same WorkSession (doer-judge). CliAgent describes hanging Turn shape; the CLI opens and finishes the Turn.

## Seam

CliAgent, IdeCli, CursorCli, VscodeCli

## Dependencies

- `sub_agent` (one-way)
- `workspace` — WorkSession for doer and judge identity (one-way)
- `harness.harness_tool` (one-way)
- `primitives.actions` (one-way)

## Constraint

Callers inject `IdeCli` into `CliAgent(ide=...)`. CliAgent does not open the hanging Turn; the CLI does. Never drive the worker with print mode.
