---
fidelity: [discovery]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Context-Driven Delivery Framework incremental backlog

## Product / context

**Product:** the CDD framework, its CDD Kanban and its Chat Bar, as mapped in [story-map.md](story-map.md).

**Slicing intent:** Increment 0 is what the code does today. The Intended and Requested stories follow the order set on 2026-11-06.

**Spine vs optional:** the increments run in the order they are built, as set on 2026-11-10: ticket management and the editor-app stories first, then syncing the design canvas with production and integrating stories with the canvas explorer, then repairing guidance from mistakes, then faster command entry and the Clean Engineering checks on the model, then the fully integrated flow, then the board's file review, workflow customizing and the Story UI editor's own stories; guards, a faster board, chat bar parity and linked models on the canvas follow, and next-step suggestions come last.

## Increments

### Increment 0: Built Today

**Outcome:** what the framework, the CDD Kanban and the Chat Bar do now: every story whose evidence is Observed or Inferred.

**Slicing notes:** not a slice to build; it is the starting line the other increments add to.

**Stories in this increment:**

- *Register Agent Toolsets*
- *Register Agent Operations*
- *Register Agent Tools*
- *Register Agent Instructions*
- *Validate Instruction Body*
- *Register Guidance*
- *Register Fidelities*
- *Register Action Tools*
- *Register Action Prompt*
- *Build Instruction Expansion*
- *Collect Deferred Tools*
- *Publish Markdown Files*
- *Publish Guidance Files*
- *Publish Action Command*
- *Store Install State*
- *Record Mcp Operation*
- *Publish Mcp Manifest*
- *Register Hook Event*
- *Publish Hooks Manifest*
- *Compose Practice Action Fidelity Command*
- *Load Practice Fidelity Instructions*
- *Call CDD Tool Through MCP*
- *Guide Output With Matching Rules*
- *Index Source Into Lens Segments*
- *Add Lens To Existing Index*
- *Describe Existing Artifacts*
- *Capture Documents Into Searchable Context*
- *Capture Live App Context*
- *Grill Plan Against Context*
- *Sketch Rough Draft*
- *Iterate One Slice At A Time*
- *Record Context Decision*
- *Generate Fidelity Artifact*
- *Render Artifact Into Another Format*
- *Generate From Previous Fidelity*
- *Generate Several Practices In One Command*
- *Validate Artifact Against Rules*
- *Satisfy Violations Until Clean*
- *Start CDD Server On Session Start*
- *Inject Action Rules After Action Call*
- *Inject Practice Rules After File Edit*
- *Announce Running Action In Toast*
- *Log Prompts And Tool Calls*
- *Display Board Server Health*
- *Update Board And CDD*
- *Open Board*
- *Display Board*
- *Arrange Board And Details*
- *Display Backlog Items As Tickets*
- *Display Ticket Card*
- *Display Ticket Details*
- *Set Stage WIP Limit*
- *Arrange Side Panel*
- *Open Ticket Session*
- *Activate Ticket*
- *Close Active Session*
- *Move Ticket*
- *Write Ticket Handoff*
- *Display Latest Handoff*
- *Restrict Actions To Active Session*
- *Add Backlog Item*
- *Archive Ticket*
- *Split Ticket Into Child Tickets*
- *Display Fidelity Progress*
- *Open Practice Tile*
- *Choose Ticket Practices*
- *Send Next Fidelity Action*
- *Send Action To Stage Practices*
- *Mark Ticket Done In Stage*
- *Open Help*
- *Choose Action And Formats*
- *Resolve Fidelity Output Paths*
- *Generate Fidelity Output*
- *Render Fidelity Format*
- *Send Tile Action To Chat*
- *Validate Fidelity*
- *Save Validation Report*
- *Open Validation Report*
- *Fix Report Violations*
- *Display Violations Band*
- *List Ticket Files*
- *Browse Ticket Folder*
- *View Fidelity Files*
- *Review Fidelity*
- *Display Server Health Mark*
- *Open Server Health Panel*
- *Reconnect CDD Server*
- *Reinstall CDD Tools*
- *Open Board From Chat*
- *Display Stage Strip*
- *Display Session Fidelity Dots*
- *Display Stage Fidelities*
- *Display Session Card*
- *Show Active Session On Status Line*
- *Add Active Ticket To System Prompt*
- *Create New Session*
- *Open Session*
- *Write Session Handoff*
- *Close Session From Chat Bar*
- *Move Session To Next Stage*
- *Select Fidelity*
- *Choose Action*
- *Generate Session Fidelity Output*
- *Resolve Session Fidelity Output Paths*
- *Fill Prompt With Fidelity Action*
- *List Session Files*
- *View Session Files*
- *Open Validation Report From Violation Count*
- *Review Session Fidelity*
- *Open Story Map By Address*
- *Browse Story Hierarchy*
- *Pan Workspace Canvas With Right-Click Drag*
- *Switch Between Map View And Increment View*
- *Switch Color Mode*
- *Expand One Story Card*
- *Expand Descendant Story Cards*
- *Expand And Collapse Whole Map*
- *Widen Columns Around Expanded Story Cards*
- *Add First Epic To Empty Map*
- *Add Epic, SubEpic, Or Story At Chosen Position*
- *Remove Epic, SubEpic, Or Story*
- *Rename Node Inline*
- *Reorder Sibling Epics, SubEpics, And Stories*
- *Move Story To A Different SubEpic*
- *Move SubEpic To A Different Epic*
- *Drop Node Into Empty Parent*
- *See Full-Size Drop Preview While Dragging*
- *Add Increment*
- *Rename Increment*
- *Reorder Increments*
- *Remove Increment*
- *Assign Story To Increment By Dragging*
- *Unassign Story From Increment*
- *Add Scenario Under Story*
- *Rename Scenario*
- *Remove Scenario*
- *Reorder Scenarios*
- *Add Step*
- *Edit Step Keyword And Text*
- *Remove Step*
- *Reorder Steps*
- *Add Example To Scenario*
- *Remove Example From Scenario*
- *Add Example Field*
- *Remove Example Field*
- *Add Example Line*
- *Edit Example Cell*
- *Remove Example Line*
- *Reorder Example Lines*
- *Save Each Edit To The Server*
- *Show Save Status*
- *Refuse Edits That Break Map Rules*
- *Place Pages On The Canvas*
- *Place Artboards On Their Pages*
- *Write The Canvas Into A Project Folder*
- *Name An Imported Screen After Its File*
- *Give Each Prototype Screen Its Own Page*
- *Place A Read-Only Story Panel Beside A Screen*
- *Load A Scenario Into A Standalone Screen*
- *Load The Explorer's Scenario Into The Screen*
- *Pick Another Scenario From Inside The Explorer*
- *Paste Dev Seed Data Into A Screen*
- *Follow A Screen Link To The Next Story*
- *Edit A Screen On Its Own Artboard*
- *Report Where The Screen's Data Came From*
- *Start The First Version*
- *Start The Next Version As A Copy*
- *Write Into The Version Not Yet Published*
- *Refuse To Add To A Published Version*
- *Title A Published Canvas By Its Version*
- *Record Each Version's Published Link*
- *Keep A Published Version As A Release*
- *Start Numbering Again From A Release*
- *Find A Release's Canvas Folder*
- *Load Working Copy Into Graph*
- *Reuse Saved Graph*
- *Rebuild Graph After Source Or Rule Changes*
- *Force Graph Reload*
- *Load Only Edited Files*
- *Skip Build And Cache Folders*
- *Report Load Progress*
- *Save Graph To Context Folder*
- *Keep Other Practices When Saving*
- *Read Modules Classes And Operations*
- *Read Clean Engineering Model Documents*
- *Place DDD Building Blocks Under Aggregates*
- *Read Story Maps And Story Tests*
- *Read BDD Spec Trees*
- *Link Steps And Observations To Operations*
- *Link Examples To Classes And Steps*
- *Place Story Nodes On Their Source Lines*
- *Give Each Node Its Fidelity*
- *Add Named Overlay From Catalog*
- *Add Overlay Folder*
- *Remove Overlay*
- *Rebuild Graph With Overlay Nodes*
- *Remember Applied Overlays*
- *Choose Repo Folder*
- *Reopen Last Folder*
- *Expand Practice Tree*
- *Follow Relationships Under Node*
- *Open Node Source*
- *Unfold Calls And Classes In Source*
- *Show Load Steps While Loading*
- *Copy Load Failure For Agent*
- *Switch Display Theme*
- *Filter By Practice*
- *Filter By Node Type*
- *Filter By Connector*
- *Show Only Violations*
- *Filter Violations By Rule*
- *Select All Or No Filter Choices*
- *Return Matching Nodes With Relationships*
- *Return Only Failing Nodes And Rules*
- *List Practice Inventory*
- *List Filter Choices*
- *Read Node Source With Members*
- *Attach Schema Rules To Nodes*
- *Check Nodes Against Practice Rules*
- *Inherit Clean Engineering Rules On DDD Types*
- *Add Overlay Rules*
- *Mark Prose Rules As Prompts*
- *Place Violation At Node Lines*
- *Name Rules By Practice Node And Rule*
- *See Rules Under Node*
- *Hover Violating Rule For Message*
- *Open Violation In Source*
- *Copy Correct Prompt*
- *Build Graph From Edited Files*
- *Report Own Practice Violations*
- *Report Saved Graph Hits*
- *Leave Unedited Files Out*
- *Refuse Missing Path*
- *Save Checked Graph Beside Report*
- *Count Graph Hits From Report*
- *Select Several Fidelities*
- *Choose Format*
- *Open Ticket Chat On Session Open*
- *Display Report Without Header Noise*
- *Display Report Errors In Code Fences*
- *Refactor Knowledge Graph App To Web Domain Access*
- *Attach Violations To Latest Graph*
- *Choose Where A Backlog Item Works*
- *Choose Session And Practice Roots*

