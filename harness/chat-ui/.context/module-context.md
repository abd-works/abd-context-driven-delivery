# harness/chat-ui
The chat UI is what CDD draws inside a Claude Code chat: the *cdd-board* mod in `pane/`, a Claude Code plugin whose hooks draw the chat bar above the prompt, the status line in the hint line under it, the failure line with its Fix and ✕, the server health mark and panel, the CDD version badge, and the fidelity help pane beside the chat. The mod's own card, `pane/.context/module-context.md`, says what the mod does and what it calls; this folder keeps the design and the decisions behind the chat bar, in `cdr/` (0001, the chat bar is the stage strip; 0002, the session list names the tickets its columns send), and `corrections.log`.

The prompt queue above the chat bar is another mod, `prompt-queue` in `tools/prompt_queue/hooks/`; its box goes first in the band, and its failures show on this mod's failure line.

- **Purpose:** keep the person and the agent in one chat looking at the same session: what stage and fidelities it is at, what to do next, and whether CDD is running, with each press calling the cdd server's own tool.
- **Seam (terms):** the `cdd-board` plugin (`pane/.claude-plugin/plugin.json`, `pane/hooks/register.ts`); the chat bar (`ChatBarClient`, `ChatBarView`); the status line (`ChatBarClient.statusLine`, drawn by the `PromptHint` hook and `$.ui.status`); the failure line (`FailureClient`, `fixFailure`, `dismissFailure`); the server health band (`pane/hooks/health/`); `/board`
- **Dependencies (one-way):** as the mod's card lists them: harness/chat, space/kanban, harness/diagnostics and harness/mcp, each through the cdd server's MCP tools, with their data types from the language adapter at compile time only. Nothing in Python imports this folder; harness/mcp publishes the mod from `pane/cdd-mod.json`.

## Constraint

Every rule and decision lives in the Python domain the mod calls; the mod draws what the tools answer and keeps only the last answer in `$.state` (the CDD Claude mod pattern, `cdd_guidance/patterns/cdd_claude_mod/`).

The chat bar's draw keeps every read inside its guard, so a draw that throws shows "chat bar failed to draw" in red in place of the bar: the engine skips a hook that throws, which would leave no bar and no reason.

## Tests

- Plugin tests, run by `claude plugin test pane` with the Claude Code the desktop app installed (`CLAUDE_CODE_EXECPATH`): `*.test.ts` and `*.test.tsx` beside the code they test in `pane/hooks/`. They run the mod's hooks and mount the band with the cdd server stubbed.
- `claude plugin validate pane` before the mod is published: a module the engine refuses hides the whole chat bar.
- The scenarios of epic Move Work Forward From Chat Bar are in `story_tests/move-work-forward-from-chat-bar/`. The stubbed story tests that played them were removed in 8c56ab052; where a scenario's evidence names a removed test, no test plays it now.
- The server health report the band draws is specified in Python, in `harness/diagnostics/server_health_spec.py` and `server_health_heavy_spec.py`.
