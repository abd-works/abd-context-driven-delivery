# harness/kanban

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far each of the board's fidelities has got through its stage's actions, and move tickets through the stages.
- **Seam (terms):** Board, Column, Backlog, Stage, Ticket, FidelityProgress, BacklogItem
- **Dependencies (one-way):** harness/guidance (PracticeGuidance, FidelityGuidance), harness/guidance_actions (GuidanceAction), cdd_guidance/actions (Generate, Validate)

## Constraint

Create a board with its practices, then read columns and tickets from it; everything is re-read from `.sessions/` when asked. Move a ticket only through `Ticket.pull`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the ticket reads back. Store only what cannot be read from the work: a ticket's title, scope, and lineage in its `session.json`. Never store progress or column.

The classes, terms, and rules are in `harness/kanban/kanban-model.md`.
