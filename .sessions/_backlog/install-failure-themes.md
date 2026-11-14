# Install failure themes

Grouped by cause from every `install-failures.md` under `.sessions/` and `.sessions/_complete/`. Update a theme in place; add a theme only for a new cause.

## A running mod holds a published file (WinError 32)

- **Seen:** 1 time. First and last: 2026-11-13 (`.sessions/main/install-failures.md`), runtime `3404eaf9d`, checkout mid-merge to `7a6dbab88`.
- **Cause:** the install copies the chat bar mod into `~/.cdd/claude-plugins/cdd-board/`; Windows refuses to replace or delete a file the running mod has open, here one the change deleted (`hooks/health/open-app-client.ts`).
- **Fix that worked:** run the install again a few seconds later.
- **Held:** yes, once. If it recurs, the installer should retry a locked plugin file the way `3404eaf9d` retries a refused manifest swap.

## A chat loses the cdd server when its header helper fails (401 read as OAuth)

- **Seen:** 2 times. First 2026-11-13 ~18:13, last 2026-11-13 ~19:20 (`.sessions/main/install-failures.md`), runtimes `3404eaf9d` and `7a6dbab88`.
- **Cause:** `~/.cdd/connect.py` raises, printing no headers, while the pinned runtime it imports is unreadable (an install swapping `~/.cdd/runtime`). The request goes without `X-CDD-Project`; the server answers 401; Claude Code takes the 401 as an OAuth challenge and fails with "Dynamic Client Registration rejected (HTTP 404)", and the chat bar reports `no connected MCP tool "board.overview" on a server named "plugin:cdd:cdd"`.
- **Fix that worked:** reinstall (pins the runtime to the checkout's commit), then `/reload-plugins` in the chat.
- **Held:** not yet known. The lasting fix is in `bf81e4c42`: the server refuses a request with no project header with 400, which names the missing header and does not start OAuth, and `connect.py` retries the runtime import for up to 30 seconds while an install swaps it. A chat that lost cdd before that fix still needs one `/reload-plugins`.

## A server started from the runtime holds the folders an install replaces (WinError 5 / 183)

- **Seen:** 1 time. 2026-11-13 ~19:50 (`.sessions/main/install-failures.md`), pinning `7a6dbab88` to `6f2a51c7a`. Related to *A running mod holds a published file*: both are Windows refusing to remove something a running process has open.
- **Cause:** a pin copies the checkout's language adapters into `~/.cdd/runtime/.claude/language-adapters`. `rmtree(..., ignore_errors=True)` silently left the folders an app server started from the runtime still held, and `copytree` then refused the existing folder, leaving the runtime's adapters empty.
- **Fix that worked:** `copytree(..., dirs_exist_ok=True)`, and copying on every install from the checkout the runtime serves, so the next install repairs a failed copy.
- **Held:** not yet known.
