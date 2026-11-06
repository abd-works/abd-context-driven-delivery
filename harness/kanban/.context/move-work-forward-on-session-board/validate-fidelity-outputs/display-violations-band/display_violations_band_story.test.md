# (E) Move Work Forward On Session Board
## (E) Validate Fidelity Outputs
### (S) Board App --> Display Violations Band

#### Scenario: Show the active ticket's violations in a band

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) with violations on stories-story-map
*When* the session board reads the board
*Then* a band across the page top names checkout-flow's violations

#### Scenario: Show no band when the active ticket is clean

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) with no violations
*When* the session board reads the board
*Then* no violations band shows
