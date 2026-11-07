# BDD Realization — Session Board

Fidelity: realization

Built from the knowledge graph of `space/kanban`: the spec tree is the graph's BDD nodes, in each spec file's order, and each `it should` holds the operations it calls, named as the graph's Clean Engineering nodes name them. The lines under an operation are its interactions in [kanban-model.md](kanban-model.md). `->` is a call and `<-` its return.

## behavior driven development:

<!-- spec: space/kanban/app/src/kanban/board/board-client.spec.ts -->

### Display Connected Status

```
it should show a band when the board read answers that cdd is not connected
-> BoardReader.refresh()
```

```
it should drop the band when cdd answers again
-> BoardStore.change({ serverFailure: 'lost' })
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> BoardReader.refresh()
```

```
it should read the board once to find that out
-> BoardStore.change({ serverFailure: 'lost' })
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> BoardReader.refresh()
```

```
it should drop the band when the chat list answers, because the chats are read through cdd
-> BoardStore.change({ serverFailure: 'lost' })
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> ChatClient.refresh()
```

#### with a tool failing

```
it should show no band
-> BoardReader.refresh()
```

```
it should show a toast
-> BoardReader.refresh()
```

##### that a person has restarted cdd

```
it should get the latest code, rebuild the page, then pin cdd to it
-> BoardPage.update()
-> BoardUpdate.update()
```

```
it should restart the board server once the update has answered
-> BoardPage.update()
-> BoardUpdate.restart()
```

```
it should load the page again from the restarted server
-> BoardPage.update()
-> BoardStore.change({ isNewBuild: true })
```

###### with a step that fails

```
it should say in a toast which step failed
-> BoardPage.update()
-> BoardUpdate.update()
<- UpdateStepFailed
```

```
it should keep the page it has
-> BoardPage.update()
```

```
it should keep the board server running
-> BoardPage.update()
-> BoardUpdate.update()
<- UpdateStepFailed
```

```
it should show the band when the server itself does not answer
-> BoardReader.refresh()
```

#### Refresh Board After Tool Calls

```
it should keep the newer board when an older read answers late
-> ChatClient.send(path, init)
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> BoardReader.refresh()
-> TicketClient.moveTo('Discovery', true)
  -> cdd ticket.move_to
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
-> TicketClient.isDone
  -> cdd board.show
    -> Ticket.is_done
    <- bool
```

#### Announce Ticket Changes

```
it should name the new column of a ticket that moves
-> TicketClient.moveTo('Discovery', true)
  -> cdd ticket.move_to
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
-> BoardReader.refresh()
```

```
it should name a fidelity that was reviewed
-> BoardReader.refresh()
```

```
it should say a ticket moved to the Backlog
-> TicketClient.movePrevious()
  -> cdd ticket.move_previous
    -> Ticket.move_previous()
    <- Ticket | BacklogItem
-> BoardReader.refresh()
```

```
it should raise nothing on each read of a session open and closed under one name
-> BoardReader.refresh()
```

```
it should raise nothing on the first read
-> BoardReader.refresh()
```

### Arrange Board And Details

#### Resize Board And Details

```
it should give the board the height a drag asks for
-> BoardLayoutClient.setBoardHeight(300, 900)
```

```
it should not let a drag close the board
-> BoardLayoutClient.setBoardHeight(10, 900)
```

```
it should not let a drag close the details
-> BoardLayoutClient.setBoardHeight(5000, 900)
```

#### Expand Board Or Details

```
it should give one region the page
-> BoardLayoutClient.toggleRegion('board')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

```
it should bring the other back on a second press
-> BoardLayoutClient.toggleRegion('board')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

### Set Stage WIP Limit

```
it should save a whole number
-> BoardClient.stageNamed('Discovery')
-> ColumnClient.submitWipLimit('4')
-> ActivationClient.show()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

```
it should read the board again
-> BoardClient.stageNamed('Discovery')
-> ColumnClient.submitWipLimit('4')
-> BoardClient.stageNamed('Discovery')
-> ColumnClient.wipLimit
```

```
it should change nothing for a limit that is not a number
-> BoardClient.stageNamed('Discovery')
-> ColumnClient.submitWipLimit('many')
```

```
it should send the header the server asks of a page on this machine
-> BoardClient.stageNamed('Discovery')
-> ColumnClient.submitWipLimit('4')
```

### Display Ticket Details

```
it should show the active ticket with no card pressed
-> BoardPage.board
-> BoardClient.selectedTicket
```

```
it should show the ticket worked on last with none active
-> BoardPage.board
-> BoardClient.selectedTicket
```

```
it should tell a closed session from an open one of the same name
-> BoardPage.board
-> BoardClient.select('Complete/billing-report')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> BoardClient.selectedTicket
```

### Display Ticket Card

```
it should say one hour in the singular
-> board-brand.ageOf(Date.parse)
```

```
it should say how many hours ago its ticket was worked on
-> board-brand.ageOf(Date.parse)
```

```
it should say a ticket with no activity has none
-> board-brand.ageOf(Date.parse)
```

<!-- spec: space/kanban/app/src/kanban/board/build-client.spec.ts -->

### Reload Page On New Build

```
it should keep the page while the server serves the build it loaded
-> BuildClient.check()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

#### with a new build deployed after the page loaded

```
it should ask for the page to be loaded again
-> ChatClient.send(path, init)
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> BuildClient.check()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

<!-- spec: space/kanban/app/src/kanban/ticket/ticket-client.spec.ts -->

### Restrict Actions To Active Session

```
it should lock a ticket that is not the active session
-> TicketClient.isLocked
```

```
it should leave the active ticket open
-> TicketClient.isLocked
```

```
it should unlock every ticket with Active session only off
-> BoardLayoutClient.toggleOnlyActive()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> TicketClient.isLocked
```

### Display Ticket Details

```
it should say what runs next
-> TicketClient.nextNote
```

```
it should say another session must be activated to run it
-> TicketClient.lockNote
```

```
it should name a split ticket by its parent
-> TicketClient.origin
```

```
it should name the ticket's stage and how far it has got there
-> TicketClient.stagePlace
```

```
it should keep a practice with two words in its skill
// the graph holds no operation this observation calls
```

### Review Fidelity

#### with a story map that has passed validate

```
it should offer the review with no chat connected, since it is the person\'s own approval
-> BoardLayoutClient.toggleOnlyActive()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> TicketClient.canRunNext
```

```
it should show the review done once Run next records it
-> BoardLayoutClient.toggleOnlyActive()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> TicketClient.runNext()
-> TicketClient.actionsOf('stories-story-map')
```

### Move Ticket

```
it should read the board again and select the ticket where it landed
-> TicketClient.moveNext()
  -> cdd ticket.move_next
    -> Ticket.move_next()
    <- Ticket
```

```
it should select a dragged ticket in the stage it was dropped on
-> TicketClient.moveTo('Implementation', true)
  -> cdd ticket.move_to
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
```

#### that a person has moved to the Backlog

```
it should let go of what was open on it
-> BoardStore.change({ openCard: 'back-to-backlog' })
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> TicketClient.movePrevious()
  -> cdd ticket.move_previous
    -> Ticket.move_previous()
    <- Ticket | BacklogItem
```

```
it should select its item
-> BoardStore.change({ openCard: 'back-to-backlog' })
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> TicketClient.movePrevious()
  -> cdd ticket.move_previous
    -> Ticket.move_previous()
    <- Ticket | BacklogItem
```

```
it should let a ticket in any column be dropped on the Backlog
-> TicketClient.dropOn('Backlog')
  -> TicketClient.moveTo()
    -> cdd ticket.move_to
      -> Ticket.move_to(stage: str, done: bool)
        -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
        <- BacklogItem
      <- Ticket | BacklogItem
  -> ActivationClient.start()
    -> Ticket.branch()
    -> ActivationClient.show()
      -> BoardStore.change()
        -> board-store.saveLayout()
        -> BoardStore.dismissToast()
  -> TicketClient.moveNext()
    -> cdd ticket.move_next
      -> Ticket.move_next()
      <- Ticket
