# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Person --> Open Board

#### Scenario: Open the board on a project

*Given* the [board](../../../kanban-model.md#board) of project cdd-board-surface-fixture shows 9 [tickets](../../../kanban-model.md#ticket--card)
*And* its [session](../../../kanban-model.md#session) checkout-flow, titled Checkout flow, is the active [ticket](../../../kanban-model.md#ticket--card)
*When* the Person opens the session board at http://127.0.0.1:8778
*Then* the header reads cdd-board-surface-fixture · 9 tickets · active: Checkout flow
*And* the session board reads the [board](../../../kanban-model.md#board) again every two seconds

#### Scenario: Find the board from a chat

*Given* a Claude Code chat has the cdd-board mod loaded
*When* the Person asks the chat where the session board is
*Then* the chat answers The board is at http://127.0.0.1:8778, and starts the board first when nothing answers on that port
