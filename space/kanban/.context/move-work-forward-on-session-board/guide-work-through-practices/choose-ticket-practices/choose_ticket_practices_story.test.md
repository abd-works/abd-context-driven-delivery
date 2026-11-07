# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Person --> Choose Ticket Practices

#### Scenario: Turn a practice off for a ticket

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) working on every [practice](../../../kanban-model.md#practiceguidance)
*And* its bounded_context tile is open
*When* the Person turns DDD off for checkout-flow
*Then* a toast says DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json
*And* the bounded_context tile closes and fades
*And* the card shows no DDD segment

#### Scenario: Finish a stage on the practices left on

*Given* pet-visits has generated, validated, and reviewed the story_map [fidelity](../../../kanban-model.md#fidelityguidance)
*And* every practice but Stories is turned off for pet-visits
*When* the session board reads pet-visits
*Then* pet-visits shows in Discovery's Done

#### Scenario: Keep practice switches off on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../kanban-model.md#ticket--card)
*When* the session board draws billing-report's practices
*Then* each practice switch is off until Active session only is turned off
