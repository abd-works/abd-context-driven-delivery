# agent — module context

## Purpose

The `agent` module implements the redesigned Agent orchestration model for GitHub #55: backlog (`backlog`, `current_task`, `completed_tasks`), participant lifecycle for doer → judge → optional human, and JSONL session logging via `AgentSessionLog`. Stubbed runtime hooks let vanilla BDD prove orchestration and log kinds before CLI or SubAgent plumbing lands in later increments.

## Seam

`Agent.run_next_task`, `Agent.kick`, `Agent.add_tasks`, `Agent.clear_backlog`, `AgentSession.open`, `AgentSession.close`, `AgentSessionLog.send`, `AgentSessionLog.accepted`, `AgentSessionLog.done`, `AgentSessionLog.verdict`, `AgentSessionLog.complete_task`

## Constraint

Agent owns AgentSessionLog writes for send, accept, done, verdict, and fault. Kit Turns are owned by external tools CLI lifecycle — Agent must never finish a kit Turn from task completion.

## Public API

- `Agent` — orchestrates doer → judge → optional human; `run_next_task` runs one backlog item; `kick` retries the doer after FAIL
- `AgentTask` — backlog item with doer and optional judge/human
- `AgentParticipant` — doer, judge, or human role on a task
- `AgentSession` — named session folder and log
- `AgentSessionLog` — append orchestration events (`send`, `accepted`, `done`, `verdict`, `kick`, …)

## Extend

Subtypes (`CliAgent`, `SubAgent`, `ChatAgent`) override participant runtime hooks to bind real chat or child processes. Manifest/turn fence and `maxFails` land in later increments.

## Dependencies

None beyond the Python standard library for increments 1–2.
