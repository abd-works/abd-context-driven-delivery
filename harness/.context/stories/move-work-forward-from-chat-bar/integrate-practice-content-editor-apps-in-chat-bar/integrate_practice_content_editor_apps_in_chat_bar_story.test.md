---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Integrate Practice Content Editor Apps In Chat Bar

### Domain terms

Each term links to its class in the model, [editor-apps-model.md](../../../editor-apps/.context/editor-apps-model.md).

- ++app status row++ — the strip of the server health panel under the chat bar's health mark: MCP host, Tools, then each [app](../../../editor-apps/.context/editor-apps-model.md#app) the server health reports ([ServerHealth.apps](../../../editor-apps/.context/editor-apps-model.md#serverhealth-extended)), then the Hook server.
- ++app++ — one CDD web app a person opens beside the chat: the Story UI editor, the Graph app or the CDD Kanban ([App](../../../editor-apps/.context/editor-apps-model.md#app)).
- ++app status++ — not installed, not running or running ([AppStatus](../../../editor-apps/.context/editor-apps-model.md#appstatus)).
- ++side panel++ — the pane beside the chat an app opens in, at the app's url.
- ++file viewer++ — the chat bar's files pane: one tab per file a fidelity declares.
- ++story map++ — a Stories file read as epics, sub-epics, stories and scenarios ([StoryModel](../../../editor-apps/.context/editor-apps-model.md#storymodel-extended)).
- ++chosen formats++ — the formats kept for a fidelity in the session, which the chat bar's chips and the Story UI's toggles both change ([FidelitySessionOutput.chosen_formats](../../../editor-apps/.context/editor-apps-model.md#fidelitysessionoutput-extended)).
- ++design view++ — the Claude Design link recorded for the latest version of the session's design canvas ([PracticeSessionOutput.design_view](../../../editor-apps/.context/editor-apps-model.md#practicesessionoutput-extended)).
- ++practice root++ — the folder a session names for one of its enabled practices ([PracticeGuidance.session_root](../../../editor-apps/.context/editor-apps-model.md#practiceguidance-extended)).
- ++violation++ — a rule a node in the latest graph breaks, with its file and the lines it covers.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### apps ([App](../../../editor-apps/.context/editor-apps-model.md#app))

| app | status row label | ports | page |
| --- | --- | --- | --- |
| ++Story UI editor++ | Story UI | 8778 (the board's server) | /story-map |
| ++Graph app++ | Graph | 5173, 5174, 5175, 5176 | / |
| ++CDD Kanban++ | Kanban | 8778 | / |

### app statuses ([AppStatus](../../../editor-apps/.context/editor-apps-model.md#appstatus))

| app status | the status row reads | a press on the app |
| --- | --- | --- |
| ++not installed++ | not installed | installs it, launches it, opens it in the side panel |
| ++not running++ | not running | launches it, opens it in the side panel |
| ++running++ | running :{port} | opens it in the side panel |

### sessions ([Session](../../../editor-apps/.context/editor-apps-model.md#session-extended), [PracticeGuidance.session_root](../../../editor-apps/.context/editor-apps-model.md#practiceguidance-extended))

| session | practices enabled | practice roots | stories it names |
| --- | --- | --- | --- |
| ++checkout-flow++ | Stories, UX, Clean Engineering | harness/.context/stories, harness/.context/ux, harness/.context | Open Story UI Side Panel From Chat Bar, Open Kanban Side Panel From Chat Bar |
| ++billing-report++ | Stories, DDD | billing/.context/stories, billing/.context | Report Billing By Month |

### files ([PracticeGuidance.editor](../../../editor-apps/.context/editor-apps-model.md#practiceguidance-extended), [StoryModel](../../../editor-apps/.context/editor-apps-model.md#storymodel-extended))

| file | practice | fidelity | editor tile |
| --- | --- | --- | --- |
| ++story-map.md++ | Stories | story map | Story UI editor |
| ++story-map.drawio++ | Stories | story map | Story UI editor |
| ++chat bar scenarios++ (`move-work-forward-from-chat-bar/.../integrate_practice_content_editor_apps_in_chat_bar_story.test.md`) | Stories | scenarios | Story UI editor |
| ++canvas.json++ (`harness/.context/ux/canvas.json`) | UX | mockup | none |
| ++this repository's story map++ (`harness/.context/stories/story-map.md`, laid out by hand) | Stories | story map | Story UI editor |
| ++this repository's thin slice++ (`harness/.context/stories/thin-slice.md`) | Stories | story map | none: its increments are edited on the story map |

### chosen formats ([FidelitySessionOutput.chosen_formats](../../../editor-apps/.context/editor-apps-model.md#fidelitysessionoutput-extended))

| fidelity | chosen formats | files a save writes |
| --- | --- | --- |
| ++story map, markdown and drawio++ | markdown, drawio | story-map.md, story-map.drawio |
| ++story map, markdown only++ | markdown | story-map.md |

### design views ([PracticeSessionOutput.design_view](../../../editor-apps/.context/editor-apps-model.md#practicesessionoutput-extended))

| session | design canvas version | design view |
| --- | --- | --- |
| ++checkout-flow design++ | version-2 under harness/.context/ux/design-canvas | https://claude.ai/design/checkout-flow-v2 |
| ++billing-report design++ | none: UX is not enabled | none |

### violations

| violation | rule | file | lines | story |
| --- | --- | --- | --- | --- |
| ++Ticket Archive name++ | verb-noun-format | harness/.context/stories/story-map.md | 86 to 88 | Ticket Archive |
| ++Move Ticket size++ | right-size-story-nodes | harness/.context/stories/story-map.md | 148 to 150 | Move Ticket |

## Story: Open Story UI Side Panel From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:803-805` | Requested (2026-11-12): the app status row lists the Story UI editor with its status; a press installs, launches and opens it in the side panel; the file viewer shows a story-map editor tile for every Stories file |
| `harness/chat-ui/pane/hooks/health/server-health-wording.ts:19-28` | Observed: the row lists MCP host, Tools, Kanban app, Graph app and Hook server today |
| `harness/chat-ui/pane/hooks/board-chat/board-server.ts:40-120` | Observed: the chat bar starts the board only, in TypeScript; this moves to *App.open* |
| `harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx:55-75` | Observed: the file viewer's tabs, and the "Open in draw.io" button a diagram tab already has, which the editor tile sits beside |

#### Scenario Outline: A press on the Story UI editor readies it by its status and opens it beside the chat

*Given* ++checkout-flow++ is the session the chat works in  
  *And* the app status row reads Story UI ${status row reads}  
*When* the Person opens the ++Story UI editor++ from the app status row  
*Then* the Story UI editor ${a press does}  
  *And* the side panel shows ++checkout-flow++'s story map at http://127.0.0.1:8778/story-map  
  *And* the app status row reads Story UI running :8778

##### Examples

| app status | status row reads | a press does |
| --- | --- | --- |
| not installed | not installed | is installed, launched and opened in the side panel |
| not running | not running | is launched and opened in the side panel |
| running | running :8778 | is opened in the side panel |

#### Scenario: An install that fails says what failed and how to fix it

*Given* the app status row reads Story UI not installed  
  *But* npm install fails in the Story UI editor's folder with `npm ERR! code ENOENT`  
*When* the Person opens the ++Story UI editor++ from the app status row  
*Then* the side panel stays closed  
  *And* the server health panel says the Story UI install failed, with `npm ERR! code ENOENT`  
  *And* it says to run npm install in the Story UI editor's folder  
  *And* the app status row still reads Story UI not installed

#### Scenario Outline: A Stories file's editor tile opens that file in the Story UI editor

*Given* ++checkout-flow++'s file viewer shows ++${file}++  
  *And* the Story UI editor is running  
*When* the Person opens ++${file}++ from its story-map editor tile  
*Then* the side panel shows the Story UI editor on ++${file}++  
  *And* it shows ${what it shows}

##### Examples

| file | what it shows |
| --- | --- |
| story-map.md | the epics, sub-epics and stories story-map.md holds |
| story-map.drawio | the epics, sub-epics and stories story-map.drawio holds |
| chat bar scenarios | the stories of Integrate Practice Content Editor Apps In Chat Bar with their scenarios |

#### Scenario: A file of another practice has no story-map editor tile

*Given* ++checkout-flow++'s file viewer shows ++canvas.json++, a UX file  
*When* the Person looks at ++canvas.json++ in the file viewer  
*Then* the file viewer shows no story-map editor tile for ++canvas.json++

## Story: Open Knowledge Graph Side Panel From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:807-809` | Requested (2026-11-12, "same but for KG"): the status row lists the Graph app; a press installs, launches and opens it; the graph loads the folders the session's practice roots name and follows the session open in the project |
| `harness/graph/app/ports.json` | the Graph app's ports, 5173 to 5176 |
| `space/session/sessions.py:268-313` | Observed: a call that names no chat, as the Graph app's do, works in the session open in its project: the ticket of the worktree it names, else the project's own open session, the one the board shows as active. Decided (2026-11-12): no field records the session activated last ([Graph](../../../editor-apps/.context/editor-apps-model.md#graph-extended)) |

#### Scenario Outline: A press on the Graph app readies it by its status and opens it beside the chat

*Given* ++checkout-flow++ is the session open in the project  
  *And* the app status row reads Graph ${status row reads}  
*When* the Person opens the ++Graph app++ from the app status row  
*Then* the Graph app ${a press does}  
  *And* the side panel shows the knowledge graph at http://127.0.0.1:5173/  
  *And* the app status row reads Graph running :5173

##### Examples

| app status | status row reads | a press does |
| --- | --- | --- |
| not installed | not installed | is installed, launched and opened in the side panel |
| not running | not running | is launched and opened in the side panel |
| running | running :5173 | is opened in the side panel |

#### Scenario: The graph loads the folders the session's practice roots name

*Given* ++checkout-flow++ is the session open in the project  
  *And* its practice roots are harness/.context/stories, harness/.context/ux and harness/.context  
*When* the Person opens the ++Graph app++ from the app status row  
*Then* the knowledge graph shows the Stories tree read from harness/.context/stories  
  *And* it shows the UX tree read from harness/.context/ux  
  *And* it shows the Clean Engineering tree read from harness/.context  
  *And* it shows no folder of ++billing-report++

#### Scenario: The open graph follows the session open in the project

*Given* the knowledge graph is open in the side panel on ++checkout-flow++'s practice roots  
*When* ++billing-report++'s session is opened in the project  
*Then* the knowledge graph shows the Stories tree read from billing/.context/stories  
  *And* it shows the DDD tree read from billing/.context  
  *And* it shows no folder of ++checkout-flow++

## Story: Open Kanban Side Panel From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:811-813` | Requested (2026-11-12): the status row lists the CDD Kanban with its status; a press installs, launches and opens it in the side panel |
| `space/kanban/app/packages/session-board/ports.json` | the board's port, 8778 |

#### Scenario Outline: A press on the CDD Kanban readies it by its status and opens it beside the chat

*Given* ++checkout-flow++ is the session the chat works in  
  *And* the app status row reads Kanban ${status row reads}  
*When* the Person opens the ++CDD Kanban++ from the app status row  
*Then* the CDD Kanban ${a press does}  
  *And* the side panel shows the board at http://127.0.0.1:8778/ with ++checkout-flow++'s ticket outlined  
  *And* the app status row reads Kanban running :8778

##### Examples

| app status | status row reads | a press does |
| --- | --- | --- |
| not installed | not installed | is installed, launched and opened in the side panel |
| not running | not running | is launched and opened in the side panel |
| running | running :8778 | is opened in the side panel |

#### Scenario: A board that does not come up says so instead of opening an empty panel

*Given* the app status row reads Kanban not running  
  *But* nothing answers on port 8778 within the wait after the launch  
*When* the Person opens the ++CDD Kanban++ from the app status row  
*Then* the side panel stays closed  
  *And* the server health panel says the Kanban did not start: nothing answered on port 8778  
  *And* the app status row still reads Kanban not running

## Story: Invoke Claude Design Story Explorer From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:815-817` | Requested (2026-11-12, for now): the file viewer has a link that opens the design view attached to the session; the explorer integration on the story map is deferred |
| `harness/design_canvas/versions.py` | Observed: *CanvasVersions* records the claude.ai link of each published version (`record_link`, `link`) |

Deferred (still Intended on the map, 2026-11-06): the story explorer opening below the story map on a story's design canvas screen. Its two scenarios are dropped from this increment until that integration is planned.

#### Scenario: The file viewer opens the session's design view

*Given* ++checkout-flow++'s UX practice has design canvas version-2 with the design view https://claude.ai/design/checkout-flow-v2  
  *And* the file viewer is open on ++checkout-flow++  
*When* the Person opens the design view from the file viewer  
*Then* https://claude.ai/design/checkout-flow-v2 opens in Claude Design

#### Scenario: A session with no design view offers no link

*Given* ++billing-report++ has Stories and DDD enabled  
  *But* no design view is recorded for ++billing-report++  
*When* the Person opens ++billing-report++'s file viewer  
*Then* the file viewer shows no design view link

## Story: Deploy Story UI App With Board State

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:819-821` | Requested (2026-11-06, non-functional): the Story UI app runs on the same app server and instance as the board's state; Requested (2026-11-12): built with the cdd_web_domain_access and lern_domain_driven patterns |
| `../story-ui/packages/story-map-workspace/serve.ts` | Observed: today it runs its own API on port 3001 and Vite on 3000 |

#### Scenario: The board's server serves the Story UI editor

*Given* the CDD Kanban runs on port 8778  
*When* the Agent deploys the Story UI editor with the board's state  
*Then* the Story UI editor answers at http://127.0.0.1:8778/story-map  
  *And* the app status row reads Story UI running :8778  
  *And* nothing answers for the Story UI on ports 3000 or 3001

#### Scenario: A ticket activated on the board is the one the Story UI editor shows

*Given* the Story UI editor is open on ++checkout-flow++'s story-map.md  
*When* the Person activates ++billing-report++'s ticket on the board  
*Then* the Story UI editor shows ++billing-report++'s story map, without a reload

## Story: Refactor Story UI App To Web Domain Access

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:823-825` | Requested (2026-11-12): the story map's backend moves out of TypeScript into the MCP-generated domain objects, not a JSON story map; each edit is saved and rendered to the formats chosen in the chat bar, which the Story UI app can toggle |
| `../story-ui/packages/story-map-workspace/stories/stories.ts` | Observed: today the domain (`StoryMapModel`, `EpicModel`, `ScenarioModel`, `StoryMapRepository`) is TypeScript over a JSON story map |
| `cdd_guidance/patterns/cdd_web_domain_access` | `domain-lives-in-python`, `state-lives-behind-the-tool`, `fail-loud-on-mcp` |
| `harness/.context/grill-answers.md` (Decisions 2026-11-12, from the person) | Requested: descriptions on epics, sub-epics and stories, saved unchanged so hand-written maps are editable; scenario files editable; acceptance tests shown as links; examples as the model holds them; increments in the story model |
| `harness/.context/grill-answers.md` (Decided while closing the three Story UI gaps) | Decided (2026-11-12): an acceptance-test link opens the file in the chat bar's file viewer through `Chat.send` (`open_file`); example rows are edited through `Example`'s own tools and written back in their row; epic and sub-epic descriptions are edited on screen |

#### Scenario: An edit is saved in the story map file and rendered to the chosen formats

*Given* ++checkout-flow++'s story-map fidelity has ++story map, markdown and drawio++ chosen  
  *And* the Story UI editor is open on ++story-map.md++  
*When* the Person renames the story Open Kanban Side Panel From Chat Bar to Open Board Side Panel From Chat Bar  
*Then* ++story-map.md++ names the story Open Board Side Panel From Chat Bar  
  *And* ++story-map.drawio++ names the story Open Board Side Panel From Chat Bar  
  *And* no JSON story map is written

#### Scenario: A format turned off in the Story UI editor is off in the chat bar and left out of the next save

*Given* ++checkout-flow++'s story-map fidelity has ++story map, markdown and drawio++ chosen  
*When* the Person turns drawio off in the Story UI editor  
*Then* the chat bar's drawio chip shows off for the story-map fidelity  
*When* the Person adds the story Open Graph Side Panel From Board under Integrate Practice Content Editor Apps In Chat Bar  
*Then* ++story-map.md++ holds the new story  
  *And* ++story-map.drawio++ is left as it was

#### Scenario: The Story UI editor shows an edit the agent made through the tools

*Given* the Story UI editor is open on ++story-map.md++  
  *And* the Agent renamed the story Trace Story Through Artifacts to Trace Story Across Artifacts through the story map's tools  
*When* the Person reads the story map in the Story UI editor  
*Then* the Story UI editor shows Trace Story Across Artifacts

#### Scenario: An edit with the cdd server down says so and is not shown as saved

*Given* the Story UI editor is open on ++story-map.md++  
  *But* the cdd server is not answering  
*When* the Person renames the story Trace Story Through Artifacts  
*Then* the Story UI editor says the cdd server is not answering and how to start it  
  *And* it still shows Trace Story Through Artifacts

#### Scenario: A story map laid out by hand is saved with every line an edit does not touch

*Given* the Story UI editor is open on ++this repository's story map++  
*When* the Person renames the story Open Story UI Side Panel From Chat Bar to Open Story UI Beside The Chat  
*Then* ++this repository's story map++ changes only that story's heading  
  *And* the paragraphs under each heading, the lines above the first epic and every other heading stay as written

#### Scenario: A story's description is the paragraph under its heading and is edited there

*Given* the Story UI editor is open on ++this repository's story map++  
*When* the Person changes the description of Open Story UI Side Panel From Chat Bar  
*Then* the Story UI editor shows the new description on the story  
  *And* ++this repository's story map++ changes only the paragraph under that story's heading

#### Scenario: A scenario file is edited in the Story UI editor through the story model

*Given* the Story UI editor is open on ++chat bar scenarios++  
*When* the Person adds the step "the story map file keeps its other lines" to a scenario  
*Then* ++chat bar scenarios++ holds the step under that scenario  
  *And* every other line of ++chat bar scenarios++ stays as written  
  *And* the Story UI editor shows each scenario's examples as the story model's one table, a row per example

#### Scenario: An example's cell is edited in the Story UI editor and written back in its row

*Given* the Story UI editor is open on ++chat bar scenarios++  
*When* the Person changes the lines of the Ticket Archive name example of Trace Story Through Artifacts from 86 to 88 to 86 to 90  
*Then* ++chat bar scenarios++ changes only that example's row  
  *And* the Story UI editor shows 86 to 90 in that row

#### Scenario: An example named by its example column is renamed in that cell

*Given* the Story UI editor is open on a scenario file whose examples are named by their example column  
*When* the Person changes the example not running to stopped  
*Then* the scenario file changes only that cell of its row  
  *And* the Story UI editor names the example stopped

#### Scenario: An example keeps the place its table gives it

*Given* the Story UI editor is open on ++chat bar scenarios++  
*When* the Agent moves the second example of Trace Story Through Artifacts before the first  
*Then* the story map refuses the move, saying an example keeps the place its table gives it  
  *And* ++chat bar scenarios++ stays as written

#### Scenario: An epic's and a sub-epic's description are edited on screen

*Given* the Story UI editor is open on ++this repository's story map++  
*When* the Person opens the epic Move Work Forward From Chat Bar and changes its description  
*Then* ++this repository's story map++ changes only the paragraph under that epic's heading  
*When* the Person opens the sub-epic Integrate Practice Content Editor Apps In Chat Bar and gives it a description  
*Then* ++this repository's story map++ adds only that paragraph under that sub-epic's heading

#### Scenario: A story's acceptance tests are links, not edited

*Given* the Story UI editor is open on ++story-map.md++ beside ++checkout-flow++'s chat  
  *And* the session holds an acceptance-test file for Open Story UI Side Panel From Chat Bar  
*When* the Person opens the story Open Story UI Side Panel From Chat Bar  
*Then* the Story UI editor links the story to its acceptance-test file  
  *And* a press on the link shows the file in the chat bar's file viewer of ++checkout-flow++'s chat  
  *But* the Story UI editor opens no file of its own  
  *And* no other story links to it

#### Scenario: A Story UI editor no chat opened says where to read a story's acceptance tests

*Given* the Story UI editor is open on ++story-map.md++ in a window no chat opened  
  *And* the session holds an acceptance-test file for Open Story UI Side Panel From Chat Bar  
*When* the Person opens the story Open Story UI Side Panel From Chat Bar  
*Then* the Story UI editor names the acceptance-test file without a link  
  *And* it says to open the Story UI from the chat bar, or from a ticket with a chat, to read it in the chat's file viewer

#### Scenario: Increments are edited through the story map and kept in its thin slice

*Given* the Story UI editor is open on ++this repository's story map++  
  *And* ++this repository's thin slice++ orders its increments  
*When* the Person adds the increment Edit Story Maps In Story UI and gives it Open Story UI Side Panel From Chat Bar  
*Then* ++this repository's thin slice++ lists Edit Story Maps In Story UI after its last increment, with that story  
  *And* the increment that delivered the story no longer lists it  
  *And* every other line of ++this repository's thin slice++ stays as written

## Story: Open UX Design In Claude Design

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Person --> Open UX Design In Claude Design |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The ticket's UX design opens as a design canvas

*Given* checkout-flow has UX enabled  
  *And* checkout-flow has a UX design canvas  
*When* the Person opens checkout-flow's UX design from its ticket  
*Then* the UX design opens as a design canvas in Claude Design

#### Scenario: A ticket without UX has no design to open

*Given* billing-report has Stories and DDD enabled  
  *But* UX is not enabled for billing-report  
*When* the Person looks at billing-report's ticket  
*Then* the ticket offers no UX design

## Story: Trace Story Through Artifacts

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Person --> Trace Story Through Artifacts |
| `.sessions/_backlog/integrate-practice-content-editor-apps.md` | "Trace pane": a story's scenarios, tests, code and diagrams, read from the knowledge graph |

#### Scenario Outline: The Inspector traces a violation's story through its artifacts

*Given* checkout-flow is the active ticket  
  *And* generate has reloaded checkout-flow's graph  
*When* the Person opens the ++${violation}++ violation in the Inspector  
*Then* ${file} opens at lines ${lines}  
  *And* the trace under the file names ${story}, its scenarios, tests and code from the graph

##### Examples

| violation | file | lines | story |
| --- | --- | --- | --- |
| Ticket Archive name | harness/.context/stories/story-map.md | 86 to 88 | Ticket Archive |
| Move Ticket size | harness/.context/stories/story-map.md | 148 to 150 | Move Ticket |
| Activate Ticket name | space/kanban/ticket.py | 212 to 213 | Activate Ticket |
