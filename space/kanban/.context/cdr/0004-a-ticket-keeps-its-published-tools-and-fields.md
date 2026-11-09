# A ticket keeps its published tools and data fields, and hands the work to the parts it holds

Round 9 split `Ticket` by job (finding 1 of `round9-space-tools.md`; fix rule 10). It held three jobs: its progress, its git checkout, and the moves and marks a person makes on its stages. Each is now a part the ticket makes once, with a name from the board's language:

- *TicketWork* (`ticket.work`): its progress on each fidelity the board requires, read from its session's log once per ticket read, the one command that runs an action on its fidelities, and the one way a line is written for it (`record`).
- *TicketCheckout* (`ticket.checkout`, `ticket_checkout.py`): its own *Branch*, made once, the branch its work is on, its worktree and the chat working there, what opening, leaving, and closing it can do now, and doing it (`open`, `open_worktree`, `leave`).
- *StageMarks* (`ticket.marks`): its latest move and its latest mark in a stage, which its session's log answers (`SessionLog.latest`), and writing a move or a mark.

That took `Ticket` from 48 methods and a total complexity of 143 to 33 methods and a total complexity of 75. The rule asks for under 30 methods. We keep the 33 because 32 of them are what the ticket publishes:

- 15 MCP tools (`ticket.create`, `branch`, `work_branch`, `format_choices`, `close_choices`, `leave_choices`, `open_choices`, `activate`, `open_worktree`, `move_next`, `move_previous`, `move_to`, `close`, `archive`, `violations`). The chat bar, the Session Board app, the installed slash commands, and the stub chat in `harness/chat-ui` call them by these names, and a toolset publishes a tool under its own class's name, so moving a tool onto a part would rename it.
- 15 data fields (`name`, `title`, `session`, `progress`, `column`, `is_closed`, `is_active`, `drop_targets`, `is_done`, `next`, `agent_context`, `last_activity`, `worktree`, `working_chat`, `stage_work`), which the generated TypeScript `TicketData` reads by these keys.
- Its constructor and its `@tool_subject` loader, which every tool needs.

Each published method is one line that asks a part, or the few lines that decide a column or a move from what the parts answer. The one private method left, `_return_to_backlog`, is shared by `move_previous` and `move_to`.

Revisit when the harness can publish a held part's tools under its owner's name: then the checkout's five tools can move onto `TicketCheckout` without renaming them, and `Ticket` drops under 30.