### Increment 1: Maintain Tickets On Board

**Outcome:** a person edits, orders, tags and removes tickets, and arranges them as parents and children.

**Slicing notes:** mod-ideas build order 4, finish the Kanban: board-enhancements "Tickets Enhancements".

**Stories in this increment:**

- *Edit Ticket Text*
- *Reorder Tickets In Column*
- *Tag Ticket Session*
- *Delete Ticket*
- *Expand Ticket From Empty Area*
- *Add Child Ticket*
- *Display Child Tickets In Parent*
- *Expand Parent Ticket*
- *Detach Child Ticket*
- *Reassign Ticket Parent*
- *Place Parent At Leftmost Child Stage*

### Increment 2: Integrate Practice Content Editor Apps

**Outcome:** the board and the chat bar open the Story UI editor, the Claude Design story explorer and the Graph app on the ticket's own scope, using what each app already does.

**Slicing notes:** requested on 2026-11-06: only the small stories that open an existing app in session context; the larger flow follows in Fully Integrated App Flow.

**Stories in this increment:**

- *Open Story UI Side Panel From Chat Bar*
- *Open Story UI On Ticket Scope*
- *Filter Knowledge Graph To Ticket Scope*
- *Filter Knowledge Graph To Ticket Practices*
- *Deploy Knowledge Graph App With Board State*
- *Trace Story Through Artifacts*
- *Invoke Claude Design Story Explorer From Chat Bar*
- *Deploy Story UI App With Board State*
- *Refactor Story UI App To Web Domain Access*