-> BoardPage.board
-> BoardClient.backlogItems()
  -> cdd board.show
    -> Board.backlog_items
    <- list[BacklogItem]
```

```
it should let only the active ticket, or one done in Implementation, be dropped on Complete
-> TicketClient.canDropOn('Complete')
```

### Send Next Fidelity Action

```
it should name the step that runs next
-> TicketClient.runNextLabel
```

```
it should say fix violations on held violations
-> TicketClient.runNextLabel
```

#### with generate next

```
it should send the generate command in the default format
-> TicketClient.runNext()
```

#### with generate next on a fidelity of a stage the ticket has moved past

```
it should generate it in its own stage's default format
-> TicketClient.runNext()
```

```
it should mark its tile as the next one
-> TicketClient.runNext()
-> BoardPage.board
-> BoardClient.stageNamed('Discovery')
-> TicketClient.isNext(discovery, 'stories-story-map')
```

```
it should fill the prompt on validate
-> TicketClient.runNext()
```

#### with violations held and no chat connected

```
it should still offer Run next
-> TicketClient.canRunNext
```

```
it should open the report
-> TicketClient.runNext()
```

```
it should stay off with no chat to send to
-> TicketClient.canRunNext
```

### Choose Ticket Practices

```
it should let go of the tile of a practice turned off
-> BoardStore.change({ tiles: [{ ticket: ACTIVE, place: 'cell-Discovery-ddd-bounded-context', stage:)
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> TicketClient.enablePractice('ddd', false)
  -> cdd practice-session-output.enable
    -> PracticeSessionOutput.enable(is_enabled: bool)
      -> PracticeSessionOutput.enabled
      <- bool
    <- PracticeSessionOutput
-> BoardPage.tiles
```

```
it should say so and where it was saved
-> BoardStore.change({ tiles: [{ ticket: ACTIVE, place: 'cell-Discovery-ddd-bounded-context', stage:)
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> TicketClient.enablePractice('ddd', false)
  -> cdd practice-session-output.enable
    -> PracticeSessionOutput.enable(is_enabled: bool)
      -> PracticeSessionOutput.enabled
      <- bool
    <- PracticeSessionOutput
```

### Write Ticket Handoff

```
it should fill the prompt with the handoff command
-> TicketClient.fillHandoff()
```

### Close Active Session

```
it should send the close session command to the chat
-> TicketClient.closeSession()
```

```
it should leave the ticket in its column
-> TicketClient.closeSession()
-> TicketClient.column
  -> cdd board.show
    -> Ticket.column
    <- Column
```

<!-- spec: space/kanban/app/src/kanban/ticket/ticket-views.spec.ts -->

### a generated ticket view

```
it should show a field no operation changes as read-only
// the graph holds no operation this observation calls
```

```
it should offer an operation with no arguments as a button
// the graph holds no operation this observation calls
```

```
it should give an operation with arguments a form for them
// the graph holds no operation this observation calls
```

#### with a field the page draws itself

```
it should draw the page’s own field in its place
// the graph holds no operation this observation calls
```

### a generated ticket client

#### that an operation has answered with new state

```
it should tell what is drawing it to draw again
// the graph holds no operation this observation calls
```

#### that the page has stopped listening to

```
it should not tell it again
// the graph holds no operation this observation calls
```

<!-- spec: space/kanban/app/src/kanban/ticket/tile-client.spec.ts -->

### Choose Action And Formats

```
it should give each fidelity its default format
-> tile-formats.defaultPicks(STAGE, [SLUG], NOTHING_MADE)
  -> tile-formats.chipsOf()
```

```
it should not pick a format already generated
-> tile-formats.defaultPicks(STAGE, [SLUG], MARKDOWN_MADE)
  -> tile-formats.chipsOf()
```

```
it should let a chip stand for a group
-> tile-formats.chipsOf(STAGE, TWO_SLUGS)
```

```
it should give each fidelity its default format from a chip
-> tile-formats.chosenFormats(STAGE, TWO_SLUGS, ['markdown'])
  -> tile-formats.chipsOf()
```

#### with a format generated on one fidelity of two

```
it should count how many fidelities it is generated on
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

```
it should say so in its hint
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

```
it should keep Run off until a format is chosen
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

```
it should keep Run off on a render with nothing to render
-> BoardPage.tiles
-> TileActionsClient.chooseAction(barAt)
  -> TileActionsClient.save()
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

```
it should keep Run off on a locked ticket
-> TileActionsClient.barOf(ticketOn)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
-> TileClient.openOn('move-me', PLACE)
```

```
it should keep Run off with no chat connected
-> BoardStore.change({ targetChat: null })
  -> board-store.saveLayout()
  -> BoardStore.dismissToast()
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

### Validate Fidelity

```
it should allow Validate on files already there, with nothing recorded yet
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

```
it should keep Validate off with no files and nothing recorded
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

```
it should link to the report of the fidelity left with violations
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

### Generate Fidelity Output

```
it should send the generate command for the picked formats
-> BoardPage.tiles
-> TileActionsClient.run(barAt)
-> TestChat.checkIn()
```

```
it should clear the picks
-> BoardPage.tiles
-> TileActionsClient.run(barAt)
```

### Render Fidelity Format

```
it should turn existing output into the chosen format
-> BoardPage.tiles
-> TileActionsClient.chooseAction(barAt)
  -> TileActionsClient.save()
-> TileActionsClient.toggleFormat(barAt)
  -> TileActionsClient.save()
-> TileActionsClient.run(barAt)
-> TestChat.checkIn()
```

### Send Tile Action To Chat

### Validate Fidelity

```
it should send the fidelity to validate
-> BoardPage.tiles
-> TileActionsClient.validate(barAt)
-> TestChat.checkIn()
```

```
it should stay off until the ticket allows it
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

### Review Fidelity

```
it should not allow Review until Validate is clean
-> BoardPage.tiles
-> TileActionsClient.barOf(ticket, STAGE, barAt)
  -> tile-actions-client.validateFaceOf()
  -> tile-formats.chipsOf()
  -> tile-actions-client.chipFaceOf()
  -> tile-actions-client.reportSlugOf()
```

### Send Action To Stage Practices

```
it should name every fidelity of the stage in one command
-> BoardPage.tiles
-> ColumnClient.workRequired
-> TileActionsClient.chooseAction(barAt)
  -> TileActionsClient.save()
-> TileActionsClient.run(barAt)
-> TestChat.checkIn()
```

### Open Practice Tile

```
it should open a tile after a short hover
-> TileClient.hoverIn(spot)
```

```
it should show the bar before its files are read
-> BoardPage.tiles
```

```
it should pick formats from the files once they are read
-> BoardPage.tiles
```

```
it should close it on leaving
-> TileClient.hoverOut(TICKET, PLACE)
  -> TileClient.close()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

```
it should keep a tile a person pressed open after the pointer leaves
-> TileClient.toggle(ticket, spot)
-> TileClient.hoverOut(TICKET, PLACE)
  -> TileClient.close()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

```
it should close on a second press
-> TileClient.toggle(ticket, spot)
```

#### with two tiles pressed

```
it should keep both bars open
-> TileClient.toggle(ticket, spot)
```

```
it should close only the bar pressed again
-> TileClient.toggle(ticket, spot)
```

```
it should change only that bar's action
-> TileClient.toggle(ticket, spot)
-> TileActionsClient.chooseAction(barAt)
  -> TileActionsClient.save()
-> BoardPage.tiles
```

#### with a pressed bar and a bar a hover opened

```
it should open the hovered bar beside the pressed one
-> TileClient.toggle(ticket, spot)
-> TileClient.hoverIn(spot)
```

```
it should replace the hovered bar with the next one a hover opens, and keep the pressed one
-> TileClient.toggle(ticket, spot)
-> TileClient.hoverIn(spot)
```

```
it should close the hovered bar on leaving, and keep the pressed one
-> TileClient.toggle(ticket, spot)
-> TileClient.hoverIn(spot)
-> TileClient.hoverOut(TICKET, OTHER_PLACE)
  -> TileClient.close()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

#### with two stage heads pressed

```
it should keep both stage bars open
-> BoardPage.board
-> BoardClient.stageNamed('Specification')
-> TileClient.toggle(ticket, spot)
-> ColumnClient.workRequired
```

### Expand Ticket

```
it should open with its tiles only, each opening its own action bar
-> OpenCardClient.toggle(ticket)
-> BoardPage.tiles
```

```
it should expand only one card at a time
-> OpenCardClient.toggle(ticket)
```

#### with a segment pressed

```
it should open the card
-> OpenCardClient.openSegment(ticket, STAGE, SLUG)
```

```
it should open the tile of that fidelity
-> OpenCardClient.openSegment(ticket, STAGE, SLUG)
```

```
it should move an open bar to the tile the ticket works on next when it moves
-> BoardPage.tiles
-> OpenCardClient.follow(ticket)
```

### Refresh Board After Tool Calls

```
it should read an open bar's files again when the board changes
-> BoardPage.tiles
-> BoardReader.refresh()
```

<!-- spec: space/kanban/app/src/kanban/board/side-panel-client.spec.ts -->

### List Ticket Files

```
it should list the files that exist
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'folder')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

#### with a list that cannot be read

```
it should say so in a toast
-> BoardApi.refused()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> FilesPanelClient.openFiles('no-such-ticket', [SLUG], 'folder')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

```
it should open no panel
-> BoardApi.refused()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> FilesPanelClient.openFiles('no-such-ticket', [SLUG], 'folder')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

### Browse Ticket Folder

```
it should group the files under their folders
// the graph holds no operation this observation calls
```

### Browse Ticket's Session Folder

```
it should list every file in the session folder
-> FilesPanelClient.openSessionFolder(TICKET)
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

```
it should show them as folders
-> FilesPanelClient.openSessionFolder(TICKET)
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

#### with its latest handoff opened

```
it should show the handoff in a tab
-> FilesPanelClient.openSessionFile(TICKET, HANDOFF)
```

```
it should read the handoff's text
-> FilesPanelClient.openSessionFile(TICKET, HANDOFF)
```

### View Fidelity Files

```
it should open one tab per format, generated or not
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'files')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

```
it should keep markdown before code before diagrams
// the graph holds no operation this observation calls
```

```
it should read the text of the file a tab shows
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'files')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
```

```
it should go back to the folder when the last tab closes
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'files')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
-> FilesPanelClient.closeTab('.context/story-map.md')
```

#### with a violation in a file its fidelity does not declare

```
it should open that file
-> FilesPanelClient.openFileAtLine(TICKET, SLUG, 'src/other.py', FAILING_LINE)
```

```
it should mark the line it failed on
-> FilesPanelClient.openFileAtLine(TICKET, SLUG, 'src/other.py', FAILING_LINE)
```

### Open Validation Report

```
it should show that fidelity's latest report
-> SidePanelClient.openReport(TICKET, SLUG)
-> SidePanelClient.reportPanel(page)
```

```
it should show every fidelity's violations with no fidelity named
-> SidePanelClient.openReport(TICKET, '')
-> SidePanelClient.reportPanel(page)
```

### Fix Report Violations

#### with Fix pressed on one violation

```
it should send one message to the chat
-> TicketClient.fixViolation(rule, violation)
```

```
it should name the rule and what it requires
-> TicketClient.fixViolation(rule, violation)
```

```
it should give the error at its file and line
-> TicketClient.fixViolation(rule, violation)
```

```
it should quote the content that failed
-> TicketClient.fixViolation(rule, violation)
```

```
it should name the ticket's session
-> TicketClient.fixViolation(rule, violation)
```

#### with Fix all pressed on a rule

```
it should send every violation of the rule in one message
-> TicketClient.fixRule(report, rule)
```

#### with Fix all pressed on the whole report

```
it should send one message to the chat
-> SidePanelClient.openReport(TICKET, '')
-> SidePanelClient.reportPanel(page)
-> TicketClient.fixReport(report)
  -> report-client.fixReportPrompt()
```

```
it should name every rule the report breaks
-> SidePanelClient.openReport(TICKET, '')
-> SidePanelClient.reportPanel(page)
-> TicketClient.fixReport(report)
  -> report-client.fixReportPrompt()
```

```
it should give every violation of every rule
-> SidePanelClient.openReport(TICKET, '')
-> SidePanelClient.reportPanel(page)
-> TicketClient.fixReport(report)
  -> report-client.fixReportPrompt()
```

### Refresh Board After Tool Calls

#### with a report and files open as the board changes

```
it should read the report again
-> TileClient.changed()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> SidePanelClient.openReport(TICKET, SLUG)
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'folder')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
-> BoardReader.refresh()
-> SidePanelClient.reportPanel(await changed)
-> ReportClient.rules
```

```
it should read the files again
-> TileClient.changed()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> SidePanelClient.openReport(TICKET, SLUG)
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'folder')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
-> BoardReader.refresh()
```

```
it should keep a tab a person closed closed
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'files')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
-> FilesPanelClient.closeTab('.context/story-map.drawio')
-> SidePanelClient.reload()
```

### Arrange Side Panel

#### Resize Side Panel

```
it should set the width a drag asks for
-> SidePanelClient.setWidth('files', 700)
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> SidePanelClient.widthOf('files')
```

```
it should not go narrower than the smallest width
-> SidePanelClient.setWidth('files', 10)
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
-> SidePanelClient.widthOf('files')
```

#### Expand Side Panel

```
it should expand one panel at a time
-> SidePanelClient.openReport(TICKET, SLUG)
-> FilesPanelClient.openFiles(TICKET, [SLUG], 'folder')
  -> FilesPanelClient.openPanel()
    -> FilesPanelClient.chooseMode()
      -> FilesPanelClient.openTab()
        -> FilesPanelClient.textOf()
