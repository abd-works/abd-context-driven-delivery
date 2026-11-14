---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

# Practice Content Editor Apps

**Sources / context:** `harness/.context/stories/story-map.md` (Integrate Practice Content Editor Apps In Chat Bar, lines 801-831; Integrate Practice Content Editor Apps On Board, lines 573-599, the 2026-11-12 notes); `harness/.context/stories/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/integrate_practice_content_editor_apps_in_chat_bar_story.test.md`; `harness/.context/stories/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/integrate_practice_content_editor_apps_on_board_story.test.md`; module cards `harness/.context/module-context.md`, `harness/graph/.context/module-context.md`, `harness/chat-ui/pane/.context/module-context.md`, `space/kanban/.context/module-context.md`, `harness/design_canvas/.context/module-context.md`, `cdd_guidance/practices/stories/model/.context/story-model.md`; code read: `harness/diagnostics/server_health.py`, `harness/installation/app_ports.py`, `space/kanban/board_app.py`, `harness/chat-ui/pane/hooks/board-chat/board-server.ts:40-120`, `harness/chat-ui/pane/hooks/health/server-health-wording.ts`, `harness/chat-ui/pane/hooks/chat-bar/format-choices-client.ts`, `space/kanban/format_choice.py`, `space/session/practice_session_output.py`, `harness/guidance/guidance.py:461-700`, `harness/graph/graph.py:1243-1420`, `cdd_guidance/practices/stories/model/story_model.py`, `../story-ui/packages/story-map-workspace/stories/stories.ts` (the TypeScript domain this replaces); `.sessions/integrate-practice-content-editor-apps/refactor-guardrails.md`.

**Python model files:** `harness/.context/editor-apps/*.py`, one family file per class family, each naming the module it belongs to in its first line; this document is canonical.

