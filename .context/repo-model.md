**Repository model**

The public seam of every module in this repository, one section per module, grouped harness, space, tools, then cdd_guidance, and lowest layer first within each group: the classes another module's production code imports, with the operations and properties those classes have in the code today, their base classes, and how they relate. Each module's own card (`{module}/.context/module-context.md`) says why a caller uses it and what the caller must honor; this document shows the shape of the types behind those cards. `.context/repo-model.drawio` is the same model rendered by the Clean Engineering practice.

Dependencies list the modules a module's production code imports today. Three run against the layering, and are named so no reader takes them for one-way: space/session imports cdd_guidance/actions (its diagnostics run generate and validate), space/kanban imports the Stories, DDD, and UX practices, and cdd_guidance/practices/agent_bdd imports space/session. No module imports another that imports it.

# harness/name

*Name* is one name, such as a class, a fidelity, or a tool, written in every case CDD needs: `StoryMap`, `story_map`, and `story-map` are the same *Name*.

- **Purpose:** Write one name in every case CDD publishes or saves it under, the same way everywhere.
- **Seam (terms):** Name
- **Dependencies (one-way):** *(none)*

## Name

*Name* is one name, such as a class, an event, or a fidelity, that CDD writes in several cases: `StoryMap`, `story_map`, and `story-map` are the same name.

+ Name(text: str)
------
+ words: list[str]
+ snake: str
+ kebab: str
+ camel: str
+ spellings: list[str]
+ title_words: list[str]
+ title_slug: str
+ title_snake: str
+ title_pascal: str
+ title_camel: str
----

# harness/marks

A *Mark* is what an author types on a class or operation; a *Destination* is a mark that says where a member is published, and an *OmissionMark* leaves a member out.

- **Purpose:** Hold the marks an author types and the channels a member is published to, below every publisher, so publishers depend on toolsets and never the other way round.
- **Seam (terms):** Mark, Destination, NamedDestination, OmissionMark, Toast
- **Dependencies (one-way):** *(none)*

## Mark

Install and discovery find what an author marked: the operations and classes a mark decorates.

------
----
+ marks(target: Any): bool

## Destination : Mark

A mark that names where a member is published: a skill, a command, a rules file, an MCP tool, or a hook.

------
+ channel: str
+ enlists_member: bool
----
+ name_marked_on(operation: Any): str
+ disabled_on(operation: Any): bool

## NamedDestination : Destination

A destination whose mark may name what it installs: `@skill("name")`, `@skill(name="name")`, or bare `@skill` for the operation's own name.

------
----

## OmissionMark : Mark

A mark that leaves what it marks out of something.

------
+ omits_install: bool
----
+ marks(target: Any): bool

## Toast : Destination

Mark an operation or instructions so the IDE shows a toast naming it when an agent calls it.

------
----

# harness/process

*BackgroundStart* and *PythonInterpreter* start a server without a console window, *StoppableProcess* ends one by its id, and *Git* runs every git command in one folder with the same time limits and errors.

- **Purpose:** Start, name, and stop the processes the framework keeps, and run git, the same way on Windows and elsewhere.
- **Seam (terms):** BackgroundStart, RunningProcess, StoppableProcess, ProcessNotStopped, PythonInterpreter, Git, RepoConnectError
- **Dependencies (one-way):** *(none)*

## BackgroundStart

How a background server is started so it keeps running without a console window.

+ BackgroundStart(breaks_away: bool = True)
------
+ creationflags: int
+ startupinfo: subprocess.STARTUPINFO | None
----
+ inside_starters_job(): BackgroundStart
+ run(command: list[str], cwd: str | Path, env: dict[str, str], log: IO[str]): subprocess.Popen

## RunningProcess

A process by its id, to ask whether it is still running.

+ RunningProcess(pid: int)
------
+ pid: int
+ alive: bool
----

## StoppableProcess : RunningProcess

A process by its id that this one may end, such as the server an address file names.

------
----
+ stop(wait_seconds: float): None
	// never signals an id of 0 or this process's own id, so a blank or stale address file cannot end the process that reads it

## ProcessNotStopped : Exception

A process was asked to stop and is still running.

+ ProcessNotStopped(pid: int, cause: BaseException | None = None)
------
----

## PythonInterpreter

One Python on this computer.

+ PythonInterpreter(executable: str | Path | None = None)
------
+ executable: Path
+ windowless: str
+ console: str
----

## Git

The git command line, run in one folder.

+ Git(folder: Path | str)
------
+ folder: Path
----
+ run(*args, env: dict[str, str] | None = None, timeout: float | None = None): str
	// every repository operation goes through run, so the time limit, the stop of a hung git, and the RepoConnectError a failure raises are the same for all of them
+ succeeds(*args): bool

## RepoConnectError : RuntimeError

Raised when git cannot be run, or a git command fails, in a clone.

------
----

# harness/markdown

*Markdown* is the prose a property loads from a file or section beside its class; *MarkdownText* reads a document's headings and sections; *Format* names the channel an artifact is written in. The whole model of this module, internals included, is `harness/markdown/.context/markdown-collection-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a class keep its words in markdown beside it, read them back typed, and convert them to HTML.
- **Seam (terms):** Markdown, MarkdownCollection, MarkdownText, FrontMatter, Format
- **Dependencies (one-way):** harness/name, harness/marks

## Markdown

The prose one property loads: the file named after the property, or the section titled after it.

+ Markdown(instance: Any, label: str, fidelity: str | None = None, format: str | None = None)
------
----
+ from_label(instance: Any, label: str, fidelity: str | None = None, format: str | None = None): Markdown
+ raw(): str
+ extract(): str
+ expand_docstring(docstring: str | None): str
+ html(): HTML
+ coerce(text: str, return_type: Any): Any
+ built_by(from_markdown: Callable[..., Any], text: str, parent: Any): Any
+ read_into(return_type: Any, build: Callable[..., Any] | None = None): Any
+ templates_path_map(): dict[str, str]
+ as_property(fn: _F): property
+ return_type_of(fn: Callable[..., Any], default: Any): Any

## MarkdownCollection

Listed or keyed extracts that keep the original markdown.

+ MarkdownCollection(entries: dict[str, Any] | list[Any] | None = None, parent: Any = None)
------
+ markdown: str
----
+ child(name: str, body: str = ''): Any
+ from_markdown(text: str, parent: Any = None): MarkdownCollection
+ from_section(markdown: Markdown, return_type: Any, parent: Any = None): Any
+ attach(instance: Any, name: str | None = None): None
+ as_property(fn: _F): property
+ markdown_collection(fn: _F | str | None = None, label: str | None = None): property | Callable[[_F], property]

## MarkdownText

A markdown document: headings, slices, and child sections.

+ MarkdownText(text: str)
------
+ yaml_fields: dict[str, Any]
+ without_yaml: str
----
+ headings(): list[tuple[int, int, int, str]]
+ slice_heading(heading: str): str
+ child_blocks(parent_heading: str): list[tuple[str, str]]
+ section_child_blocks(): list[tuple[str, str]]
+ fidelity_blocks(): list[tuple[str, str]]
+ fidelity_block(fidelity_name: str): str
+ named_subsection(heading: str): str

## FrontMatter

The settings at the top of a file: a YAML block between `---` lines, or, in a code template, the same block written as `# ---` comment lines.

+ FrontMatter(text: str)
------
+ settings: str
+ fields: dict[str, str]
+ content: str
----

## Format

*Format* is a channel an artifact is written in, such as `markdown`, `python`, or `drawio`.

+ Format(name: str | None)
------
+ name: str
+ short: str
+ extension: str
+ is_known: bool
+ is_code: bool
+ is_templated: bool
+ template_folder: str
+ template_extension: str
----
+ from_extension(extension: str): Format

# harness/agent_tools

