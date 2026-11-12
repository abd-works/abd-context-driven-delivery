---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Organize Ticket Hierarchy

### Domain terms

- ++parent ticket++ — a ticket other tickets name as their parent in their session.json.
- ++child ticket++ — a ticket whose session.json names a parent.
- ++pulled-out child++ — a child that moves on the board as a card of its own and still has its parent; its parent keeps a dashed row for it.

## Examples

Seed state from `space/kanban/session_board_examples.py`, which the shared stories and the screen specs seed from.

### ticket

| ticket | title | parent | text |
| --- | --- | --- | --- |
| ++checkout-flow++ | Checkout flow |  | Pay for the basket. |
| ++enter-card-details++ | Enter card details | checkout-flow |  |
| ++confirm-order++ | Confirm order | checkout-flow | Show the order and take the payment. |
| ++pet-visits++ | Pet visits |  |  |
| ++billing-report++ | Billing report |  |  |
| ++gift-cards++ | Gift cards | checkout-flow, once started under it | Sell gift cards. |

### backlog item

| backlog item | text |
| --- | --- |
| ++Gift cards++ | Sell gift cards. |

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

## Story: Add Child Ticket

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Create children: a person can also add children to a ticket by hand" |
| `harness/.context/ux/ticket-ui.drawio` | "add and remove a child" |
| `space/kanban/ticket.py:97-100`, `space/session/sessions.py:269-276` | Observed: `Ticket.create` with a parent records the parent in `session.json` and opens the ticket in Discovery |
| the person, 2026-11-11 | "user needs to drag the card outside the parent"; "alt drag … create an orphaned ticket … no longer a child"; "drag to adds to parent and removes from board" |

The realizations name the operations these scenarios need. Built (2026-11-11): the plus on a ticket card opens a title field, and Enter calls `ticket.add_child`; dropping a ticket on another card calls `ticket.reassign_parent`.

#### Scenario: Add a child ticket by hand

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is In progress in Discovery
*But* checkout-flow has no child tickets
*When* the Person adds the child ticket Enter card details to checkout-flow

```realization
Board.ticket("checkout-flow")
  <- checkout-flow
checkout-flow.add_child("Enter card details")
  -> self.session.open_child("Enter card details", scope="story")
  <- enter-card-details In progress in Discovery, its parent checkout-flow
```

*Then* the ticket enter-card-details is In progress in Discovery with the parent checkout-flow
*And* checkout-flow's card holds enter-card-details (Display Child Tickets In Parent)

#### Scenario: Drag a ticket onto a parent

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery with no parent
*And* the ticket checkout-flow is In progress in Discovery
*When* the Person makes pet-visits a child of checkout-flow

```realization
Board.ticket("pet-visits")
  <- pet-visits
Board.ticket("checkout-flow")
  <- checkout-flow
pet-visits.reassign_parent(checkout-flow)
  -> self.session.set_parent(checkout-flow.session)
  <- pet-visits inside checkout-flow
```

*Then* checkout-flow's card holds pet-visits
*And* no column shows pet-visits as a card of its own

## Story: Display Child Tickets In Parent

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "a parent ticket holds its child tickets stacked inside it. The parent's title sits small, above the children." |
| `harness/.context/ux/ticket-ui.drawio` | a pulled-out child keeps a dashed row in its parent |
| `space/kanban/app/src/kanban/ticket/ticket-client.tsx:97-98` | Observed: a child's card names its scope and parent, such as story of checkout-flow, and sits in its column like any other ticket |
| the person, 2026-11-11 | a stacked child names no stage: "its state is state of parent"; "hover tooltip should show ticket text" |