### Increment 3: Sync Design Canvas With Production

**Outcome:** a design canvas shows production as it is: every file is proven against the product repo by hash, styles and assets come from one pinned Design System package, each screen mounts the real view, hosted edits come back before the next version, and a screen being redesigned is detached and marked diverged until its change reaches production.

**Slicing notes:** `.sessions/_backlog/sync-design-canvas-with-production.md`, the asset reuse plan's phases 1 to 5, the features Trace Canvas Files To Production, Install Production Design System On The Canvas, Mount Production Views As Screens and Redesign A Screen By Detaching It. It comes before every other design canvas increment. Start with the plan's Phase 0 spike on `select-plan`. If its gates 1 to 3 fail, the mounting stories give way to screens rendered to markup and hash-pinned to the TSX; the tracing and Design System stories hold either way. Migrating pml-web's 28 screens and deleting its generators is a task inside this increment.

**Stories in this increment:**

- *Record Packaged Files In Sources Manifest*
- *Fail Check When A Packaged File Drifts*
- *Report Version Traceability Percentage*
- *Store Each Screenshot Once By Content Hash*
- *Find Screen Files Through The Manifest*
- *Package Product Styles And Assets In Their Production Layout*
- *Publish Product Package As Design System Artifact*
- *Record Installed Design Systems In Canvas File*
- *Derive Publish List From Sources Manifest*
- *Pull Hosted Edits Back Before Next Version*
- *Bundle Product Views For The Canvas*
- *Mount Production View In A Thin Screen*
- *Answer Screen Requests From Fixture Routes*
- *Keep Explorer Navigation Inside The Artboard*
- *Keep Product Styles Inside The Screen*
- *Type Scenario Values Into A Mounted Screen*
- *Generate Attached Screens Without Markup*
- *Detach A Screen To Editable Markup*
- *Keep Leaf Components Mounted In A Detached Screen*
- *Mark Detached Screen As Diverged*
- *Reattach A Screen Once Its Change Reaches Production*

