# utilities/plan — module context

## Purpose

Plan is a front-end to git: ordered Workspace Turns whose TicketState maps to Project/Workflow columns (Backlog / In Progress / Done). Optional JudgeCheckpoint and HILCheck hang on a Turn. CliAgent is the worker.

## Seam

Plan, JudgeCheckpoint, HILCheck, TicketState

## Dependencies

- `workspace` (one-way)
- `git` — TicketState / Project columns (one-way)
