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

> The example ++another project++ is the Files app opened on a project other than the CDD checkout, its server started for the CDD checkout, as [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md#example-another-project) names it.

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

##### Example: another project

*Given* the Files app is opened on ++another project++ and lists checkout-flow's Stories and Clean Engineering files  
*When* the Person switches the file bar to the graph view  
*Then* the file bar shows the Stories and Clean Engineering practice trees  
  *And* they are that project's graph, whose class Ticket holds close and delete alone, not the CDD checkout's Ticket

#### Scenario: Switching back shows the files again

*Given* the Files app shows checkout-flow's graph  
*When* the Person switches the file bar back to the files  
*Then* the file bar lists checkout-flow's files as a list or in folders, as it showed them before

## Story: Read Story Map Into Stories Tree

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

#### Scenario: A story map listed with a code story test keeps every epic of the map

Requested 2026-11-16: the Files app listed the project's story map with a code story test, and its graph view showed one epic of eleven, read from the story test alone, its stories sourced to the story test and the markdown scenarios' stories gone.

*Given* checkout-flow's story map holds Manage Tickets and Plan Releases, with Plan Releases' story Cut Release  
  *And* the Files app lists the story map with Delete Ticket's and Restore Ticket's story tests  
*When* the Person switches the file bar to the graph view  
*Then* the Stories tree holds Manage Tickets and Plan Releases, with Cut Release, read from the story map  
  *And* Delete Ticket is the story map's story, holding the scenario its story test holds  
  *And* Restore Ticket, which only its story test holds, sits under Manage Tickets and Remove Tickets, the folders its story test sits in

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

#### Scenario: Every practice turned off leaves the graph view with no tree

Round 3 of exploratory testing (r3-lens-06): with no practice on, the graph was still built, by a worker that took no practice for every practice, and the graph view showed its traceback. Acceptance tests: `space/session/session_graph_spec.py`, and with a real worker `space/session/session_graph_heavy_spec.py`.

*Given* the Files app shows checkout-flow's graph
*When* the Person turns every practice off
*Then* the graph view holds no tree, since no practice reads the files listed
  *But* shows no failure

#### Scenario: The Changed button keeps only the nodes of changed files

*Given* the Files app shows checkout-flow's graph with Clean Engineering on  
*When* the Person narrows the files to those the branch changed  
*Then* the Clean Engineering tree holds Ticket and its operations  
  *But* not Board, since board.py is unchanged on the branch

#### Scenario: The chat bar's selected dots narrow the graph

*Given* the Files app shows checkout-flow's graph with Stories and Clean Engineering on  
*When* the Person selects only the Stories dot on the chat bar  
*Then* the graph view holds only the Stories tree

## Story: Filter Callouts Like The Graph

### Evidence

| Source | Note |
|--------|------|
| the person, 2026-11-20 | "Which callouts show follows the file view's filters: the practices chosen and the graph's connectors." |
| the person, 2026-11-20, third wave | Which callouts a file shows is decided in Python by the same filter that narrows the knowledge graph, as `session.graph_trees` applies it with the node filter and the file list. The page sends its filter with the read of the file and draws what comes back. |
| `harness/graph/graph.py` `Filter`, `space/session/files/file_view_filter.py` `FileViewFilter` | the graph's filter, narrowed by the files listed and the node filter, decides each callout |
| walk of the Files app on a copy of round 3's combined project, 2026-11-20 (`round-3-fix-shots/pixel-wave3/`) | Observed: with DDD turned off the scenario's callouts into the domain model leave the rendered view and the source view, and come back with DDD on; with observes left out of the graph view's connectors the steps no longer carry the examples they observe, and carry them again once no connector is left out. |

The file view's filters are the files the page lists for the stages, practices and formats chosen, and the graph view's node filter. The page sends both with each read of a file (`session.file` `paths` and `node_filter`), and the session answers only the callouts they show. The page's part, sending them and reading the open files again when one changes: `harness/files_app/app/files/file-callouts.spec.ts`, `files-page.spec.ts`; in a real browser: `switch-files-app-between-files-and-graph.story.ui_e2e_spec.py`.

#### Scenario: A practice turned off leaves out the callouts into its files

*Given* Delete Ticket's Given links the ticket to space/kanban/ticket.py and its Then links the board to the kanban's class model, both files of Clean Engineering
*When* the Person views the scenarios file with Clean Engineering turned off, so the files listed are the story map and the scenarios
*Then* the scenarios file carries no callout, in the rendered view and the source view alike
*When* the Person turns Clean Engineering on again, so ticket.py and the class model are listed too
*Then* line 7 carries its callout into ticket.py and line 9 its callout into the class model

#### Scenario: A callout into a file no practice declares shows whatever is turned off

A note belongs to no practice, so no practice turned off can hide it.

*Given* a note, notes/reading.md, links to notes/plain.md, and no fidelity declares either
*When* the Person views notes/reading.md with every practice turned off, so no file is listed
*Then* line 1 carries its callout into notes/plain.md

#### Scenario: A link to a heading not there, in a file left out, says nothing

*Given* a markdown file of no practice links to a heading the kanban's class model does not have
*When* the Person views it with Clean Engineering turned off
*Then* the line carries no callout
  *But* with the class model listed, the line's callout says the model has no heading no-such-heading

#### Scenario: A link to a file not there says so whatever is turned off

A file that is not there is in no list of files, so no filter hides the callout that says it is missing.

*Given* a markdown file links to nowhere/gone.md, a file not there
*When* the Person views it with every practice turned off, so no file is listed
*Then* the line's callout says nowhere/gone.md is not there

#### Scenario: A read that sends no filter holds every callout

An agent, or a page that lists no session's files, reads a file without the file view's filters.

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test
*When* an agent reads the shared story test, sending no files listed and no node filter
*Then* the When's line carries delete and the Then's line carries CHECKOUT_TICKET

## Story: Filter Step Callouts By Node Filter

#### Scenario: A connector left out of the node filter leaves out what a step reaches by it

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose When invokes Ticket.delete and whose Then observes CHECKOUT_TICKET
*When* the Person views the shared story test with observes left out of the graph view's connectors
*Then* the When's line carries delete, and the Then's line carries nothing
*When* the Person leaves invokes out instead
*Then* the Then's line carries CHECKOUT_TICKET, and the When's line carries nothing

#### Scenario: A node type left out of the node filter leaves out the nodes of that type a step reaches

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose When invokes Ticket.delete, an operation, and whose Then observes CHECKOUT_TICKET, an example
*When* the Person views the shared story test with the node filter narrowed to operations
*Then* the When's line carries delete, and the Then's line carries nothing

#### Scenario: A step keeps what it reaches in the files listed with it

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose Then observes CHECKOUT_TICKET in ticket_story_examples.py, the examples file Stories declares
*When* the Person views the shared story test with the story test and its examples file listed
*Then* the Then's line carries CHECKOUT_TICKET
  *But* the When's line carries nothing, since ticket.py is Clean Engineering's and is not listed
