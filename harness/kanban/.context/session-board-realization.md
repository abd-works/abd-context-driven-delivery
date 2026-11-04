# Scenario Realizations: Session Board

Source: the `*_story.test.py` files under `move-work-forward-on-session-board/`, one per Story in its epic, sub-epic, and story folders, on `story-map.md`; domain terms link to `kanban-model.md`.

Each block traces the domain operations a When (or a Then that triggers a collaborator) runs: `->` is a call, `<-` its return.
`Board page` is the board app in `harness/kanban/app`, `chat mod` is `harness/chat-ui/pane/hooks/register.ts`, and `Agent` is a Claude Code chat calling the cdd tools.

---

## Open Board

Actor: Person · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/open-board/open_board_story.test.py`

### Scenario: Open the board on a project

Evidence: observed: board-page.ts start() and board-header-view.tsx; tests/board-surface.spec.ts 'with the board drawn'. The header counts each ticket name once.

**Given** the [board](kanban-model.md#board) of project cdd-board-surface-fixture shows 9 [tickets](kanban-model.md#ticket--card)

**And** its [session](kanban-model.md#session) checkout-flow, titled Checkout flow, is the active [ticket](kanban-model.md#ticket--card)

**When** the Person opens the session board at http://127.0.0.1:8778

```realization
Board page -> Board.show()
Board <- Board.to_json(): project, active, columns
Board page -> Chat.list()
Chat <- the chats whose cdd-board mod checked in lately
```

**Then** the header reads cdd-board-surface-fixture · 9 tickets · active: Checkout flow

**And** the session board reads the [board](kanban-model.md#board) again every two seconds

### Scenario: Find the board from a chat

Evidence: inferred: the 'board' command handler in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod.

**Given** a Claude Code chat has the cdd-board mod loaded

**When** the Person asks the chat where the session board is

```realization
Person -> Claude Code command.run('board')  [External: Claude Code]
chat mod -> board server start when it does not answer
chat mod <- the board's address
```

**Then** the chat answers The board is at http://127.0.0.1:8778, and starts the board first when nothing answers on that port

---

## Display Board

Actor: Board App · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py`

### Scenario: Draw the columns of the board

Evidence: observed: kanban_spec 'should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order', 'should have story_map, bounded_context, and ia as Discovery's work required', 'should give every stage Generate, Validate, and Review, in that order'.

