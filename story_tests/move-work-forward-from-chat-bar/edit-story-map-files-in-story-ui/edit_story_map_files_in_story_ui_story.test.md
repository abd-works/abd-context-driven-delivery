---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Edit Story Map Files In Story UI

### Domain terms

Each term links to its class in the model, [editor-apps-model.md](../../../harness/.context/editor-apps/.context/editor-apps-model.md).

- ++side panel++ — the pane beside the chat an app opens in, at the app's url.
- ++file viewer++ — the chat bar's files pane: one tab per file a fidelity declares.
- ++story map++ — a Stories file read as epics, sub-epics, stories and scenarios ([StoryMap](../../../harness/.context/editor-apps/.context/editor-apps-model.md#storymap-extended)).
- ++chosen formats++ — the formats kept for a fidelity in the session, which the chat bar's chips and the Story UI's toggles both change ([FidelitySessionOutput.chosen_formats](../../../harness/.context/editor-apps/.context/editor-apps-model.md#fidelitysessionoutput-extended)).

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### sessions ([Session](../../../harness/.context/editor-apps/.context/editor-apps-model.md#session-extended), [PracticeGuidance.session_root](../../../harness/.context/editor-apps/.context/editor-apps-model.md#practiceguidance-extended))

| session | practices enabled | practice roots | stories it names |
| --- | --- | --- | --- |
| ++checkout-flow++ | Stories, UX, Clean Engineering | harness/.context/stories, harness/.context/ux, harness/.context | Open Story UI Side Panel From Chat Bar, Open Kanban Side Panel From Chat Bar |
| ++billing-report++ | Stories, DDD | billing/.context/stories, billing/.context | Report Billing By Month |

### files ([PracticeGuidance.editor](../../../harness/.context/editor-apps/.context/editor-apps-model.md#practiceguidance-extended), [StoryMap](../../../harness/.context/editor-apps/.context/editor-apps-model.md#storymap-extended))

| file | practice | fidelity | editor tile |
| --- | --- | --- | --- |
| ++story-map.md++ | Stories | story map | Story UI editor |
| ++story-map.drawio++ | Stories | story map | Story UI editor |
| ++chat bar scenarios++ (`move-work-forward-from-chat-bar/.../integrate_practice_content_editor_apps_in_chat_bar_story.test.md`) | Stories | scenarios | Story UI editor |
| ++canvas.json++ (`harness/.context/ux/canvas.json`) | UX | mockup | none |
| ++this repository's story map++ (`.context/story-map.md`, laid out by hand) | Stories | story map | Story UI editor |
| ++this repository's thin slice++ (`.context/thin-slice.md`) | Stories | story map | none: its increments are edited on the story map |

### chosen formats ([FidelitySessionOutput.chosen_formats](../../../harness/.context/editor-apps/.context/editor-apps-model.md#fidelitysessionoutput-extended))

| fidelity | chosen formats | files a save writes |
| --- | --- | --- |
| ++story map, markdown and drawio++ | markdown, drawio | story-map.md, story-map.drawio |
| ++story map, markdown only++ | markdown | story-map.md |

## Story: Save Story Map Edit Through Domain

### Evidence

| Source | Note |
|--------|------|
| `.context/story-map.md:823-825` | Requested (2026-11-12): the story map's backend moves out of TypeScript into the MCP-generated domain objects, not a JSON story map; each edit is saved and rendered to the formats chosen in the chat bar, which the Story UI app can toggle |
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

## Story: Edit Descriptions And Increments On Story Map

#### Scenario: A story's description is the paragraph under its heading and is edited there

*Given* the Story UI editor is open on ++this repository's story map++  
*When* the Person changes the description of Open Story UI Side Panel From Chat Bar  
*Then* the Story UI editor shows the new description on the story  
  *And* ++this repository's story map++ changes only the paragraph under that story's heading

#### Scenario: An epic's and a sub-epic's description are edited on screen

*Given* the Story UI editor is open on ++this repository's story map++  
*When* the Person opens the epic Move Work Forward From Chat Bar and changes its description  
*Then* ++this repository's story map++ changes only the paragraph under that epic's heading  
*When* the Person opens the sub-epic Integrate Practice Content Editor Apps In Chat Bar and gives it a description  
*Then* ++this repository's story map++ adds only that paragraph under that sub-epic's heading

#### Scenario: Increments are edited through the story map and kept in its thin slice

*Given* the Story UI editor is open on ++this repository's story map++  
  *And* ++this repository's thin slice++ orders its increments  
*When* the Person adds the increment Edit Story Maps In Story UI and gives it Open Story UI Side Panel From Chat Bar  
*Then* ++this repository's thin slice++ lists Edit Story Maps In Story UI after its last increment, with that story  
  *And* the increment that delivered the story no longer lists it  
  *And* every other line of ++this repository's thin slice++ stays as written

## Story: Edit Scenario Files Through Story Model

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

## Story: Link Story To Its Acceptance Tests

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
