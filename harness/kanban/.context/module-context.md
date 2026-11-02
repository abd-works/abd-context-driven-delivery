# harness/kanban

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far each of its fidelities has got through its stage's actions, and move tickets through the stages.
- **Seam (terms):** Board, Column, Backlog, Stage, Ticket, FidelityProgress, BacklogItem, with `Board`, `Ticket`, and `BacklogItem` each its own toolset (the `cdd` MCP tools `board.show`, `board.set_wip_limit`, `board.help`, `ticket.new`, `ticket.move_next`, `ticket.move_previous`, `ticket.close`, `ticket.archive`, `ticket.activate`, `ticket.workspace`, `ticket.enable_practice`, `ticket.files`, `ticket.read_file`, `ticket.report`, `ticket.generate_commands`, `backlog-item.add`, `backlog-item.start`), and the language adapter `@language_adapter(language="typescript")` deploys from them
- **Dependencies (one-way):** harness/guidance (PracticeGuidance, FidelityGuidance), harness/guidance_actions (GuidanceAction), cdd_guidance/actions (Generate, Validate, and the saved graph reader `validate.graph_json_reader`), space/repo (Repo), space/session (Session, PracticeSessionOutput)

## Constraint

Create a board on a repository, then read columns and tickets from it; everything is re-read from `.sessions/` when asked. Move a ticket only through `Ticket.move_next`, `Ticket.move_previous`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the ticket reads back. A ticket holds a reference to its `Session`, which owns the session's files, so `Ticket.close` calls `Session.close`. Store only what cannot be read from the work: a ticket's title, scope, lineage, and turned-off practices in its `session.json`, and the stages' WIP limits in `.sessions/_board.json`. Never store progress or column.

The classes, terms, and rules are in `harness/kanban/.context/kanban-model.md`; the behavior is `kanban_spec.py` and `kanban_tools_spec.py`, organised by story.

## The board app

`harness/kanban/app/` is the Session Board: a web app built in `patterns-lern-domain-driven` on the access in `patterns-cdd-access`, opened in the Claude desktop Browser pane. Each route asks a `{Object}Node`, which extends the `{Object}Tools` class the installer generates from these toolsets, so the app holds no rule and no copy of the board. Run `python scripts/install.py --ide Claude` first, because the app imports the language adapter from the install, then `npm install`, `npm run build`, and `npm start` in that folder. It listens on 127.0.0.1:8778 and answers only its own page and mod, because it can put prompts into a live chat. `BOARD_PROJECT` names the repository to show, and `BOARD_PORT` the port.

Shapes the app reads are `TypedDict`s in `data.py`, so changing one and installing changes the TypeScript. Test anything that acts on a throwaway project with no real remote, because these tools really commit and push.

## The chat mod (Claude Code)

`harness/kanban/chat-mod/` is the `cdd-board` plugin: it registers a chat with the board app and passes its buttons into the chat, shows the active ticket on the status line, and adds it to the system prompt. It polls the app every second and holds no board logic. A fill waits for the end of a turn, because one made during a turn can report success and show nothing. Load it with `claude --plugin-dir harness/kanban/chat-mod`.

The earlier board pane, its desktop test driver, and the list of what a pane could not draw are in `retired/harness/kanban/`.
