# harness/hooks

A *Hook* annotation makes a member answer an IDE event; the *HookServer* of a checkout runs every enabled hook for a *HookPayload* and merges their *HookResult*, and the *HookDaemon* keeps that server running. *HookInstallation* is the hook channel's server installation, registered with the Installer when the package is imported. The whole model of this module, internals included, is `harness/hooks/.context/hooks-runtime-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a toolset member answer IDE events, through one hook server per checkout that runs every hooked member and merges their answers.
- **Seam (terms):** Hook, Toast, Hooks, HookPayload, HookResult, HookServer, HookDaemon, HookInstallation; `rules_toast`, `TOAST_ARROW`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/process

## Hook : Destination

`@hook("event")` on an operation: install adds the hook command for that IDE event to `{ide}/hooks.json` and lists the operation in `hook-handlers.json`; the hook server runs it when the IDE fires the event.

------
+ EVENTS: frozenset[str]
----
+ events_served(event: str): tuple[str, ...]

## Toast : Destination

`@Toast` on an operation or instructions: nothing is written at install; the notifier the hook server shows toasts with (tools/prompt_notify) shows a toast naming the operation when an agent calls it.

------
----

## Hooks : Annotation

`@Hooks(disabled=..., deploy=...)` on a toolset class: turns off, or keeps out of install, every hook operation the toolset has.

------
----
+ annotate(toolset_class: type): type
+ disabled_on(toolset: Any): bool
+ deploys(toolset: Any): bool

## HookPayload : Mapping[str, Any]

The fields an IDE sends on stdin for one firing of a hook, such as the tool that just ran and its input, and the tool call and session that firing works in.

+ HookPayload(fields: Mapping[str, Any], checkout: Path | None = None)
------
+ hook_event_name: str
+ conversation_id: str
+ generation_id: str
+ tool_name: str
+ tool_input: dict[str, Any]
+ workspace_roots: list[Path]
+ project: Path | None
+ << composition >> call: ToolCall
	// made once per event, so every handler of the event opens the same session
+ chat_id: str
+ session: Any
+ is_edit: bool
+ invoked_tool: str
----
+ from_stdin(raw: bytes, checkout: Path | None = None): HookPayload
+ received_in(checkout: Path): HookPayload
+ edited_path(): str
---<<creates>>--> ToolCall
---<<calls session_in on>>--> ToolCall

## HookResult

The fields a hook answers the IDE with (`permission`, `continue`, the user and agent messages, `additional_context`), and a `toast` the notifier shows; the results of every hook on one event merge into one.

+ HookResult(permission: str = 'allow', continue_flag: bool | None = None, user_message: Any = None, agent_message: Any = None, followup_message: Any = None, additional_context: Any = None, toast: Any = None)
------
+ permission: str
+ continue_flag: bool | None
+ user_message: Any
+ agent_message: Any
+ followup_message: Any
+ additional_context: Any
+ toast: Any
+ followup_only: bool
----
+ from_handler(raw: Mapping[str, Any] | None): HookResult
+ with_description(description: str): HookResult
+ merge(other: HookResult): HookResult
+ as_dict(): dict[str, Any]

## HookToasts

How the process shows the toast a hook gives in its result: the one notifier, which registers itself when it is loaded. The process keeps one, `HOOK_TOASTS`.

+ HookToasts()
------
+ shown_by: Callable[[str, list[Path]], Any] | None
----
+ show_with(show: Callable[[str, list[Path]], Any] | None): None
+ show(toast: str, workspace_roots: list[Path]): None

## HookServer

The hooks of one checkout, loaded once: it runs the enabled handlers for each event and merges their answers.

+ HookServer(repo_root: Path, catalog: HandlerCatalog)
------
+ << composition >> skipped: SkippedTools
----
+ from_repository(toolsets: RepositoryToolsets): HookServer
+ from_handlers(handlers: Path | str, repo: Path | str): HookServer
+ handle_stdin(raw: bytes): HookResult
+ dispatch(payload: HookPayload): HookResult
+ diagnose(): dict[str, Any]
---<<shows each merged result's toast through>>--> HookToasts
---<<loads>>--> HookPayload
---<<merges>>--> HookResult
---<<runs the members annotated>>--> Hook
---<<skips the members annotated>>--> Hooks
---<<loads the toolsets of>>--> RepositoryToolsets
---<<reads which guideline applies from>>--> ContextConfig

## HookDaemon

The long-running hook server of one checkout, whichever IDE's hook command reaches it; it keeps its address, log, and start lock in the checkout's `.hook-server/` folder.

+ HookDaemon(repo: Path | str, port: int | None = None)
------
+ repo: Path
+ << composition >> toolsets: RepositoryToolsets
+ folder: Path
+ log_path: Path
+ port: int
+ source_stamp: str
----
+ live_address(): HookDaemonAddress | None
+ is_running(): bool
+ ensure(): HookDaemonAddress
	// starts the daemon, or replaces one that loaded older hook code, and answers its address
+ replace_stale(): None
+ stop(): None
+ spawn(): None
+ serve(server: HookServer | None = None): None
+ claim_port(): socket.socket | None
---<<creates>>--> BackgroundStart
---<<creates>>--> PythonInterpreter
---<<loads>>--> HookServer
---<<handles stdin>>--> HookServer
---<<claims its port with>>--> ExclusivePort
---<<stops older daemons as>>--> RunningProcess
---<<checks the lock holder is alive with>>--> RunningProcess
---<<raises>>--> HookPortTaken

## HookInstallation : ServerInstallation

Write the IDE's `hooks.json`, which runs the hook command for each event a hook operation serves, and `hook-handlers.json`, which lists those operations for the hook server. The install stands up, starts, and reports no hook server: the hook command starts it on the first event.

+ HookInstallation(layout: IdeLayout, path: Path | str, python: str | None = None, repo: Path | str | None = None)
------
+ interpreter: PythonInterpreter
+ dispatch_command: str
+ handlers_file: HookHandlersFile
+ manifest: HooksManifest
+ published: list[str]
+ registered_events: list[str]
+ registered_operations: list[str]
----
+ accepts(tool: AgentTool): bool
+ write(tool: AgentTool): None
+ write_handlers(): None
+ write_hooks_manifest(): None
+ status(): list[str]
---<<reads hook event of>>--> AgentTool
---<<enrolls in hooks.json>>--> Hook
---<<registers with>>--> Installer
