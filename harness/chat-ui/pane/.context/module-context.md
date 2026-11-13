# harness/chat-ui/pane
The *cdd-board* plugin connects a Claude Code chat to the CDD Kanban, so the board's buttons can put a prompt in that chat or run a command there. It also shows the active ticket on the chat's status line, tells the agent which ticket it is working on, and draws the chat bar above the prompt, which starts with the server health mark. The bar's design and decisions are in `harness/chat-ui`.

`/board` readies the CDD Kanban as a press on it does and says where it is, or what failed and how to fix it. The server health panel's status row lists every app the report lists with its status; a press on one calls `app.open`, which installs it while it is not installed, then, while it is not running, starts its server (the command and folder `app.open` answers) with `$.process.spawn`, so the server lives as long as this chat's mod and stops when the chat ends, as /board's did; an app this chat did not start keeps running. It then opens the app in the side panel (the desktop app's Browser pane, else the browser), or shows why it did not open.

- **Purpose:** let a person drive the agent from the board, and keep the chat aware of the active ticket.
- **Seam (terms):** `cdd-board` plugin; `/board`; the status line entry; the active ticket section of the system prompt; the server health band
- **Dependencies (one-way):** harness/chat (the chat tools it checks in with, through the board's `/api/chat/:chat/check-in` route), space/kanban (the board it reads, and ticket types from the language adapter at compile time only), harness/diagnostics (`server-health.report`, which lists every app with its url, the CDD Kanban's being the board's address the chat checks in at, and `app.open`, which readies an app; their types from the language adapter at compile time only), harness/mcp (`install.json`, the install command the cdd home publishes in the mod, which Run install runs)

## Constraint

Load it with `claude --plugin-dir harness/chat-ui/pane`, or install it from this repository's marketplace. It holds no board logic: it checks the chat in every second, runs the commands waiting for it, and reads the board for the active ticket. The chat bar shows what the Python Board, Ticket and FidelityProgress send: the tickets to switch to, whether the stage is done, each action's command, the agent context, and the choices the open and close dialogs offer.

A fill waits until the chat's turn has ended, because one made during a turn can report success and show nothing.