-> SidePanelClient.toggleExpanded('report')
```

#### Close Side Panel

```
it should close the panel
-> SidePanelClient.openReport(TICKET, SLUG)
-> SidePanelClient.close('report')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

<!-- spec: space/kanban/app/src/kanban/ticket/activation-client.spec.ts -->

### Activate Ticket

```
it should offer commit and push on leaving and open with merge off
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

```
it should offer a branch to a ticket that has none
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> TileClient.opening
```

```
it should choose nothing to leave when the session has no branch
-> ActivationClient.start(ticketOn)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

```
it should say what it switches from and to
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

#### that a person has confirmed with merge chosen

```
it should send what was chosen
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.toggleLeaving('merge')
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.confirm()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
  -> ActivationClient.activateSession()
    -> activation-client.reportOf()
```

```
it should report it
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.toggleLeaving('merge')
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.confirm()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
  -> ActivationClient.activateSession()
    -> activation-client.reportOf()
```

#### that a person has cancelled

```
it should close the dialog
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.cancel()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> BoardPage.activation
```

```
it should send nothing
-> ActivationClient.start(chosen, false)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.cancel()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

### Close Active Session

```
it should ask what to do with its work
-> ActivationClient.start(active, true)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> BoardPage.activation
```

```
it should send what to do with its work
-> ActivationClient.start(active, true)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.confirm()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
  -> ActivationClient.activateSession()
    -> activation-client.reportOf()
```

```
it should select the ticket in Complete
-> ActivationClient.start(active, true)
  -> Ticket.branch()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ActivationClient.confirm()
  -> ActivationClient.show()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
  -> ActivationClient.activateSession()
    -> activation-client.reportOf()
```

