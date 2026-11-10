# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Board App --> Display Latest Handoff

#### Scenario: Show the latest handoff

*Given* checkout-flow's [session](../../../kanban-model.md#session) folder holds handoff-20261101T120000.md and an earlier handoff
*When* the Person selects checkout-flow
*Then* the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md
*When* the Person opens the handoff
*Then* the files panel shows the handoff in a tab with its text # Handoff

#### Scenario: Say a ticket has no handoff

*Given* billing-report's [session](../../../kanban-model.md#session) folder holds no handoff
*When* the Person selects billing-report
*Then* the details say No handoff yet
