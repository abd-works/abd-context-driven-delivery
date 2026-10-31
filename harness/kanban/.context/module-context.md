# harness/kanban

*Board* shows every work session as a ticket and where it stands in delivery: Backlog, the stages Discovery, Specification, and Implementation, and Complete. It is created with the chosen practices; tickets read their own session logs, so nothing about progress is stored.

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far each of the board's fidelities has got through its stage's actions, and move tickets through the stages.
- **Seam (terms):** Board, Column, Stage, Ticket, FidelityProgress, BacklogItem
- **Dependencies (one-way):** harness/guidance (PracticeGuidance, FidelityGuidance), harness/guidance_actions (GuidanceAction), cdd_guidance/actions (Generate, Validate)

## Constraint

Create a board with its practices, then read columns and tickets from it; everything is re-read from `.sessions/` when asked. Move a ticket only through `Ticket.pull`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the ticket reads back. Store only what cannot be read from the work: a ticket's title, scope, and lineage in its `session.json`, and the board's practices in `_options/`. Never store progress or location.

The model is `harness/kanban/kanban-model.md`.
