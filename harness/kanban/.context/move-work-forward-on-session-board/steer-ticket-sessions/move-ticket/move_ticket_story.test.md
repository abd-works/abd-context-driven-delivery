# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Move Ticket

#### Scenario: Move a ticket on to the next column

*Given* the [ticket](../../../kanban-model.md#ticket--card) ready-to-move is in Discovery's Done
*When* the Person moves ready-to-move on
*Then* ready-to-move is In progress in Specification and selected
*And* its session log ends with move Specification

#### Scenario: Drag a ticket into a stage's Done whatever its work

*Given* the [ticket](../../../kanban-model.md#ticket--card) move-me is In progress in Discovery with nothing done
*When* the Person moves move-me into Implementation's Done
*Then* move-me shows in Implementation's Done and is selected

#### Scenario: Move a ticket back to the previous column

*Given* the [ticket](../../../kanban-model.md#ticket--card) second-spec is In progress in Specification
*When* the Person moves second-spec back
*Then* second-spec shows in Discovery's Done

#### Scenario: Move a ticket into the Backlog with its work

*Given* the [ticket](../../../kanban-model.md#ticket--card) back-to-backlog is In progress in Discovery with its story map generated
*When* the Person moves back-to-backlog into the Backlog
*Then* the Backlog shows the [backlog item](../../../kanban-model.md#backlogitem--card) Back to backlog and it is selected
*And* a toast says Back to backlog moved to Backlog
*But* no stage shows back-to-backlog

#### Scenario: Close a ticket moved on past Implementation

*Given* the [ticket](../../../kanban-model.md#ticket--card) almost-shipped is in Implementation's Done
*And* almost-shipped is not the active ticket
*When* the Person moves almost-shipped on into Complete
*Then* almost-shipped shows in Complete
*And* its folder is in .sessions/_complete/almost-shipped

#### Scenario: Reopen a ticket moved back out of Complete

*Given* the closed [ticket](../../../kanban-model.md#ticket--card) shipped-work is in Complete
*When* the Person moves shipped-work back
*Then* shipped-work shows in Implementation's Done
*And* its folder is back in .sessions/shipped-work

#### Scenario: Refuse a move into a column that is not a stage

*Given* the [ticket](../../../kanban-model.md#ticket--card) billing-report is In progress in Discovery
*And* billing-report is not the active ticket
*When* the Person tries to move billing-report into Complete
*Then* Complete does not take billing-report
*And* billing-report stays In progress in Discovery
