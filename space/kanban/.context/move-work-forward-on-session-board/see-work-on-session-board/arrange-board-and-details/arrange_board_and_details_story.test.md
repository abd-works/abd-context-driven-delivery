# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Person --> Arrange Board And Details

#### Scenario: Give the board more height

*Given* the page is 900 pixels high
*When* the Person resizes the board to 300 pixels
*Then* the [board](../../../kanban-model.md#board) region is 300 pixels high and the details take the rest

#### Scenario: Keep both regions open

*Given* the page is 900 pixels high
*When* the Person resizes the board to 10 pixels
*Then* the [board](../../../kanban-model.md#board) region stays 160 pixels high
*When* the Person resizes the board to 5000 pixels
*Then* the board region stops at 650 pixels, so the details stay open

#### Scenario: Expand one region and show both again

*Given* the board and the details share the page
*When* the Person expands the board
*Then* the [board](../../../kanban-model.md#board) takes the whole page
*When* the Person collapses the board
*Then* the board and the details share the page again
