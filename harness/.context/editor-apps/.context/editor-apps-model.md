---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

# Practice Content Editor Apps

**Sources / context:** `harness/.context/stories/story-map.md` (Integrate Practice Content Editor Apps In Chat Bar, lines 801-831; Integrate Practice Content Editor Apps On Board, lines 573-599, the 2026-11-12 notes); `harness/.context/stories/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/integrate_practice_content_editor_apps_in_chat_bar_story.test.md`; `harness/.context/stories/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/integrate_practice_content_editor_apps_on_board_story.test.md`; module cards `harness/.context/module-context.md`, `harness/graph/.context/module-context.md`, `harness/chat-ui/pane/.context/module-context.md`, `space/kanban/.context/module-context.md`, `harness/design_canvas/.context/module-context.md`, `cdd_guidance/practices/stories/model/.context/story-model.md`; code read: `harness/diagnostics/server_health.py`, `harness/installation/app_ports.py`, `space/kanban/board_app.py`, `harness/chat-ui/pane/hooks/board-chat/board-server.ts:40-120`, `harness/chat-ui/pane/hooks/health/server-health-wording.ts`, `harness/chat-ui/pane/hooks/chat-bar/format-choices-client.ts`, `space/kanban/format_choice.py`, `space/session/practice_session_output.py`, `harness/guidance/guidance.py:461-700`, `harness/graph/graph.py:1243-1420`, `cdd_guidance/practices/stories/model/story_model.py`, `../story-ui/packages/story-map-workspace/stories/stories.ts` (the TypeScript domain this replaces); `.sessions/integrate-practice-content-editor-apps/refactor-guardrails.md`.

**Python model files:** `harness/.context/editor-apps/*.py`, one family file per class family, each naming the module it belongs to in its first line; this document is canonical.

**Patterns:** cdd_web_domain_access (every rule below stays in Python and is reached through the generated `{Object}ClientGenerated`), lern_domain_driven (the pages that compose these clients live in the CDD Kanban app, `space/kanban/app`).

This increment adds **three new types and three named failures** and extends **thirteen existing classes**; everything else the scenarios touch is reused as it is. It does not restate the classes it extends: each section names the canonical document of the class and lists only what this increment adds, changes, or deletes there.

| Module (partition) | New | Extended | Deleted names |
|---|---|---|---|
| `harness/diagnostics` | *App*, *AppStatus*, *AppNotStarted*, *AppNotRegistered* | *ServerHealth* | `kanban_app_port`, `kanban_app_url`, `graph_app_port`, `reports_graph_app_on`, `reports_kanban_app_on` |
| `harness/guidance` | — | *PracticeGuidance*, *FidelityGuidance* | — |
| `harness/graph` | — | *Graph* | — |
| `space/session` | *FormatNotOffered* | *Session*, *FidelitySessionOutput* | `kept_format`, `keep_format` |
| `space/kanban` | — | *Board*, *Ticket*, *FidelityProgress*, *FormatChoice* | `starts_picked`; *BoardPage* and its `rebuild` (moved onto *App*) |
| `cdd_guidance/practices/stories/model` | *StoryMapEditRefused* | *StoryNode*, *StoryModel*, *Epic*, *Story*, *Scenario*, *Step* | — |

---

## harness/diagnostics: App

What an app is, how far it has got (installed, running), and how it is readied. Until this increment the chat bar worked this out in TypeScript (`board-server.ts`: `runningBoardUrl`, `openedBoard`) for the board only, and *BoardPage* rebuilt the board's page; both moved here, so the chat bar, the board and an agent ready every app the same way.

Decided while coding (implementation, 2026-11-12): *App* lives in harness/diagnostics, beside *ServerHealth*, not in harness/installation, because `open` is an `@mcp` operation and harness/installation imports no harness/mcp (harness/mcp imports it). harness/graph sits below harness/diagnostics, so the Graph app is made and registered in `harness/diagnostics/app.py` from `GRAPH_APP_PORTS`. An *App* takes its folder and its server's ports rather than an *AppPorts*: a ports file names several servers (the Graph app's `app` and `web`), and the Story UI editor's folder (`cdd_guidance/practices/stories/app`) is not the folder of the board's ports file that it answers on.

### App

<<Entity>> <<language_adapter typescript>> <<agent_toolset>>