**Given** a [board](kanban-model.md#board) with the Stories, DDD, and UX [practices](kanban-model.md#practiceguidance) chosen

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board page -> Board.show()
Board -> Board.columns
Board <- Backlog, Stage Discovery, Stage Specification, Stage Implementation, Column Complete
Stage -> Stage.work_required
Stage <- every chosen practice's fidelities of that stage
```

**Then** the [columns](kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, and Complete, in that order

**And** each [stage](kanban-model.md#stage--column) shows an In progress list and a Done list

**And** the Discovery [stage](kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate, Validate, and Review

### Scenario: Say the cdd server is not connected

Evidence: observed: board-client.spec 'should show a band when the board read answers that cdd is not connected', 'should show the band when the server itself does not answer' (the band then says not answering); board-header-view.tsx names the button Connect.

**Given** the cdd server behind the session board is not connected

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board page -> Board.show()
Board page <- the cdd server is not connected
```

**Then** a band across the top of the page says The cdd server is not connected

**And** the header offers Connect in place of Restart cdd

### Scenario: Show a failing tool in a toast

Evidence: observed: board-client.spec 'with a tool failing' — 'should show no band', 'should show a toast'.

**Given** the [session](kanban-model.md#session) folder .sessions/broken holds a session.json that is not JSON

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board page -> Board.show()
Board -> Board.tickets
Board <- JSONDecodeError
```

**Then** a toast says cdd board.show failed: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)

**But** no band says the cdd server is lost

### Scenario: Restart cdd on the current code

Evidence: observed: board-client.spec 'that a person has restarted cdd' — 'should read the board again from a fresh cdd server', 'should say so in a toast'; board-page.ts restartCdd.

**Given** the band says the cdd server is lost

**When** the Person restarts cdd

```realization
Board page -> session board server: restart cdd  [External: cdd server]
Board page -> Board.show()
Board page -> Chat.list()
```

**Then** the session board shows the [board](kanban-model.md#board) read from a fresh cdd server

**And** the band is gone

**And** a toast says cdd restarted on the current code

### Scenario: Keep the newer board when an older read answers late

Evidence: observed: board-client.spec 'Refresh Board After Tool Calls' — 'should keep the newer board when an older read answers late'; board-reader.ts refresh.

**Given** the [ticket](kanban-model.md#ticket--card) move-me is In progress in the Discovery [stage](kanban-model.md#stage--column)

**And** a read of the [board](kanban-model.md#board) is still waiting for its answer

**When** another chat moves move-me into Discovery's Done and the session board reads the [board](kanban-model.md#board) again

```realization
Agent -> Ticket.move_to('Discovery', done=True)
Ticket -> Ticket.record('done Discovery')
Board page -> Board.show()
Board <- move-me done in Discovery
```

**Then** the session board shows move-me in Discovery's Done even though the older read answered last

### Scenario: Announce a ticket that moved

Evidence: observed: board-client.spec 'Announce Ticket Changes' — 'should name the new column of a ticket that moves', 'should raise nothing on the first read', 'should raise nothing on each read of a session open and closed under one name'.

**Given** the session board shows the [ticket](kanban-model.md#ticket--card) move-me In progress in Discovery

**When** another chat moves move-me into Discovery's Done

```realization
Agent -> Ticket.move_to('Discovery', done=True)
Ticket -> Ticket.record('done Discovery')
Board page -> Board.show()
Board page -> BoardClient.announcementsSince(earlier read)
```

**Then** a toast says Move me moved to Discovery · Done

### Scenario: Announce a reviewed fidelity

Evidence: observed: board-client.spec 'should name a fidelity that was reviewed'.

**Given** the [ticket](kanban-model.md#ticket--card) billing-report has the story_map [fidelity](kanban-model.md#fidelityguidance) generated and validated with no violations

**When** a review of stories-story_map is written to billing-report's [session log](kanban-model.md#session)

```realization
Person -> Ticket.finish_review(['stories-story_map'])
Ticket -> Ticket.record('review Stories story_map')
Board page -> Board.show()
Board <- stories-story_map done on billing-report
```

**Then** a toast says stories-story_map reviewed on billing-report

---

## Arrange Board And Details

Actor: Person · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-details/arrange_board_and_details_story.test.py`

### Scenario: Give the board more height

Evidence: observed: board-client.spec 'should give the board the height a drag asks for'; story-actions.spec 'should give the board more height on a drag, and never close the details'.

**Given** the page is 900 pixels high

**When** the Person resizes the board to 300 pixels

```realization
Person -> BoardLayoutClient.setBoardHeight(300, 900)
```

**Then** the [board](kanban-model.md#board) region is 300 pixels high and the details take the rest

### Scenario: Keep both regions open

Evidence: observed: board-client.spec 'should not let a drag close the board', 'should not let a drag close the details'.

**Given** the page is 900 pixels high

**When** the Person resizes the board to 10 pixels

```realization
Person -> BoardLayoutClient.setBoardHeight(10, 900)
```

**Then** the [board](kanban-model.md#board) region stays 160 pixels high

**When** the Person resizes the board to 5000 pixels

```realization
Person -> BoardLayoutClient.setBoardHeight(5000, 900)
```

**Then** the board region stops at 650 pixels, so the details stay open

### Scenario: Expand one region and show both again

Evidence: observed: board-client.spec 'should give one region the page', 'should bring the other back on a second press'; story-actions.spec 'should give a region the whole page and bring the other back'.

**Given** the board and the details share the page

**When** the Person expands the board

```realization
Person -> BoardLayoutClient.toggleRegion('board')
```

**Then** the [board](kanban-model.md#board) takes the whole page

**When** the Person collapses the board

```realization
Person -> BoardLayoutClient.toggleRegion('board')
```

**Then** the board and the details share the page again

---

## Display Backlog Items As Tickets

Actor: Board App · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/display-backlog-items-as-tickets/display_backlog_items_as_tickets_story.test.py`

### Scenario: Show each idea file in the Backlog

Evidence: observed: kanban_spec 'should show each backlog item in the Backlog column'; kanban_tools_spec 'should give a backlog item its text', 'should say when a backlog item last changed'.

**Given** the [repository](kanban-model.md#repo)'s .sessions/_backlog/ holds search-the-catalog.md headed Search the catalog with the text An idea.

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board page -> Board.show()
Board -> Board.backlog_items
BacklogItem -> BacklogItem.title, BacklogItem.text, BacklogItem.last_activity
```

**Then** the Backlog [column](kanban-model.md#column) shows the [backlog item](kanban-model.md#backlogitem--card) Search the catalog

**And** selecting it shows its text An idea. in the details

**And** its last activity is when search-the-catalog.md last changed

### Scenario: Show a ticket kept in the Backlog under its own file

Evidence: observed: kanban_spec 'that is kept as a folder holding a file of its own name' — 'should be in the Backlog under the heading of that file', 'should show the text of that file'; 'should be off the stages'.

**Given** the Backlog folder holds the folder gift-cards with its session log and gift-cards.md headed Gift cards

**And** gift-cards.md holds the text Sell them at the till.

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board -> Board.backlog_items
Board <- one BacklogItem for gift-cards/gift-cards.md
Board -> Board.tickets
Board <- no ticket for gift-cards
```

**Then** the Backlog [column](kanban-model.md#column) shows one [backlog item](kanban-model.md#backlogitem--card) Gift cards with the text Sell them at the till.

**But** no [stage](kanban-model.md#stage--column) shows a [ticket](kanban-model.md#ticket--card) for gift-cards

### Scenario: Name an item that has no heading by its file name

Evidence: inferred: BacklogItem.title in harness/kanban/backlog_item.py; no spec writes an item without a heading.

**Given** the Backlog folder holds returns-and-refunds.md with no # heading

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board -> Board.backlog_items
BacklogItem -> BacklogItem.title
BacklogItem <- the file name in words
```

**Then** the Backlog [column](kanban-model.md#column) shows the [backlog item](kanban-model.md#backlogitem--card) Returns and refunds

---

## Display Ticket Card

Actor: Board App · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/display-ticket-card/display_ticket_card_story.test.py`

### Scenario: Show every work session as a ticket

Evidence: observed: kanban_spec 'should show every work session as a ticket', 'should leave main off the board', 'should leave archived sessions off the board', 'should show closed sessions in Complete'.

**Given** the [repository](kanban-model.md#repo)'s .sessions/ holds the work [sessions](kanban-model.md#session) pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board -> Board.tickets
Board -> Session.all_in(repo_root)
Session <- pet-visits, sign-up, browse-pets
```

**Then** the Discovery [stage](kanban-model.md#stage--column) shows the [tickets](kanban-model.md#ticket--card) Pet visits and Sign up

**And** the Complete [column](kanban-model.md#column) shows Browse pets

**But** main and old-spike are not on the board

### Scenario: Place a ticket in the stage of its latest move

Evidence: observed: kanban_tools_spec 'should show the ticket in the next stage'; Ticket.column in ticket.py; fixture-repo.ts second-spec.

**Given** the [session log](kanban-model.md#session) of the [ticket](kanban-model.md#ticket--card) second-spec ends with move Specification

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board -> Ticket.column
Ticket <- the stage of its latest move line: Specification
```

**Then** second-spec shows In progress in the Specification [stage](kanban-model.md#stage--column)

### Scenario: Place a ticket with no move in the earliest stage it has work in

Evidence: observed: kanban_spec 'with its first logged work on a Specification fidelity' — 'should be in Specification'; 'that has just been started' — 'should be in Discovery, in progress'.

**Given** the [session log](kanban-model.md#session) of the [ticket](kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux

**But** it has no move line

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board -> Ticket.column
Ticket -> Ticket.progress
Ticket <- the first stage with work done: Specification
```

**Then** pet-visits shows in the Specification [stage](kanban-model.md#stage--column)

### Scenario: Draw the card's title, age, and practice blocks

Evidence: observed: board-client.spec 'Display Ticket Card' — 'should say how many hours ago its ticket was worked on', 'should say one hour in the singular', 'should say a ticket with no activity has none'; ticket-card-view.tsx SegmentsView draws one block per enabled fidelity of its stage, dim while not started.

**Given** the [ticket](kanban-model.md#ticket--card) checkout-flow, titled Checkout flow, last worked on at 2026-11-01T10:00:00Z

**And** its story_map [fidelity](kanban-model.md#fidelityguidance) has violations and its other Discovery fidelities are not started

**When** the session board draws checkout-flow's [card](kanban-model.md#card) 13 hours later

```realization
Board page -> Ticket.to_json(): title, last_activity, progress, practices
```

**Then** the card reads Checkout flow and 13 hours ago

**And** it shows one block for each enabled Discovery fidelity, the story_map block in the violations colour and the rest dim

**And** a violations link on the card opens the report

### Scenario: Outline the active ticket

Evidence: observed: kanban_spec 'should name the ticket of the current session as active'; ticket-card-view.tsx draws the active ticket's border 3 pixels wide in the accent colour.

**Given** the [repository](kanban-model.md#repo)'s .sessions/session.json names checkout-flow as the open [session](kanban-model.md#session)

**When** the session board reads the [board](kanban-model.md#board)

```realization
Board -> Board.active
Board <- Ticket checkout-flow
```

**Then** the checkout-flow [card](kanban-model.md#card) has a thick orange outline

**And** the header names Checkout flow as active

### Scenario: Name the active ticket on the chat's status line

Evidence: inferred: statusOf and readActive in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card), in Discovery, with violations on stories-story_map

**When** a turn in a chat with the cdd-board mod loaded ends

```realization
chat mod -> Board.show()
Board <- the active ticket checkout-flow
```

**Then** the chat's status line reads checkout-flow · Discovery · next: stories-story_map · 1 with violations

---

## Display Ticket Details

Actor: Board App · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/display-ticket-details/display_ticket_details_story.test.py`

### Scenario: Show the ticket of a card pressed anywhere

Evidence: observed: story-actions.spec 'should show the ticket of a card pressed anywhere'; ticket-client.spec 'should name the ticket's stage and how far it has got there', 'should say what runs next'.

**Given** the [ticket](kanban-model.md#ticket--card) billing-report is In progress in Discovery with nothing recorded

**When** the Person selects billing-report's card

```realization
Person -> TicketClient.select()
Board page -> Ticket.to_json()
```

**Then** the details show Billing report, root whole repository, and Discovery · in progress

**And** the details say No handoff yet and Next: stories-story_map, generate

**And** the details show a tile for each enabled [fidelity](kanban-model.md#fidelityguidance) with its [fidelity progress](kanban-model.md#fidelityprogress)

### Scenario: Show the active ticket with no card pressed

Evidence: observed: board-client.spec 'should show the active ticket with no card pressed'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**But** no card is pressed

**When** the session board draws the details

```realization
Board page -> BoardClient.selectedTicket
Board <- active ticket checkout-flow
```

**Then** the details show Checkout flow

### Scenario: Show the ticket worked on last when none is active

Evidence: observed: board-client.spec 'should show the ticket worked on last with none active'.

**Given** no [ticket](kanban-model.md#ticket--card) is active

**And** billing-report has the latest line in its session log, at 2026-11-02T10:00:00Z

**When** the session board draws the details

```realization
Board page -> BoardClient.selectedTicket
Board <- the ticket with the latest last_activity: billing-report
```

**Then** the details show Billing report

### Scenario: Name a split ticket by the ticket it came from

Evidence: observed: ticket-client.spec 'should name a split ticket by its parent'.

**Given** the [ticket](kanban-model.md#ticket--card) child has scope story and parent epic in its session.json

**When** the Person selects child's card

```realization
Board page -> Ticket.to_json(): scope, parent
```

**Then** the details read child · story of epic

### Scenario: Say another session must be activated to act on a locked ticket

Evidence: observed: ticket-client.spec 'should say another session must be activated to run it'.

**Given** Active session only is on

**And** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**When** the Person selects billing-report's card

```realization
Person -> TicketClient.select()
```

**Then** the details say Activate this session to run actions

### Scenario: Expand one ticket's card at a time

Evidence: observed: tile-client.spec 'Expand Ticket' — 'should open with its tiles only, each opening its own action bar', 'should expand only one card at a time'; story-actions.spec 'should expand only one card at a time'.

**Given** the card of the [ticket](kanban-model.md#ticket--card) checkout-flow is expanded over the board

**When** the Person expands billing-report's card

```realization
Person -> OpenCardClient.toggle(billing-report)
```

**Then** billing-report's card is expanded with a tile for each enabled Discovery fidelity

**And** checkout-flow's card is closed

### Scenario: Open a card on the fidelity of a pressed block

Evidence: observed: tile-client.spec 'with a segment pressed' — 'should open the card', 'should open the tile of that fidelity'; story-actions.spec 'should open a card on the fidelity of a pressed segment'.

**Given** billing-report's card shows a block for the story_map [fidelity](kanban-model.md#fidelityguidance)

**When** the Person opens billing-report's story_map block

```realization
Person -> OpenCardClient.openSegment(billing-report, Discovery, 'stories-story_map')
```

**Then** billing-report's card is expanded with the story_map tile's action bar open

---

## Set Stage WIP Limit

Actor: Person · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/set-stage-wip-limit/set_stage_wip_limit_story.test.py`

### Scenario: Set a stage's limit

Evidence: observed: board-client.spec 'Set Stage WIP Limit' — 'should save a whole number', 'should read the board again'; Board.set_wip_limit.

**Given** the Discovery [stage](kanban-model.md#stage--column) has the limit 3

**When** the Person sets Discovery's limit to 4

```realization
Person -> Board.set_wip_limit('Discovery', 4)
Board -> .sessions/_board.json: {'wip_limits': {'Discovery': 4}}
Board page -> Board.show()
```

**Then** Discovery shows the limit 4

**And** the limit is still 4 when the board is read again

### Scenario: Give every stage a limit of 3 until a person sets one

Evidence: observed: kanban_tools_spec and wip_limits.spec.shared 'should give every stage a limit of 3 tickets until a person sets one'.

**Given** the [repository](kanban-model.md#repo) has no .sessions/_board.json

**When** the session board reads the [board](kanban-model.md#board)

```realization
Stage -> Stage.wip_limit
Board -> Board.wip_limit(stage) <- 3
```

**Then** Discovery, Specification, and Implementation each show the limit 3

### Scenario: Show a stage over its limit

Evidence: observed: kanban_tools_spec 'that sets a stage's limit below the tickets it holds' — 'should show the stage over its limit'; Stage.to_json is_over_limit.

**Given** the Discovery [stage](kanban-model.md#stage--column) holds the [tickets](kanban-model.md#ticket--card) billing-report, move-me, and back-to-backlog

**When** the Person sets Discovery's limit to 2

```realization
Person -> Board.set_wip_limit('Discovery', 2)
Stage -> Stage.to_json() <- is_over_limit: true
```

**Then** Discovery's count shows in red, over its limit

### Scenario: Change nothing for a limit that is not a whole number

Evidence: observed: board-client.spec 'should change nothing for a limit that is not a number'; story-actions.spec 'should close the field on Escape without changing the limit'.

**Given** the Discovery [stage](kanban-model.md#stage--column) has the limit 3

**When** the Person types many as Discovery's limit

**Then** Discovery still shows the limit 3

**But** no limit is saved

---

## Arrange Side Panel

Actor: Person · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/arrange-side-panel/arrange_side_panel_story.test.py`

### Scenario: Set a panel's width

Evidence: observed: side-panel-client.spec 'should set the width a drag asks for', 'should not go narrower than the smallest width'; story-actions.spec 'should set a panel's width on a drag of its left edge'.

**Given** the files panel is open beside the board

**When** the Person widens the files panel to 700 pixels

```realization
Person -> SidePanelClient.setWidth('files', 700)
```

**Then** the files panel is 700 pixels wide

**When** the Person narrows the files panel to 10 pixels

```realization
Person -> SidePanelClient.setWidth('files', 10)
```

**Then** the files panel stops at 360 pixels

### Scenario: Expand one panel at a time

Evidence: observed: side-panel-client.spec 'should expand one panel at a time'; story-actions.spec 'should let an expanded panel take the board's place, and × close it'.

**Given** the report panel and the files panel are open

**And** the report panel is expanded

**When** the Person expands the files panel

```realization
Person -> SidePanelClient.toggleExpanded('files')
```

**Then** the files panel takes the board's width less the other open panels

**And** the report panel is no longer expanded

### Scenario: Close a side panel

Evidence: observed: side-panel-client.spec 'Close Side Panel' — 'should close the panel'.

**Given** checkout-flow's [validation report](kanban-model.md#validate--guidanceaction) panel is open

**When** the Person closes the report panel

```realization
Person -> SidePanelClient.close('report')
```

**Then** no side panel is open

### Scenario: Keep the columns' width when a panel opens

Evidence: observed: story-actions.spec 'should keep the columns' width and scroll them sideways when a panel opens'.

**Given** the [board](kanban-model.md#board) shows its five [columns](kanban-model.md#column) at their own width

**When** the Person opens checkout-flow's files list

**Then** the columns keep their width and scroll sideways beside the files panel

---

## Add Backlog Item

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py`

### Scenario: Add an idea to the Backlog

Evidence: observed: kanban_tools_spec 'that adds a backlog item' — 'should show the item in the Backlog with its text', 'should write the title and text to one markdown file'; backlog-item-client.spec 'with a title and text typed'.

**Given** the Backlog [column](kanban-model.md#column) has no [backlog item](kanban-model.md#backlogitem--card) titled Gift cards

**When** the Person adds the backlog item Gift cards with the text Sell gift cards.

```realization
Person -> BacklogItem.add('Gift cards', 'Sell gift cards.')
BacklogItem -> .sessions/_backlog/gift-cards.md: # Gift cards / Sell gift cards.
BacklogItem <- BacklogItem Gift cards
Board page -> Board.show()
```

**Then** the Backlog shows Gift cards with the text Sell gift cards.

**And** Gift cards is selected and the form is closed

**And** a toast says Gift cards added to Backlog

### Scenario: Keep Add off with no title

Evidence: observed: backlog-item-client.spec 'should stay off with no title'; story-actions.spec 'should keep Add off with no title'.

**Given** the new backlog item form is open

**But** the Person has typed no title

**When** the Person tries to add the item

**Then** Add stays off

**And** no [backlog item](kanban-model.md#backlogitem--card) is written

### Scenario: Start a backlog item in a chosen folder

Evidence: observed: root-choice-client.spec 'with a backlog item a person has asked to start' — 'should browse the top of the repository for its root before it starts', 'should not start it yet', 'should open its ticket with that folder as its root', 'should stay open on the new ticket's roots'; backlog-item-client.spec 'should say so in a toast'.

**Given** the [backlog item](kanban-model.md#backlogitem--card) Gift cards is in the Backlog

**And** the [repository](kanban-model.md#repo) has the folders src/billing and src/visits

**When** the Person starts Gift cards

```realization
Person -> Board.folders('')
Board <- the repository's top folders
```

**Then** the roots dialog lists the top folders of the repository

**And** Gift cards is still in the Backlog

**When** the Person chooses src/visits as its root

```realization
Person -> BacklogItem.start(path='src/visits')
BacklogItem -> Ticket.new('Gift cards', 'feature', '', 'src/visits')
Ticket -> Session.new('gift-cards', <repo>/src/visits, <repo>, fields, is_current=False)
BacklogItem -> Ticket.record('backlog .sessions/_backlog/gift-cards.md')
BacklogItem -> Ticket.keep(gift-cards.md)
BacklogItem <- Ticket gift-cards
```

**Then** the [ticket](kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits

**And** the roots dialog stays open on gift-cards so its practices' roots can be set

**And** a toast says Gift cards started in Discovery

### Scenario: Keep the idea file with the new ticket

Evidence: observed: kanban_spec 'that has been started' — 'should keep the item's file, text and all, in the new ticket's session folder', 'should open a ticket in Discovery', 'should name the item's file in the new ticket's session log'; kanban_tools_spec 'should take the item off the Backlog'.

**Given** the [backlog item](kanban-model.md#backlogitem--card) Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md

**When** the Person starts Returns and refunds on the whole repository

```realization
Person -> BacklogItem.start(scope='feature')
BacklogItem -> Ticket.new('Returns and refunds', 'feature', '', '')
BacklogItem -> Ticket.record('backlog <path of returns-and-refunds.md>')
BacklogItem -> Ticket.keep(returns-and-refunds.md)
```

**Then** the [ticket](kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery

**And** its session folder holds returns-and-refunds.md, text and all

**And** its session log names the item's file

**But** the Backlog no longer shows Returns and refunds

### Scenario: Bring a ticket back from the Backlog with its work

Evidence: observed: kanban_tools_spec 'that starts the item again' — 'should bring the ticket back with its work'; kanban_spec 'should bring its ticket back with the history in its session log'.

**Given** the [ticket](kanban-model.md#ticket--card) sign-up was moved back out of Discovery and waits in the Backlog as the [backlog item](kanban-model.md#backlogitem--card) Sign up

**And** its folder .sessions/_backlog/sign-up/ keeps its session log

**When** the Person starts Sign up

```realization
Person -> BacklogItem.start()
BacklogItem -> Session.at(.sessions/_backlog/sign-up, repo).reopen()
BacklogItem <- Ticket sign-up
```

**Then** sign-up is back on the board with its session log and session.json

**But** no new ticket is opened

---

## Open Ticket Session

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py`

### Scenario: Open a new ticket

Evidence: observed: kanban_tools_spec 'that opens a new ticket' — 'should return the new ticket in Discovery', 'should leave the current session as it is'; kanban_spec 'should name Generate on story_map as next'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**When** the Person opens a new ticket titled Pet visits

```realization
Person -> Ticket.new('Pet visits', 'feature')
Ticket -> Session.new('pet-visits', <repo>, <repo>, {title, scope, parent}, is_current=False)
Ticket <- Ticket pet-visits
```

**Then** pet-visits is In progress in Discovery, titled Pet visits

**And** its next step is Generate on stories-story_map

**And** checkout-flow is still the active ticket

### Scenario: Ask a chat to open a ticket

Evidence: observed: board-page.ts openNewTicket; tests/board-surface.spec.ts 'with no chat connected' shows + Ticket off.

**Given** a chat is connected to the session board

**When** the Person asks for a new ticket from the board's header

```realization
Board page -> Chat.send('fill', 'Open a new ticket with ticket.new, titled: ')
```

**Then** the chat's prompt holds Open a new ticket with ticket.new, titled: for the Person to finish

**But** with no chat connected, + Ticket is off

### Scenario: Open a ticket on a folder of the repository

Evidence: observed: kanban_tools_spec 'that opens a ticket on a folder in the repository' — 'should save that folder as the session's workpath'; 'that opens a ticket with no folder' — 'should leave the session working on the repository'.

**Given** the [repository](kanban-model.md#repo) has the folder src/billing

**When** the Person opens a ticket titled Billing report on src/billing

```realization
Person -> Ticket.new('Billing report', 'feature', '', 'src/billing')
Ticket -> Session.new('billing-report', <repo>/src/billing, <repo>, fields, is_current=False)
```

**Then** billing-report's [session](kanban-model.md#session) works in src/billing

**And** the details show its root as src/billing

### Scenario: Choose a ticket's root

Evidence: observed: root-choice-client.spec 'that a person browses into a folder for the session root' — 'should list the folders inside it', 'should make it the ticket's root'; kanban_tools_spec 'should keep the folder as the session's work folder'.

**Given** checkout-flow works on the whole [repository](kanban-model.md#repo)

**And** the repository has src/billing and src/visits under src

**When** the Person browses src for checkout-flow's root

```realization
Person -> Board.folders('src')
Board <- src/billing, src/visits
```

**Then** the roots dialog lists src/billing and src/visits

**When** the Person chooses src/visits as checkout-flow's root

```realization
Person -> Ticket.choose_root('src/visits')
Ticket -> Session.change_workpath(<repo>/src/visits)
```

**Then** checkout-flow's root reads src/visits

**And** each practice's default root sits under src/visits

### Scenario: Choose one practice's root and go back to its default

Evidence: observed: root-choice-client.spec 'that a person chooses a folder for one practice's root' — 'should show it as that practice's chosen root', 'and then goes back to its default'; kanban_tools_spec 'should leave every other practice on its default root'.

**Given** checkout-flow's Stories [practice](kanban-model.md#practiceguidance) writes under its default root

**When** the Person chooses src/billing for checkout-flow's Stories root

```realization
Person -> Ticket.choose_practice_root('stories', 'src/billing')
Ticket -> Session.choose_output_root('stories', <repo>/src/billing)
```

**Then** the Stories root reads src/billing, chosen by the Person

**And** every other practice stays on its default root

**When** the Person puts Stories back on its default root

```realization
Person -> Ticket.use_default_practice_root('stories')
Ticket -> Session.forget_output_root('stories')
```

**Then** the Stories root is the default again

---

## Close Active Session

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py`

### Scenario: Close the active session with its work committed

Evidence: observed: activation-client.spec 'Close Active Session' — 'should ask what to do with its work', 'should send what to do with its work', 'should select the ticket in Complete'; story-actions.spec 'should ask what to do with its work, then show the ticket in Complete'; kanban_tools_spec 'should leave no ticket active'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card), on its own branch

**When** the Person closes checkout-flow's session

```realization
Person -> Ticket.workspace()
Ticket <- leaving_has_branch: true
```

**Then** a dialog headed Close session Checkout flow offers commit and push, chosen

**When** the Person confirms

```realization
Person -> Ticket.close(['commit', 'push'])
Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
Ticket -> Session.close()
Ticket -> Session.move_to_closed()
Board page -> Board.show()
```

**Then** checkout-flow shows in Complete and is selected

**And** a toast says Checkout flow: committed, pushed · Session Checkout flow closed

**And** no ticket is active

### Scenario: Close a ticket that has no branch of its own

Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'should commit nothing on a ticket that has no branch'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**But** it has no branch of its own

**When** the Person closes checkout-flow's session and confirms

```realization
Person -> Ticket.close([])
Ticket -> Session.close()
Ticket -> Session.move_to_closed()
```

**Then** checkout-flow shows in Complete

**And** its folder is in .sessions/closed/checkout-flow

**But** nothing is committed

### Scenario: Close the active ticket by moving it to Complete

Evidence: observed: ticket-client.spec 'should let only the active ticket, or one done in Implementation, be dropped on Complete'; ticket-client.tsx dropOn opens the Close dialog for the active ticket.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card), In progress in Discovery

**When** the Person moves checkout-flow into Complete

**Then** the dialog headed Close session Checkout flow asks what to do with its work

---

## Restrict Actions To Active Session

Actor: Person · Sub-epic: See Work On Session Board · File: `move-work-forward-on-session-board/see-work-on-session-board/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py`

### Scenario: Lock tickets that are not the active session

Evidence: observed: ticket-client.spec 'should lock a ticket that is not the active session', 'should leave the active ticket open'; tile-client.spec 'should keep Run off on a locked ticket'; story-actions.spec 'should keep its practice switches off until Active session only is turned off'.

**Given** Active session only is on

**And** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**When** the Person looks at billing-report's card and tiles

**Then** billing-report's Run next, Run, practice switches, Split, and Handoff are off

**And** checkout-flow's actions stay on

### Scenario: Keep information and moves open on a locked ticket

Evidence: observed: story-actions.spec 'should let a ticket that is not active be dragged, activated, and its files opened'; ticket-card-view.tsx keeps every card draggable.

**Given** Active session only is on

**And** billing-report is not the active [ticket](kanban-model.md#ticket--card)

**When** the Person opens billing-report's files and moves it

```realization
Person -> Ticket.files(['stories-story_map'])
Person -> Ticket.move_to('Specification')
```

**Then** the files panel lists billing-report's files

**And** billing-report moves to Specification

**And** Activate stays on for billing-report

### Scenario: Unlock every ticket

Evidence: observed: ticket-client.spec 'should unlock every ticket with Active session only off'.

**Given** Active session only is on

**When** the Person turns Active session only off

**Then** billing-report's actions are on like the active ticket's

---

## Move Ticket

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/move-ticket/move_ticket_story.test.py`

### Scenario: Move a ticket on to the next column

Evidence: observed: kanban_tools_spec 'that moves a ticket to the next column' — 'should show the ticket in the next stage', 'should show the ticket in progress there'; kanban_spec 'should write the stage it entered to its session log'; ticket-client.spec 'should read the board again and select the ticket where it landed'.

**Given** the [ticket](kanban-model.md#ticket--card) ready-to-move is in Discovery's Done

**When** the Person moves ready-to-move on

```realization
Person -> Ticket.move_next()
Ticket -> Stage.next_stage <- Specification
Ticket -> Ticket.record('move Specification')
Board page -> Board.show()
```

**Then** ready-to-move is In progress in Specification and selected

**And** its session log ends with move Specification

### Scenario: Drag a ticket into a stage's Done whatever its work

Evidence: observed: kanban_tools_spec 'that drags a ticket into a later stage's Done' — 'should show the ticket in that stage's Done'; kanban_spec 'that a person has dragged into a later stage's done part'; ticket-client.spec 'should select a dragged ticket in the stage it was dropped on'.

**Given** the [ticket](kanban-model.md#ticket--card) move-me is In progress in Discovery with nothing done

**When** the Person moves move-me into Implementation's Done

```realization
Person -> Ticket.move_to('Implementation', done=True)
Ticket -> Ticket.record('move Implementation')
Ticket -> Ticket.record('done Implementation')
```

**Then** move-me shows in Implementation's Done and is selected

### Scenario: Move a ticket back to the previous column

Evidence: observed: kanban_tools_spec 'and back to the previous column' — 'should show the ticket in Discovery', 'should show the ticket in Discovery's Done'.

**Given** the [ticket](kanban-model.md#ticket--card) second-spec is In progress in Specification

**When** the Person moves second-spec back

```realization
Person -> Ticket.move_previous()
Ticket -> Stage.previous_stage <- Discovery
Ticket -> Ticket.record('move Discovery')
Ticket -> Ticket.record('done Discovery')
```

**Then** second-spec shows in Discovery's Done

### Scenario: Move a ticket into the Backlog with its work

Evidence: observed: kanban_tools_spec 'that moves the ticket back out of Discovery' — 'should show an item in the Backlog with the ticket's title', 'should take the ticket off the board's stages'; ticket-client.spec 'that a person has moved to the Backlog', 'should let a ticket in any column be dropped on the Backlog'; board-client.spec 'should say a ticket moved to the Backlog'.

**Given** the [ticket](kanban-model.md#ticket--card) back-to-backlog is In progress in Discovery with its story map generated

**When** the Person moves back-to-backlog into the Backlog

```realization
Person -> Ticket.move_to('Backlog')
Ticket -> Session.close()
Ticket -> Session.move_to_backlog()
Ticket -> BacklogItem.holding(ticket, board)
BacklogItem -> .sessions/_backlog/back-to-backlog/back-to-backlog.md: # Back to backlog
Ticket <- BacklogItem Back to backlog
```

**Then** the Backlog shows the [backlog item](kanban-model.md#backlogitem--card) Back to backlog and it is selected

**And** a toast says Back to backlog moved to Backlog

**But** no stage shows back-to-backlog

### Scenario: Close a ticket moved on past Implementation

Evidence: observed: kanban_tools_spec 'and past Implementation' — 'should close the ticket', 'should leave a ticket in Complete where it is on another move forward'; ticket-client.spec 'should let only the active ticket, or one done in Implementation, be dropped on Complete'.

**Given** the [ticket](kanban-model.md#ticket--card) almost-shipped is in Implementation's Done

**And** almost-shipped is not the active ticket

**When** the Person moves almost-shipped on into Complete

```realization
Person -> Ticket.move_next()
Ticket -> Stage.next_stage <- none
Ticket -> Ticket.close()
Ticket -> Session.close()
Ticket -> Session.move_to_closed()
```

**Then** almost-shipped shows in Complete

**And** its folder is in .sessions/closed/almost-shipped

### Scenario: Reopen a ticket moved back out of Complete

Evidence: observed: kanban_tools_spec 'and back again' — 'should reopen the ticket in Implementation'; kanban_spec 'that a person has dragged out of Complete' — 'should be open again, in progress in that stage'.

**Given** the closed [ticket](kanban-model.md#ticket--card) shipped-work is in Complete

**When** the Person moves shipped-work back

```realization
Person -> Ticket.move_previous()
Ticket -> Session.reopen()
Ticket -> Ticket.record('move Implementation')
Ticket -> Ticket.record('done Implementation')
```

**Then** shipped-work shows in Implementation's Done

**And** its folder is back in .sessions/shipped-work

### Scenario: Refuse a move into a column that is not a stage

Evidence: observed: NotAStageError in Ticket.move_to; ticket-client.tsx canDropOn accepts Complete only for the active ticket or one done in Implementation. No spec moves a ticket into Complete through move_to.

**Given** the [ticket](kanban-model.md#ticket--card) billing-report is In progress in Discovery

**And** billing-report is not the active ticket

**When** the Person tries to move billing-report into Complete

```realization
Person -> TicketClient.canDropOn('Complete') <- false
```

**Then** Complete does not take billing-report

**And** billing-report stays In progress in Discovery

---

## Activate Ticket

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py`

### Scenario: Switch to another ticket, committing, pushing, and merging the one left

Evidence: observed: activation-client.spec 'Activate Ticket' — 'should offer commit and push on leaving and open with merge off', 'should offer a branch to a ticket that has none', 'should say what it switches from and to', 'that a person has confirmed with merge chosen'; story-actions.spec 'should switch the session from the dialog, with merge off'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card), on its own branch pushed to origin

**And** billing-report has no branch in the [repository](kanban-model.md#repo)

**When** the Person activates billing-report

```realization
Person -> Ticket.workspace()
Ticket <- has_branch: false, has_worktree: false, leaving_has_branch: true
```

**Then** a dialog headed Switch from Checkout flow to Billing report offers commit and push, chosen, and merge, not chosen

**And** it offers a branch for billing-report, chosen

**When** the Person chooses merge and confirms

```realization
Person -> Ticket.activate(['commit', 'push', 'merge'], ['branch'])
Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
Ticket -> Repo.close_branch('checkout-flow')
Ticket -> Repo.switch_branch('billing-report')
Ticket -> Session.switch('billing-report', repo_path)
```

**Then** billing-report is the active ticket with a thick orange outline

**And** a toast says Checkout flow: committed, pushed, merged to main · Billing report: branch created · Billing report is now active

### Scenario: Activate a ticket when the active one has no branch

Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'with the active ticket on no branch of its own' — 'should commit nothing on a ticket that has no branch', 'should leave the branch checked out as it was'; 'that activates a ticket' — 'should make the chosen ticket the current session'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**But** checkout-flow has no branch of its own

**When** the Person activates billing-report with nothing chosen

```realization
Person -> Ticket.activate([], [])
Ticket -> Session.switch('billing-report', repo_path)
```

**Then** billing-report is the active ticket

**And** the branch checked out is as it was

**But** nothing is committed

### Scenario: Commit nothing when the ticket left is not checked out

Evidence: observed: kanban_tools_spec 'with the active ticket's branch not checked out' — 'should commit nothing on a branch that is not checked out'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card) and has a branch

**But** that branch is not checked out

**When** the Person activates billing-report with commit chosen

```realization
Person -> Ticket.activate(['commit'], [])
Ticket -> Session.switch('billing-report', repo_path)
```

**Then** billing-report is the active ticket

**But** nothing is committed on checkout-flow's branch

### Scenario: Cancel the switch

Evidence: observed: activation-client.spec 'that a person has cancelled' — 'should close the dialog', 'should send nothing'.

**Given** the dialog to switch from Checkout flow to Billing report is open

**When** the Person cancels

**Then** the dialog is closed

**And** checkout-flow is still the active ticket

### Scenario: Create the ticket's branch on activation

Evidence: observed: kanban_tools_spec 'that activates a ticket with a new branch' — 'should create the ticket's branch when a ticket that has none is activated'; 'should say a ticket has no branch yet'.

**Given** the git [repository](kanban-model.md#repo) has no branch billing-report

**When** the Person activates billing-report with a new branch

```realization
Person -> Ticket.activate(opening=['branch'])
Ticket -> Repo.switch_branch('billing-report')
Ticket -> Session.switch('billing-report', repo_path)
```

**Then** the repository has the branch billing-report

**And** billing-report is the active ticket

---

## Split Ticket Into Child Tickets

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`

### Scenario: Ask the chat to split a ticket into child tickets

Evidence: observed: ticket-client.tsx fillSplit and ticket-card-view.tsx SplitActionView; kanban_tools_spec 'that opens a ticket split from another' — 'should name the ticket it was split from'; ticket-client.spec 'should name a split ticket by its parent'. No spec presses Split.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card) and a chat is connected

**When** the Person splits checkout-flow into child tickets

```realization
Board page -> Chat.send('fill', 'Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.new with parent checkout-flow for each story.')
```

**Then** the chat's prompt holds Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.new with parent checkout-flow for each story.

**When** the chat opens a child ticket Enter card details with parent checkout-flow

```realization
Agent -> Ticket.new('Enter card details', 'story', 'checkout-flow')
Ticket -> Session.new('enter-card-details', <repo>, <repo>, {parent: checkout-flow}, is_current=False)
```

**Then** enter-card-details is In progress in Discovery

**And** its details read enter-card-details · story of checkout-flow

### Scenario: Keep Split off where nothing can take the prompt

Evidence: observed: ticket-card-view.tsx useCannotFill; tests/board-surface.spec.ts 'with no chat connected'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**But** no chat is connected

**When** the Person looks at checkout-flow's card

**Then** Split is off

**And** Split is also off on a closed ticket and on a locked one

---

## Archive Ticket

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py`

### Scenario: Archive a ticket off the board

Evidence: observed: kanban_spec 'that has been archived' — 'should be off the board', 'should have its folder in the archive'; kanban_tools_spec 'that archives a ticket' — 'should leave the ticket off the board'. Called as the ticket.archive tool; the board app has no Archive button.

**Given** the [ticket](kanban-model.md#ticket--card) pet-visits is In progress in Discovery with its story map generated

**When** the Person archives pet-visits

```realization
Person -> Ticket.archive()
Ticket -> Session.close()
Ticket -> Session.move_to_archive()
```

**Then** no [column](kanban-model.md#column) shows pet-visits

**And** its folder is in .sessions/_archive/pet-visits

---

## Write Ticket Handoff

Actor: Person · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/write-ticket-handoff/write_ticket_handoff_story.test.py`

### Scenario: Ask the chat to write a handoff

Evidence: observed: ticket-client.spec 'Write Ticket Handoff' — 'should fill the prompt with the handoff command'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card) and a chat is connected

**When** the Person asks for a handoff on checkout-flow

```realization
Board page -> Chat.send('fill', 'Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.')
chat mod -> Chat.check_in(is_busy=False) <- the fill
chat mod -> Claude Code prompt.fill(text, append)  [External: Claude Code]
```

**Then** the chat's prompt holds Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.

**And** a toast says Queued for the prompt, for you to review

### Scenario: Hold the handoff until the chat's turn ends

Evidence: observed: chat-client.spec 'should say a fill waits for the turn to end while the chat is busy'; story-actions.spec 'should hold a fill at the server until the turn ends'; Chat.check_in keeps a fill waiting while busy.

**Given** the connected chat is running a turn

**When** the Person asks for a handoff on checkout-flow

```realization
Board page -> Chat.send('fill', ...)
chat mod -> Chat.check_in(is_busy=True) <- nothing
```

**Then** a toast says the fill goes in when this turn ends

**And** the prompt receives the text once the turn has ended

### Scenario: Keep Handoff off with no chat

Evidence: observed: tests/board-surface.spec.ts 'with no chat connected' — 'should say to load the mod and turn off what sends to a chat'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card)

**But** no chat is connected

**When** the Person looks at checkout-flow's card

**Then** Handoff is off

**And** the header says No chat connected: load the cdd-board mod in a chat to send commands

---

## Display Latest Handoff

Actor: Board App · Sub-epic: Steer Ticket Sessions · File: `move-work-forward-on-session-board/steer-ticket-sessions/display-latest-handoff/display_latest_handoff_story.test.py`

### Scenario: Show the latest handoff

Evidence: observed: kanban_tools_spec 'with handoffs written for the ticket' — 'should show the latest handoff'; side-panel-client.spec 'with its latest handoff opened' — 'should show the handoff in a tab', 'should read the handoff's text'.

**Given** checkout-flow's [session](kanban-model.md#session) folder holds handoff-20261101T120000.md and an earlier handoff

**When** the Person selects checkout-flow

```realization
Board page -> Ticket.latest_handoff
Ticket <- .sessions/checkout-flow/handoff-20261101T120000.md
```

**Then** the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md

**When** the Person opens the handoff

```realization
Person -> Ticket.read_file('.sessions/checkout-flow/handoff-20261101T120000.md')
```

**Then** the files panel shows the handoff in a tab with its text # Handoff

### Scenario: Say a ticket has no handoff

Evidence: observed: kanban_tools_spec 'should show no handoff for a ticket that has none'; details-view.tsx.

**Given** billing-report's [session](kanban-model.md#session) folder holds no handoff

**When** the Person selects billing-report

**Then** the details say No handoff yet

---

## Display Fidelity Progress

Actor: Board App · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/display-fidelity-progress/display_fidelity_progress_story.test.py`

### Scenario: Show Generate done

Evidence: observed: kanban_spec 'with a fidelity generated' — 'should show Generate done and Validate and Review remaining for that fidelity', 'should still find the practice and fidelity by name'.

**Given** pet-visits' [session log](kanban-model.md#session) has generate /work, /work/docs stories story_map markdown stories

**When** the session board reads pet-visits

```realization
Ticket -> Ticket.progress
Ticket -> FidelityProgress.from_log(story_map, Discovery, lines)
FidelityProgress <- done: generate
```

**Then** the story_map tile marks Generate ✓ and Validate and Review ○

### Scenario: Show violations held on Validate

Evidence: observed: kanban_spec 'that has a validate naming graph-rule violations' — 'should still need Validate for that fidelity'; FidelityProgress.action_states marks validate in_progress.

**Given** pet-visits' story_map is generated

**And** its latest validate line is validate Stories story_map graph-rule actor-named-in-step map.md:12

**When** the session board reads pet-visits

```realization
FidelityProgress -> FidelityProgress.from_log(...) <- has_violations: true
FidelityProgress -> FidelityProgress.action_states <- validate: in_progress
```

**Then** the story_map tile marks Validate as violations and its block shows in the violations colour

**And** Review stays to do

### Scenario: Show Validate done after a clean validate

Evidence: observed: kanban_spec 'that has a validate with no violations' — 'should show Validate done for that fidelity', 'should match the practice's class name in the validate line to its folder name'.

**Given** pet-visits' story_map is generated

**And** its latest validate line is validate Stories story_map with no graph-rule

**When** the session board reads pet-visits

```realization
FidelityProgress -> FidelityProgress.from_log(...) <- done: generate, validate
```

**Then** the story_map tile marks Generate ✓, Validate ✓, and Review ○

### Scenario: Show each fidelity of the stage on the ticket

Evidence: observed: kanban_tools_spec 'should show each fidelity's Generate, Validate, and Review'; ticket-client.tsx standingOf for a stage head.

**Given** billing-report has nothing recorded in its [session log](kanban-model.md#session)

**When** the session board reads billing-report

```realization
Ticket -> Ticket.to_json() <- actions: each fidelity's generate, validate, review as to_do
```

**Then** each Discovery tile marks Generate, Validate, and Review ○, its block dim

---

## Open Practice Tile

Actor: Person · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/open-practice-tile/open_practice_tile_story.test.py`

### Scenario: Open a tile on a short hover

Evidence: observed: tile-client.spec 'should open a tile after a short hover', 'should close it on leaving'.

**Given** billing-report's card is expanded

**When** the Person rests the pointer on the story_map tile for half a second

```realization
Person -> TileClient.open(spot, false)
Board page -> Ticket.files(['stories-story_map'])
```

**Then** the story_map tile's action bar opens above the grid, at full width

**When** the Person moves the pointer away

**Then** the action bar closes

### Scenario: Keep a pressed tile open

Evidence: observed: tile-client.spec 'should keep a tile a person pressed open after the pointer leaves', 'should close on a second press'; story-actions.spec 'should keep a pressed tile open after the pointer leaves'.

**Given** billing-report is selected

**When** the Person presses the story_map tile

```realization
Person -> TileClient.open(spot, true)
```

**Then** the story_map action bar stays open after the pointer leaves

**When** the Person presses the story_map tile again

**Then** the story_map action bar closes

### Scenario: Keep two pressed tiles open at once

Evidence: observed: tile-client.spec 'with two tiles pressed' — 'should keep both bars open', 'should close only the bar pressed again', 'should change only that bar's action'; story-actions.spec 'should keep two pressed tiles open at once'.

**Given** billing-report's story_map tile is pressed open

**When** the Person presses the bounded_context tile

**Then** both action bars are open

**When** the Person chooses sketch on the bounded_context bar

**Then** only the bounded_context bar's action is sketch

### Scenario: Open a hovered tile beside a pressed one

Evidence: observed: tile-client.spec 'with a pressed bar and a bar a hover opened' — 'should open the hovered bar beside the pressed one', 'should replace the hovered bar with the next one a hover opens, and keep the pressed one', 'should close the hovered bar on leaving, and keep the pressed one'.

**Given** billing-report's card is expanded with the story_map tile pressed open

**When** the Person hovers on the ia tile

**Then** the ia bar opens beside the story_map bar

**When** the Person moves the pointer away from the ia tile

**Then** the ia bar closes and the story_map bar stays open

### Scenario: Leave a tile in the details closed under a resting pointer

Evidence: observed: story-actions.spec 'should leave a tile in the details closed while the pointer only rests on it'.

**Given** billing-report is shown in the details

**When** the Person rests the pointer on the story_map tile in the details

**Then** the story_map action bar stays closed

---

## Choose Ticket Practices

Actor: Person · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/choose-ticket-practices/choose_ticket_practices_story.test.py`

### Scenario: Turn a practice off for a ticket

Evidence: observed: kanban_tools_spec 'that turns a practice off for a ticket' — 'should show the practice off for that ticket', 'should save the choice to the ticket's session.json'; ticket-client.spec 'Choose Ticket Practices'; story-actions.spec 'should turn a practice off, say where it was saved, and fade its tile'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card) working on every [practice](kanban-model.md#practiceguidance)

**And** its bounded_context tile is open

**When** the Person turns DDD off for checkout-flow

```realization
Person -> Ticket.enable_practice('ddd', False)
Ticket -> PracticeSessionOutput.enabled = False
PracticeSessionOutput -> .sessions/checkout-flow/session.json practices
```

**Then** a toast says DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json

**And** the bounded_context tile closes and fades

**And** the card shows no DDD block

### Scenario: Finish a stage on the practices left on

Evidence: observed: kanban_spec 'with every practice but Stories turned off' — 'should be done with the one practice it works on'.

**Given** pet-visits has generated, validated, and reviewed the story_map [fidelity](kanban-model.md#fidelityguidance)

**And** DDD and UX are turned off for pet-visits

**When** the session board reads pet-visits

```realization
Ticket -> Ticket.is_done
Ticket <- every enabled fidelity of Discovery is done
```

**Then** pet-visits shows in Discovery's Done

### Scenario: Keep practice switches off on a locked ticket

Evidence: observed: story-actions.spec 'should keep its practice switches off until Active session only is turned off'; practice-grid-view.tsx.

**Given** Active session only is on

**And** billing-report is not the active [ticket](kanban-model.md#ticket--card)

**When** the Person looks at billing-report's practices

**Then** each practice switch is off until Active session only is turned off

---

## Send Action To Stage Practices

Actor: Person · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/send-action-to-stage-practices/send_action_to_stage_practices_story.test.py`

### Scenario: Sketch every fidelity of a stage in one command

Evidence: observed: tile-client.spec 'Send Action To Stage Practices' — 'should name every fidelity of the stage in one command'.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) in Discovery and a chat is connected

**And** the Discovery stage head's action bar is open

**When** the Person runs sketch from the Discovery stage head

```realization
Board page -> Chat.send('command', '/actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior')
```

**Then** the chat receives the command /actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior

### Scenario: Keep two stage heads open at once

Evidence: observed: tile-client.spec 'with two stage heads pressed' — 'should keep both stage bars open'.

**Given** billing-report's Discovery stage head is pressed open

**When** the Person presses the Specification stage head

**Then** both stage bars are open

---

## Mark Ticket Done In Stage

Actor: Person · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/mark-ticket-done-in-stage/mark_ticket_done_in_stage_story.test.py`

### Scenario: Mark a ticket done in its stage

Evidence: observed: kanban_spec 'with its stage not done' / 'that a person has moved on' — 'should be done in its stage, in the same column', 'should have no next'; move_ticket.behavior.e2e 'should say in a toast that it is done in its stage'.

**Given** the [ticket](kanban-model.md#ticket--card) pet-visits is In progress in Discovery with only its story map generated

**When** the Person marks pet-visits done in Discovery

```realization
Person -> Ticket.move_next()
Ticket -> Ticket.is_done <- false
Ticket -> Ticket.record('done Discovery')
```

**Then** pet-visits shows in Discovery's Done

**And** it has no next step

**And** a toast says Pet visits moved to Discovery · Done

### Scenario: Mark a ticket back in progress

Evidence: observed: kanban_tools_spec 'and back from Done' — 'should show the ticket in progress in that stage'; kanban_spec 'that a person has dragged back into its own stage's in progress part'.

**Given** the ticket ready-to-move is in Discovery's Done

**When** the Person moves ready-to-move back into Discovery's In progress

```realization
Person -> Ticket.move_to('Discovery')
Ticket -> Ticket.record('in-progress Discovery')
```

**Then** ready-to-move shows In progress in Discovery

### Scenario: Read a done mark from a log written before moves were named move

Evidence: observed: kanban_spec 'with a session log written before moves were named move' — 'should still be in the stage the log names', 'should still be marked done there'.

**Given** pet-visits' session log has pull Specification then done Specification

**When** the session board reads pet-visits

```realization
Ticket -> Ticket.column <- Specification
Ticket -> Ticket.is_done <- true
```

**Then** pet-visits shows in Specification's Done

---

## Add Active Ticket To System Prompt

Actor: Board App · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/add-active-ticket-to-system-prompt/add_active_ticket_to_system_prompt_story.test.py`

### Scenario: Name the active ticket and its next guidance in the system prompt

Evidence: inferred: the prompt.compose handler in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod. The map records it Live with a local stand-in for the model.

**Given** checkout-flow, titled Checkout flow, is the active [ticket](kanban-model.md#ticket--card), in Discovery, with stories-story_map next

**When** a chat with the cdd-board mod loaded composes its system prompt

```realization
chat mod -> Board.show()
Board <- active ticket checkout-flow
```

**Then** the system prompt holds CDD session board: you are working on ticket checkout-flow (Checkout flow), in Discovery. Its next guidance is stories-story_map.

**And** it says each fidelity goes through generate, validate, then review by a person

### Scenario: Say a done ticket waits for a person to move it

Evidence: inferred: register.ts prompt.compose.

**Given** the active [ticket](kanban-model.md#ticket--card) ready-to-move is in Discovery's Done with no next guidance

**When** the chat composes its system prompt

```realization
chat mod -> Board.show()
```

**Then** the system prompt says Its stage is done and waits for a person to move it.

### Scenario: Add nothing with no active ticket

Evidence: inferred: register.ts prompt.compose returns the prompt unchanged with no active ticket.

**Given** no [ticket](kanban-model.md#ticket--card) is active

**When** the chat composes its system prompt

```realization
chat mod -> Board.show()
Board <- active: none
```

**Then** the system prompt holds no session board section

---

## Open Help

Actor: Person · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/open-help/open_help_story.test.py`

### Scenario: Open a fidelity's help

Evidence: observed: kanban_tools_spec 'that opens help on a fidelity' — 'should show the fidelity's rules', 'should name the stage a fidelity belongs to', 'should link to the fidelity's page on the forge'; story-actions.spec 'should show a fidelity's overview, guidance, rules, and Forge link'.

**Given** billing-report's story_map tile is shown

**When** the Person opens help on the story_map fidelity

```realization
Person -> Board.help('stories', 'story_map')
Board <- practice, fidelity, stage Discovery, overview, guidance, rules, href
```

**Then** a side panel shows story_map's overview, guidance, and rules such as verb-noun-format

**And** it names the stage Discovery

**And** its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html

### Scenario: Open a practice's help

Evidence: observed: kanban_tools_spec 'that opens help on a practice' — 'should show the practice's shared rules', 'should name no fidelity on a practice's help'; story-actions.spec 'should head a practice's rules SHARED RULES and say Practice overview'.

**Given** billing-report's [practices](kanban-model.md#practiceguidance) are shown in the details

**When** the Person opens help on the Stories practice

```realization
Person -> Board.help('stories', '')
```

**Then** a side panel shows Practice overview and SHARED RULES such as do-not-invent-requirements

**And** it names no fidelity

**And** its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/context-tools/stories.html

### Scenario: Link a fidelity with no page of its own to its practice's page

Evidence: inferred: FIDELITIES_WITHOUT_PAGE in harness/kanban/board.py; no spec opens help on ddd-model.

**Given** the ddd model fidelity has no page on the forge

**When** the Person opens help on the ddd model fidelity

```realization
Person -> Board.help('ddd', 'model')
```

**Then** its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/context-tools/ddd.html

---

## Send Next Fidelity Action

Actor: Person · Sub-epic: Guide Work Through Practices · File: `move-work-forward-on-session-board/guide-work-through-practices/send-next-fidelity-action/send_next_fidelity_action_story.test.py`

### Scenario: Generate the next fidelity in its default format

Evidence: observed: ticket-client.spec 'with generate next' — 'should ask for the commands of the default format', 'should send those commands in order'; 'should name the step that runs next'; kanban_tools_spec 'should name generate as the next action'.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) with nothing recorded and a chat is connected

**When** the Person runs billing-report's next step

```realization
Person -> Ticket.next_action <- generate on stories-story_map
Person -> Ticket.generate_commands(['stories-story_map'], ['markdown'])
Ticket <- ['/actions-generate stories-story-map format=markdown']
Board page -> Chat.send('command', '/actions-generate stories-story-map format=markdown')
```

**Then** Run next read Run next: generate before it ran

**And** the chat receives the command /actions-generate stories-story-map format=markdown

### Scenario: Fill the prompt to validate

Evidence: observed: ticket-client.spec 'should fill the prompt on validate'.

**Given** back-to-backlog is the active [ticket](kanban-model.md#ticket--card) with its story map generated and a chat is connected

**When** the Person runs back-to-backlog's next step

```realization
Person -> Ticket.next_action <- validate on stories-story_map
Board page -> Chat.send('fill', '/actions-validate stories-story-map')
```

**Then** the chat's prompt holds /actions-validate stories-story-map

### Scenario: Open the report while violations hold the ticket

Evidence: observed: ticket-client.spec 'should say fix violations on held violations', 'with violations held and no chat connected' — 'should still offer Run next', 'should open the report'; kanban_tools_spec 'should name satisfy as the next action'; tests/board-surface.spec.ts 'should keep local actions working'.

**Given** checkout-flow's story map has a verb-noun-format violation on tests/story-map.md line 6

**But** no chat is connected

**When** the Person runs checkout-flow's next step

```realization
Person -> Ticket.next_action <- satisfy on stories-story_map
Person -> Ticket.report('stories-story_map')
```

**Then** Run next read Run next: fix violations

**And** the report panel opens on stories-story_map

### Scenario: Record a review with no chat

Evidence: observed: ticket-client.spec 'Review Fidelity' — 'should offer the review with no chat connected, since it is the person's own approval', 'should show the review done once Run next records it'.

**Given** billing-report's story map is generated and validated with no violations

**But** no chat is connected

**When** the Person runs billing-report's next step

```realization
Person -> Ticket.next_action <- review on stories-story_map
Person -> Ticket.finish_review(['stories-story_map'])
Ticket -> Ticket.record('review Stories story_map')
Board page -> Board.show()
```

**Then** billing-report's story_map marks Review ✓

### Scenario: Go back to an earlier stage's fidelity still to review

Evidence: observed: kanban_spec 'that a person has moved on with an earlier stage's fidelity still to review' — 'should name Review on that fidelity as next'.

**Given** pet-visits' story map is generated and validated with no violations

**And** a person has moved pet-visits into Specification

**When** the session board reads pet-visits

```realization
Ticket -> Ticket.next
Ticket <- the first fidelity not done in Specification or an earlier stage: stories-story_map
```

**Then** Run next reads Run next: review on stories-story_map

### Scenario: Keep Run next off where it cannot run

Evidence: observed: ticket-client.spec 'should stay off with no chat to send to'; ticket-client.tsx runNextHint for a locked ticket.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) with generate next

**But** no chat is connected

**When** the Person looks at billing-report's Run next

**Then** Run next is off

**And** on a locked ticket it says Activate this session to run its next step

### Scenario: Name nothing to run on a ticket done in its stage

Evidence: observed: kanban_spec 'with every required fidelity in its stage done' — 'should have no next'; ticket-client.tsx runNextHint.

**Given** every Discovery fidelity of pet-visits is reviewed

**When** the session board reads pet-visits

```realization
Ticket -> Ticket.next <- none
```

**Then** Run next says Nothing to run next

---

## Choose Action And Formats

Actor: Person · Sub-epic: Generate Fidelity Outputs · File: `move-work-forward-on-session-board/generate-fidelity-outputs/choose-action-and-formats/choose_action_and_formats_story.test.py`

### Scenario: Pick the fidelity's default format

Evidence: observed: tile-client.spec 'should give each fidelity its default format'; kanban_tools_spec 'should give each fidelity its default format'.

**Given** billing-report's story_map [fidelity](kanban-model.md#fidelityguidance) has no file generated

**When** the Person opens the story_map tile

```realization
Board page -> Ticket.files(['stories-story_map'])
Ticket <- markdown tests/story-map.md, not there
```

**Then** the generate action is chosen with the markdown chip picked

### Scenario: Leave a generated format unpicked

Evidence: observed: tile-client.spec 'should not pick a format already generated'; register.test 'a format already generated carries a check' in the map.

**Given** billing-report's story map is tests/story-map.md, already there

**When** the Person opens the story_map tile

**Then** the markdown chip is green and not picked

### Scenario: Stand one chip for a group of formats

Evidence: observed: tile-client.spec 'should let a chip stand for a group', 'should give each fidelity its default format from a chip', 'with a format generated on one fidelity of two'.

**Given** billing-report's story map is generated in markdown and its bounded context is not

**When** the Person opens the Discovery stage head on story_map and bounded_context

**Then** the bar shows a diagram chip and a markdown chip

**And** the markdown chip reads 1 of 2 with the hint markdown: 1 of 2 done

### Scenario: Keep Run off with no format picked

Evidence: observed: tile-client.spec 'should keep Run off until a format is chosen'.

**Given** billing-report's story map is already in markdown

**But** no format is picked

**When** the Person looks at the story_map bar

**Then** Run is off

### Scenario: Keep Run off on a render with nothing to render

Evidence: observed: tile-client.spec 'should keep Run off on a render with nothing to render'.

**Given** billing-report's story map has no file

**When** the Person chooses render on the story_map bar

**Then** Run is off

### Scenario: Keep Run off with no chat or on a locked ticket

Evidence: observed: tile-client.spec 'should keep Run off with no chat connected', 'should keep Run off on a locked ticket'.

**Given** the story_map bar has the markdown chip picked

**But** no chat is connected, or the ticket is not the active session with Active session only on

**When** the Person looks at the story_map bar

**Then** Run is off

---

## Resolve Fidelity Output Paths

Actor: Claude Code · Sub-epic: Generate Fidelity Outputs · File: `move-work-forward-on-session-board/generate-fidelity-outputs/resolve-fidelity-output-paths/resolve_fidelity_output_paths_story.test.py`

### Scenario: Put a fidelity's files under its practice's root

Evidence: observed: space/session/session_spec.py 'should put each format's file under the practice's root folder'; harness/guidance/fidelity_outputs_spec.py 'should name the file for each format'.

**Given** the [session](kanban-model.md#session) alpha works in /work

**And** the story_map fidelity declares root tests, markdown story-map.md, and drawio story-map.drawio

**When** Claude Code asks where story_map's files go

```realization
Generate -> Session.fidelity_outputs(Stories story_map)
Session -> FidelityGuidance.outputs
Session <- markdown /work/tests/story-map.md, drawio /work/tests/story-map.drawio
```

**Then** the markdown file is /work/tests/story-map.md

### Scenario: Use the practice's root named in session.json

Evidence: observed: session_spec.py 'with session.json naming a root folder for the practice' — 'should use that root'.

**Given** alpha's session.json names docs/stories as the stories root

**When** Claude Code asks where story_map's files go

```realization
Generate -> Session.fidelity_outputs(Stories story_map)
```

**Then** the markdown file is /work/docs/stories/story-map.md

### Scenario: Prefer the fidelity's own root

Evidence: observed: session_spec.py 'with session.json naming a root folder for the fidelity too' — 'should prefer the fidelity's root'.

**Given** alpha's session.json names docs/stories for stories and docs/map for story_map

**When** Claude Code asks where story_map's files go

```realization
Generate -> Session.fidelity_outputs(Stories story_map)
```

**Then** the drawio file is /work/docs/map/story-map.drawio

### Scenario: Rename a single-file output and keep a pattern

Evidence: observed: session_spec.py 'with session.json naming a file for a single-file output' — 'should use that file name', 'should keep the declared name for the other formats'; 'with session.json naming a file for a patterned output' — 'should keep the declared pattern'.

**Given** alpha's session.json names our-map.md for story_map's markdown and one-file.py for scenarios' python

**When** Claude Code asks where story_map's and scenarios' files go

```realization
Generate -> Session.fidelity_outputs(Stories story_map)
Generate -> Session.fidelity_outputs(Stories scenarios)
```

**Then** story_map's markdown is /work/tests/our-map.md and its drawio stays /work/tests/story-map.drawio

**And** scenarios' python stays {story_snake}_story.test.py

---

## Generate Fidelity Output

Actor: Person · Sub-epic: Generate Fidelity Outputs · File: `move-work-forward-on-session-board/generate-fidelity-outputs/generate-fidelity-output/generate_fidelity_output_story.test.py`

### Scenario: Send the generate command from a tile

Evidence: observed: tile-client.spec 'Generate Fidelity Output' — 'should send the commands the ticket names', 'should clear the picks'; story-actions.spec 'should send the generate commands from Run on an opened card'.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) with nothing generated and a chat is connected

**And** its story_map bar has generate chosen and the markdown chip picked

**When** the Person runs generate on story_map

```realization
Person -> Ticket.generate_commands(['stories-story_map'], ['markdown'])
Ticket <- ['/actions-generate stories-story-map format=markdown']
Board page -> Chat.send('command', '/actions-generate stories-story-map format=markdown')
chat mod -> Chat.check_in() <- the command
chat mod -> Claude Code command.run('actions-generate', 'stories-story-map format=markdown')  [External: Claude Code]
```

**Then** the chat runs /actions-generate stories-story-map format=markdown

**And** the bar's picks are cleared

### Scenario: Render the earlier fidelity into a new format first

Evidence: observed: kanban_tools_spec 'with a fidelity's markdown generated' — 'should render the earlier fidelity into the new format first'; Ticket.generate_commands.

**Given** pet-visits' story map is docs/story-map.md, generated in markdown only

**When** the Person generates scenarios in drawio

```realization
Person -> Ticket.generate_commands(['stories-scenarios'], ['drawio'])
Ticket -> Session.fidelity_outputs(Stories story_map) <- markdown docs/story-map.md there, drawio not
```

**Then** the first command is /actions-render stories-story-map format=drawio source=markdown

**And** the last is /actions-generate stories-scenarios format=drawio

### Scenario: Count a generate line as Generate done

Evidence: observed: kanban_spec 'should show Generate done and Validate and Review remaining for that fidelity'.

**Given** the [session log](kanban-model.md#session) of pet-visits has no generate line for story_map

**When** Claude Code finishes generating the story map

```realization
Generate -> GuidanceAction.run(...)
GuidanceAction -> Session.log_guidance_action('generate', [Stories story_map])
```

**Then** the session log ends with a generate line naming stories story_map markdown

**And** the story_map tile marks Generate ✓

---

## Render Fidelity Format

Actor: Person · Sub-epic: Generate Fidelity Outputs · File: `move-work-forward-on-session-board/generate-fidelity-outputs/render-fidelity-format/render_fidelity_format_story.test.py`

### Scenario: Render existing output into another format

Evidence: observed: tile-client.spec 'Render Fidelity Format' — 'should turn existing output into the chosen format'.

**Given** billing-report's story map is tests/story-map.md, in markdown

**And** a chat is connected

**When** the Person renders story_map into the diagram format

```realization
Board page -> Chat.send('command', '/actions-render stories-story-map format=drawio')
```

**Then** the chat receives the command /actions-render stories-story-map format=drawio

### Scenario: Keep render off with nothing to render

Evidence: observed: tile-client.spec 'should keep Run off on a render with nothing to render'.

**Given** billing-report's story map has no file

**When** the Person chooses render on the story_map bar

**Then** Run is off

---

## Send Tile Action To Chat

Actor: Person · Sub-epic: Generate Fidelity Outputs · File: `move-work-forward-on-session-board/generate-fidelity-outputs/send-tile-action-to-chat/send_tile_action_to_chat_story.test.py`

### Scenario: Send sketch, iterate, or document as its own command

Evidence: observed: tile-client.spec 'Send Tile Action To Chat' — 'should send %s as its own command' for sketch, iterate, and document; story-actions.spec 'should send the chosen action on a tile'.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) and a chat is connected

**And** its story_map bar is open

**When** the Person runs sketch on story_map

```realization
Board page -> Chat.send('command', '/actions-sketch stories-story-map')
```

**Then** the chat receives the command /actions-sketch stories-story-map

**When** the Person runs iterate, then document, on story_map

```realization
Board page -> Chat.send('command', '/actions-iterate stories-story-map')
Board page -> Chat.send('command', '/actions-document stories-story-map')
```

**Then** the chat receives /actions-iterate stories-story-map, then /actions-document stories-story-map

### Scenario: Tell the person which chat got the command

Evidence: observed: chat-client.spec 'should choose the only chat connected', 'should choose none among several', 'should send once a person picks one of several', 'should send nothing with no chat chosen', 'should show the refusal of a chat that has gone'; Chat.send raises ChatNotConnectedError.

**Given** two chats are connected and none is picked

**When** the Person runs sketch on story_map

**Then** nothing is sent

**When** the Person picks a chat and runs sketch again

```realization
Board page -> Chat.send('command', '/actions-sketch stories-story-map')
```

**Then** a toast says Sent to the chat: /actions-sketch stories-story-map

---

## Validate Fidelity

Actor: Person · Sub-epic: Validate Fidelity Outputs · File: `move-work-forward-on-session-board/validate-fidelity-outputs/validate-fidelity/validate_fidelity_story.test.py`

### Scenario: Send the fidelity to validate

Evidence: observed: tile-client.spec 'Validate Fidelity' — 'should send the fidelity to validate', 'should allow Validate on files already there, with nothing recorded yet'.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) and a chat is connected

**And** its story map tests/story-map.md is there

**When** the Person validates story_map

```realization
Board page -> Chat.send('command', '/actions-validate stories-story-map')
```

**Then** the chat receives the command /actions-validate stories-story-map

### Scenario: Count Validate done only with no graph-rule violations

Evidence: observed: kanban_spec 'that has a validate with no violations' — 'should show Validate done for that fidelity'; 'that has a validate naming graph-rule violations' — 'should still need Validate for that fidelity'.

**Given** pet-visits' story map is generated

**When** Claude Code validates the story map and finds no graph-rule violation

```realization
Validate -> Graph.load_files(...)
Validate -> Session.log_validation(Stories story_map, [])
```

**Then** the session log ends with validate Stories story_map

**And** the story_map tile marks Validate ✓

**When** Claude Code validates it again and finds actor-named-in-step on map.md line 12

```realization
Validate -> Session.log_validation(Stories story_map, ['actor-named-in-step map.md:12'])
```

**Then** the session log ends with validate Stories story_map graph-rule actor-named-in-step map.md:12

**And** the story_map tile marks Validate as violations again

### Scenario: Keep Validate off with nothing to check

Evidence: observed: tile-client.spec 'should keep Validate off with no files and nothing recorded', 'should stay off until the ticket allows it'; kanban_tools_spec 'should allow only Generate before anything is generated'.

**Given** billing-report's story map has no file

**But** nothing is recorded on it

**When** the Person looks at the story_map bar

**Then** validate is off

### Scenario: Allow Validate again on the same output

Evidence: observed: kanban_tools_spec 'should allow Validate and Review again on the same output'.

**Given** checkout-flow's story map has violations

**When** the session board reads checkout-flow

```realization
Ticket -> Ticket.to_json() <- allowed_actions: generate, validate, review
```

**Then** validate is on for story_map

---

## Save Validation Report

Actor: Claude Code · Sub-epic: Validate Fidelity Outputs · File: `move-work-forward-on-session-board/validate-fidelity-outputs/save-validation-report/save_validation_report_story.test.py`

### Scenario: Save the report and the graph it checked

Evidence: observed: cdd_guidance/actions/validate/validate_spec.py 'should save the report in the session's reports folder, named after the fidelity and date', 'should save the graph it checked beside the report, under the same name', 'should keep the rule hits on the nodes of the saved graph', 'should say where the report is saved'.

**Given** the [session](kanban-model.md#session) checkout-flow has an entity root with a private-method-naming violation

**When** Claude Code validates ddd-tactics on that file

```realization
Validate -> Graph.load_files(folder, ['ddd'], [file], [])
Graph -> PracticeGraph.apply_rules(...)
Validate -> Graph.write_json(<report>.json)
Validate -> Session.log_validation(Ddd tactics, ['private-method-naming ...'])
```

**Then** the [validation report](kanban-model.md#validate--guidanceaction) is saved as validation-reports/ddd-tactics-<date>.md naming private-method-naming

**And** the graph it checked is saved beside it as ddd-tactics-<date>.json, with the rule hits on its nodes

**And** Claude Code's reply says where the report is saved

### Scenario: Save one report for each listed guidance

Evidence: observed: validate_spec.py 'should save a report for each listed guidance'.

**Given** the session checkout-flow has edited files for ddd-tactics and stories-scenarios

**When** Claude Code validates ddd-tactics and stories-scenarios together

**Then** validation-reports holds one stories-scenarios report and one ddd-tactics report

### Scenario: Leave an earlier report's graph as it was

Evidence: observed: validate_spec.py 'should leave an earlier report's saved graph as it was'.

**Given** validation-reports holds ddd-tactics-20200101T000000.json

**When** Claude Code validates ddd-tactics again

**Then** ddd-tactics-20200101T000000.json is unchanged

---

## Open Validation Report

Actor: Person · Sub-epic: Validate Fidelity Outputs · File: `move-work-forward-on-session-board/validate-fidelity-outputs/open-validation-report/open_validation_report_story.test.py`

### Scenario: Open a fidelity's latest report

Evidence: observed: kanban_tools_spec 'with validation reports saved for a fidelity' — 'should show that fidelity's latest report', 'should list each rule the report names with its violations', 'should give a violation the line it failed on', 'should show the source lines around a violation'; side-panel-client.spec 'Open Validation Report'; story-actions.spec 'should show the rules with the failing line marked'.

**Given** checkout-flow's story map has the [validation report](kanban-model.md#validate--guidanceaction) stories-story-map-20261101T100000.md with its saved graph

**And** the graph names verb-noun-format on tests/story-map.md line 6

**When** the Person opens checkout-flow's story_map report

```realization
Person -> Ticket.report('stories-story_map')
Ticket -> Ticket.reports <- .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md
Ticket <- path, text, rules from the saved graph, has_saved_graph: true
```

**Then** the report panel shows .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md

**And** it lists verb-noun-format with one violation at tests/story-map.md line 6 and the source lines around it

### Scenario: Show every fidelity's violations at once

Evidence: observed: side-panel-client.spec 'should show every fidelity's violations with no fidelity named'; kanban_tools_spec 'with violations left on two fidelities', 'should list a rule two fidelities share once'.

**Given** checkout-flow has violations

**When** the Person opens checkout-flow's violations from its card

```realization
Person -> Ticket.violations()
Ticket -> Ticket.report(each fidelity with violations)
```

**Then** the report panel shows .sessions/checkout-flow/validation-reports with every rule broken, each naming its fidelity

### Scenario: Say a report has no saved graph

Evidence: observed: kanban_tools_spec 'with a validation report saved without its graph' — 'should say a report has no saved graph', 'should still return the report's text'.

**Given** the ticket's latest story_map report has no graph saved beside it

**When** the Person opens the story_map report

```realization
Person -> Ticket.report('stories-story_map') <- rules: [], has_saved_graph: false
```

**Then** the report panel shows the report's text

**And** it says the report has no saved graph in place of saying it has no violations

### Scenario: Open a violation's file at its line

Evidence: observed: story-actions.spec 'should open a violation's file at its line in the Files panel'; side-panel-client.spec 'with a violation in a file its fidelity does not declare'.

**Given** checkout-flow's story_map report is open

**When** the Person opens the verb-noun-format violation

```realization
Person -> Ticket.read_file('tests/story-map.md')
```

**Then** the files panel shows tests/story-map.md with line 6 marked

### Scenario: Say there is no report

Evidence: observed: kanban_tools_spec 'should show no report for a fidelity that has none'.

**Given** billing-report has no validation report

**When** the session board reads billing-report

```realization
Ticket -> Ticket.reports <- none
```

**Then** the story_map bar shows no report link

---

## Fix Report Violations

Actor: Person · Sub-epic: Validate Fidelity Outputs · File: `move-work-forward-on-session-board/validate-fidelity-outputs/fix-report-violations/fix_report_violations_story.test.py`

### Scenario: Fix one violation at its line

Evidence: observed: side-panel-client.spec 'Fix Report Violations' — 'should send Fix for one violation at its line'; story-actions.spec 'should send Fix and Fix all to the chat'.

**Given** checkout-flow's story_map report lists verb-noun-format at tests/story-map.md line 6

**And** a chat is connected

**When** the Person fixes that violation

```realization
Board page -> Chat.send('command', fix message: the verb-noun-format rule, the error at tests/story-map.md:6, and the content that failed)
```

**Then** the chat receives one message naming the verb-noun-format rule, the error at tests/story-map.md:6, and the content that failed, with instructions to fix it

### Scenario: Fix every violation of a rule

Evidence: observed: side-panel-client.spec 'should send Fix all for every violation of a rule'.

**Given** checkout-flow's story_map report lists verb-noun-format

**When** the Person fixes every violation of verb-noun-format

```realization
Board page -> Chat.send('command', fix message: the verb-noun-format rule and every violation of it, each with its content)
```

**Then** the chat receives one message with every verb-noun-format violation, each at its file and line with the content that failed, and instructions to fix them

### Scenario: Read an open report again after the fix

Evidence: observed: side-panel-client.spec 'with a report and files open as the board changes' — 'should read the report again'.

**Given** checkout-flow's story_map report is open with verb-noun-format listed

**When** Claude Code validates the story map again with no violations

```realization
Validate -> Session.log_validation(Stories story_map, [])
Board page -> Board.show()
Board page -> Ticket.report('stories-story_map')
```

**Then** the open report lists no rules

---

## Display Violations Band

Actor: Board App · Sub-epic: Validate Fidelity Outputs · File: `move-work-forward-on-session-board/validate-fidelity-outputs/display-violations-band/display_violations_band_story.test.py`

### Scenario: Show the active ticket's violations in a band

Evidence: observed: board-page-view.tsx ViolationsBandView; story-actions.spec 'should name the active ticket's violations across the page top'.

**Given** checkout-flow is the active [ticket](kanban-model.md#ticket--card) with violations on stories-story_map

**When** the session board reads the board

```realization
Board page -> Board.show()
Board <- active ticket checkout-flow with progress violations on stories-story_map
```

**Then** a band across the page top names checkout-flow's violations

### Scenario: Show no band when the active ticket is clean

Evidence: observed: board-page-view.tsx draws the band only when the active ticket has violated fidelities.

**Given** billing-report is the active [ticket](kanban-model.md#ticket--card) with no violations

**When** the session board reads the board

**Then** no violations band shows

---

## List Ticket Files

Actor: Person · Sub-epic: Review Fidelity Outputs · File: `move-work-forward-on-session-board/review-fidelity-outputs/list-ticket-files/list_ticket_files_story.test.py`

### Scenario: List a fidelity's files with whether each exists

Evidence: observed: kanban_tools_spec 'with a fidelity's markdown generated' — 'should list the file with whether it exists', 'should list only the fidelities asked for'; side-panel-client.spec 'should list the files that exist'.

**Given** checkout-flow's story map tests/story-map.md is there and tests/story-map.drawio is not

**When** the Person lists checkout-flow's story_map files

```realization
Person -> Ticket.files(['stories-story_map'])
Ticket -> Session.fidelity_outputs(Stories story_map)
Ticket <- markdown tests/story-map.md exists, drawio tests/story-map.drawio missing
```

**Then** the files panel lists tests/story-map.md as there

**But** no file of another fidelity is listed

### Scenario: List only what the ticket's branch changed

Evidence: observed: kanban_tools_spec 'with specs in the repository and one changed on the ticket's branch' — 'should list only the files the ticket's branch changed'.

**Given** the [ticket](kanban-model.md#ticket--card) pet-visits works on the whole [repository](kanban-model.md#repo) on its own branch pet-visits

**And** the repository holds src/theirs_spec.py and its branch added src/mine_spec.py

**When** the Person lists pet-visits' bdd behavior files

```realization
Person -> Ticket.files(['bdd-behavior'])
Ticket -> Repo.files_changed_on('pet-visits')
```

**Then** the files panel lists src/mine_spec.py

**But** src/theirs_spec.py is not listed

### Scenario: Say in a toast when the list cannot be read

Evidence: observed: side-panel-client.spec 'with a list that cannot be read' — 'should say so in a toast', 'should open no panel'.

**Given** the board shows no ticket named no-such-ticket

**When** the Person lists no-such-ticket's story_map files

```realization
Person -> Ticket.load('no-such-ticket') <- TicketNotFoundError
```

**Then** a toast says cdd ticket.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board

**But** no panel opens

---

## Browse Ticket Folder

Actor: Person · Sub-epic: Review Fidelity Outputs · File: `move-work-forward-on-session-board/review-fidelity-outputs/browse-ticket-folder/browse_ticket_folder_story.test.py`

### Scenario: Group a stage's files under their folders

Evidence: observed: side-panel-client.spec 'Browse Ticket Folder' — 'should group the files under their folders'; story-actions.spec 'should show the three modes of the files panel'.

**Given** checkout-flow's Discovery files are tests/a.md, tests/deep/b.md, and src/c.ts

**When** the Person browses checkout-flow's Discovery files

```realization
Person -> Ticket.files(Discovery's enabled fidelities)
```

**Then** the files panel groups a.md and deep/b.md under tests/ and c.ts under src/

### Scenario: Browse the ticket's session folder

Evidence: observed: side-panel-client.spec 'Browse Ticket's Session Folder' — 'should list every file in the session folder', 'should show them as folders'; kanban_tools_spec 'with files in its session folder'.

**Given** checkout-flow's [session](kanban-model.md#session) folder holds its log and validation-reports/stories-story-map-20261101T100000.md

**When** the Person browses checkout-flow's session folder

```realization
Person -> Ticket.session_files()
```

**Then** the files panel lists .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md under its folder

---

## View Fidelity Files

Actor: Person · Sub-epic: Review Fidelity Outputs · File: `move-work-forward-on-session-board/review-fidelity-outputs/view-fidelity-files/view_fidelity_files_story.test.py`

### Scenario: Open one tab per format, generated or not

Evidence: observed: side-panel-client.spec 'View Fidelity Files' — 'should open one tab per format, generated or not', 'should read the text of the file a tab shows'; story-actions.spec 'should offer a tab for a format not generated yet and say so'; kanban_tools_spec 'should return the file's text'.

**Given** checkout-flow's story map is tests/story-map.md and tests/story-map.drawio is not there

**When** the Person views checkout-flow's story_map files

```realization
Person -> Ticket.files(['stories-story_map'])
Person -> Ticket.read_file('tests/story-map.md')
```

**Then** the files panel shows the tabs tests/story-map.md and tests/story-map.drawio

**And** the story-map.md tab shows # Check Out Order

**And** the drawio tab says it is not generated yet

### Scenario: Go back to the list when the last tab closes

Evidence: observed: side-panel-client.spec 'should go back to the list when the last tab closes', 'should keep a tab a person closed closed'.

**Given** the tabs tests/story-map.md and tests/story-map.drawio are open

**When** the Person closes both tabs

**Then** the files panel shows the list

### Scenario: Refuse a file outside the repository

Evidence: inferred: TicketFileError in Ticket.read_file; no spec reads a path outside the repository.

**Given** checkout-flow's repository is the project folder

**When** a file outside the repository is asked for

```realization
Person -> Ticket.read_file('../secrets.txt') <- TicketFileError
```

**Then** the board says ../secrets.txt is not a file in this repository

---

## Review Fidelity

Actor: Person · Sub-epic: Review Fidelity Outputs · File: `move-work-forward-on-session-board/review-fidelity-outputs/review-fidelity/review_fidelity_story.test.py`

### Scenario: Review a fidelity after a clean validate

Evidence: observed: kanban_tools_spec 'with a ticket whose story map has passed validate' — 'should name review as the next action', 'that a person has finished reviewing' — 'should show the fidelity's review done', 'should write the review to the session log'; kanban_spec 'should show the fidelity done'.

**Given** billing-report's story map is generated and its latest validate passed with no graph-rule

**When** the Person reviews story_map on billing-report

```realization
Person -> Ticket.finish_review(['stories-story_map'])
Ticket -> Ticket.record('review Stories story_map')
Board page -> Board.show()
```

**Then** billing-report's session log ends with review Stories story_map

**And** the story_map tile marks Review ✓ and the fidelity is done

**And** a toast says stories-story_map reviewed on billing-report

### Scenario: Keep Review off until Validate is clean

Evidence: observed: tile-client.spec 'should not allow Review until Validate is clean'.

**Given** billing-report's story map has no file

**But** nothing is recorded on it

**When** the Person looks at the story_map bar

**Then** review is off

### Scenario: Ignore a review recorded before a clean validate

Evidence: observed: kanban_spec 'that was reviewed before its validate passed' — 'should not count the review'.

**Given** pet-visits' session log has generate, then review, then validate Stories story_map

**When** the session board reads pet-visits

```realization
FidelityProgress -> FidelityProgress.from_log(...) <- done: generate, validate
```

**Then** the story_map tile marks Review ○

### Scenario: Refuse a fidelity the ticket does not have

Evidence: observed: kanban_tools_spec 'that a person names a fidelity the ticket does not have' — 'should refuse it, naming the fidelity', 'among fidelities it does have' — 'should write no review for the others named with it'.

**Given** billing-report's story map passed validate

**When** the Person reviews stories-story_map and stories-no_such_fidelity together

```realization
Person -> Ticket.finish_review(['stories-story_map', 'stories-no_such_fidelity']) <- FidelityNotFoundError
```

**Then** the board says no fidelity named stories-no_such_fidelity on this ticket

**But** no review line is written for stories-story_map

### Scenario: Complete a stage's work

Evidence: observed: kanban_spec 'with every required fidelity in its stage done' — 'should be done, waiting in its stage's done part', 'should have no next'.

**Given** pet-visits has every Discovery fidelity generated, validated, and reviewed

**When** the session board reads pet-visits

```realization
Stage -> Stage.done
Ticket -> Ticket.is_done <- true
```

**Then** pet-visits waits in Discovery's Done

**And** it has no next step
