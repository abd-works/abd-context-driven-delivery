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

##### Example: another project

*Given* the Files app is opened on ++another project++ and shows checkout-flow's graph, whose class Ticket defines delete  
*When* the Person selects Ticket.delete  
*Then* that project's ticket.py opens in the source view, not the CDD checkout's

#### Scenario: Selecting a node whose file has moved says so

Found on 2026-11-19 (exploratory testing, pixel-08): a node whose file was moved or deleted after the graph was read answered no lines, as a node read from no lines does, so the selection did nothing and the file of the node selected before stayed on show with no word that this node's source was gone. Acceptance test: `space/session/session_graph_spec.py`.

*Given* the graph view shows the class Ticket, read from *ticket.py*, and *ticket.py* was moved on disk since the graph was read
*When* the Person selects Ticket
*Then* the Files app says Ticket did not open because nothing is at *ticket.py*, naming the file
*And* the node selected before stays selected, with its own file on show

#### Scenario: Selecting a node whose file changed since the graph read it opens the node's lines as the file is now

Round 3 of exploratory testing (r3-lens-07): a file a chat changed after the graph was read kept its nodes' old line numbers, so the lines of another member were marked in the new text and the selected one stayed folded. Acceptance test: `space/session/session_graph_spec.py`.

*Given* the graph view shows Ticket.close, read from lines 5 to 6 of *ticket.py*, and two lines were added at the top of *ticket.py* since the graph was read
*When* the Person selects Ticket.close
*Then* *ticket.py* opens at lines 7 to 8, where Ticket.close is now

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

#### Scenario: Selecting a package's node opens every listed file below it

Round 3 of exploratory testing (r3-lens-01): a package, a module or an aggregate is read from a folder, and the refusal for a file moved since the graph was read took the folder for a file that is gone, so every folder node failed to open. Acceptance test: `space/session/session_graph_spec.py`.

*Given* the Files app shows checkout-flow's graph, whose package kanban is the folder holding ticket.py and board.py  
*When* the Person selects the package kanban  
*Then* ticket.py and board.py both open, each at the lines of the class it holds  
  *But* a package whose folder was moved since the graph was read is refused, naming the folder

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

#### Scenario: Selecting a scenario opens only its own lines, not the examples module its example comes from

Seen by the person on 2026-11-17: selecting a scenario marked lines far outside it.

*Given* the Files app shows the Stories tree of Delete Ticket's story test, whose Then observes CHECKOUT_TICKET from the examples module  
*When* the Person selects the scenario a ticket on the board is deleted  
*Then* only the story test opens, at lines 7 to 19, its decorator through its Then

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

#### Scenario: Selecting a step in a Python story test unfolds its function

Requested 2026-11-16 by the person: "when selecting a step in code mode expand the step if it's a function". A step spans its decorator and the function under it, and only the folds around its first line opened, so the function stayed folded under its decorator. Only the page folds: `harness/files_app/app/files/source-folding.spec.ts`.

*Given* Delete Ticket's Python shared story test is open in the code view, its scenario's step functions folded  
*When* the Person selects the step given a ticket on the board, its decorator `@s.given("a ticket on the board")` on line 9 and its function `def _(world):` on line 10  
*Then* the function on line 10 is unfolded, showing its body  
  *And* the scenario's other step functions stay folded

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

#### Scenario: Selecting a markdown story's second scenario spans its own lines, not the examples the story declares

Round 3 of exploratory testing (r3-lens-04): the examples of a story's Examples table sit under every scenario that can use them, and a selected scenario was widened with their lines, so the second scenario was marked from the first scenario's heading and stayed folded.

*Given* the Files app shows the Stories tree of Reopen Ticket's scenarios, whose Examples table both of its scenarios use  
*When* the Person selects the scenario Refuse a ticket still open  
*Then* the scenarios file opens at lines 20 to 24, its heading through its Then  
  *But* not from the first scenario or the Examples table, which the scenario uses and does not hold

#### Scenario: A markdown When is not asked to invoke code before a realization names it

Requested 2026-11-16 by the person: steps in markdown scenario files "would only have [invokes] if realizations are generated", so require invokes only on code-backed steps; linking markdown steps through realizations is in the Backlog.

*Given* checkout-flow's Delete Ticket scenarios in markdown, whose When the Person deletes the ticket's card names no code, and Clean Engineering read  
*When* the Person views the scenarios file with the rules the whole working copy breaks  
*Then* the When carries no finding that it invokes nothing, since only a step backed by code can name the code it invokes

#### Scenario: A When in a story test that calls none of the code it tests is flagged

*Given* Delete Ticket's Python shared story test, whose When the Person looks up the deleted ticket calls only the file's own helper ticket_left  
*When* the Person views the shared story test with its own rules  
*Then* that When carries the code-steps-invoke-code finding  
  *But* the When that calls Ticket.delete carries none

#### Scenario: A story test outside the session's folder shows the rules it breaks

Requested 2026-11-16 by the person: "fix the session to include relevant test epics and stories". file-manager works in harness, its story tests sit in the project's story_tests, and a story test read on its own for its rules read nothing: no folds, no steps, no findings.

*Given* checkout-flow works in the folder space, and Delete Ticket's Python shared story test, under story_tests outside it, has a When that calls only the file's own helper ticket_left  
*When* the Person views the shared story test with its own rules  
*Then* the story test's steps are read, and that When carries the code-steps-invoke-code finding

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

#### Scenario: A link to a whole file opens the file in place

Round 3 of exploratory testing (r3-pixel-04): a story map links each story to its scenario file, naming no heading, and that link opened nothing.

