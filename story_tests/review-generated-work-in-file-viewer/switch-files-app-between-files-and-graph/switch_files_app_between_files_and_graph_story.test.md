---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Switch Files App Between Files And Graph

### Domain terms

- ++Files app++ — the page beside the chat that lists the files a link names and shows the open ones in the source view (`harness/files_app/`).
- ++file bar++ — the Files app's side bar: the listed files as a list or in their folders, or the session's graph in the graph view.
- ++graph view++ — the file bar showing the practice trees of the session's graph, holding only the nodes of the files the file list would show.
- ++guidance selection++ — the stages, practices and format groups the session has selected, which the Files app's buttons and the chat bar's dots and chips show (`Session.guidance_selection`).
- ++node++ — a class, operation, story or other element the session's graph reads from a file, with the lines it covers.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

> Evidence: every scenario here was requested on 2026-11-15 and is Built on the file-manager branch (the Stories root, folder and scroll scenarios on 2026-11-15, from "why is story graph empty", "module would show multiple files" and "we should scroll to line of member if it's below the fold"), held by `harness/files_app/app/files/files-graph.spec.ts` (the page), `story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch-files-app-between-files-and-graph.story.shared.py` replayed by its `.story.domain.spec.py` and `.story.server.spec.py` (the session's answers), and `space/session/session_graph_spec.py` (the edges of the session's graph operations); none is walked in the browser yet.

## Examples

### checkout-flow files

| file | practice | format | changed on the branch |
| --- | --- | --- | --- |
| ++story map++ .context/story-map.md | Stories | markdown | yes |
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
| ++Clean Engineering++ | practice root | none | none |

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

#### Scenario: The Stories tree holds the project's story map

*Given* the project's .context holds checkout-flow's story map  
  *And* an old story map is left in harness/.context/stories, from before maps moved to the project's .context  
*When* the Person switches the file bar to the graph view  
*Then* the Stories tree holds Delete Ticket, read from .context/story-map.md  
  *And* holds none of the old story map's epics

#### Scenario: The Stories tree holds a story listed only by its story test in code

*Given* the Files app lists only the code formats, so of checkout-flow's Stories files only Delete Ticket's and Restore Ticket's story tests  
*When* the Person switches the file bar to the graph view  
*Then* the Stories tree holds Manage Tickets, Remove Tickets and Delete Ticket, read from the folders the story test sits in under story_tests  
  *And* Delete Ticket holds the scenario its story test holds  
  *And* Restore Ticket, which has a story test but is not on the markdown map yet

#### Scenario: A story map listed in markdown and drawio is read once, from its markdown

*Given* the Files app lists checkout-flow's story map in markdown and in drawio  
*When* the Person switches the file bar to the graph view  
*Then* the Stories tree holds each story once, read from the markdown: when one thing is written in several formats, code is read before markdown and markdown before a diagram

#### Scenario: The Stories tree holds a story's scenarios listed in markdown

*Given* the Files app lists only the markdown formats: checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person switches the file bar to the graph view  
*Then* Delete Ticket holds its scenario and its steps from the scenarios file

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
*When* the Person narrows the files to those the branch changed  
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

#### Scenario: Selecting a folder's node opens every listed file below it

*Given* the Files app shows checkout-flow's graph  
*When* the Person selects the Clean Engineering root, which no file's lines hold  
*Then* ticket.py opens in the source view  
  *And* board.py opens below it at lines 104 to 397, the lines Board covers

#### Scenario: Selecting a step opens its scenarios file at the step's line

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the Given step a ticket on the board  
*Then* the scenarios file opens at the Given's own line

#### Scenario: Selecting a scenario in a Python story test spans its whole function

Requested by the person on 2026-11-16: a scenario or step selected in code opened on its decorator's line alone.

*Given* the Files app shows the Stories tree of Remove Tickets' shared story test  
*When* the Person selects the scenario a ticket is deleted  
*Then* the shared story test opens at lines 7 to 15, its decorator through the last line of its function

#### Scenario: Selecting a step in a Python story test spans its whole function

*Given* the Files app shows the Stories tree of Remove Tickets' shared story test  
*When* the Person selects the Given step a ticket on the board  
*Then* the shared story test opens at lines 9 to 11, the Given's decorator through its function

#### Scenario: Selecting a story in a Python story test spans its scenarios

Requested by the person on 2026-11-16: a story or sub-epic selected in code opened on one line, so it looked like the wrong file.

*Given* the Files app shows the Stories tree of Remove Tickets' shared story test  
*When* the Person selects the story Delete Ticket  
*Then* the shared story test opens at lines 7 to 22, its first scenario through its last

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

#### Scenario: The page scrolls to a node below the fold

*Given* ticket.py is open at its first line  
*When* the Person selects Ticket.close, at line 538  
*Then* the page scrolls so line 538 shows near the top of the window, so it is plain where the page went

#### Scenario: Selecting a node marks its lines

Requested by the person on 2026-11-16.

*Given* ticket.py is open at its first line  
*When* the Person selects Ticket.close, which covers lines 538 to 560  
*Then* the source view marks lines 538 to 560 as selected  
  *And* a node that covers the whole file marks no lines

## Story: Open Story Scenarios Across Files

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-16 | "story map md story has scenario file", the story's scenarios not opened beside it |

#### Scenario: Selecting a story map story opens its scenarios file too

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the story Delete Ticket  
*Then* the story map opens at line 5, Delete Ticket's line  
  *And* the scenarios file opens below it at lines 5 to 9, the scenario a ticket is deleted

#### Scenario: Selecting a markdown scenario spans its heading through its last step

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the scenario a ticket is deleted  
*Then* the scenarios file opens at lines 5 to 9, its heading through its Then

## Story: Open Linked Sections In Place

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-16 | "should have callout to expand and see story scenarios" |
| user request, 2026-11-16 | "scenario has domain references in its terms, callout to markdown class model if it exists" |

#### Scenario: A story map story opens its scenarios in place

*Given* checkout-flow's story map links Delete Ticket to the Story: Delete Ticket heading of its scenarios  
*When* the Person views the story map  
*Then* line 5 carries a callout to the scenarios file's lines 3 to 9, holding Delete Ticket and its scenario

#### Scenario: A scenario's domain term opens its class in the markdown model

*Given* Delete Ticket's Then links the board to the Board section of the kanban's class model  
*When* the Person views the scenarios file  
*Then* line 9 carries a callout to the model's lines 3 to 5, the Board section

#### Scenario: A link to a heading no file holds carries no callout

*Given* a markdown file links to a heading its target does not have, and to a file not there  
*When* the Person views it  
*Then* neither line carries a callout

#### Scenario: A callout opens and closes from its mark beside the line

*Given* the Files app shows the story map, its callouts closed  
*When* the Person presses the callout mark beside Delete Ticket  
*Then* Delete Ticket's scenarios show under its line, with the file they come from  
  *And* a second press closes them again
