# Install failures

## 2026-11-13 ~19:12: install.py from the Load story editor UI chat

- **Ran:** `python scripts/install.py --ide Claude`, by hand from the Load story editor UI chat (desktop app), to regenerate the language adapters after merging `integrate-practice-content-editor-apps` into main.
- **Checkout:** `C:\dev\abd-context-driven-delivery`, branch `main`, mid-merge (merge of `8badc6467` into `3404eaf9d`, later committed as `7a6dbab88`). `~/.cdd/runtime.json` commit: `3404eaf9d`.
- **Error:**

  ```
  harness.installation.installer.ToolsetInstallFailed: install failed for <class 'cdd_guidance.actions.diagnose.diagnose.Diagnose'>: Error: [('C:\\Users\\thoma\\.cdd\\runtime\\harness\\chat-ui\\pane\\hooks\\health\\open-app-client.ts', 'C:\\Users\\thoma\\.cdd\\claude-plugins\\cdd-board\\hooks\\health\\open-app-client.ts', '[WinError 32] The process cannot access the file because it is being used by another process')]
  ```

  The merge deleted `open-app-client.ts`; the running chat bar mod still held the published copy open, so the plugin copy could not replace it.
- **Tried:** ran the same install again a few seconds later; it succeeded. Cleared.
- **Diagnostics:** `/harness-diagnostics-agent-tools-diagnostics` not run: this chat's cdd MCP connection was down (its header helper had failed, so Claude Code fell back to OAuth: "Dynamic Client Registration rejected (HTTP 404)"). Themes updated from logs alone.

## 2026-11-13 ~18:13–19:30: this chat lost the cdd server

- **Symptom:** the chat bar showed `The board did not answer: cdd-board: $.mcp.call: no connected MCP tool "board.overview" on a server named "plugin:cdd:cdd"`; `/reload-plugins` did not bring it back. The session's MCP status said `plugin:cdd:cdd: "Dynamic Client Registration rejected (HTTP 404): Not Found"`.
- **Runtime:** pinned to `3404eaf9d`; checkout and origin/main at `7a6dbab88`.
- **Cause:** the cdd plugin's `headersHelper` (`~/.cdd/connect.py`) exits with an error, printing no headers, when it cannot read the runtime it imports, such as while an install is swapping `~/.cdd/runtime` (last swapped 18:13, server restarted 19:17). The request then reaches `127.0.0.1:47800/mcp` without `X-CDD-Project`, the server answers 401, and Claude Code treats the 401 as an OAuth challenge: `/.well-known/oauth-protected-resource` is 404, so registration fails and the server is marked failed for the chat.
- **Tried:** ran the helper by hand (works, 1.5 s); probed the server with the header (200, `board.overview` listed); reinstalled, pinning the runtime to `7a6dbab88`; asked the person to `/reload-plugins`.

## 2026-11-13 ~19:50: install.py from the CDD main session chat

- **Ran:** `python scripts/install.py --ide Claude`, by hand from the CDD main session chat, after pulling origin/main and committing the 400 / connect.py fix.
- **Checkout:** `C:\dev\abd-context-driven-delivery`, branch `main`, commit `6f2a51c7a`. `~/.cdd/runtime.json` commit before: `7a6dbab88`; after: `6f2a51c7a` (the pin itself succeeded).
- **Error:**

  ```
  File "scripts\install.py", line 110, in _write_runtime_adapters
    shutil.copytree(source, target)
  FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'C:\Users\thoma\.cdd\runtime\.claude\language-adapters'
  ```

  `shutil.rmtree(target, ignore_errors=True)` removed the files but not the folders (`PermissionError: [WinError 5] Access is denied` on `...\typescript\harness\chat`), which a process started from the runtime still held open, so the copy found the folder there. The runtime's language adapters were left empty, so any app started from the runtime could not import `@cdd/cdd-connection`.
- **Tried:** `copytree(..., dirs_exist_ok=True)`, so the copy writes into folders that are still held; and the copy now runs on every install from the checkout the runtime serves, not only on the install that pins it, so the next install repairs a pin whose copy failed. Reinstalled: cleared, `runtime language adapters: copied`.
- **Diagnostics:** `/harness-diagnostics-agent-tools-diagnostics` not run: this chat's cdd MCP connection is down (the 401 / OAuth failure above), so the MCP call cannot be made until `/reload-plugins`. Themes updated from logs alone.
