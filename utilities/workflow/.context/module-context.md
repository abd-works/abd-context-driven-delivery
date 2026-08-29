# workflow — module context

## Purpose

Workflow is a front-end to git: **one GitHub Project per Workflow**; that Project’s Status columns are the flow’s states. The kit reads/writes Status (kit + board only — no GitHub Actions). Per-state behavior lives in `workflow/flows/{name}.yaml` (tools, one action, utilities, prose, optional hil/judge, owner + project_number written on save). Columns stay on GitHub — do not mirror the board in the repo. Named reusable Workflows (including prebaked *small-work*) and throwaway Workflows (temp Project + yaml deleted on `/finish-plan`) are what a Plan runs. Moving a card into a state creates a Turn. Workspace path is the working folder; Repo is the git backend.

## Seam

Workflow, FlowState, FlowFile

## Dependencies

- `git` — Repo, Project, Ticket, TicketState (one-way)
- `WorkTicket` — same Repo as Workflow
- `workspace` — working folder / WorkSession (one-way)
- `handoff` (one-way)
