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