<!-- spec: space/kanban/app/src/kanban/backlog-item/backlog-item-client.spec.ts -->

### Add Backlog Item

```
it should stay off with no title
-> BoardPage.draft
```

#### with a title and text typed

```
it should write the title and text
-> BoardPage.draft
-> ActivationClient.show()
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
```

```
it should select the item
-> BoardPage.draft
```

```
it should say so in a toast
-> BoardPage.draft
```

```
it should close the form
-> BoardPage.draft
```

#### Start Backlog Item

```
it should open a ticket and select it, with the title safe in the path
-> BoardPage.board
-> BoardClient.backlogItems()
  -> cdd board.show
    -> Board.backlog_items
    <- list[BacklogItem]
```

```
it should say so in a toast
-> BoardPage.board
-> BoardClient.backlogItems()
  -> cdd board.show
    -> Board.backlog_items
    <- list[BacklogItem]
```

<!-- spec: space/kanban/app/src/kanban/ticket/root-choice-client.spec.ts -->

### Choose Session Root

#### with the roots of a ticket open

```
it should show the ticket's practices with their roots
-> BoardPage.roots
-> RootChoiceClient.ticket
```

##### that a person browses into a folder for the session root

```
it should list the folders inside it
-> RootChoiceClient.browse(TICKET_ROOT, 'src')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> board-store.browsing(await browsed)
```

```
it should go back up to the top of the repository
-> RootChoiceClient.browse(TICKET_ROOT, 'src')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.up()
  -> RootChoiceClient.browse()
    -> Board.folders()
    -> RootChoiceClient.change()
      -> BoardStore.change()
        -> board-store.saveLayout()
        -> BoardStore.dismissToast()
-> board-store.browsing(page)
```

###### and uses it

```
it should make it the ticket's root
-> RootChoiceClient.browse(TICKET_ROOT, 'src/visits')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.use()
```

```
it should go back to the list of roots
-> RootChoiceClient.browse(TICKET_ROOT, 'src/visits')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.use()
-> board-store.browsing(await used)
```

##### that a person chooses a folder for one practice's root

```
it should show it as that practice's chosen root
-> RootChoiceClient.browse('stories', 'src/billing')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.use()
```

###### and then goes back to its default

```
it should show the practice on its default root
-> RootChoiceClient.browse('stories', 'src/billing')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.use()
-> RootChoiceClient.useDefault('stories')
-> TicketClient.session
  -> cdd board.show
    -> Ticket.session
    <- Session
-> Session.practices
<- dict[str, PracticeSessionOutput]
-> PracticeSessionOutput.is_root_chosen
<- bool
```

#### with a backlog item a person has asked to start

```
it should browse the top of the repository for its root before it starts
-> RootChoiceClient.openToStart(page.board.backlogItems.find)
-> BoardPage.board
-> BoardClient.backlogItems()
  -> cdd board.show
    -> Board.backlog_items
    <- list[BacklogItem]
-> board-store.browsing(await asked)
```

```
it should not start it yet
-> RootChoiceClient.openToStart(page.board.backlogItems.find)
-> BoardPage.board
-> BoardClient.backlogItems()
  -> cdd board.show
    -> Board.backlog_items
    <- list[BacklogItem]
```

##### that a person has started in a folder

```
it should open its ticket with that folder as its root
-> RootChoiceClient.browse(TICKET_ROOT, 'src/visits')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.use()
```

```
it should stay open on the new ticket's roots, so its practices' roots can be set
-> RootChoiceClient.browse(TICKET_ROOT, 'src/visits')
  -> Board.folders()
  -> RootChoiceClient.change()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> RootChoiceClient.use()
```

<!-- spec: space/kanban/app/src/kanban/chat/chat-client.spec.ts -->

### Send commands to a chat

```
it should choose the only chat connected
-> ChatClient.refresh()
```

```
it should choose the first of several when none has been picked
-> ChatClient.refresh()
```

```
it should choose again the chat a person picked once it is back
-> ChatClient.choose('chat-2')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ChatClient.refresh()
```

```
it should send once a person picks one of several
-> ChatClient.refresh()
-> ChatClient.choose('chat-2')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ChatClient.canSend
```

```
it should keep a picked chat while it stays connected
-> ChatClient.choose('chat-2')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ChatClient.refresh()
```

```
it should let go of a chat that has gone
-> ChatClient.choose('chat-2')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ChatClient.refresh()
-> ChatClient.canSend
```

```
it should send nothing with no chat chosen
-> ChatClient.command('/actions-validate a')
```

```
it should send a skill as a command
-> ChatClient.command('/actions-validate a')
```

```
it should name the chat a command went to and the whole command
-> ChatClient.refresh()
-> ChatClient.choose('chat-2')
  -> BoardStore.change()
    -> board-store.saveLayout()
    -> BoardStore.dismissToast()
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
-> ChatClient.command('/actions-validate stories-story-map session=.sessions/checkout-flow/session.jso)
```

#### with the chat's messages

```
it should show them, the latest first
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
```

```
it should show a message as waiting until the chat takes it
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
```

```
it should show a message as taken, not yet shown, once the chat has taken it
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
-> ChatClient.refresh()
```

```
it should say why the chat could not show a message
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
-> ChatClient.refresh()
```

```
it should show a message as done once the chat has finished working on it
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
-> ChatClient.refresh()
```

```
it should put a message the chat did not show back in its queue when a person resends it
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
-> ChatClient.refresh()
-> ChatClient.resend(failed.message)
```

```
it should no longer show a message a person removes
-> ChatClient.command('/actions-validate a')
-> ChatClient.fill('Split this')
-> ChatClient.remove(page.store.state.messages[0]!.message)
  -> ChatClient.readMessages()
    -> BoardStore.change()
      -> board-store.saveLayout()
      -> BoardStore.dismissToast()
```

```
it should tell the person a fill is queued for review
-> ChatClient.fill('Split this')
```

```
it should say a fill waits for the turn to end while the chat is busy
-> ChatClient.fill('Split this')
```

```
it should show the refusal of a chat that has gone
-> ChatClient.command('/actions-validate a')
```

<!-- spec: space/kanban/app/src/kanban/board/help-text.spec.ts -->

### Open Help

```
it should drop the section heading the panel already says
-> help-text.helpBlocksOf('#### Overview\n\nScope the solution.')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should keep a lead in bold and code as code
-> help-text.helpBlocksOf('**Name the layers.** Actors are `people`.')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should show a link\'s words, with no address to follow
-> help-text.helpBlocksOf('Read [the tools](../tools.md).')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should keep a list as a list
-> help-text.helpBlocksOf('- one\n- two')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should keep a fenced block as written
-> help-text.helpBlocksOf('Before\n\n```\nhello\n\n  there\n```\n\nAfter')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should keep a table as written
-> help-text.helpBlocksOf('| a | b |\n|---|---|\n| 1 | 2 |')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should keep a heading inside the text
-> help-text.helpBlocksOf('First\n\n## Later\n\nSecond')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

```
it should give nothing for no text
-> help-text.helpBlocksOf('')
  -> help-text.textBlocksOf()
    -> help-text.textBlockOf()
```

<!-- spec: space/kanban/app/tests/kanban/wip-limits/wip_limits.spec.shared.ts -->

### a board

```
it should give every stage a limit of 3 tickets until a person sets one
-> Stage.wip_limit
<- int
```

```
it should leave a stage holding fewer tickets than its limit within it
// the graph holds no operation this observation calls
```

#### that sets a stage's limit below the tickets it holds

```
it should show the stage over its limit
-> Stage.set_wip_limit(stage='Specification', limit=1)
<- Stage
```

<!-- spec: space/kanban/app/tests/kanban/move-ticket/move_ticket.spec.shared.ts -->

### a ticket

#### that a person has moved to the next column

```
it should show the ticket in the next stage
-> Ticket.move_next('ready-to-move')
<- Ticket
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

