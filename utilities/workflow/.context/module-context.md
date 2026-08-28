# workflow — module context

## Purpose

Workflow is a front-end to git: `/backlog` / `/start-ticket` / `/finish-ticket` move GitHub issues on Project columns (Backlog / In Progress / Done) and open or close WorkSessions. Not a second ticket store.

## Seam

Workflow

## Dependencies

- `git` — Repo, Project, Ticket, TicketState (one-way)
- `workspace` — WorkSession (one-way)
- `handoff` (one-way)
