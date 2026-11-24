# harness/mcp

The *McpHost* is the one cdd server every chat talks to; it keeps one *ProjectToolsets* per project. Chats reach it over HTTP through *HttpEndpoints*, which speak MCP to them through a *ChatProtocol*, and that makes one *ChatRequest* for each request a chat sends. *McpInstallation* is the MCP channel's *RegisteredChannel*: it writes each IDE's `cdd` entry, and its *McpChannelServer* stands the server up, starts it from *CddHome*, and installs the plugins of the home's *ClaudeMarketplace* through *ClaudePlugins*.

- **Purpose:** Let any chat, in any project, call the operations authors annotate `@mcp`, through one long-running server that keeps each project's toolsets apart.
- **Seam (terms):** Mcp, LongCall, McpHost, ChatProtocol, HttpEndpoints, ProjectToolsets, ChatRequest, McpInstallation, McpChannelServer, CddHome, ClaudeMarketplace, PublishedPlugin, PublishedMods, ClaudePlugins, PluginInstall, ThrottledReporter
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/process, harness/git

## McpHost

The cdd server's MCP side: one *ProjectToolsets* for each project a chat works on, answering every chat. Chats reach it over HTTP through *HttpEndpoints*, made for it where the server starts. A host serving chats is made with the two lanes and its cdd home, so it hands a call whose project runs on the other lane to that lane; one made in process for a probe or a spec has neither.

+ McpHost(checkout_toolsets: ProjectToolsets, lanes: ServerLanes | None = None, home: CddHome | None = None)
------
+ << composition >> checkout_toolsets: ProjectToolsets
+ projects: list[Path]
----
+ dispatch(name: str, arguments: dict[str, object] | None = None, project: Path | None = None): object
+ answer(call: ToolCall): object
+ answer_for_chat(call: ToolCall, reporter: Callable[[str], None] | None): object
	// on a chat's worker thread: reporter listens to its progress, and the answer is read into data while the call is still the one being answered
+ tools_listed_for(project: Path | None): list[dict[str, Any]]
	// as data, with no MCP SDK: the built-in ping and restart, then the toolsets' own; the other lane's when that lane answers project
+ call_sent(arguments: dict[str, object] | None, project: Path | None, request: ToolRequest): ToolCall
+ tool_request(tool: str): ToolRequest
+ restart(): dict[str, Any]
	// publishes the mods of the code it now runs, so a chat watching them reloads with the restart
+ diagnose(): dict[str, Any]
+ from_repo(repo: Path | str, lanes: ServerLanes | None = None, home: CddHome | None = None): McpHost
+ from_refs(toolset_refs: tuple[str, ...], repo: str | None = None, project: str | None = None, lanes: ServerLanes | None = None, home: CddHome | None = None): McpHost
---<<keeps one per project>>--> ProjectToolsets
---<<resolves call name>>--> ProjectToolsets
---<<creates>>--> ToolCall
---<<answers with the data of>>--> DataClass
---<<publishes the mods on restart through>>--> ClaudeMarketplace

## ChatProtocol

The MCP protocol a host speaks to chats: the SDK's protocol server with the host's handlers, made the first time it is asked for, so a call dispatched in process (a probe, a script, a spec) never loads the SDK. Each call a chat sends runs on a worker thread, and one still running at its time limit is answered as still running.

+ ChatProtocol(host: McpHost)
------
+ << association >> host: McpHost
+ protocol: Any
	// the MCP SDK's protocol server
----
+ content_blocks(answer: SentValue): list[TextContent]
	// the answer as the chat reads it: text, or its data as JSON
---<<answers each call through>>--> McpHost
---<<makes one for each request from the module as it is now>>--> ChatRequest
---<<reports progress through>>--> ThrottledReporter

## HttpEndpoints

Where a host answers over HTTP: MCP at `/mcp`, `/ping`, which says which pid and checkout serve, and `/lane-call`, where the other lane's server hands over a chat's call and hears back its answer or its failure by kind and message. Only this machine's own clients get in. `python -m harness.mcp` makes them for its host and serves.

