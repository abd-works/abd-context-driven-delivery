# Hooks — object model (model fidelity)

Markdown channel for **`harness/hooks`**. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *AgentToolSet*, *AgentTool*, *ToolCall*, and *InstallDestination* belong to `harness/agent_tools`, *Destination* to `harness/annotations`, *Installation*, *RepositoryToolsets*, and *ContextConfig* to `harness/installation`, *RunningProcess*, *StoppableProcess*, and *ProcessNotStopped* to `harness/process`, and *Session* and its *ChatInjections* to `space/session`; they appear here only as names this module uses. *PromptLog* (`tools/prompt_log`) is one toolset whose members are hooks; it keeps its own model.

**Install** writes files. **Runtime** is the IDE running `hook_daemon.py` (the hook command) with the event's JSON on stdin; that script finds or starts one long-running *HookServer* per repository through *HookDaemon* and passes the event to it. `@Hook` and `@mcp` on the same operation remain two independent installs.

## Language companion                                             <!-- L -->

*Hook* is a *Destination* on an `AgentToolSet` member. The event name is the identity the IDE uses (`sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, …). The operation receives the event payload and returns the fields the IDE understands.

*HookServer* is the long-running process for one repository: it takes each event's stdin, finds every enabled hook for that event, runs them, merges their results, and returns one JSON object. It is not an MCP client.

A hook's result can carry a `toast`, a short notice the person sees beside the chat. It is not sent to the IDE: the hook server hands the merged toast to the notifier registered with `HookServer.show_toasts_with` (`tools/prompt_notify` registers when it is loaded). `rules_toast(source, labels)` writes the toast for injected rules, and `TOAST_ARROW` separates a toast's source from the rest.

---

## Hook : Destination                                             <!-- Md -->

The `@Hook` decorator on an operation. Event is required and must be an IDE event name.

+ Hook(event: str, disabled: bool = false)
	// event is one of Hook.EVENTS; unknown names are rejected at decoration
	// channel is InstallDestination.HOOK
------
+ name: str
	// identity the IDE sends as hook_event_name
+ disabled: bool
+ EVENTS: frozenset[str]
----
+ annotate(operation): operation
	// sets the hook annotation; disabled sets _hook_disabled
+ companion_flags(): tuple[str, ...]
	// the destination's flags plus _hook_disabled
+ disabled_on(operation): bool
	// the one reader of the disabled annotation
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
	// keeps itself on the class as `_hooks`; read through disabled_on(toolset) and deploys(toolset)
	// write `@Hooks(disabled=True)` above `@agent_toolset` so the annotation stays on the registered type

## HookInstallation : ServerInstallation                                <!-- Md -->

Install-time writer for hook artifacts. Same walk as markdown and MCP; only the leaf writes differ.

+ HookInstallation(layout: IdeLayout, path: Path, *, python: str | None = None, repo: Path | None = None)
------
+ interpreter: PythonInterpreter
+ handlers_file: HookHandlersFile
+ manifest: HooksManifest
+ daemon: HookDaemon
+ server: HookServer | None
+ diagnosis: dict | None
+ dispatch_command: str
	// "{console python} -u {harness/hooks}/hook_daemon.py"; HookDaemon.COMMAND_SCRIPT
+ << composition >> handlers_file: HookHandlersFile
+ << composition >> manifest: HooksManifest
+ registered_events: list[str]
	-> HooksManifest.registered_events
+ registered_operations: list[str]
	-> HookHandlersFile.operation_names
----
+ write(tool: AgentTool): None
	// skip unless tool.install_to_hook, the toolset class is not @Hooks(deploy=False), and tool.hook_event is set
	// enroll each (event, operation, ref) once
	-> write_hooks_manifest()
	-> write_handlers()
+ write_handlers(): None
	-> HookHandlersFile.write
+ write_hooks_manifest(): None
	// one dispatch command per distinct event; postToolUse also installs afterFileEdit, stop, and subagentStop
	// afterAgentResponse holds only the dispatch command — the IDE runs the first entry only
	// every other command the file holds stays
	-> HooksManifest.hooks
	-> HooksManifest.write
+ standup(): HookServer
	-> HookServer.from_handlers
+ diagnose(): dict
	-> HookServer.diagnose

## HooksManifest                                                  <!-- Md -->

`hooks.json`: the command an IDE runs for each hook event, beside the person's own hooks.

+ HooksManifest(path: Path)
------
+ hooks: dict[str, list[dict]]
	// a file that is not a JSON object raises HooksFileUnreadable; an install never writes over it
+ registered_events: list[str]
----
+ write(hooks: dict): None

## HookHandlersFile                                               <!-- Md -->

`hook-handlers.json`: the hook operations an install registered. The one reader and writer of the file.

+ HookHandlersFile(path: Path)
------
+ handlers: list[dict]
	// { event, operation, ref } each; a malformed file raises HooksFileUnreadable
+ refs: tuple[str, ...]
+ operation_names: list[str]
----
+ write(handlers: list[dict]): None

## HooksFileUnreadable : Exception                                <!-- Md -->

A hooks file is not the JSON object it should be; the install stops and names the file.

+ HooksFileUnreadable(path: Path, cause: Exception)

## HookPayload : Mapping[str, Any]                                <!-- Md -->

The stdin JSON for one firing. Handlers read it through the named properties; it also reads as a mapping of every field the IDE sent.

+ HookPayload(fields: Mapping, checkout: Path | None = None)
	// checkout: the checkout of the hook server that received the event
+ HookPayload.from_stdin(raw: bytes, checkout: Path | None = None): HookPayload
	// strips UTF-8 BOMs; empty or unreadable raw → allow-only result at HookServer.handle_stdin, not here
------
+ hook_event_name: str
	// empty name means no handlers run; result is permission allow
+ conversation_id: str
+ chat_id: str
	// the chat an injection belongs to: a subagent's own transcript for subagentStop, else the conversation
+ generation_id: str
+ tool_name: str
	// empty for an event about no tool
+ tool_input: dict
	// empty when the IDE sent none or sent text that is not a JSON object
+ workspace_roots: list[Path]
+ project: Path | None
	// the first workspace root, else the folder Claude Code ran in
+ session: Session | None
	// the session open in the project, else in the checkout that received the event; read once for the event
	-> ToolCall.session_in(project or checkout)
----
+ received_in(checkout: Path): HookPayload
	// itself when it already names the checkout that received it
+ edited_path(): str
	// file_path, path, or uri; else the path inside tool_input

## HookResult                                                     <!-- Md -->

Fields the IDE reads back from the hook process.

+ HookResult(permission: str = "allow", continue_flag: bool | None = None, user_message, agent_message, followup_message, additional_context, toast)
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
+ toast: str | None
	// shown beside the chat, never sent to the IDE; toasts join with newlines
+ followup_only: bool
	// as_dict returns only followup_message
----
+ from_handler(raw: dict | None): HookResult
+ with_description(description: str): HookResult
	// prepends the tool docstring onto agent_message
+ merge(other: HookResult): HookResult
	// deny and continue false win; user_message, agent_message, and toast join with newlines
+ as_dict(): dict
	// the fields the IDE reads; the toast is left out

## HookHandler                                                    <!-- Md -->

One annotated operation that may run for an event.

+ HookHandler(tool: AgentTool, repo_root: Path)
------
+ << association >> tool: AgentTool
	// name, toolset, callable, hook_event, and docstring are read from the tool, never copied
+ repo_root: Path
+ label: str
	// {toolset class}.{tool.name}, for the dispatch log and skipped handlers
----
+ is_enabled(payload: HookPayload | None = None): bool
	// false when the toolset class is annotated @Hooks(disabled=True)
	// a toolset with a `pattern` runs only where that guideline is enabled for the edited file
	-> ContextConfig.guideline
+ invoke(payload: HookPayload): HookResult
	// call tool.callable with the payload
	// agent_message includes tool.docstring unless additional_context is already set
	-> HookResult.from_handler
	-> HookResult.with_description

## HandlerCatalog                                                 <!-- Md -->

The toolsets whose hooks the server runs.

+ HandlerCatalog(toolsets: list | None = None, repo_root: Path | None = None, handlers: Path | None = None)
	// the toolsets named; a toolset whose @Hooks(deploy=False) keeps it out of install is left out
	-> HookHandlersFile.refs
------
+ << composition >> toolsets: list[AgentToolSet]
	// skips toolsets whose class is annotated @hosted_only
+ repo_root: Path | None
+ failures: list[tuple[str, BaseException]]
	// a reference that does not load (bad reference, missing module or class, not a toolset, constructor mismatch)
+ event_names: list[str]
----
+ ref_label(item): str
+ for_event(event_name: str): list[HookHandler]
	// tools_for(InstallDestination.HOOK) serving the event: Hook.events_served(hook_event), so a postToolUse hook also serves afterFileEdit

## HookServer                                                     <!-- Md -->

The hooks of one checkout, loaded once in its hook daemon. It runs the enabled handlers for each event and merges their answers.

+ HookServer(repo_root: Path, catalog: HandlerCatalog)
------
+ << association >> catalog: HandlerCatalog
+ << composition >> skipped: SkippedTools
	// harness/installation's one record of what a server skipped, shared with the cdd server: skip, as_data, notice, notify
----
+ show_toasts_with(show: Callable[[str, list[Path]], Any]): None
	// the notifier registers itself when it is loaded, so a hook names its toast and never the notifier
+ from_repository(toolsets: RepositoryToolsets): HookServer
	// the toolsets the hook-handlers.json of every hook-running IDE folder lists (InstalledHookHandlers), else every class the repository defines; every module is imported either way
+ from_handlers(handlers: Path, repo: Path): HookServer
	-> SkippedTools.notify()
+ handle_stdin(raw: bytes): HookResult
	// empty or unreadable raw → permission allow
	-> HookPayload.from_stdin
	-> dispatch(payload)
	// with the event's session: its ChatInjections keep the rules and replay them on beforeSubmitPrompt
	-> HookPayload.session
	-> ChatInjections.keep
	-> ChatInjections.replay
+ dispatch(payload: HookPayload): HookResult
	// no event → permission allow
	-> HookPayload.received_in(repo_root)
	-> HandlerCatalog.for_event
	-> HookHandler.is_enabled
	-> HookHandler.invoke
	-> HookResult.merge
	// then hands the merged toast to the registered notifier
+ diagnose(): dict
	-> dispatch
	-> HandlerCatalog.event_names
- _append_debug(payload: HookPayload, message: str): None
	// dispatch.debug in the logs folder of the session the event works in
	-> HookPayload.session
	-> Session.append_hook_log

## HookDaemon                                                     <!-- Md -->

The hook daemon of one checkout: it listens on the one port the checkout's daemon may hold, publishes its address, and serves every hook command with one loaded HookServer. The hook command (`run_hook_command` in `hook_daemon.py`) runs `HookDaemon(checkout).ensure().handle_stdin(raw)`.

+ HookDaemon(repo: Path, port: int | None = None)
------
+ HOST: str
	// "127.0.0.1"
+ repo: Path
+ state_path: Path
	// .hook-server/address.json in the checkout, the running daemon's address; it belongs to no IDE folder
+ port: int
	// the one port this checkout's daemon may listen on, from the checkout's path
+ source_stamp: str
	// identity of the hook code the checkout holds now
----
+ live_address(): HookDaemonAddress | None
	// the published address when a daemon answers a ping there
+ is_running(): bool
+ ensure(): HookDaemonAddress
	// replace a daemon on older code, then the live one, or start one (one hook command at a time) and wait for it
	-> replace_stale
	-> spawn
+ replace_stale(): None
	-> StoppableProcess.stop
+ spawn(): None
	// the daemon imports from the checkout, through RepositoryToolsets.pythonpath and pycache_prefix
+ serve(server: HookServer | None = None): None
	// with no server, loads every toolset class the repository defines first, so their registrations hold here
	-> HookServer.from_repository(self.toolsets)

## HookDaemonAddress                                              <!-- Md -->

Where a running hook daemon answers.

+ HookDaemonAddress(host: str, port: int, pid: int | None = None)
------
+ host: str
+ port: int
+ pid: int | None
----
+ answers(): bool
+ handle_stdin(raw: bytes): dict

---

## Installed artifacts                                            <!-- Mu -->

```
{Installer.path}/                 typically .cursor/
  hooks.json                      HooksManifest — event → hook_daemon.py command
  hook-handlers.json              HookHandlersFile
.hook-server/                    HookDaemon.folder — address.json, server.log, spawn.lock
.sessions/{name}/logs/            dispatch.debug, prompt-log.txt
.sessions/{name}/chat-injections/ ChatInjections (space/session)
```
