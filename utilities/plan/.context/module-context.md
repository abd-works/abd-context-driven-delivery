# utilities/plan — module context

## Purpose

Plan is a front-end to git: a **Workflow** (states on its own GitHub Project) **plus** the ticket set. No planned-turn list — FIFO is the default; the agent may batch related tickets. Moving a ticket off Project 1 (inbox) onto the flow board / into a state creates a real Turn. `/start-ticket /small-work 14` starts #14 on that board; unnamed start stays inbox In Progress. `/plan /small-work {context}` loads the prebaked small-work Workflow into a Plan. When the flow is done, cards stay on the flow Project until operator `/finish-plan` (inbox Done, close issues, close session). TurnAttachments hang HILCheck and JudgeCheckpoint when the entered state yaml marks them. CliAgent is the worker. BDD owns CE companions; Plan does not inject CE.

## Seam

Plan, PlanCommands, PlanExecution, PlanSeed, JudgeCheckpoint, HILCheck, ProgressView, TicketState, SmallWorkRunner, ThemedIssue

## Dependencies

- `workspace` (one-way) — working folder, not the Repo
- `git` — TicketState / Projects (inbox + flow) / themed issue list (one-way)
- `workflow` (one-way) — reusable / named / throwaway Workflow the Plan runs