An *AgentToolSet* is an ordinary class an agent can list and run: each `@agent_tool` member is an *AgentOperation* and each `@agent_instructions` member is *AgentInstructions*. A *ToolCall* is one call as a chat made it, with its project and chat. The whole model of this module, internals included, is `harness/agent_tools/.context/agent-tools-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let an author publish an ordinary class as operations and instructions an agent can list and use, and let every publisher read those members from one place.
- **Seam (terms):** AgentToolSet, AgentTool, AgentOperation, GuidanceAgentOperation, AgentInstructions, AgentToolMark, AgentToolSetMark, InstallDestination, OnSubject, ToolSubjectLoader, ToolCall, ChatPointer
- **Dependencies (one-way):** harness/name, harness/marks, harness/markdown

## AgentToolSet : AgentToolSetOrigin

Injected by @agent_toolset — the operations, instructions, and nested collections of one toolset as the tools it publishes.

------
+ parameter_notes: dict[str, str]
+ mode: ExpansionMode
+ toolset_collections: list[Any]
+ << composition >> operations: dict[str, AgentOperation]
+ << composition >> instructions: Mapping[str, AgentInstructions]
+ << composition >> tools: dict[str, AgentTool]
----
+ instantiate(toolset: Any = None): Any
+ from_items(items: list[Any], context: dict[str, object] | None = None): list[Any]
+ instantiate_all(items: list): list
+ child_toolsets(): None
+ tools_for(destination: str): list[AgentTool]
+ for_call(call: ToolCall): Any
+ session_for(call: ToolCall): Any

## AgentTool : AgentToolDestination

One published member of a toolset: its name in every channel, its input schema, and how a call is answered.

------
+ name: str
+ callable: Callable[..., Any]
+ toolset: AgentToolSet
+ slug: str
+ registration_name: str
+ deploy_name: str
+ mcp_name: str
+ input_schema: dict[str, Any]
+ kind: str
+ docstring: str
+ description: str
+ parameters: dict[str, str]
+ response: str | None
----
+ invoke_line(): str
+ invoke(arguments: dict[str, Any] | None = None, project: Path | str | None = None): Any
+ answer(call: ToolCall): Any
+ on(toolset: Any): AgentTool
+ should_log_session_invocation(arguments: dict[str, Any] | None): bool
+ log_session_invocation(call: ToolCall): None

## AgentOperation : AgentTool

An `@agent_tool` member: an operation an agent calls and gets a result from.

------
+ kind: str
----

## GuidanceAgentOperation : AgentOperation

An `@agent_tool` on a guidance action: its call is logged as the action, such as `render`, rather than as a `tool …` line.

------
----
+ log_session_invocation(call: ToolCall): None

## AgentInstructions : AgentTool

An `@agent_instructions` operation: its recipe body, expanded for a call, is the instructions an agent follows.

------
+ kind: str
+ prompt: tuple[str, ...]
+ tools: list[str]
+ result_template: str
----
+ for_callable(callable: Callable[..., Any], instance: AgentToolSet | None = None): AgentInstructions
+ answer(call: ToolCall): str
+ expand(arguments: dict[str, Any]): ExpansionResult
+ members_of(target: Any): ToolsetMembers
+ member_of(target: Any, member: str): AgentInstructions
+ provider_of(owner: Any, provider_name: str): Any
+ parent_recipe(after_class: type | None = None): tuple[AgentInstructions, type] | None

## AgentToolMark : Mark

Mark a method as a tool; description comes from the method docstring.

------
----

## AgentToolSetMark : _ClassJoiningMark

Mark a class as an agent toolset — @agent_tool and @agent_instructions.

------
----

## InstallDestination

The channels a member is published to, in the order a tool lists them.

------
----

## OnSubject : Mark

Set on the tool made from an instance operation of a `@tool_subject` class: it loads its object from its leading arguments before it runs the operation.

------
----

## ToolSubjectLoader

How a domain class marked `@agent_toolset` finds the object a tool call acts on: its `@tool_subject` classmethod.

+ ToolSubjectLoader(toolset_class: type)
------
+ loader: Callable[..., Any] | None
----
+ on_subject(load: Callable[..., Any], operation: Callable[..., Any]): Callable[..., Any]
+ given_the_called_project(operation: Any): Any

## ToolCall

One call of a tool as its caller made it: the arguments it sent, the folder of the project the calling chat works on, and that chat.

+ ToolCall(arguments: dict[str, Any] | None = None, project: Path | str | None = None, chat: ChatPointer | None = None, tool: str = '', mcp_host: Any = None)
------
+ arguments: dict[str, Any]
+ project: Path
+ << association >> chat: ChatPointer | None
+ tool: str
+ identity: str
+ session: Any
	// the session open in this call's own project, never the one the process worked on last; a call that names no project works in no session
----
+ sent(arguments: dict[str, Any] | None, project: Path | str | None, tool: str = '', mcp_host: Any = None): ToolCall
+ open_sessions_with(opener: SessionOpener): None
+ session_named(session_file: str): Any

## ChatPointer

Which chat a tool call, and the session.log line it writes, came from, so `read_loop` can put that chat's words back under the line.

+ ChatPointer(id: str, transcript: Path | None = None, lines: str = '')
------
+ id: str
+ transcript: Path | None
+ lines: str
+ is_missing: bool
+ line_range: tuple[int, int]
----
+ of(chat_id: str, transcript: str | Path | None, lines: str = ''): ChatPointer | None
+ taken_from(arguments: dict[str, object] | None): tuple[ChatPointer | None, dict[str, object]]
+ from_claude_chat(chat_id: str): ChatPointer | None
+ in_log_line(line: str): ChatPointer | None
+ in_chat_file(path: Path): tuple[ChatPointer, str]
+ transcript_text(): list[str]

# harness/installation

An *Installation* writes one channel (skills, commands, rules, language adapters) for one IDE, laid out by its *IdeLayout*; *RepositoryToolsets* finds every toolset a repository defines.

- **Purpose:** Give every channel the writer it publishes a member with, and find the toolsets a repository defines.
- **Seam (terms):** Installation, FileInstallation, LanguageAdapterInstallation, IdeLayout, RepositoryToolsets, ContextConfig, Skill, SourceFile, NoCatalog
- **Dependencies (one-way):** harness/name, harness/marks, harness/agent_tools, harness/markdown

## Installation

Write one channel for one IDE; each channel overrides `write`.

+ Installation(ide: str, path: Path | str, toolset_ref: str = '', repo: Path | str | None = None)
------
+ ide: str
+ path: Path
+ toolset_ref: str
+ repo: Path | None
----
+ track_writes_with(tracker: InstallTracker): None
+ track_write(dest: Path): None
+ folder_for(toolset: Any): Path
+ install(tool: Any): None
+ write(tool: Any): None

## FileInstallation : Installation

Write the markdown files of one channel — skills, slash commands, or rules — where the IDE reads them.

+ FileInstallation(ide: str, path: Path | str, destination: str = '', mcp_mode: bool = False, repo: Path | str | None = None)
------
----
+ relative_path(toolset: Any, name: str): Path
+ write(tool: AgentTool): None
+ write_standing_rule(source: Path): None

## LanguageAdapterInstallation : Installation

Records marked toolsets during the install walk, then writes them together, because their files import each other.

+ LanguageAdapterInstallation(ide: str, path: Path | str, toolset_ref: str = '', repo: Path | str | None = None)
------
----
+ record(toolset: Any): None
+ write_all(): list[Path]

## IdeLayout

How one IDE lays out the folder CDD installs into: the folder's name in a project, where its slash commands and rules go, and the shape of a rule file.

+ IdeLayout(ide: str)
------
+ folder_name: str
+ is_claude_code: bool
+ rule_suffix: str
+ commands_folder: str
+ nests_skills: bool
+ scopes_rules_by_paths: bool
+ runs_hooks: bool
+ user_settings_folder: Path | None
+ user_mcp_config: Path | None
+ mcp_servers_key: str
+ names_mcp_transport: bool
----

## RepositoryToolsets

*RepositoryToolsets* finds every toolset class in one repository by reading its source, without importing it, and puts the folders that load those classes on the import path.

+ RepositoryToolsets(root: Path | str)
------
+ root: Path
----
+ import_path_entries(): list[str]
+ pythonpath(): str
+ pycache_prefix(): str
+ use_for_this_process(): None
+ ensure_import_path(): None
+ import_modules(): list[str]
+ collect(): list[str]
	// reads the repository's source without importing it, so the installer, the hook server, and the MCP host publish the same toolsets

## ContextConfig

One project's `.context/config.json`: the guidelines that apply to it, each `enabled` or `disabled`, and the folder each practice writes in.

+ ContextConfig(root: Path | str)
------
+ root: Path
+ path: Path
----
+ exists(): bool
+ load(): dict[str, Any]
+ save(configuration: Mapping[str, Any]): Path
+ update(**sections): dict[str, Any]
+ guidelines(): dict[str, str]
+ practice_folders(): dict[str, str]
+ guideline(pattern: str): str
+ practice_folder(practice: str): str | None
+ set_guidelines(guidelines: Mapping[str, str] | str): dict[str, Any]
+ set_practice_folders(folders: Mapping[str, str] | str): dict[str, Any]

## Skill : NamedDestination

Mark an operation to be published as a skill.

------
----

## SourceFile

Marks a data field that holds a path in the session's workspace: `path: Annotated[str, SourceFile]`.

------
----

## NoCatalog : OmissionMark

Omit this class or operation from the catalog.

------
----

# harness/hooks

A *Hook* mark makes a member answer an IDE event; the *HookServer* of a checkout runs every enabled hook for a *HookPayload*, and the *HookDaemon* keeps that server running. The whole model of this module, internals included, is `harness/hooks/.context/hooks-runtime-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a toolset member answer IDE events, through one hook server per checkout that runs every hooked member and merges their answers.
- **Seam (terms):** Hook, Hooks, HookPayload, HookServer, HookDaemon, HookInstallation
- **Dependencies (one-way):** harness/marks, harness/agent_tools, harness/installation, harness/process

## Hook : Destination

Mark an operation to answer one IDE event, such as `postToolUse`.

------
----
+ disabled_on(operation: Any): bool

## Hooks

Class annotation: disable every hook operation on the toolset.

------
----

## HookPayload : Mapping[str, Any]

The fields an IDE sends on stdin for one firing of a hook, such as the tool that just ran and its input.

+ HookPayload(fields: Mapping[str, Any])
------
+ hook_event_name: str
+ conversation_id: str
+ generation_id: str
+ tool_name: str
+ tool_input: dict[str, Any]
+ workspace_roots: list[Path]
+ project: Path | None
+ chat_id: str
----
+ from_stdin(raw: bytes): HookPayload
+ edited_path(): str

## HookServer

The hooks of one checkout, loaded once: it runs the enabled handlers for each event and merges their answers.

+ HookServer(repo_root: Path, catalog: HandlerCatalog)
------
+ session: Any
+ chat_injections: ChatInjections | None
----
+ show_toasts_with(show: Callable[[str, list[Path]], Any]): None
+ from_toolsets(repo_root: Path, toolsets: list[Any] | None = None): HookServer
+ from_handlers(handlers: Path | str, repo: Path | str): HookServer
+ skip(tool: str, error: BaseException): None
+ handle_stdin(raw: bytes): HookResult
+ dispatch(payload: HookPayload): HookResult
+ diagnose(): dict[str, Any]
+ notice(): str
+ notify_exceptions(): None

## HookDaemon

The hook daemon of one checkout.

+ HookDaemon(repo: Path | str, port: int | None = None)
------
+ repo: Path
+ state_path: Path
+ port: int
+ source_stamp: str
----
+ live_address(): HookDaemonAddress | None
+ is_running(): bool
+ ensure(): HookDaemonAddress
+ replace_stale(): None
+ spawn(): None
+ serve(server: HookServer | None = None): None

## HookInstallation : Installation

Write the IDE's `hooks.json`, which runs the hook command for each event a hook operation serves, and `hook-handlers.json`, which lists those operations for the hook server.

+ HookInstallation(ide: str, path: Path | str, python: str | None = None, repo: Path | str | None = None)
------
+ << association >> server: HookServer | None
+ dispatch_command: str
+ handlers_file: HookHandlersFile
+ manifest: HooksManifest
+ registered_events: list[str]
+ registered_operations: list[str]
----
+ write(tool: AgentTool): None
+ write_handlers(): None
+ write_hooks_manifest(): None
+ standup(): HookServer
+ diagnose(): dict[str, Any]

# harness/mcp

The *McpHost* is the one cdd server every chat talks to; it keeps one *McpServer* per project, and *McpInstallation* writes each IDE's `cdd` entry and starts it from *CddHome*.

- **Purpose:** Let any chat, in any project, call the operations authors mark @mcp, through one long-running server that keeps each project's toolsets apart.
- **Seam (terms):** McpHost, McpServer, McpInstallation, UserMcpConfig, CddHome, SpecServer, UserHome
- **Dependencies (one-way):** harness/marks, harness/agent_tools, harness/installation, harness/process

## McpHost

The cdd server's MCP side: one *McpServer* for each project a chat works on, answering every chat.

+ McpHost(checkout_server: McpServer)
------
+ << composition >> checkout_server: McpServer
+ projects: list[Path]
----
+ server_for(project: Path): McpServer
	// one McpServer per project, so one project's toolsets never answer another project's call
+ dispatch(name: str, arguments: dict[str, object] | None = None, project: Path | None = None): object
+ answer(call: ToolCall): object
+ serve(daemon: McpDaemon, listener: socket.socket): None
+ http_app(port: int): Any
+ ping(): str
+ restart(): dict[str, Any]
+ diagnose(): dict[str, Any]
+ notice(): str
+ notify_exceptions(): None
+ from_repo(repo: Path | str): McpHost
+ from_refs(toolset_refs: tuple[str, ...], constructor_context: dict[str, object] | None = None, repo: str | None = None, project: str | None = None): McpHost

## McpServer

The toolsets one project's calls are answered by: every `@mcp` operation of the toolsets it was started with, published under its MCP name, made for that project.

+ McpServer(repo: str | Path | None = None, project: str | Path | None = None)
------
+ repo: Path | None
+ project: Path | None
+ started: bool
+ tools: dict[str, AgentTool]
+ prompts: dict[str, AgentTool]
+ skipped: list[dict[str, str]]
----
+ skip(tool: str, error: BaseException): None
+ enroll(tool: AgentTool): None
+ start(toolset_refs: tuple[str, ...], constructor_context: dict[str, object] | None = None): None
+ for_project(project: Path): McpServer
+ restarted(): McpServer
+ resolve_call_name(name: str): str
+ enrolled(name: str): AgentTool | None
+ call_seconds(name: str): float
+ invoke_tool(mcp_name: str, arguments: dict[str, object] | None = None): object
+ invoke_prompt(mcp_name: str, arguments: dict[str, object] | None = None): object
+ answer_tool(mcp_name: str, call: ToolCall): object
	-> AgentTool.answer
+ answer_prompt(mcp_name: str, call: ToolCall): object

## McpInstallation : Installation

Record `@mcp` operations, write each IDE's `cdd` entry, and start the one cdd server from `~/.cdd`.

+ McpInstallation(ide: str, path: Path | str, toolset_ref: str = '', repo: Path | str | None = None, home: CddHome | None = None)
------
+ << association >> server_home: CddHome
+ << association >> host: McpHost | None
+ << composition >> user_config: UserMcpConfig | None
+ manifest_path: Path
+ connect_script: Path
----
+ write(tool: AgentTool): None
+ record_operation(tool: AgentTool): None
+ write_mcp_manifest(): None
+ allow_cdd_tools(settings: Path): None
+ drop_project_cdd_server(): None
+ drop_user_cdd_server(): None
+ standup(): McpHost
+ diagnose(): dict[str, Any]
+ ensure_server(): str
+ pin_server(): str
+ serve_from_checkout(): str
+ server_is_running(): bool
+ server_runs_this_process(): bool

## UserMcpConfig

The IDE's own user-level MCP config — where CDD deploys its host for every project.

+ UserMcpConfig(ide: str)
------
+ ide: str
+ << composition >> layout: IdeLayout
+ folder: Path | None
+ path: Path | None
+ servers_key: str
+ project_folder: str
----

## CddHome

The user's cdd folder: which checkout the one server runs, the Python it runs on, and the server's address.

+ CddHome(folder: Path | str | None = None)
------
+ folder: Path
+ state_path: Path
+ log_path: Path
+ connect_script: Path
+ claude_plugins: Path
+ runtime_record: Path
+ pinned_checkout: Path
+ is_installed: bool
+ source: Path
+ mode: str
+ python: str
+ server_environment: dict[str, str]
----
+ write_claude_plugin(server: dict[str, object]): list[Path]
+ write_board_plugin(): None
+ install(checkout: Path | str, connect_script: Path | str): None
+ pin(checkout: Path | str): str
+ serve_from(checkout: Path | str): None