```
it should show the ticket in progress there
-> Ticket.move_next('ready-to-move')
<- Ticket
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

#### with that stage's work not done

```
it should show the ticket in that stage's Done all the same
-> Ticket.move_next('move-me')
<- Ticket
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

##### and back from Done

```
it should show the ticket in progress in that stage
-> Ticket.move_previous('move-me')
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

#### that a person has dragged into a later stage's Done

```
it should show the ticket in that stage's Done
-> Ticket.move_to('move-me', 'Implementation', true)
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

#### that a person has dragged into the Backlog from a later stage

```
it should show an item in the Backlog with the ticket's title
-> Ticket.move_to('pricing-rules', 'Backlog', false)
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
-> Board.backlog_items
<- list[BacklogItem]
```

```
it should take the ticket off the board's stages
-> Ticket.move_to('pricing-rules', 'Backlog', false)
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
-> Board.tickets
<- list[Ticket]
```

#### that a person has moved back to the previous column

```
it should show the ticket in Discovery
-> Ticket.move_previous('pricing-rules')
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

```
it should show the ticket in Discovery's Done
-> Ticket.move_previous('pricing-rules')
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

#### that a person has moved back out of Discovery

```
it should show an item in the Backlog with the ticket's title
-> Ticket.move_previous('back-to-backlog')
<- Ticket | BacklogItem
-> Board.backlog_items
<- list[BacklogItem]
```

```
it should take the ticket off the board's stages
-> Ticket.move_previous('back-to-backlog')
<- Ticket | BacklogItem
-> Board.tickets
<- list[Ticket]
```

#### that a person has moved past Implementation

```
it should close the ticket
-> Ticket.move_next('almost-shipped')
<- Ticket
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

##### and back again

```
it should reopen the ticket in Implementation
-> Ticket.move_previous('almost-shipped')
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

<!-- spec: space/kanban/app/tests/kanban/backlog-items/backlog_items.spec.shared.ts -->

### a backlog item

#### that a person has added

```
it should show the item in the Backlog with its text
// the graph holds no operation this observation calls
```

#### that a person has started

```
it should return the new ticket in Discovery
-> BacklogItem.start('Search the catalog')
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

```
it should take the item off the Backlog
-> BacklogItem.start('Search the catalog')
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

#### that holds a ticket moved back out of Discovery

```
it should bring the ticket back with its work
-> BacklogItem.start('Back to backlog')
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

<!-- spec: space/kanban/app/tests/kanban/files-and-reports/files_and_reports.spec.shared.ts -->

### a ticket

#### with a fidelity's markdown generated

```
it should list the file with whether it exists
-> FidelityProgress.files(ticket=TICKET, fidelity=FIDELITY)
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

```
it should return the file's text
-> Session.read_file(path=STORY_MAP)
<- dict
```

#### with validation reports saved for a fidelity

```
it should show that fidelity's latest report
-> FidelityProgress.report(ticket=TICKET, fidelity=FIDELITY)
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should list each rule the report names with its violations
-> FidelityProgress.report(ticket=TICKET, fidelity=FIDELITY)
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should give a violation the line it failed on
-> FidelityProgress.report(ticket=TICKET, fidelity=FIDELITY)
  -> ReportFile.report()
  <- Report
<- Report
```

<!-- spec: space/kanban/kanban_spec.py -->

### a board

#### with Stories, DDD, and UX chosen

```
it should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order
-> Board.column("Discovery")
<- Column
-> Board.columns
<- list[Column]
```

```
it should have story_map, bounded_context, and ia as Discovery's work required
-> Board.column("Discovery")
<- Column
```

```
it should give every stage Generate, Validate, and Review, in that order
-> Board.column("Discovery")
<- Column
```

#### with BDD chosen

```
it should have behavior as Discovery's work required
-> Board.column("Discovery")
<- Column
```

```
it should have realization as Specification's work required
-> Board.column("Specification")
<- Column
```

#### that has been loaded with no practices given

```
it should choose every practice
-> Board.load(SessionsFolder)
<- Board
-> Board.practices
<- list[PracticeGuidance]
```

```
it should share its practices with every other board loaded in the process, since they do not change between calls
-> Board.load(SessionsFolder)
<- Board
-> Board.practices
<- list[PracticeGuidance]
```

#### of a project named by a folder inside its checkout

```
it should show the board of the whole checkout, where sessions keep their folders
-> Board.load(project)
<- Board
-> Board.repo
<- Repo
```

#### with no session saved as open

```
it should have no active ticket, since main is not on the board
-> Board.active
  -> Sessions.saved
  <- Session
<- Ticket
```

#### with a sessions folder of work sessions, closed sessions, default, backlog items, and archived sessions

```
it should show every work session as a ticket
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.tickets
<- list[Ticket]
```

```
it should leave main off the board
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.tickets
<- list[Ticket]
```

```
it should show each backlog item in the Backlog column
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.column("Backlog")
<- Column
-> Column.cards
  -> Board.cards
  <- list[Card]
  -> Card.column
  <- Column
<- list[Card]
```

```
it should leave archived sessions off the board
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.tickets
<- list[Ticket]
```

```
it should show closed sessions in Complete
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.column("Complete")
<- Column
-> Column.cards
  -> Board.cards
  <- list[Card]
  -> Card.column
  <- Column
<- list[Card]
```

```
it should name the ticket of the current session as active
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.active
  -> Sessions.saved
  <- Session
<- Ticket
```

```
it should show tickets and backlog items alike as the board's cards
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.cards
<- list[Card]
```

```
it should count both a ticket and a backlog item as a card
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Board.cards
<- list[Card]
```

```
it should give each card one column
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> Card.column
<- Column
-> Board.cards
<- list[Card]
```

```
it should list every column with its tickets or items
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.load(project).ticket("pet-visits")
<- Board
-> data_of(Board)
  <- the board's data fields, each column and card as its own data
<- dict
```

### a backlog item

#### that a person has added to the backlog folder

```
it should be in the Backlog
-> Board.backlog_item("returns-and-refunds.md", "Returns and refunds")
<- BacklogItem
-> Board.backlog_items
<- list[BacklogItem]
```

##### that a person has moved on

```
it should open its ticket in Discovery
-> Board.backlog_items
<- list[BacklogItem]
```

##### that a person has moved back

```
it should stay in the Backlog
-> Board.backlog_items
<- list[BacklogItem]
```

##### that has been started

