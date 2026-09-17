# Hooks runtime — object model (model fidelity)

Markdown channel for **`primitives/hooks`**. Requirements are the live install mark, `HookInstallation` artifacts, and the Cursor dispatch process (`dispatch.py` and the `@hook` hosts). This file names the resources those files implement; it does not add a second hook decorator or a second installer.

**Install** writes files. **Runtime** is Cursor launching `dispatch.py` with stdin JSON. `@hook` and `@mcp` on the same operation remain two independent installs.

## Language companion                                             <!-- L -->

*Hook* is an operation on an `AgentToolSet` that Cursor may call when a named IDE event fires. The event name is the identity Cursor uses (`sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, …). The operation receives the event payload and returns the fields Cursor understands (`permission`, `continue`, `user_message`, `agent_message`, `followup_message`).

*Dispatch* is the Cursor process: read stdin, find every enabled hook for that event, run them, merge their results, print one JSON object. It is not an MCP client.

## Modules                                                        <!-- Mu -->

Build order: `primitives/installer` (mark + `HookInstallation`) → `primitives/hooks` (catalog, flags, dispatch) → handler hosts (`PromptLog`, `SkillInject`, `PromptEcho`, `workspace.Turn`)

---

# primitives/installer                                            <!-- Mu -->

- **Purpose:** Declare the hook on the operation and write Cursor’s hook files. The mark and the installment live here so install stays one walk. <!-- Mu -->
- **Seam (terms):** HookMark, HookInstallation, AgentTool <!-- Mu -->
- **Dependencies (one-way):** AgentToolSet <!-- Mu -->

## HookMark                                                       <!-- Md -->

The `@hook` decorator on an operation. Event is required and must be a Cursor event name.

+ HookMark(event: str, always: bool = false)
	// event is one of CURSOR_EVENTS; unknown names are rejected at decoration
------
+ event: str
	// identity Cursor sends as hook_event_name
+ always: bool
	// true: run unless the disabled flag file exists; false: run only when the enabled flag file exists
----
+ apply(operation): operation
	// sets _hook, _hook_name = event, _hook_always = always
	-> AgentTool.destinations includes hook

## HookInstallation                                               <!-- Md -->

Install-time writer for hook artifacts. Same walk as markdown and MCP; only the leaf writes differ.

+ HookInstallation(ide: str, path: Path)
------
+ python: str
+ << composition >> handlers: list[HookHandler]
----
+ write(tool: AgentTool): None
	// skip unless tool.install_to_hook and the member has _hook_name
	-> write skill file skills/hook-{name}/SKILL.md
	-> append HookHandler(event, operation, toolset_ref)
	-> write_hooks_manifest()
	-> write_handlers()
+ write_handlers(): None
	// hook-handlers.json is { handlers: [{ event, operation, ref }] }
+ write_hooks_manifest(): None
	// Cursor hooks.json version 1; one dispatch.py command per distinct event
	// afterAgentResponse holds only the dispatch command — Cursor runs the first entry only
	// other events keep non-dispatch commands already in the file

---

# primitives/hooks                                                <!-- Mu -->

- **Purpose:** Run enabled hooks for one Cursor event and return one merged result. Owns catalog load, flags, payload parse, and result merge. <!-- Mu -->
- **Seam (terms):** CursorEvent, HookPayload, HookResult, HookHandler, HandlerCatalog, HookFlag, Dispatcher <!-- Mu -->
- **Dependencies (one-way):** primitives/installer (HookMark, HookInstallation), primitives/agent_tools (AgentToolSet), SessionLog <!-- Mu -->

## CursorEvent                                                    <!-- Md -->

Named Cursor hook moment. Identity is the event string.

+ CursorEvent(name: str)
	// name is a CURSOR_EVENTS value
------
+ name: str
----
+ normalize(): str
	// sessionStart → session_start — used in flag file names

## HookPayload                                                    <!-- Md -->

Cursor stdin JSON for one firing.

+ HookPayload.from_stdin(raw: bytes): HookPayload
	// strip UTF-8 BOM; empty or unreadable raw → allow-only result at the process, not here
------
+ hook_event_name: str
	// empty name means no handlers run; result is permission allow
+ conversation_id: str
+ fields: dict
	// remaining Cursor keys (tool_name, tool_input, prompt, …) stay on the payload for the handler
----

## HookResult                                                     <!-- Md -->

Fields Cursor reads back from the hook process.

+ HookResult(permission: str = "allow")
	// default permission is allow
------
+ permission: str
	// deny wins when any handler returns deny
+ continue: bool | None
	// false wins when any handler returns continue false
+ user_message: str | None
+ agent_message: str | None
+ followup_message: str | None
	// last non-empty followup_message wins
----
+ merge(others: list[HookResult]): HookResult
	// user_message and agent_message concatenate with newlines
	// empty handler results are skipped

## HookFlag                                                       <!-- Md -->

Enable or disable one handler without editing code.

+ HookFlag(owner: type, method: str, event: CursorEvent)
------
+ enabled_path: Path
	// .context/hooks/{owner-slug}/{method}_{normalized-event}.enabled
+ disabled_path: Path
	// same stem with .disabled
----
+ allows(handler: HookHandler): bool
	// always handlers: true unless disabled_path exists
	// opt-in handlers: true only when enabled_path exists
+ set_enabled(enabled: bool): Path
	// create or remove enabled_path

## HookHandler                                                    <!-- Md -->

One marked operation that may run for an event.

+ HookHandler(event: CursorEvent, operation: str, ref: str)
	// ref is module:Class of the AgentToolSet
------
+ event: CursorEvent
+ operation: str
+ ref: str
+ always: bool
	// read from the loaded member’s HookMark
+ << association >> owner: type
----
+ is_enabled(): bool
	-> HookFlag.allows(self)
+ invoke(payload: HookPayload): HookResult
	// construct owner() and call operation(payload)
	// the handler body owns domain work (commit, log, inject, echo)

## HandlerCatalog                                                 <!-- Md -->

Installed list of hook handlers. File is next to Cursor config: `{Installer.path}/hook-handlers.json`.

+ HandlerCatalog.load(path: Path): HandlerCatalog
	// missing or unreadable file → default refs: workspace.workspace:Turn, PromptLog, SkillInject, PromptEcho
------
+ << composition >> handlers: list[HookHandler]
----
+ for_event(event: CursorEvent): list[HookHandler]
	// members on each loaded owner whose _hook_name equals the event
+ load_hosts(hosts: list[type] | None): list[type]
	// explicit hosts win (tests); otherwise import each unique ref

## Dispatcher                                                     <!-- Md -->

Cursor process for every hooked event. One command in hooks.json: `python primitives/hooks/dispatch.py`.

+ Dispatcher()
------
+ << association >> catalog: HandlerCatalog
+ << association >> log: SessionLog
----
+ run(): None
	// chdir repo root; ensure default session; read stdin; print JSON HookResult
	-> HookPayload.from_stdin
	-> dispatch(payload)
+ dispatch(payload: HookPayload, hosts: list[type] | None = None): HookResult
	// no event → permission allow
	-> catalog.load_hosts
	-> HookHandler.is_enabled
	-> HookHandler.invoke
	-> HookResult.merge
- _append_debug(message: str): None
	// dispatch.debug under the session logs folder

---

# primitives/hooks hosts                                          <!-- Mu -->

- **Purpose:** Domain handlers that happen to be hooks. Each is an AgentToolSet; operations carry HookMark. Dispatch does not special-case them. <!-- Mu -->
- **Seam (terms):** PromptLog, SkillInject, PromptEcho <!-- Mu -->
- **Dependencies (one-way):** primitives/hooks (HookPayload, HookResult), primitives/installer (HookMark) <!-- Mu -->

`Turn.auto_turn` lives on `workspace.workspace:Turn` (`afterAgentResponse`, opt-in flag). It is a handler host, not a type in this package.

## PromptLog                                                      <!-- Md -->

Audit what Cursor sent the model. Always on unless a HookFlag disabled file exists.

+ PromptLog()
------
----
+ before_submit_prompt(payload: HookPayload): HookResult
	// @hook("beforeSubmitPrompt", always=True)
+ before_read_file(payload: HookPayload): HookResult
	// @hook("beforeReadFile", always=True)
+ pre_tool_use(payload: HookPayload): HookResult
	// @hook("preToolUse", always=True)
+ subagent_start(payload: HookPayload): HookResult
	// @hook("subagentStart", always=True)
+ after_agent_response(payload: HookPayload): HookResult
	// @hook("afterAgentResponse", always=True)
	// appends to the session prompt-log.txt; beforeSubmitPrompt returns continue true

## SkillInject                                                    <!-- Md -->

Inject a skill digest before an edit, once per conversation per file.

+ SkillInject()
------
----
+ on_pre_tool_use(payload: HookPayload): HookResult
	// @hook("preToolUse", always=True)
	// Write / StrReplace only; tag in the first twenty lines of the target file
+ on_pre_compact(payload: HookPayload): HookResult
	// @hook("preCompact", always=True)
	// drop injection state for the conversation so the next edit can inject again

## PromptEcho                                                     <!-- Md -->

Surface a detected action name on preToolUse.

+ PromptEcho()
------
----
+ on_pre_tool_use(payload: HookPayload): HookResult
	// @hook("preToolUse", always=True)
	// no-op when .context/hooks/prompt_echo.disabled exists — that file is this host’s own switch, not HookFlag

---

## Installed artifacts                                            <!-- Mu -->

```
{Installer.path}/                 typically .cursor/
  hooks.json                      CursorEvent → dispatch.py command
  hook-handlers.json              HandlerCatalog
  skills/hook-{operation}/SKILL.md
.context/hooks/{owner}/{method}_{event}.enabled
.context/hooks/{owner}/{method}_{event}.disabled
.sessions/{name}/logs/            dispatch.debug, prompt-log.txt
```

## Requirements trace (code → model)                              <!-- Mu -->

| Requirement | Code today | Model |
| ----------- | ---------- | ----- |
| Mark | `marks.hook` | `HookMark` |
| Install files | `HookInstallation.write` | `HookInstallation` |
| Catalog file | `hook-handlers.json` | `HandlerCatalog` |
| Cursor command | `dispatch.main` | `Dispatcher.run` |
| Find methods | `_hook_methods` | `HandlerCatalog.for_event` |
| Flags | `is_enabled` / `set_enabled` | `HookFlag` |
| Invoke + merge | `dispatch` / `_merge_results` | `HookHandler.invoke` + `HookResult.merge` |
| Audit / inject / echo | `PromptLog` / `SkillInject` / `PromptEcho` | same names, as handler hosts |
| Auto-turn | `Turn.auto_turn` | handler host in workspace |
