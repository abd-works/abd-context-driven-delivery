# harness/diagnostics

This module reports whether CDD is running and answering: *ServerHealth* says which of its long-running parts are up right now, and the diagnostics toolsets, each a *CallDiagnostics* made for one call, probe what an install published through the MCP host answering that call and write a report section.

- **Purpose:** Show whether CDD is running: which of its servers and apps are up, for the chat's server health band, and whether what an install published answers through the live MCP host, so a broken publication shows up in a report rather than in a failing chat.
- **Seam (terms):** ServerHealth, CallDiagnostics, DiagnosticsNeedACall, AgentToolsDiagnostics, GuidanceDiagnostics, AgentToolsProbe, GuidanceProbe; the MCP operations `server-health.report`, `agent-tools-diagnostics.agent_tools_diagnostics`, `guidance-diagnostics.guidance_diagnostics`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/process, harness/git, harness/hooks, harness/mcp, harness/guidance, harness/graph

## ServerHealth

Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal: every registered *App*, each read as it is now, and the latest heavy and e2e test runs.

+ ServerHealth(repo_root: Path | str, cadence: TestCadence | None = None, e2e_review: E2eReview | None = None)
------
+ apps: list[App]
----
+ load(project: Path | str): ServerHealth
+ report(): ServerHealth
---<<aggregation>>--> App
---<<annotated with>>--> LanguageAdapter

## App

One CDD web app a person opens beside the chat (Kanban, Graph, Story UI), and the one registry of them. The module that owns each app makes it once and registers it: the Graph app here, from `GRAPH_APP_PORTS`; the CDD Kanban and the Story UI editor in space/kanban.

+ App(label: str, folder: Path, server: AppServer, page: str = "/")
------
+ label: str
+ status: AppStatus
+ port: int | None
+ url: str
+ server: AppServer
+ is_installed: bool
----
+ register(): App
+ registered(): list[App]
+ load(app: str, project: Path | str): App
+ open(): App
+ install(): App
---<<raises>>--> AppNotRegistered
---<<raises>>--> AppNotStarted
---<<aggregation>>--> AppServer
---<<annotated with>>--> LanguageAdapter

## AppServer

The server an app answers from, which the chat that opens the app starts and its end stops: the folder it runs in, the command that starts it (node on its script, through tsx for TypeScript), and the ports it tries in turn.

+ AppServer(folder: Path, script: str, ports: tuple[int, ...])
------
+ folder: str
+ command: list[str]
+ port: int | None

## CallDiagnostics

A diagnostics toolset made for one call: it holds the call, so it probes through the MCP host answering it, and the install of the project the call names, made once. The toolset an install publishes is made with no call and answers each call through `for_call`.

+ CallDiagnostics(call: ToolCall | None = None)
------
+ << association >> call: ToolCall
----
+ for_call(call: ToolCall): CallDiagnostics
---<<creates>>--> Installer
---<<raises>>--> DiagnosticsNeedACall

## AgentToolsDiagnostics : CallDiagnostics

Probe the space, harness, and tools MCP operations an install published (ping and invoke), through the MCP host answering the call.

------
----
+ agent_tools_diagnostics(guidance: list[str] | None = None): str
---<<creates>>--> AgentToolsProbe

## GuidanceDiagnostics : CallDiagnostics

Probe installed guidance instructions and guidance-action MCP operations, through the MCP host answering the call.

------
----
+ guidance_diagnostics(guidance: list[str] | None = None): str
---<<creates>>--> GuidanceProbe
---<<calls instructions on>>--> GuidanceProbe
---<<calls actions on>>--> GuidanceProbe

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
---<<loads>>--> McpHost
---<<creates>>--> ProbeArguments
---<<creates>>--> ProbeSection

## GuidanceProbe

A probe of the guidance one install deployed, made for its Installer and the guidance slugs that filter what it calls; it leaves `improvement.repair` and `improvement.verify_fix` alone and reports them skipped.

+ GuidanceProbe(installer: Any, slugs: list[str])
------
+ installer: Installer
+ slugs: list[str]
+ << composition >> arguments: ProbeArguments
+ prefixes: list[str]
----
+ from_filter(installer: Any, guidance: list[str] | None): GuidanceProbe
+ matches(mcp_name: str): bool
+ instructions(): str
+ actions(): str
---<<lists the actions of>>--> ActionCatalogue
---<<names toolsets with>>--> ToolsetReference
---<<creates>>--> ProbeArguments
---<<creates>>--> ProbeSection
