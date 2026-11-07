# (E) Move Work Forward On Session Board
## (E) See Work On Session Board
### (S) Person --> Set Stage WIP Limit

#### Scenario: Set a stage's limit

*Given* the Discovery [stage](../../../kanban-model.md#stage--column) has the limit 3
*When* the Person sets Discovery's limit to 4
*Then* Discovery shows the limit 4
*And* the limit is still 4 when the board is read again

#### Scenario: Give every stage a limit of 3 until a person sets one

*Given* the [repository](../../../kanban-model.md#repo) has no .sessions/_board.json
*When* the session board reads the [board](../../../kanban-model.md#board)
*Then* Discovery, Specification, and Implementation each show the limit 3

#### Scenario: Show a stage over its limit

*Given* the Discovery [stage](../../../kanban-model.md#stage--column) holds the [tickets](../../../kanban-model.md#ticket--card) billing-report, move-me, and back-to-backlog
*When* the Person sets Discovery's limit to 2
*Then* Discovery's count shows in red, over its limit

#### Scenario: Change nothing for a limit that is not a whole number

*Given* the Discovery [stage](../../../kanban-model.md#stage--column) has the limit 3
*When* the Person types many as Discovery's limit
*Then* Discovery still shows the limit 3
*But* no limit is saved