One CDD web app a person opens beside the chat: the Story UI editor, the Graph app, or the CDD Kanban. Three instances of one class; the module that owns each app makes its instance once, keeps it, and registers it (`app.register()`), from the ports `GRAPH_APP_PORTS` and `BOARD_APP_PORTS` read: harness/diagnostics makes the Graph app, space/kanban (`board_app.py`) makes the CDD Kanban and, since the board's server serves it, the Story UI editor. *App* keeps the one registry of apps, as *PracticeCatalogue* keeps the practices; nothing else lists them.

+ App(label: str, folder: Path, server: AppServer, page: str = "/")
	// folder: where its package.json, packages and built page sit; server: what answers for it (the Story UI editor and the CDD Kanban share the board's); page: the path its page answers on, "/story-map" for the Story UI editor
------
+ label: str  <<data_field>> <<identity>>
	// "Story UI", "Graph", "Kanban": what the status row shows and what a tool call names to load it
+ status: AppStatus  <<data_field>>
	// derived: NOT_INSTALLED while its folder has no package.json, no node_modules, or, when its package has a build script, no built page (dist); DOWN while installed and none of its ports answers; RUNNING otherwise
+ port: int | None  <<data_field>>
	// derived: the first of its ports that answers; none while it is not running
+ url: str  <<data_field>>
	// derived: http://127.0.0.1:{port}{page}, on the first of its ports while it is not running
+ folder: Path
+ server: AppServer  <<data_field>> <<aggregation>>
+ registered() -> list[App]  <<classmethod>>
	// every app registered, in the order registered: Graph (harness/diagnostics is imported first), then Kanban and Story UI
----
+ register() -> App
	// registering a label again replaces the earlier app rather than listing it twice
+ load(app: str, *, project: Path) -> App  <<classmethod>> <<tool_subject>>
	// the registered app whose label the call names (the adapter's identity, as Ticket.load names a ticket); a label no module registered is refused with AppNotRegistered
+ open() -> App  <<mcp>> <<agent_tool>>
	-> self.install
	// install while NOT_INSTALLED, then answer itself with its url and its server; the chat that pressed it starts the server while it is not running ($.process.spawn in the chat bar's mod, as /board did), so the server stops when that chat ends and an app the chat did not start keeps running (decided 2026-11-12 by the person)
+ install() -> App
	-> npm install in folder, then npm run build when its package has a build script (what BoardPage.rebuild did)
	// raises AppNotStarted(self, "install", reason) when either step fails, or when its folder holds no package.json (the app is not there yet); report_progress at each step

### AppServer

<<Value Object>>

The server an app answers from: what the chat that opens the app starts, and its end stops.

+ AppServer(folder: Path, script: str, ports: tuple[int, ...])
------
+ folder: str  <<data_field>>
+ command: list[str]  <<data_field>>
	// derived: node on its script, through tsx (--import tsx) for a TypeScript one
+ port: int | None
	// derived: the first of its ports that answers

**Invariants**

- `open` answers an installed app or refuses; the chat never starts the server of an app that is not installed, and opens no side panel before one of its ports answers.
- `status` is read from the folder and the ports every time it is asked; the app keeps no copy of it.

### AppStatus

<<Value Object>> <<Enum>>

+ NOT_INSTALLED = "not installed"
+ DOWN = "not running"
+ RUNNING = "running"

### AppNotRegistered

<<Domain Exception>>

+ AppNotRegistered(label: str)  // a KeyError: the label a call named, which no module registered

### AppNotStarted

<<Domain Exception>>

+ AppNotStarted(app: App, reason: str)
------
+ app: App
+ reason: str  // the error lines of the step's output, which the status row shows with the fix: "The Story UI install failed: {reason}. Run npm install in {folder}." A server that does not come up is the chat bar's to say: "The Kanban did not start: nothing answered on port 8778. Run {command} in {folder}." 

---

## harness/diagnostics

### ServerHealth (extended)

Canonical: `harness/diagnostics/server_health.py`. It already reports the Kanban and Graph apps by port; it now holds the apps themselves, so the status row lists every registered app with its status and the chat bar presses that app.

+ << aggregation >> apps: list[App]  <<data_field>>
	-> App.registered
	// replaces kanban_app_port, kanban_app_url and graph_app_port, which are deleted with every caller (server-health-wording.ts, board-server.ts, board.py). reports_graph_app_on and reports_kanban_app_on are deleted too: an app registers itself with App.register, and the constructor's graph_ports and kanban_ports parameters go with them