### Increment 4: Integrate Stories With The Canvas Explorer

**Outcome:** a person tests a screen against its scenarios from the explorer, and changes stories from the canvas or story-ui with the map updating, both ending in the same story code.

**Slicing notes:** `.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md`, the features Check Screens Against Their Scenarios and Change Stories From Canvas And Story UI. Test results first (slices A, B, C; D only if C proves too limited), and comment to story code first. Decide the source of truth before any story change (story code is recommended, which changes `map-mirrors-drawio` and needs a CDR). Playing UI steps and rearranging stories inside the canvas need Sync Design Canvas With Production's mounted screens.

**Stories in this increment:**

- *Package End-To-End Results With The Canvas*
- *Mark Each Explorer Scenario Passed Or Failed*
- *Label Stale Test Results*
- *Run A Scenario's Thens On The Canvas*
- *Play A Story's UI Steps On A Screen*
- *Check Screen Logic Against Scenarios From A Command*
- *Give Each Map Card A Stable Node Id*
- *Comment On A Story Card*
- *Change Story Code From A Canvas Comment*
- *Refresh Map Artboard From A Data File*
- *Save Story Map To Story Files*
- *Comment On A Story In Story UI*
- *Place Notes On The Story Map*
- *Rearrange Stories Inside The Canvas*

### Increment 5: Repair Guidance From Mistakes

**Outcome:** a violation is traced back to the guidance that let it happen and that guidance is fixed, a mistake and its correction are captured as a regression example, and a failed example becomes a new named rule, so each error makes every later run better.

**Slicing notes:** the person, 2026-11-11: repair is not built yet, so it is taken out of Built Today and planned as its own increment.

**Stories in this increment:**

- *Repair Guidance Behind Violation*
- *Improve Guidance From Mistake*
- *Add Rule From Failed Example*

### Increment 6: Enter Commands Faster

**Outcome:** a person types a CDD command with the actions, practices, fidelities and formats offered as they go.

**Slicing notes:** mod-ideas build order 2, command entry and autocomplete; Choose Format sits here because a format is one of the command's parameters.

**Stories in this increment:**

- *Autocomplete CDD Commands*
- *Show Command Argument Hints*
- *Display Action Before Fidelity Dots*
- *Add Comment To Sent Command*
- *Announce CDD Tool Calls*

### Increment 7: Check Clean Engineering On The Model

**Outcome:** validating at the Clean Engineering model or code fidelity measures each function, class and module, keeps each measure as a fact on its node, and reports what is past a limit in the same validation report; the same validation finds the problems that only show across files, as graph rules where the graph can answer and as one AI-judged pass over the codebase where it cannot.

**Slicing notes:** `.sessions/_backlog/measure-code-on-the-model.md` and `.sessions/_backlog/check-clean-engineering-across-files.md`, merged on 2026-11-11 at the person's request; the always-on metrics gate was removed on 2026-11-09, and its measuring moves into the practice, which also replaces the cross-file passes agents ran by hand.

**Stories in this increment:**