*Given* Delete Ticket's Given links the ticket to space/kanban/ticket.py, naming no heading
*When* the Person views the scenarios file
*Then* line 7 carries a callout to ticket.py's lines 1 to 9, the whole file

#### Scenario: A link to a heading that holds a link opens the heading's section

A heading's anchor is made from the words it shows, so a link the heading holds counts as its words alone.

*Given* a story map's heading for Delete Ticket holds a link to its scenarios, and a markdown file links to that heading
*When* the Person views the linking file
*Then* line 1 carries a callout to the map's lines 3 to 5, the heading's section

#### Scenario: A link to a heading or a file not there says what is not there

Changed in round 3 of exploratory testing (r3-pixel-04): such a line carried no callout, so a wrong anchor looked like a line with no link.

*Given* a markdown file links to a heading its target does not have, and to a file not there
*When* the Person views it
*Then* line 3's callout says the kanban model has no heading no-such-heading, and line 4's that nowhere/gone.md is not there

#### Scenario: A story test in code opens the domain term a step links

Round 3 of exploratory testing (r3-pixel-05): a scenario written in Python or TypeScript links its domain terms inside its steps' strings, as the markdown scenario does.

*Given* a Python story test's Given links the board to the Board section of the kanban's class model, its When calls handlers[name](event), and its last line reads # Model: with the model's path
*When* the Person views the story test
*Then* the Given's line carries a callout to the model's lines 3 to 5, the Board section
  *And* its `# Model:` line, which names the kanban's class model, carries a callout to the model's lines 1 to 9, the whole file
  *And* the call's line carries none, since code that reads as a link to no file is not one

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

#### Scenario: A step in a Python story test invokes only the code it tests, never the test's own functions

Requested 2026-11-16: "internal functions in the test don't count for invokes; you have to cross to the methods that exist in the CE part of the graph". A step listed names_in and opened_names, helpers of its own story test, as code it invokes.

*Given* the Files app shows the Stories tree of Delete Ticket's Python shared story test, whose Given calls its seed ticket_on_board, whose When calls Ticket.delete, and whose Then calls the file's own helper ticket_left  
*When* the Person opens the Given, the When and the Then  
*Then* the When shows an invokes group holding delete, Ticket's operation in Clean Engineering  
  *But* the Given and the Then show no invokes group, since the seed and the helper are the story test's own code

#### Scenario: Selecting an operation a step invokes opens just that operation

Requested 2026-11-16: selecting `data_of` in a step's invokes group, with every session file listed, answered "maximum recursion depth exceeded", because the lines were gathered through every step that invokes it and every operation those steps invoke.

*Given* the Files app shows the Stories tree of Delete Ticket's Python shared story test, its When opened to the invokes group holding delete  
*When* the Person selects delete  
*Then* ticket.py opens at lines 8 to 9, delete's own lines  
  *But* the shared story test, whose When invokes delete, does not open

#### Scenario: Selecting an example a step observes opens its definition

Requested 2026-11-16: selecting STORY_MAP in a step's observes group opened the shared story test at the first scenario that uses it, not the examples module that defines it.

*Given* the Files app shows the Stories tree of Delete Ticket's Python shared story test, whose Then observes CHECKOUT_TICKET, imported from ticket_story_examples.py  
*When* the Person selects CHECKOUT_TICKET in the Then's observes group  
*Then* ticket_story_examples.py opens at line 5, where CHECKOUT_TICKET is defined  
  *But* the shared story test, whose Then observes it, does not open

#### Scenario: A story test's callouts sit on the step that invokes them

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose docstring names the class Ticket  
*When* the Person views the shared story test  
*Then* the When's line carries a callout to Ticket.delete, the operation it invokes  
  *But* the Given's line, calling only its seed, and the docstring's line carry none

#### Scenario: A step in a with-block Python story test invokes the operation its block calls

*Given* the Files app shows the Stories tree of Archive Ticket's Python story test, whose `with when` block calls Ticket.delete on an object it holds  
*When* the Person opens the When  
*Then* the When shows an invokes group holding delete

#### Scenario: A step's invokes are not judged while the session reads no Clean Engineering

*Given* checkout-flow works with Clean Engineering off, and Archive Ticket's Python story test's `with when` block calls Ticket.delete  
*When* the Person views the story test with the rules the whole working copy breaks  
*Then* the When carries no conforms-to-schema finding, since no operation is read for it to invoke

## Story: Filter Callouts Like The Graph

### Evidence

| Source | Note |
|--------|------|
| the person, 2026-11-20 | "Which callouts show follows the file view's filters: the practices chosen and the graph's connectors." |
| the person, 2026-11-20, third wave | Which callouts a file shows is decided in Python by the same filter that narrows the knowledge graph, as `session.graph_trees` applies it with the node filter and the file list. The page sends its filter with the read of the file and draws what comes back. |
| `harness/graph/graph.py` `Filter`, `space/session/file_view_filter.py` `FileViewFilter` | the graph's filter, narrowed by the files listed and the node filter, decides each callout |
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

#### Scenario: A step keeps what it reaches in a file no practice declares

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose Then observes CHECKOUT_TICKET in ticket_story_examples.py, a file no fidelity declares
*When* the Person views the shared story test with only the story test listed
*Then* the Then's line carries CHECKOUT_TICKET
  *But* the When's line carries nothing, since ticket.py is Clean Engineering's and is not listed

#### Scenario: A read that sends no filter holds every callout

An agent, or a page that lists no session's files, reads a file without the file view's filters.

*Given* the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test
*When* an agent reads the shared story test, sending no files listed and no node filter
*Then* the When's line carries delete and the Then's line carries CHECKOUT_TICKET