## SpecServer

The cdd server as chats meet it: its own process on its own port, started through `~/.cdd/connect.py`, here with a throwaway `~/.cdd` that serves this checkout and only the toolsets a spec names.

+ SpecServer(toolsets: tuple[str, ...] = (), home: Path | str | None = None, port: int | None = None)
------
+ url: str
----
+ install(): None
+ start(): dict
+ stop(): None
+ chat(project: Path | str | None, seconds: float | None = None): AsyncIterator[object]

## UserHome

Points HOME, USERPROFILE and APPDATA at a temp folder so specs never touch the user's own config.

+ UserHome()
------
----
+ enter(): Path
+ leave(): None

# harness/guidance

A *PracticeGuidance* is one practice: its *FidelityGuidance* fidelities, its *Rule* lists, templates, and examples, read from its markdown. *PracticeCatalogue* and *ActionCatalogue* name what CDD ships; *ApproachStage* is a stage of the approach. The whole model of this module, internals included, is `harness/guidance/.context/practice-guidance-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a practice be one class plus its markdown, with fidelities, rules, templates, and examples an agent can follow and a validator can check against.
- **Seam (terms):** Guidance, PracticeGuidance, FidelityGuidance, GuidanceCollection, Rule, RulesCollection, Schema, PracticeCatalogue, ActionCatalogue, Action, ApproachStage, StageScope
- **Dependencies (one-way):** harness/name, harness/marks, harness/agent_tools, harness/markdown, harness/installation, harness/hooks, harness/mcp

## Guidance

Words and rules an agent follows, read from markdown beside the class.

+ Guidance(format: str | None = None)
------
+ default_format: str
+ name: str | None
+ domain_slug: str | None
+ session: Any
+ registration_name: str
+ slug: str
+ install_folder: Path
+ module_dir: Path
+ overview: str
+ guidance: str
+ << aggregation >> listed_rules: list[Rule]
+ sketch_template: str
+ instructions: str
----
+ rules(): RulesCollection
+ checked_rule_collections(): list[RulesCollection]
+ checked_rules(): list[Rule]
+ every_rule(): list[Rule]
+ templates(): str
+ rules_after_edit(payload: Any): str

## PracticeGuidance : Guidance

One practice as a class plus its markdown: overview, shared rules, fidelities, templates, examples, and formats.

+ PracticeGuidance(format: str | None = None, fidelity: str | None = None, default_workspace_folder: str = '.', formats: dict[str, Any] | None = None)
------
+ sketch_titles: tuple[str, ...]
+ key: str
+ practice_slug: str
+ short_name: str
+ colour: str
+ fidelity_slugs: list[str]
+ supported_formats: frozenset
+ clean_engineering_companion: FidelityGuidance | None
+ guidance: str
+ instructions: str
+ schema: str
+ formats: dict[str, Any]
----
+ rules(): RulesCollection
+ checked_rule_collections(): list[RulesCollection]
+ every_rule(): list[Rule]
+ files(): dict[str, dict[str, list]]
+ output_paths(): dict[str, list[str]]
+ project_rules(): list
+ work_in(session_output: Any): None
+ generate_output(): str
+ schema_guide(): str
+ schema_node_fidelities(): dict[str, list[str]]
+ schema_fidelity_errors(): list[str]
+ fidelities(): GuidanceCollection
+ domain_markdown_path(): Path
+ examples(): str
+ read_paths(paths: list[str] | str, source: str | None = None): Any
+ render(format: str, content: Any = '', source: str | None = None, previous: str = ''): dict
	-> read_paths
+ render_files(format: str, paths: list[str] | str, source: str | None = None): dict
+ scoped_markdown(): str

## FidelityGuidance : Guidance

One fidelity of a practice, such as the story map: its stage, its outputs, and its rules.

+ FidelityGuidance(name: str = '', stage: str = '', default_format: str = '', clean_engineering: FidelityGuidance | None = None)
------
+ stage: str
+ companion_of: FidelityGuidance | None
+ session_output: Any
+ judged_on: str
+ is_judged_on_graph: bool
+ name: str
+ outputs: dict[str, str | list[str]]
+ << association >> practice_guidance: PracticeGuidance | None
+ format: str | None
+ default_format: str
+ default_output: str | list[str]
+ clean_engineering: FidelityGuidance | None
+ slug: str
+ install_folder: Path
+ scaffold: str
+ section: str
+ instructions: str
----
+ work_in(session_output: Any): None
+ output_paths(): dict[str, list[str]]
+ files(): dict[str, list]
+ has_declared_output(): bool
+ reports(): list[Path]
+ new_report_path(): Path
+ rules(): RulesCollection

## GuidanceCollection : MarkdownCollection, Guidance

A practice's fidelities, read from its markdown, published together.

+ GuidanceCollection(entries: dict[str, Guidance] | None = None, parent: Any = None)
------
----
+ child_for_stage(stage: str): Guidance
+ child(name: str, body: str = ''): FidelityGuidance
+ overview(): str
+ guidance(): str
+ rules(): RulesCollection
+ templates(): str
+ instructions(): str

## Rule

One rule a practice checks, by its slug, with its body.

+ Rule(slug: str, body: str, fidelity: str | None = None, tag: str = 'base')
------
+ fidelity: str | None
+ slug: str
+ body: str
----
+ attribute_to(practice: str, tag: str = 'base', shared: bool = False): Rule
+ validate(): str
+ from_bullet(text: str, fidelity: str | None = None): Rule

## RulesCollection : MarkdownCollection

The rules of one practice or fidelity, and the paths they apply to.

+ RulesCollection(entries: dict[str, Rule | RulesCollection] | None = None, applies_to: AppliesTo | None = None, parent: Any = None)
------
+ applies_to: AppliesTo
+ practice_key: str
+ fidelity_name: str
+ markdown_block: str
----
+ inject_rules(payload: HookPayload): dict[str, Any]
+ from_markdown(text: str, fidelity: str | None = None, parent: Any = None): RulesCollection
+ formatted(): str
+ validate(): str
+ scan(paths: Any): Any

## Schema

The types one schema file declares, keyed by their schema key, in the order written.

+ Schema(text: str)
------
----
+ load(path: Path): Schema
+ fidelities(): dict[str, str]
+ rules(): dict[str, tuple[str, ...]]

## PracticeCatalogue

Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD.

------
----
+ keys(): tuple[str, ...]
+ has(key: str): bool
+ practices(): tuple[PracticeGuidance, ...]
+ practice(key: str): PracticeGuidance
+ create(key: str): PracticeGuidance
+ practice_class(key: str): type[PracticeGuidance]
+ module_of(key: str): str
+ practice_named(slug: str): PracticeGuidance | None
+ toolset_ref(slug: str): str | dict[str, str] | None

## ActionCatalogue

Every action CDD ships, read from its action folders: each folder under `cdd_guidance/actions` whose name does not start with `_` holds its toolset in the module of the folder's name, as the class of that name in Pascal case (`grill_context/grill_context.py` holds `GrillContext`).

------
----
+ toolsets(): tuple[type, ...]
+ actions(): tuple[Action, ...]
+ names(): tuple[str, ...]
+ has(name: str): bool
+ action(name: str): Action | None

## Action

One action CDD ships: an operation an action toolset installs as a skill, such as generate, repair, or validate.

+ Action(name: str, toolset_class: type)
------
+ name: str
+ toolset_class: type
+ toolset_ref: str
+ operation
+ folder: Path
----

## ApproachStage

One stage of the CDD approach: the name each fidelity's **Stage:** gives it, its title, its scope, and the actions a person runs on a fidelity in it.

+ ApproachStage(name: str, scope: StageScope)
------
+ name: str
+ title: str
+ << composition >> scope: StageScope
+ steps: list[str]
+ actions: list[str]
+ producing_actions: list[str]
+ actions_with_formats: list[str]
----

## StageScope

How much of the solution a stage's work covers, drawn as a shape that narrows and deepens along the board: Discovery takes in the whole solution wide and shallow, Implementation one story narrow and deep.

+ StageScope(shape: str, name: str, reach: str, covers: str)
------
+ shape: str
+ name: str
+ reach: str
+ covers: str
----

# harness/guidance_actions

A *GuidanceAction* is an action, such as generate, run on the guidance a call names, made for the session that call works in.

- **Purpose:** Give every guidance action the same way to take guidance, open its session, and run once per listed guidance.
- **Seam (terms):** GuidanceAction, ActionWorksInNoSession
- **Dependencies (one-way):** harness/name, harness/marks, harness/agent_tools, harness/guidance, harness/hooks

## GuidanceAction

An action, such as generate, on the guidance a call names, such as stories-story-map, made for the session that call works in.

+ GuidanceAction(session: Any = None)
------
+ injects_rules: bool
+ session: Any
+ session_context: str
----
+ for_call(call: ToolCall): GuidanceAction
	-> ToolCall.session_named
	-> made_for
+ made_for(session: Any): GuidanceAction
+ session_for(call: ToolCall): Any
+ source_label(content: str = '', paths: list[str] | str | None = None): str
+ path_named(named: str | Path): Path
+ document_named(content: str = '', paths: list[str] | str | None = None): str
+ guidance_text(): str | None
+ listed(): list
+ each(operation: Callable[[Any], Any]): list
+ run(operation: Callable[[Any], Any], action: str = ''): list
+ begin(guidance: GuidanceArg | None = None, action: str = ''): str
+ act_quickly(): str
+ inject_rules(payload: HookPayload): dict[str, Any]

## ActionWorksInNoSession : Exception

An action made for no session, such as one listed for install, was asked for the session it works in.

+ ActionWorksInNoSession(action: str)
------
----

# harness/graph

A *Graph* holds one *PracticeGraph* per practice, each a tree of *Node* objects read from source; a *GraphPractice* is what one practice gives the graph, and its *PracticeGraphRule* checks report *Violation* records. The whole model of this module, internals included, is `harness/graph/.context/graph-populate-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Turn a working copy into practice graphs that rules can check and a person can explore.
- **Seam (terms):** Graph, PracticeGraph, Node, ModelNode, ModelChildren, Source, GraphPractice, GraphPractices, GraphOverlay, PatternOverlays, PracticeGraphRule, RuleCheckContext, Violation, SavedGraph
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/guidance, harness/installation, harness/mcp

## Graph

One graph.

+ Graph()
------
+ << composition >> practices: dict[str, PracticeGraph]
+ overlays: list[str]
+ folder: str
+ loaded_folder: Path | None
+ applied_overlays: list[str]
+ overlay_patterns: tuple[str, ...]
----
+ of_practice(folder: Path | str, name: str, source_root: Path | str): Graph
+ report_progress(message: str): None
+ practice(name: str): PracticeGraph
+ load_working_copy(folder: str, practices: dict[str, str], database: str | None = None, overlays: list[str] | None = None, force: bool = False): GraphLoaded
+ load_files(folder: str, practices: list[str], files: list[str], overlays: list[str] | None = None): GraphLoaded
+ source_files(root: Path, suffixes: set[str]): list[Path]
+ edited_files(): list[Path] | None
+ scoped(found: list[Path]): list[Path]
+ scope_folders(): list[Path] | None
+ write_json(path: str): str
+ save_json(): GraphSaved
+ sync_schema_edges(): None
+ schema_sync_held(): Iterator[None]
+ set_overlays(overlays: list[str]): AppliedOverlays
+ overlay_of(folder: str): Overlay
+ practice_names(): list[str]
+ inventory(): Inventory
+ filter_choices(practices: list[str], node_types: list[str]): Filter
+ source(node_id: str): NodeSource | None
+ return_nodes(filter: dict | None = None): list[FilteredNode]

## PracticeGraph

An edge is recorded only when both ends are already registered.

+ PracticeGraph(name: str)
------
+ name: str
+ << composition >> nodes: dict[str, list[Node]]
+ graph: Graph | None
+ node_counts: dict[str, int]
+ edge_count: int
+ node_type_names: list[str]
+ edge_type_kinds: list[str]
+ rule_labels: list[str]
+ schema
+ tree: ExplorerEntry
----
+ apply_rule(rule: str, types: list[str]): None
+ rules_for(node_type: str): list[str]
+ rule_labels_for(types: set[str]): set[str]
+ add(node: Node, node_id: str, file: str, start_line: int, end_line: int): Node
+ unused_node_id(type: str, name: str): str
+ add_named(type: str, node_id: str, name: str, source: Source): Node
+ restore(saved: SavedPractice): None
+ restore_links(saved: SavedPractice): None
+ registered(node_id: str): Node | None
+ link(kind: str, parent: Node, child: Node, display: Display = 'direct'): None
+ record(edge_type: EdgeType, parent: Node, child: Node): None
+ edges_from(kind: str, parent: Node): list[Edge]
+ direct_parent(child: Node): Node | None
+ node_count(type: str): int
+ rebuild_tree(): None

