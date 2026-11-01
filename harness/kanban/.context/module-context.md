# harness/kanban

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far each of its fidelities has got through its stage's actions, and move tickets through the stages.
- **Seam (terms):** Board, Column, Backlog, Stage, Ticket, FidelityProgress, BacklogItem, with `Board`, `Ticket`, and `BacklogItem` each its own toolset (the `cdd` MCP tools `board.show`, `board.set_wip_limit`, `board.help`, `ticket.new`, `ticket.move_next`, `ticket.move_previous`, `ticket.close`, `ticket.archive`, `ticket.activate`, `ticket.workspace`, `ticket.enable_practice`, `ticket.files`, `ticket.read_file`, `ticket.report`, `ticket.generate_commands`, `backlog-item.add`, `backlog-item.start`)
- **Dependencies (one-way):** harness/guidance (PracticeGuidance, FidelityGuidance), harness/guidance_actions (GuidanceAction), cdd_guidance/actions (Generate, Validate, and the saved graph reader `validate.graph_json_reader`), space/repo (Repo), space/session (Session, PracticeSessionOutput)

## Constraint

Create a board on a repository, then read columns and tickets from it; everything is re-read from `.sessions/` when asked. Move a ticket only through `Ticket.move_next`, `Ticket.move_previous`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the ticket reads back. A ticket holds a reference to its `Session`, which owns the session's files, so `Ticket.close` calls `Session.close`. Store only what cannot be read from the work: a ticket's title, scope, lineage, and turned-off practices in its `session.json`, and the stages' WIP limits in `.sessions/_board.json`. Never store progress or column.

The classes, terms, and rules are in `harness/kanban/.context/kanban-model.md`; the behavior is `kanban_spec.py` and `kanban_tools_spec.py`, organised by story.

## The board pane (Claude Code)

`harness/kanban/pane/` is the `cdd-board` Claude Code plugin: a Board pane beside the chat, the active ticket on the status line, a band above the prompt when the active ticket has violations, toasts when a ticket moves or a fidelity is done, the active ticket in the system prompt, `/board`, and `/ticket next|previous|close|activate <ticket>`. It paints its own canvas in the abd.works engineering (dark) colors so those colors hold on either Claude Code theme. It follows `patterns-cdd-claude-mod`: `hooks/register.tsx` is Boot only, and `hooks/kanban/` holds a display-only client and plain-function actions for each object, the views, and the surface modules. It only draws: everything it shows comes from the `cdd` MCP tools, and it reads the board again after every `cdd` tool call and every prompt. Load it with `claude --plugin-dir harness/kanban/pane`. Check it with `claude plugin validate harness/kanban/pane` and `claude plugin test harness/kanban/pane`.