+ HttpEndpoints(host: McpHost)
------
+ << association >> host: McpHost
+ << composition >> chat_protocol: ChatProtocol
	// the MCP protocol it speaks to chats, made for host
----
+ serve(daemon: McpDaemon, listener: socket.socket): None
+ app(port: int): Any
	// the web app answering on port
---<<answers handed-over calls through>>--> McpHost
---<<serves MCP through>>--> ChatProtocol
---<<replies to the other lane with>>--> LaneReply

## ChatRequest

One request a chat sent the cdd server, from its headers and the port the caller's end of its connection uses. The host makes it from its module as it is now, so a restarted server names chats and calls with the classes its re-imported tools know.

+ ChatRequest(headers: Mapping[str, str], client_port: int | None, claude_settings: Path)
------
+ << association >> process: ClaudeChatProcess | None
	// the process X-CDD-Chat-Process names, else the one holding the request's connection
+ << association >> chat: ChatPointer | None
----
+ project_for(tool: str): Path | None
	// the folder the chat works in now, read on every call; cdd.ping and cdd.restart need none
	// raises ProjectNotNamed when no folder is found, ProjectIsClaudeSettings when it is Claude Code's settings folder
+ tool_request(tool: str, host: McpHost): ToolRequest
---<<names the chat with>>--> ChatPointer
---<<creates>>--> ToolRequest

## ProjectToolsets

The toolsets one project's calls are answered by: every `@mcp` operation of the toolsets it was started with, published under its MCP name, made for that project.

+ ProjectToolsets(repo: str | Path | None = None, project: str | Path | None = None)
------
+ repo: Path | None
+ project: Path | None
+ started: bool
+ tools: dict[str, AgentTool]
+ prompts: dict[str, AgentTool]
+ << composition >> skipped: SkippedTools
----
+ enroll(tool: AgentTool): None
+ start(toolsets: Iterable[ToolsetReference]): None
+ for_project(project: Path): ProjectToolsets
+ restarted(): ProjectToolsets
+ resolve_call_name(name: str): str
+ enrolled(name: str): AgentTool | None
+ call_seconds(name: str): float
+ invoke(mcp_name: str, arguments: dict[str, object] | None = None): object
+ answer(mcp_name: str, call: ToolCall): object
	-> AgentTool.answer
+ of_repo(repo: Path | str): ProjectToolsets
	// every annotated toolset class in repo; raises McpStandupFailed when it cannot stand up
+ of_refs(toolset_refs: tuple[str, ...], repo: str | None = None, project: str | None = None): ProjectToolsets
---<<creates>>--> RepositoryToolsets
---<<keeps>>--> AgentTool
---<<makes each toolset with>>--> ToolsetReference
---<<reads the tools published to Mcp of>>--> AgentToolSet
---<<reads arguments of>>--> ToolCall
---<<waits longer for operations annotated>>--> LongCall
---<<serves the operations annotated>>--> Mcp

## McpInstallation : RegisteredChannel

Record `@mcp` operations and write each IDE's `cdd` entry once every tool is recorded; its server is the one cdd server (*McpChannelServer*). It names *CddServerHooks*, the hooks that start the server when a chat starts, as a toolset every install publishes.

+ McpInstallation(target: InstallTarget, record: InstallRecord, served: ServedCheckout)
------
+ destination: Mcp
+ << association >> served: ServedCheckout
+ lanes: ServerLanes
	// both lanes as the served checkout's sees them; a project pointed at the dev lane names the dev lane's server
+ daemon: McpDaemon
	// the stable lane's server, which every chat's cdd plugin names
+ << composition >> server: McpChannelServer
+ << composition >> cdd_entry: CddEntry
+ mcp_operations: list[AgentTool]
+ toolsets: tuple[type, ...]
+ published: list[str]
----
+ create(target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None): McpInstallation
	// serving repository, else the running checkout, on the lane its folder runs on
+ write(tool: AgentTool): None
+ write_once_recorded(): None
	// writes the IDE's cdd entry, or for Claude Code the cdd plugin, once; nothing when no MCP operation was recorded
+ status(): list[str]
	// whether the server the cdd entry names is running
