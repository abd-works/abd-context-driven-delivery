# Install failure themes

Grouped by cause from every `install-failures.md` under `.sessions/` and `.sessions/_complete/`. Update a theme in place; add a theme only for a new cause.

## A running mod holds a published file (WinError 32)

- **Seen:** 1 time. First and last: 2026-11-13 (`.sessions/main/install-failures.md`), runtime `3404eaf9d`, checkout mid-merge to `7a6dbab88`.
- **Cause:** the install copies the chat bar mod into `~/.cdd/claude-plugins/cdd-board/`; Windows refuses to replace or delete a file the running mod has open, here one the change deleted (`hooks/health/open-app-client.ts`).
- **Fix that worked:** run the install again a few seconds later.
- **Held:** yes, once. If it recurs, the installer should retry a locked plugin file the way `3404eaf9d` retries a refused manifest swap.

## A chat loses the cdd server when its header helper fails (401 read as OAuth)

- **Seen:** 1 time. 2026-11-13 (`.sessions/main/install-failures.md`), runtime `3404eaf9d`.
- **Cause:** `~/.cdd/connect.py` raises, printing no headers, while the pinned runtime it imports is unreadable (an install swapping `~/.cdd/runtime`). The request goes without `X-CDD-Project`; the server answers 401; Claude Code takes the 401 as an OAuth challenge and fails with "Dynamic Client Registration rejected (HTTP 404)", and the chat bar reports `no connected MCP tool "board.overview" on a server named "plugin:cdd:cdd"`.
- **Fix that worked:** reinstall (pins the runtime to the checkout's commit), then `/reload-plugins` in the chat.
- **Held:** not yet known. A lasting fix would be for the server to refuse a request with no project header with a status other than 401 (400 names the missing header and does not start OAuth), and for `connect.py` to retry the runtime import briefly instead of exiting.
