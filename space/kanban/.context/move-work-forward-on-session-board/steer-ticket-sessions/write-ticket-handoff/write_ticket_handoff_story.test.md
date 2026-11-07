# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Write Ticket Handoff

#### Scenario: Ask the chat to write a handoff

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) and a chat is connected
*When* the Person asks for a handoff on checkout-flow
*Then* the chat's prompt holds Write a handoff for ticket checkout-flow with /space-session-handoff-session.
*And* a toast says Queued for the prompt, for you to review

#### Scenario: Hold the handoff until the chat's turn ends

*Given* the connected chat is running a turn
*When* the Person asks for a handoff on checkout-flow
*Then* a toast says the fill goes in when this turn ends
*And* the prompt receives the text once the turn has ended

#### Scenario: Keep Handoff off with no chat

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*But* no chat is connected
*When* the session board draws checkout-flow's card
*Then* Handoff is off
*And* the header says No chat connected: load the cdd-board mod in a chat to send commands