## Node

children is the list populate writes on this node.

+ Node(practice: PracticeGraph, type: str, node_id: str, name: str, source: Source)
------
+ practice: PracticeGraph
+ type: str
+ node_id: str
+ name: str
+ << composition >> source: Source
+ << aggregation >> children: list[Node]
+ parent: Node | None
+ graph_facts: tuple[str, ...]
+ facts: dict
+ fidelity: str
+ fidelities: list[str]
+ rules: GraphRulesCollection
+ file_language: str | None
+ failed_rules: list[str]
+ passing_rules: list[str]
----
+ set_fact(key: str, value): None
+ get_fact(key: str, default = None): None
+ has_fact(key: str): bool
+ release(): None
+ place(file: str, start_line: int, end_line: int): None
+ populate(parent: Node | None = None): None
+ serialize(seen: set[str] | None = None, via: Node | None = None, stack: set[str] | None = None): ExplorerEntry
+ rule_category(): GraphRulesCollection | None

## ModelNode : Node

Base model object for one practice.

+ ModelNode(name: str, sequential_order: int, graph: Graph | None = None)
------
+ has_source_file: bool
+ node: ModelNode
+ << association >> graph: Graph
----
+ semantic_type(): str
+ batch_schema_sync(): Iterator[None]

## ModelChildren : list

The list callers already append to.

+ ModelChildren(owner: ModelNode, kind: str)
------
----
+ append(child): None
+ extend(children: Iterable): None
+ insert(index: int, child): None
+ pop(index: int = -1): None

## Source

Source text Monaco displays: file, start and end line, and text with each call marked.

+ Source(path: str, line_start: int, line_end: int, root: str = '')
------
+ file: str
+ start_line: int
+ end_line: int
+ language: str
+ text: str
+ contents: str
----
+ whole_file(relative: str, root: str): Source
+ load_calls(raw: str): None
+ insert_calls(raw: str): str
+ align_to_label(label: str): None
+ widen_to_call_close(): None
+ align_to_example_export(root: str, name: str): None

## GraphPractice

What one practice gives the graph.

+ GraphPractice(name: str, package: str = '')
------
+ name: str
+ package: str
+ reads_after: tuple[str, ...]
+ node_types: tuple[str, ...]
+ class_types: tuple[str, ...]
+ member_types: tuple[str, ...]
+ class_node_type: str
+ source_ordered_types: frozenset[str]
+ extends: str
+ anchor_types: dict[str, str]
+ rule_types: dict[str, tuple[str, ...]]
----
+ align(node: Node): None
+ read(practice: PracticeGraph): None
+ link(graph: Graph): None
+ rules(): dict[str, PracticeGraphRule]
+ own_rules(): dict[str, PracticeGraphRule]
+ language_rules(language: str): dict[str, PracticeGraphRule]
+ checks(patterns: tuple[str, ...] = ()): dict[str, PracticeGraphRule]
+ checks_for(node: Node, patterns: tuple[str, ...]): dict[str, PracticeGraphRule]

## GraphPractices

Every practice and pattern overlay registered with the graph.

------
----
+ register(practice: GraphPractice): None
+ register_overlay(overlay: GraphOverlay): None
+ named(name: str): GraphPractice
+ overlay(pattern: str): GraphOverlay
+ in_reading_order(names: list[str]): list[GraphPractice]

## GraphOverlay

What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each practice, which live in `<pattern>/practices/<practice>/rules`.

+ GraphOverlay(pattern: str)
------
+ pattern: str
+ direct_kinds: frozenset[str]
----
+ display_of(kind: str): str
+ read(graph: Graph): None
+ guidance(): None
+ rules_for(practice: str): dict[str, PracticeGraphRule]

## PatternOverlays

The pattern overlays a graph applies.

+ PatternOverlays(overlays: list[str] | tuple[str, ...] = ())
------
+ patterns: tuple[str, ...]
+ available: list[str]
----
+ root_of(overlay: str): Path

## PracticeGraphRule

One graph rule: the node types it checks and what it reports on a node or on the whole practice.

------
+ node_types: tuple[str, ...]
----
+ check(node, context: RuleCheckContext): list[str]
+ check_practice(context: RuleCheckContext): list[tuple[str, str]]
+ applies_to(node_type: str): bool

## RuleCheckContext

The practice one load checks, and the folder its source was read from.

+ RuleCheckContext(practice, source_root: Path | None)
------
----
+ child_count(node, edge_kinds: tuple[str, ...]): int
+ children(node, edge_kind: str): list
+ node_data(node): dict
+ scenario_outline(node): bool
+ scenario_evidence(node): list[str]

## Violation

A rule broken at one place: the rule and the practice that checks it, the node it was found on, what that node is (`Operation `checkout``), the file and lines, the message, and how severe it is.

+ Violation(rule: str, message: str, practice: str = '', node_id: str = '', subject: str = '', location: str = '', line: int | None = None, end_line: int | None = None, severity: str = 'error', source: list[SourceLine] | None = None)
------
+ rule: str
+ practice: str
+ node_id: str
+ subject: str
+ location: Annotated[str, SourceFile]
+ line: int | None
+ end_line: int | None
+ message: str
+ severity: str
+ source: list[SourceLine]
+ described: str
----
+ on_node(rule: str, message: str, node): Violation
+ from_data(data: dict): Violation
+ is_under(prefixes: list[str]): bool
+ in_file(location: str, file: Path, lines_before: int, lines_after: int): Violation

## SavedGraph

Every practice a folder's saved graph keeps, with the pattern overlays it was loaded with.

+ SavedGraph(overlays: list[str], practices: dict[str, SavedPractice])
------
+ overlays: list[str]
+ document: dict
+ text: str
----
+ from_graph(graph: Graph): SavedGraph
+ from_document(document: dict, source: str = ''): SavedGraph
+ from_text(text: str, source: str = ''): SavedGraph
+ merged_over(older: SavedGraph | None): SavedGraph
+ holds(practice_roots: dict[str, Path], overlays: list[str]): bool
+ violations(practices: list[str] | None = None): list[Violation]
+ restored_graph(): Graph

# harness/installer

The *Installer* publishes every marked member of a repository's toolsets into one IDE folder, then starts the hook server and the cdd server.

- **Purpose:** Install one repository into one IDE folder through every channel, from one walk of the repository, and start what that install needs running.
- **Seam (terms):** Installer
- **Dependencies (one-way):** harness/agent_tools, harness/markdown, harness/installation, harness/hooks, harness/mcp

## Installer

Publish every marked member of the toolsets a repository defines into one IDE folder, through the installation of each channel its marks name, then start the hook server and the cdd server the install points at.

+ Installer(ide: str | None = None, path: str | Path | None = None, repo: str | Path)
------
+ repo: Path
+ ide: str
+ << composition >> layout: IdeLayout
+ path: Path
+ << composition >> toolsets: RepositoryToolsets
----
+ load(project: Path | str): Installer
+ track(installation: Installation): None
+ installations_for(tool: AgentTool): list[Installation]
+ clean(): list[str]
+ install(toolsets: Iterable[Any] | None = None, replace: bool = True): Any
	-> RepositoryToolsets.ensure_import_path
	-> RepositoryToolsets.collect
+ install_self(replace: bool = False): Any
+ ensure_runtimes(): dict[str, Any]
+ ensure_mcp_server(): str
+ diagnose_after_install(): list[str]
+ diagnose_install(): str
+ install_instructions(): str
+ clean_instructions(): str
+ diagnose_install_instructions(): str
+ runtime_instructions(): str
+ diagnose_instructions(): str
+ ensure_mcp_server_on_session_start(payload: HookPayload): str
+ ensure_mcp_server_after_agent_response(payload: HookPayload): str

# harness/diagnostics

Each diagnostics toolset probes what an install published through the live host and writes a report section.

- **Purpose:** Check that what an install published answers through the live host, so a broken publication shows up in a report rather than in a failing chat.
- **Seam (terms):** AgentToolsDiagnostics, GuidanceDiagnostics, AgentToolsProbe, GuidanceProbe
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/installation, harness/mcp, harness/installer

## AgentToolsDiagnostics

Probe workspace MCP tools on the install host (space, harness, tools — ping + invoke).

+ AgentToolsDiagnostics(call: ToolCall | None = None)
------
----
+ for_call(call: ToolCall): AgentToolsDiagnostics
+ agent_tools_diagnostics(guidance: list[str] | None = None): str

## GuidanceDiagnostics

Probe installed guidance instructions and guidance-action MCP operations.

+ GuidanceDiagnostics(call: ToolCall | None = None)
------
----
+ for_call(call: ToolCall): GuidanceDiagnostics
+ guidance_diagnostics(guidance: list[str] | None = None): str

## AgentToolsProbe

A probe of the workspace MCP tools one install deployed (space, harness, and tools): ping each, call the light ones with probe arguments, and call session and graph tools with `cdd-diagnostic` fixtures.

+ AgentToolsProbe(installer: Any, guidance: list[str] | None = None, mcp_host: Any = None, project: Path | None = None)
------
+ host: Any
+ toolset_refs: tuple[str, ...]
+ published: list[str]
----
+ run(): str
+ ping(): str
+ invoke(): str
+ heavy_invoke(): str

## GuidanceProbe

A probe of the guidance one install deployed, made for its Installer and the guidance slugs that filter what it calls.

+ GuidanceProbe(installer: Any, slugs: list[str])
------
+ prefixes: list[str]
----
+ from_filter(installer: Any, guidance: list[str] | None): GuidanceProbe
+ matches(mcp_name: str): bool
+ instructions(): str
+ actions(): str

# harness/sub_agent

*SubAgent* hands work to a non-blocking sub-agent with its own instructions.

- **Purpose:** Let an agent delegate work to a sub-agent through one published operation.
- **Seam (terms):** SubAgent
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp

## SubAgent

Launch a non-blocking sub-agent with custom instructions.

------
----
+ sub_agent(instructions: str, summary: str = ''): str

# harness/health

*ServerHealth* reports the parts of CDD that run outside the MCP host.

- **Purpose:** Report whether the board app, the graph app, and the hook server are running, for the chat's server health band.
- **Seam (terms):** ServerHealth
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/hooks, harness/mcp

## ServerHealth

Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal.

+ ServerHealth(repo_root: Path | str, graph_ports: tuple[int, ...] = GRAPH_APP_PORTS, kanban_ports: tuple[int, ...] = KANBAN_APP_PORTS, hook_daemon: HookDaemon | None = None)
------
+ kanban_app_port: int | None
+ graph_app_port: int | None
+ is_hook_server_running: bool
----
+ load(project: Path | str): ServerHealth
+ report(): ServerHealth

# harness/catalog_generator

The *Catalog* renders CDD's practices, actions, and approach as pages; a *CatalogPractice* is one practice as the catalog shows it.

- **Purpose:** Show people what CDD offers, as pages generated from the same guidance the agent follows.
- **Seam (terms):** Catalog, CatalogPractice
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/markdown, harness/guidance, harness/installation, harness/process, harness/mcp

## Catalog

The top-level entry point - the only class `generate_cdd_catalog.py` calls.

+ Catalog(repo_url: str = '', ref: str = '', out_root: str = '', brands_root: str | Path | None = None, approach_md_path: str | Path | None = None, project: str | Path | None = None)
------
+ repo_url: str
+ project: CatalogProject
+ out_root: Path
+ << composition >> practices: list[CatalogPractice]
+ utilities: list[Utility]
+ lifecycle_actions: list[LifecycleAction]
+ approach_copy: ApproachCopy
+ board: HubBoard
+ brands: dict[str, Path]
----
+ load(project: Path): Catalog
+ generate_catalog(brand: str | Path = ''): str
+ apply_brand(name: str): str
+ generate_project_approach(examples_json: str = '', project_title: str = ''): str
+ configure_project_approach(example_paths: list[str] | None = None): str
+ write_page(relative_path: str, html_text: str): Path

