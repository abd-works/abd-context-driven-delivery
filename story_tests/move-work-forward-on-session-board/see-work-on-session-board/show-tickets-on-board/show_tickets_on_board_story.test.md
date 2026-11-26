---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Show Tickets On Board

## Story: Open Board

#### Scenario: Open the board on a project

*Given* the [board](../../../../space/kanban/.context/kanban-model.md#board) of project cdd-board-surface-fixture shows 9 [tickets](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*And* its [session](../../../../space/kanban/.context/kanban-model.md#session) checkout-flow, titled Checkout flow, is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person opens the session board at http://127.0.0.1:8778
*Then* the header reads cdd-board-surface-fixture · 10 tickets · active: Checkout flow
*And* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board) again every two seconds

#### Scenario: Find the board from a chat

*Given* a Claude Code chat has the cdd-board mod loaded
*When* the Person asks the chat where the session board is
*Then* the chat answers The board is at http://127.0.0.1:8778/?project=<the chat's repository folder>, and starts the board first when nothing answers on that port
*And* the board shows that repository's tickets, whichever repository the board server was started from

## Story: Display Board

#### Scenario: Draw the columns of the board

*Given* a [board](../../../../space/kanban/.context/kanban-model.md#board) with the Stories, DDD, and UX [practices](../../../../space/kanban/.context/kanban-model.md#practiceguidance) chosen
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* the [columns](../../../../space/kanban/.context/kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, Hardening, and Complete, in that order
*And* each [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) shows an In progress list and a Done list
*And* the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate and Validate

#### Scenario: Show the other tickets when one ticket's session file does not read

> Test: see-work-on-session-board.story.shared.py, replayed by the domain spec; unit: space/kanban/kanban_tools_spec.py; the page's notice: see-work-on-session-board.story.ui.spec.ts and space/kanban/app/src/kanban/board/board-page.spec.ts.

> Evidence: exploratory-testing defect pixel-07. One session.json cut off half way took every card off the board.

*Given* the [session](../../../../space/kanban/.context/kanban-model.md#session) folder .sessions/broken holds a session.json that is not JSON
*And* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is on the [board](../../../../space/kanban/.context/kanban-model.md#board)
*When* the session board reads the board
*Then* pet-visits shows in Discovery
*And* no column shows broken
*And* the board names .sessions/broken/session.json as a file it could not read, with what is wrong in it
*When* the Person tags broken's session with billing
*Then* the board says .sessions/broken/session.json is not a readable JSON object
*And* that file is as it was

#### Scenario: Keep the newer board when an older read answers late

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) move-me is In progress in the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column)
*And* a read of the [board](../../../../space/kanban/.context/kanban-model.md#board) is still waiting for its answer
*And* another chat has moved move-me into Discovery's Done
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board) again
*Then* the session board shows move-me in Discovery's Done even though the older read answered last

#### Scenario: Announce a ticket that moved

*Given* the session board shows the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) move-me In progress in Discovery
*When* another chat moves move-me into Discovery's Done
*Then* a toast says Move me moved to Discovery · Done

#### Scenario: Move a ticket into Hardening

> Walked by hand on 2026-11-24 (Flow A), on a board of the throwaway project board-sandbox served by the dev lane at f65c11a24; the screens are in [walks/hardening/](walks/hardening/). Not yet captured in a browser story test.

> Evidence: a board served by a cdd server that has no Hardening stage, such as a stable lane older than the stage, draws no Hardening column and shows a ticket whose session log moved it into Hardening In progress in Discovery.

*Given* the session board shows the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) second-spec In progress in Specification, and almost-shipped in Hardening's Done ([screen](walks/hardening/1-given-board-with-hardening.png))
*When* the Person drags second-spec into Hardening's In progress
*Then* second-spec shows In progress in the Hardening [stage](../../../../space/kanban/.context/kanban-model.md#stage--column), between Implementation and Complete
*And* a toast says Second spec moved to Hardening · In progress ([screen](walks/hardening/2-when-dragged-into-hardening.png))
*And* the ticket's details read Hardening · in progress, with Stories hardening and BDD hardening under the Hardening head and no hardening [fidelity](../../../../space/kanban/.context/kanban-model.md#fidelityguidance) for DDD, UX, or Clean Engineering
*When* the Person presses second-spec's card
*Then* the card lists Stories hardening and BDD hardening as its work in the stage ([screen](walks/hardening/3-then-card-shows-hardening-fidelities.png))
*When* the Person drags second-spec into Hardening's Done
*Then* second-spec shows in Hardening's Done, below almost-shipped
*And* a toast says Second spec moved to Hardening · Done ([screen](walks/hardening/4-when-moved-to-hardening-done.png))
*And* the catalog's board shows a Hardening column with hardening for Stories and BDD ([screen](walks/hardening/5-catalog-board-hardening-column.png)), and its approach page shows Hardening between Implement and Validate ([screen](walks/hardening/6-catalog-approach-hardening-stage.png))

#### Scenario: Announce a fidelity done

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report has the story_map [fidelity](../../../../space/kanban/.context/kanban-model.md#fidelityguidance) generated and validated with no violations
*When* a clean validate of stories-story-map is written to billing-report's [session log](../../../../space/kanban/.context/kanban-model.md#session)
*Then* a toast says stories-story-map done on billing-report

## Story: Display Backlog Items As Tickets

#### Scenario: Show each idea file in the Backlog

*Given* the [repository](../../../../space/kanban/.context/kanban-model.md#repo)'s .sessions/_backlog/ holds search-the-catalog.md headed Search the catalog with the text An idea.
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Backlog [column](../../../../space/kanban/.context/kanban-model.md#column) shows the [backlog item](../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Search the catalog
*And* selecting it shows its text An idea. in the details
*And* its last activity is when search-the-catalog.md last changed

#### Scenario: Show a ticket kept in the Backlog under its own file

*Given* the Backlog folder holds the folder gift-cards with its session log and gift-cards.md headed Gift cards
*And* gift-cards.md holds the text Sell them at the till.
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Backlog [column](../../../../space/kanban/.context/kanban-model.md#column) shows one [backlog item](../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards with the text Sell them at the till.
*But* no [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) shows a [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) for gift-cards

#### Scenario: Name an item that has no heading by its file name

*Given* the Backlog folder holds returns-and-refunds.md with no # heading
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Backlog [column](../../../../space/kanban/.context/kanban-model.md#column) shows the [backlog item](../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Returns and refunds

## Story: Display Ticket Card

#### Scenario: Show every work session as a ticket

*Given* the [repository](../../../../space/kanban/.context/kanban-model.md#repo)'s .sessions/ holds the work [sessions](../../../../space/kanban/.context/kanban-model.md#session) pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column) shows the [tickets](../../../../space/kanban/.context/kanban-model.md#ticket--card) main, Pet visits, and Sign up
*And* the Complete [column](../../../../space/kanban/.context/kanban-model.md#column) shows Browse pets
*But* old-spike is not on the board

#### Scenario: Draw the card's title, age, and fidelity segments

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow, titled Checkout flow, last worked on at 2026-11-01T10:00:00Z
*And* its story_map [fidelity](../../../../space/kanban/.context/kanban-model.md#fidelityguidance) has violations and its other Discovery fidelities are not started
*When* the session board draws checkout-flow's [card](../../../../space/kanban/.context/kanban-model.md#card) 13 hours later
*Then* the card reads Checkout flow and 13 hours ago
*And* it shows one segment for each enabled Discovery fidelity, the story_map segment in the violations colour and the rest dim
*And* a violations link on the card opens the report

#### Scenario: Outline the active ticket

*Given* the [repository](../../../../space/kanban/.context/kanban-model.md#repo)'s .sessions/session.json names checkout-flow as the open [session](../../../../space/kanban/.context/kanban-model.md#session)
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* the checkout-flow [card](../../../../space/kanban/.context/kanban-model.md#card) has a thick orange outline
*And* the header names Checkout flow as active

#### Scenario: Name the active ticket on the chat's status line

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card), in Discovery, with violations on stories-story-map
*When* a turn in a chat with the cdd-board mod loaded ends
*Then* the chat's status line reads checkout-flow · Discovery · next: stories-story-map · 1 with violations

## Story: Place Ticket In Column

#### Scenario: Place a ticket in the stage of its latest move

*Given* the [session log](../../../../space/kanban/.context/kanban-model.md#session) of the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) second-spec ends with move Specification
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* second-spec shows In progress in the Specification [stage](../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Place a ticket with no move in the stage of its latest work

*Given* the [session log](../../../../space/kanban/.context/kanban-model.md#session) of the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux
*But* it has no move line
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Follow work into a later stage

*Given* a person moved pet-visits into Discovery
*And* pet-visits' ux mockup was generated after that move
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Keep a person's move until the next work

*Given* pet-visits' ux mockup was generated
*And* a person then moved pet-visits back into Discovery
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Discovery [stage](../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Follow work back into an earlier stage

*Given* a person moved pet-visits into Implementation
*And* pet-visits' ux mockup was generated after that move
*When* the session board reads the [board](../../../../space/kanban/.context/kanban-model.md#board)
*Then* pet-visits shows in the Specification [stage](../../../../space/kanban/.context/kanban-model.md#stage--column)

#### Scenario: Place a ticket with no move in the earliest stage it has work in

> From `story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/display-ticket-card/display_ticket_card_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the [session log](../../../../.context/kanban-model.md#session) of the [ticket](../../../../.context/kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux  
  *But* it has no move line  
*When* the session board reads the [board](../../../../.context/kanban-model.md#board)  
*Then* pet-visits shows in the Specification [stage](../../../../.context/kanban-model.md#stage--column)
