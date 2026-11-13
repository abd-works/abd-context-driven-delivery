# Fully Integrated App Flow

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** the chat bar, the board, the Story UI editor with its story explorer, and the Graph app work on one ticket together, and violations are read from the latest graph that generate refreshes.

**Slicing notes:** requested on 2026-11-06: validation inside generate, the chat bar and board joined with the Story UI editor, the story explorer in the Story UI app framed by design canvas screens, and each app tested on a real session.

## Notes from the backlog

From `board-enhancements.md`:

> better graph integration - eg load up fron on sesison open show all violations as a result of graph no need fo exlici run

From `mod-ideas.md`, "Validate on save":

> When an artifact in a session changes, run the graph rules and update the band.

Built today: Attach Violations To Latest Graph (a graph refresh records each violation on its node).

## Epic: Connect Sessions Across Channels And Apps

### Feature: Check Work In Generate

#### Story: Refresh Graph After Generate

*Generate*. Requested (2026-11-06, "generate --> load refreshed graph based on changes immediately"): when generate writes a fidelity's files, the knowledge graph rebuilds those files at once, without a separate load or Validate run. Built today (checked 2026-11-10): generate tells the agent to call validate afterwards, and validate refreshes the graph (`generate.py:32-33`, `graph.py:1397`). Missing: generate refreshing the graph itself.

#### Story: Judge Rules During Generate

*Generate*. Requested (2026-11-06, "judge validation must be part of generate, merge the two actions"): generate ends with the agent's rule-by-rule judgment of what it wrote, saved with the graph's hits, so a generate counts as generated and validated. Built today (checked 2026-11-10): generate ends by calling validate, which runs the AI judgment and saves it with the graph hits (`generate.py:32-36`, `validate.py:80`). Missing: one action; validate is still a separate call, log line, and board and chat bar action.

#### Story: Fix Graph Violations

*Agent*. Requested (2026-11-06, "/fix is a first class action; fix rule; file; default across all rules / files"): Fix is an action of its own: on one rule, on one file, or by default on every violation of every rule in every file, reading the violations from the latest graph.

#### Story: Validate Fidelity On Demand

*Agent*. Requested (2026-11-06, "validate still exists as independent action"; "validate is a slash command story only now"): Validate runs on its own on any files only as the `/actions-validate` slash command, and its report is saved as today; the board and the chat bar have no Validate, since generate judges the rules. Built today (checked 2026-11-10): `/actions-validate` runs and saves its report. Missing: validate is still on the board tiles (`action-bar-view.tsx:64-70`) and in the chat bar's stage actions.

#### Story: Check Graph Rules When An Artifact Changes

*Claude Code* (system). Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "Validate on save"): when an artifact in a session changes, the graph rules run on it and the band's violation count updates, with no explicit validate.

### Feature: Read Graph Violations On Board

#### Story: Read Fidelity Violations From Latest Graph

*Board App*. Requested (2026-11-06, "default is to have a graph and just read the violations"): a tile's violation count and list come from the latest graph, not from the last validation report. Also Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "better graph integration - load up front on session open, show all violations as a result of graph, no need for explicit run").

#### Story: Generate And Judge Fidelity From Board

*Person*. Requested (2026-11-06, "board and chat generate"): an expanded tile offers ▶ generate, which runs generate with its judgment on the ticket's enabled practices, and the tile shows the violations the refreshed graph holds. Built today (checked 2026-11-10): a tile's generate sends `/actions-generate`, which chains to validate. Missing: the tile's violations come from the report, not the refreshed graph.

#### Story: Fix Graph Violations From Board

*Person*. Requested (2026-11-06, "board and chat ... fix"): an expanded tile offers fix, and the Inspector offers Fix rule and Fix this one; each sends the Fix action for that scope, and with nothing picked it fixes every violation. Built today (checked 2026-11-10): the report panel has Fix per violation, Fix all per rule and Fix all violations (`report-rule-view.tsx:56,79`, `report-panel-view.tsx:71`), as prompts built from the report. Missing: Fix on the expanded tile, fed from the graph.

### Feature: Read Graph Violations In Chat Bar

#### Story: Read Session Violations From Latest Graph

