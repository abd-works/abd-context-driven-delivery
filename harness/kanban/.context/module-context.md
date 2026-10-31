# harness/kanban

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far each of the board's fidelities has got through its stage's actions, and move tickets through the stages.
- **Seam (terms):** Board, Column, Backlog, Stage, Ticket, FidelityProgress, BacklogItem, Kanban (the `cdd` MCP tools `kanban.board`, `kanban.pull`, `kanban.start`, `kanban.close`, `kanban.archive`)
- **Dependencies (one-way):** harness/guidance (PracticeGuidance, FidelityGuidance), harness/guidance_actions (GuidanceAction), cdd_guidance/actions (Generate, Validate)

## Constraint

Create a board with its practices, then read columns and tickets from it; everything is re-read from `.sessions/` when asked. Move a ticket only through `Ticket.pull`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the ticket reads back. Store only what cannot be read from the work: a ticket's title, scope, and lineage in its `session.json`. Never store progress or column.

The classes, terms, and rules are in `harness/kanban/kanban-model.md`; the behavior is `kanban_spec.py` and `kanban_tools_spec.py`.

## The board pane (Claude Code)

`harness/kanban/pane/` is the `cdd-board` Claude Code plugin: a Board pane beside the chat, the active ticket on the status line, a band above the prompt when the active ticket has violations, toasts when a ticket moves or a fidelity is done, the active ticket in the system prompt, and `/board`. It only draws: everything it shows comes from the `kanban.*` tools on the `cdd` MCP server, and it reads the board again after every `cdd` tool call and every prompt. Load it with `claude --plugin-dir harness/kanban/pane`. Check it with `claude plugin validate harness/kanban/pane` and `claude plugin test harness/kanban/pane`.
