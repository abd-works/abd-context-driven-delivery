# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Person --> Restrict Actions To Active Session

#### Scenario: Lock tickets that are not the active session

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*When* the session board draws billing-report's card and tiles
*Then* billing-report's Run next, Run, practice switches, Split, and Handoff are off
*And* billing-report's Run next says Activate this session to run its next step
*And* checkout-flow's actions stay on

#### Scenario: Keep information and moves open on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../kanban-model.md#ticket--card)
*When* the Person opens billing-report's files
*Then* the files panel lists billing-report's files
*When* the Person moves billing-report to Specification
*Then* billing-report moves to Specification
*And* Activate stays on for billing-report

#### Scenario: Unlock every ticket

*Given* Active session only is on
*When* the Person turns Active session only off
*Then* billing-report's actions are on like the active ticket's