---

## harness/guidance

### PracticeGuidance (extended)

Canonical: `harness/guidance/.context/practice-guidance-model.md`.

+ editor: App | None
	// the app that edits this practice's files: the Story UI editor for Stories, none for every other practice
----
+ edit_with(app: App) -> None  <<classmethod>>
	// space/kanban, which makes the Story UI editor's App, gives it to Stories (Stories.edit_with(STORY_UI_APP)), so no practice imports space
+ session_root: Path | None
	// derived: the folder the session this practice works in names for it (its PracticeSessionOutput.folder); none outside a session. work_in keeps the session output it is given so this reads it
----
+ work_in(session_output) -> None  (changed: also keeps session_output)

### FidelityGuidance (extended)

+ format: Format  (changed)
	// the first of session_output.chosen_formats, else its default; the setter calls session_output.choose_format(value, True) instead of keep_format

---

## harness/graph

### Graph (extended)

Canonical: `harness/graph/.context/module-context.md`.

+ load_practice_roots(call: ToolCall | None = None) -> GraphLoaded  <<mcp>> <<agent_tool>>
	-> practice.session_root (each practice it holds)
	-> self.build.load
	// opens each practice it holds on the root its session names, applies the session's overlays, and builds: the Graph app's whole load, with no folder or practice key passed in. A practice with no session_root is left out

**Invariants**

- A session's graph holds only the practices the session has enabled (already true of `Session.graph`), so `load_practice_roots` never reads a practice the ticket turned off.

---

## space/session

### Session (extended)

Canonical: `space/session/session.py`.

+ design_view: str  <<data_field>>
	// derived: the claude.ai link recorded for the latest version of the design canvas under an enabled practice's folder (CanvasVersions.in_practice_root(output.folder).link(latest)); empty when none is recorded

### FidelitySessionOutput (extended)

Canonical: `space/session/practice_session_output.py`. It already keeps the one format a fidelity was last given; it now keeps the formats chosen for it, which the chat bar's chips and the Story UI's toggles both change, so the two show one choice.

+ chosen_formats: list[str]  <<data_field>>
	// the formats session.json keeps for this fidelity, in the order chosen; replaces kept_format (deleted)
----
+ load(session: str, practice: str, fidelity: str, *, call) -> FidelitySessionOutput  <<classmethod>> <<tool_subject>>
+ choose_format(format: str, is_chosen: bool) -> FidelitySessionOutput  <<mcp>> <<agent_tool>>
	// replaces keep_format (deleted); a format the fidelity does not offer is refused with FormatNotOffered

### FormatNotOffered

<<Domain Exception>>

+ FormatNotOffered(fidelity: FidelityGuidance, format: str)

**Invariants**

- `chosen_formats` only ever holds formats the fidelity offers (`fidelity.outputs`), each once.

---

## space/kanban

### Board (extended)

+ last_activated: Ticket | None  <<data_field>>
	// the ticket activated last, kept in .sessions/_board.json, because activation changes no open session and cannot be read from the work; the Graph app follows it
----
+ keep_activated(ticket: Ticket) -> None

### Ticket (extended)

+ activate() -> Ticket  (changed)
	-> self.checkout.open
	-> board.keep_activated(self)
+ choose_formats(fidelities: list[str], label: str, is_chosen: bool) -> list[FormatChoice]  <<mcp>> <<agent_tool>>
	-> fidelity.session_output.choose_format (each fidelity the chip covers)
	// one call per chip press, so the chat bar and the board turn a chip on or off the same way; answers the chips again, as format_choices does

### FormatChoice (extended)

+ is_chosen: bool  <<data_field>>
	// whether every fidelity in the chip has the chip's format chosen; replaces starts_picked (deleted), so a chip shows what is kept rather than what a bar opens with

### FidelityProgress (extended)

+ editor: App | None  <<data_field>>
	// its practice's editor on the practice's first fidelity row (Stories: the story map), none on every other row: the board's small editor widget sits on that row only

### BoardPage (deleted)

Its `rebuild` is `App.install` of the CDD Kanban's *App* (`KANBAN_APP`); `scripts/install.py` calls that instead and prints an *AppNotStarted* rather than raising it.

---

## cdd_guidance/practices/stories/model

