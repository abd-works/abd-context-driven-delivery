# harness/chat-ui/pane
The *cdd-board* plugin connects a Claude Code chat to the Session Board, so the board's buttons can put a prompt in that chat or run a command there. It also shows the active ticket on the chat's status line, tells the agent which ticket it is working on, and draws the chat bar above the prompt, which starts with the server health mark. The bar's design and decisions are in `harness/chat-ui`.

`/board` says where the Session Board is and how to start it.

- **Purpose:** let a person drive the agent from the board, and keep the chat aware of the active ticket.
- **Seam (terms):** `cdd-board` plugin; `/board`; the status line entry; the active ticket section of the system prompt; the server health band
- **Dependencies (one-way):** tools/chat (the chat tools it checks in with, through the board's `/api/chat/:chat/check-in` route), harness/kanban (the board it reads, and ticket types from the language adapter at compile time only), harness/health (`server-health.report`, and its types from the language adapter at compile time only)

## Constraint

Load it with `claude --plugin-dir harness/chat-ui/pane`, or install it from this repository's marketplace. It holds no board logic: it checks the chat in every second, runs the commands waiting for it, and reads the board for the active ticket.

A fill waits until the chat's turn has ended, because one made during a turn can report success and show nothing.
