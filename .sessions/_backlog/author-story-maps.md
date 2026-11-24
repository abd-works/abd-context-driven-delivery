# Author Story Maps

**Outcome:** the Story UI editor gets its own remaining stories: dashboard, nested lanes, the node inspector, save history, real-time sessions and AI story changes.

**Slicing notes:** requested on 2026-11-06: the Author Story Maps stories move out of Fully Integrated App Flow into an increment of their own, right after it.

## Epic: Author Story Maps

### Feature: Save And Share Changes

#### Story: Test Story UI Editor On Session Story Map

*Agent*. Requested on 2026-11-06: the Story UI editor opens a CDD session's `story-map.md`, edits it and saves it back, and its tests run against that map. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

#### Story: Record One Save Event Per Save

*Story UI*. Intended (mern-story-map-ai-sketch.md Resolved Implementation Decisions; story_map.modules.md audit): stories-server.ts only comments that the collaboration layer emits the event, and no audit module exists.

#### Story: Browse Save History

*Story Designer*. Intended (story_map.information_architecture.md, Version History Timeline scaffold): no history screen or save record exists.

#### Story: Recover Workspace View State

*Story Designer*. Intended (story_map.stories.md, Recover Persisted Story Map State; story_map.modules.md session): session.ts and session-server.ts can store view mode, expanded nodes, and toggles, but app.ts never mounts `createSessionRouter` and the workspace never calls `useStoryMapSession`, so a reload resets the view.

#### Story: Join Real-Time Story Map Session

*Story Designer*. Intended (story_map.stories.md, Synchronize Story Map State; story_map.modules.md collaboration): no collaboration module or broadcast exists.

#### Story: Reconcile Concurrent View State Changes

*Story UI*. Intended (story_map.stories.md, Resolve Concurrent View State Changes; mern-story-map-ai-sketch.md realtime-collaboration): no collaboration module exists.

### Feature: View Story Map

#### Story: Pick Story Map From Dashboard

*Story Designer*. Intended (story_map.information_architecture.md, Story Map Dashboard scaffold): a dashboard lists maps and "open map" takes the designer into the workspace; no dashboard screen exists.

#### Story: Browse Nested SubEpic Lanes

*Story Designer*. Intended (mern-story-map-ai-sketch.md, Browse Story Hierarchy): nested SubEpics render as two stacked SubEpic lanes under their parent SubEpic; the model in stories.ts holds only one SubEpic level.

#### Story: Inspect Selected Node Fields

*Story Designer*. Intended (mern-story-map-ai-sketch.md, BDD "when the Story Designer selects a node"): selecting a Story shows story_type and users, a SubEpic shows test_file and domain_concepts; the cards show only names and controls.

#### Story: Show And Hide Scenarios And Examples

*Story Designer*. Intended (story_map.information_architecture.md toolbar; story_map.modules.md session toggles): Show Scenarios and Show Examples buttons toggle their active state in stories-client.tsx, but the story card and scenario panel ignore them, so nothing is shown or hidden.

### Feature: Author Story Changes With AI

#### Story: Open AI Chat Panel

*Story Designer*. Intended (story_map.information_architecture.md, open chat to AI Chat Panel scaffold): no chat panel exists.

#### Story: Request AI Story Change

*Story Designer*. Intended (story_map.stories.md, Request AI Story Mutation; story_map.modules.md ai-mutation): no ai-mutation module exists.

#### Story: Review Proposed Map Changes

*Story Designer*. Intended (story_map.stories.md, Review Proposed Graph Changes): no proposal view exists.

#### Story: Apply AI Change To Story Map

*Agent*. Intended (story_map.stories.md, Apply AI Mutation to Story Map; mern-story-map-ai-sketch.md "Direct auto-apply changes"): no ai-mutation module exists.

## From Fully Integrated App Flow

Moved here on 2026-11-23: the Story UI editor's screen frames view and its increment tickets are the editor's own stories.

### Feature: Connect Chat Bar Board And Story UI

#### Story: Start Ticket Session From Increment

*Person*. Requested (2026-11-06, "increment could be a separate ticket/session in board"; "create a ticket on board on demand in backlog with proper naming reference to story map increment"): the Story UI editor's increments view offers Create ticket on each increment; pressing it adds a ticket to the board's backlog named after the story map and the increment, with its own session holding that increment's stories.

#### Story: Show Increment Ticket In Story UI

*Board App*. Requested (2026-11-06, "story UI -> board/chat integration"): an increment that has a ticket shows that ticket's stage and active state in the Story UI editor.

### Feature: Show Screen Frames In Story UI

#### Story: Switch Story Map To Screen Frames View

*Person*. Requested (2026-11-06): the Story UI editor has a screen frames view beside its base view; in it, each story's card has its screen as a frame beneath it. The base view stays the plain story map.

#### Story: Show Screen Frame Under Each Story

*Story UI*. Requested (2026-11-06): each frame is the story's main design canvas screen, drawn small under its card. It replaces the design canvas, where today the story map artboard draws a thumbnail under each story (`thumbnail` in `canvas.py`, `claude_design_story_model_spec.py`).

#### Story: Mark Story Without A Screen

*Story UI*. Requested (2026-11-06): a story with no screen gets an empty frame saying so. It replaces the design canvas, where today the artboard shows "No screenshot" in place of the picture (`thumbnail` in `canvas.py`).

#### Story: Open Story Explorer From Screen Frame

*Person*. Requested (2026-11-06): pressing a frame opens the browser story explorer at that story, scenario and step. It replaces the design canvas, where today only the artboard's thumbnails link, each opening `explorer.dc.html` at its story (`claude_design_story_model_spec.py`).

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.
