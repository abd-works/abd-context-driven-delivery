# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Archive Ticket

#### Scenario: Archive a ticket off the board

*Given* the [ticket](../../../kanban-model.md#ticket--card) pet-visits is In progress in Discovery with its story map generated
*When* the Person archives pet-visits
*Then* no [column](../../../kanban-model.md#column) shows pet-visits
*And* its folder is in .sessions/_archive/pet-visits

#### Scenario: Refuse to archive a ticket the board does not have

*Given* the [board](../../../kanban-model.md#board) shows no [ticket](../../../kanban-model.md#ticket--card) named no-such-ticket
*When* the Person archives no-such-ticket
*Then* the board says no ticket named 'no-such-ticket' on the board
*But* nothing is moved to .sessions/_archive
