# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Close Active Session

#### Scenario: Close the active session from its card

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), In progress in Discovery, with a chat connected
*When* the Person closes checkout-flow's session from its card
*Then* the chat is sent /space:session:close-session
*And* checkout-flow stays In progress in Discovery

#### Scenario: Complete the active ticket with its work committed

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), on its own branch
*When* the Person moves checkout-flow into Complete
*Then* a dialog headed Close session Checkout flow offers commit and push, chosen
*When* the Person confirms
*Then* checkout-flow shows in Complete and is selected
*And* a toast says Checkout flow: committed, pushed · Session Checkout flow closed
*And* main is the active ticket

#### Scenario: Complete a ticket that has no branch of its own

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*But* it has no branch of its own
*When* the Person moves checkout-flow into Complete and confirms
*Then* checkout-flow shows in Complete
*And* its folder is in .sessions/_complete/checkout-flow
*But* nothing is committed
