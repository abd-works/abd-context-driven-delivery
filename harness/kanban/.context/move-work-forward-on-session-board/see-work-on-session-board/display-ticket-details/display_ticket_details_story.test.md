# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Board App --> Display Ticket Details

#### Scenario: Show the ticket of a card pressed anywhere

*Given* the [ticket](../../../kanban-model.md#ticket--card) billing-report is In progress in Discovery with nothing recorded
*When* the Person selects billing-report's card
*Then* the details show Billing report, root whole repository, and Discovery · in progress
*And* the details say No handoff yet and Next: stories-story_map, generate
*And* the details show a tile for each enabled [fidelity](../../../kanban-model.md#fidelityguidance) with its [fidelity progress](../../../kanban-model.md#fidelityprogress)

#### Scenario: Show the active ticket with no card pressed

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*But* no card is pressed
*When* the session board draws the details
*Then* the details show Checkout flow

#### Scenario: Show the ticket worked on last when none is active

*Given* no [ticket](../../../kanban-model.md#ticket--card) is active
*And* billing-report has the latest line in its session log, at 2026-11-02T10:00:00Z
*When* the session board draws the details
*Then* the details show Billing report

#### Scenario: Name a split ticket by the ticket it came from

*Given* the [ticket](../../../kanban-model.md#ticket--card) child has scope story and parent epic in its session.json
*When* the Person selects child's card
*Then* the details read child · story of epic

#### Scenario: Say another session must be activated to act on a locked ticket

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*When* the Person selects billing-report's card
*Then* the details say Activate this session to run actions

#### Scenario: Expand one ticket's card at a time

*Given* the card of the [ticket](../../../kanban-model.md#ticket--card) checkout-flow is expanded over the board
*When* the Person expands billing-report's card
*Then* billing-report's card is expanded with a tile for each enabled Discovery fidelity
*And* checkout-flow's card is closed

#### Scenario: Open a card on the fidelity of a pressed segment

*Given* billing-report's card shows a segment for the story_map [fidelity](../../../kanban-model.md#fidelityguidance)
*When* the Person opens billing-report's story_map segment
*Then* billing-report's card is expanded with the story_map tile's action bar open