**Patterns:** cdd_web_domain_access (every rule below stays in Python and is reached through the generated `{Object}ClientGenerated`), lern_domain_driven (the pages that compose these clients live in their app folders: the Story UI editor in `cdd_guidance/practices/stories/app`, beside the Stories practice whose model it edits, as the Graph app lives in `harness/graph/app`; the board's server serves it at `/story-map`).

This increment adds **three new types and three named failures** and extends **thirteen existing classes**; everything else the scenarios touch is reused as it is. It does not restate the classes it extends: each section names the canonical document of the class and lists only what this increment adds, changes, or deletes there.

| Module (partition) | New | Extended | Deleted names |
|---|---|---|---|
| `harness/diagnostics` | *App*, *AppStatus*, *AppNotStarted*, *AppNotRegistered* | *ServerHealth* | `kanban_app_port`, `kanban_app_url`, `graph_app_port`, `reports_graph_app_on`, `reports_kanban_app_on` |
| `harness/guidance` | — | *PracticeGuidance*, *FidelityGuidance* | — |
| `harness/graph` | — | *Graph* | — |
| `space/session` | *FormatNotOffered* | *Session*, *FidelitySessionOutput* | `kept_format`, `keep_format` |
| `space/kanban` | — | *Ticket*, *FidelityProgress*, *FormatChoice* | `starts_picked`; *BoardPage* and its `rebuild` (moved onto *App*) |
| `cdd_guidance/practices/stories/model` | *OpenedStoryMap*, *StoryMapEditRefused*, *StoryNodeNotFound* | *StoryNode*, *StoryModel*, *Epic*, *Story*, *Scenario*, *Step* | — |
| `cdd_guidance/practices/stories/app` | the Story UI editor's page: *StoryMapClient*, *StoryMapApi*, its views | — | the Story UI's TypeScript domain (`stories.ts`, `stories-server.ts`, the JSON and MongoDB stores) |

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

+ editor: App | None  <<class field>>
	// the app that edits this practice's files: the Story UI editor for Stories, none for every other practice; space/kanban, which makes the Story UI editor's App, sets it on Stories (Stories.editor = STORY_UI_APP), so no practice imports space
+ session_root: Path | None
	// derived: the folder the session this practice works in names for it (its PracticeSessionOutput.folder); none outside a session. work_in keeps the session output it is given so this reads it
----
+ work_in(session_output) -> None  (changed: also keeps session_output)

### FidelityGuidance (extended)

+ format: Format  (changed)
	// the format it was last given while that is still chosen in the session, else the first chosen there, else its default; a format the fidelity does not write is worked in while held
	-> session_output.chosen_formats
+ offers(format: str) -> bool
	// whether one of its outputs names format
+ format = value  (changed)
	-> session_output.choose_format(value, True)  (a format it writes only; keep_format is deleted)

---

## harness/graph

### Graph (extended)

Canonical: `harness/graph/.context/module-context.md`.

+ load_practice_roots(call: ToolCall | None = None) -> GraphLoaded  <<mcp>> <<agent_tool>>
	-> practice.session_root (each practice it holds)
	-> self.build.load
	// opens each practice it holds on the root its session names, applies the session's overlays, and builds: the Graph app's whole load, with no folder or practice key passed in. A practice with no session_root, or whose root folder is not written yet, is left out

**Invariants**

- A session's graph holds only the practices the session has enabled (already true of `Session.graph`), so `load_practice_roots` never reads a practice the ticket turned off.

Decided while coding (implementation, 2026-11-12): no *Board* field records the ticket activated last (grill answer). The Graph app names its project as the board does (`?project=`, the `X-CDD-Project` header, one cdd connection per project in its server), so each of its calls works in the session open in that project (`ToolCall.session`, `Graph.for_call`): the same *Session* object, and so the same graph, as the board's active ticket (`Board.active`), read again on every call, with nothing pushed. A ticket's graph widget opens the app on the ticket's worktree, where the ticket's session is the open one; the board header opens it on the board's project. DDD builds its building blocks from Clean Engineering only when the graph holds Clean Engineering (`DddReading._clean_engineering`), so a session with DDD on and Clean Engineering off loads.

---

## space/session

### Session (extended)

Canonical: `space/session/session.py`.

Decided while coding (implementation, 2026-11-12): *Session* gains nothing. The design view moved to *PracticeSessionOutput.design_view* (below): Session is the class with the most methods in the repository, and the metrics gate refuses a change that grows it.

### PracticeSessionOutput (extended)

+ design_view: str  <<data_field>>
	-> CanvasVersions.in_practice_root(self.output_root).link(latest)
	// the claude.ai link recorded for the latest version of the design canvas under the folder this practice writes under (the UX practice's); empty while the practice is off or none is recorded. The chat bar's file viewer opens the first practice's that has one

### FidelitySessionOutput (extended)

<<language_adapter typescript>> <<agent_toolset>> <<identity session_file, practice_name, name>>

Canonical: `space/session/practice_session_output.py`. It kept the one format a fidelity was last given; it now keeps the formats chosen for it, which the chat bar's chips, the board's chips and the Story UI's toggles all change, so every page shows one choice.

+ session_file: str  <<data_field>>
+ practice_name: str  <<data_field>>
+ name: str  <<data_field>>
	// the fidelity's name, such as story_map
+ offered_formats: list[str]  <<data_field>>
	// the formats the fidelity writes (`fidelity.outputs`): what a person can choose
+ chosen_formats: list[str]  <<data_field>>
	// the formats session.json keeps for this fidelity, in the order chosen; the fidelity's default until one is chosen. Replaces kept_format (deleted); a session saved with one kept format reads it as that one
----
+ load(session: str, practice: str, fidelity: str, *, call) -> FidelitySessionOutput  <<classmethod>> <<tool_subject>>
+ choose_format(format: str, is_chosen: bool) -> FidelitySessionOutput  <<mcp>> <<agent_tool>>
	// replaces keep_format (deleted); a format chosen again keeps its place; a format the fidelity does not offer is refused with FormatNotOffered

### FormatNotOffered

<<Domain Exception>>

+ FormatNotOffered(fidelity: FidelityGuidance, format: str)

**Invariants**

- `chosen_formats` only ever holds formats the fidelity offers (`fidelity.outputs`), each once.

---

## space/kanban

### Ticket (extended)

+ choose_formats(fidelities: list[str], label: str, is_chosen: bool) -> list[FormatChoice]  <<mcp>> <<agent_tool>>
	-> fidelity.session_output.choose_format (each fidelity the chip covers)
	-> FormatChoice.choose (the chip labelled label)
	// one call per chip press, so the chat bar and the board turn a chip on or off the same way; answers the chips again, as format_choices does

### FormatChoice (extended)

+ is_chosen: bool  <<data_field>>
	// whether every fidelity in the chip has the chip's format chosen; replaces starts_picked (deleted), so a chip shows what is kept rather than what a bar opens with
----
+ choose(is_chosen: bool) -> None
	-> fidelity.session_output.choose_format (each fidelity the chip covers, with the format it uses from the group)

### BoardFidelity (extended)

+ editor: App | None  <<data_field>>
	// its practice's editor on the practice's first fidelity (Stories: the story map), none on every other fidelity: the board's small editor widget sits on that row of every ticket only

### BoardPractice (extended)

+ editor: App | None  <<data_field>>
	-> practice.editor
	// the app that edits the practice's files, on every practice the board overview sends: the chat bar's file viewer shows the Story UI editor tile on every file of a fidelity whose practice has one (the person's decision: every Stories file)

Decided while coding (implementation, 2026-11-12): the chat bar's file viewer shows a tile on every Stories file, not only the story map's, so it reads the editor from the practice the board overview sends (*BoardPractice.editor*), not from the row's own editor. The row's editor, first named *FidelityProgress.editor*, is *BoardFidelity.editor*: it is the same for every ticket, so the board sends it once with the fidelity rather than with each ticket's progress, and *FidelityProgress* stays under the metrics gate's limit of classes it depends on. *PracticeGuidance.editor* is a class field that space/kanban sets (`Stories.editor = STORY_UI_APP`), since every session makes its own practice instances and all of them edit with the same app; the `edit_with` classmethod the model first named was dropped (prefer-instance-operations).

### BoardPage (deleted)

Its `rebuild` is `App.install` of the CDD Kanban's *App* (`KANBAN_APP`); `scripts/install.py` calls that instead and prints an *AppNotStarted* rather than raising it.

---

## cdd_guidance/practices/stories/model

Canonical: `cdd_guidance/practices/stories/model/story_model.py`, `opened_story_map.py`; spec `story_map_edits_spec.py`. The story map's backend moves out of TypeScript: the Story UI's `StoryMapModel`, `EpicModel`, `SubEpicModel`, `StoryModel`, `ScenarioModel` and `StoryMapRepository` (`stories.ts`, `stories-server.ts`) are not carried into `cdd_guidance/practices/stories/app`, and the page uses the generated clients of these Python classes. No JSON story map is kept: an edit saves the map in the file it was read from and renders it to the chosen formats.

Every edit answers the **story map**, not the node it changed (`standard-mutation-response`): the page redraws the whole map as its file now holds it.

### StoryNode (extended)

<<hosted_only>> <<identity node>>: each concrete kind below is a toolset of its own, with its own generated adapter.

+ address: str  <<data_field key="node">>
	// `{file}#{path}`: the file its map was opened from, and the slugs from its top epic down (`checkout.pay.pay-by-card`), a step by its place (`step-2`)
+ shown_name: str  <<data_field key="name">>
+ description_text: str  <<data_field key="description">>
	// what the story map says about it: the paragraphs under its heading in an outline story map (the story map's own: the lines above its first epic; an increment's: its outcome and slicing notes in the thin slice); written back unchanged (decided 2026-11-12 by the person)
+ story_map: StoryModel
	// derived: the story map at the top of its parent chain
+ parts: list[StoryNode]
	// the nodes a path goes through below it
+ segment: str
+ path: str
----
+ load(node: str, *, call) -> StoryNode  <<classmethod>> <<tool_subject>>
	-> StoryModel.load (the file the node names)
	-> StoryModel.node_at
	// a node of another kind than the toolset's is refused with StoryNodeNotFound
+ holding(part: StoryNode) -> list[StoryNode]
	// the list of its own that holds part; each kind answers its own
+ rename(name: str) -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.story_map.write_back
+ move_before(other: StoryNode) -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.story_map.node_at(other.path)
	-> self.story_map.write_back
	// refuses with StoryMapEditRefused when other is not a node of its own kind; it then takes other's parent and the place before it
+ remove() -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.story_map.write_back
+ edit_description(description: str) -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.story_map.write_back

### StoryModel (extended)

<<language_adapter typescript>> <<agent_toolset>> <<identity file>>

+ file: Annotated[str, SourceFile]  <<data_field>>
+ formats: FidelitySessionOutput  <<data_field>>
	// what the fidelity declaring its file keeps in the session: offered_formats and chosen_formats, which the Story UI's toggles change
+ refusal: str  <<data_field>>
	// why an edit is not saved, such as an acceptance-test file opened to be read, or a file that would not read back as its format writes the map; empty when edits are saved
+ epics: list[Epic]  <<data_field>>
+ increments: list[Increment]  <<data_field>>
	// in order, read from the thin slice beside a markdown story map (its slicing)
+ scope: list[str]  <<data_field>>
	// the addresses of its stories the session it was opened in names (OpenedStoryMap.session_stories, stories_named): the part of the map the ticket covers, which the Story UI shows; none when the session names none (decided 2026-11-12: the model owns the ticket's scope, not a page query)
+ slicing: ThinSlice | None
	// the file that keeps its increments and writes them on a save; none for a map that keeps none, such as a scenario file
----
+ load(file: str, *, call) -> StoryModel  <<classmethod>> <<tool_subject>>
	-> call.session.session_files.file_manager.read (refuses a file outside the session's roots with PathOutsideRootsError)
	-> call.session.graph.practices.of(Stories).open_file
	// a markdown story map or scenario file is read by itself (MarkdownStoryModel.opened_from), with the thin slice beside a story map, so a save keeps every line it does not change; a story test is merged onto its story map to be read
	-> OpenedStoryMap(the map read, the file, the session), which the map keeps
+ open_in_session(*, call) -> StoryModel  <<classmethod>> <<mcp>> <<agent_tool>>
	// the first story map file the open session's Stories practice declares: the page with no file follows the session open in the project, so a ticket activated on the board shows its own map on the next read
+ show() -> StoryModel  <<mcp>> <<agent_tool>>
+ new_epic(name: str) -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.write_back
+ node_at(path: str) -> StoryNode
+ new_increment(name: str) -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.write_back
	// refuses with StoryMapEditRefused when it keeps no increments (no slicing)
+ acceptance_tests_of(story: Story) -> list[str]
	-> OpenedStoryMap.acceptance_tests_of
+ write_back() -> StoryModel
	// was save(): a markdown, drawio or code map is itself the opened map now, and those formats' save answers their text
	-> OpenedStoryMap.write
	// refuses with StoryMapEditRefused, writing nothing, while refusal says why

### Story (extended)

+ acceptance_tests: list[str]  <<data_field>>
	// the session's story tests that hold it, as paths from the project: shown as links, never edited (decided 2026-11-12 by the person); a link opens the file in the chat bar's file viewer of the chat the Story UI editor was opened beside (Chat.send open_file), not in the Story UI (decided 2026-11-12, implementation)
	-> self.story_map.acceptance_tests_of

### Scenario (extended)

+ example_rows: list[Example]  <<data_field key="examples">>
	// its examples, a row each, in the order its table gives them: the Story UI edits each through the example's own tools
+ parts: list[StoryNode]
	// its steps, then its examples, so a path reaches an example (`{scenario}.example:{slug}`) and a save checks the examples read back
+ holding(part) -> list[StoryNode]
	// refuses an Example with StoryMapEditRefused: an example keeps the place its table gives it

### Example (extended)

<<language_adapter typescript>> <<agent_toolset>>: one row of a scenario's examples table, edited through the story map like every other node (decided 2026-11-12, implementation: the Story UI's example rows edit through the model, not a copy of it).

+ row: dict[str, str]  <<data_field key="fields">>
	// its row of its table: its name under `example`, then its fields, each as text
+ segment_prefix = "example:"
+ naming_columns = ("example", "name")
----
+ edit_field(field: str, value: str) -> StoryModel  <<mcp>> <<agent_tool>>
	// the column that names it (`example`, or `name` while it says its name) renames it; a column its row does not have is refused with StoryMapEditRefused
	-> self.story_map.write_back
+ rename(name: str) -> StoryModel  <<mcp>> <<agent_tool>>
	// renames the column of its row that names it too, and keeps its place in its scope's Examples
	-> Examples.rename
	-> self.story_map.write_back
+ remove() -> StoryModel  <<mcp>> <<agent_tool>>  (from StoryNode; it leaves its scope's Examples, Examples.drop)
+ move_before(other) -> StoryModel  <<mcp>> <<agent_tool>>  (from StoryNode; refused by Scenario.holding)
+ edit_description(description) -> StoryModel
	// refused, and no tool offers it: a row holds no description

### MarkdownExample (new, cdd_guidance/practices/stories/model/markdown/markup.py)

An example read from a row of a markdown examples table (*ScenarioFileReading* makes one per row and keeps it where the row stood). It keeps the row's line and the table's headers, so an unchanged example is written back as read, an edited one changes only the cells the edit changed, and one taken off its scope writes no line.

+ line() -> str

### Increment (extended)

<<language_adapter typescript>> <<agent_toolset>>

+ delivered: list[str]  <<data_field key="stories">>
	// the addresses of the stories it delivers
+ segment_prefix = "increment:"
	// its path is `increment:{slug}`, apart from any epic's
----
+ add_story(story: Story) -> StoryModel  <<mcp>> <<agent_tool>>
	// a story is delivered by one increment at most: it leaves the increment that held it
	-> self.story_map.write_back
+ remove_story(story: Story) -> StoryModel  <<mcp>> <<agent_tool>>
	-> self.story_map.write_back
// rename, move_before, remove and edit_description come from StoryNode

### ThinSlice (new, cdd_guidance/practices/stories/model/markdown/thin_slice.py)

The thin slice a markdown story map keeps its increments in (`thin-slice.md` beside it), with the lines it was read with, so a save writes back every line an edit does not touch. `MarkdownIncrement` keeps each increment's lines (`IncrementLines`).

+ text(increments) -> str
+ write(increments) -> list[Path]
	// writes only when the text changed

### OpenedStoryMap (new)

The file a story map was opened from in a session, and the one owner of its writes.

+ OpenedStoryMap(story_map: StoryModel, path: Path, session: Session)
	// the session's own Stories practice (session.graph.practices.of(Stories)) reads and writes the file
	// it keeps the map as its own format writes it on opening, which a save compares the file with
------
+ file: str
+ fidelity: FidelityGuidance
	// derived: the fidelity of the session's Stories practice that declares the file
+ own_format: Format
+ refusal: str
	// empty while the file reads back exactly as its format writes the map; otherwise why a save would change it beyond the edit
----
+ write() -> list[Path]
	-> Stories.formats.render (its own format, then each of fidelity.session_output.chosen_formats, beside the file with that format's extension)
	-> session.graph.refresh (the files written)
	// an edit its own format would not read back, such as a scenario on a story map, is refused before anything is written

### Epic (extended)

+ epics, stories  <<data_field>>
+ new_epic(name: str) -> StoryModel  <<mcp>> <<agent_tool>>
+ new_story(name: str) -> StoryModel  <<mcp>> <<agent_tool>>

### Story (extended)

+ scenarios  <<data_field>>; kind: str  <<data_field key="story_type">>
+ new_scenario(name: str) -> StoryModel  <<mcp>> <<agent_tool>>

### Scenario (extended)

+ steps  <<data_field>>
+ new_step(step_type: str, text: str) -> StoryModel  <<mcp>> <<agent_tool>>
	// step_type is given, when or then (StepType)

### Step (extended)

+ keyword, ands  <<data_field>>; written_text: str  <<data_field key="text">>
+ edit_text(text: str) -> StoryModel  <<mcp>> <<agent_tool>>

### StoryMapEditRefused, StoryNodeNotFound

<<Domain Exception>>

+ StoryMapEditRefused(node: StoryNode, operation: str, reason: str)
+ StoryNodeNotFound(node: str, kind: type)  // a LookupError

**Invariants**

- Every edit operation saves through its story map before it answers, so the file, the rendered formats and the graph never lag behind the answer the page shows.
- A story map opened in a session writes only its own file and the formats chosen beside it, under the session's roots.
- A save never changes its file beyond the edit: a file not laid out as its format writes the map, or an edit its format would not read back, is refused and nothing is written.

---

## cdd_guidance/practices/stories/app

The Story UI editor, moved from its own repository (`C:/dev/story-ui`) beside the Stories practice. It keeps no domain, no store and no routes of its own:

- `story-map/story-map-client.ts` — *StoryMapClient* extends the generated `StoryModelClientGenerated` with what only the page knows: which node client an id the views hand back takes, and how a drag the views report as a new order becomes one `move_before`.
- `story-map/story-map-api.ts` — *StoryMapApi*, the page's `CddApi` over the board's server; a failed call says what failed and how to fix it, answers null, and the page keeps the map Python last sent (`fail-loud-on-mcp`).
- `story-map/story-map-view-models.ts`, `story-map/story-map-views.tsx` — the Story UI's views, drawing the generated data.
- `story-map-routes.ts` — `storyMapRoutes` (the generated routes of StoryModel, Epic, Story, Scenario, Step, Example, Increment, FidelitySessionOutput and Chat) and `storyMapBuild` (the built page), which the board's server mounts; `story-map-page.ts` — the page's path, `/story-map`.

## Interactions across modules

| Caller | Operation | Owner |
|---|---|---|
| chat bar status row press | `App.open` | harness/installation |
| chat bar file viewer tile | `StoryModel.load(file)` | stories model |
| chat bar file viewer link | `PracticeSessionOutput.design_view` | space/session |
| Story UI edit | `StoryNode.rename` and the other edits, then `StoryModel.write_back` | stories model |
| Story UI increment view | `StoryModel.new_increment`, `Increment.add_story`, `Increment.remove_story` | stories model |
| Story UI acceptance-test link | `Chat.send(open_file)`, then the chat bar's files pane shows it at the chat's next check-in (`FileManager.read` through `session.read_file`) | harness/chat, harness/chat-ui |
| Story UI example cell | `Example.edit_field`, `Example.remove`, then `StoryModel.write_back` | stories model |
| Story UI epic or sub-epic description | `Epic.edit_description`, then `StoryModel.write_back` | stories model |
| Story UI with no file | `StoryModel.open_in_session`, read every two seconds | stories model |
| Story UI format toggle, chat bar chip | `FidelitySessionOutput.choose_format`, `Ticket.choose_formats` | space/session, space/kanban |
| Graph app open | `Graph.load_practice_roots` on the session open in the project (the chat's open session) | harness/graph, space/session |
| board story-map row widget | `BoardFidelity.editor` then `App.open`, opened on the ticket's worktree, where `StoryModel.open_in_session` shows the ticket's story map | space/kanban, harness/diagnostics |
| board graph widget | `Graph.load_practice_roots` on the ticket's session graph | harness/graph |