## CatalogPractice

One practice as the catalog shows it: the live `PracticeGuidance`, the catalog card it gives itself, and its fidelities placed in the board's stage columns.

+ CatalogPractice(practice: PracticeGuidance, skills: SkillSlashName | None = None)
------
+ << association >> practice: PracticeGuidance
+ key: str
+ display_name: str
+ label: str
+ family: str
+ perspective: str
+ order: int
+ spec_blurb: str
+ href: str
+ skill_name: str
+ fidelities: list[FidelityGuidance]
+ on_board: bool
+ shared_markdown: str
----
+ load_all(): list[CatalogPractice]
	-> PracticeCatalogue.practices
+ column_of(fidelity: FidelityGuidance): StageColumn | None
+ fidelity_in(column: StageColumn): FidelityGuidance | None
+ fidelity_href(fidelity: FidelityGuidance): str

# harness/design_canvas

A *DesignCanvas* is the pages, boards, and artboard files of one Claude Design canvas.

- **Purpose:** Let a practice publish its views as a Claude Design canvas without knowing the canvas's file layout.
- **Seam (terms):** DesignCanvas
- **Dependencies (one-way):** *(none)*

## DesignCanvas

The pages, boards and artboard files of one Claude Design canvas.

+ DesignCanvas(title: str)
------
+ title: str
+ launch_page: str | None
----
+ add_page(page_id: str, name: str): None
+ add_board(name: str, board: dict, text: str | None = None): None
+ files(): dict[str, str]
+ write(root: str | Path): list[str]

# space/repo

A *Repo* is the local clone; a *Branch* is a named branch on it and a *Worktree* one checkout of it.

- **Purpose:** Give every caller one object graph for the clone, its branches and worktrees, and its commits, so version control is never reimplemented with raw git output.
- **Seam (terms):** Repo, Branch, Worktree
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/process, harness/mcp, tools/file_manager

## Repo

Local git clone: its branches and its commits.

+ Repo(root: str | Path = '.')
------
+ root: Path
+ default_branch: str
+ << composition >> git: Git
+ worktrees: Worktrees
+ is_clone: bool
+ checkout_folder: Path
+ << association >> file_manager: FileManager
+ current_branch: str
+ current_commit: str
+ default_start_point: str
----
+ of_project(project: Path): Repo
+ find_root(): Path | None
+ is_linked_worktree(): bool
+ primary_root(): Path
+ path_from_top(path: Path | str): str
+ branch_named(name: str): Branch
+ has_ref(ref: str): bool
+ is_dirty(path: str | Path | None = None, untracked: bool = True): bool
+ commit(paths: list[str], message: str, untracked: bool = False): str
	-> Git.run
+ push_upstream(): None
+ needs_push(): bool
+ fetch(): None
+ pull(): None
+ merge_from(other: Branch, message: str = ''): str
+ switch_branch(name: str = ''): str
+ close_branch(name: str = '', commit_message: str = 'branch: close'): str
+ switch_worktree(name: str = ''): str
+ close_worktree(commit_message: str = 'worktree: close'): str
+ switch_branch_command(): str
+ close_branch_command(): str
+ switch_worktree_command(): str
+ close_worktree_command(): str
+ push_commit(message: str, untracked: bool = True, sync_remote: bool = True): Commit
+ push(hint: str = ''): str

## Branch

Named branch on a *Repo* — checkout, commit, merge, and close.

+ Branch(repo: Repo, name: str)
------
+ repo: Repo
+ name: str
+ exists: bool
+ is_checked_out: bool
+ is_default: bool
+ << association >> worktree: Worktree | None
+ start_point: str
----
+ changed_files(): list[str]
+ check_out(): Branch
+ switch_to(): Branch
+ open_in_worktree(): Worktree
+ move_to_worktree(): Worktree
+ save(commit_message: str): None
+ land_on_default(): None
+ delete(): None
+ close(commit_message: str = 'branch: close'): None

## Worktree

One checkout of the repository: its folder and the branch checked out there.

+ Worktree(path: Path | str, branch: Branch | None, repository: Repo | None = None)
------
+ path: Path
+ branch: Branch | None
+ << association >> repository: Repo
----
+ from_repo(repository: Repo): Worktree
+ from_checkout(path: Path | str, branch_name: str): Worktree
+ fetch_pull(): None
+ close(commit_message: str): Branch

# space/session

A *Session* is one named piece of work in `.sessions/{name}/`; *Sessions* are all of a checkout's sessions; its *SessionLog* records each action, and a *PracticeSessionOutput* is what one practice has in it.

- **Purpose:** Keep the state of one piece of work so any chat or tool can pick the work up from its folder.
- **Seam (terms):** Sessions, Session, SessionLog, LogEntry, PracticeSessionOutput, SessionDiagnostics
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/guidance, harness/installation, harness/mcp, harness/graph, harness/installer, space/repo, tools/file_manager, cdd_guidance/actions

## Sessions

The work sessions of one checkout: open ones in `.sessions/{name}/`, closed ones in `.sessions/_complete/`, and the one saved as open in `.sessions/session.json`.

+ Sessions(project: Path | str)
------
+ project: Path
+ root: Path
+ folder: Path
+ backlog_folder: Path
+ open_name: str
+ << association >> saved: Session
----
+ of_project(project: Path): Sessions
+ folder_of(name: str): Path
+ all(): list[Session]
+ named(name: str): Session | None
+ load(folder: Path): Session
+ create(name: str, workpath: Path, title: str = '', scope: str = '', parent: str = ''): Session
+ open(session: Session, workpath: Path | None = None): Session
+ current(): Session
	// main, which works on the whole repository, is the open session when no other is named
+ switch(name: str = '', workpath: Path | None = None): str
+ close(session: Session): None

## Session

One named piece of work in a project, kept in `.sessions/{name}/`.

+ Session(repo_root: Path | str)
------
+ workpath: Path | None
+ << association >> chat: ChatPointer | None
+ << composition >> log: SessionLog
+ name: str
+ << association >> repo: Repo
+ is_closed: bool
+ session_file: Path
+ session_file_from_project: str
+ root: Path
+ workpath_from_project: str
+ title: str
+ scope: str
+ parent: str
+ fields: dict
+ reports_folder: Path
+ << composition >> practices: dict[str, PracticeSessionOutput]
+ active_practices: list[PracticeSessionOutput]
+ opened_practices: list[PracticeSessionOutput]
+ handoffs: Handoffs
+ latest_handoff: str
+ decision_records: DecisionRecords
----
+ load(session_path: Path, repo_path: Path): Session
+ from_file(session: str, project: Path | str): Session
+ path_named(named: str | Path): Path
+ document_named(content: str = '', paths: list[str] | str | None = None): str
+ from_project(path: Path | str): str
+ save_fields(**values): None
+ save(): None
+ hook_log(filename: str): Path
+ keep_file(file: Path): Path
+ move_to_closed(): Session
+ move_to_archive(): Session
+ move_to_backlog(): Session
+ reopen(): Session
+ practice(name: str): PracticeSessionOutput
+ reset(): None
+ close(): None
+ choose_workpath(path: str = ''): Session
+ folder_files(): list[FileEntry]
+ read_file(path: str = ''): FileText
+ mark_loop(): str
	-> SessionLog.mark_loop
+ read_loop(number: int | None = None): str
	-> SessionLog.read_loop
+ append_log(note: str = '', loop: int | None = None, paths: list[str] | None = None): str
+ write_handoff(content: str = '', paths: list[str] | str | None = None): str
+ read_handoff_format(): str
+ handoff_session(next_focus: str = ''): str
+ read_cdr_format(): str
+ list_cdrs(): str
+ write_cdr(slug: str, content: str = '', paths: list[str] | str | None = None): str
+ record_decisions_session(): str

## SessionLog

The log of one session: `session.log`, one timestamped line per action, tool call, note, and loop marker, each ending with a pointer to the chat that caused it, and `session.err`, the full trace of each failure a log line points at.

+ SessionLog(session: Session)
------
+ path: Path | None
+ error_path: Path | None
+ << composition >> entries: list[LogEntry]
+ injected_rules: InjectedRules
+ last_loop_number: int
+ latest_loop_with_entries: int
----
+ timestamp(moment: datetime): str
+ record(line: str): None
	// a session without a folder has a log that writes nothing
+ note_chat(chat: ChatPointer): None
+ line(line: str): None
+ action(action: str, paths: list[Path]): None
+ guidance_action(action: str): None
+ tool(tool_name: str, tool_input: dict | None = None): None
+ note(message: str, paths: list[Path] | None = None): None
+ failure(failure: BaseException, tool: str = ''): None
+ append_chat(action: str, chat: ChatPointer): None
+ seed_first_loop(): None
+ next_loop(): Loop
+ loop_at(number: int): Loop
+ mark_loop(): int
+ read_loop(number: int | None = None): str
+ append_note(note: str, loop: int | None = None, paths: list[str] | None = None): str
+ instructions(): str

## LogEntry

One line of a session log: `<time> <verb> <words...>`, the words being the subject the verb acted on.

+ LogEntry(line: str)
------
+ time: str
+ verb: str
+ words: list[str]
+ stage: str
+ loop_number: int | None
----
+ names(fidelity: FidelityGuidance): bool

## PracticeSessionOutput

What one practice has in one session: its guideline, the paths it reads, its graph, whether it is on, the folder it writes under, and the files each of its fidelities declares.

+ PracticeSessionOutput(name: str, session: Session)
------
+ name: str
+ session: Session
+ session_file: str
+ << association >> guideline: PracticeGuidance
+ fidelities: GuidanceCollection
+ << composition >> graph: Graph
	-> Graph.of_practice
+ root_node_name: str
+ enabled: bool
+ working_fidelity: str
+ working_format: str
+ folder: Path
+ output_root: Path
+ root: str
+ is_root_chosen: bool
----
+ load(session: str, practice: str, project: Path): PracticeSessionOutput
+ of_fidelity(fidelity: FidelityGuidance): FidelitySessionOutput
+ enable(is_enabled: bool): PracticeSessionOutput
+ keep_format(): None
+ use_kept_format(): None
+ log_validation(violations: list[str]): None
+ choose_root(path: str): PracticeSessionOutput
+ keep_root(root: Path): None
+ use_default_root(): PracticeSessionOutput

## SessionDiagnostics

Probe session logging (generate, validate, loops, chat pointers).

+ SessionDiagnostics(call: ToolCall | None = None)
------
----
+ for_call(call: ToolCall): SessionDiagnostics
+ session_diagnostics(): str
+ write_to(installer: Any): str

# space/kanban

