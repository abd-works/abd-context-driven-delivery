# harness/chat-ui/pane
The *cdd-board* plugin connects a Claude Code chat to the CDD Kanban, so the board's buttons can put a prompt in that chat or run a command there. It also tells the agent which ticket it is working on, and draws the chat bar above the prompt, which starts with the server health mark, and the status line below the chat: repository · branch · the whole path of the folder the session works in. The bar's design and decisions are in `harness/chat-ui`.

`/board` says where the CDD Kanban is and how to start it.

- **Purpose:** let a person drive the agent from the board, and keep the chat aware of the active ticket.
- **Seam (terms):** `cdd-board` plugin; `/board`; the status line below the chat; the active ticket section of the system prompt; the server health band
- **Dependencies (one-way):** harness/chat (the chat tools it checks in with, through the board's `/api/chat/:chat/check-in` route), space/kanban (the board it reads, and ticket types from the language adapter at compile time only), harness/diagnostics (`server-health.report`, which also gives the board's address the chat checks in at, and its types from the language adapter at compile time only), harness/mcp (`install.json`, the install command the cdd home publishes in the mod, which Run install runs), harness/graph and scripts (`scripts/start_graph_web.py` and `scripts/start_graph_app.py`, run from the repository's own folder when a press on the health panel's Graph app finds it not running)

## Constraint

Load it with `claude --plugin-dir harness/chat-ui/pane`, or install it from this repository's marketplace. It holds no board logic: it checks the chat in every second, runs the commands waiting for it, and reads the board for the active ticket. The chat bar shows what the Python Board, Ticket and FidelityProgress send: the tickets to switch to, whether the stage is done, each action's command, the agent context, and the choices the open and close dialogs offer.

A fill waits until the chat's turn has ended, because one made during a turn can report success and show nothing.
