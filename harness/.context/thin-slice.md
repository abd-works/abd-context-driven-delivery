---
fidelity: [discovery]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Context-Driven Delivery Framework incremental backlog

## Product / context

**Product:** the CDD framework, its Session Board and its Chat Bar, as mapped in [story-map-v2.md](story-map-v2.md).

**Slicing intent:** Increment 0 is what the code does today. The Intended and Requested stories follow the order set on 2026-11-06.

**Spine vs optional:** the increments run in the order they are built: ticket management first, then the small editor-app stories that open each app in a session, then next-step suggestions, then the fully integrated flow, then faster command entry and the board's file review. Guards, chat bar parity and workflow customizing follow, each standing on its own.

## Increments

### Increment 0: Built Today

**Outcome:** what the framework, the Session Board and the Chat Bar do now: every story whose evidence is Observed or Inferred.

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
- *Repair Guidance Behind Violation*
- *Improve Guidance From Mistake*
- *Add Rule From Failed Example*
- *Review Fidelity Output*
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
- *Move Child Ticket To Another Parent*
- *Nest Child Branch And Session*

### Increment 2: Integrate Practice Content Editor Apps

**Outcome:** the board and the chat bar open the Story UI editor, the Claude Design story explorer and the Graph app on the ticket's own scope, using what each app already does.

**Slicing notes:** requested on 2026-11-06: only the small stories that open an existing app in session context; the larger flow follows in Fully Integrated App Flow.

**Stories in this increment:**

- *Open Story UI Side Panel From Chat Bar*
- *Open Story UI On Ticket Scope*
- *Filter Knowledge Graph To Ticket Scope*
- *Filter Knowledge Graph To Ticket Practices*
- *Deploy Knowledge Graph App With Board State*
- *Refactor Knowledge Graph App To Web Domain Access*
- *Trace Story Through Artifacts*
- *Invoke Claude Design Story Explorer From Chat Bar*
- *Deploy Story UI App With Board State*
- *Refactor Story UI App To Web Domain Access*

### Increment 3: Suggest The Next Step

**Outcome:** the chat proposes the next command, and captures handoffs, corrections and decisions.

**Slicing notes:** mod-ideas build order 3, next-step suggestions.

**Stories in this increment:**

- *Suggest Next Command*
- *Write Handoff When Session Ends*
- *Display Latest Session Handoff*
- *Open Ticket Chat On Session Open*
- *Offer Correction Log Entry*
- *Offer Decision Record*

### Increment 4: Fully Integrated App Flow

**Outcome:** the chat bar, the board, the Story UI editor with its story explorer, and the Graph app work on one ticket together, and violations are read from the latest graph that generate refreshes.

**Slicing notes:** requested on 2026-11-06: validation inside generate, the chat bar and board joined with the Story UI editor, the story explorer in the Story UI app framed by design canvas screens, and each app tested on a real session.

**Stories in this increment:**

- *Refresh Graph After Generate*
- *Attach Violations To Latest Graph*
- *Judge Rules During Generate*
- *Fix Graph Violations*
- *Validate Fidelity On Demand*
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

### Increment 5: Author Story Maps

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

### Increment 6: Enter Commands Faster

**Outcome:** a person types a CDD command with the actions, practices, fidelities and formats offered as they go.

**Slicing notes:** mod-ideas build order 2, command entry and autocomplete; Choose Format sits here because a format is one of the command's parameters.

**Stories in this increment:**

- *Autocomplete CDD Commands*
- *Show Command Argument Hints*
- *Display Action Before Fidelity Dots*
- *Select Several Fidelities*
- *Choose Format*
- *Add Comment To Sent Command*
- *Announce CDD Tool Calls*

### Increment 7: Review Work In Board Files

**Outcome:** a person reads a ticket's context and changed files in a proper viewer, comments on them to the chat, and reads clean reports.

**Slicing notes:** board-enhancements "Files" and the report fixes under "Actions".

**Stories in this increment:**

- *List Ticket Context Files*
- *Open Session Files From Details*
- *View Files In Rich Viewer*
- *Comment On File Selection*
- *Show AI Changes As Diff*
- *Display Report Without Header Noise*
- *Display Report Errors In Code Fences*

### Increment 8: Guard Work And Recover Fast

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

### Increment 9: Bring Chat Bar Level With Board

**Outcome:** everything a person can do to one session on the board, they can do from the chat bar.

**Slicing notes:** Requested on 2026-11-06: each channel does what the other does for one session.

**Stories in this increment:**

- *Move Session To Previous Stage*
- *Mark Session Done In Stage*
- *Choose Session Practices*
- *Open Fidelity Help*
- *Fix Violations From Chat Bar*

### Increment 10: Customize Board Workflow

**Outcome:** a team shapes the board's stages, policies, steps and test strategy to its own way of working.

**Slicing notes:** board-enhancements "Workflow Enhancements"; it changes the board's own structure, so it comes after the board is finished.

**Stories in this increment:**

- *Customize Workflow Stages*
- *Write Column Policies*
- *Collapse Column Policies*
- *Configure Todo List*
- *Run Work Type Flows*
- *Choose Testing Strategy*
- *Toggle Sub Agents*