The *Board* shows every session as a *Ticket* in a *Column*: Backlog, a *Stage*, or Complete. A *FidelityProgress* is how far one fidelity has got on one ticket; a *BacklogItem* is an idea not yet started. The whole model of this module, internals included, is `space/kanban/.context/kanban-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** See every session's progress through the delivery stages, and move sessions through them, from an agent's tools or from the Session Board app.
- **Seam (terms):** Board, Column, Stage, Card, Ticket, BacklogItem, FidelityProgress
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/guidance, harness/installation, harness/mcp, harness/graph, harness/catalog_generator, space/session, space/repo, tools/file_manager, cdd_guidance/actions, cdd_guidance/practices/stories, cdd_guidance/practices/ddd, cdd_guidance/practices/ux

## Board

Show every work session as a ticket on a kanban: Backlog, Discovery, Specification, Implementation, and Complete.

+ Board(repo: Repo, practices: list[PracticeGuidance])
------
+ << association >> repo: Repo
+ << association >> sessions: Sessions
+ file: Path
+ project: str
+ worktrees: dict[Branch, Worktree]
+ << association >> practices: list[PracticeGuidance]
+ << composition >> columns: list[Column]
+ tickets: list[Ticket]
+ backlog_items: list[BacklogItem]
+ cards: list[Card]
+ active: Ticket | None
----
+ load(project: Path | str): Board
	-> Repo.primary_root
	-> PracticeCatalogue.practices
+ column(name: str): Column
+ ticket(name: str): Ticket | None
+ backlog_item(title: str): BacklogItem | None
+ open_ticket(title: str, scope: str, parent: str, path: str): Ticket
+ show(): Board
+ folders(path: str = ''): list[str]
+ help(practice: str): Help
+ practice(key: str): PracticeGuidance

## Column

*Column* is one place on the board: Backlog, a stage, or Complete.

+ Column(name: str, board: Board)
------
+ name: str
+ << aggregation >> cards: list[Card]
----

## Stage : Column

Show one stage of the board, the tickets at work in it, and how many it takes before it is over its limit.

+ Stage(approach: ApproachStage, board: Board)
------
+ steps: list[str]
+ << association >> scope: StageScope
+ actions: list[str]
+ producing_actions: list[str]
+ actions_with_formats: list[str]
+ work_required: list[FidelityGuidance]
+ next_stage: Stage | None
+ previous_stage: Stage | None
+ wip_limit: int
+ is_over_limit: bool
+ in_progress: list[Ticket]
+ done: list[Ticket]
----
+ load(stage: str, project: Path | str): Stage
+ set_wip_limit(limit: int): Stage

## Card : ABC

*Card* is anything on the board that a person moves: a ticket or a backlog item.

+ Card(board: Board)
------
+ board: Board
+ title: str
+ column: Column
+ last_activity: str
----
+ move_next(): Card
+ move_previous(): Card

## Ticket : Card

Show one work session as a unit of delivery and move it through the stages.

+ Ticket(session: Session, board: Board)
------
+ name: str
+ title: str
+ << association >> session: Session
+ << composition >> progress: list[FidelityProgress]
+ column: Column
+ is_closed: bool
+ is_active: bool
+ drop_targets: list[str]
+ is_done: bool
+ next_fidelity: FidelityProgress | None
+ last_activity: str
+ worktree: str
----
+ load(ticket: str, project: Path | str): Ticket
+ create(title: str, scope: str = 'feature', parent: str = '', path: str = '', project: Path | str): Ticket
+ branch(): Branch
	-> Repo.branch_named
+ progress_of(slug: str): FidelityProgress
+ activate(leaving: list[str] | None = None, opening: list[str] | None = None): Ticket
	-> Repo.switch_branch
	-> Repo.switch_worktree
	-> Sessions.switch
	-> leave
+ open_worktree(): Ticket
+ leave(leaving: list[str]): None
+ move_next(): Ticket
+ move_previous(): Ticket | BacklogItem
+ move_to(stage: str, done: bool = False): Ticket | BacklogItem
+ close(leaving: list[str] | None = None): Ticket
+ archive(): Ticket
+ violations(): Report
	-> FidelityProgress.report
	-> Session.from_project

## BacklogItem : Card

Hold an idea not yet started.

+ BacklogItem(path: Path, board: Board)
------
+ path: Path
+ path_from_project: str
+ title: str
+ column: Column
+ text: str
+ last_activity: str
----
+ load(backlog_item: str, project: Path | str): BacklogItem
+ create(title: str, text: str = '', project: Path | str): BacklogItem
+ from_ticket(ticket: Ticket): BacklogItem
+ write_if_missing(title: str): None
+ start(scope: str = 'feature', path: str = ''): Ticket
	-> Session.keep_file
+ move_next(): Ticket
+ move_previous(): BacklogItem

## FidelityProgress

*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket.

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool, ticket: Ticket)
------
+ ticket: Ticket
+ << association >> fidelity: FidelityGuidance
+ stage: Stage
+ practice: PracticeGuidance
+ is_enabled: bool
+ done_actions: list[str]
+ remaining_actions: list[str]
+ next_action: str
+ allowed_actions: list[str]
+ has_violations: bool
+ is_done: bool
+ state: str
+ action_states: ActionStates
+ report_file: str
+ latest_report: ReportFile | None
+ violation_count: int
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket): FidelityProgress
+ load(ticket: str, fidelity: str, project: Path | str): FidelityProgress
+ finish_review(): FidelityProgress
+ report(): Report
+ help(): Help
+ files(): dict[str, list[FileEntry]]
+ with_violations(): FidelityProgress

# tools/file_manager

The *FileManager* lists and reads the files under a session's roots; a *FileEntry* is one declared file and whether it exists. space/session, space/repo, and space/kanban import it, and it imports nothing of space.

- **Purpose:** Give every caller one safe way to list and read a session's files, confined to the folders that session works in.
- **Seam (terms):** FileManager, FileEntry, FileText, PathOutsideRootsError
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp

## FileManager

List and read the files under a session's roots, the folders its practices work in.

+ FileManager(workpath: Path | str, roots: tuple[Path, ...])
------
+ workpath: Path
+ roots: tuple[Path, ...]
----
+ load(project: Path): FileManager
+ list(folder: str = ''): Folder
+ read(path: str): FileText
	// never reads a path outside the session's roots; such a path raises PathOutsideRootsError
+ find(pattern: str): list[Path]

## FileEntry

One file something declares, such as a fidelity's output, as a path from the project, and whether it is there yet.

+ FileEntry(path: str, exists: bool)
------
+ path: str
+ exists: bool
----

## FileText

The text of one file, with its path from the workpath; no text for a file that is not there.

+ FileText(path: str, text: str)
------
+ path: Annotated[str, SourceFile]
+ text: str
----

## PathOutsideRootsError : ValueError

A path outside every root of the session, which a page may name but never reach.

+ PathOutsideRootsError(path: str)
------
----

# tools/chat

A *Chat* is one connected Claude Code chat the board can send a command to.

- **Purpose:** Let the board drive any connected chat without the chats and the board sharing a process.
- **Seam (terms):** Chat
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp

## Chat

Reach a Claude Code chat from outside it: list the chats that are connected, and send one a command.

+ Chat(folder: Path)
------
+ id: str
+ name: str
+ is_busy: bool
+ folder: str
+ is_connected: bool
----
+ load(chat: str): Chat
+ list(): list[Chat]
+ send(kind: CommandKind, text: str): Chat
+ messages(): list[ChatMessage]
+ check_in(is_busy: bool = False, name: str = '', folder: str = ''): list[ChatCommand]
+ confirm(message: str, is_shown: bool, reason: str = ''): Chat
+ finish(message: str): Chat
+ resend(message: str): Chat
+ remove(message: str): Chat

# tools/echo

*Echo* shows an action's instructions inside a do-not-follow fence.

- **Purpose:** Inspect what an action instructs, for debugging guidance, without running it.
- **Seam (terms):** Echo
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp

## Echo

Echo wrapped action instructions inside a DO-NOT-FOLLOW fence so the user can inspect them.

------
----
+ fence(body: str): str
+ echo_session(): str

# tools/granola

*Granola* files meeting notes into folders and writes the ones that matter as `.context` files.

- **Purpose:** Keep meeting notes organized in Granola and turn the ones that matter into context files beside the work they inform.
- **Seam (terms):** Granola
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/installation, harness/mcp

## Granola

Organize Granola notes into folders and capture notes as independent .context files, in the project the call works on.

+ Granola(project: Path | str)
------
+ root: Path
----
+ of_project(project: Path): Granola
+ format_filing_plan(plan: str): str
+ list_note_context(folder: str): str
+ write_note_context(folder: str, note_id: str, title: str, date: str, url: str, content: str): str
+ organize(scope: str = 'unfiled'): str
+ context(notes: str, folder: str): str

# tools/prompt_log

*PromptLog* writes each IDE event's entry to the open session's log folder.

- **Purpose:** Record what crossed to the model during a session without changing it.
- **Seam (terms):** PromptLog
- **Dependencies (one-way):** harness/agent_tools, harness/hooks, harness/installation, space/session

## PromptLog

Audit what Cursor sends the model — one `@Hook` per event, each writing that event's entry to the log.

+ PromptLog(log: Path | None = None)
------
----
+ log_for(payload: HookPayload): Path
+ before_submit_prompt(payload: HookPayload): dict
+ before_read_file(payload: HookPayload): dict
+ pre_tool_use(payload: HookPayload): dict
+ subagent_start(payload: HookPayload): dict
+ after_agent_response(payload: HookPayload): dict

# tools/prompt_notify

*PromptNotify* shows a toast naming the action, practice, or fidelity a tool call used. The whole model of this module, internals included, is `tools/prompt_notify/.context/prompt-notify-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Make the guidance an agent is following visible to the person while it runs.
- **Seam (terms):** PromptNotify
- **Dependencies (one-way):** harness/name, harness/marks, harness/agent_tools, harness/guidance, harness/installation, harness/hooks, harness/installer, space/session

## PromptNotify

Echo detected action, practice, fidelity, and guideline names on preToolUse.

------
+ catalog: list[tuple[str, str]]
----
+ on_pre_tool_use(payload: HookPayload): dict
+ handle(payload: HookPayload, toolsets: list | None = None): dict
+ detect_echo(payload: HookPayload, toolsets: list | None = None): tuple[str, str] | None
+ detect(payload: HookPayload): tuple[str, str] | None
+ echo_toolsets(): list
+ show_toast(toast: str, workspace_roots: list[Path]): list[Path]
+ show_ide_toast(echo: str, workspace_roots: list[Path | str]): list[Path]
+ install_ide_toast_extension(): Path

# cdd_guidance/actions

