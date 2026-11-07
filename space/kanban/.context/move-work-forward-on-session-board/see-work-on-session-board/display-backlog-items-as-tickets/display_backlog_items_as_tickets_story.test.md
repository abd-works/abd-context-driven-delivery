# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Board App --> Display Backlog Items As Tickets

#### Scenario: Show each idea file in the Backlog

*Given* the [repository](../../../kanban-model.md#repo)'s .sessions/_backlog/ holds search-the-catalog.md headed Search the catalog with the text An idea.
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* the Backlog [column](../../../kanban-model.md#column) shows the [backlog item](../../../kanban-model.md#backlogitem--card) Search the catalog
*And* selecting it shows its text An idea. in the details
*And* its last activity is when search-the-catalog.md last changed

#### Scenario: Show a ticket kept in the Backlog under its own file

*Given* the Backlog folder holds the folder gift-cards with its session log and gift-cards.md headed Gift cards
*And* gift-cards.md holds the text Sell them at the till.
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* the Backlog [column](../../../kanban-model.md#column) shows one [backlog item](../../../kanban-model.md#backlogitem--card) Gift cards with the text Sell them at the till.
*But* no [stage](../../../kanban-model.md#stage--column) shows a [ticket](../../../kanban-model.md#ticket--card) for gift-cards

#### Scenario: Name an item that has no heading by its file name

*Given* the Backlog folder holds returns-and-refunds.md with no # heading
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* the Backlog [column](../../../kanban-model.md#column) shows the [backlog item](../../../kanban-model.md#backlogitem--card) Returns and refunds