#### Scenario: Stack a parent's children inside its card

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is in Discovery
*And* its child tickets enter-card-details and confirm-order are in Discovery
*When* the [board](../../../../../space/kanban/.context/kanban-model.md#board) shows Discovery
*Then* checkout-flow's card holds enter-card-details and confirm-order stacked inside it
*And* checkout-flow's title sits small above them
*And* neither enter-card-details nor confirm-order shows as a card of its own in Discovery
*And* neither enter-card-details' row nor confirm-order's names a stage of its own

#### Scenario: Keep a dashed row for a child pulled out of its parent

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is in Discovery
*And* its child ticket enter-card-details was pulled out of it and is in Specification
*When* the [board](../../../../../space/kanban/.context/kanban-model.md#board) shows checkout-flow
*Then* checkout-flow's card holds a dashed row for enter-card-details

#### Scenario: Show a child's text when the pointer rests on it

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow holds its child ticket confirm-order
*And* confirm-order's text is Show the order and take the payment.
*When* the Person rests the pointer on confirm-order in checkout-flow's card
*Then* confirm-order's tooltip shows Show the order and take the payment.

## Story: Expand Parent Ticket

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "expand and collapse a parent to see its children" |
| `harness/.context/ux/ticket-ui.drawio` | collapsed: + N children; expanded: - N children above the child rows |

#### Scenario: Expand a parent to show its children

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is collapsed with the child tickets enter-card-details and confirm-order
*And* checkout-flow's card reads + 2 children
*When* the Person expands checkout-flow
*Then* checkout-flow's card shows enter-card-details and confirm-order
*And* checkout-flow's card reads - 2 children

#### Scenario: Collapse a parent to its own card

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is expanded to show enter-card-details and confirm-order
*When* the Person collapses checkout-flow
*Then* checkout-flow's card shows no child rows
*And* checkout-flow's card reads + 2 children

## Story: Detach Child Ticket

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "pull a child out of its parent so it moves on its own"; "a child pulled out of its parent becomes a ticket of its own beside it" |
| `harness/.context/ux/ticket-ui.drawio` | "pull out of parent; and then drag and then move like regular ticket; remembers parent"; the pulled-out card reads parent.Child |
| the person, 2026-11-11 | "user needs to drag the card outside the parent"; "alt drag … create an orphaned ticket … no longer a child"; "drag to adds to parent and removes from board" |

The realizations name the operations these scenarios need. `Ticket.pull_out` is built in Python (2026-11-11); the board's drag of a child out of its parent's card is built with its screen story (2026-11-12).

#### Scenario: Pull a child out of its parent

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow holds its child ticket enter-card-details in Discovery
*When* the Person pulls enter-card-details out of checkout-flow

```realization
Board.ticket("enter-card-details")
  <- enter-card-details
enter-card-details.pull_out()
  -> self.session.mark_pulled_out()
  <- enter-card-details pulled out, its parent still checkout-flow
```

*Then* enter-card-details shows as a card of its own beside checkout-flow, titled Checkout flow.Enter card details
*And* enter-card-details still has the parent checkout-flow
*And* checkout-flow's card holds a dashed row for enter-card-details

#### Scenario: Move a pulled-out child like any ticket

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) enter-card-details was pulled out of checkout-flow and is Done in Discovery
*When* the Person moves enter-card-details to Specification

```realization
Board.ticket("enter-card-details")
  <- enter-card-details
enter-card-details.move_next()
  <- enter-card-details in Specification, its parent still checkout-flow
```

*Then* the Specification [column](../../../../../space/kanban/.context/kanban-model.md#column) shows enter-card-details
*And* enter-card-details still has the parent checkout-flow (Place Parent At Leftmost Child Stage)

## Story: Reassign Ticket Parent

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Add a ticket as a child of a different parent"; "Make a child independent of its parent" |
| `harness/.context/ux/ticket-ui.drawio` | "add and remove a child" |
| `space/session/sessions.py:276` | Observed: a ticket's parent is the `parent` field of its `session.json` |
| the person, 2026-11-11 | "user needs to drag the card outside the parent"; "alt drag … create an orphaned ticket … no longer a child"; "drag to adds to parent and removes from board" |

The realizations name the operations these scenarios need. Built (2026-11-11): dropping a ticket on another card calls `ticket.reassign_parent`, and dropping a Backlog item on a ticket calls `backlog-item.start_under`; the board offers only the cards `Ticket.parent_choices` names, so a drop that would make a loop is never offered. The Alt-drag out of a parent, `ticket.reassign_parent` with no parent, is built with its screen story (2026-11-12).

#### Scenario: Move a child to another parent

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) enter-card-details is a child of checkout-flow
*And* the ticket billing-report is In progress in Discovery
*When* the Person makes billing-report the parent of enter-card-details

```realization
Board.ticket("enter-card-details")
  <- enter-card-details
Board.ticket("billing-report")
  <- billing-report
enter-card-details.reassign_parent(billing-report)
  -> self.session.set_parent(billing-report.session)
  <- enter-card-details, its parent billing-report
```

*Then* billing-report's card holds enter-card-details
*And* checkout-flow's card no longer holds enter-card-details
*And* enter-card-details' session.json names billing-report as its parent

#### Scenario: Take a child off its parent

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) enter-card-details is a child of checkout-flow
*When* the Person takes enter-card-details off checkout-flow

```realization
Board.ticket("enter-card-details")
  <- enter-card-details
enter-card-details.reassign_parent(None)
  -> self.session.set_parent(None)
  <- enter-card-details with no parent
```

