# Hooks — object model (model fidelity)

Markdown channel for **`harness/hooks`**. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *AgentToolSet* and *AgentTool* belong to `harness/agent_tools`, *Destination* and *Installation* to `harness/installation`, *Session* to `space/session`, *Repo* to `space/repo`, and *ContextConfig* to `space/context_config`; they appear here only as names this module uses. *PromptLog* (`tools/prompt_log`) is one toolset whose members are hooks; it keeps its own model.

**Install** writes files. **Runtime** is the IDE running `hook_server.py` with the event's JSON on stdin; that script finds or starts one long-running *HookServer* per repository through *HookDaemon* and passes the event to it. `@Hook` and `@mcp` on the same operation remain two independent installs.

## Language companion                                             <!-- L -->

*Hook* is a *Destination* on an `AgentToolSet` member. The event name is the identity the IDE uses (`sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, …). The operation receives the event payload and returns the fields the IDE understands.

*HookServer* is the long-running process for one repository: it takes each event's stdin, finds every enabled hook for that event, runs them, merges their results, and returns one JSON object. It is not an MCP client.

---

## Hook : Destination                                             <!-- Md -->

The `@Hook` decorator on an operation. Event is required and must be an IDE event name.

+ Hook(event: str, disabled: bool = false)
	// event is one of Hook.EVENTS; unknown names are rejected at decoration
------
+ name: str
	// identity the IDE sends as hook_event_name
+ disabled: bool
+ EVENTS: frozenset[str]
----
+ annotate(operation): operation
	// sets the hook mark; disabled sets _hook_disabled
+ companion_flags(): tuple[str, ...]
	// the destination's flags plus _hook_disabled
+ disabled_on(operation): bool
	// the one reader of the disabled mark
+ normalize_event(event: str): str
	// sessionStart → session_start

## Hooks                                                          <!-- Md -->

Class annotation. Turns off, or keeps out of the install, every hook on that toolset.

+ Hooks(disabled: bool = false, deploy: bool = true)
------
+ disabled: bool
+ deploy: bool
	// false keeps the toolset's hooks out of hook-handlers.json
----
+ annotate(toolset): toolset
	// sets _hooks_disabled and _hooks_deploy
	// write `@Hooks(disabled=True)` above `@agent_toolset` so the mark stays on the registered type

## HookInstallation : Installation                                <!-- Md -->

Install-time writer for hook artifacts. Same walk as markdown and MCP; only the leaf writes differ.

+ HookInstallation(ide: str, path: Path, python: str | None = None, repo: Path | None = None)
------
+ python: str
+ server: HookServer | None
+ diagnosis: dict | None
+ dispatch_command: str
	// "{python} -u {repo}/harness/hooks/hook_server.py"
----
+ write(tool: AgentTool): None
	// skip unless tool.install_to_hook, the toolset class is not @Hooks(deploy=False), and tool.hook_event is set
	// enroll each (event, operation, ref) once
	-> write_hooks_manifest()
	-> write_handlers()
+ write_handlers(): None
	// hook-handlers.json is { handlers: [{ event, operation, ref }] }
+ write_hooks_manifest(): None
	// hooks.json version 1; one dispatch command per distinct event
	// postToolUse also installs afterFileEdit, stop, and subagentStop
	// afterAgentResponse holds only the dispatch command — the IDE runs the first entry only
	// other events keep non-dispatch commands already in the file
+ standup(): HookServer
	-> HookServer.from_handlers
+ diagnose(): dict
	-> HookServer.diagnose

## CursorEvent                                                    <!-- Md -->

Named IDE hook moment. Identity is the event string.

+ CursorEvent(name: str)
------
+ name: str
----
+ normalize(): str
	-> Hook.normalize_event

## HookPayload                                                    <!-- Md -->

The stdin JSON for one firing.

+ HookPayload(fields: dict)
+ HookPayload.from_stdin(raw: bytes): HookPayload
	// strips UTF-8 BOMs; empty or unreadable raw → allow-only result at HookServer.handle_stdin, not here
------
+ hook_event_name: str
	// empty name means no handlers run; result is permission allow
+ conversation_id: str
+ generation_id: str
----
+ edited_path(): str
	// file_path, path, or uri; else the path inside tool_input
+ as_dict(): dict
	// remaining keys (tool_name, tool_input, prompt, …) stay on the payload for the handler

## HookResult                                                     <!-- Md -->

Fields the IDE reads back from the hook process.

+ HookResult(permission: str = "allow", continue_flag: bool | None = None, user_message, agent_message, followup_message, additional_context)
------
+ permission: str
	// deny wins when any handler returns deny
+ continue_flag: bool | None
	// false wins when any handler returns continue false
+ user_message: str | None
+ agent_message: str | None
+ followup_message: str | None
	// last non-empty followup_message wins
+ additional_context: str | None
	// unique parts join with blank lines
+ followup_only: bool
	// as_dict returns only followup_message
----
+ from_handler(raw: dict | None): HookResult
+ with_description(description: str): HookResult
	// prepends the tool docstring onto agent_message
+ merge(other: HookResult): HookResult
	// deny and continue false win; user_message and agent_message join with newlines
+ as_dict(): dict

## HookHandler                                                    <!-- Md -->

One marked operation that may run for an event.

+ HookHandler(tool: AgentTool, event: CursorEvent, repo_root: Path)
------
+ event: CursorEvent
+ << association >> tool: AgentTool
	// name, toolset, callable, hook_event, and docstring are read from the tool, never copied
+ repo_root: Path
+ label: str
	// {toolset class}.{tool.name}, for the dispatch log and skipped handlers
----
+ is_enabled(payload: HookPayload | None = None): bool
	// false when the toolset class is marked @Hooks(disabled=True)
	// a toolset with a `pattern` runs only where that guideline is enabled for the edited file
	-> ContextConfig.guideline
+ invoke(payload: HookPayload): HookResult
	// call tool.callable with payload.as_dict()
	// agent_message includes tool.docstring unless additional_context is already set
	-> HookResult.from_handler
	-> HookResult.with_description

## HandlerCatalog                                                 <!-- Md -->

The toolsets whose hooks the server runs.

+ HandlerCatalog(toolsets: list | None = None, repo_root: Path | None = None, handlers: Path | None = None)
	// given handlers file, given toolsets, else .cursor/hook-handlers.json, else Installer.collect_toolsets
------
+ << composition >> toolsets: list[AgentToolSet]
	// skips toolsets named in AgentToolSet.HOSTED_ONLY_CLASS_NAMES
+ repo_root: Path | None
+ failures: list[tuple[str, BaseException]]
----
+ refs_from_handlers(handlers: Path): tuple[str, ...]
+ ref_label(item): str
+ for_event(event: CursorEvent): list[HookHandler]
	// tools_for(HOOK) whose hook_event matches the event; inject_rules marked postToolUse also serves afterFileEdit

## HookStandupFailed : Exception                                  <!-- Md -->

The hook server could not stand up or failed diagnose.

+ HookStandupFailed(operation: str, server: HookServer | None, message: str, cause: BaseException | None = None)
------
+ operation: str
+ server: HookServer | None
+ cause: BaseException | None
----

## HookIllegitimateHandler : Exception                            <!-- Md -->

One hook handler was skipped so the hook server could finish standup.

+ HookIllegitimateHandler(tool: str, reason: str, cause: BaseException | None = None)
------
+ tool: str
+ reason: str
+ cause: BaseException | None
----

## HookServer                                                     <!-- Md -->

The long-running process that answers every hook call for one repository. `hook_server.py` calls `HookServer.ensure(repo).handle_stdin(raw)`.

+ HookServer(repo_root: Path, catalog: HandlerCatalog | None = None, host: str | None = None, port: int | None = None)
	// with a port, this object is a client of the running daemon and forwards stdin to it
------
+ << association >> catalog: HandlerCatalog
+ exceptions: list[HookIllegitimateHandler]
+ session: Session
	// the session open in .sessions/session.json (main when none), read for each event
	-> Sessions.saved
----
+ state_path(repo: Path): Path
	// .cursor/hook-server.json, the running daemon's address
+ ensure(repo: Path): HookServer
	// replace a daemon on older code, connect to the live one, or spawn one and wait for it
	-> HookDaemon.replace_stale
	-> HookDaemon.live_address
	-> HookDaemon.spawn
+ handle_stdin(raw: bytes): HookResult
	// empty or unreadable raw → permission allow
	-> HookPayload.from_stdin
	-> dispatch(payload)
+ run(): None
	// print handle_stdin(stdin) as JSON
+ dispatch(payload: HookPayload): HookResult
	// no event → permission allow
	-> HandlerCatalog.for_event
	-> HookHandler.is_enabled
	-> HookHandler.invoke
	-> HookResult.merge
+ skip(tool: str, error: BaseException): None
	// records a HookIllegitimateHandler; a failing handler never stops the others
+ from_toolsets(repo_root: Path, toolsets: list | None = None): HookServer
	-> HandlerCatalog
+ from_handlers(handlers: Path, repo: Path | None = None): HookServer
+ standup(): HookServer
	-> notify_exceptions()
+ diagnose(): dict
	-> ping()
	-> dispatch
+ ping(): str
	// "pong"
+ notice(): str
+ notify_exceptions(): None
- _append_debug(message: str): None
	// dispatch.debug in the open session's logs folder
	-> Session.hook_log

## HookDaemon                                                     <!-- Md -->

Finds, starts, checks, and serves the one hook server process for a repository over a local socket.

+ HookDaemon(host: str | None = None, port: int | None = None)
------
+ HOST: str
	// "127.0.0.1"
+ host: str
+ port: int | None
----
+ live_address(path: Path): tuple | None
	// (host, port, pid) when the address file names a daemon that answers ping
+ call_handle_stdin(raw: bytes): dict
+ spawn(repo: Path, path: Path): None
+ repo_port(repo: Path): int
	// the one port this checkout's daemon may listen on
+ serve(repo: Path, inner: HookServer | None = None): None
+ source_stamp(repo: Path): str
	// identity of the hook code this process loaded
+ replace_stale(repo: Path, path: Path): None
	// stop a daemon that loaded older hook code
	-> StoppableProcess.stop

## RunningProcess                                                 <!-- Md -->

A process on this computer by its id.

+ RunningProcess(pid: int)
------
+ pid: int
+ alive: bool
----

## StoppableProcess : RunningProcess                              <!-- Md -->

A process by its id that this one may end. An id of 0 and this process's own id are never signalled.

+ StoppableProcess(pid: int)
------
----
+ stop(wait_seconds: float): None
	// raises ProcessNotStopped when the process is still running

## ProcessNotStopped : Exception                                  <!-- Md -->

+ ProcessNotStopped(pid: int, cause: BaseException | None = None)
------
+ pid: int
+ cause: BaseException | None
----

---

## Installed artifacts                                            <!-- Mu -->

```
{Installer.path}/                 typically .cursor/
  hooks.json                      CursorEvent → hook_server.py command
  hook-handlers.json              HandlerCatalog
  hook-server.json                HookServer.state_path — the running daemon's address
.sessions/{name}/logs/            dispatch.debug, prompt-log.txt
```
