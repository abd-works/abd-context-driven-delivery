# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Person --> Send Action To Stage Practices

#### Scenario: Sketch every fidelity of a stage in one command

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) in Discovery and a chat is connected
*And* the Discovery stage head's action bar is open
*When* the Person runs sketch from the Discovery stage head
*Then* the chat receives the command /actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior

#### Scenario: Keep two stage heads open at once

*Given* billing-report's Discovery stage head is pressed open
*When* the Person presses the Specification stage head
*Then* both stage bars are open