*Then* enter-card-details shows as a card of its own with no parent
*And* checkout-flow's card holds no row for enter-card-details, dashed or not
*And* enter-card-details' session.json names no parent

#### Scenario: Start a Backlog item under a ticket

*Given* the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards is in the Backlog
*And* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is In progress in Discovery
*When* the Person starts Gift cards as a child of checkout-flow

```realization
Board.backlog_item("Gift cards")
  <- Gift cards
Board.ticket("checkout-flow")
  <- checkout-flow
Gift cards.start_under(checkout-flow)
  -> self.start()
  -> gift-cards.reassign_parent(checkout-flow)
  <- gift-cards In progress in Discovery, its parent checkout-flow
```

*Then* checkout-flow's card holds gift-cards
*And* the Backlog no longer shows Gift cards

#### Scenario: Refuse to make a ticket a child of its own child

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow holds its child ticket enter-card-details
*When* the Person tries to make checkout-flow a child of enter-card-details

```realization
Board.ticket("checkout-flow")
  <- checkout-flow
Board.ticket("enter-card-details")
  <- enter-card-details
checkout-flow.reassign_parent(enter-card-details)
  -> self._can_be_child_of(enter-card-details)
  <- refused: ParentLoopError, enter-card-details is one of checkout-flow's children
```

*Then* checkout-flow keeps no parent
*And* enter-card-details' card does not offer itself as a place to drop checkout-flow (`Ticket.parent_choices`)

## Story: Place Parent At Leftmost Child Stage

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/ux/ticket-ui.drawio` | "parents cant be dragged; they change stage by taking on the stage of the leftmost ticket" |

The realizations name the operations these scenarios need.

#### Scenario: Show a parent in its earliest child's stage

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow has the child tickets enter-card-details in Specification and confirm-order in Discovery
*When* the [board](../../../../../space/kanban/.context/kanban-model.md#board) shows checkout-flow

```realization
Board.show()
  -> checkout-flow.column
     -> self.children
  <- checkout-flow in Discovery, the stage of its leftmost child
```

*Then* checkout-flow shows in the Discovery [column](../../../../../space/kanban/.context/kanban-model.md#column)

#### Scenario: Move a parent on when its last child moves on

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow has the child tickets enter-card-details in Specification and confirm-order, pulled out of it, Done in Discovery
*When* the Person moves confirm-order to Specification

```realization
Board.ticket("confirm-order")
  <- confirm-order
confirm-order.move_next()
  <- confirm-order in Specification
Board.show()
  -> checkout-flow.column
     -> self.children
  <- checkout-flow in Specification, the stage of its leftmost child
```

*Then* checkout-flow shows in the Specification [column](../../../../../space/kanban/.context/kanban-model.md#column)

#### Scenario: Refuse to move a parent by hand

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow has the child ticket confirm-order in Discovery
*When* the Person tries to move checkout-flow to Specification

```realization
Board.ticket("checkout-flow")
  <- checkout-flow
checkout-flow.move_next()
  -> self.children
  <- checkout-flow, still in Discovery: a parent moves only with its children
```

*Then* checkout-flow stays in the Discovery [column](../../../../../space/kanban/.context/kanban-model.md#column)

## Story: Nest Child Branch And Session

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Nest branches and sessions for tickets in a hierarchy" |
| `space/kanban/ticket.py:114-125` | Observed: a ticket's branch and work branch are named after the ticket |

The realizations name the operations these scenarios need.

Evidence gap: the source says to nest, not how. The folder and branch below are examples to agree. Git cannot hold a branch checkout-flow/enter-card-details beside a branch checkout-flow, so the child's branch joins the names with a dot, as the drawing's parent.Child does.

#### Scenario: Nest a child's session and branch under its parent's

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's [session](../../../../../space/kanban/.context/kanban-model.md#session) is .sessions/checkout-flow on the branch checkout-flow
*When* Claude Code opens the child ticket Enter card details of checkout-flow

```realization
ticket.create("Enter card details", scope="story", parent="checkout-flow")
  -> Board.ticket("checkout-flow")
  <- checkout-flow
  -> checkout-flow.add_child("Enter card details")
     -> self.session.open_child("Enter card details", scope="story")
     <- the session .sessions/checkout-flow/enter-card-details
     -> enter-card-details.branch
        -> self.parent.branch
     <- checkout-flow.enter-card-details
```

*Then* enter-card-details' session folder is .sessions/checkout-flow/enter-card-details
*And* enter-card-details' branch is checkout-flow.enter-card-details
