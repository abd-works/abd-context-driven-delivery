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

#### Scenario: A story listed only by its story map holds its scenarios

Requested 2026-11-16: "scenarios not rendering in graph". The Files app listed file-manager's story map but not its unchanged scenarios files, so every story arrived with no scenarios.

*Given* the Files app lists only checkout-flow's story map, .context/story-map.md  
  *But* not Delete Ticket's scenarios file under story_tests  
*When* the Person switches the file bar to the graph view  
*Then* Delete Ticket holds its scenario and its steps, read from its scenarios file

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

#### Scenario: Collapse one open file, then every open file

Requested by the person on 2026-11-16: each of several open files collapses and expands on its own, with Collapse all and Expand all. Only the page shows it: `harness/files_app/app/files/open-files.spec.ts`.

*Given* ticket.py and board.py are both open in the source view, with story-map.md below them  
*When* the Person collapses board.py  
*Then* board.py shows only its name, and ticket.py and story-map.md stay whole  
*When* the Person presses Collapse all  
*Then* every open file shows only its name  
*When* the Person presses Expand all  
*Then* every open file shows whole again

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

#### Scenario: A code file opens with its classes open and their members folded

Requested 2026-11-16 by the person: "Default on open for code is classes opened and members collapsed." Only the page folds: `harness/files_app/app/files/code-outline.spec.ts`.

*Given* no node is selected, and ticket.py holds the class Ticket with its operations activate and close  
*When* the Person views ticket.py  
*Then* Ticket is unfolded  
  *And* Ticket.activate, Ticket.close and Ticket's other operations are folded to their first lines  
  *And* a TypeScript file opens the same way, files-graph.ts with the class FilesGraph unfolded and its operations folded  
*When* the Person then selects Ticket.close  
*Then* the lines of Ticket.close are unfolded, as a selected node's are

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

#### Scenario: A selected node is marked by one orange line beside its lines

Requested 2026-11-16 by the person: "The selected node on text viewer - make it a single orange range line to the side; no shading of text required." Only the page marks lines: `harness/files_app/app/files/file-marks.spec.ts`.

*Given* ticket.py is open at its first line  
*When* the Person selects Ticket.close, which covers lines 538 to 560  
*Then* one orange line runs beside lines 538 to 560, in the margin between the line numbers and the text  
  *And* the text of lines 538 to 560 is not shaded

## Story: Open Story Scenarios Across Files

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-16 | "story map md story has scenario file", the story's scenarios not opened beside it |

#### Scenario: Selecting a story map story opens its scenarios file too

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the story Delete Ticket  
*Then* the story map opens at line 5, Delete Ticket's line  
  *And* the scenarios file opens below it at lines 3 to 9, from Delete Ticket's own heading through its scenario a ticket is deleted

#### Scenario: Selecting a story map sub-epic opens its scenarios file from its heading

Reported by the person on 2026-11-16: a selected sub-epic's lines in its scenarios file began at its first scenario, below its own heading.

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the sub-epic Remove Tickets  
*Then* the scenarios file opens from its Sub-epic: Remove Tickets heading, on line 1, through its last scenario

#### Scenario: Selecting a markdown scenario spans its heading through its last step

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the scenario a ticket is deleted  
*Then* the scenarios file opens at lines 5 to 9, its heading through its Then

#### Scenario: Selecting a markdown step spans its own line, whatever its prose holds

Reported by the person on 2026-11-16: a scenario selected in markdown ran past its last step, because a step's apostrophe (*checkout-flow's*) was read as code's quote.

*Given* the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios  
*When* the Person selects the When step the Person deletes the ticket's card  
*Then* the scenarios file opens at the When's own line alone

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

Changed by the person on 2026-11-16 ("only shade once; on expand, hide the callout label and show the content; on collapse, bring it back"): the label that names the section shows while it is closed, and the section alone, shaded once, while it is open.

*Given* the Files app shows the story map, its callouts closed, Delete Ticket's line labelled with the scenarios it opens  
*When* the Person presses the callout mark beside Delete Ticket  
*Then* Delete Ticket's scenarios show under its line, shaded once, and the label is hidden  
  *And* a second press closes them again and brings the label back

## Story: Follow Story Steps To Code

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-16 | "when the Person opens ..." shows observes and invokes "but they do not reach the Python code; this has been tested for TypeScript but not Python before" |
| user request, 2026-11-16 | "it's not clear what class callouts are for in the tests. Are they story to code relationships? They should be placed next to steps if they are step relationships." |
| probe of the file-manager worktree, 2026-11-16 | a Python step invoked the operations it called on an object (`session_of(world).graph_branch(...)` reached Session.graph_branch) but none of the functions it called by name (`session_of`, `node_id_of`), which the graph holds as operations of their module |
| main session's validation report, 2026-11-16 (`stories-acceptance-tests-20261116T173912.md`) | 11 When steps of the serve-cdd-code-in-lanes story tests, written as `with when("..."):` blocks calling `self.lanes.for_project(...)`, were reported with no invokes relationship to Operation or Property; the main session has Clean Engineering off, so its graph holds no operation for any step to invoke |

#### Scenario: A step in a Python story test invokes the functions and operations it calls

*Given* the Files app shows the Stories tree of Delete Ticket's Python shared story test, whose Given calls the function ticket_on_board and whose When calls Ticket.delete  
*When* the Person opens the Given and the When  
*Then* the Given shows an invokes group holding ticket_on_board  
  *And* the When shows an invokes group holding delete

#### Scenario: A story test's callouts sit on the step that invokes them

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose docstring names the class Ticket  
*When* the Person views the shared story test  
*Then* the When's line carries a callout to Ticket.delete, the operation it invokes  
  *And* the Given's line a callout to ticket_on_board  
  *But* the docstring's line carries none

#### Scenario: A step in a with-block Python story test invokes the operation its block calls

*Given* the Files app shows the Stories tree of Archive Ticket's Python story test, whose `with when` block calls Ticket.delete on an object it holds  
*When* the Person opens the When  
*Then* the When shows an invokes group holding delete

#### Scenario: A step's invokes are not judged while the session reads no Clean Engineering

*Given* checkout-flow works with Clean Engineering off, and Archive Ticket's Python story test's `with when` block calls Ticket.delete  
*When* the Person views the story test with the rules the whole working copy breaks  
*Then* the When carries no conforms-to-schema finding, since no operation is read for it to invoke
