# utilities/plan — module context

## Purpose

Owns a Plan associated with a Workspace: an ordered sequence of Turns. Each Turn already has action, fidelity, context, and toolCalls. Turn.state is TicketState (Backlog / In Progress / Done). Optional JudgeCheckpoint and/or HILCheck hang on a Turn. Start Plan opens a WorkSession; the first Backlog Turn becomes In Progress. Execute Turn runs that In Progress Turn. Advance Turn finishes it (Done) and the next Backlog Turn becomes In Progress. Fix and Rerun uses Turn.recordMistake, recordCorrection, and WorkSession.repairs.

## Primary use case

A Practitioner creates a Plan on a Workspace, adds Turns (one action, multiple tool_keys/toolCalls), optional HILCheck and JudgeCheckpoint, then starts and executes the Plan through TicketState.

## Rationale

Plan sequences existing workspace.Turn work. No PlannedTurn. CliAgent describes hanging Turn shape elsewhere; Plan does not open Turns for CliAgent.

## Seam

Plan, JudgeCheckpoint, HILCheck, TicketState

## Public API

- `Plan` — `workspace`, `turns`; `create(workspace)`, `start()` → WorkSession, `executeTurn()`, `advanceTurn()`
- `JudgeCheckpoint` — `rubric`, `judgeResult` (same rubric argument as `ai_judge`)
- `HILCheck` — human-in-the-loop check hanging on a Turn

## Dependencies

- `workspace` (one-way)
