# utilities/plan — module context

## Purpose

Plan is a front-end to git: ordered Workspace Turns whose TicketState maps to Project/Workflow columns. TurnAttachments hang HILCheck and JudgeCheckpoint on Turns. PlanExecution runs start/execute/judge-record/advance/fix. CliAgent is the worker.

## Seam

Plan, PlanExecution, TurnAttachments, JudgeCheckpoint, HILCheck, ProgressView, TicketState

## Dependencies

- `workspace` (one-way)
- `git` — TicketState / Project columns (one-way)