---<<keeps>>--> AgentTool
---<<is handed>>--> ServedCheckout
---<<stands up and starts the server through>>--> McpChannelServer
---<<publishes as a cdd MCP tool>>--> Mcp
---<<publishes the server-starting hooks with>>--> Hook
---<<registers with>>--> Installer

## McpChannelServer : ChannelServer

The one cdd server as an install handles it: stood up in the install's process over every toolset of the served checkout, to check it loads, then started from `~/.cdd`, and, for Claude Code, the `cdd` plugin and every mod the served code declares installed. Inside the cdd server, as an install through MCP runs, it stands up nothing.

+ McpChannelServer(served: ServedCheckout, lanes: ServerLanes, claude_plugins: ClaudePlugins | None)
	// claude_plugins for Claude Code; none for any other IDE, which installs no plugins
------
+ << association >> served: ServedCheckout
+ runs_this_process: bool
----
+ stand_up(): StandUp
+ ensure_running(): list[str]
	// returns the dev lane to main first when its served feature's worktree is gone, and says so on a `dev lane:` line
+ install_plugins(): list[str]
	// one line for each plugin, `{plugin name}: {state}`: the cdd plugin the stable lane publishes, then the mods of the marketplace of the lane the install serves: the dev lane's when it serves a feature there, else the stable lane's; a full install and every repin run it
---<<loads>>--> McpHost
---<<creates>>--> StandUp
---<<installs the plugins of>>--> ClaudeMarketplace
---<<installs each plugin through>>--> ClaudePlugins

## CddHome

The user's cdd folder: which checkout the one server runs, the pinned copy of it, the Python it runs on, and the server's own files. The Claude Code marketplace it publishes is its own object.

+ CddHome(folder: Path | str | None = None)
------
+ folder: Path
+ state_path: Path
+ log_path: Path
+ connect_script: Path
+ runtime_record: Path
+ pinned_checkout: Path
+ is_installed: bool
+ is_dev_lane: bool
+ source: Path
+ mode: str
+ served_branch: str
+ served_worktree: Path | None
+ interpreter: PythonInterpreter
+ server_environment: dict[str, str]
+ << composition >> marketplace: ClaudeMarketplace
----
+ is_pinned_to(checkout: Path | str): bool
+ return_to_main_when_feature_gone(): str
	// on the dev lane only: withdraws the runtime record once the served feature's worktree is gone, naming the branch and the worktree
+ install(checkout: Path | str, connect_script: Path | str): None
+ pin(checkout: Path | str): str
+ serve_current(checkout: Path | str): None
+ serve_from(checkout: Path | str): None
---<<creates>>--> Git
---<<creates>>--> PythonInterpreter
---<<takes the import path from>>--> RepositoryToolsets
---<<reads and writes through>>--> JsonFile
---<<publishes the mods of the code it serves through>>--> ClaudeMarketplace

## ClaudeMarketplace

The local Claude Code marketplace a cdd home publishes, its `claude-plugins` folder: the `cdd` plugin, which declares the cdd server for every chat, and the mods of the code the server runs. One install publishes into it at a time, so installs from the main checkout and a ticket's worktree at the same moment both finish.

+ ClaudeMarketplace(folder: Path, home: CddHome)
------
+ folder: Path
+ INSTALL_COMMAND: str
	// install.json, the file in a published mod naming the command its Run install runs
+ cdd_plugin: PublishedPlugin
+ mods: list[PublishedPlugin]
+ install_command: list[str]
----
+ plugin(name: str): PublishedPlugin
+ mod_folder(plugin: PublishedPlugin): Path
	// a served checkout's own mod folder, so an edit there reloads in every chat, else the published copy
+ publish_cdd_plugin(server: dict[str, object]): list[Path]
+ publish_mods(code: Path): None
	// into this lane's own marketplace only: a dev lane's mods never reach the stable lane's marketplace
---<<creates>>--> PublishedPlugin
---<<finds the mods to publish through>>--> PublishedMods
---<<publishes the mods one install at a time, holding>>--> InstallLock
---<<reads and writes through>>--> JsonFile

