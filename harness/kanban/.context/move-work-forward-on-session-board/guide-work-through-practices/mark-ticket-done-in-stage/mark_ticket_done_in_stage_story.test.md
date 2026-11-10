# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Person --> Mark Ticket Done In Stage

#### Scenario: Mark a ticket done in its stage

*Given* the [ticket](../../../kanban-model.md#ticket--card) pet-visits is In progress in Discovery with only its story map generated
*When* the Person marks pet-visits done in Discovery
*Then* pet-visits shows in Discovery's Done
*And* it has no next step
*And* a toast says Pet visits moved to Discovery · Done

#### Scenario: Mark a ticket back in progress

*Given* the ticket ready-to-move is in Discovery's Done
*When* the Person moves ready-to-move back into Discovery's In progress
*Then* ready-to-move shows In progress in Discovery
