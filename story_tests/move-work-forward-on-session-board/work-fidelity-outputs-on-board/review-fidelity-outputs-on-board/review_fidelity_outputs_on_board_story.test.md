---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Review Fidelity Outputs On Board

Changed (2026-11-21, design proposal 24, approved by the person): the board's own files panel is gone. Every press here opens the Files app (`harness/files_app`) on what it names: a fidelity's files, the session folder, the folder the session works in, or a file at a line. The tabs, the practice filters, the changed-files filter and the viewer the scenarios below describe are the Files app's now, and its own specs prove them (`story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/`); the board's browser tier proves only the Files app's link each press opens (`review-fidelity-outputs.story.ui.spec.ts`), and the Python tiers what the cdd server lists.

## Story: List Ticket Files

#### Scenario: List a fidelity's files with whether each exists

*Given* checkout-flow's story map .context/story-map.md is there and .context/story-map.drawio is not
*When* the Person lists checkout-flow's story_map files
*Then* the Files app shows a .context/story-map.md tab, as there
*But* no file of another fidelity shows

#### Scenario: List every file of the fidelity, changed or not

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits works on its own branch pet-visits
*And* its bdd behavior files are src/theirs_spec.py and src/mine_spec.py, and its branch added src/mine_spec.py
*When* the Person lists pet-visits' bdd behavior files
*Then* the tabs show src/theirs_spec.py and src/mine_spec.py

#### Scenario: Filter the tabs to the files the ticket's branch changed

Intended (the person, 2026-11-12: "this is a filter eg a checkbox on the file viewer at the top where tabs are; you click only changed files listed"). Not built: today the list shows only the changed files, with no filter.

*Given* the tabs show pet-visits' bdd behavior files src/theirs_spec.py and src/mine_spec.py
*And* pet-visits' branch added src/mine_spec.py
*When* the Person filters the files to changed files only
*Then* the tabs show src/mine_spec.py
*But* no src/theirs_spec.py tab shows

#### Scenario: Clear the changed-files filter

*Given* the tabs show only pet-visits' changed file src/mine_spec.py
*When* the Person clears the changed-files filter
*Then* the tabs show src/theirs_spec.py and src/mine_spec.py again

