# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Board App --> Display Board

#### Scenario: Draw the columns of the board

*Given* a [board](../../../kanban-model.md#board) with the Stories, DDD, and UX [practices](../../../kanban-model.md#practiceguidance) chosen
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* the [columns](../../../kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, and Complete, in that order
*And* each [stage](../../../kanban-model.md#stage--column) shows an In progress list and a Done list
*And* the Discovery [stage](../../../kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate, Validate, and Review

#### Scenario: Say the cdd server is not connected

*Given* the cdd server behind the session board is not connected
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* a band across the top of the page says The cdd server is not connected
*And* the header offers Update

#### Scenario: Show a failing tool in a toast

*Given* the [session](../../../kanban-model.md#session) folder .sessions/broken holds a session.json that is not JSON
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* a toast says cdd board.show failed: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
*But* no band says the cdd server is lost

#### Scenario: Update the board and cdd to the latest code

*Given* the band says the cdd server is lost
*When* the Person presses Update
*Then* the session board server gets the latest code, rebuilds the page, and pins the cdd server to it
*And* the session board server restarts on the new code
*And* the page loads again from the restarted server

#### Scenario: Say which update step failed

*Given* the latest code cannot be pulled
*When* the Person presses Update
*Then* a toast says Update failed at get latest, with the reason
*And* the page and the session board server keep running as they were

#### Scenario: Keep the newer board when an older read answers late

*Given* the [ticket](../../../kanban-model.md#ticket--card) move-me is In progress in the Discovery [stage](../../../kanban-model.md#stage--column)
*And* a read of the [board](../../../kanban-model.md#board) is still waiting for its answer
*And* another chat has moved move-me into Discovery's Done
*When* the session board reads the [board](../../../kanban-model.md#board) again
*Then* the session board shows move-me in Discovery's Done even though the older read answered last

#### Scenario: Announce a ticket that moved

*Given* the session board shows the [ticket](../../../kanban-model.md#ticket--card) move-me In progress in Discovery
*When* another chat moves move-me into Discovery's Done
*Then* a toast says Move me moved to Discovery · Done

#### Scenario: Announce a fidelity done

*Given* the [ticket](../../../kanban-model.md#ticket--card) billing-report has the story_map [fidelity](../../../kanban-model.md#fidelityguidance) generated and validated with no violations
*When* a review of stories-story-map is written to billing-report's [session log](../../../kanban-model.md#session)
*Then* a toast says stories-story-map done on billing-report
