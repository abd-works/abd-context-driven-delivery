# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Board App --> Display Ticket Card

#### Scenario: Show every work session as a ticket

*Given* the [repository](../../../kanban-model.md#repo)'s .sessions/ holds the work [sessions](../../../kanban-model.md#session) pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* the Discovery [stage](../../../kanban-model.md#stage--column) shows the [tickets](../../../kanban-model.md#ticket--card) Pet visits and Sign up
*And* the Complete [column](../../../kanban-model.md#column) shows Browse pets
*But* main and old-spike are not on the board

#### Scenario: Place a ticket in the stage of its latest move

*Given* the [session log](../../../kanban-model.md#session) of the [ticket](../../../kanban-model.md#ticket--card) second-spec ends with move Specification
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* second-spec shows In progress in the Specification [stage](../../../kanban-model.md#stage--column)

#### Scenario: Place a ticket with no move in the earliest stage it has work in

*Given* the [session log](../../../kanban-model.md#session) of the [ticket](../../../kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux
*But* it has no move line
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../kanban-model.md#stage--column)

#### Scenario: Draw the card's title, age, and fidelity segments

*Given* the [ticket](../../../kanban-model.md#ticket--card) checkout-flow, titled Checkout flow, last worked on at 2026-11-01T10:00:00Z
*And* its story_map [fidelity](../../../kanban-model.md#fidelityguidance) has violations and its other Discovery fidelities are not started
*When* the session board draws checkout-flow's [card](../../../kanban-model.md#card) 13 hours later
*Then* the card reads Checkout flow and 13 hours ago
*And* it shows one segment for each enabled Discovery fidelity, the story_map segment in the violations colour and the rest dim
*And* a violations link on the card opens the report

#### Scenario: Outline the active ticket

*Given* the [repository](../../../kanban-model.md#repo)'s .sessions/session.json names checkout-flow as the open [session](../../../kanban-model.md#session)
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* the checkout-flow [card](../../../kanban-model.md#card) has a thick orange outline
*And* the header names Checkout flow as active

#### Scenario: Name the active ticket on the chat's status line

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), in Discovery, with violations on stories-story_map
*When* a turn in a chat with the cdd-board mod loaded ends
*Then* the chat's status line reads checkout-flow · Discovery · next: stories-story_map · 1 with violations
