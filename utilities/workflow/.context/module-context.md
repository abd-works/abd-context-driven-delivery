# workflow — module context

## Purpose

Workflow is a front-end to git: `/backlog` / `/start-ticket` / `/finish-ticket` move GitHub issues on Project columns. Named reusable Workflows (including prebaked *small-work*) are what a Plan is based on. Workspace path is the working folder; Repo is the git backend.

## Seam

Workflow

## Dependencies

- `git` — Repo, Project, Ticket, TicketState (one-way)
- `WorkTicket` — same Repo as Workflow
- `workspace` — working folder / WorkSession (one-way)
- `handoff` (one-way)
- `cli_agent` — CliAgent for non-blocking sub-agent launch from `/backlog` (one-way)
