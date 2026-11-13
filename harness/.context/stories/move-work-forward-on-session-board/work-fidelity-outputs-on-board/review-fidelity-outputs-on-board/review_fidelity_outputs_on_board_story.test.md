---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Review Fidelity Outputs On Board

## Story: List Ticket Files

#### Scenario: List a fidelity's files with whether each exists

*Given* checkout-flow's story map .context/story-map.md is there and .context/story-map.drawio is not
*When* the Person lists checkout-flow's story_map files
*Then* the files panel shows a .context/story-map.md tab, as there
*But* no file of another fidelity shows

#### Scenario: List every file of the fidelity, changed or not

*Given* the [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits works on its own branch pet-visits
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

## Story: Browse Ticket Files By Practice

Evidence:
- Observed (`file-views-view.tsx`): the folder mode of the files panel groups files under their folders. That grouping is replaced.
- Intended (the person, 2026-11-11, `.sessions/review-work-in-board-files/review-work-in-board-files.md`): files are grouped by the roots of the knowledge graph, such as each practice. A click selects a file.
- Requested (the person, 2026-11-12): "these are just filters on left; all files are shown in tabs above grouped by practice colored by practice color", then "just put the filter toggles on the top, it will waste less space". So the filters sit along the top with the tabs, and nothing is on the left.
- Requested (the person, 2026-11-12): "list a shortened form/image of each practice top to bottom on left side, filters preset when clicking files button in chat ui, user can toggle them; top has file tabs like now but colored to practice".

None of this is built. That the chat bar's Files button presets the filters to the practice the chat bar is on is my reading of "filters preset", and needs confirming.

#### Scenario: Show the practice filters and every file as a tab along the top

*Given* the [session](../../../../../../space/kanban/.context/kanban-model.md#session) of [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow works on Stories and BDD
*And* its Stories files are stories/story-map.md and stories/checkout_story.test.md, and its BDD file is src/order_spec.py
*When* the Person browses checkout-flow's files
*Then* the top of the files panel shows a Stories filter and a BDD filter, each by its short form
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

The files panel shows the practice filters and then every file as a tab, both along the top, each tab in its practice's color (the person, 2026-11-12; see Browse Ticket Files By Practice). The tabs never go away, so closing one needs no scenario.

#### Scenario: Open one tab per format, colored by its practice, generated or not

*Given* checkout-flow's story map is .context/story-map.md and .context/story-map.drawio is not there
*When* the Person views checkout-flow's story_map files
*Then* the tabs along the top show .context/story-map.md and .context/story-map.drawio, both in Stories' color
*And* the .context/story-map.md tab shows # Check Out Order
*And* the drawio tab says it is not generated yet

## Story: Open Session Files From Details

The latest handoff opening from the details is Display Latest Handoff's (`steer_ticket_sessions_story.test.md`), so it is not repeated here.

Evidence: `space/kanban/app/src/kanban/ticket/details-view.tsx:37-55` (checked 2026-11-12) shows the session folder, the stage's files and the latest handoff, each opening from its link. The workpath link opens the root chooser. That it should open the workpath folder is intended, from `.sessions/_backlog/review-work-in-board-files.md` ("session information -> link to file or folders"), and was not observed.

#### Scenario: Open the session folder from the session button

Requested (the person, 2026-11-12: "make this super simple - clicking on a session button when the button is in session mode eg no expand no main; opens the file view on .session/session"). Today the board's details open the session folder from the ticket's name (`details-view.tsx:38`), and the chat bar's session name toggles the session card (`chat-bar-view.tsx:103`).

*Given* the [session](../../../../../../space/kanban/.context/kanban-model.md#session) button shows [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's own session
*But* not main, and not expanded
*When* the Person opens checkout-flow's session from its session button
*Then* the file view shows .sessions/checkout-flow

#### Scenario: Open the workpath folder from the details

*Given* the session of ticket checkout-flow works in the workpath harness/.context
*When* the Person opens checkout-flow's workpath from its details
*Then* the files panel lists the entries of harness/.context
*But* the root chooser does not open
