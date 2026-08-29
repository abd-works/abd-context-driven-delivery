# utilities/swarm — module context

## Purpose

Swarm is a front-end to git and Plan: Supervisor plus Agents on a shared flow/ticket slice (not a planned-turn list). Agent is a CliAgent under one Hypothesis. CliAgent.launch_sessions starts at Plan.start. JudgeCheckpoint / HILCheck hang on the Turn when the entered flow state marks them (CliAgent doer-judge); Supervisor.compare reads that result and does not judge. Agents keep context across calls and may batch related tickets.

## Seam

Swarm, Supervisor, Agent, Hypothesis, Outcome

## Dependencies

- `plan` (one-way)
- `cli_agent` (one-way)
- `workspace` (one-way)
- `git` — ticket/Project columns via flow moves that create Turns (one-way)