#### Scenario: List only what the ticket's branch changed

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/list-ticket-files/list_ticket_files_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the [ticket](../../../.context/kanban-model.md#ticket--card) pet-visits works on the whole [repository](../../../.context/kanban-model.md#repo) on its own branch pet-visits  
  *And* the repository holds src/theirs_spec.py and its branch added src/mine_spec.py  
*When* the Person lists pet-visits' bdd behavior files  
*Then* the Files app lists src/mine_spec.py  
  *But* src/theirs_spec.py is not listed

#### Scenario: Say in a toast when the list cannot be read

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/list-ticket-files/list_ticket_files_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the board shows no ticket named no-such-ticket  
*When* the Person lists no-such-ticket's story_map files  
*Then* a toast says cdd fidelity-progress.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board  
  *But* no panel opens

## Story: Browse Ticket Files By Practice

Evidence:
- Observed (`file-views-view.tsx`): the folder mode of the Files app groups files under their folders. That grouping is replaced.
- Intended (the person, 2026-11-11, `.sessions/review-work-in-board-files/review-work-in-board-files.md`): files are grouped by the roots of the knowledge graph, such as each practice. A click selects a file.
- Requested (the person, 2026-11-12): "these are just filters on left; all files are shown in tabs above grouped by practice colored by practice color", then "just put the filter toggles on the top, it will waste less space". So the filters sit along the top with the tabs, and nothing is on the left.
- Requested (the person, 2026-11-12): "list a shortened form/image of each practice top to bottom on left side, filters preset when clicking files button in chat ui, user can toggle them; top has file tabs like now but colored to practice".

None of this is built. Confirmed (the person, 2026-11-12): the chat bar's Files button presets the filters to the practice the chat bar is on, "it works like it currently does".

#### Scenario: Show the practice filters and every file as a tab along the top

*Given* the [session](../../../../space/kanban/.context/kanban-model.md#session) of [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow works on Stories and BDD
*And* its Stories files are stories/story-map.md and stories/checkout_story.test.md, and its BDD file is src/order_spec.py
*When* the Person browses checkout-flow's files
*Then* the top of the Files app shows a Stories filter and a BDD filter, each by its short form
*And* the tabs below them show story-map.md and checkout_story.test.md together in Stories' color, then order_spec.py in BDD's color

#### Scenario: Preset the practice filters from the chat bar's Files button

*Given* the chat bar shows ticket checkout-flow at Stories scenarios
*When* the Person opens checkout-flow's files from the chat bar
*Then* the Stories filter is on, and the tabs show story-map.md and checkout_story.test.md
*But* the BDD filter is off, and no order_spec.py tab shows

#### Scenario: Turn a practice filter on

*Given* checkout-flow's files show with only the Stories filter on
*When* the Person turns the BDD filter on
*Then* an order_spec.py tab shows in BDD's color, after the Stories tabs

#### Scenario: Select a tab to view its file

*Given* the tabs show story-map.md, checkout_story.test.md and order_spec.py
*When* the Person selects the order_spec.py tab
*Then* the viewer shows src/order_spec.py

## Story: View Fidelity Files

The Files app shows the practice filters and then every file, both along the top, each tab in its practice's color (the person, 2026-11-12; see Browse Ticket Files By Practice). The tabs never go away, so closing one needs no scenario.

#### Scenario: Open one tab per format, colored by its practice, generated or not

*Given* checkout-flow's story map is .context/story-map.md and .context/story-map.drawio is not there
*When* the Person views checkout-flow's story_map files
*Then* the tabs along the top show the story map's files, .context/story-map.md, .context/story-map.drawio and .context/story-map.whiteboard, and the thin slice's, .context/thin-slice.md, .context/thin-slice.drawio and .context/thin-slice.whiteboard, all in Stories' color
*And* the .context/story-map.md tab shows # Check Out Order
*And* the drawio tab says it is not generated yet

#### Scenario: Open one tab per format, generated or not

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/view-fidelity-files/view_fidelity_files_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow's story map is .context/story-map.md and .context/story-map.drawio is not there  
*When* the Person views checkout-flow's story_map files  
*Then* the Files app shows the tabs .context/story-map.md and .context/story-map.drawio  
  *And* the .context/story-map.md tab shows # Check Out Order  
  *And* the drawio tab says it is not generated yet

#### Scenario: Go back to the list when the last tab closes

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/view-fidelity-files/view_fidelity_files_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the tabs .context/story-map.md and .context/story-map.drawio are open  
*When* the Person closes both tabs  
*Then* the Files app shows the list

#### Scenario: Refuse a file outside the repository

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/view-fidelity-files/view_fidelity_files_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow's repository is the project folder  
*When* a file outside the repository is asked for  
*Then* the board says ../secrets.txt is not a file in this repository

## Story: Open Session Files From Details

The latest handoff opening from the details is Display Latest Handoff's (`close_and_hand_off_ticket_sessions_story.test.md`), so it is not repeated here.

Evidence: `space/kanban/app/src/kanban/ticket/details-view.tsx:37-55` (checked 2026-11-12) shows the session folder, the stage's files and the latest handoff, each opening from its link. The workpath link opens the root chooser. That it should open the workpath folder is intended, from `.sessions/_backlog/review-work-in-board-files.md` ("session information -> link to file or folders"), and was not observed.

#### Scenario: Open the session folder from the session button

Requested (the person, 2026-11-12: "make this super simple - clicking on a session button when the button is in session mode eg no expand no main; opens the file view on .session/session"). Today the board's details open the session folder from the ticket's name (`details-view.tsx:38`), and the chat bar's session name toggles the session card (`chat-bar-view.tsx:103`).

*Given* the [session](../../../../space/kanban/.context/kanban-model.md#session) button shows [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's own session
*But* not main, and not expanded
*When* the Person opens checkout-flow's session from its session button
*Then* the file view shows .sessions/checkout-flow

#### Scenario: Open the workpath folder from the details

*Given* the session of ticket checkout-flow works in the workpath harness/.context
*When* the Person opens checkout-flow's workpath from its details
*Then* the Files app lists the entries of harness/.context
*But* the root chooser does not open

## Story: Browse Ticket Folder

#### Scenario: Group a stage's files under their folders

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/browse-ticket-folder/browse_ticket_folder_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow's Discovery files are tests/a.md, tests/deep/b.md, and src/c.ts  
*When* the Person browses checkout-flow's Discovery files  
*Then* the Files app groups a.md and deep/b.md under tests/ and c.ts under src/

#### Scenario: Browse the ticket's session folder

> From `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/browse-ticket-folder/browse_ticket_folder_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow's [session](../../../.context/kanban-model.md#session) folder holds its log and validation-reports/stories-story-map-20261101T100000.md  
*When* the Person browses checkout-flow's session folder  
*Then* the Files app lists .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md under its folder
