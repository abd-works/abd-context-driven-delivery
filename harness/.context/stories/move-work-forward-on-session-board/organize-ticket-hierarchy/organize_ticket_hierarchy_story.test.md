---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Organize Ticket Hierarchy

## Story: Split Ticket Into Child Tickets

#### Scenario: Ask the chat to split a ticket into child tickets

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) and a chat is connected
*When* the Person splits checkout-flow into child tickets
*Then* the chat's prompt holds Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.create with parent checkout-flow for each story.
*When* the chat opens a child ticket Enter card details with parent checkout-flow
*Then* enter-card-details is In progress in Discovery
*And* its details read enter-card-details · story of checkout-flow

#### Scenario: Keep Split off where nothing can take the prompt

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* no chat is connected
*When* the session board draws checkout-flow's card
*Then* Split is off

#### Scenario: Keep Split off on a closed ticket

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) browse-pets is closed in Complete
*When* the session board draws browse-pets' card
*Then* Split is off

#### Scenario: Keep Split off on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the session board draws billing-report's card
*Then* Split is off
