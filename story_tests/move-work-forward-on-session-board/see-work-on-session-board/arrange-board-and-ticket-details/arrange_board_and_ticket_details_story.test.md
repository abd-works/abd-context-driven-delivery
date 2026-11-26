---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Arrange Board And Ticket Details

## Story: Arrange Board And Details

#### Scenario: Give the board more height

*Given* the page is 900 pixels high
*When* the Person resizes the board to 300 pixels
*Then* the [board](../../../../space/kanban/.context/kanban-model.md#board) region is 300 pixels high and the details take the rest

#### Scenario: Keep both regions open

*Given* the page is 900 pixels high
*When* the Person resizes the board to 10 pixels
*Then* the [board](../../../../space/kanban/.context/kanban-model.md#board) region stays 160 pixels high
*When* the Person resizes the board to 5000 pixels
*Then* the board region stops at 650 pixels, so the details stay open

#### Scenario: Expand one region and show both again

*Given* the board and the details share the page
*When* the Person expands the board
*Then* the [board](../../../../space/kanban/.context/kanban-model.md#board) takes the whole page
*When* the Person collapses the board
*Then* the board and the details share the page again

## Story: Display Ticket Details

#### Scenario: Show the ticket of a card pressed anywhere

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report is In progress in Discovery with nothing recorded
*When* the Person selects billing-report's card
*Then* the details show Billing report, root whole repository, and Discovery · in progress
*And* the details say No handoff yet and Next: stories-story-map, generate
*And* the details show a tile for each enabled [fidelity](../../../../space/kanban/.context/kanban-model.md#fidelityguidance) with its [fidelity progress](../../../../space/kanban/.context/kanban-model.md#fidelityprogress)

#### Scenario: Show the active ticket with no card pressed

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* no card is pressed
*When* the session board draws the details
*Then* the details show Checkout flow

#### Scenario: Show main when no other ticket is opened

*Given* no [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) is opened, so main, the default session, is the active ticket
*But* no card is pressed
*When* the session board draws the details
*Then* the details show main

#### Scenario: Name a split ticket by the ticket it came from

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) child has scope story and parent epic in its session.json
*When* the Person selects child's card
*Then* the details read child · story of epic

#### Scenario: Say another session must be activated to act on a locked ticket

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person selects billing-report's card
*Then* the details say Activate this session to run actions

#### Scenario: Name the board's own project

*Given* the session board runs in board-sandbox
*When* the details show a ticket
*Then* their corner names board-sandbox

## Story: Set Stage WIP Limit

#### Scenario: Set a stage's limit

*Given* the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) has the limit 3
*When* the Person sets Discovery's limit to 4
*Then* Discovery shows the limit 4
*And* the limit is still 4 when the board is read again

#### Scenario: Give every stage a limit of 3 until a person sets one

*Given* the [repository](../../../../space/kanban/.context/kanban-model.md#repo) has no .sessions/_board.json
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* Discovery, Specification, and Implementation each show the limit 3

#### Scenario: Show a stage over its limit

*Given* the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) holds the [tickets](../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report, move-me, and back-to-backlog
*When* the Person sets Discovery's limit to 2
*Then* Discovery's count shows in red, over its limit

#### Scenario: Change nothing for a limit that is not a whole number

*Given* the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) has the limit 3
*When* the Person types many as Discovery's limit
*Then* Discovery still shows the limit 3
*But* no limit is saved

## Story: Arrange Side Panel

#### Scenario: Set a panel's width

*Given* the help panel is open beside the board
*When* the Person widens the help panel to 700 pixels
*Then* the help panel is 700 pixels wide
*When* the Person narrows the help panel to 10 pixels
*Then* the help panel stops at 360 pixels

#### Scenario: Expand one panel at a time

*Given* the report panel and the help panel are open
*And* the report panel is expanded
*When* the Person expands the help panel
*Then* the help panel takes the board's width less the other open panels
*And* the report panel is no longer expanded

#### Scenario: Close a side panel

*Given* checkout-flow's validation report panel is open
*When* the Person closes the report panel
*Then* no side panel is open

#### Scenario: Keep the columns' width when a panel opens

*Given* the [board](../../../../space/kanban/.context/kanban-model.md#board) shows its five [columns](../../../../space/kanban/.context/kanban-model.md#column) at their own width
*When* the Person opens checkout-flow's validation report
*Then* the columns keep their width and scroll sideways beside the report panel

## Story: Expand Ticket From Empty Area

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/maintain-tickets-on-board.md` | "click any empty area to expand ticket" |
| `space/kanban/app/src/kanban/ticket/ticket-card-view.tsx:57`, `:198` | Observed: a press on a card chooses it and shows its details; only the expand mark opens its actions |

#### Scenario: Expand a card from an empty area

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's card is collapsed on the [board](../../../../space/kanban/.context/kanban-model.md#board)
*When* the Person presses an empty area of checkout-flow's card
*Then* checkout-flow's card is expanded to show its actions
*And* the details show checkout-flow

#### Scenario: Leave a card's controls to do their own work

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's card is collapsed on the [board](../../../../space/kanban/.context/kanban-model.md#board)
*When* the Person opens checkout-flow's files from its card
*Then* checkout-flow's files show
*And* checkout-flow's card stays collapsed

#### Scenario: Expand one ticket's card at a time

*Given* the card of the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is expanded over the board
*When* the Person expands billing-report's card
*Then* billing-report's card is expanded with a tile for each enabled Discovery fidelity
*And* checkout-flow's card is closed

#### Scenario: Open a card on the fidelity of a pressed segment

*Given* billing-report's card shows a segment for the story_map [fidelity](../../../../space/kanban/.context/kanban-model.md#fidelityguidance)
*When* the Person opens billing-report's story_map segment
*Then* billing-report's card is expanded with the story_map tile's action bar open
