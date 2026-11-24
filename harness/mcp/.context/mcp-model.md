# harness/mcp

The *McpHost* is the one cdd server every chat talks to; it keeps one *McpServer* per project, and *McpInstallation* writes each IDE's `cdd` entry and starts the server from *CddHome*.

- **Purpose:** Let any chat, in any project, call the operations authors annotate `@mcp`, through one long-running server that keeps each project's toolsets apart.
- **Seam (terms):** Mcp, LongCall, McpHost, McpServer, McpInstallation, CddHome, ThrottledReporter
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/process, harness/git

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
+ from_repo(repo: Path | str): McpHost
+ from_refs(toolset_refs: tuple[str, ...], repo: str | None = None, project: str | None = None): McpHost
---<<loads>>--> McpServer
---<<resolves call name>>--> McpServer
---<<creates>>--> RepositoryToolsets
---<<creates>>--> ToolCall
---<<reports progress through>>--> ThrottledReporter
---<<answers with the data of>>--> DataClass

## McpServer

The toolsets one project's calls are answered by: every `@mcp` operation of the toolsets it was started with, published under its MCP name, made for that project.

+ McpServer(repo: str | Path | None = None, project: str | Path | None = None)
------
+ repo: Path | None
+ project: Path | None
+ started: bool
+ tools: dict[str, AgentTool]
+ prompts: dict[str, AgentTool]
+ << composition >> skipped: SkippedTools
----
+ enroll(tool: AgentTool): None
+ start(toolsets: Iterable[Any]): None
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
---<<keeps>>--> AgentTool
---<<loads>>--> AgentToolSet
---<<reads constants of>>--> InstallDestination
---<<reads arguments of>>--> ToolCall
---<<waits longer for operations annotated>>--> LongCall
---<<serves the operations annotated>>--> Mcp

## McpInstallation : ServerInstallation

Record `@mcp` operations, write each IDE's `cdd` entry, and start the one cdd server from `~/.cdd`; it names *CddServerHooks*, the hooks that start the server when a chat starts, as a toolset every install publishes.

+ McpInstallation(layout: IdeLayout, path: Path | str, served: ServedCheckout)
------
+ << association >> served: ServedCheckout
+ daemon: McpDaemon
+ << composition >> claude_plugins: ClaudePlugins
+ << association >> host: McpHost | None
+ mcp_operations: list[AgentTool]
+ toolsets: tuple[type, ...]
+ published: list[str]
+ manifest_path: Path
----
+ write(tool: AgentTool): None
+ record_operation(tool: AgentTool): None
+ write_mcp_manifest(): None
+ allow_cdd_tools(settings: Path): None
+ drop_project_cdd_server(): None
+ drop_user_cdd_server(): None
+ standup(): McpHost | None
+ diagnose(): dict[str, Any]
+ ensure_running(): dict[str, str]
+ status(): list[str]
+ create(layout: IdeLayout, path: Path | str, repo: Path | str | None = None): McpInstallation
+ ensure_server(): str
+ pin_server(): str
+ keep_pinned_current(): str | None
+ serve_from_checkout(): str
+ serves_this_process(): bool
---<<keeps>>--> AgentTool
---<<is handed>>--> ServedCheckout
---<<loads>>--> McpHost
---<<publishes as a cdd MCP tool>>--> Mcp
---<<publishes the server-starting hooks with>>--> Hook
---<<registers with>>--> Installer

## CddHome

The user's cdd folder: which checkout the one server runs, the pinned copy of it, the Python it runs on, and the server's address.

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
+ interpreter: PythonInterpreter
+ install_command: list[str]
+ server_environment: dict[str, str]
----
+ write_claude_plugin(server: dict[str, object]): list[Path]
+ write_mod_plugins(): None
+ is_pinned_to(checkout: Path | str): bool
+ install(checkout: Path | str, connect_script: Path | str): None
+ pin(checkout: Path | str): str
+ serve_from(checkout: Path | str): None
---<<creates>>--> Git
---<<creates>>--> PythonInterpreter
---<<takes the import path from>>--> RepositoryToolsets
---<<reads and writes through>>--> JsonFile

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