## PublishedPlugin

One plugin of the marketplace by its name, and the one owner of its `{name}/.claude-plugin/plugin.json`. A mod is published from its folder in the code the server runs, versioned by a hash of its files, because Claude Code keeps a plugin it has already seen at the same version.

+ PublishedPlugin(marketplace: ClaudeMarketplace, name: str)
------
+ << association >> marketplace: ClaudeMarketplace
+ name: str
+ folder: Path
+ is_published: bool
+ manifest: dict[str, Any]
+ version: str
+ description: str
+ installed_name: str
	// {name}@cdd-home
----
+ write_manifest(manifest: dict[str, Any]): Path
+ publish_from(mod: PublishedMod): None
---<<reads and writes its manifest through>>--> JsonFile

## PublishedMods

The mods a checkout's code declares, each a *PublishedMod*: a folder holding `.claude-plugin/plugin.json` and a `cdd-mod.json` beside it, which names the plugin, the files of the checkout it carries besides its own, and the file its Run install command is written to. A mod declares itself in its own folder, so harness/mcp names no folder of a module built on it, and a pinned server publishes the mods its own code declares.

+ PublishedMods(code: Path)
------
+ code: Path
+ every: list[PublishedMod]
----

## ClaudePlugins

The plugins a cdd home's marketplace publishes, loaded by Claude Code from one fixed folder per plugin, `~/.cdd/chat-plugins/{name}`, which its user settings name in `CLAUDE_CODE_PLUGIN_DIRS`, never from a copy in its own plugin cache: a cached copy keeps the version it was installed at, so a mod published afterwards never reaches the chats. Every install and repin points the fixed folder at the published folder of the lane the `cdd` plugin serves, the stable lane, for the `cdd` plugin and every mod alike (a directory junction on Windows, a symbolic link elsewhere), so a mod never calls a server from another lane. The settings name the same folder after the first time, so a repin and `/reload-plugins` reach every chat with no restart of the app. There is one fixed folder per plugin, not one per lane, so a dev lane's mods would reach every chat while their server, the one the `cdd` plugin names, stays on the stable lane (issue 106). A cached copy found at install is uninstalled with the `claude` command, along with a checkout's own marketplace (`abd-works`). A plugin is a convenience on top of the install, so a miss is printed, never raised.

+ ClaudePlugins(home: CddHome | None = None, claude_folder: Path | None = None)
------
+ installed: dict[str, str]
+ claude_cli: str | None
----
+ install(plugin: PublishedPlugin): PluginInstall
	// points chat-plugins/{name} at the plugin's published folder, names that fixed folder in CLAUDE_CODE_PLUGIN_DIRS in place of any other folder of the plugin (a published copy, another home's fixed folder, or any folder whose manifest names the plugin, such as a checkout's own mod folder), and uninstalls every cached copy
---<<loads from its folder>>--> PublishedPlugin
---<<creates>>--> PluginInstall
---<<reads and writes Claude Code's settings through>>--> IdeLayout

## PluginInstall

What installing one plugin came to, printed as its state: watched (Claude Code loads it from its folder already), watched from now on (the install named the fixed folder just now; Claude Code reads it when the app restarts, the only restart it needs, since later repins move only where the fixed folder leads), or a cached copy still loaded (no claude command to uninstall it).

+ PluginInstall(state: str)
------
+ state: str
+ WATCHED: str
+ NEWLY_WATCHED: str
+ CACHED: str
----

## ThrottledReporter

Passes a tool's progress on to its chat at most four times a second.

+ ThrottledReporter(reporter: Reporter, seconds: float = _REPORT_SECONDS)
------
----

## Mcp : Destination

`@mcp` on an operation: install publishes it as the MCP tool `{toolset}.{operation}` of the one `cdd` server, whose entry McpInstallation writes to the IDE's MCP config (`.mcp.json`, `~/.claude.json`).

------
----

## LongCall : Annotation

`@long_call` on an MCP operation: the cdd server waits `LONG_CALL_SECONDS` (600) for its answer instead of `CALL_SECONDS` (10) before telling the chat it is still running.

------
----
