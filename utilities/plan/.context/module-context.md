# utilities/plan — module context

## Purpose

Plan is a front-end to git based on a reusable Workflow or a Workflow named on `/plan`. `/plan /small-work {context}` loads the prebaked small-work Workflow into a Plan (does not execute tickets). TurnAttachments hang HILCheck and JudgeCheckpoint on Turns. PlanExecution runs start/execute/judge-record/advance/fix. CliAgent is the worker. BDD owns CE companions; Plan does not inject CE.

## Seam

Plan, PlanExecution, TurnAttachments, TurnTemplate, JudgeCheckpoint, HILCheck, ProgressView

## Dependencies

- `workspace` — working folder (one-way)
- `workflow` — named/reusable Workflow the Plan is based on (one-way)
- `git` — TicketState / Project columns (one-way)
