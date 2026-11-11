---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Maintain Tickets

### Domain terms

- ++ticket text++ — what a ticket is about, kept in the markdown file in its session folder (checkout-flow.md), or in a backlog item's file.
- ++tag++ — a word a person puts on a ticket's session; its card shows it.

## Story: Add Backlog Item

#### Scenario: Add an idea to the Backlog

*Given* the Backlog [column](../../../../../space/kanban/.context/kanban-model.md#column) has no [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) titled Gift cards
*When* the Person adds the backlog item Gift cards with the text Sell gift cards.
*Then* the Backlog shows Gift cards with the text Sell gift cards.
*And* Gift cards is selected and the form is closed
*And* a toast says Gift cards added to Backlog

#### Scenario: Keep Add off with no title

*Given* the new backlog item form is open
*But* the Person has typed no title
*When* the Person tries to add the item
*Then* Add stays off
*And* no [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) is written

#### Scenario: Start a backlog item in a chosen folder

*Given* the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards is in the Backlog
*And* the [repository](../../../../../space/kanban/.context/kanban-model.md#repo) has the folders src/billing and src/visits
*When* the Person starts Gift cards
*Then* the roots dialog lists the top folders of the repository
*And* Gift cards is still in the Backlog
*When* the Person chooses src/visits as its root
*Then* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits
*And* the roots dialog stays open on gift-cards so its practices' roots can be set
*And* a toast says Gift cards started in Discovery

#### Scenario: Keep the idea file with the new ticket

*Given* the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md
*When* the Person starts Returns and refunds on the whole repository
*Then* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery
*And* its session folder holds returns-and-refunds.md, text and all
*And* its session log names the item's file
*But* the Backlog no longer shows Returns and refunds

#### Scenario: Bring a ticket back from the Backlog with its work

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) sign-up was moved back out of Discovery and waits in the Backlog as the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Sign up
*And* its folder .sessions/_backlog/sign-up/ keeps its session log
*When* the Person starts Sign up
*Then* sign-up is back on the board with its session log and session.json
*But* no new ticket is opened

## Story: Edit Ticket Text

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Edit a ticket's text"; backlog item text and session ticket text, kept in a markdown file the session's instructions refer to |
| `harness/.context/ux/ticket-ui.drawio` | "edit text in markdown file" |
| `space/kanban/backlog_item.py:121-128`, `space/kanban/app/src/kanban/backlog-item/backlog-item-view.tsx:62` | Observed: starting a backlog item moves its file, text and all, into the ticket's session folder; a backlog card shows its file's text |

Intended, not built: a ticket's card does not show its text, no card edits text, and `Ticket.agent_context` does not name the file. The last scenario is the interaction the story map's validation asks to split into a story of its own.

#### Scenario: Show a ticket's text from its session file

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's [session](../../../../../space/kanban/.context/kanban-model.md#session) folder holds checkout-flow.md with the text Pay for the basket.
*When* the Person opens the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* checkout-flow's card shows Pay for the basket.

#### Scenario: Edit a ticket's text

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's card shows Pay for the basket.
*When* the Person edits checkout-flow's text to Pay for the basket by card.
*Then* checkout-flow.md in checkout-flow's [session](../../../../../space/kanban/.context/kanban-model.md#session) folder holds Pay for the basket by card.
*And* checkout-flow's card shows Pay for the basket by card.

#### Scenario: Write the text file for a ticket that has none

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery
*But* pet-visits' [session](../../../../../space/kanban/.context/kanban-model.md#session) folder holds no pet-visits.md
*When* the Person edits pet-visits' text to Book a visit for a pet.
*Then* pet-visits.md in pet-visits' session folder holds Book a visit for a pet.
*And* pet-visits' card shows Book a visit for a pet.

#### Scenario: Edit a backlog item's text

*Given* the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards has the text Sell gift cards.
*When* the Person edits Gift cards' text to Sell gift cards at the till.
*Then* .sessions/_backlog/gift-cards.md holds Sell gift cards at the till.
*And* the Backlog shows Gift cards with the text Sell gift cards at the till.

#### Scenario: Tell the agent which file holds the ticket's text

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's [session](../../../../../space/kanban/.context/kanban-model.md#session) folder holds checkout-flow.md
*When* checkout-flow becomes the active ticket
*Then* the agent's context for checkout-flow names .sessions/checkout-flow/checkout-flow.md as the ticket's text

## Story: Reorder Tickets In Column

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Reorder tickets in a column" |
| `space/kanban/board.py:328` | Observed: the Backlog lists its items by file name; no column keeps a place a person chose |

#### Scenario: Keep a ticket where it was moved in its column

*Given* the Discovery [column](../../../../../space/kanban/.context/kanban-model.md#column) shows the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits above sign-up
*When* the Person moves sign-up above pet-visits in Discovery
*Then* Discovery shows sign-up above pet-visits
*And* Discovery still shows sign-up above pet-visits when the [board](../../../../../space/kanban/.context/kanban-model.md#board) is read again

#### Scenario: Keep a backlog item where it was moved

*Given* the Backlog shows the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards above Returns and refunds
*When* the Person moves Returns and refunds above Gift cards
*Then* the Backlog shows Returns and refunds above Gift cards
*And* the Backlog still shows Returns and refunds above Gift cards when the [board](../../../../../space/kanban/.context/kanban-model.md#board) is read again

## Story: Archive Ticket

#### Scenario: Archive a ticket off the board

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery with its story map generated
*When* the Person archives pet-visits
*Then* no [column](../../../../../space/kanban/.context/kanban-model.md#column) shows pet-visits
*And* its folder is in .sessions/_archive/pet-visits

#### Scenario: Refuse to archive a ticket the board does not have

*Given* the [board](../../../../../space/kanban/.context/kanban-model.md#board) shows no [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) named no-such-ticket
*When* the Person archives no-such-ticket
*Then* the board says no ticket named 'no-such-ticket' on the board
*But* nothing is moved to .sessions/_archive

## Story: Delete Ticket

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Delete a ticket"; Delete on a card removes the ticket and its session folder |
| `space/kanban/ticket.py:352` | Observed: Archive is the nearest operation; there is no delete |

Evidence gap: the source does not say what becomes of a deleted ticket's branch and worktree; these scenarios leave them out.

#### Scenario: Delete a ticket and its session folder

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery
*When* the Person deletes pet-visits
*Then* no [column](../../../../../space/kanban/.context/kanban-model.md#column) shows pet-visits
*And* .sessions/pet-visits is gone

#### Scenario: Refuse to delete a ticket the board does not have

*Given* the [board](../../../../../space/kanban/.context/kanban-model.md#board) shows no [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) named no-such-ticket
*When* the Person deletes no-such-ticket
*Then* the board says no ticket named 'no-such-ticket' on the board
*But* no session folder is removed

## Story: Tag Ticket Session

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/maintain-tickets-on-board.md` | "tagging sessions" |
| `space/session/sessions.py:276` | Observed: `session.json` holds no tags |

#### Scenario: Tag a ticket's session

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits has no tags
*When* the Person tags pet-visits' [session](../../../../../space/kanban/.context/kanban-model.md#session) with billing
*Then* pet-visits' card shows the tag billing
*And* pet-visits' session.json holds the tag billing

#### Scenario: Add a second tag

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is tagged billing
*When* the Person tags pet-visits' [session](../../../../../space/kanban/.context/kanban-model.md#session) with urgent
*Then* pet-visits' card shows the tags billing and urgent
