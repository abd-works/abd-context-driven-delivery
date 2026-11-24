# harness/apps

The CDD web apps a person opens beside the chat: each module that owns an app makes it once and registers it with *App*, the one registry, and `app.open` installs and readies it.

- **Purpose:** Give every module that owns a web app one way to register it, install it, and say where it answers, apart from the module that diagnoses installs.
- **Seam (terms):** App, Apps (`APPS`), AppPackage, AppPage, AppServer, NodeScript, Npm, AppSources, PortProbe, AppStatus, AppNotStarted, AppNotRegistered, PackageNotInstalled; the MCP operations `app.open` and `app.install`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp, harness/process

## App

One CDD web app a person opens beside the chat (Kanban, Graph, Story UI), and the one registry of them. The module that owns each app makes it once and registers it: the Graph app in harness/graph, from `GRAPH_APP_PORTS`; the CDD Kanban and the Story UI editor in space/kanban; the Files app in harness/files_app.

+ App(label: str, package: AppPackage, page: AppPage)
------
+ label: str
+ package: AppPackage
+ status: AppStatus
+ port: int | None
+ url: str
+ server: AppServer
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

## AppPackage

The npm package an app installs from, which installs itself: its folder, `package.json`, the sources its install reads, and npm. It keeps the fingerprint of what each install read beside what that install wrote, so an install with nothing changed takes no npm.

+ AppPackage(folder: Path, imports: tuple[Path, ...] = (), npm: Npm | None = None)
------
+ is_installed: bool
+ is_current: bool
----
+ install(label: str): None
---<<raises>>--> PackageNotInstalled
