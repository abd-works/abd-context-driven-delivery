# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Add Backlog Item

#### Scenario: Add an idea to the Backlog

*Given* the Backlog [column](../../../kanban-model.md#column) has no [backlog item](../../../kanban-model.md#backlogitem--card) titled Gift cards
*When* the Person adds the backlog item Gift cards with the text Sell gift cards.
*Then* the Backlog shows Gift cards with the text Sell gift cards.
*And* Gift cards is selected and the form is closed
*And* a toast says Gift cards added to Backlog

#### Scenario: Keep Add off with no title

*Given* the new backlog item form is open
*But* the Person has typed no title
*When* the Person tries to add the item
*Then* Add stays off
*And* no [backlog item](../../../kanban-model.md#backlogitem--card) is written

#### Scenario: Start a backlog item in a chosen folder

*Given* the [backlog item](../../../kanban-model.md#backlogitem--card) Gift cards is in the Backlog
*And* the [repository](../../../kanban-model.md#repo) has the folders src/billing and src/visits
*When* the Person starts Gift cards
*Then* the roots dialog lists the top folders of the repository
*And* Gift cards is still in the Backlog
*When* the Person chooses src/visits as its root
*Then* the [ticket](../../../kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits
*And* the roots dialog stays open on gift-cards so its practices' roots can be set
*And* a toast says Gift cards started in Discovery

#### Scenario: Keep the idea file with the new ticket

*Given* the [backlog item](../../../kanban-model.md#backlogitem--card) Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md
*When* the Person starts Returns and refunds on the whole repository
*Then* the [ticket](../../../kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery
*And* its session folder holds returns-and-refunds.md, text and all
*And* its session log names the item's file
*But* the Backlog no longer shows Returns and refunds

#### Scenario: Bring a ticket back from the Backlog with its work

*Given* the [ticket](../../../kanban-model.md#ticket--card) sign-up was moved back out of Discovery and waits in the Backlog as the [backlog item](../../../kanban-model.md#backlogitem--card) Sign up
*And* its folder .sessions/_backlog/sign-up/ keeps its session log
*When* the Person starts Sign up
*Then* sign-up is back on the board with its session log and session.json
*But* no new ticket is opened