```
it should keep the item's file, text and all, in the new ticket's session folder
-> Board.backlog_items
<- list[BacklogItem]
-> BacklogItem.start("feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

```
it should open a ticket in Discovery
-> Board.backlog_items
<- list[BacklogItem]
-> BacklogItem.start("feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
-> Board.ticket("returns-and-refunds")
<- Ticket
-> Ticket.column
<- Column
```

```
it should name the item's file in the new ticket's session log
-> Board.backlog_items
<- list[BacklogItem]
-> BacklogItem.start("feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

#### that is kept as a folder holding a file of its own name

```
it should be in the Backlog under the heading of that file
-> Board.backlog_items
<- list[BacklogItem]
```

```
it should show the text of that file
-> Board.backlog_items
<- list[BacklogItem]
```

##### that has been started

```
it should bring its ticket back with the history in its session log
-> Board.backlog_items
<- list[BacklogItem]
-> BacklogItem.start("feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

```
it should keep its file in the ticket's session folder
-> Board.backlog_items
<- list[BacklogItem]
-> BacklogItem.start("feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

#### that a ticket became when a person dragged it into the Backlog from a later stage

```
it should be in the Backlog
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.ticket("pet-visits")
<- Ticket
-> Board.backlog_items
<- list[BacklogItem]
```

```
it should keep the ticket's whole folder, its history included
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.ticket("pet-visits")
<- Ticket
```

```
it should show the ticket's own idea file as its text
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.ticket("pet-visits")
<- Ticket
-> Board.backlog_items
<- list[BacklogItem]
```

```
it should be off the stages
-> Session.load(session_path: Path, repo_path: Path)
<- Session
-> Board.ticket("pet-visits")
<- Ticket
-> Ticket.progress
<- list[FidelityProgress]
```

### a ticket

#### that has just been started

```
it should be in Discovery, in progress
-> Ticket.create("PawPlace", "initiative")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

```
it should keep its title, scope, and parent
-> Ticket.create("PawPlace", "initiative")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
-> Session.scope
<- str
-> Session.parent
<- str
```

```
it should name Generate on story_map as next
-> Ticket.create("PawPlace", "initiative")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
```

#### with its first logged work on a Specification fidelity

```
it should be in Specification
-> Ticket.column
<- Column
```

#### with a fidelity generated

```
it should show Generate done and Validate and Review remaining for that fidelity
// the graph holds no operation this observation calls
```

##### with log lines whose paths hold spaces and commas

```
it should still find the practice and fidelity by name
// the graph holds no operation this observation calls
```

##### that has a validate naming graph-rule violations

```
it should still need Validate for that fidelity
// the graph holds no operation this observation calls
```

##### that has a validate with no violations

```
it should show Validate done for that fidelity
// the graph holds no operation this observation calls
```

```
it should match the practice's class name in the validate line to its folder name
-> FidelityProgress.done_actions
<- list[str]
```

###### that has been reviewed

```
it should show the fidelity done
// the graph holds no operation this observation calls
```

##### that was reviewed before its validate passed

```
it should not count the review
// the graph holds no operation this observation calls
```

#### with every required fidelity in its stage done

```
it should be done, waiting in its stage's done part
-> Board.ticket("pet-visits")
<- Ticket
-> Board.column("Discovery")
<- Column
```

```
it should have no next
-> Board.ticket("pet-visits")
<- Ticket
```

##### that a person has moved on

```
it should be in the next stage
-> Ticket.move_next()
<- Ticket
-> Ticket.column
<- Column
```

```
it should write the stage it entered to its session log
-> Ticket.move_next()
<- Ticket
```

#### with its stage not done

```
it should stay in its stage
-> Ticket.column
<- Column
```

##### that a person has moved on

```
it should be done in its stage, in the same column
-> Ticket.move_next()
<- Ticket
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

```
it should have no next
-> Ticket.move_next()
<- Ticket
```

#### that a person has moved on with an earlier stage's fidelity still to review

```
it should name Review on that fidelity as next
-> Ticket.move_to("Specification")
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
-> FidelityProgress.next_action
<- str
```

#### that a person has dragged into a later stage's done part

```
it should be done in that stage
-> Ticket.move_to("Implementation", done=True)
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

#### that a person has dragged back into its own stage's in progress part

```
it should be in progress in that stage
-> Board.ticket("pet-visits")
<- Ticket
-> Ticket.move_to("Discovery")
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
-> Ticket.column
<- Column
-> Ticket.is_done
<- bool
```

#### that a person has dragged out of Complete

```
it should be open again, in progress in that stage
-> Board.ticket("pet-visits")
<- Ticket
```

#### with every practice but Stories turned off

```
it should be done with the one practice it works on
-> Session.practice("ddd")
<- PracticeSessionOutput
-> PracticeSessionOutput.enable(False)
  -> PracticeSessionOutput.enabled
  <- bool
<- PracticeSessionOutput
-> Ticket.is_done
<- bool
```

#### that has been closed

```
it should be in Complete
-> Board.ticket("pet-visits")
<- Ticket
```

```
it should have its folder in closed
-> Board.ticket("pet-visits")
<- Ticket
```

#### that has been archived

```
it should be off the board
-> Board.ticket("pet-visits")
<- Ticket
-> Ticket.archive()
  -> Session.close()
  -> Session.move_to_archive()
  <- Session
<- Ticket
-> Board.tickets
<- list[Ticket]
```

```
it should have its folder in the archive
-> Board.ticket("pet-visits")
<- Ticket
-> Ticket.archive()
  -> Session.close()
  -> Session.move_to_archive()
  <- Session
<- Ticket
```

<!-- spec: space/kanban/kanban_tools_spec.py -->

### the board tools

#### with a project whose sessions folder holds a ticket and a backlog item

```
it should return every column of the board
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Board.show()
<- Board
```

```
it should name the project the board belongs to
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Board.show()
<- Board
```

```
it should say when a backlog item last changed
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should give a backlog item its text
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should say a ticket works on the whole repository until a person chooses a root
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

##### with folders in the repository

```
it should list the folders at the top of the repository a root can be chosen from
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Board.folders()
<- list[str]
```

```
it should leave out installed packages and hidden folders
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Board.folders()
<- list[str]
```

```
it should list the folders inside one, as paths from the project
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Board.folders(path="src")
<- list[str]
```

###### that a person has chosen as a ticket's root

```
it should show the folder as the ticket's root
-> Session.choose_workpath(session=_session_file("pet-visits"), path="src/visits")
  -> PracticeSessionOutput.keep_root(root: Path)
<- Session
```

```
it should keep the folder as the session's work folder
-> Session.choose_workpath(session=_session_file("pet-visits"), path="src/visits")
  -> PracticeSessionOutput.keep_root(root: Path)
<- Session
```

###### that a person has chosen as one practice's root

```
it should show the folder as that practice's root, chosen by a person
-> PracticeSessionOutput.choose_root(session=_session_file("pet-visits"), practice="stories", path="src/visits")
  -> PracticeSessionOutput.keep_root(root: Path)
<- PracticeSessionOutput
```

```
it should write that practice's files there
-> PracticeSessionOutput.choose_root(session=_session_file("pet-visits"), practice="stories", path="src/visits")
  -> PracticeSessionOutput.keep_root(root: Path)
<- PracticeSessionOutput
-> FidelityProgress.files(ticket="pet-visits", fidelity="stories-story-map")
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

```
it should leave every other practice on its default root
-> PracticeSessionOutput.choose_root(session=_session_file("pet-visits"), practice="stories", path="src/visits")
  -> PracticeSessionOutput.keep_root(root: Path)
<- PracticeSessionOutput
```

###### that a person has chosen as one practice's root · and then a new root for the ticket

```
it should keep that practice writing to the folder chosen for it
-> Session.choose_workpath(session=_session_file("pet-visits"), path="src")
  -> PracticeSessionOutput.keep_root(root: Path)
<- Session
```

###### that a person has chosen as one practice's root · and then back to its default

```
it should show the practice on its default root again
-> PracticeSessionOutput.use_default_root(session=_session_file("pet-visits"), practice="stories")
<- PracticeSessionOutput
```

###### that a person has chosen as the ticket's root, with no practice root chosen

```
it should put each practice's default root under the ticket's root
-> Session.choose_workpath(session=_session_file("pet-visits"), path="src/visits")
  -> PracticeSessionOutput.keep_root(root: Path)
<- Session
```

###### that a person has started a backlog item in a folder

```
it should open its ticket with that folder as its root
-> BacklogItem.start(backlog_item="Returns and refunds", path="src/billing")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

```
it should give every stage a limit of 3 tickets until a person sets one
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

##### that sets a stage's limit below the tickets it holds

```
it should show the stage over its limit
-> Stage.set_wip_limit(stage="Discovery", limit=0)
<- Stage
```

```
it should show no handoff for a ticket that has none
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

##### with handoffs written for the ticket

```
it should show the latest handoff
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should show no report for a fidelity that has none
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

##### with validation reports saved for a fidelity

```
it should show that fidelity's latest report
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should list each rule the report names with its violations
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should give a violation the line it failed on
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should show no source for a file that is not in the repository
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

###### with the file a violation names in the repository

```
it should show the source lines around a violation
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

###### with a session whose root is a folder of the project

```
it should name the violation's file from the project's root
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should show the source lines of the file in the session's root
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should return exactly the fields ViolationData names
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should return exactly the fields ReportRuleData names
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should count the violations of each rule
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should leave out the violations of other practices in the saved graph
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should say the report has its saved graph
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

##### with a validation report saved without its graph

```
it should say a report has no saved graph
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

```
it should still return the report's text
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.report(ticket="pet-visits", fidelity="clean-engineering-modules")
  -> ReportFile.report()
  <- Report
<- Report
```

##### with a validation report on a rule the practice describes

```
it should show the text of each rule under its name
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

###### with the judgment of the agent that validated it

```
it should list each rule the judgment fails after the graph's rules, once each
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

```
it should count each finding of a judged rule
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

```
it should give a judged finding the judged file and its line
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

```
it should show the source lines around a judged finding
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

```
it should list a rule an older report warns on as failing, since a warning is a Fail
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

##### with a validation report on a rule no scanner checks any more

```
it should leave that rule's hits out of the report
-> ProjectTools.report("pet-visits", "stories-story-map-20261031T041200", deleted)
```

##### that opens a new ticket

```
it should return the new ticket in Discovery
-> Ticket.create(title="Loyalty points", scope="feature")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
```

```
it should leave the current session as it is
-> Ticket.create(title="Loyalty points", scope="feature")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
-> Board.show()
<- Board
```

##### that opens a ticket on a folder in the repository

```
it should save that folder as the session's workpath
-> Ticket.create(title="Pet records", scope="feature", path="harness/pets")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
```

##### that opens a ticket with no folder

```
it should leave the session working on the repository
-> Ticket.create(title="Pet records", scope="feature")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
```

##### that opens a ticket split from another

```
it should name the ticket it was split from
-> Ticket.create(title="Book a visit", scope="story", parent="pet-visits")
  -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
  <- Session
<- Ticket
```

##### that adds a backlog item

```
it should show the item in the Backlog with its text
-> BacklogItem.create(title="Gift cards", text="Sell gift cards.")
<- BacklogItem
```

```
it should write the title and text to one markdown file
-> BacklogItem.create(title="Gift cards", text="Sell gift cards.")
<- BacklogItem
```

##### that starts a backlog item

```
it should return the new ticket in Discovery
-> BacklogItem.start(backlog_item="Returns and refunds", scope="feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

```
it should take the item off the Backlog
-> BacklogItem.start(backlog_item="Returns and refunds", scope="feature")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

##### that closes a ticket

```
it should show the ticket in Complete
-> Ticket.close(ticket="pet-visits")
  -> Session.close()
  -> Session.move_to_closed()
  <- Session
<- Ticket
```

##### that closes the active ticket

```
it should leave no ticket active
-> Ticket.close(ticket="pet-visits")
  -> Session.close()
  -> Session.move_to_closed()
  <- Session
<- Ticket
-> Board.show()
<- Board
```

##### that archives a ticket

```
it should leave the ticket off the board
-> Ticket.archive(ticket="pet-visits")
  -> Session.close()
  -> Session.move_to_archive()
  <- Session
<- Ticket
-> Board.show()
<- Board
```

##### that drags a ticket into a later stage's Done

```
it should show the ticket in that stage's Done
-> Ticket.move_to(ticket="pet-visits", stage="Implementation", done=True)
  -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
  <- BacklogItem
<- Ticket | BacklogItem
```

##### that moves a ticket to the next column

```
it should show the ticket in the next stage
-> Ticket.move_next(ticket="pet-visits")
<- Ticket
```

```
it should show the ticket in progress there
-> Ticket.move_next(ticket="pet-visits")
<- Ticket
```

###### with that stage's work not done

```
it should show the ticket in that stage's Done all the same
-> Ticket.move_next(ticket="pet-visits")
<- Ticket
```

###### with that stage's work not done · and on to the column after

###### with that stage's work not done · and on to the column after · and past Implementation

```
it should close the ticket
-> Ticket.move_next(ticket="pet-visits")
<- Ticket
```

```
it should leave a ticket in Complete where it is on another move forward
-> Ticket.move_next(ticket="pet-visits")
<- Ticket
```

###### with that stage's work not done · and on to the column after · and past Implementation · and back again

```
it should reopen the ticket in Implementation
-> Ticket.move_previous(ticket="pet-visits")
<- Ticket | BacklogItem
```

###### with that stage's work not done · and back from Done

```
it should show the ticket in progress in that stage
-> Ticket.move_previous(ticket="pet-visits")
<- Ticket | BacklogItem
```

###### and back to the previous column

```
it should show the ticket in Discovery
-> Ticket.move_previous(ticket="pet-visits")
<- Ticket | BacklogItem
```

```
it should show the ticket in Discovery's Done
-> Ticket.move_previous(ticket="pet-visits")
<- Ticket | BacklogItem
```

##### that turns a practice off for a ticket

```
it should show the practice off for that ticket
-> PracticeSessionOutput.enable(session=_session_file("pet-visits"), practice="ux", is_enabled=False)
  -> PracticeSessionOutput.enabled
  <- bool
<- PracticeSessionOutput
```

```
it should save the choice to the ticket's session.json
-> PracticeSessionOutput.enable(session=_session_file("pet-visits"), practice="ux", is_enabled=False)
  -> PracticeSessionOutput.enabled
  <- bool
<- PracticeSessionOutput
```

```
it should give each fidelity its default format
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should show each fidelity's Generate, Validate, and Review
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

##### that opens help on a fidelity

```
it should show the fidelity's rules
-> FidelityProgress.help()
<- Help
```

```
it should name the stage a fidelity belongs to
-> FidelityProgress.help()
<- Help
```

```
it should link to the fidelity's page on the forge
-> FidelityProgress.help()
<- Help
```

##### that opens help on a practice

```
it should show the practice's shared rules
-> Board.help(practice="stories")
<- Help
```

```
it should name no fidelity on a practice's help
-> Board.help(practice="stories")
<- Help
```

##### with a work folder outside the repository

```
it should list the files a pattern finds there
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.files(ticket="pet-visits", fidelity="bdd-behavior")
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

```
it should list the files a named part of the path finds there, in folders at any depth
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.files(ticket="pet-visits", fidelity="clean-engineering-model")
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

##### with a fidelity's markdown generated

```
it should list the file with whether it exists
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.files(ticket="pet-visits", fidelity="stories-story-map")
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

```
it should list only the fidelities asked for
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> FidelityProgress.files(ticket="pet-visits", fidelity="stories-story-map")
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

```
it should give the board the ticket's session.json
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should return the file's text
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Session.read_file(session=_session_file("pet-visits"), path="docs/.context/story-map.md")
<- dict
```

##### with files in its session folder

```
it should list every file in the session folder
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Session.folder_files(session=_session_file("pet-visits"))
<- list[dict]
```

```
it should list the files from the project
-> Board.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> Session.folder_files(session=_session_file("pet-visits"))
<- list[dict]
```

#### with a ticket in Discovery

##### that moves the ticket back out of Discovery

```
it should show an item in the Backlog with the ticket's title
-> Ticket.move_previous(ticket="sign-up")
<- Ticket | BacklogItem
```

```
it should give the item's path from the project
-> Ticket.move_previous(ticket="sign-up")
<- Ticket | BacklogItem
```

```
it should take the ticket off the board's stages
-> Ticket.move_previous(ticket="sign-up")
<- Ticket | BacklogItem
```

###### that starts the item again

```
it should bring the ticket back with its work
-> BacklogItem.start(backlog_item="Sign up")
  -> Ticket.create(title: str, scope: str, parent: str, path: str)
    -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
    <- Session
  <- Ticket
<- Ticket
```

```
it should name generate as the next action
-> Board.ticket("sign-up", title="Sign up")
<- Ticket
```

```
it should allow only Generate before anything is generated
-> Board.ticket("sign-up", title="Sign up")
<- Ticket
```

#### with a ticket whose story map has passed validate

```
it should name review as the next action
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z generate /work)
<- Ticket
```

##### with a report whose judgment fails rules the graph passed

```
it should name satisfy as the next action
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200")
```

```
it should count each finding of the judgment
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200")
```

##### that a person has finished reviewing

```
it should show the fidelity's review done
-> FidelityProgress.finish_review(ticket="sign-up", fidelity="stories-story-map")
  -> SessionLog.record(line: str)
<- FidelityProgress
```

```
it should write the review to the session log
-> FidelityProgress.finish_review(ticket="sign-up", fidelity="stories-story-map")
  -> SessionLog.record(line: str)
<- FidelityProgress
```

##### that a person names a fidelity the ticket does not have

```
it should refuse it, naming the fidelity
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z generate /work)
<- Ticket
-> FidelityProgress.finish_review(ticket="sign-up", fidelity="stories-nothing")
  -> SessionLog.record(line: str)
<- FidelityProgress
```

###### among fidelities it does have

```
it should write no review for the others named with it
-> FidelityProgress.finish_review(ticket="sign-up", fidelity="stories-nothing")
  -> SessionLog.record(line: str)
<- FidelityProgress
```

#### with a ticket whose next fidelity has violations

```
it should name satisfy as the next action
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z generate /work)
<- Ticket
```

```
it should allow Validate and Review again on the same output
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z generate /work)
<- Ticket
```

##### with that fidelity's report saved with its graph

```
it should count the violations of the fidelity on its ticket
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

##### with that fidelity's report saved without its graph

```
it should leave a fidelity with no saved graph uncounted
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200")
```

#### with violations left on two fidelities

```
it should list the rules of every fidelity with violations
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
-> Ticket.violations(ticket="sign-up")
<- dict
```

```
it should name the fidelity a rule was broken on
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
```

```
it should give the folder of the reports for every fidelity
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
-> Ticket.violations(ticket="sign-up")
<- dict
```

#### with violations left on a fidelity of a later stage

```
it should list only the rules of the fidelities in the ticket's stage
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
-> Ticket.violations(ticket="sign-up")
<- dict
```

#### with violations two fidelities of one practice share in their saved graphs

```
it should list a rule two fidelities share once
-> Board.ticket("sign-up",
                "2026-10-31T01:00:00Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
-> Ticket.violations(ticket="sign-up")
<- dict
```

#### with a scenarios report whose saved graph holds every stories rule's hits

```
it should list the scenarios rules and the story map rules
-> Board.ticket("sign-up",
                "2026-10-31T01:00:01Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)
```

```
it should count the same rules on the ticket
-> Board.ticket("sign-up",
                "2026-10-31T01:00:01Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)
```

##### with a story map report newer than the scenarios report

```
it should leave the story map rules to the story map report
-> Board.ticket("sign-up",
                "2026-10-31T01:00:01Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)
```

```
it should count only the rules the scenarios report answers for
-> Board.ticket("sign-up",
                "2026-10-31T01:00:01Z validate Stori)
<- Ticket
-> ProjectTools.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)
```

#### with a git repository and two tickets

##### that activates a ticket

```
it should make the chosen ticket the current session
-> Ticket.activate(ticket="sign-up")
  -> Repo.switch_branch(name: str)
  <- str
  -> Repo.switch_worktree(name: str)
  <- str
  -> Sessions.switch
<- Ticket
-> Board.show()
<- Board
```

##### that activates a ticket with a new branch

```
it should create the ticket's branch when a ticket that has none is activated
-> Ticket.activate(ticket="sign-up", opening=["branch"])
  -> Repo.switch_branch(name: str)
  <- str
  -> Repo.switch_worktree(name: str)
  <- str
  -> Sessions.switch
<- Ticket
-> Ticket.branch(ticket="sign-up")
<- dict
```

```
it should say a ticket has no branch yet
-> GuidanceAction.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
  -> SessionLog.guidance_action(action: str)
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Ticket.branch(ticket="sign-up")
<- dict
```

##### with the active ticket on no branch of its own

```
it should say the ticket being left has no branch yet
-> GuidanceAction.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
  -> SessionLog.guidance_action(action: str)
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Ticket.branch(ticket="sign-up")
<- dict
```

```
it should commit nothing on a ticket that has no branch
-> GuidanceAction.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
  -> SessionLog.guidance_action(action: str)
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Ticket.activate(ticket="sign-up", leaving=["commit", "push", "merge"])
  -> Repo.switch_branch(name: str)
  <- str
  -> Repo.switch_worktree(name: str)
  <- str
  -> Sessions.switch
<- Ticket
```

```
it should leave the branch checked out as it was
-> GuidanceAction.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
  -> SessionLog.guidance_action(action: str)
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Ticket.close(ticket="pet-visits", leaving=["commit", "merge"])
  -> Session.close()
  -> Session.move_to_closed()
  <- Session
<- Ticket
```

##### with the active ticket on its own branch

```
it should say the ticket being left is on its branch
-> GuidanceAction.run(["git", "checkout", "-q", "-b", "pet-visits"], cwd=self.project.root, check=True)
  -> SessionLog.guidance_action(action: str)
-> Ticket.branch(ticket="sign-up")
<- dict
```

```
it should commit the branch the ticket being left is on
-> GuidanceAction.run(["git", "checkout", "-q", "-b", "pet-visits"], cwd=self.project.root, check=True)
  -> SessionLog.guidance_action(action: str)
-> Ticket.activate(ticket="sign-up", leaving=["commit"])
  -> Repo.switch_branch(name: str)
  <- str
  -> Repo.switch_worktree(name: str)
  <- str
  -> Sessions.switch
<- Ticket
```

##### with specs in the repository and one changed on the ticket's branch

```
it should list only the files the ticket's branch changed
-> GuidanceAction.run(["git", "add", "src"], cwd=self.project.root, check=True)
  -> SessionLog.guidance_action(action: str)
-> FidelityProgress.files(ticket="pet-visits", fidelity="bdd-behavior")
  -> FidelityGuidance.files()
    -> FidelitySessionOutput.output_paths()
      -> FidelityGuidance.outputs
      <- dict
    <- dict
    -> Branch.changed_files()
    <- list[str]
  <- dict
<- dict[str, list[FileEntry]]
```

##### with the active ticket's branch not checked out

```
it should commit nothing on a branch that is not checked out
-> GuidanceAction.run(["git", "branch", "pet-visits"], cwd=self.project.root, check=True)
  -> SessionLog.guidance_action(action: str)
-> Ticket.activate(ticket="sign-up", leaving=["commit"])
  -> Repo.switch_branch(name: str)
  <- str
  -> Repo.switch_worktree(name: str)
  <- str
  -> Sessions.switch
<- Ticket
```

#### with a session open in the project

```
it should leave the board read out of the session log
-> Sessions(self.project.root).switch("pet-visits", self.project.root)
<- str
-> Board.show()
<- Board
```

#### that are published through the cdd server

```
it should name each tool after its object
// the graph holds no operation this observation calls
```

```
it should take the ticket's name on every ticket tool that acts on one
// the graph holds no operation this observation calls
```

#### whose JSON is compared with the data fields each class marks

```
it should return exactly the fields TicketData names
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should return exactly the fields BranchData names
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
-> GuidanceAction.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
  -> SessionLog.guidance_action(action: str)
-> Ticket.branch(ticket="pet-visits")
<- dict
```

```
it should return exactly the fields BacklogItemData names
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

```
it should return only the fields ColumnData names on a stage
-> Board.ticket("pet-visits", title="Pet visits")
<- Ticket
-> Board.backlog_item("returns.md", "Returns and refunds")
<- BacklogItem
```

#### whose signatures are compared with the board app's shared behaviors

```
it should state every shared behavior here under the same sentence
// the graph holds no operation this observation calls
```

