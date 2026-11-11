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
*Then* the files panel lists .context/story-map.md as there
*But* no file of another fidelity is listed

#### Scenario: List only what the ticket's branch changed

*Given* the [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits works on the whole [repository](../../../../../../space/kanban/.context/kanban-model.md#repo) on its own branch pet-visits
*And* the repository holds src/theirs_spec.py and its branch added src/mine_spec.py
*When* the Person lists pet-visits' bdd behavior files
*Then* the files panel lists src/mine_spec.py
*But* src/theirs_spec.py is not listed

#### Scenario: Say in a toast when the list cannot be read

*Given* the board shows no ticket named no-such-ticket
*When* the Person lists no-such-ticket's story_map files
*Then* a toast says cdd fidelity-progress.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board
*But* no panel opens

## Story: Browse Ticket Folder

#### Scenario: Group a stage's files under their folders

*Given* checkout-flow's Discovery files are tests/a.md, tests/deep/b.md, and src/c.ts
*When* the Person browses checkout-flow's Discovery files
*Then* the files panel groups a.md and deep/b.md under tests/ and c.ts under src/

#### Scenario: Browse the ticket's session folder

*Given* checkout-flow's [session](../../../../../../space/kanban/.context/kanban-model.md#session) folder holds its log and validation-reports/stories-story-map-20261101T100000.md
*When* the Person browses checkout-flow's session folder
*Then* the files panel lists .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md under its folder

## Story: View Fidelity Files

#### Scenario: Open one tab per format, generated or not

*Given* checkout-flow's story map is .context/story-map.md and .context/story-map.drawio is not there
*When* the Person views checkout-flow's story_map files
*Then* the files panel shows the tabs .context/story-map.md and .context/story-map.drawio
*And* the .context/story-map.md tab shows # Check Out Order
*And* the drawio tab says it is not generated yet

#### Scenario: Go back to the list when the last tab closes

*Given* the tabs .context/story-map.md and .context/story-map.drawio are open
*When* the Person closes both tabs
*Then* the files panel shows the list

#### Scenario: Refuse a file outside the repository

*Given* checkout-flow's repository is the project folder
*When* a file outside the repository is asked for
*Then* the board says ../secrets.txt is not a file in this repository

## Story: Review Fidelity

#### Scenario: Review a fidelity after a clean validate

*Given* billing-report's story map is generated and its latest validate passed with no graph-rule
*When* the Person reviews story_map on billing-report
*Then* billing-report's session log ends with review stories story_map
*And* the story_map tile marks Review ✓ and the fidelity is done
*And* a toast says stories-story-map done on billing-report

#### Scenario: Keep Review off until Validate is clean

*Given* billing-report's story map has no file
*But* nothing is recorded on it
*When* the session board draws the story_map bar
*Then* review is off

#### Scenario: Ignore a review recorded before a clean validate

*Given* pet-visits' session log has generate, then review, then validate Stories story_map
*When* the session board reads pet-visits
*Then* the story_map tile marks Review ○

#### Scenario: Refuse a fidelity the ticket does not have

*Given* billing-report's story map passed validate
*When* the Person reviews stories-no_such_fidelity
*Then* the board says no fidelity named stories-no_such_fidelity on ticket billing-report
*But* no review line is written for stories-story-map

#### Scenario: Complete a stage's work

*Given* pet-visits has every Discovery fidelity generated, validated, and reviewed
*When* the session board reads pet-visits
*Then* pet-visits waits in Discovery's Done
*And* it has no next step
