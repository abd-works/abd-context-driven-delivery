# harness/kanban/chat-mod
The *cdd-board* plugin connects a Claude Code chat to the Session Board, so the board's buttons can put a prompt in that chat or run a command there. It also shows the active ticket on the chat's status line and tells the agent which ticket it is working on.

`/board` says where the Session Board is and how to start it.

- **Purpose:** let a person drive the agent from the board, and keep the chat aware of the active ticket.
- **Seam (terms):** `cdd-board` plugin; `/board`; the status line entry; the active ticket section of the system prompt
- **Dependencies (one-way):** harness/kanban/app (its `/api/chats` routes), harness/kanban (ticket types from the language adapter, at compile time only)

## Constraint

Load it with `claude --plugin-dir harness/kanban/chat-mod`, or install it from this repository's marketplace. It holds no board logic: it registers the chat, asks the board every second for work queued for this chat, and passes that work into the chat.

A fill waits until the chat's turn has ended, because one made during a turn can report success and show nothing.
