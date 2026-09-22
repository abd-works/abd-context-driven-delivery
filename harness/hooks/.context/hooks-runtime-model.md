# Hooks — object model (model fidelity)

Markdown channel for **`harness/hooks`**. Requirements are the live install mark, `HookInstallation` artifacts, and the Cursor process (`hook_server.py`). Partition: [module-context.md](module-context.md). *PromptEcho* types stay in [prompt-echo-model.md](../../tools/prompt_echo/.context/prompt-echo-model.md).

**Install** writes files. **Runtime** is Cursor launching `hook_server.py` with stdin JSON. `@Hook` and `@mcp` on the same operation remain two independent installs.

## Language companion                                             <!-- L -->

*Hook* is a *Destination* on an `AgentToolSet` member. The event name is the identity Cursor uses (`sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, …). The operation receives the event payload and returns the fields Cursor understands.

*Dispatch* is the Cursor process: read stdin, find every enabled hook for that event, run them, merge their results, print one JSON object. It is not an MCP client.

---

# harness/hooks                                                <!-- Mu -->

- **Purpose:** Mark a member `@Hook("event")` so Cursor stdin events run that Python and return one merged result. <!-- Mu -->
- **Seam (terms):** Hook, Hooks, HookInstallation, HookServer <!-- Mu -->
- **Dependencies (one-way):** installation (Destination, Installation), harness/agent_tools (AgentToolSet) <!-- Mu -->

## Hook : Destination                                             <!-- Md -->

The `@Hook` decorator on an operation. Event is required and must be a Cursor event name.

+ Hook(event: str)
	// event is one of Hook.EVENTS; unknown names are rejected at decoration
------
+ name: str
	// identity Cursor sends as hook_event_name
+ EVENTS: frozenset[str]
----
+ annotate(operation): operation
	// sets _hook, _hook_name = event
+ normalize_event(event: str): str
	// sessionStart → session_start

## Hooks                                                          <!-- Md -->

Class annotation. Turns off every hook on that toolset.

+ Hooks(disabled: bool = false)
------
+ disabled: bool
----
+ annotate(toolset): toolset
	// sets _hooks_disabled
	// write `@Hooks(disabled=True)` above `@agent_toolset` so the mark stays on the registered type

## HookInstallation : Installation                                <!-- Md -->

Install-time writer for hook artifacts. Same walk as markdown and MCP; only the leaf writes differ.

+ HookInstallation(ide: str, path: Path)
------
+ python: str
+ << composition >> handlers: list
----
+ write(tool: AgentTool): None
	// skip unless tool.install_to_hook and the member has _hook_name
	// skip inject_rules on RulesCollection and FidelityGuidance
	-> append { event, operation, ref }
	-> write_hooks_manifest()
	-> write_handlers()
+ write_handlers(): None
	// hook-handlers.json is { handlers: [{ event, operation, ref }] }
+ write_hooks_manifest(): None
	// Cursor hooks.json version 1; one hook_server.py command per distinct event
	// afterAgentResponse holds only the dispatch command — Cursor runs the first entry only
	// other events keep non-dispatch commands already in the file
+ standup(): HookServer
	-> HookServer.standup
+ diagnose(): dict
	-> HookServer.diagnose

## CursorEvent                                                    <!-- Md -->

Named Cursor hook moment. Identity is the event string.

+ CursorEvent(name: str)
	// name is a Hook.EVENTS value
------
+ name: str
----
+ normalize(): str
	// sessionStart → session_start
	-> Hook.normalize_event

## HookPayload                                                    <!-- Md -->

Cursor stdin JSON for one firing.

+ HookPayload.from_stdin(raw: bytes): HookPayload
	// strip UTF-8 BOM; empty or unreadable raw → allow-only result at HookServer.run, not here
------
+ hook_event_name: str
	// empty name means no handlers run; result is permission allow
+ conversation_id: str
----
+ as_dict(): dict
	// remaining Cursor keys (tool_name, tool_input, prompt, …) stay on the payload for the handler

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
+ additional_context: str | None
	// unique parts join with blank lines
----
+ from_handler(raw: dict | None): HookResult
+ with_description(description: str): HookResult
	// prepends tool docstring onto agent_message
+ merged(results: list[HookResult]): HookResult
	// user_message and agent_message concatenate with newlines
	// empty handler results are skipped
+ as_dict(): dict

## HookHandler                                                    <!-- Md -->

One marked operation that may run for an event.

+ HookHandler(tool: AgentTool, event: CursorEvent, repo_root: Path)
------
+ event: CursorEvent
+ operation: str
	// tool.name
+ owner: type
	// type(tool.toolset)
+ << association >> tool: AgentTool
----
+ is_enabled(): bool
	// false when owner._hooks_disabled is true
+ invoke(payload: HookPayload): HookResult
	// call the bound operation with payload.as_dict()
	// agent_message includes tool.docstring unless additional_context is already set
	-> HookResult.from_handler
	-> HookResult.with_description

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

## HookStandupFailed                                              <!-- Md -->

The hook server could not stand up or failed diagnose.

+ HookStandupFailed(operation: str, server: HookServer | None, message: str, cause: BaseException | None = None)
------
+ operation: str
+ server: HookServer | None
+ cause: BaseException | None
----

## HookIllegitimateHandler                                        <!-- Md -->

One hook handler was skipped so the hook server could finish standup.

+ HookIllegitimateHandler(tool: str, reason: str, cause: BaseException | None = None)
------
+ tool: str
+ reason: str
+ cause: BaseException | None
----

## HookServer                                                     <!-- Md -->

Cursor process for every hooked event. `hook_server.py` constructs `HookServer` and calls `run`.

+ HookServer(repo_root: Path, toolsets: list | None = None)
	// HandlerCatalog(toolsets, repo_root)
------
+ << association >> catalog: HandlerCatalog
+ exceptions: list[HookIllegitimateHandler]
----
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
+ standup(handlers: Path, repo: Path | None = None): HookServer
+ diagnose(): dict
	-> ping()
	-> dispatch
+ ping(): str
	// "pong"
- _append_debug(message: str): None
	// dispatch.debug under the session logs folder

## PromptLog                                                      <!-- Md -->

Audit what Cursor sent the model. Off while `@Hooks(disabled=True)` stays on the class.

+ PromptLog()
------
----
+ before_submit_prompt(payload: HookPayload): HookResult
	// @Hook("beforeSubmitPrompt") — appends to the session prompt-log.txt; returns continue true
+ before_read_file(payload: HookPayload): HookResult
	// @Hook("beforeReadFile")
+ pre_tool_use(payload: HookPayload): HookResult
	// @Hook("preToolUse")
+ subagent_start(payload: HookPayload): HookResult
	// @Hook("subagentStart")
+ after_agent_response(payload: HookPayload): HookResult
	// @Hook("afterAgentResponse")

---

## Installed artifacts                                            <!-- Mu -->

```
{Installer.path}/                 typically .cursor/
  hooks.json                      CursorEvent → hook_server.py command
  hook-handlers.json              HandlerCatalog
.sessions/{name}/logs/            dispatch.debug, prompt-log.txt
```
