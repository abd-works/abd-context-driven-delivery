# Install failure themes

Grouped by cause from every `install-failures.md` under `.sessions/` (CDD checkout) and `C:\dev\pml-web\.sessions\main\install-failures.md`, plus `installs[]` in `diagnostics.json`. Update a theme in place when it recurs.

## 1. Installer started under the wrong Python (3.11 from another tool's venv)

- **Seen:** 2 times, both 2026-11-27, on `babac3c18`: `/install-latest` from the CDD main chat; `/harness:installation:install` from the pml-web chat.
- **Signature:** `SyntaxError: invalid syntax` at `type CollectionEntry = object` (`harness/agent_tools/agent_tools.py:25`) while importing `harness.hooks`.
- **Cause:** the bare `python` on PATH is `C:\Users\thoma\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (3.11.15). CDD needs 3.12+. The slash commands tell the chat to run `python …install.py`, and `install-latest.py` passes on `sys.executable`.
- **Fix that worked:** run with the interpreter `~/.cdd/runtime.json` pins, `C:\dev\abd-context-driven-delivery\.venv\Scripts\python.exe`. Held both times.
- **Recurring, so propose a code fix:** have `scripts/install.py` and `install-latest.py` check `sys.version_info >= (3, 12)` before any import and re-exec under `runtime.json`'s `python` (or fail with that path in the message), and have the install commands name that interpreter instead of bare `python`.

## 2. Windows file locks while copying into the runtime or plugin folders

- **Seen:** 2 times, 2026-11-13 (`3404eaf9d`, `6f2a51c7a`).
- **Signature:** `WinError 32` (file in use) on a plugin hook copy; `WinError 183` / `WinError 5` on `language-adapters` copytree.
- **Cause:** a running chat bar mod or app process holds files open in the published copy.
- **Fix that worked:** rerun (WinError 32); `copytree(..., dirs_exist_ok=True)` and copying on every install (WinError 183). Code fix held: not seen since.

## 3. Chat loses the cdd server when the header helper fails during a runtime swap

- **Seen:** 1 time, 2026-11-13 (`3404eaf9d` → `7a6dbab88`).
- **Signature:** `no connected MCP tool "board.overview"`; MCP status `Dynamic Client Registration rejected (HTTP 404)`.
- **Cause:** `~/.cdd/connect.py` printed no headers while `~/.cdd/runtime` was being swapped; the 401 was read as an OAuth challenge.
- **Fix that worked:** the 400 / connect.py fix (`6f2a51c7a`), reinstall, `/reload-plugins`. Held.

## 4. Chat outside a main checkout gets 0 cdd tools: the dev lane serves a stale feature (related, not an install failure)

- **Seen:** 1 time, 2026-11-27, pml-web chat; stable lane `babac3c18`, dev lane `file-manager` @ `aa4cd18` (pinned 2026-11-16, merged to main ~1,150 commits ago; worktree `C:\dev\abd-cdd-file-manager` still on disk).
- **Signature:** chat bar `no connected MCP tool "board.overview"`; plugin connected with `tool_count: 0`; `session.err` logs `ToolNotEnrolled: cdd.list_tools is not a tool the cdd server publishes` from `~/.cdd/dev/runtime`.
- **Cause:** `ServerLanes.for_project` sends any non-main-checkout project to the dev lane; the stable lane asks it for `cdd.list_tools` (added `1f802aac5`, 2026-11-17), which the older dev runtime does not have. The dev lane only returns to main when the feature's worktree is gone, so a merged feature whose worktree is kept stays served indefinitely. A plain install does not touch it.
- **Fix that worked:** with the person's go-ahead, backed up and removed `~/.cdd/dev/runtime.json` and stopped the dev server (`ServerLanes().dev.daemon.stop()`), so dev-lane chats run on main. A `tools/list` with pml-web's headers then returned 295 tools including `board.overview`; the chat needs `/reload-plugins` to drop its cached empty listing. Code fix to propose: return the dev lane to main when its served branch is merged into main (not only when the worktree is gone), and fall back to the stable lane's own tools when the dev lane rejects `cdd.list_tools`.