Canonical: `cdd_guidance/practices/stories/model/.context/story-model.md`. The story map's backend moves out of TypeScript: the Story UI's `StoryMapModel`, `EpicModel`, `SubEpicModel`, `StoryModel`, `ScenarioModel` and `StoryMapRepository` (`stories.ts`, `stories-server.ts`) are deleted, and the page uses the generated clients of these Python classes. No JSON story map is kept: an edit saves the map in the file it was read from and renders it to the chosen formats.

### StoryNode (extended)

+ story_map: StoryModel
	// derived: the story map at the top of its parent chain
----
+ load(file: str, node: str, *, call) -> StoryNode  <<classmethod>> <<tool_subject>>
	-> StoryModel.load
	// node is the node's dot-path id on the map; each node class (Epic, Story, Scenario, Step) has its own generated adapter through this
+ rename(name: str) -> StoryNode  <<mcp>> <<agent_tool>>
	-> self.story_map.save
+ move_before(other: StoryNode) -> StoryNode  <<mcp>> <<agent_tool>>
	-> self.story_map.save
	// refuses with StoryMapEditRefused when other is not a node of its own kind; it then takes other's parent and the order before it
+ remove() -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.story_map.save

### StoryModel (extended)

<<language_adapter typescript>> <<agent_toolset>>

+ StoryModel(source, graph, fidelity: FidelityGuidance | None = None)
	// fidelity: the story-map fidelity of the session's Stories practice; none for a map read outside a session
------
+ file: Annotated[str, SourceFile]  <<data_field>>
+ session_stories: list[Story]  <<data_field>>
	// derived: stories_named(session.stories), the stories the session the map was opened in names: the ticket's scope
+ chosen_formats: list[str]  <<data_field>>
	// derived: fidelity.session_output.chosen_formats
----
+ load(file: str, *, call) -> StoryModel  <<classmethod>> <<tool_subject>>
	-> call.session.file_manager.read(file)
	-> Stories.read_files (the session's Stories practice, from call.session.graph)
	// a file outside the session's roots is refused by FileManager (PathOutsideRootsError)
+ new_epic(name: str) -> Epic  <<mcp>> <<agent_tool>>
	-> self.append_epic
	-> self.save
+ save() -> StoryModel
	-> fidelity.practice_guidance.formats.render (its own file's format, then each of chosen_formats)
	-> self.graph.refresh (the files written; the map was read into the session's graph)
	// writes its own file first; a render that fails leaves its own file written and names the format that failed

### Epic (extended)

+ new_epic(name: str) -> Epic  <<mcp>> <<agent_tool>>
	-> self.append_epic
	-> self.story_map.save
+ new_story(name: str) -> Story  <<mcp>> <<agent_tool>>
	-> self.append_story
	-> self.story_map.save

### Story (extended)

+ new_scenario(name: str) -> Scenario  <<mcp>> <<agent_tool>>
	-> self.story_map.save

### Scenario (extended)

+ new_step(step_type: StepType, text: str) -> Step  <<mcp>> <<agent_tool>>
	-> self.story_map.save

### Step (extended)

+ edit_text(text: str) -> Step  <<mcp>> <<agent_tool>>
	-> self.story_map.save

### StoryMapEditRefused

<<Domain Exception>>

+ StoryMapEditRefused(node: StoryNode, operation: str, reason: str)

**Invariants**

- Every edit operation saves through its story map before it answers, so the file, the rendered formats and the graph never lag behind the answer the page shows.
- A story map opened in a session writes only under the session's roots.

---

## Interactions across modules

| Caller | Operation | Owner |
|---|---|---|
| chat bar status row press | `App.open` | harness/installation |
| chat bar file viewer tile | `StoryModel.load(file)` | stories model |
| chat bar file viewer link | `Session.design_view` | space/session |
| Story UI edit | `StoryNode.rename` and the other edits, then `StoryModel.save` | stories model |
| Story UI format toggle, chat bar chip | `FidelitySessionOutput.choose_format`, `Ticket.choose_formats` | space/session, space/kanban |
| Graph app open | `Graph.load_practice_roots` on `Board.last_activated.session.graph` | harness/graph, space/kanban |
| board story-map row widget | `FidelityProgress.editor` then `App.open` and `StoryModel.load` | space/kanban, harness/installation |
| board graph widget | `Graph.load_practice_roots` on the ticket's session graph | harness/graph |
