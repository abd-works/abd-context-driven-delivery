# Grill Answers — inject rules into chat

### No extra install step

`Installer.install` does not grow a special rules-inject walk. `@Hook` on the new operation is enough: `HookInstallation.write` already enrolls it into `hooks.json` and `hook-handlers.json`, same as `PromptLog` / `PromptEcho`.

### Two operations on existing types — installation unchanged

Do not add `RulesInstallation`. Do not change `HookInstallation` or `Installer.install`. `@Hook` on the two operations is enough for the existing enroll walk.

- **`Guidance.inject_rules`** — `@Hook("preToolUse")`. Body is **`rules_markdown`** (the formatted string `@rules` already produces). Not `RulesCollection`. Glob still comes from that host’s `appliesTo` / deployed front matter.
- **`GuidanceAction.inject_rules`** — `@Hook("postToolUse")`. After the action tool returns. Skip `Document`. `additional_context` is the listed Guidances’ `rules_markdown`. Concrete actions inherit the one method.

Tab / `afterTabFileEdit` is out. Direct edit means the **agent** Write / StrReplace from chat.

Cursor docs ([hooks](https://cursor.com/docs/hooks)):
- `beforeSubmitPrompt` cannot inject. Output is only `continue` + `user_message`. Staff confirmed no `additional_context` / `updated_input` on that event.
- `preToolUse` `agent_message` is documented **only when permission is deny**. Allow does not feed rules into the model.
- `postToolUse` is the event whose output includes **`additional_context`** (“injected into the conversation after the tool result”). That is the field that actually reaches the next model step.
- `beforeMCPExecution` sees `tool_name` / `mcp_server_name` before generate/sketch/iterate run. Its `agent_message` is not qualified as deny-only. Not in our `Hook.EVENTS` yet.
- `afterFileEdit` is after the agent already wrote — too late to change that edit. It is agent-only (not Tab).

Recommended pair:
1. **Actions** — `@Hook("postToolUse")` when the tool is an action MCP/skill except document. After generate/sketch/iterate/partition (and validate/satisfy if we keep them) return, `additional_context` is the guidance rules. The agent has not started Write yet.
2. **Agent file edits** — `@Hook("preToolUse")` for Write / StrReplace (and the edit-notebook tool). Glob `tool_input` path against rule front matter. Because allow cannot inject, the reliable companion is **`postToolUse` after Read** of that path (`additional_context` for the matching `.mdc`). Write-without-Read is the hole Cursor left; the documented hammer is deny-once with `agent_message` holding the rules.
