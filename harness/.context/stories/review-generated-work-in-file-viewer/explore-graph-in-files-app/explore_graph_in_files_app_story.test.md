---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Explore Graph In Files App

### Domain terms

- ++graph view++ — the Files app's file bar showing the practice trees of the session's graph, holding only the nodes of the files the file list would show.
- ++practice tree++ — one practice's nodes in the graph view, nested as the Graph app nests them, each practice collapsed until opened.
- ++relationship group++ — the nodes a node relates to by one kind of edge, such as the operations an operation invokes, shown as a child of the node.
- ++overlay++ — a pattern such as LERN laid over the session's practices, adding its own nodes and rules; the session holds the overlays chosen (`ticket.choose_overlays`).
- ++load step++ — the step the session's graph is on while it loads, as the Graph app shows it (`graph/query-progress.ts`).
- ++member++ — a class, operation or property the session's graph holds, with its text, from which the source view opens a call in place, in its own file or another.

> In steps: ++example++ names a row of a table below.

> Evidence: every scenario here is Intended (requested 2026-11-15), except Expand Practice Tree In Files App, Show Graph Load Steps In Files App's load step scenario and Open Calls Across Files In Files App, Built on the file-manager branch on 2026-11-15, not walked, and held by `harness/files_app/app/files/files-graph.spec.ts` (the page) and `space/session/explore-graph-in-files-app.story.shared.py` replayed by its `.story.domain.spec.py` and `.story.server.spec.py` (the session's answers). Each brings in a Graph app story that is Observed in the Graph app (`harness/.context/stories/story-map.md`, Explore Graph In Graph App and Filter Graph In Graph App); the Files app has no graph view yet.

## Examples

### checkout-flow nodes

| node | type | practice | file |
| --- | --- | --- | --- |
| ++Ticket++ | class | Clean Engineering | space/kanban/ticket.py |
| ++Ticket.activate++ | operation | Clean Engineering | space/kanban/ticket.py |
| ++Ticket.close++ | operation | Clean Engineering | space/kanban/ticket.py |
| ++Ticket.delete++ | operation | Clean Engineering | space/kanban/ticket.py |
| ++Board.reread++ | operation | Clean Engineering | space/kanban/board.py |
| ++Delete Ticket++ | story | Stories | harness/.context/stories/story-map.md |

### checkout-flow relationships

| from | relationship | to |
| --- | --- | --- |
| ++Ticket.delete++ | invokes | ++Board.reread++ |

### checkout-flow overlays

| overlay | adds |
| --- | --- |
| ++LERN++ | its tier rules on each node root, such as the Domain tier on Ticket |

## Story: Expand Practice Tree In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do" |
| Graph app, Expand Practice Tree (Observed) | `GraphView.tsx` `TreeNode` |

#### Scenario: Each practice tree starts collapsed

*Given* the Files app lists checkout-flow's Stories and Clean Engineering files  
*When* the Person switches the file bar to the graph view  
*Then* the Stories and Clean Engineering practice trees show collapsed

#### Scenario: Opening a node shows one level of its children

*Given* the Files app shows checkout-flow's graph with the Clean Engineering tree collapsed  
*When* the Person opens Ticket  
*Then* Ticket shows its operations, such as Ticket.activate and Ticket.close  
  *But* their own children stay hidden until they are opened

#### Scenario: Each node shows the mark of its kind

*Given* the Files app shows checkout-flow's graph with Ticket opened  
*When* the Files app draws the Clean Engineering tree  
*Then* Ticket shows the Graph app's class mark  
  *And* Ticket.activate and Ticket.close show its operation mark

## Story: Follow Relationships Under Node In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do except for you're now selecting file(s)" |
| Graph app, Follow Relationships Under Node (Observed) | `graph.py` `Node.serialize` |

#### Scenario: An operation lists the operations it invokes

*Given* the Files app shows checkout-flow's graph with Ticket opened  
*When* the Person opens Ticket.delete  
*Then* Ticket.delete shows an invokes group holding Board.reread

#### Scenario: Selecting a related node opens its file beside the open one

*Given* Ticket.delete is selected and ticket.py is open  
*When* the Person selects Board.reread under Ticket.delete's invokes  
*Then* board.py opens beside ticket.py, at Board.reread

## Story: Filter Graph By Node Type And Connector In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "graph filtered like file filter is" |
| Graph app, Filter By Node Type, Filter By Connector, Select All Or No Filter Choices (Observed) | `Graph.filter_choices`, `Filter._on_relationship`, `FilterView.tsx` |

#### Scenario: Choosing a node type keeps only those nodes

*Given* the Files app shows checkout-flow's graph with Clean Engineering on  
*When* the Person filters the graph to operations  
*Then* the Clean Engineering tree holds Ticket.activate, Ticket.close, Ticket.delete and Board.reread  
  *And* the connectors and rules offered narrow to the ones operations carry

#### Scenario: Choosing a connector keeps the nodes on that edge

*Given* the Files app shows checkout-flow's graph filtered to operations  
*When* the Person filters the graph to the invokes connector  
*Then* the tree holds Ticket.delete and Board.reread  
  *But* not Ticket.activate or Ticket.close, which invoke none of the operations listed

#### Scenario: None clears a filter list

*Given* the graph is filtered to operations  
*When* the Person clears the node types with None  
*Then* the graph view holds every node of the files listed again

## Story: Apply Pattern Overlays In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do" |
| Graph app, Apply Pattern Overlays; chat bar, Choose Graph Overlays | `ticket.choose_overlays`, `overlay-choices-client.ts` |

#### Scenario: The graph view shows the overlays the session chose

*Given* checkout-flow's session has the LERN overlay chosen on the chat bar  
*When* the Person switches the file bar to the graph view  
*Then* Ticket carries LERN's Domain tier rules among its rules

#### Scenario: An overlay taken off leaves the graph view

*Given* the Files app shows checkout-flow's graph with LERN applied  
*When* the Person takes LERN off the session  
*Then* Ticket's LERN rules leave the graph view  
  *And* the chat bar's LERN chip shows off

## Story: Show Graph Load Steps In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do" |
| Graph app, Show Load Steps While Loading, Copy Load Failure For Agent (Observed) | `graph/query-progress.ts`, `server.ts` `diagnosis` |

#### Scenario: The graph view shows the step the load is on

*Given* checkout-flow's graph is not loaded yet  
*When* the Person switches the file bar to the graph view  
*Then* the graph view shows the load step the cdd server reports and how long it has run  
  *And* shows the practice trees once the load ends

#### Scenario: A failed load shows the server's reason, ready to copy for the chat

*Given* checkout-flow's graph fails to load  
*When* the Person switches the file bar to the graph view  
*Then* the graph view shows the server's reason and its traceback instead of loading forever  
  *And* offers a copy of them for the chat

## Story: Open Calls Across Files In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "inner cross file code folding doesn't seem to be working; in original graph explorer folding expansion across files" |
| Graph app, Unfold Calls And Classes In Source (Observed) | `source/call-expansion.ts` `inlineCallLayout`, given every member by `graph.source` |

#### Scenario: A call to an operation in another file opens in place

*Given* the Files app shows checkout-flow's graph and ticket.py is open  
*When* the Person opens the call to Board.reread in Ticket.delete  
*Then* the lines of Board.reread, from board.py, show in place below the call  
  *And* ticket.py stays open where it was

#### Scenario: Calls open in place only once the graph is read

*Given* the Files app lists checkout-flow's files and the graph view was never shown  
*When* the Person opens ticket.py  
*Then* its calls show as written, with no fold to open them
