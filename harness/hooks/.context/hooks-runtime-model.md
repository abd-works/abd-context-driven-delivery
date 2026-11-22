# Hooks — object model (model fidelity)

Markdown channel for **`harness/hooks`**. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *AgentToolSet*, *AgentTool*, *ToolCall*, and *ToolsetReference* belong to `harness/agent_tools`, *Destination* and *DestinationKind* to `harness/annotations`, *RegisteredChannel*, *InstallTarget*, *InstallRecord*, *RepositoryToolsets*, and *ContextConfig* to `harness/installation`, *RunningProcess* and *ProcessNotStopped* to `harness/process`, and *Session* and its *ChatInjections* to `space/session`; they appear here only as names this module uses. *PromptLog* (`tools/prompt_log`) is one toolset whose members are hooks; it keeps its own model.

**Install** writes files. **Runtime** is the IDE running `hook_daemon.py` (the hook command) with the event's JSON on stdin; that script finds or starts one long-running *HookServer* per repository through *HookDaemon* and passes the event to it. `@Hook` and `@mcp` on the same operation remain two independent installs.

## Language companion                                             <!-- L -->

*Hook* is a *Destination* on an `AgentToolSet` member. The event name is the identity the IDE uses (`sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, …). The operation receives the event payload and returns the fields the IDE understands.

*HookServer* is the long-running process for one repository: it takes each event's stdin, finds every enabled hook for that event, runs them, merges their results, and returns one JSON object. It is not an MCP client.

A hook's result can carry a `toast`, a short notice the person sees beside the chat. It is not sent to the IDE: the hook server hands the merged toast to the notifier registered with the process's one *HookToasts* (`HOOK_TOASTS.show_with`) (`tools/prompt_notify` registers when it is loaded). `rules_toast(source, labels)` writes the toast for injected rules, and `TOAST_ARROW` separates a toast's source from the rest.

---

## Hook : Destination                                             <!-- Md -->

The `@Hook` decorator on an operation. Event is required and must be an IDE event name.

+ Hook(event: str, disabled: bool = false)
	// event is one of Hook.EVENTS; unknown names are rejected at decoration
	// the Hook kind is the hook channel; its channel string is "hook"
------
+ name: str
	// identity the IDE sends as hook_event_name
+ disabled: bool
+ EVENTS: frozenset[str]
----
+ Hook.publishes(operation): bool
	// install publishes operation as a hook: it carries @Hook, turned on, and no omission keeps it out
+ Hook.name_given(operation): str
	// the event the operation runs on; empty when it carries no @Hook
	// the Hook annotation records itself on the operation, holding its event and disabled, which DestinationKind's
	// name_given and disabled_on read (harness/annotations); Hook adds no kind of its own
	// sessionStart → session_start

## Toast : Destination

`@Toast` on an operation or instructions: nothing is written at install; the notifier the hook server shows toasts
with (`HOOK_TOASTS`, which tools/prompt_notify registers with) toasts the operation when an agent calls it.

------
----

## Hooks                                                          <!-- Md -->

Class annotation. Turns off, or keeps out of the install, every hook on that toolset.

+ Hooks(disabled: bool = false, deploy: bool = true)
------
+ disabled: bool
+ deploy: bool
	// false keeps the toolset's hooks out of hook-handlers.json
----
+ annotate(toolset_class: type): type
	// keeps itself on the class as `_hooks`; read through Hooks.from_toolset_class(type(toolset)).disabled and .deploy
	// write `@Hooks(disabled=True)` above `@agent_toolset` so the annotation stays on the registered type

## HookInstallation : RegisteredChannel                                <!-- Md -->

Install-time writer for hook artifacts. Same walk as markdown and MCP; only the leaf writes differ. It holds no server: the hook command starts the hook daemon on the first event.

+ HookInstallation(target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None)
------
+ destination = Hook
+ server: None
+ interpreter: PythonInterpreter
+ handlers_file: HookHandlersFile
+ manifest: HooksManifest
+ dispatch_command: str
	// "{console python} -u {harness/hooks}/hook_daemon.py"; HookDaemon.COMMAND_SCRIPT
+ << composition >> handlers_file: HookHandlersFile
+ << composition >> manifest: HooksManifest
+ registered_events: list[str]
	-> HooksManifest.registered_events
+ registered_operations: list[str]
	-> HookHandlersFile.operation_names
+ published: list[str]
	-> registered_operations
----
+ accepts(tool: AgentTool): bool
	// tool.is_published_to(Hook), and the layout runs hooks
+ write(tool: AgentTool): None
	// skip unless tool.is_published_to(Hook), the toolset class is not @Hooks(deploy=False), and Hook.name_given(tool.callable) is set
	// enroll each (event, operation, ref) once; ref is str(tool.toolset.reference)
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
+ status(): list[str]
	// the events and operations the install registered; the install stands up and starts no hook server

## HooksManifest                                                  <!-- Md -->

`hooks.json`: the command an IDE runs for each hook event, beside the person's own hooks.

+ HooksManifest(path: Path)
------
+ hooks: dict[str, list[dict[str, Any]]]
	// a file that is not a JSON object raises HooksFileUnreadable; an install never writes over it
+ registered_events: list[str]
----
+ write(hooks: dict[str, list[dict[str, Any]]]): None

## HookHandlersFile                                               <!-- Md -->

`hook-handlers.json`: the hook operations an install registered. The one reader and writer of the file.

+ HookHandlersFile(path: Path)
------
+ handlers: list[dict]
	// { event, operation, ref } each; a malformed file raises HooksFileUnreadable
+ refs: tuple[ToolsetReference, ...]
	// each ref parsed back from its "{module}:{Class}" text
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
	-> SESSION_OPENING.saved_in(project or checkout)
----
+ received_in(checkout: Path): HookPayload
	// itself when it already names the checkout that received it
+ edited_path(): str
	// the file Cursor's file-edit event names, else the first path its tool call names (`ToolCall.named_paths`)
+ invoked_tool: str
	// the tool the agent called: the one an IDE's MCP wrapper, such as `CallMcpTool`, names in its input, else the event's own tool
	// file_path, path, or uri; else the path inside tool_input

## HookResult                                                     <!-- Md -->

Fields the IDE reads back from the hook process.

+ HookResult(permission: str = "allow", continue_flag: bool | None = None, messages: HookMessages = HookMessages())
------
+ messages: HookMessages
	// what the hooks say back, held as made; the result keeps no copy of its texts
+ permission: str
	// deny wins when any handler returns deny
+ continue_flag: bool | None
	// false wins when any handler returns continue false
+ followup_only: bool
	// as_dict returns only followup_message
----
+ from_handler(raw: dict | None): HookResult
+ keep_context(context: str | None): None
	// the context it adds to the agent's model, in place of what it held
+ with_description(description: str): HookResult
	// prepends the tool docstring onto agent_message
+ merge(other: HookResult): HookResult
	// deny and continue false win; the messages' user_message, agent_message, and toast join with newlines, the last
	// non-empty followup_message wins, and the unique parts of additional_context join with blank lines
+ as_dict(): dict
	// the fields the IDE reads; the toast is left out

## HookMessages                                                   <!-- Md -->

What a hook says back, each part none when it says nothing there. A *HookResult* is made from one.

+ HookMessages(user_message: str | None = None, agent_message: str | None = None, followup_message: str | None = None, additional_context: str | None = None, toast: str | None = None)
------
+ user_message: str | None
+ agent_message: str | None
+ followup_message: str | None
+ additional_context: str | None
+ toast: str | None
----
+ from_handler(raw: Mapping[str, Any]): HookMessages
	// each message a handler's answer names, read as text; an empty one is none

## HookHandler                                                    <!-- Md -->

One annotated operation that may run for an event.

+ HookHandler(tool: AgentTool, repo_root: Path)
------
+ << association >> tool: AgentTool
	// name, toolset, callable, and docstring are read from the tool, and the event from Hook.name_given(tool.callable), never copied
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

+ HandlerCatalog(toolsets: list[ToolsetReference | AgentToolSet], repo_root: Path | None = None)
	// the toolsets named by their reference, or handed in made, as a spec's fake is; each is made with item.made()
	// a toolset whose @Hooks(deploy=False) keeps it out of install is left out
------
+ << composition >> toolsets: list[AgentToolSet]
	// skips toolsets whose class is annotated @hosted_only
+ repo_root: Path | None
+ failures: list[tuple[str, BaseException]]
	// a reference that does not load (bad reference, missing module or class, not a toolset, constructor mismatch)
+ event_names: list[str]
----
+ for_event(event_name: str): list[HookHandler]
	// tools_published_to(Hook) serving the event: events_served(Hook.name_given(tool.callable)), so a postToolUse hook also serves afterFileEdit

## HookToasts                                                     <!-- Md -->

How the process shows the toast a hook gives in its result: the one notifier registers itself when it is loaded, so a hook names its toast and never the notifier. The process keeps one, `HOOK_TOASTS`.

+ HookToasts()
----
+ show_with(show: Callable[[str, list[Path]], Any] | None): Callable[[str, list[Path]], Any] | None
	// answers the notifier it replaces, so a caller that registers its own for a while can put that one back
+ show(toast: str, workspace_roots: list[Path]): None
	// shows nothing when the toast is empty or no notifier is registered

## HookServer                                                     <!-- Md -->

The hooks of one checkout, loaded once in its hook daemon. It runs the enabled handlers for each event and merges their answers.

+ HookServer(repo_root: Path, catalog: HandlerCatalog)
------
+ << association >> catalog: HandlerCatalog
+ << composition >> skipped: SkippedTools
	// harness/installation's one record of what a server skipped, shared with the cdd server: skip, as_data, notice, notify
----
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
	-> SessionFolder.hook_log("dispatch.debug").stamped

## HookDaemon                                                     <!-- Md -->

The hook daemon of one checkout, a *ServerDaemon* (harness/process): it listens on the one port the checkout's daemon may hold, publishes its address, and serves every hook command with one loaded HookServer. The hook command (`run_hook_command` in `hook_daemon.py`) runs `daemon.ensure()` and then `daemon.address.handle_stdin(raw)`. A daemon that finds the port held by this checkout's daemon on older code, including one the older layout started (address in `.cursor/hook-server.json`, a ping that names no process or checkout), stops it and takes the port; anything else on the port raises *HookPortTaken*, so a daemon never exits silently. Closing a worktree stops its checkout's daemon (`Worktrees.remove` in space/repo calls `stop`).

+ HookDaemon(repo: Path, port: int | None = None)          : ServerDaemon
------
+ HOST: str
	// "127.0.0.1"
+ repo: Path
+ address: HookDaemonAddress
	// where this checkout's daemon answers: its host and its one port
+ address_file: HookDaemonAddressFile
	// .hook-server/address.json in the checkout, the running daemon's address; it belongs to no IDE folder
- _older_layout_file: HookDaemonAddressFile
	// .cursor/hook-server.json, read only to find and stop a daemon the older layout started
+ port: int
	// the one port this checkout's daemon may listen on, from the checkout's path
+ source_stamp: str
	// identity of the hook code the checkout holds now
----
+ running(): RunningServer | None
	// this checkout's daemon when one answers a ping on its port as this checkout's
+ is_running(): bool
+ ensure(): RunningServer
	// replace a daemon on older code, then the running one, or start one (one hook command at a time, ServerDaemon's start lock) and wait for it
	-> _replace_stale
	-> ServerDaemon.ensure
- _replace_stale(): None
	-> RunningProcess.stop
+ stop(): None
	// stop the daemon answering on the port as this checkout's, or as one of the older layout; remove both address files
+ spawn(): RunningProcess
	// ServerDaemon's; the daemon imports from the checkout, through RepositoryToolsets.pythonpath and pycache_prefix
+ serve(server: HookServer | None = None): None
	// answers pings at once with its address; with no server, loads every toolset class the repository defines first
	-> claim_port
	-> HookServer.from_repository(self.toolsets)
+ claim_port(): socket | None
	// the port, taken over from this checkout's daemon on older code; none when its daemon on this code holds it
	-> ExclusivePort.claim
	-> HookDaemonAddress.running
	-> ExclusivePort.holder
	// raises HookPortTaken for a process that is not this checkout's daemon, or one that will not stop

## HookDaemonAddress                                              <!-- Md -->

Where a hook daemon answers. The address file holds these fields with who the daemon is, and a ping answers them.

+ HookDaemonAddress(host: str, port: int)
------
+ host: str
+ port: int
----
+ running(): RunningServer | None
	// the daemon answering here, as it reports itself (its process, checkout, and code stamp); a daemon of the older layout reports none of them
+ handle_stdin(raw: bytes): dict

## HookDaemonAddressFile                                          <!-- Md -->

The file a daemon publishes its address and itself in: `address()`, `server()` (a *RunningServer*), `write(address, server)`, `remove()`.
---

## Installed artifacts                                            <!-- Mu -->

```
{Installer.path}/                 typically .cursor/
  hooks.json                      HooksManifest — event → hook_daemon.py command
  hook-handlers.json              HookHandlersFile
.hook-server/                    HookDaemon.folder — address.json, server.log, start.lock
.sessions/{name}/logs/            dispatch.debug, prompt-log.txt (in the session's work folder)
.sessions/{name}/chat-injections/ ChatInjections (space/session)
```