- *Record Code Metrics As Node Facts*
- *Check Code Metrics Against Clean Engineering Limits*
- *Report Unused Class For Deletion*
- *Report Runtime Dependency That Should Be Owned*
- *Report Disconnected Class*
- *Report One-Class Package*
- *Judge Clean Engineering Rules Across Files*

### Increment 8: Fully Integrated App Flow

**Outcome:** the chat bar, the board, the Story UI editor with its story explorer, and the Graph app work on one ticket together, and violations are read from the latest graph that generate refreshes.

**Slicing notes:** requested on 2026-11-06: validation inside generate, the chat bar and board joined with the Story UI editor, the story explorer in the Story UI app framed by design canvas screens, and each app tested on a real session.

**Stories in this increment:**

- *Refresh Graph After Generate*
- *Judge Rules During Generate*
- *Fix Graph Violations*
- *Validate Fidelity On Demand*
- *Check Graph Rules When An Artifact Changes*
- *Read Fidelity Violations From Latest Graph*
- *Generate And Judge Fidelity From Board*
- *Fix Graph Violations From Board*
- *Read Session Violations From Latest Graph*
- *Generate And Judge Fidelity From Chat Bar*
- *Fix Graph Violations From Chat Bar*
- *Open Board Side Panel From Chat Bar*
- *Sync Chat Bar With Board Selection*
- *Keep Chosen Formats Across Actions In A Fidelity*
- *Start Ticket Session From Increment*
- *Show Increment Ticket In Story UI*
- *Test Story Explorer On Session Story Map*
- *Switch Story Map To Screen Frames View*
- *Show Screen Frame Under Each Story*
- *Mark Story Without A Screen*
- *Open Story Explorer From Screen Frame*
- *Open The Explorer At A Story, Scenario And Step*
- *Collapse And Reset The Story Tree*
- *Play The Next Story*
- *Hide And Show The Story Panel*
- *Return To Story UI Map*
- *Keep The Selected Story In View*
- *Copy A Request To Open A Story In Its File*
- *Pick An Outline Scenario's Example*
- *Show Design Canvas Screen As Explorer Frame*
- *Choose The Screen For A Step*
- *Join A Step Without A Screen To The Next Step*
- *Show A Screenshot When No Screen Runs*
- *Keep Each Screen's Own Stylesheets*
- *Invoke Story Explorer In Session Context*
- *Open UX Design In Claude Design*
- *Remove Older Versions When Keeping A Release*
- *Test Knowledge Graph Explorer On Session Files*
- *Display Drawio File As Diagram*

### Increment 9: Review Work In Board Files

**Outcome:** a person reads a ticket's context and changed files in a proper viewer, comments on them to the chat, and reads clean reports.

**Slicing notes:** board-enhancements "Files" and the report fixes under "Actions".

**Stories in this increment:**

- *List Ticket Context Files*
- *Open Session Files From Details*
- *View Files In Rich Viewer*
- *Comment On File Selection*
- *Show AI Changes As Diff*

### Increment 10: Customize Board Workflow

**Outcome:** a team shapes the board's stages, policies, steps and test strategy to its own way of working.

**Slicing notes:** board-enhancements "Workflow Enhancements"; it changes the board's own structure, so it comes after the board is finished.

**Stories in this increment:**

- *Customize Workflow Stages*
- *Write Column Policies*
- *Collapse Column Policies*
- *Configure Todo List*
- *Run Work Type Flows*
- *Display Board From Customized Workflow*
- *Move Ticket Along Customized Workflow*
- *Approve Ticket Out Of Human Review Column*
- *Track Ticket Status Through Workflow*
- *Show Stage Practices From Customized Workflow*
- *Choose Testing Strategy*
- *Toggle Sub Agents*

### Increment 11: Author Story Maps

**Outcome:** the Story UI editor gets its own remaining stories: dashboard, nested lanes, the node inspector, save history, real-time sessions and AI story changes.

**Slicing notes:** requested on 2026-11-06: the Author Story Maps stories move out of Fully Integrated App Flow into an increment of their own, right after it.

**Stories in this increment:**