*Chat Bar*. Requested (2026-11-06, "default is to have a graph and just read the violations"): each fidelity dot's red count comes from the latest graph, not from the last validation report.

#### Story: Generate And Judge Fidelity From Chat Bar

*Person*. Requested (2026-11-06, "board and chat generate"): generate from the action button runs generate with its judgment, and the dots update from the refreshed graph. Built today (checked 2026-11-10): generate from the action button chains to validate. Missing: the dots update from the report, not the graph.

#### Story: Fix Graph Violations From Chat Bar

*Person*. Requested (2026-11-06, "board and chat ... fix"): Fix in the action picker sends the Fix action for the selected fidelity, a rule or a file, every violation by default.

### Feature: Connect Chat Bar Board And Story UI

#### Story: Open Board Side Panel From Chat Bar

*Person*. Requested (2026-11-06, "chat band -> board side panel"): the chat bar opens the active ticket's board card and tiles in a side panel beside the chat.

#### Story: Sync Chat Bar With Board Selection

*Chat Bar*. Requested (2026-11-06, "update chat band, eg selected stage, next action"; "and on the chat panel"; "and practices enabled for that session"): a ticket, stage or fidelity selected on the board becomes the chat bar's session, shown stage and selected fidelity, so the action button shows that fidelity's next action; the chat panel switches to that ticket's chat and the band shows the practices enabled for its session.

#### Story: Keep Chosen Formats Across Actions In A Fidelity

*Chat Bar*. Requested (2026-11-06, "have format saved across actions in fidelity"): the formats picked for a fidelity stay picked when the person switches between generate, render, sketch, iterate, document and fix, so each action writes the same formats without picking them again. Built today (checked 2026-11-10): format chips are kept per set of fidelities (`format-choices-client.ts:23,30`, commit 07c9026ee). Missing: the picks go back to the defaults after an action runs, and only generate and render take formats.

#### Story: Start Ticket Session From Increment

*Person*. Requested (2026-11-06, "increment could be a separate ticket/session in board"; "create a ticket on board on demand in backlog with proper naming reference to story map increment"): the Story UI editor's increments view offers Create ticket on each increment; pressing it adds a ticket to the board's backlog named after the story map and the increment, with its own session holding that increment's stories.

#### Story: Show Increment Ticket In Story UI

*Board App*. Requested (2026-11-06, "story UI -> board/chat integration"): an increment that has a ticket shows that ticket's stage and active state in the Story UI editor.

## Epic: Explore Stories In Story UI

### Feature: Play Stories In The Explorer

#### Story: Test Story Explorer On Session Story Map

*Agent*. Requested on 2026-11-06: the browser story explorer plays a CDD session's story map on its design canvas screens, and its specs run against that map. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

#### Story: Play The Next Story

*Person*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer's *Play next* button moves the selection to the next step or story (`explorer.dc.html`).

#### Story: Hide And Show The Story Panel

*Person*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the » and « buttons hide the story panel so the screen fills the frame, and bring it back (`explorer.dc.html`).

#### Story: Return To Story UI Map

*Person*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the panel's **← Story map** link opens `Main.dc.html` again (`explorer.dc.html`).

### Feature: Show Screen Frames In Story UI

#### Story: Switch Story Map To Screen Frames View

*Person*. Requested (2026-11-06): the Story UI editor has a screen frames view beside its base view; in it, each story's card has its screen as a frame beneath it. The base view stays the plain story map.

#### Story: Show Screen Frame Under Each Story

*Story UI*. Requested (2026-11-06): each frame is the story's main design canvas screen, drawn small under its card. It replaces the design canvas, where today the story map artboard draws a thumbnail under each story (`thumbnail` in `canvas.py`, `claude_design_story_model_spec.py`).

#### Story: Mark Story Without A Screen

*Story UI*. Requested (2026-11-06): a story with no screen gets an empty frame saying so. It replaces the design canvas, where today the artboard shows "No screenshot" in place of the picture (`thumbnail` in `canvas.py`).

#### Story: Open Story Explorer From Screen Frame

*Person*. Requested (2026-11-06): pressing a frame opens the browser story explorer at that story, scenario and step. It replaces the design canvas, where today only the artboard's thumbnails link, each opening `explorer.dc.html` at its story (`claude_design_story_model_spec.py`).

