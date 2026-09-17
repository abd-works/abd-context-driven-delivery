# Hooks runtime — object model (model fidelity)

Markdown channel for **`primitives/hooks`**. Requirements are the live install mark, `HookInstallation` artifacts, and the Cursor process (`hook_server.py` and the `@hook` toolsets). This file names the resources those files implement; it does not add a second hook decorator or a second installer.

**Install** writes files. **Runtime** is Cursor launching `hook_server.py` with stdin JSON. `@hook` and `@mcp` on the same operation remain two independent installs.

## Language companion                                             <!-- L -->

*Hook* is an operation on an `AgentToolSet` that Cursor may call when a named IDE event fires. The event name is the identity Cursor uses (`sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, …). The operation receives the event payload and returns the fields Cursor understands (`permission`, `continue`, `user_message`, `agent_message`, `followup_message`).

*Dispatch* is the Cursor process: read stdin, find every enabled hook for that event, run them, merge their results, print one JSON object. It is not an MCP client.

## Modules                                                        <!-- Mu -->

Build order: `primitives/installer` (mark + `HookInstallation`) → `primitives/hooks` (catalog, class disable, dispatch) → hook toolsets (`PromptLog`, `PromptEcho`, `workspace.Turn`)

---

# primitives/installer                                            <!-- Mu -->

- **Purpose:** Declare the hook on the operation and write Cursor’s hook files. The mark and the installment live here so install stays one walk. <!-- Mu -->
- **Seam (terms):** HookMark, HookInstallation, AgentTool <!-- Mu -->
- **Dependencies (one-way):** AgentToolSet <!-- Mu -->

## HookMark                                                       <!-- Md -->

The `@hook` decorator on an operation. Event is required and must be a Cursor event name.

+ HookMark(event: str)
	// event is one of CURSOR_EVENTS; unknown names are rejected at decoration
------
+ event: str
	// identity Cursor sends as hook_event_name
----
+ apply(operation): operation
	// sets _hook, _hook_name = event
	-> AgentTool.destinations includes hook

## HooksDisable                                                    <!-- Md -->

Class annotation. Turns off every hook on that toolset.

+ HooksDisable(disabled: bool = false)
------
+ disabled: bool
----
+ apply(toolset): toolset
	// sets _hooks_disabled
	// write `@hooks(disabled=True)` above `@agent_toolset` so the mark stays on the registered type

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
	// Cursor hooks.json version 1; one hook_server.py command per distinct event
	// afterAgentResponse holds only the dispatch command — Cursor runs the first entry only
	// other events keep non-dispatch commands already in the file

---

# primitives/hooks                                                <!-- Mu -->

- **Purpose:** Run enabled hooks for one Cursor event and return one merged result. Owns catalog load, class disable, payload parse, and result merge. <!-- Mu -->
- **Seam (terms):** CursorEvent, HookPayload, HookResult, HookHandler, HandlerCatalog, HookServer <!-- Mu -->
- **Dependencies (one-way):** primitives/installer (HookMark, HookInstallation), primitives/agent_tools (AgentToolSet), SessionLog <!-- Mu -->

## CursorEvent                                                    <!-- Md -->

Named Cursor hook moment. Identity is the event string.

+ CursorEvent(name: str)
	// name is a CURSOR_EVENTS value
------
+ name: str
----
+ normalize(): str
	// sessionStart → session_start

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

## HookHandler                                                    <!-- Md -->

One marked operation that may run for an event.

+ HookHandler(event: CursorEvent, operation: str, ref: str)
	// ref is module:Class of the AgentToolSet
------
+ event: CursorEvent
+ operation: str
+ ref: str
+ << association >> owner: type
----
+ is_enabled(): bool
	// false when owner._hooks_disabled is true
+ invoke(payload: HookPayload): HookResult
	// construct owner() and call operation(payload)
	// agent_message includes tool.docstring; the handler body owns domain work

## HandlerCatalog                                                 <!-- Md -->

Installed list of hook handlers. File is next to Cursor config: `{Installer.path}/hook-handlers.json`.

+ HandlerCatalog(toolsets: list | None = None, repo_root: Path | None = None)
	// given toolsets, or _refs_from_file, or _collect_refs — then AgentToolSet.load_toolsets
------
+ << composition >> toolsets: list[AgentToolSet]
+ repo_root: Path | None
----
- _refs_from_file(): list[str]
	// .cursor/hook-handlers.json
- _collect_refs(): list[str]
	// Installer.collect_toolsets
+ for_event(event: CursorEvent): list[HookHandler]
	// tools_for(HOOK) whose _hook_name matches the event

## HookServer                                                     <!-- Md -->

Cursor process for every hooked event. `hook_server.py` constructs `HookServer` and calls `run`.

+ HookServer(repo_root: Path, toolsets: list | None = None)
	// HandlerCatalog(toolsets, repo_root)
------
+ << association >> catalog: HandlerCatalog
+ run(): None
	// ensure default session; read stdin; print JSON HookResult
	-> HookPayload.from_stdin
	-> dispatch(payload)
+ dispatch(payload: HookPayload): HookResult
	// no event → permission allow
	-> HandlerCatalog.for_event
	-> HookHandler.is_enabled
	-> HookHandler.invoke
	-> HookResult.merged
- _append_debug(message: str): None
	// dispatch.debug under the session logs folder

---

# primitives/hooks toolsets                                       <!-- Mu -->

- **Purpose:** Domain handlers that happen to be hooks. Each is an AgentToolSet; operations carry HookMark. Dispatch does not special-case them. <!-- Mu -->
- **Seam (terms):** PromptLog, PromptEcho <!-- Mu -->
- **Dependencies (one-way):** primitives/hooks (HookPayload, HookResult), primitives/installer (HookMark) <!-- Mu -->

`Turn.auto_turn` lives on `workspace.workspace:Turn` (`afterAgentResponse`). It is a toolset in workspace, not a type in this package. `@hooks(disabled=True)` on `Turn` skips that handler.

## PromptLog                                                      <!-- Md -->

Audit what Cursor sent the model.

+ PromptLog()
------
----
+ before_submit_prompt(payload: HookPayload): HookResult
	// @hook("beforeSubmitPrompt")
+ before_read_file(payload: HookPayload): HookResult
	// @hook("beforeReadFile")
+ pre_tool_use(payload: HookPayload): HookResult
	// @hook("preToolUse")
+ subagent_start(payload: HookPayload): HookResult
	// @hook("subagentStart")
+ after_agent_response(payload: HookPayload): HookResult
	// @hook("afterAgentResponse")
	// appends to the session prompt-log.txt; beforeSubmitPrompt returns continue true

## PromptEcho                                                     <!-- Md -->

Surface a detected action name on preToolUse. `@hooks(disabled=True)` skips the handler.

+ PromptEcho()
------
----
+ on_pre_tool_use(payload: HookPayload): HookResult
	// @hook("preToolUse")

---

## Installed artifacts                                            <!-- Mu -->

```
{Installer.path}/                 typically .cursor/
  hooks.json                      CursorEvent → hook_server.py command
  hook-handlers.json              HandlerCatalog
  skills/hook-{operation}/SKILL.md
.sessions/{name}/logs/            dispatch.debug, prompt-log.txt
```

## Requirements trace (code → model)                              <!-- Mu -->

| Requirement | Code today | Model |
| ----------- | ---------- | ----- |
| Mark | `marks.hook` | `HookMark` |
| Install files | `HookInstallation.write` | `HookInstallation` |
| Catalog file | `hook-handlers.json` | `HandlerCatalog` |
| Cursor command | `dispatch.main` | `HookServer.run` |
| Find methods | `_hook_methods` | `HandlerCatalog.for_event` |
| Disable | `@hooks(disabled=True)` / `HookHandler.is_enabled` | `HooksDisable` |
| Invoke + merge | `HookServer.dispatch` | `HookHandler.invoke` + `HookResult.merged` |
| Audit / echo | `PromptLog` / `PromptEcho` | same names, as hook toolsets |
| Operation description | `HookHandler.invoke` puts `tool.docstring` on `agent_message` | `HookHandler.invoke` |
| Auto-turn | `Turn.auto_turn` | toolset in workspace |