- *Test Story UI Editor On Session Story Map*
- *Pick Story Map From Dashboard*
- *Browse Nested SubEpic Lanes*
- *Inspect Selected Node Fields*
- *Show And Hide Scenarios And Examples*
- *Record One Save Event Per Save*
- *Browse Save History*
- *Recover Workspace View State*
- *Join Real-Time Story Map Session*
- *Reconcile Concurrent View State Changes*
- *Open AI Chat Panel*
- *Request AI Story Change*
- *Review Proposed Map Changes*
- *Apply AI Change To Story Map*

### Increment 12: Guard Work And Recover Fast

**Outcome:** a person sees at once when cdd is down, fixes it from where they are, and the agent is stopped before it breaks a rule.

**Slicing notes:** mod-ideas build order 1, server health band and rule guards: small, and they fix problems that already happened.

**Stories in this increment:**

- *Refuse Forbidden Edits*
- *Warn When Work Outruns Fidelity*
- *Catch Banned Words In Markdown*
- *Warn On Branch Mismatch*
- *Open Board Server Health Panel*
- *Reconnect CDD Server From Board*
- *Reinstall CDD Tools From Board*
- *Reload Everything With One Button*
- *Update CDD From Chat Bar*
- *Restart Parts From Chat Bar*
- *Open App From Health Panel*

### Increment 13: Show Board Quickly

**Outcome:** `board.show` stops repeating git checks, guidance parsing and session file reads, so the board and the chat bar answer faster and `space/kanban/kanban_tools_spec.py` runs in under 60 s.

**Slicing notes:** `.sessions/_backlog/show-board-quickly.md`. Technical stories in shared modules (`space/repo`, `harness/guidance`, `harness/installation`), so reinstall after; small, and can go in at any point.

**Stories in this increment:**

- *Check Ticket Branches Once Per Board Build*
- *Cache Practice Guidance By File And Change Time*
- *Read Session File Once Per Board Build*

### Increment 14: Bring Chat Bar Level With Board

**Outcome:** everything a person can do to one session on the board, they can do from the chat bar.

**Slicing notes:** Requested on 2026-11-06: each channel does what the other does for one session.

**Stories in this increment:**

- *Move Session To Previous Stage*
- *Mark Session Done In Stage*
- *Choose Session Practices*
- *Open Fidelity Help*
- *Choose Session Folders From Chat Bar*
- *Fix Violations From Chat Bar*
- *Add Backlog Item From Chat Bar*
- *Commit Work From Chat Bar*
- *Push Work From Chat Bar*
- *Pull Latest From Chat Bar*

### Increment 15: Draw Linked Models On The Canvas

**Outcome:** from any story a person reaches its screen, its classes and its bounded context by clicking, and back, and every diagram matches its drawio layout.

**Slicing notes:** `.sessions/_backlog/draw-linked-models-on-the-canvas.md`; depends on nothing, so it can run beside Sync Design Canvas With Production and Integrate Stories With The Canvas Explorer. The bounded context map is the first slice.

**Stories in this increment:**

- *Draw Arrows From Drawio Waypoints*
- *Draw Bounded Context Map As An Artboard*
- *Draw Domain Model As An Artboard*
- *Draw Module Class Models As Artboards*
- *Follow Links From A Context To Its Models*
- *See The Classes A Scenario Touches*
- *See The Stories That Exercise A Class*
- *Mark Model Nodes That Fail Rules*

### Increment 16: Suggest The Next Step

**Outcome:** the chat proposes the next command, and captures handoffs, corrections and decisions.

**Slicing notes:** mod-ideas build order 3, next-step suggestions.

**Stories in this increment:**

- *Suggest Next Command*
- *Write Handoff When Session Ends*
- *Display Latest Session Handoff*
- *Offer Correction Log Entry*
- *Offer Decision Record*

### Increment 17: Maybe Later

**Outcome:** work set aside for now because it is complicated and not needed yet; picked up only when asked.

**Slicing notes:** the person, 2026-11-11, on the story explorer: "this is complicated, I don't want to do it; add to backlog 'maybe later' ticket". Taken out of Maintain Tickets On Board.

**Stories in this increment:**

- *Nest Child Branch And Session*
