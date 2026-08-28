# utilities/swarm — module context

## Purpose

Swarm is a front-end to git and Plan: Supervisor plus Agents on a shared Plan turn slice. Agent is a CliAgent under one Hypothesis. CliAgent.launch_sessions starts at Plan.start. JudgeCheckpoint hangs on the Turn (CliAgent doer-judge); Supervisor.compare reads that result and does not judge.

## Seam

Swarm, Supervisor, Agent, Hypothesis, Outcome

## Dependencies

- `plan` (one-way)
- `cli_agent` (one-way)
- `workspace` (one-way)
- `git` — ticket/Project columns via Plan Turn.state (one-way)