### Feature: Navigate The Story Tree

#### Story: Open The Explorer At A Story, Scenario And Step

*Person*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `explorer.dc.html` reads the story, scenario and step from the link, or from the place the map kept, and selects it in the tree.

#### Story: Collapse And Reset The Story Tree

*Person*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer's *Collapse all* and *Reset* buttons close the epic → sub-epic → story → scenario → step tree or return it to the first story (`explorer.dc.html`).

#### Story: Keep The Selected Story In View

*Story UI*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer scrolls the selected entry into view when the selection changes (`explorer.dc.html`).

#### Story: Copy A Request To Open A Story In Its File

*Person*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, the explorer carries each story's and scenario's `path:line` and offers to copy an open-in-file-viewer request for it (`claude_design_story_model_spec.py`, `copyOpenRequest` in `explorer.dc.html`).

#### Story: Pick An Outline Scenario's Example

*Person*. Built in the design canvas explorer (checked 2026-11-10): `explorer.dc.html` lists an outline scenario's examples from the fixtures bundle and picking one calls `go(..., ex.name)` (`outlineRows`). Intended: the Story UI explorer does the same. Was: Intended (`claude_design.md` outline-rows): an outline scenario lists its examples from the fixtures bundle and picking one loads it on the screen; the explorer does not list them yet.

### Feature: Frame Design Canvas Screens In Explorer

#### Story: Show Design Canvas Screen As Explorer Frame

*Story UI*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, `_imports` in `nodes.py` imports each prototype screen into the explorer with the story, scenario and a `go` call, so the selected scenario runs on the real screen (`claude_design_story_model_spec.py`).

#### Story: Choose The Screen For A Step

*Story UI*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, a step shows the screen it is shown on, else its scenario's screen, else its story's screen (`_story_entry` and `_screen_of` in `nodes.py`, `claude_design_story_model_spec.py`).

#### Story: Join A Step Without A Screen To The Next Step

*Story UI*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `_story_entry` in `nodes.py` groups a step with no screen of its own with the next step that has one, so every entry the person picks shows a screen.

#### Story: Show A Screenshot When No Screen Runs

*Story UI*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, when no prototype applies, the explorer shows the step's screenshot, skipping blank captures (`_blank` in `nodes.py`).

#### Story: Keep Each Screen's Own Stylesheets

*Story UI*. Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `_stylesheets` in `nodes.py` links every stylesheet the prototype screens use, so a screen drawn inside the explorer keeps its own look.

## Epic: Move Work Forward On Session Board

### Feature: Work Fidelity Outputs On Board → Integrate Practice Content Editor Apps On Board

#### Story: Invoke Story Explorer In Session Context

*Person*. Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "view story map / ux design canvas for a session", requested on 2026-11-06): the board opens the browser story explorer on the ticket's story map, framed by its design canvas screens.

## Epic: Move Work Forward From Chat Bar

### Feature: Work Fidelity Outputs In Chat Bar → Integrate Practice Content Editor Apps In Chat Bar

#### Story: Open UX Design In Claude Design

*Person*. Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "claude design integration with ux tool"): the UX practice's design opens in Claude Design from the chat.

## Epic: Build Design Canvas Screens

### Feature: Publish And Release A Canvas Version

#### Story: Remove Older Versions When Keeping A Release

*Agent*. Intended (`claude_design.md` release-a-version): when a version is kept as a release the older versions are removed; `release` in `versions.py` only renames.

## Epic: Map Work Into Knowledge Graph

### Feature: Review Violations In Graph App

#### Story: Test Knowledge Graph Explorer On Session Files

*Agent*. Requested on 2026-11-06: the Graph app loads a CDD session's files and shows their nodes and violations, and its specs run against those files. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

#### Story: Display Drawio File As Diagram

*Person*. Requested on 2026-11-06: a `.drawio` file opens as its diagram, with a Source tab for the XML. A violation marks the shape it names in red, and pressing a shape opens its lines in the source. Built today (checked 2026-11-10): the chat bar's files view offers Open in draw.io, which opens the file in the draw.io editor through `tools/drawio_viewer` (`drawio-viewer-client.ts:44`). Missing: a Source tab, marking the shape a violation names, and opening a pressed shape's lines.
