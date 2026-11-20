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

> The example ++another project++ is the Files app opened on a project other than the CDD checkout, its server started for the CDD checkout, as [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md#example-another-project) names it.

> Evidence: every scenario here is Intended (requested 2026-11-15), except Expand Practice Tree In Files App, Show Graph Load Steps In Files App's load step scenario and Open Calls Across Files In Files App, Built on the file-manager branch on 2026-11-15, not walked, and held by `harness/files_app/app/files/files-graph.spec.ts` (the page) and `story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore-graph-in-files-app.story.shared.py` replayed by its `.story.domain.spec.py` and `.story.server.spec.py` (the session's answers). Each brings in a Graph app story that is Observed in the Graph app (`.context/story-map.md`, Explore Graph In Graph App and Filter Graph In Graph App); the Files app has no graph view yet.

## Examples

### checkout-flow nodes

| node | type | practice | file |
| --- | --- | --- | --- |
| ++Ticket++ | class | Clean Engineering | space/kanban/ticket.py |
| ++Ticket.activate++ | operation | Clean Engineering | space/kanban/ticket.py |
| ++Ticket.close++ | operation | Clean Engineering | space/kanban/ticket.py |
| ++Ticket.delete++ | operation | Clean Engineering | space/kanban/ticket.py |
| ++Board.reread++ | operation | Clean Engineering | space/kanban/board.py |
| ++Delete Ticket++ | story | Stories | .context/story-map.md |

### checkout-flow relationships

| from | relationship | to |
| --- | --- | --- |
| ++Ticket.delete++ | invokes | ++Board.reread++ |

### checkout-flow overlays

| overlay | adds |
| --- | --- |
| ++LERN++ | its tier rules on each TypeScript node root, such as the Domain tier on Ticket in ticket.ts; LERN is constrained to TypeScript, so it adds nothing to a Python class such as Ticket in ticket.py (decided 2026-11-16 by the person) |

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

#### Scenario: Selecting a related node opens the related node alone, in its own file

Decided by the person on 2026-11-20 (round 3 of exploratory testing, r3-lens-08): selecting a parent shows the parent in its file, where its children can be opened in place; selecting a child, including a member under a relationship group such as invokes, shows only the child, in the child's own file. The page had opened the node that holds the group instead, so a relationship could not be followed. Browser test: `explore-graph-in-files-app.story.ui_e2e_spec.py`; the page: `harness/files_app/app/files/files-graph.spec.ts`.

*Given* Ticket.delete is selected and ticket.py is open  
*When* the Person selects Board.reread under Ticket.delete's invokes  
*Then* board.py opens at Board.reread  
  *But* ticket.py, which holds Ticket.delete, is no longer open

## Story: Filter Graph By Node Type And Connector In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "graph filtered like file filter is" |
| Graph app, Filter By Node Type, Filter By Connector, Select All Or No Filter Choices (Observed) | `Graph.filter_choices`, `Filter._on_relationship`, `FilterView.tsx` |
| person's decision, 2026-11-16 | The file list stays the one file filter. A node filter is a different filter, on the graph's nodes, and it extends the file filter rather than replacing it: both apply, the node filter only narrows the nodes of the files listed and never brings back a file the list leaves out. |
| user request, 2026-11-16 | "Collapse the graph filters by default — let users expand if they want them." |

#### Scenario: The node filter starts collapsed behind one Filters toggle

> Requested 2026-11-16, not walked.

*Given* the Person never opened the graph view's filters in this browser  
*When* the Person switches the file bar to the graph view  
*Then* the graph view shows one closed Filters toggle above the practice trees  
  *But* not the node type, connector and rule lists or the Violations switch, so the trees get the space

#### Scenario: Pressing Filters opens the node filter, and the browser remembers it

*Given* the graph view shows its Filters toggle closed  
*When* the Person presses Filters  
*Then* the node type, connector and rule lists and the Violations switch show above the trees  
  *And* the graph view opens with them shown the next time this browser opens it, until the Person presses Filters again

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

#### Scenario: A node filter narrows only the files listed

*Given* the Files app lists ticket.py but not board.py  
*When* the Person filters the graph to operations  
*Then* the Clean Engineering tree holds Ticket.activate, Ticket.close and Ticket.delete  
  *But* not Board.reread, whose file the list leaves out

#### Scenario: Changing the file list keeps the node filter

*Given* the graph is filtered to operations and the Files app lists ticket.py alone  
*When* the Person lists board.py too  
*Then* Board.reread joins the Clean Engineering tree  
  *And* the graph stays filtered to operations

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
*Then* Ticket in ticket.ts carries LERN's Domain tier rules among its rules  
  *But* Ticket in ticket.py carries none, since LERN applies only to TypeScript

#### Scenario: An overlay taken off leaves the graph view

*Given* the Files app shows checkout-flow's graph with LERN applied  
*When* the Person takes LERN off the session  
*Then* the LERN rules on Ticket in ticket.ts leave the graph view  
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

#### Scenario: A class never opens itself in place

Requested 2026-11-16 by the person: "don't code fold yourself! a class doesn't fold to itself; it folds across classes or methods". The line `class AppNotRegistered(KeyError):` opened a copy of AppNotRegistered inside AppNotRegistered. Only the page finds callouts: `harness/files_app/app/files/call-expansion.spec.ts`.

*Given* the Files app shows ticket.py, which defines the class Ticket, and the graph is read  
*When* the Person views the line `class Ticket:` and the lines of Ticket's own operations  
*Then* no line inside Ticket opens Ticket in place  
  *But* a line inside Ticket that names the class Board still opens Board

#### Scenario: A method's call to another method of its class opens in place

Requested 2026-11-16 by the person: "I can't find a single instance of code folding where it's supposed to happen, e.g. nesting methods and other classes". A Python call on `self` (`self.close()`) was skipped, and a call to a module function by its bare name (`reread_all(board)`) was not looked for.

*Given* the Files app shows ticket.py, whose Ticket.delete calls `self.close()` and the module function `reread_all(board)`, and the graph is read  
*When* the Person views Ticket.delete  
*Then* the call `self.close()` opens Ticket.close in place below it  
  *And* the call `reread_all(board)` opens the function reread_all in place below it

##### Example: another project

*Given* the Files app is opened on ++another project++ and shows that project's ticket.py, whose Ticket.delete calls `self.close()`, and that project's graph is read  
*When* the Person views Ticket.delete  
*Then* the call `self.close()` opens that project's Ticket.close in place below it, not the CDD checkout's

#### Scenario: A call inside a folded method opens in place once the method is unfolded

Requested 2026-11-16 by the person: "I can't find a single instance of code folding where it's supposed to happen". In harness/diagnostics/app.py, opened from the graph, AppServer.restart's line `if not self.stop():` opened AppServer.stop 0 px tall: opening the file folds every block, the `if` block's own body stayed folded once restart was unfolded, and Monaco gives no height to a view zone whose next line a fold hides. The page and Monaco's view zones: `harness/graph/app/app.test.tsx`; the real editor is checked by hand in the Files app.

*Given* the Files app shows ticket.py from the graph with Ticket.delete folded, and the graph is read  
*When* the Person unfolds Ticket.delete and opens the call `self.close()`, whose `if` block is still folded  
*Then* the lines of Ticket.close show in place below the call, at their full height  
  *And* the page grows by those lines, so it scrolls down to them

#### Scenario: Calls open in place only once the graph is read

*Given* the Files app lists checkout-flow's files and the graph view was never shown  
*When* the Person opens ticket.py  
*Then* its calls show as written, with no fold to open them
