# harness/kanban
*Board* shows every work session in a repository as a *Ticket* on a kanban, so a person can see at a glance what each session has done and what it needs next. Its *Columns* are the *Backlog*, three *Stages* (Discovery, Specification, Implementation), and *Complete*. A *Stage* splits into In progress and Done and carries a WIP limit, set with `board.set_wip_limit`.

A *Ticket* is one session. It is placed by its *FidelityProgress*: which of Generate, Validate, and Review are done on each fidelity its stage requires. A person moves it on with `ticket.move_next`, back with `ticket.move_previous`, straight into a stage's In progress or Done with `ticket.move_to`, and off the stages with `ticket.close` or `ticket.archive`. `ticket.activate` makes it the session the agent works in.

A *BacklogItem* is an idea that is not a session yet. `backlog-item.create` writes one, and `backlog-item.start` opens it as a ticket in Discovery and moves the item's file into the ticket's session folder, where the idea stays until it becomes lasting context.

- **Purpose:** see every session's progress through the delivery stages, and move sessions through them, from an agent's tools or from the Session Board.
- **Seam (terms):** Board, Column, Stage, Ticket, FidelityProgress, BacklogItem; the `cdd` MCP tools `board.*`, `ticket.*`, and `backlog-item.*`; `@language_adapter(language="typescript")` on `Board`, `Ticket`, and `BacklogItem`, so TypeScript reaches the same tools as typed objects
- **Dependencies (one-way):** harness/guidance, harness/guidance_actions, cdd_guidance/actions (Generate, Validate, and the saved graph reader), space/repo, space/session

## Constraint

Read a board from a repository; every column and ticket is read again from `.sessions/` each time it is asked for. Move a ticket only through `ticket.move_next`, `ticket.move_previous`, `ticket.move_to`, `ticket.close`, and `ticket.archive`, so every move is a line in the session log or a folder move that the ticket reads back.

Store only what cannot be read from the work: a ticket's title, scope, parent, workpath, turned-off practices, and each practice root, in its `session.json`, and the WIP limits in `.sessions/_board.json`. Never store a ticket's progress or column; they come from the session log, so a move made by the agent and one made on the board give the same answer.

Progress counts only actions recorded in the session log. A fidelity's files existing is shown on the files list, but it does not mark Generate done. Validate and Review are allowed once any action on a fidelity is recorded, as often as a person wants to check the same output again.

Never delete a backlog item's file: it is the only copy of the idea, so starting the item moves it instead.