Each action is a *GuidanceAction*: *Generate*, *Validate*, *Document*, *Render*, *Satisfy*, *Sketch*, *Partition*, *Iterate*, *GrillContext*, *Improvement* (repair), and *Diagnose*. A *SketchOutline* is a sketch file, read one *SketchLens* (one practice's section) at a time.

- **Purpose:** Give every practice the same generate, document, validate, satisfy, render, sketch, partition, grill, iterate, repair, and diagnose steps, so a practice owns only its words, rules, and formats.
- **Seam (terms):** Generate, Validate, Document, Render, Satisfy, Sketch, SketchOutline, SketchLens, Partition, Iterate, GrillContext, Improvement, Diagnose
- **Dependencies (one-way):** harness/agent_tools, harness/markdown, harness/guidance, harness/guidance_actions, harness/installation, harness/mcp, harness/graph

## Generate : GuidanceAction

Write the artifacts each listed guidance asks for at its current fidelity.

------
----
+ generate(guidance: GuidanceArg): str
	-> GuidanceAction.run
+ add_generate_header_to_generated(): str
+ generate_output(): str
+ generate_fixes_from_validate(): str

## Validate : GuidanceAction

Check artifacts against each listed guidance's rules and save the report.

+ Validate(session = None)
------
----
+ validate(guidance: GuidanceArg, rule: Rule | None = None, graph: bool | str | list[str] | None = None, paths: list[str] | None = None): str
+ listed_rules(): str
+ create_rule(guidance: GuidanceArg, failed: str = '', wanted: str = ''): str

## Document : GuidanceAction

Record what already exists for each listed guidance without correcting it.

------
----
+ document(guidance: GuidanceArg, paths: list[str]): str

## Render : GuidanceAction

Convert already-generated content into another format.

------
----
+ render(guidance: GuidanceArg, format: str, paths: list[str] | str, content: str = '', source: str | None = None): list
	-> GuidanceAction.document_named
+ place_rendered(): str

## Satisfy : GuidanceAction

Validate, fix from the report, and validate again.

------
----
+ satisfy(guidance: GuidanceArg): str

## Sketch : GuidanceAction

Sketch a solution interactively before generating the formal artifact.

+ Sketch(agent_dir: str = '', session = None)
------
+ sketch_template: str
----
+ made_for(session): Sketch
+ find_template(agent_dir: str = ''): str
+ save_sketch(content: str = '', paths: list[str] | str | None = None, module: str = ''): str
+ list_sketches(module: str = ''): str
+ review_sketch(): str
+ sketch(guidance: GuidanceArg): str

## SketchOutline

A sketch whose hierarchy is carried by markdown headings above fenced detail.

+ SketchOutline(text: str, nesting_indent: int = 2)
------
----
+ holds(lens: SketchLens): bool
+ body_for(lens: SketchLens): str

## SketchLens

The section of a sketch that one practice writes, opened by the headings the practice declares.

+ SketchLens(titles: tuple[str, ...])
------
+ titles: tuple[str, ...]
----
+ of(practice: str): SketchLens
+ every(): tuple[SketchLens, ...]
+ opens(title: str): bool

## Partition : GuidanceAction

Split a corpus into an index and verbatim segments.

------
----
+ verify_segment_completeness(segment_path: str, expected_names: str = '', min_body_chars: int = MIN_ENTRY_BODY_CHARS, index_path: str = ''): str
+ partition_guidance(): str
+ index(context: str = '', out_root: str | None = None, paths: list[str] | str | None = None): str
+ segment(out_root: str | None = None): str
+ partition_corpus(context: str = '', mode: str = 'one_go', paths: list[str] | str | None = None, out_root: str | None = None): str
+ partition(guidance: GuidanceArg, context: str = '', mode: str = 'one_go', out_root: str | None = None, paths: list[str] | str | None = None): str

## Iterate : GuidanceAction

Grill, then generate and validate one small slice at a time.

------
----
+ mark_iterate_round(): str
+ iterate(guidance: GuidanceArg): str

## GrillContext : GuidanceAction

Interview a plan relentlessly against the codebase context until reaching shared understanding.

------
----
+ explore_context_files(folder: str = ''): str
+ read_context_file(path: str): str
+ write_grill_answer(heading: str, body: str): str
+ grill(guidance: GuidanceArg): str
+ generate_each(): list
+ grill_with_context(plan: str = '', paths: list[str] | str | None = None): str

## Improvement : GuidanceAction

Repair a guidance's artifact for one violation, and re-check a repair theme.

------
----
+ repair_loop(): str
+ repair(guidance: GuidanceArg, asset: str = '', violation: str = ''): str
+ verify_fix(guidance: GuidanceArg, theme: str): str

## Diagnose : GuidanceAction

Disciplined diagnosis loop for hard bugs and performance regressions.

------
----
+ diagnose(guidance: GuidanceArg | None = None): str

# cdd_guidance/practices/clean_engineering

*CleanEngineering* is the practice; *CleanEngineeringModel* is the one class model every format reads and writes (modules, classes, properties, operations); *CodeLanguage* and *CodeBody* are what every code format shares; *Drawio* draws the model as a class diagram, placing cards and routing arrows with *ArrowRouter*. The whole model of this module, internals included, is `cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md and cdd_guidance/practices/clean_engineering/model/drawio/.context/drawio-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep boundaries, types, and code consistent, so a change stays inside one module instead of spreading to every caller.
- **Seam (terms):** CleanEngineering, CleanEngineeringGraph, CleanEngineeringModel, Module, OoadClass, Property, Operation, MarkdownCleanEngineeringModel, PythonCleanEngineeringModel, CodeLanguage, CodeBody, WrittenBlock, CallGraphEntry, Drawio, Geometry, DiagramCard, DiagramArrow, ArrowRouter
- **Dependencies (one-way):** harness/agent_tools, harness/markdown, harness/guidance, harness/installation, harness/graph, cdd_guidance/actions

## CleanEngineering : PracticeGuidance

The Clean Engineering practice: modules, model, and code.

+ CleanEngineering(fidelity: str = 'modules', format: str | None = None)
------
+ << composition >> drawio: Drawio
----
+ generate_output(): str

## CleanEngineeringGraph : GraphPractice

Clean Engineering's nodes, its rules, and the draw.io rules it checks on a diagram's nodes.

------
----
+ own_rules(): dict
+ language_rules(language: str): dict
+ read(practice: PracticeGraph): None

## CleanEngineeringModel : OoadNode

One class model that every format reads and writes: modules holding classes.

+ CleanEngineeringModel(name: str | Graph = '', sequential_order: int = 1, graph: Graph | None = None)
------
+ path: str
+ module_type: type
+ << composition >> modules: list[Module]
----
+ every_class(): list[OoadClass]
+ as_record(): dict
+ update_self(source: OoadNode): None
+ clone(): CleanEngineeringModel
+ load(path: str): CleanEngineeringModel
+ save(): str
+ parse(text: str): CleanEngineeringModel
+ sync(text: str, canonical: CleanEngineeringModel): UpdateReport
+ load_content(): None
+ load_modules(): None
+ has_more_module(): bool
+ load_next_module(): Module
+ get_next_module_from_file(): Module
+ load_module(source: Module): Module
+ child_collections(source: OoadNode): list[ChildCollectionPair]

## Module : OoadNode

A named module boundary grouping closely related classes.

+ Module(name: str, sequential_order: int, description: str = '', seam: str = '', constraint: str = '', seam_terms: list[str] | None = None, dependencies: list[str] | None = None, graph: Graph | None = None)
------
+ description: str
+ seam_terms: list[str]
+ dependencies: list[str]
+ modules: list[Module]
+ << composition >> classes: list[OoadClass]
----
+ as_record(): dict
+ public_terms(): list[str]
+ update_self(source: OoadNode): None
+ clone(): Module
+ load_module(source: Module): Module
+ load_class(source: OoadClass): OoadClass
+ load(): None
+ load_modules(): None
+ has_more_module(): bool
+ load_next_module(): Module
+ get_next_module_from_file(): Module
+ append_module(module: Module): None
+ append_class(oclass: OoadClass): None
+ load_classes(): None
+ has_more_class(): bool
+ load_next_class(): OoadClass
+ get_next_class_from_file(): OoadClass
+ load_source_facts(text: str, file: Path, root: Path): None
+ import_targets(text: str, file: Path, root: Path): list[str]
+ load_folder_facts(folder: Path): None
+ child_collections(source: OoadNode): list[ChildCollectionPair]

## OoadClass : OoadNode

A class in the model: what it remembers, what it does, and how it relates.

+ OoadClass(name: str, sequential_order: int, intent: str = '', properties: list[Property] | None = None, operations: list[Operation] | None = None, relationships: list[Relationship] | None = None, collaborators: list[str] | None = None, line: int | None = None, graph: Graph | None = None)
------
+ intent: str
+ stereotypes: list[str]
+ bases: list[str]
+ << composition >> properties: list[Property]
+ << composition >> operations: list[Operation]
+ relationships: list[Relationship]
----
+ load_source_facts(class_text: str): None
+ declared_bases(known_names: Iterable[str]): list[str]
+ update_self(source: OoadNode): None
+ clone(): OoadClass
+ as_record(): dict
+ load_relationship(source: Relationship): Relationship
+ load_property(source: Property): Property
+ load_operation(source: Operation): Operation
+ child_collections(source: OoadNode): list[ChildCollectionPair]
+ load_properties(): None
+ has_more_property(): bool
+ load_next_property(): Property
+ get_next_property_from_file(): Property
+ load_operations(): None
+ has_more_operation(): bool
+ load_next_operation(): Operation
+ get_next_operation_from_file(): Operation
+ place_relationship(relationship: Relationship): None
+ load_relationships(): None
+ has_more_relationship(): bool
+ load_next_relationship(): Relationship
+ get_next_relationship_from_file(): Relationship

## Property : OoadNode

Something a class remembers or derives, with its relationship when its type names a domain class.

+ Property(name: str, sequential_order: int = 0, type_hint: str = '', description: str = '', graph: Graph | None = None)
------
+ type_hint: str
+ relationship: Relationship | None
----
+ clone(): Property
+ derive_relationship(): None
+ save(): str
+ render(): str
+ as_record(): dict
+ update_self(source: OoadNode): None
+ child_collections(source: OoadNode): list[ChildCollectionPair]

## Operation : OoadNode

Something a class does: its parameters, return, interactions, and invariants.

+ Operation(name: str, sequential_order: int = 0, return_type: str = '', description: str = '', callees: list[str] | None = None, parameters: list[str] | None = None, **fields)
------
+ return_type: str
+ callees: list[str]
+ << composition >> body: CodeBody
+ owner: str
+ parameters: list[Parameter]
----
+ clone(): Operation
+ load_span_facts(source_span: str): None
+ load_brace_body_facts(body: str): None
+ load_python_function_facts(node): None
+ save(): str
+ render(): str
+ as_record(): dict
+ update_self(source: OoadNode): None
+ load_parameters(): None
+ has_more_parameter(): bool
+ load_next_parameter(): Parameter
+ get_next_parameter_from_file(): Parameter
+ load_parameter(source: Parameter): Parameter
+ child_collections(source: OoadNode): list[ChildCollectionPair]

## MarkdownCleanEngineeringModel : CleanEngineeringModel

The markdown format of the class model: a `#` heading per module and a `##` card per class.

------
----
+ load_module(source: Module): MarkdownModule
+ load_class(source: OoadClass): MarkdownOoadClass
+ load_content(): None
+ has_more_module(): bool
+ get_next_module_from_file(): MarkdownModule
+ parse(text: str): MarkdownCleanEngineeringModel
+ render(canonical: CleanEngineeringModel | None = None, previous: str | None = None): str
	-> translate_from
+ from_workspace(root: Path): MarkdownCleanEngineeringModel | None

## PythonCleanEngineeringModel : CodeCleanEngineeringModel

The Python format of the class model.

------
----
+ load_module(source: Module): PythonModule
+ parse(text: str): PythonCleanEngineeringModel
+ file_header(canonical: CleanEngineeringModel, preamble: CodeBody): list[str]
+ class_open(oclass: OoadClass, known_names: list[str]): list[str]
+ class_close(has_members: bool): list[str]
+ property_line(prop: Property, contract: bool): list[str]
+ constructor_lines(oclass: OoadClass, constructor: Operation | None, body: list[str]): list[str]
+ signature(operation: Operation, contract: bool): list[str]
+ block_close(): list[str]

## CodeLanguage

How one programming language spells what every code channel writes the same way.

+ CodeLanguage(name: str, line_comment: str, indent: str, unfinished: str, spelling: CodeSpelling, type_names: dict[str, str])
------
+ name: str
+ line_comment: str
----
+ named(name: str): CodeLanguage
+ comment(text: str): str
+ is_unfinished(text: str): bool
+ identifier(name: str): str
+ type_name(hint: str): str
+ interaction(callee: str): str
+ assignment(name: str): str

## CodeBody

The statements inside one operation, test, or step, kept with the language they were read in.

+ CodeBody(text: str = '', language: CodeLanguage | None = None)
------
+ text: str
+ << association >> language: CodeLanguage | None
+ is_empty: bool
	// a body that is unfinished in its language is empty
----
+ mentions(word: str): bool
+ lines_in(language: CodeLanguage, indent: str, unfinished: str): list[str]
+ in_language_of(other: CodeBody, language: CodeLanguage): CodeBody

## WrittenBlock

The source lines around one block of code that no node holds, kept exactly as read.

+ WrittenBlock(language: CodeLanguage, key: WrittenKey, lead: list[str], heading: list[str])
------
+ << association >> language: CodeLanguage
----
+ is_in(language: CodeLanguage, key: WrittenKey): bool
+ split_inside(lines: list[str], inside: tuple[int, int], children: list[tuple[int, int]]): tuple[list[str], list[list[str]], list[str]]
+ inside_for(body: CodeBody): list[str] | None
+ lead_body(): CodeBody
+ closing_body(): CodeBody

## CallGraphEntry

One line in an indented call graph.

------
+ depth: int
+ kind: str
+ text: str
----

## Drawio

Draw the class model as a draw.io diagram, then scan its layout and repair the generator.

+ Drawio()
------
+ module_dir: Path
+ domain_slug: str
----
+ contexts(): str
+ examples(): str
+ create_diagram(content: str, path: str): str
+ scan(paths: list[str]): str
+ validate(): str
+ repair(asset: str, violation: str): str
+ render(content: str = '', path: str = ''): str
+ verify_regression(examples_root: str = ''): str

## Geometry : NamedTuple

x, y, width, height of one placed node.

------
+ x: float
+ y: float
+ width: float
+ height: float
+ center: tuple[float, float]
----
+ overlaps(other: Geometry): bool
+ shifted(dx: float, dy: float): Geometry
+ moved_to(x: float, y: float): Geometry

## DiagramCard

A box to place or route around for a view with no diagram node of its own, such as the DDD aggregate view.

------
+ cell_id: str
+ width: float
+ height: float
+ group: str
+ x: float
+ y: float
+ << composition >> geometry: Geometry
----

## DiagramArrow

The line drawn between two cards for every relationship one class has to another.

------
+ source: str
+ target: str
+ kind: str
+ label: str
+ exit_side: str
+ entry_side: str
+ exit_point: Point
+ entry_point: Point
+ corners: list[Point]
+ cells: list[Point]
+ routed: bool
+ path: list[Point]
----

## ArrowRouter

Routes every arrow, retrying the ones that crossed until a pass finds nothing better.

+ ArrowRouter(cards: list[Card], arrows: list[DiagramArrow], obstacles: Iterable[Geometry] = (), kept_paths: Iterable[list[Point]] = ())
------
----
+ route(): list[DiagramArrow]
	// an arrow never passes through a card or runs along another arrow

# cdd_guidance/practices/stories

*Stories* is the practice; a *StoryModel* holds *Epic*, *Story*, *Scenario*, and *Step* objects, and the diagram and JavaScript formats extend them. The whole model of this module, internals included, is `cdd_guidance/practices/stories/model/.context/story-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep one Epic, Story, Scenario hierarchy that discovery, specification, and tests all read, so scope and behaviour stay traceable from the map to the code.
- **Seam (terms):** Stories, StoriesGraph, StoryModel, Epic, Story, Scenario, Step, StepType, Example, DiagramStoryModel, DiagramEpic, DiagramStory, JavaScriptStory
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/markdown, harness/guidance, harness/graph, cdd_guidance/actions, cdd_guidance/practices/clean_engineering

## Stories : PracticeGuidance

The Stories practice: story map, scenarios, and acceptance tests.

+ Stories(fidelity: str = 'story_map', format: str | None = None, stage: str | None = None, story_test_folder: str | None = None)
------
----
+ read_paths(paths: list[str] | str, source: str | None = None): None

## StoriesGraph : GraphPractice

The Stories practice's nodes and its rules.

------
----
+ align(node): None
+ read(practice: PracticeGraph): None
+ link(graph: Graph): None

## StoryModel : StoryNode

One story map: its epics and increments.

+ StoryModel(source: StoryModel | Graph | None = None, graph: Graph | None = None)
------
+ << composition >> epics: list[Epic]
+ increments: list[Increment]
----
+ load(root, on_file = None): StoryModel
+ load_files(files, project, on_file = None): StoryModel
+ every_epic(): list[Epic]
+ every_story(): list[Story]
+ append_epic(epic: Epic): None
+ append_increment(increment: Increment): None
+ clone(): StoryModel

## Epic : StoryNode

An epic.

+ Epic(name: str | Epic, sequential_order: int = 0, story_class: type | None = None)
------
+ epics: list[Epic]
+ << composition >> stories: list[Story]
+ has_epics: bool
+ depth: int
----
+ estimate_label(): str
+ clone(): Epic
+ load_map_facts(): None
+ every_epic(): list[Epic]
+ every_story(): list[Story]
+ append_epic(epic: Epic): None
+ append_story(story: Story): None
+ place_in(file: str): None
+ span_columns(): int
+ diagram_span_columns(): int
+ tree_depth(): int

## Story : StoryNode

One story under an epic, with its scenarios.

+ Story(name: str | Story, sequential_order: int = 0, story_type: StoryType = StoryType.USER)
------
+ actors: list[str]
+ backgrounds: list[Background]
+ << composition >> scenarios: list[Scenario]
+ code_key: tuple
----
+ load_map_facts(): None
+ clone(): Story

## Scenario : StoryNode

Behaviour walk-through under a story.

+ Scenario(name: str | Scenario = '', sequential_order: int = 0, story_name: str = '')
------
+ story_name: str
+ backgrounds: list[Background]
+ << composition >> steps: list[Step]
+ code_key: tuple
----
+ steps_in(step_type: StepType): list[Step]
+ when_then_runs(): list[tuple]
+ load_map_facts(): None
+ clone(): Scenario

## Step : StoryNode

One Given, When, or Then line of a scenario.

+ Step(text: str | Step, step_type: StepType | None = None, sequential_order: int = 0, keyword: str = '', concepts: list[str] | None = None, values: list[str] | None = None, actor: str = '', source: SourceLocation | None = None, name: str = '')
------
+ text: str
+ step_type: StepType | None
+ << composition >> call_graph: list[CallGraphEntry]
+ code_key: tuple
+ ands: list[Step]
+ keyword: str
+ is_continuation: bool
+ continuation: bool
+ phase: str
+ callees: list[str]
----
+ clone(): Step

## StepType : str, Enum

Given, When, or Then.

------
----

## Example : StoryNode

One named example.

+ Example(name: str, value: Any = None, sequential_order: int = 0, scope: StoryNode | None = None)
------
----
+ clone(): Example
+ cells(): dict[str, Any]
+ as_code(): str

## DiagramStoryModel : StoryModel

Story map whose epics and stories are the diagram types.

------
+ max_sub_epic_depth: int
+ actor_y: int
+ sub_epic_top: int
+ story_floor: int
+ story_y: int
----
+ sub_epic_y(depth: int): int

## DiagramEpic : Epic, DiagramStoryNode

An epic as the story map diagram draws it.

------
----

## DiagramStory : Story, DiagramStoryNode

A story as the story map diagram draws it.

------
----

## JavaScriptStory : CodeStory

A story read from, or written as, a JavaScript acceptance test.

------
----
+ load_all(content: str): list[JavaScriptStory]
+ load(content: str, story_slug: str): JavaScriptStory
+ create(story: Story, relative_story_test_path: str = '../../story-test.js', relative_types_path: str | None = None, **kwargs): str

# cdd_guidance/practices/ddd

*Ddd* is the practice: bounded contexts, the aggregate model, and tactics. *DddGraph* reads DDD's nodes after Clean Engineering's classes. The whole model of this module, internals included, is `cdd_guidance/practices/ddd/model/.context/ddd-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep the software in the business's language, with each rule held in the aggregate that owns it, before any technical detail is added.
- **Seam (terms):** Ddd, DddGraph
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/markdown, harness/guidance, harness/graph, cdd_guidance/actions, cdd_guidance/practices/clean_engineering

## Ddd : PracticeGuidance

The DDD practice: bounded context, model, and tactics.

+ Ddd(fidelity: str = 'bounded_context', format: str | None = None, stage: str | None = None)
------
----

## DddGraph : GraphPractice

DDD's nodes, read after Clean Engineering's classes, and its rules with Clean Engineering's.

------
----
+ own_rules(): dict
+ read(practice: PracticeGraph): None

# cdd_guidance/practices/ux

*Ux* is the practice: information architecture, mockups, and front-end code. *UxGraph* names its node types and rules. The whole model of this module, internals included, is `cdd_guidance/practices/ux/model/.context/ux-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep screens, navigation, and interactions in one hierarchy that the diagram, the mockup, and the front-end code all follow.
- **Seam (terms):** Ux, UxGraph
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/guidance, harness/graph, harness/design_canvas, cdd_guidance/practices/stories

## Ux : PracticeGuidance

The UX practice: information architecture, mockup, and front-end code.

+ Ux(fidelity: str = 'ia', format: str | None = None)
------
----
+ ensure_javascript(practice: str, source_format: str, content: Any): dict
+ javascript_practice(key: str): PracticeGuidance

## UxGraph : GraphPractice

The UX practice's node types and its rules.

------
----

# cdd_guidance/practices/bdd

*Bdd* is the practice: behavior, realization, and development. *BddGraph* links each observation to the Clean Engineering members it drives. The whole model of this module, internals included, is `cdd_guidance/practices/bdd/model/.context/bdd-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Turn domain vocabulary into passing tests, locking what is observed before how it is built.
- **Seam (terms):** Bdd, BddGraph
- **Dependencies (one-way):** harness/name, harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/actions, cdd_guidance/practices/clean_engineering

## Bdd : PracticeGuidance

The BDD practice: behavior, realization, and development.

+ Bdd(fidelity: str = 'behavior', format: str | None = None)
------
----

## BddGraph : GraphPractice

BDD's describe trees, linked to the Clean Engineering members each observation drives.

------
----
+ read(practice: PracticeGraph): None
+ link(graph: Graph): None

# cdd_guidance/practices/agent_bdd

*AgentBdd* is the practice for specs that drive a real agent and judge what it did.

- **Purpose:** Test agent behaviour end to end against a real agent, so a spec fails when the agent would actually do the wrong thing.
- **Seam (terms):** AgentBdd
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/installation, harness/mcp, harness/installer, space/session, cdd_guidance/actions, cdd_guidance/practices/bdd

## AgentBdd : PracticeGuidance

The agent BDD practice: mamba specs that drive a real agent.

+ AgentBdd(format: str = 'python')
------
----
+ generate_output(): str

# cdd_guidance/patterns

Each pattern is a *PracticeGuidance* that adds rules for one kind of solution; *DomainDrivenStack* is the base for a domain-organized TypeScript stack such as *LernDomainDriven* and *MernDomainDriven*.

- **Purpose:** Add the guidance and the graph rules one kind of solution needs on top of the practices, without changing a practice.
- **Seam (terms):** DomainDrivenStack, LernDomainDriven, MernDomainDriven, CddWebDomainAccess, CddClaudeMod
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices/stories

## DomainDrivenStack : PracticeGuidance

Implementation fidelity for a domain-module-organized TypeScript stack on an already-designed vertical slice.

+ DomainDrivenStack()
------
+ story_test_folder: str | None
----

## LernDomainDriven : DomainDrivenStack

The LERN stack: lowdb JSON files, Express, React, and Node, in TypeScript, organized by domain module.

------
----

## MernDomainDriven : DomainDrivenStack

The MERN stack: MongoDB, Express, React, and Node, in TypeScript, organized by domain module.

------
----

## CddWebDomainAccess : PracticeGuidance

How code outside Python reaches the CDD domain: through MCP tools, by a language adapter the installer deploys.

+ CddWebDomainAccess()
------
----

## CddClaudeMod : PracticeGuidance

A Claude Code mod that is a view of the CDD domain: each component runs view, client, MCP tool, domain.

+ CddClaudeMod()
------
----

# cdd_guidance/builders

A *Builder* is guidance for building a new part of CDD; *CreateAgentToolset* and *CreatePracticeGuidance* are the two builders.

- **Purpose:** Start every new toolset and practice from the same templates, so it installs and runs with the existing actions on its first try.
- **Seam (terms):** Builder, CreateAgentToolset, CreatePracticeGuidance
- **Dependencies (one-way):** harness/agent_tools, harness/guidance

## Builder : PracticeGuidance

Guidance for building a new part of CDD, such as a toolset or a practice.

------
+ default_workspace_folder: str
----

## CreateAgentToolset : Builder

Scaffold a new agent toolset: an @agent_toolset class with @agent_tool and @agent_instructions operations.

------
----

## CreatePracticeGuidance : Builder

Scaffold a new practice: its PracticeGuidance class, its markdown, templates, and examples.

------
----

# cdd_guidance/context_setup

*ContextSetup* converts documents or captures a live app and partitions the result; *ContextIndex* embeds the segments and answers questions with citations.

- **Purpose:** Turn existing documents or a running application into partitioned, indexed context that later stages can search and cite.
- **Seam (terms):** ContextSetup, ContextIndex
- **Dependencies (one-way):** harness/agent_tools, harness/guidance_actions, harness/installation, harness/mcp, cdd_guidance/actions, cdd_guidance/practices/stories, cdd_guidance/practices/ddd, cdd_guidance/practices/ux, cdd_guidance/practices/clean_engineering

## ContextSetup

Convert a folder of documents to markdown and delegate partitioning to selected context tools.

+ ContextSetup(stories: Stories | None = None, clean_engineering: CleanEngineering | None = None, ddd: Ddd | None = None, ux: Ux | None = None, partition: Partition | None = None, context_index: ContextIndex | None = None, session: Any = None)
------
+ session: Any
----
+ for_call(call: ToolCall): ContextSetup
+ convert(folder_path: str): ConversionResult
+ smoke_test(repo_path: str, surface: str = 'web', capture_repo: str = '', base_url: str = '', entry_paths: list[str] | None = None): SmokeTestResult
+ scout_app(repo_path: str, surface: str = 'web', capture_repo: str = '', base_url: str = '', entry_paths: list[str] | None = None): ScoutResult
+ complete_capture(repo_path: str, missing_pages: list[str], surface: str = 'web', capture_repo: str = '', base_url: str = ''): CaptureResult
+ capture_from_live_app(repo_path: str, capture_repo: str = '', surface: str = 'web'): str
+ capture_from_documents(folder_path: str, indexers: list[str] | None = None, first: str = ''): str

## ContextIndex

Embed partitioned segments into a FAISS index and answer questions with source citations.

+ ContextIndex(embedding_provider: EmbeddingProvider | None = None)
------
----
+ embed(segments_paths: list[str], out_path: str): EmbedResult
+ search(query: str, index_path: str, top_k: int = 5): SearchResult
+ ask(question: str, index_path: str): str
