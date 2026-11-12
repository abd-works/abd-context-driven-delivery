---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: See Work On Session Board

## Story: Open Board

#### Scenario: Open the board on a project

*Given* the [board](../../../../../space/kanban/.context/kanban-model.md#board) of project cdd-board-surface-fixture shows 9 [tickets](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*And* its [session](../../../../../space/kanban/.context/kanban-model.md#session) checkout-flow, titled Checkout flow, is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person opens the session board at http://127.0.0.1:8778
*Then* the header reads cdd-board-surface-fixture · 10 tickets · active: Checkout flow
*And* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board) again every two seconds

#### Scenario: Find the board from a chat

*Given* a Claude Code chat has the cdd-board mod loaded
*When* the Person asks the chat where the session board is
*Then* the chat answers The board is at http://127.0.0.1:8778, and starts the board first when nothing answers on that port

## Story: Display Board

#### Scenario: Draw the columns of the board

*Given* a [board](../../../../../space/kanban/.context/kanban-model.md#board) with the Stories, DDD, and UX [practices](../../../../../space/kanban/.context/kanban-model.md#practiceguidance) chosen
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* the [columns](../../../../../space/kanban/.context/kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, and Complete, in that order
*And* each [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) shows an In progress list and a Done list
*And* the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate and Validate

#### Scenario: Say the cdd server is not connected

*Given* the cdd server behind the session board is not connected
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* a band across the top of the page says The cdd server is not connected
*And* the header offers Update

#### Scenario: Show a failing tool in a toast

*Given* the [session](../../../../../space/kanban/.context/kanban-model.md#session) folder .sessions/broken holds a session.json that is not JSON
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* a toast says cdd board.show failed: JsonFileUnreadable: .sessions/broken/session.json is not a readable JSON object (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))
*But* no band says the cdd server is lost

#### Scenario: Update the board and cdd to the latest code

*Given* the band says the cdd server is lost
*When* the Person presses Update
*Then* the session board server gets the latest code, rebuilds the page, and pins the cdd server to it
*And* the session board server restarts on the new code
*And* the page loads again from the restarted server

#### Scenario: Say which update step failed

*Given* the latest code cannot be pulled
*When* the Person presses Update
*Then* a toast says Update failed at get latest, with the reason
*And* the page and the session board server keep running as they were

#### Scenario: Keep the newer board when an older read answers late

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) move-me is In progress in the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column)
*And* a read of the [board](../../../../../space/kanban/.context/kanban-model.md#board) is still waiting for its answer
*And* another chat has moved move-me into Discovery's Done
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board) again
*Then* the session board shows move-me in Discovery's Done even though the older read answered last

#### Scenario: Announce a ticket that moved

*Given* the session board shows the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) move-me In progress in Discovery
*When* another chat moves move-me into Discovery's Done
*Then* a toast says Move me moved to Discovery · Done

