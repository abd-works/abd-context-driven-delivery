# utilities/plan — module context

## Purpose

Plan is a front-end to git based on a reusable Workflow or a new Workflow named on `/plan`. `/plan /small-work {context}` (PlanCommands) loads the prebaked small-work Workflow into a Plan without running against issues. TurnAttachments hang HILCheck and JudgeCheckpoint on Turns. PlanExecution runs start/execute/judge-record/advance/fix. CliAgent is the worker. BDD owns CE companions; Plan does not inject CE.

## Seam

Plan, PlanCommands, PlanExecution, PlanSeed, PlanTurns, TurnAttachments, TurnTemplate, JudgeCheckpoint, HILCheck, ProgressView, TicketState

## Dependencies

- `workspace` (one-way) — working folder, not the Repo
- `git` — TicketState / Project columns (one-way)
- `workflow` (one-way) — reusable / named Workflow the Plan is based on
