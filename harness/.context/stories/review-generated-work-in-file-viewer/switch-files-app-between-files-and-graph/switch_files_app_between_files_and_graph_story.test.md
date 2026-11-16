---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Switch Files App Between Files And Graph

### Domain terms

- ++Files app++ — the page beside the chat that lists the files a link names and shows the open ones in the source view (`harness/files_app/`).
- ++file bar++ — the Files app's side bar: the listed files as a list or in their folders today, and the session's graph in the graph view.
- ++graph view++ — the file bar showing the practice trees of the session's graph, holding only the nodes of the files the file list would show.
- ++guidance selection++ — the stages, practices and format groups the session has selected, which the Files app's buttons and the chat bar's dots and chips show (`Session.guidance_selection`).
- ++node++ — a class, operation, story or other element the session's graph reads from a file, with the lines it covers.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

> Evidence: every scenario here is Intended (requested 2026-11-15). The Files app on release-2 has the file list, its filters, one open file and the session graph's folds; it has no graph view yet.

## Examples

### checkout-flow files

| file | practice | format | changed on the branch |
| --- | --- | --- | --- |
| ++story map++ harness/.context/stories/story-map.md | Stories | markdown | yes |
| ++ticket code++ space/kanban/ticket.py | Clean Engineering | code | yes |
| ++board code++ space/kanban/board.py | Clean Engineering | code | no |
| ++information architecture++ harness/.context/information-architecture.drawio | UX | diagram | no |

### checkout-flow nodes

| node | type | file | lines |
| --- | --- | --- | --- |
| ++Ticket++ | class | ticket.py | 106 to 670 |
| ++Ticket.activate++ | operation | ticket.py | 460 to 465 |
| ++Ticket.close++ | operation | ticket.py | 538 to 555 |
| ++Board++ | class | board.py | 104 to 397 |
| ++Board.reread++ | operation | board.py | 286 to 289 |
| ++Delete Ticket++ | story | story-map.md | 315 to 319 |

## Story: Switch Files App To Graph View

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "the actual file viewer is going to have a toggle that can switch from folder files and graph" |

#### Scenario: The graph view shows the practice trees of the listed files

*Given* the Files app lists checkout-flow's Stories and Clean Engineering files  
*When* the Person switches the file bar to the graph view  
*Then* the file bar shows the Stories and Clean Engineering practice trees, each collapsed  
  *And* the open file stays open in the source view

#### Scenario: Switching back shows the files again

*Given* the Files app shows checkout-flow's graph  
*When* the Person switches the file bar back to the files  
*Then* the file bar lists checkout-flow's files as a list or in folders, as it showed them before

## Story: Filter Graph Like The File List

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "graph filtered like file filter is" |
| `files-page.ts` `filesShown`, `file-bar.ts` `entries` | the filters the file list applies today |

#### Scenario: A practice turned off leaves the graph view

*Given* the Files app shows checkout-flow's graph with Stories and Clean Engineering on  
*When* the Person turns Clean Engineering off  
*Then* the graph view holds only the Stories tree  
  *And* the file list, switched back, lists only story-map.md

#### Scenario: The Changed button keeps only the nodes of changed files

*Given* the Files app shows checkout-flow's graph with Clean Engineering on  
*When* the Person turns the Changed button on  
*Then* the Clean Engineering tree holds Ticket and its operations  
  *But* not Board, since board.py is unchanged on the branch

#### Scenario: The chat bar's selected dots narrow the graph

*Given* the Files app shows checkout-flow's graph with Stories and Clean Engineering on  
*When* the Person selects only the Stories dot on the chat bar  
*Then* the graph view holds only the Stories tree

## Story: Open Several Files From Graph Nodes

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "except for you're now selecting file(s), eg more than one file opens" |

#### Scenario: Selecting a node opens its file

*Given* the Files app shows checkout-flow's graph  
  *But* no file is open  
*When* the Person selects Ticket.activate  
*Then* ticket.py opens in the source view at lines 460 to 465

#### Scenario: Selecting nodes in two files opens both files

*Given* the Files app shows checkout-flow's graph, with Ticket.activate selected and ticket.py open  
*When* the Person also selects Board.reread  
*Then* ticket.py and board.py are both open in the source view

## Story: Fold Open Files To Selected Nodes

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "expand and collapse in file viewer based on the nodes in the graph" |
| `session.file` folds | the folds the session's graph places in a file today |

#### Scenario: An open file unfolds only the selected node

*Given* Ticket.activate is selected and ticket.py is open  
*When* the Files app shows ticket.py  
*Then* the lines of Ticket.activate are unfolded  
  *And* Ticket.close and Ticket's other operations are folded

#### Scenario: Selecting another node in the same file unfolds it too

*Given* Ticket.activate is selected and unfolded in ticket.py  
*When* the Person also selects Ticket.close  
*Then* Ticket.activate and Ticket.close are both unfolded  
  *And* Ticket's other operations stay folded