#### Scenario: Announce a fidelity done

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report has the story_map [fidelity](../../../../../space/kanban/.context/kanban-model.md#fidelityguidance) generated and validated with no violations
*When* a clean validate of stories-story-map is written to billing-report's [session log](../../../../../space/kanban/.context/kanban-model.md#session)
*Then* a toast says stories-story-map done on billing-report

#### Scenario: Show a server failure on one line

*Given* the cdd server answers with a Python traceback
*When* the session board draws its server band
*Then* the band shows the traceback's exception line
*And* the whole traceback is behind Details

#### Scenario: Say a slow call is still running

*Given* the cdd server is busy
*When* a ticket call has run for eight seconds
*Then* a toast says the board is still waiting on it

## Story: Arrange Board And Details

#### Scenario: Give the board more height

*Given* the page is 900 pixels high
*When* the Person resizes the board to 300 pixels
*Then* the [board](../../../../../space/kanban/.context/kanban-model.md#board) region is 300 pixels high and the details take the rest

#### Scenario: Keep both regions open

*Given* the page is 900 pixels high
*When* the Person resizes the board to 10 pixels
*Then* the [board](../../../../../space/kanban/.context/kanban-model.md#board) region stays 160 pixels high
*When* the Person resizes the board to 5000 pixels
*Then* the board region stops at 650 pixels, so the details stay open

#### Scenario: Expand one region and show both again

*Given* the board and the details share the page
*When* the Person expands the board
*Then* the [board](../../../../../space/kanban/.context/kanban-model.md#board) takes the whole page
*When* the Person collapses the board
*Then* the board and the details share the page again

## Story: Display Backlog Items As Tickets

#### Scenario: Show each idea file in the Backlog

*Given* the [repository](../../../../../space/kanban/.context/kanban-model.md#repo)'s .sessions/_backlog/ holds search-the-catalog.md headed Search the catalog with the text An idea.
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Backlog [column](../../../../../space/kanban/.context/kanban-model.md#column) shows the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Search the catalog
*And* selecting it shows its text An idea. in the details
*And* its last activity is when search-the-catalog.md last changed

#### Scenario: Show a ticket kept in the Backlog under its own file

*Given* the Backlog folder holds the folder gift-cards with its session log and gift-cards.md headed Gift cards
*And* gift-cards.md holds the text Sell them at the till.
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Backlog [column](../../../../../space/kanban/.context/kanban-model.md#column) shows one [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards with the text Sell them at the till.
*But* no [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) shows a [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) for gift-cards

#### Scenario: Name an item that has no heading by its file name

*Given* the Backlog folder holds returns-and-refunds.md with no # heading
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Backlog [column](../../../../../space/kanban/.context/kanban-model.md#column) shows the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Returns and refunds

## Story: Display Ticket Card

#### Scenario: Show every work session as a ticket

*Given* the [repository](../../../../../space/kanban/.context/kanban-model.md#repo)'s .sessions/ holds the work [sessions](../../../../../space/kanban/.context/kanban-model.md#session) pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) shows the [tickets](../../../../../space/kanban/.context/kanban-model.md#ticket--card) main, Pet visits, and Sign up
*And* the Complete [column](../../../../../space/kanban/.context/kanban-model.md#column) shows Browse pets
*But* old-spike is not on the board

#### Scenario: Place a ticket in the stage of its latest move

*Given* the [session log](../../../../../space/kanban/.context/kanban-model.md#session) of the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) second-spec ends with move Specification
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* second-spec shows In progress in the Specification [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Place a ticket with no move in the stage of its latest work

*Given* the [session log](../../../../../space/kanban/.context/kanban-model.md#session) of the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux
*But* it has no move line
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Follow work into a later stage

*Given* a person moved pet-visits into Discovery
*And* pet-visits' ux mockup was generated after that move
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Keep a person's move until the next work

*Given* pet-visits' ux mockup was generated
*And* a person then moved pet-visits back into Discovery
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Follow work back into an earlier stage

*Given* a person moved pet-visits into Implementation
*And* pet-visits' ux mockup was generated after that move
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Draw the card's title, age, and fidelity segments

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow, titled Checkout flow, last worked on at 2026-11-01T10:00:00Z
*And* its story_map [fidelity](../../../../../space/kanban/.context/kanban-model.md#fidelityguidance) has violations and its other Discovery fidelities are not started
*When* the session board draws checkout-flow's [card](../../../../../space/kanban/.context/kanban-model.md#card) 13 hours later
*Then* the card reads Checkout flow and 13 hours ago
*And* it shows one segment for each enabled Discovery fidelity, the story_map segment in the violations colour and the rest dim
*And* a violations link on the card opens the report

#### Scenario: Outline the active ticket

*Given* the [repository](../../../../../space/kanban/.context/kanban-model.md#repo)'s .sessions/session.json names checkout-flow as the open [session](../../../../../space/kanban/.context/kanban-model.md#session)
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* the checkout-flow [card](../../../../../space/kanban/.context/kanban-model.md#card) has a thick orange outline
*And* the header names Checkout flow as active

#### Scenario: Name the active ticket on the chat's status line

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card), in Discovery, with violations on stories-story-map
*When* a turn in a chat with the cdd-board mod loaded ends
*Then* the chat's status line reads checkout-flow · Discovery · next: stories-story-map · 1 with violations

## Story: Display Ticket Details

#### Scenario: Show the ticket of a card pressed anywhere

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report is In progress in Discovery with nothing recorded
*When* the Person selects billing-report's card
*Then* the details show Billing report, root whole repository, and Discovery · in progress
*And* the details say No handoff yet and Next: stories-story-map, generate
*And* the details show a tile for each enabled [fidelity](../../../../../space/kanban/.context/kanban-model.md#fidelityguidance) with its [fidelity progress](../../../../../space/kanban/.context/kanban-model.md#fidelityprogress)

#### Scenario: Show the active ticket with no card pressed

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* no card is pressed
*When* the session board draws the details
*Then* the details show Checkout flow

#### Scenario: Show the ticket worked on last when none is active

*Given* no [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) is active
*And* billing-report has the latest line in its session log, at 2026-11-02T10:00:00Z
*When* the session board draws the details
*Then* the details show Billing report

#### Scenario: Name a split ticket by the ticket it came from

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) child has scope story and parent epic in its session.json
*When* the Person selects child's card
*Then* the details read child · story of epic

#### Scenario: Say another session must be activated to act on a locked ticket

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person selects billing-report's card
*Then* the details say Activate this session to run actions

#### Scenario: Expand one ticket's card at a time

*Given* the card of the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow is expanded over the board
*When* the Person expands billing-report's card
*Then* billing-report's card is expanded with a tile for each enabled Discovery fidelity
*And* checkout-flow's card is closed

#### Scenario: Open a card on the fidelity of a pressed segment

*Given* billing-report's card shows a segment for the story_map [fidelity](../../../../../space/kanban/.context/kanban-model.md#fidelityguidance)
*When* the Person opens billing-report's story_map segment
*Then* billing-report's card is expanded with the story_map tile's action bar open

#### Scenario: Name the board's own project

*Given* the session board runs in board-sandbox
*When* the details show a ticket
*Then* their corner names board-sandbox

## Story: Set Stage WIP Limit

#### Scenario: Set a stage's limit

*Given* the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) has the limit 3
*When* the Person sets Discovery's limit to 4
*Then* Discovery shows the limit 4
*And* the limit is still 4 when the board is read again

#### Scenario: Give every stage a limit of 3 until a person sets one

*Given* the [repository](../../../../../space/kanban/.context/kanban-model.md#repo) has no .sessions/_board.json
*When* the session board reads the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*Then* Discovery, Specification, and Implementation each show the limit 3

#### Scenario: Show a stage over its limit

*Given* the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) holds the [tickets](../../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report, move-me, and back-to-backlog
*When* the Person sets Discovery's limit to 2
*Then* Discovery's count shows in red, over its limit

#### Scenario: Change nothing for a limit that is not a whole number

*Given* the Discovery [stage](../../../../../space/kanban/.context/kanban-model.md#stage--column) has the limit 3
*When* the Person types many as Discovery's limit
*Then* Discovery still shows the limit 3
*But* no limit is saved

## Story: Arrange Side Panel

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

*Given* the [board](../../../../../space/kanban/.context/kanban-model.md#board) shows its five [columns](../../../../../space/kanban/.context/kanban-model.md#column) at their own width
*When* the Person opens checkout-flow's files list
*Then* the columns keep their width and scroll sideways beside the files panel

## Story: Expand Ticket From Empty Area

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/maintain-tickets-on-board.md` | "click any empty area to expand ticket" |
| `space/kanban/app/src/kanban/ticket/ticket-card-view.tsx:57`, `:198` | Observed: a press on a card chooses it and shows its details; only the expand mark opens its actions |

#### Scenario: Expand a card from an empty area

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's card is collapsed on the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*When* the Person presses an empty area of checkout-flow's card
*Then* checkout-flow's card is expanded to show its actions
*And* the details show checkout-flow

#### Scenario: Leave a card's controls to do their own work

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's card is collapsed on the [board](../../../../../space/kanban/.context/kanban-model.md#board)
*When* the Person opens checkout-flow's files from its card
*Then* checkout-flow's files show
*And* checkout-flow's card stays collapsed
