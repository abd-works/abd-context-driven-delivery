# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Person --> Arrange Side Panel

#### Scenario: Set a panel's width

*Given* the files panel is open beside the board
*When* the Person widens the files panel to 700 pixels
*Then* the files panel is 700 pixels wide
*When* the Person narrows the files panel to 10 pixels
*Then* the files panel stops at 360 pixels

#### Scenario: Expand one panel at a time

*Given* the report panel and the files panel are open
*And* the report panel is expanded
*When* the Person expands the files panel
*Then* the files panel takes the board's width less the other open panels
*And* the report panel is no longer expanded

#### Scenario: Close a side panel

*Given* checkout-flow's validation report panel is open
*When* the Person closes the report panel
*Then* no side panel is open

#### Scenario: Keep the columns' width when a panel opens

*Given* the [board](../../../kanban-model.md#board) shows its five [columns](../../../kanban-model.md#column) at their own width
*When* the Person opens checkout-flow's files list
*Then* the columns keep their width and scroll sideways beside the files panel
