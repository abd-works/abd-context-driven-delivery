# harness/kanban

*KanbanBoard* shows every work session as a ticket and where it stands in delivery: Backlog, Discovery, Specification, Implementation, Complete. It reads `.sessions/` each time it is asked and stores nothing of its own.

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far its selected guidance has got, and move tickets through the stages.
- **Seam (terms):** KanbanBoard, Ticket, BacklogItem, BoardPosition, SkillProgress, Column, Stage
- **Dependencies (one-way):** space/session (Session), space/repo (Repo), harness/guidance (FidelityGuidance)

## Constraint

Read the board through `KanbanBoard.board()`; it re-reads `.sessions/` every time. Move a ticket only through `Ticket.pull`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the board reads back. Store only what cannot be read from the work: title, scope, lineage, and selected guidance in `session.json`. Never store skill progress or board position.

The model is `harness/kanban/kanban-model.md`.
