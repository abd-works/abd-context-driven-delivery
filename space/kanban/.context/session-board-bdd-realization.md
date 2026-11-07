Add Backlog Item
  ```
  -> BoardPage.draft
  -> BacklogDraftClient.add()
  it should stay off with no title
  ```
  with a title and text typed
    ```
    -> BoardPage.draft
    -> BacklogDraftClient.type(field: 'title' | 'text', typed: string)
    -> BacklogDraftClient.add()
    -> ColumnClient.items
    -> ReportClient.text
    it should write the title and text
    ```
    ```
    -> BoardPage.draft
    -> BacklogDraftClient.type(field: 'title' | 'text', typed: string)
    -> BacklogDraftClient.add()
    it should select the item
    ```
    ```
    -> BoardPage.draft
    -> BacklogDraftClient.type(field: 'title' | 'text', typed: string)
    -> BacklogDraftClient.add()
    -> ReportClient.text
    it should say so in a toast
    ```
    ```
    -> BoardPage.draft
    -> BacklogDraftClient.type(field: 'title' | 'text', typed: string)
    -> BacklogDraftClient.add()
    -> TileClient.isOpen(ticket: string, place: string)
    it should close the form
    ```
  Start Backlog Item
    ```
    -> BoardPage.board
    -> BoardClient.backlogItems
    it should open a ticket and select it, with the title safe in the path
    ```
    ```
    -> BoardPage.board
    -> BoardClient.backlogItems
    -> ReportClient.text
    it should say so in a toast
    ```


Display Connected Status
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should show a band when the board read answers that cdd is not connected
  ```
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should drop the band when cdd answers again
  ```
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should read the board once to find that out
  ```
  ```
  -> TileActionsClient.chat
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should drop the band when the chat list answers, because the chats are read through cdd
  ```
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should show the band when the server itself does not answer
  ```
  with a tool failing
    ```
    -> BoardPage.reader
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    it should show no band
    ```
    ```
    -> BoardPage.reader
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    it should show a toast
    ```
  that a person has pressed Update
    ```
    -> BoardPage.update()
    -> BoardUpdate.update()
      -> git pull --ff-only  [External: git]
      -> vite build  [External: vite]
      -> scripts/install.py --ide Claude --pin-runtime  [External: cdd installer]
    it should get the latest code, rebuild the page, then pin cdd to it
    ```
    ```
    -> BoardPage.update()
    -> BoardUpdate.restart()
    it should restart the board server once the update has answered
    ```
    ```
    -> BoardPage.update()
    -> BoardPage.boardServerIsBack()
    -> BoardStore.change({ isNewBuild: true })
    it should load the page again from the restarted server
    ```
    with a step that fails
      ```
      -> BoardPage.update()
      -> BoardUpdate.update()
      <- UpdateStepFailed
      it should say in a toast which step failed
      ```
      ```
      -> BoardPage.update()
      <- null
      it should keep the page it has
      ```
      ```
      -> BoardPage.update()
      -> BoardUpdate.update()
      <- UpdateStepFailed
      it should keep the board server running
      ```

Refresh Board After Tool Calls
  ```
  -> ChatClient.send(kind: CommandKind, text: string, sent: string)
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  -> TicketClient.moveTo(stage: string, done?: boolean)
  it should keep the newer board when an older read answers late
  ```


Announce Ticket Changes
  ```
  -> TicketClient.moveTo(stage: string, done?: boolean)
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should name the new column of a ticket that moves
  ```
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should name a fidelity that was reviewed
  ```
  ```
  -> TicketClient.movePrevious()
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should say a ticket moved to the Backlog
  ```
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should raise nothing on each read of a session open and closed under one name
  ```
  ```
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should raise nothing on the first read
  ```


Arrange Board And Details
  Resize Board And Details
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.setBoardHeight(wanted: number, pageHeight: number)
    it should give the board the height a drag asks for
    ```
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.setBoardHeight(wanted: number, pageHeight: number)
    it should not let a drag close the board
    ```
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.setBoardHeight(wanted: number, pageHeight: number)
    it should not let a drag close the details
    ```
  Expand Board Or Details
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.toggleRegion(region: Region)
    it should give one region the page
    ```
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.toggleRegion(region: Region)
    it should bring the other back on a second press
    ```


Set Stage WIP Limit
  ```
  -> BoardPage.board
  -> BoardClient.stageNamed(name: string)
  -> ColumnClient.submitWipLimit(text: string)
  -> ColumnClient.name
  it should save a whole number
  ```
  ```
  -> BoardPage.board
  -> BoardClient.stageNamed(name: string)
  -> ColumnClient.submitWipLimit(text: string)
  -> BoardClient.stageNamed(name: string)
  -> ColumnClient.wipLimit
  it should read the board again
  ```
  ```
  -> BoardPage.board
  -> BoardClient.stageNamed(name: string)
  -> ColumnClient.submitWipLimit(text: string)
  it should change nothing for a limit that is not a number
  ```
  ```
  -> BoardPage.board
  -> BoardClient.stageNamed(name: string)
  -> ColumnClient.submitWipLimit(text: string)
  it should send the header the server asks of a page on this machine
  ```


Display Ticket Details
  ```
  -> BoardPage.board
  -> BoardClient.selectedTicket
  -> ColumnClient.name
  it should show the active ticket with no card pressed
  ```
  ```
  -> BoardPage.board
  -> BoardClient.selectedTicket
  -> ColumnClient.name
  it should show the ticket worked on last with none active
  ```
  ```
  -> BoardPage.board
  -> BoardClient.selectedTicket
  it should tell a closed session from an open one of the same name
  ```


Display Ticket Card
  ```
  -> _module.ageOf(now: number, stamp: string)
  it should say one hour in the singular
  ```
  ```
  -> _module.ageOf(now: number, stamp: string)
  it should say how many hours ago its ticket was worked on
  ```
  ```
  -> _module.ageOf(now: number, stamp: string)
  it should say a ticket with no activity has none
  ```


Reload Page On New Build
  ```
  -> BuildClient.check()
  it should keep the page while the server serves the build it loaded
  ```
  with a new build deployed after the page loaded
    ```
    -> TicketClient.json
    -> ChatClient.send(kind: CommandKind, text: string, sent: string)
    -> BuildClient.check()
    it should ask for the page to be loaded again
    ```


Open Help
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should drop the section heading the panel already says
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should keep a lead in bold and code as code
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should show a link\'s words, with no address to follow
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should keep a list as a list
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should keep a fenced block as written
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should keep a table as written
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should keep a heading inside the text
  ```
  ```
  -> _module.helpBlocksOf(markdown: string)
  it should give nothing for no text
  ```


List Ticket Files
  ```
  -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
  -> _module.generatedPaths(panel: FilesPanel)
  it should list the files that exist
  ```
  with a list that cannot be read
    ```
    -> BoardApi.refused(status: number, error: string)
    -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
    -> ReportClient.text
    it should say so in a toast
    ```
    ```
    -> BoardApi.refused(status: number, error: string)
    -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
    it should open no panel
    ```


Browse Ticket Folder
  ```
  -> _module.folderGroupsOf(paths: string[])
  it should group the files under their folders
  ```


Browse Ticket's Session Folder
  ```
  -> FilesPanelClient.openSessionFolder(ticket: string)
  -> _module.generatedPaths(panel: FilesPanel)
  it should list every file in the session folder
  ```
  ```
  -> FilesPanelClient.openSessionFolder(ticket: string)
  it should show them as folders
  ```
  with its latest handoff opened
    ```
    -> FilesPanelClient.openSessionFile(ticket: string, path: string)
    it should show the handoff in a tab
    ```
    ```
    -> FilesPanelClient.openSessionFile(ticket: string, path: string)
    it should read the handoff's text
    ```


View Fidelity Files
  ```
  -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
  it should open one tab per format, generated or not
  ```
  ```
  -> _module.offeredTabs(files: FilesByFidelity, slugs: string[])
  it should keep markdown before code before diagrams
  ```
  ```
  -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
  it should read the text of the file a tab shows
  ```
  ```
  -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
  -> FilesPanelClient.closeTab(path: string)
  it should go back to the folder when the last tab closes
  ```
  with a violation in a file its fidelity does not declare
    ```
    -> FilesPanelClient.openFileAtLine(ticket: string, fidelity: string, path: string, line: number)
    it should open that file
    ```
    ```
    -> FilesPanelClient.openFileAtLine(ticket: string, fidelity: string, path: string, line: number)
    it should mark the line it failed on
    ```


Open Validation Report
  ```
  -> SidePanelClient.openReport(ticket: string, fidelity: string)
  -> SidePanelClient.reportPanel
  -> _module.reportPanel
  -> ReportClient.path
  it should show that fidelity's latest report
  ```
  ```
  -> SidePanelClient.openReport(ticket: string, fidelity: string)
  -> SidePanelClient.reportPanel
  -> _module.reportPanel
  -> ReportClient.path
  it should show every fidelity's violations with no fidelity named
  ```


Fix Report Violations
  with Fix pressed on one violation
    ```
    -> TicketClient.fixViolation(rule: ReportRuleData, violation: ViolationData)
    it should send one message to the chat
    ```
    ```
    -> TicketClient.fixViolation(rule: ReportRuleData, violation: ViolationData)
    -> ReportClient.text
    it should name the rule and what it requires
    ```
    ```
    -> TicketClient.fixViolation(rule: ReportRuleData, violation: ViolationData)
    -> ReportClient.text
    it should give the error at its file and line
    ```
    ```
    -> TicketClient.fixViolation(rule: ReportRuleData, violation: ViolationData)
    -> ReportClient.text
    it should quote the content that failed
    ```
    ```
    -> TicketClient.fixViolation(rule: ReportRuleData, violation: ViolationData)
    -> ReportClient.text
    it should name the ticket's session
    ```
  with Fix all pressed on a rule
    ```
    -> TicketClient.fixRule(report: ReportClient, rule: ReportRuleData)
    -> ReportClient.text
    it should send every violation of the rule in one message
    ```
  with Fix all pressed on the whole report
    ```
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    -> SidePanelClient.reportPanel
    -> _module.reportPanel
    -> TicketClient.fixReport(report: ReportClient)
    it should send one message to the chat
    ```
    ```
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    -> SidePanelClient.reportPanel
    -> _module.reportPanel
    -> TicketClient.fixReport(report: ReportClient)
    -> ReportClient.text
    it should name every rule the report breaks
    ```
    ```
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    -> SidePanelClient.reportPanel
    -> _module.reportPanel
    -> TicketClient.fixReport(report: ReportClient)
    -> ReportClient.text
    it should give every violation of every rule
    ```


Refresh Board After Tool Calls
  ```
  -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
  -> FilesPanelClient.closeTab(path: string)
  it should keep a tab a person closed closed
  ```
  with a report and files open as the board changes
    ```
    -> TileClient.changed(tile)
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
    -> BoardPage.reader
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    -> SidePanelClient.reportPanel
    -> _module.reportPanel
    -> ReportClient.rules
    it should read the report again
    ```
    ```
    -> TileClient.changed(tile)
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
    -> BoardPage.reader
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    -> _module.generatedPaths(panel: FilesPanel)
    it should read the files again
    ```


Arrange Side Panel
  Resize Side Panel
    ```
    -> SidePanelClient.setWidth(kind: string, wanted: number)
    it should set the width a drag asks for
    ```
    ```
    -> SidePanelClient.setWidth(kind: string, wanted: number)
    it should not go narrower than the smallest width
    ```
  Expand Side Panel
    ```
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    -> FilesPanelClient.openFiles(ticket: string, slugs: string[], mode: string)
    -> SidePanelClient.toggleExpanded(kind: string)
    it should expand one panel at a time
    ```
  Close Side Panel
    ```
    -> SidePanelClient.openReport(ticket: string, fidelity: string)
    it should close the panel
    ```


Send commands to a chat
  ```
  -> TileActionsClient.chat
  -> _module.chat
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should choose the only chat connected
  ```
  ```
  -> TileActionsClient.chat
  -> _module.chat
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should choose the first of several when none has been picked
  ```
  ```
  -> TileActionsClient.chat
  -> _module.chat
  -> ChatClient.choose(chat: string)
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should choose again the chat a person picked once it is back
  ```
  ```
  -> TileActionsClient.chat
  -> _module.chat
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  -> ChatClient.choose(chat: string)
  -> ChatClient.canSend
  it should send once a person picks one of several
  ```
  ```
  -> TileActionsClient.chat
  -> _module.chat
  -> ChatClient.choose(chat: string)
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should keep a picked chat while it stays connected
  ```
  ```
  -> TileActionsClient.chat
  -> ChatClient.choose(chat: string)
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  -> ChatClient.canSend
  it should let go of a chat that has gone
  ```
  ```
  -> TileActionsClient.chat
  -> ChatClient.command(text: string)
  it should send nothing with no chat chosen
  ```
  ```
  -> TileActionsClient.chat
  -> ChatClient.command(text: string)
  it should send a skill as a command
  ```
  ```
  -> TileActionsClient.chat
  -> _module.chat
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  -> ChatClient.choose(chat: string)
  -> ChatClient.command(text: string)
  -> ReportClient.text
  it should name the chat a command went to and the whole command
  ```
  ```
  -> TileActionsClient.chat
  -> ChatClient.fill(text: string)
  -> ReportClient.text
  it should tell the person a fill is queued for review
  ```
  ```
  -> TileActionsClient.chat
  -> ChatClient.fill(text: string)
  -> ReportClient.text
  it should say a fill waits for the turn to end while the chat is busy
  ```
  ```
  -> TileActionsClient.chat
  -> ChatClient.command(text: string)
  it should show the refusal of a chat that has gone
  ```
  with the chat's messages
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    -> ReportClient.text
    it should show them, the latest first
    ```
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    it should show a message as waiting until the chat takes it
    ```
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    it should show a message as taken, not yet shown, once the chat has taken it
    ```
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    it should say why the chat could not show a message
    ```
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    -> ReportClient.text
    it should show a message as done once the chat has finished working on it
    ```
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    -> BoardReader.refresh()
    -> ChatClient.refresh()
    -> ChatClient.resend(message: string)
    it should put a message the chat did not show back in its queue when a person resends it
    ```
    ```
    -> TileActionsClient.chat
    -> ChatClient.command(text: string)
    -> ChatClient.fill(text: string)
    -> ChatClient.remove(message: string)
    -> ReportClient.text
    it should no longer show a message a person removes
    ```


Activate Ticket
  ```
  -> BoardPage.activation
  it should offer commit and push on leaving and open with merge off
  ```
  ```
  -> BoardPage.activation
  -> TileClient.opening
  it should offer a branch to a ticket that has none
  ```
  ```
  -> BoardPage.activation
  it should choose nothing to leave when the session has no branch
  ```
  ```
  -> BoardPage.activation
  -> _module.activationHeading(open: Activation)
  it should say what it switches from and to
  ```
  that a person has confirmed with merge chosen
    ```
    -> BoardPage.activation
    -> ActivationClient.toggleLeaving(option: string)
    -> ActivationClient.confirm()
    it should send what was chosen
    ```
    ```
    -> BoardPage.activation
    -> ActivationClient.toggleLeaving(option: string)
    -> ActivationClient.confirm()
    -> ReportClient.text
    it should report it
    ```
  that a person has cancelled
    ```
    -> BoardPage.activation
    -> BacklogDraftClient.cancel()
    -> ActivationClient.cancel()
    it should close the dialog
    ```
    ```
    -> BoardPage.activation
    -> BacklogDraftClient.cancel()
    -> ActivationClient.cancel()
    it should send nothing
    ```


Close Active Session
  ```
  -> BoardPage.activation
  -> _module.activationHeading(open: Activation)
  it should ask what to do with its work
  ```
  ```
  -> BoardPage.activation
  -> ActivationClient.confirm()
  -> ReportClient.path
  it should send what to do with its work
  ```
  ```
  -> BoardPage.activation
  -> ActivationClient.confirm()
  it should select the ticket in Complete
  ```


Choose Session Root
  with the roots of a ticket open
    ```
    -> BoardPage.roots
    it should show the ticket's practices with their roots
    ```
    that a person browses into a folder for the session root
      ```
      -> BoardPage.roots
      -> RootChoiceClient.browse(target: string, path: string)
      -> _module.browsing
      it should list the folders inside it
      ```
      ```
      -> BoardPage.roots
      -> RootChoiceClient.browse(target: string, path: string)
      -> RootChoiceClient.up()
      -> _module.browsing
      -> ReportClient.path
      it should go back up to the top of the repository
      ```
      and uses it
        ```
        -> BoardPage.roots
        -> RootChoiceClient.browse(target: string, path: string)
        -> RootChoiceClient.use()
        it should make it the ticket's root
        ```
        ```
        -> BoardPage.roots
        -> RootChoiceClient.browse(target: string, path: string)
        -> RootChoiceClient.use()
        -> _module.browsing
        it should go back to the list of roots
        ```
    that a person chooses a folder for one practice's root
      ```
      -> BoardPage.roots
      -> RootChoiceClient.browse(target: string, path: string)
      -> RootChoiceClient.use()
      it should show it as that practice's chosen root
      ```
      and then goes back to its default
        ```
        -> BoardPage.roots
        -> RootChoiceClient.browse(target: string, path: string)
        -> RootChoiceClient.use()
        -> RootChoiceClient.useDefault(practice: string)
        it should show the practice on its default root
        ```
  with a backlog item a person has asked to start
    ```
    -> BoardPage.roots
    -> RootChoiceClient.openToStart(item: BacklogItemClient)
    -> BoardPage.board
    -> BoardClient.backlogItems
    -> _module.browsing
    -> ReportClient.path
    it should browse the top of the repository for its root before it starts
    ```
    ```
    -> BoardPage.roots
    -> RootChoiceClient.openToStart(item: BacklogItemClient)
    -> BoardPage.board
    -> BoardClient.backlogItems
    it should not start it yet
    ```
    that a person has started in a folder
      ```
      -> BoardPage.roots
      -> RootChoiceClient.browse(target: string, path: string)
      -> RootChoiceClient.use()
      it should open its ticket with that folder as its root
      ```
      ```
      -> BoardPage.roots
      -> RootChoiceClient.browse(target: string, path: string)
      -> RootChoiceClient.use()
      it should stay open on the new ticket's roots, so its practices' roots can be set
      ```


Restrict Actions To Active Session
  ```
  -> TicketClient.isLocked
  it should lock a ticket that is not the active session
  ```
  ```
  -> TicketClient.isLocked
  it should leave the active ticket open
  ```
  ```
  -> BoardPage.layout
  -> BoardLayoutClient.toggleOnlyActive()
  -> TicketClient.isLocked
  it should unlock every ticket with Active session only off
  ```


Display Ticket Details
  ```
  -> TicketClient.nextNote
  it should say what runs next
  ```
  ```
  -> TicketClient.lockNote
  it should say another session must be activated to run it
  ```
  ```
  -> TicketClient.origin
  it should name a split ticket by its parent
  ```
  ```
  -> TicketClient.stagePlace
  it should name the ticket's stage and how far it has got there
  ```
  ```
  -> _module.skillOf(slug: string)
  it should keep a practice with two words in its skill
  ```


Review Fidelity
  with a story map that has passed validate
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.toggleOnlyActive()
    -> TicketClient.canRunNext
    it should offer the review with no chat connected, since it is the person\'s own approval
    ```
    ```
    -> BoardPage.layout
    -> BoardLayoutClient.toggleOnlyActive()
    -> TicketClient.runNext()
    -> TicketClient.actionsOf(slug: string)
    it should show the review done once Run next records it
    ```


Move Ticket
  ```
  -> TicketClient.moveNext()
  it should read the board again and select the ticket where it landed
  ```
  ```
  -> TicketClient.moveTo(stage: string, done?: boolean)
  it should select a dragged ticket in the stage it was dropped on
  ```
  ```
  -> TicketClient.dropOn(edge: string)
  -> BoardPage.board
  -> BoardClient.backlogItems
  it should let a ticket in any column be dropped on the Backlog
  ```
  ```
  -> TicketClient.canDropOn(edge: string)
  it should let only the active ticket, or one done in Implementation, be dropped on Complete
  ```
  that a person has moved to the Backlog
    ```
    -> TicketClient.movePrevious()
    it should let go of what was open on it
    ```
    ```
    -> TicketClient.movePrevious()
    it should select its item
    ```


Send Next Fidelity Action
  ```
  -> TicketClient.runNextLabel
  it should name the step that runs next
  ```
  ```
  -> TicketClient.runNextLabel
  it should say fix violations on held violations
  ```
  ```
  -> TicketClient.runNext()
  it should fill the prompt on validate
  ```
  ```
  -> TicketClient.canRunNext
  it should stay off with no chat to send to
  ```
  with generate next
    ```
    -> TicketClient.runNext()
    it should send the generate command in the default format
    ```
  with generate next on a fidelity of a stage the ticket has moved past
    ```
    -> TicketClient.runNext()
    it should generate it in its own stage's default format
    ```
    ```
    -> TicketClient.runNext()
    -> BoardPage.board
    -> BoardClient.stageNamed(name: string)
    -> TicketClient.isNext(stage: ColumnClient, slug: string)
    it should mark its tile as the next one
    ```
  with violations held and no chat connected
    ```
    -> TicketClient.canRunNext
    it should still offer Run next
    ```
    ```
    -> TicketClient.runNext()
    it should open the report
    ```


Choose Ticket Practices
  ```
  -> TicketClient.enablePractice(practice: string, isEnabled: boolean)
  -> BoardPage.tiles
  it should let go of the tile of a practice turned off
  ```
  ```
  -> TicketClient.enablePractice(practice: string, isEnabled: boolean)
  -> ReportClient.text
  it should say so and where it was saved
  ```


Write Ticket Handoff
  ```
  -> TicketClient.fillHandoff()
  it should fill the prompt with the handoff command
  ```


Close Active Session
  ```
  -> ActivationClient.closeSession(open: Activation)
  -> TicketClient.closeSession()
  it should send the close session command to the chat
  ```
  ```
  -> ActivationClient.closeSession(open: Activation)
  -> TicketClient.closeSession()
  it should leave the ticket in its column
  ```


a generated ticket view
  ```
  // the graph holds no operation this observation calls
  it should show a field no operation changes as read-only
  ```
  ```
  // the graph holds no operation this observation calls
  it should offer an operation with no arguments as a button
  ```
  ```
  // the graph holds no operation this observation calls
  it should give an operation with arguments a form for them
  ```
  with a field the page draws itself
    ```
    // the graph holds no operation this observation calls
    it should draw the page’s own field in its place
    ```


a generated ticket client
  that an operation has answered with new state
    ```
    -> TicketClient.moveNext()
    it should tell what is drawing it to draw again
    ```
  that the page has stopped listening to
    ```
    -> TicketClient.moveNext()
    it should not tell it again
    ```


Choose Action And Formats
  ```
  -> _module.defaultPicks(stage: ColumnClient, slugs: string[], files: FilesByFidelity)
  it should give each fidelity its default format
  ```
  ```
  -> _module.defaultPicks(stage: ColumnClient, slugs: string[], files: FilesByFidelity)
  it should not pick a format already generated
  ```
  ```
  -> _module.chipsOf(stage: ColumnClient, slugs: string[])
  it should let a chip stand for a group
  ```
  ```
  -> _module.chosenFormats(stage: ColumnClient, slugs: string[], picked: string[])
  it should give each fidelity its default format from a chip
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should keep Run off until a format is chosen
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.chooseAction(tile: Tile, action: string)
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should keep Run off on a render with nothing to render
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should keep Run off on a locked ticket
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should keep Run off with no chat connected
  ```
  with a format generated on one fidelity of two
    ```
    -> BoardPage.tiles
    -> BoardPage.tileActions
    -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
    -> ColumnClient.count
    it should count how many fidelities it is generated on
    ```
    ```
    -> BoardPage.tiles
    -> BoardPage.tileActions
    -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
    it should say so in its hint
    ```


Validate Fidelity
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should allow Validate on files already there, with nothing recorded yet
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should keep Validate off with no files and nothing recorded
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should link to the report of the fidelity left with violations
  ```


Generate Fidelity Output
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.run(tile: Tile, stage: ColumnClient)
  it should send the generate command for the picked formats
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.run(tile: Tile, stage: ColumnClient)
  it should clear the picks
  ```


Render Fidelity Format
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.chooseAction(tile: Tile, action: string)
  -> TileActionsClient.toggleFormat(tile: Tile, chip: string)
  -> TileActionsClient.run(tile: Tile, stage: ColumnClient)
  it should turn existing output into the chosen format
  ```


Send Tile Action To Chat


Validate Fidelity
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.validate(tile: Tile)
  it should send the fidelity to validate
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should stay off until the ticket allows it
  ```


Review Fidelity
  ```
  -> BoardPage.tiles
  -> BoardPage.tileActions
  -> TileActionsClient.barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile)
  it should not allow Review until Validate is clean
  ```


Send Action To Stage Practices
  ```
  -> BoardPage.tiles
  -> ColumnClient.workRequired
  -> BoardPage.tileActions
  -> TileActionsClient.chooseAction(tile: Tile, action: string)
  -> TileActionsClient.run(tile: Tile, stage: ColumnClient)
  it should name every fidelity of the stage in one command
  ```


Open Practice Tile
  ```
  -> BoardPage.tiles
  -> TileClient.hoverIn(spot: TileSpot)
  it should open a tile after a short hover
  ```
  ```
  -> BoardPage.tiles
  it should show the bar before its files are read
  ```
  ```
  -> BoardPage.tiles
  it should pick formats from the files once they are read
  ```
  ```
  -> BoardPage.tiles
  -> TileClient.hoverOut(ticket: string, place: string)
  it should close it on leaving
  ```
  ```
  -> BoardPage.tiles
  -> OpenCardClient.toggle(ticket: TicketClient)
  -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
  -> TileClient.hoverOut(ticket: string, place: string)
  it should keep a tile a person pressed open after the pointer leaves
  ```
  ```
  -> BoardPage.tiles
  -> OpenCardClient.toggle(ticket: TicketClient)
  -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
  it should close on a second press
  ```
  with two tiles pressed
    ```
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    it should keep both bars open
    ```
    ```
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    it should close only the bar pressed again
    ```
    ```
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    -> BoardPage.tileActions
    -> TileActionsClient.chooseAction(tile: Tile, action: string)
    it should change only that bar's action
    ```
  with a pressed bar and a bar a hover opened
    ```
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    -> TileClient.hoverIn(spot: TileSpot)
    it should open the hovered bar beside the pressed one
    ```
    ```
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    -> TileClient.hoverIn(spot: TileSpot)
    it should replace the hovered bar with the next one a hover opens, and keep the pressed one
    ```
    ```
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    -> TileClient.hoverIn(spot: TileSpot)
    -> TileClient.hoverOut(ticket: string, place: string)
    it should close the hovered bar on leaving, and keep the pressed one
    ```
  with two stage heads pressed
    ```
    -> BoardPage.board
    -> BoardClient.stageNamed(name: string)
    -> BoardPage.tiles
    -> OpenCardClient.toggle(ticket: TicketClient)
    -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
    -> ColumnClient.workRequired
    -> _module.headPlace(stage: string)
    -> ColumnClient.name
    it should keep both stage bars open
    ```


Expand Ticket
  ```
  -> BoardPage.cards
  -> OpenCardClient.toggle(ticket: TicketClient)
  -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
  -> BoardPage.tiles
  it should open with its tiles only, each opening its own action bar
  ```
  ```
  -> BoardPage.cards
  -> OpenCardClient.toggle(ticket: TicketClient)
  -> TileClient.toggle(ticket: TicketClient, spot: TileSpot)
  it should expand only one card at a time
  ```
  ```
  -> BoardPage.tiles
  -> BoardPage.cards
  -> OpenCardClient.follow(moved: TicketClient)
  it should move an open bar to the tile the ticket works on next when it moves
  ```
  with a segment pressed
    ```
    -> BoardPage.cards
    -> OpenCardClient.openSegment(ticket: TicketClient, stage: ColumnClient, slug: string)
    it should open the card
    ```
    ```
    -> BoardPage.cards
    -> OpenCardClient.openSegment(ticket: TicketClient, stage: ColumnClient, slug: string)
    it should open the tile of that fidelity
    ```


Refresh Board After Tool Calls
  ```
  -> BoardPage.tiles
  -> BoardPage.reader
  -> BoardReader.refresh()
  -> ChatClient.refresh()
  it should read an open bar's files again when the board changes
  ```


the session board on the page
  with the board drawn
    ```
    // the graph holds no operation this observation calls
    it should fill the pane's height
    ```
    ```
    // the graph holds no operation this observation calls
    it should keep a card's controls inside the card
    ```
    ```
    // the graph holds no operation this observation calls
    it should keep a card's move buttons on one line
    ```
    ```
    // the graph holds no operation this observation calls
    it should keep the sideways scrollbar on screen
    ```
    ```
    // the graph holds no operation this observation calls
    it should draw a card at the canvas width
    ```
  with a card opened
    ```
    // the graph holds no operation this observation calls
    it should show its tiles with no action bar until a tile is pressed
    ```
    ```
    // the graph holds no operation this observation calls
    it should show the whole opened card
    ```
    with a tile pressed on it
      ```
      // the graph holds no operation this observation calls
      it should offer the action list and Run in that tile
      ```
  with the files folder pressed on a card
    ```
    // the graph holds no operation this observation calls
    it should open the files list beside the board
    ```
    ```
    // the graph holds no operation this observation calls
    it should keep the header on one line
    ```
  with the activation dialog open
    ```
    // the graph holds no operation this observation calls
    it should draw the primary action in the accent colour
    ```
  with no chat connected
    ```
    // the graph holds no operation this observation calls
    it should say to load the mod and turn off what sends to a chat
    ```
    ```
    // the graph holds no operation this observation calls
    it should keep local actions working
    ```
  at phone width
    ```
    -> RootChoiceClient.use()
    it should scroll the page sideways nowhere but in the board and details scrollers
    ```
    ```
    -> RootChoiceClient.use()
    it should give an open panel the whole page, with no sideways scroll
    ```
    ```
    -> RootChoiceClient.use()
    it should keep the dialog inside the page
    ```


a backlog item a person acts on
  ```
  -> BacklogDraftClient.add()
  it should say in a toast that it was added
  ```
  ```
  // the graph holds no operation this observation calls
  it should say in a toast that it started
  ```


a backlog item
  that a person has added
    ```
    -> BacklogDraftClient.add()
    -> FilesPanelClient.textOf(ticket: string, path: string, isOnDisk: boolean)
    it should show the item in the Backlog with its text
    ```
  that a person has started
    ```
    // the graph holds no operation this observation calls
    it should return the new ticket in Discovery
    ```
    ```
    // the graph holds no operation this observation calls
    it should take the item off the Backlog
    ```
  that holds a ticket moved back out of Discovery
    ```
    // the graph holds no operation this observation calls
    it should bring the ticket back with its work
    ```


a ticket
  with a fidelity's markdown generated
    ```
    // the graph holds no operation this observation calls
    it should list the file with whether it exists
    ```
    ```
    // the graph holds no operation this observation calls
    it should return the file's text
    ```
  with validation reports saved for a fidelity
    ```
    // the graph holds no operation this observation calls
    it should show that fidelity's latest report
    ```
    ```
    // the graph holds no operation this observation calls
    it should list each rule the report names with its violations
    ```
    ```
    // the graph holds no operation this observation calls
    it should give a violation the line it failed on
    ```


a ticket a person moves
  ```
  -> TicketClient.moveNext()
  it should say in a toast that it is done in its stage
  ```
  ```
  -> TicketClient.movePrevious()
  it should say in a toast that it moved to the Backlog
  ```


a ticket
  that a person has moved to the next column
    ```
    -> TicketClient.moveNext()
    it should show the ticket in the next stage
    ```
    ```
    -> TicketClient.moveNext()
    it should show the ticket in progress there
    ```
  with that stage's work not done
    ```
    -> TicketClient.moveNext()
    it should show the ticket in that stage's Done all the same
    ```
    and back from Done
      ```
      -> TicketClient.movePrevious()
      it should show the ticket in progress in that stage
      ```
  that a person has dragged into a later stage's Done
    ```
    // the graph holds no operation this observation calls
    it should show the ticket in that stage's Done
    ```
  that a person has dragged into the Backlog from a later stage
    ```
    // the graph holds no operation this observation calls
    it should show an item in the Backlog with the ticket's title
    ```
    ```
    // the graph holds no operation this observation calls
    it should take the ticket off the board's stages
    ```
  that a person has moved back to the previous column
    ```
    -> TicketClient.movePrevious()
    it should show the ticket in Discovery
    ```
    ```
    -> TicketClient.movePrevious()
    it should show the ticket in Discovery's Done
    ```
  that a person has moved back out of Discovery
    ```
    -> TicketClient.movePrevious()
    it should show an item in the Backlog with the ticket's title
    ```
    ```
    -> TicketClient.movePrevious()
    it should take the ticket off the board's stages
    ```
  that a person has moved past Implementation
    ```
    -> TicketClient.moveNext()
    it should close the ticket
    ```
    and back again
      ```
      -> TicketClient.movePrevious()
      it should reopen the ticket in Implementation
      ```


a board
  ```
  // the graph holds no operation this observation calls
  it should give every stage a limit of 3 tickets until a person sets one
  ```
  ```
  -> ColumnClient.isOverLimit
  it should leave a stage holding fewer tickets than its limit within it
  ```
  that sets a stage's limit below the tickets it holds
    ```
    -> ColumnClient.isOverLimit
    it should show the stage over its limit
    ```


Restrict Actions To Active Session
  ```
  // the graph holds no operation this observation calls
  it should let a ticket that is not active be dragged, activated, and its files opened
  ```
  ```
  // the graph holds no operation this observation calls
  it should keep its practice switches off until Active session only is turned off
  ```


Add Backlog Item
  ```
  // the graph holds no operation this observation calls
  it should keep Add off with no title
  ```


Set Stage WIP Limit
  ```
  -> ChatClient.fill(text: string)
  it should close the field on Escape without changing the limit
  ```
  ```
  -> ChatClient.fill(text: string)
  it should save the field on leaving it
  ```


Send commands to a chat
  ```
  // the graph holds no operation this observation calls
  it should show a chat by the name its mod reports, and keep its id to send to
  ```
  ```
  // the graph holds no operation this observation calls
  it should pick the only chat and say a fill is queued
  ```
  ```
  -> BoardReader.poll()
  it should hold a fill at the server until the turn ends
  ```


Generate Fidelity Output
  ```
  -> BoardReader.poll()
  -> ReportClient.text
  it should send the generate command from Run on an opened card
  ```


Send Tile Action To Chat
  ```
  // the graph holds no operation this observation calls
  it should send the chosen action on a tile
  ```


Open Practice Tile
  ```
  // the graph holds no operation this observation calls
  it should leave a tile in the details closed while the pointer only rests on it
  ```
  ```
  // the graph holds no operation this observation calls
  it should keep a pressed tile open after the pointer leaves
  ```
  ```
  // the graph holds no operation this observation calls
  it should keep two pressed tiles open at once
  ```


Expand Ticket
  ```
  // the graph holds no operation this observation calls
  it should open a card on the fidelity of a pressed segment
  ```
  ```
  // the graph holds no operation this observation calls
  it should show the skill of the segment under the pointer
  ```
  ```
  // the graph holds no operation this observation calls
  it should expand only one card at a time
  ```


Display Ticket Details
  ```
  // the graph holds no operation this observation calls
  it should show the ticket of a card pressed anywhere
  ```
  ```
  // the graph holds no operation this observation calls
  it should show a closed ticket with Complete as its place
  ```


Choose Ticket Practices
  ```
  // the graph holds no operation this observation calls
  it should turn a practice off, say where it was saved, and fade its tile
  ```


Arrange Board And Details
  ```
  -> RootChoiceClient.up()
  it should give the board more height on a drag, and never close the details
  ```
  ```
  // the graph holds no operation this observation calls
  it should give a region the whole page and bring the other back
  ```


Arrange Side Panel
  ```
  -> RootChoiceClient.up()
  it should set a panel\'s width on a drag of its left edge
  ```
  ```
  // the graph holds no operation this observation calls
  it should keep the columns\' width and scroll them sideways when a panel opens
  ```
  ```
  // the graph holds no operation this observation calls
  it should let an expanded panel take the board\'s place, and × close it
  ```


Open Help
  ```
  // the graph holds no operation this observation calls
  it should show a fidelity\'s overview, guidance, rules, and Forge link
  ```
  ```
  // the graph holds no operation this observation calls
  it should head a practice\'s rules SHARED RULES and say Practice overview
  ```


Open Validation Report
  ```
  // the graph holds no operation this observation calls
  it should show the rules with the failing line marked
  ```
  ```
  // the graph holds no operation this observation calls
  it should open a violation\'s file at its line in the Files panel
  ```


Fix Report Violations
  ```
  // the graph holds no operation this observation calls
  it should send Fix and Fix all to the chat
  ```


Display Violations Band
  ```
  // the graph holds no operation this observation calls
  it should name the active ticket\'s violations across the page top
  ```


List, browse, and view files
  ```
  // the graph holds no operation this observation calls
  it should show the two modes of the files panel
  ```
  ```
  // the graph holds no operation this observation calls
  it should offer a tab for a format not generated yet and say so
  ```


Refresh Board After Tool Calls
  ```
  // the graph holds no operation this observation calls
  it should show a move made elsewhere with a toast
  ```
  ```
  // the graph holds no operation this observation calls
  it should read an open files list again when the board changes
  ```


Display Connected Status
  ```
  // the graph holds no operation this observation calls
  it should show a band when cdd cannot be reached
  ```
  ```
  // the graph holds no operation this observation calls
  it should show no band while cdd answers
  ```
  ```
  // the graph holds no operation this observation calls
  it should show a tool failure in a toast
  ```


Choose Session Root
  ```
  // the graph holds no operation this observation calls
  it should open the roots from the details bar and browse the repository's folders for the session root
  ```


Activate Ticket
  ```
  // the graph holds no operation this observation calls
  it should switch the session from the dialog, with merge off
  ```


Close Active Session
  ```
  // the graph holds no operation this observation calls
  it should send the close session command to the chat
  ```
  ```
  // the graph holds no operation this observation calls
  it should leave the ticket in its column
  ```


a board
  with Stories, DDD, and UX chosen
    ```
    -> BoardData.project
    it should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order
    ```
    ```
    -> BoardData.project
    it should have story_map, bounded_context, and ia as Discovery's work required
    ```
    ```
    -> BoardData.project
    it should give every stage Generate, Validate, and Review, in that order
    ```
  with BDD chosen
    ```
    -> BoardData.project
    it should have behavior as Discovery's work required
    ```
    ```
    -> BoardData.project
    it should have realization as Specification's work required
    ```
  that has been loaded with no practices given
    ```
    -> BoardData.project
    it should choose every practice
    ```
    ```
    -> BoardData.project
    it should share its practices with every other board loaded in the process, since they do not change between calls
    ```
  of a project named by a folder inside its checkout
    ```
    -> BoardData.project
    -> Board.load(project)
    <- Board
    -> Board.repo
    <- Repo
    it should show the board of the whole checkout, where sessions keep their folders
    ```
  with no session saved as open
    ```
    -> BoardData.project
    it should have no active ticket, since main is not on the board
    ```
  with a sessions folder of work sessions, closed sessions, default, backlog items, and archived sessions
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should show every work session as a ticket
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should leave main off the board
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should show each backlog item in the Backlog column
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should leave archived sessions off the board
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should show closed sessions in Complete
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should name the ticket of the current session as active
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should show tickets and backlog items alike as the board's cards
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should count both a ticket and a backlog item as a card
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should give each card one column
    ```
    ```
    -> Ticket.session
    <- Session
    -> SessionSeed.folder
    -> Board.load(project)
    <- Board
    -> SessionsFolder.current(name: str)
    -> BoardData.project
    it should list every column with its tickets or items
    ```


a backlog item
  that a person has added to the backlog folder
    ```
    -> BoardData.project
    -> Board.backlog_items
    <- list[BacklogItem]
    it should be in the Backlog
    ```
    that a person has moved on
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      it should open its ticket in Discovery
      ```
    that a person has moved back
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      it should stay in the Backlog
      ```
    that has been started
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      -> BacklogItemHandle.start(scope: str, path: str)
      it should keep the item's file, text and all, in the new ticket's session folder
      ```
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      -> BacklogItemHandle.start(scope: str, path: str)
      -> Board.ticket(name: str)
      <- Ticket
      it should open a ticket in Discovery
      ```
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      -> BacklogItemHandle.start(scope: str, path: str)
      it should name the item's file in the new ticket's session log
      ```
  that is kept as a folder holding a file of its own name
    ```
    -> SessionSeed.folder
    -> BoardData.project
    -> Board.backlog_items
    <- list[BacklogItem]
    it should be in the Backlog under the heading of that file
    ```
    ```
    -> SessionSeed.folder
    -> BoardData.project
    -> Board.backlog_items
    <- list[BacklogItem]
    it should show the text of that file
    ```
    that has been started
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      -> BacklogItemHandle.start(scope: str, path: str)
      it should bring its ticket back with the history in its session log
      ```
      ```
      -> Board.backlog_items
      <- list[BacklogItem]
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      -> BacklogItemHandle.start(scope: str, path: str)
      it should keep its file in the ticket's session folder
      ```
  that a ticket became when a person dragged it into the Backlog from a later stage
    ```
    -> Ticket.session
    <- Session
    -> BoardData.project
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    -> Board.backlog_items
    <- list[BacklogItem]
    it should be in the Backlog
    ```
    ```
    -> Ticket.session
    <- Session
    -> BoardData.project
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    it should keep the ticket's whole folder, its history included
    ```
    ```
    -> Ticket.session
    <- Session
    -> BoardData.project
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    -> Board.backlog_items
    <- list[BacklogItem]
    it should show the ticket's own idea file as its text
    ```
    ```
    -> Ticket.session
    <- Session
    -> BoardData.project
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    it should be off the stages
    ```


a ticket
  that has just been started
    ```
    -> TicketTools.create(title: str, scope: str, parent: str, path: str)
    -> Ticket.create(title: str, scope: str, parent: str, path: str)
      -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
      <- Session
    <- Ticket
    it should be in Discovery, in progress
    ```
    ```
    -> TicketTools.create(title: str, scope: str, parent: str, path: str)
    -> Ticket.create(title: str, scope: str, parent: str, path: str)
      -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
      <- Session
    <- Ticket
    -> Ticket.session
    <- Session
    -> Session.parent
    <- str
    it should keep its title, scope, and lineage
    ```
    ```
    -> TicketTools.create(title: str, scope: str, parent: str, path: str)
    -> Ticket.create(title: str, scope: str, parent: str, path: str)
      -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
      <- Session
    <- Ticket
    -> FidelityProgress.remaining_actions
    <- list[str]
    it should name Generate on story_map as next
    ```
  with its first logged work on a Specification fidelity
    ```
    // the graph holds no operation this observation calls
    it should be in Specification
    ```
  with a fidelity generated
    ```
    -> FidelityProgress.remaining_actions
    <- list[str]
    it should show Generate done and Validate and Review remaining for that fidelity
    ```
    with log lines whose paths hold spaces and commas
      ```
      -> FidelityProgress.done_actions
      <- list[str]
      it should still find the practice and fidelity by name
      ```
    that has a validate naming graph-rule violations
      ```
      -> FidelityProgress.remaining_actions
      <- list[str]
      it should still need Validate for that fidelity
      ```
    that has a validate with no violations
      ```
      -> FidelityProgress.done_actions
      <- list[str]
      it should show Validate done for that fidelity
      ```
      ```
      -> FidelityProgress.done_actions
      <- list[str]
      it should match the practice's class name in the validate line to its folder name
      ```
      that has been reviewed
        ```
        // the graph holds no operation this observation calls
        it should show the fidelity done
        ```
    that was reviewed before its validate passed
      ```
      -> FidelityProgress.done_actions
      <- list[str]
      it should not count the review
      ```
  with every required fidelity in its stage done
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should be done, waiting in its stage's done part
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should have no next
    ```
    that a person has moved on
      ```
      -> Board.ticket(name: str)
      <- Ticket
      it should be in the next stage
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      it should write the stage it entered to its session log
      ```
  with a session log written before moves were named move
    ```
    // the graph holds no operation this observation calls
    it should still be in the stage the log names
    ```
    ```
    // the graph holds no operation this observation calls
    it should still be marked done there
    ```
  with its stage not done
    ```
    // the graph holds no operation this observation calls
    it should stay in its stage
    ```
    that a person has moved on
      ```
      // the graph holds no operation this observation calls
      it should be done in its stage, in the same column
      ```
      ```
      // the graph holds no operation this observation calls
      it should have no next
      ```
  that a person has moved on with an earlier stage's fidelity still to review
    ```
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    it should name Review on that fidelity as next
    ```
  that a person has dragged into a later stage's done part
    ```
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    it should be done in that stage
    ```
  that a person has dragged back into its own stage's in progress part
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    it should be in progress in that stage
    ```
  that a person has dragged out of Complete
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.move_to(stage: str, done: bool)
      -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
      <- BacklogItem
    <- Ticket | BacklogItem
    it should be open again, in progress in that stage
    ```
  with every practice but Stories turned off
    ```
    -> PracticeSessionOutput.enable(is_enabled: bool)
      -> PracticeSessionOutput.enabled
      <- bool
    <- PracticeSessionOutput
    it should be done with the one practice it works on
    ```
  that has been closed
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should be in Complete
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should have its folder in closed
    ```
  that has been archived
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.archive()
      -> Session.close()
      -> Session.move_to_archive()
      <- Session
    <- Ticket
    it should be off the board
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.archive()
      -> Session.close()
      -> Session.move_to_archive()
      <- Session
    <- Ticket
    it should have its folder in the archive
    ```


the board tools
  with a project whose sessions folder holds a ticket and a backlog item
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Board.show()
    <- Board
    it should return every column of the board
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Board.show()
    <- Board
    it should name the project the board belongs to
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should say when a backlog item last changed
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should give a backlog item its text
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should say a ticket works on the whole repository until a person chooses a root
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should give every stage a limit of 3 tickets until a person sets one
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should show no handoff for a ticket that has none
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should show no report for a fidelity that has none
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should give each fidelity its default format
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should show each fidelity's Generate, Validate, and Review
    ```
    with folders in the repository
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Board.folders(path: str)
      <- list[str]
      it should list the folders at the top of the repository a root can be chosen from
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Board.folders(path: str)
      <- list[str]
      it should leave out installed packages and hidden folders
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Board.folders(path: str)
      <- list[str]
      it should list the folders inside one, as paths from the project
      ```
      that a person has chosen as a ticket's root
        ```
        -> Session.choose_workpath(path: str)
          -> PracticeSessionOutput.keep_root(root: Path)
        <- Session
        it should show the folder as the ticket's root
        ```
        ```
        -> Session.choose_workpath(path: str)
          -> PracticeSessionOutput.keep_root(root: Path)
        <- Session
        it should keep the folder as the session's work folder
        ```
      that a person has chosen as one practice's root
        ```
        -> PracticeSessionOutput.choose_root(path: str)
          -> PracticeSessionOutput.keep_root(root: Path)
        <- PracticeSessionOutput
        it should show the folder as that practice's root, chosen by a person
        ```
        ```
        -> PracticeSessionOutput.choose_root(path: str)
          -> PracticeSessionOutput.keep_root(root: Path)
        <- PracticeSessionOutput
        -> FidelityProgress.files()
          -> FidelityGuidance.files()
            -> FidelitySessionOutput.output_paths()
              -> FidelityGuidance.outputs
              <- dict
            <- dict
            -> Branch.changed_files()
            <- list[str]
          <- dict
        <- dict[str, list[FileEntry]]
        it should write that practice's files there
        ```
        ```
        -> PracticeSessionOutput.choose_root(path: str)
          -> PracticeSessionOutput.keep_root(root: Path)
        <- PracticeSessionOutput
        it should leave every other practice on its default root
        ```
        and then a new root for the ticket
          ```
          -> Session.choose_workpath(path: str)
            -> PracticeSessionOutput.keep_root(root: Path)
          <- Session
          it should keep that practice writing to the folder chosen for it
          ```
        and then back to its default
          ```
          -> PracticeSessionOutput.use_default_root()
          <- PracticeSessionOutput
          it should show the practice on its default root again
          ```
      that a person has chosen as the ticket's root, with no practice root chosen
        ```
        -> Session.choose_workpath(path: str)
          -> PracticeSessionOutput.keep_root(root: Path)
        <- Session
        it should put each practice's default root under the ticket's root
        ```
      that a person has started a backlog item in a folder
        ```
        -> BacklogItem.start(scope: str, path: str)
          -> Ticket.create(title: str, scope: str, parent: str, path: str)
            -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
            <- Session
          <- Ticket
        <- Ticket
        it should open its ticket with that folder as its root
        ```
    that sets a stage's limit below the tickets it holds
      ```
      -> Stage.set_wip_limit(limit: int)
      <- Stage
      -> TicketData.next
      -> Ticket.next_fidelity
      <- FidelityProgress
      it should show the stage over its limit
      ```
    with handoffs written for the ticket
      ```
      -> Board.ticket(name: str)
      <- Ticket
      it should show the latest handoff
      ```
    with validation reports saved for a fidelity
      ```
      -> Board.ticket(name: str)
      <- Ticket
      it should show that fidelity's latest report
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should list each rule the report names with its violations
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should give a violation the line it failed on
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should show no source for a file that is not in the repository
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should return exactly the fields ViolationData names
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should return exactly the fields ReportRuleData names
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should count the violations of each rule
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should leave out the violations of other practices in the saved graph
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should say the report has its saved graph
      ```
      with the file a violation names in the repository
        ```
        -> Board.ticket(name: str)
        <- Ticket
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should show the source lines around a violation
        ```
      with a session whose root is a folder of the project
        ```
        -> Board.ticket(name: str)
        <- Ticket
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should name the violation's file from the project's root
        ```
        ```
        -> Board.ticket(name: str)
        <- Ticket
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should show the source lines of the file in the session's root
        ```
    with a validation report saved without its graph
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should say a report has no saved graph
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should still return the report's text
      ```
    with a validation report on a rule the practice describes
      ```
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should show the text of each rule under its name
      ```
      with the judgment of the agent that validated it
        ```
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should list each rule the judgment fails after the graph's rules, once each
        ```
        ```
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should count each finding of a judged rule
        ```
        ```
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should give a judged finding the judged file and its line
        ```
        ```
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should show the source lines around a judged finding
        ```
        ```
        -> FidelityProgress.report()
          -> ReportFile.report()
          <- Report
        <- Report
        it should list a rule an older report warns on as failing, since a warning is a Fail
        ```
    with a validation report on a rule no scanner checks any more
      ```
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should leave that rule's hits out of the report
      ```
    that opens a new ticket
      ```
      -> Ticket.create(title: str, scope: str, parent: str, path: str)
        -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
        <- Session
      <- Ticket
      it should return the new ticket in Discovery
      ```
      ```
      -> Ticket.create(title: str, scope: str, parent: str, path: str)
        -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
        <- Session
      <- Ticket
      -> Board.show()
      <- Board
      it should leave the current session as it is
      ```
    that opens a ticket on a folder in the repository
      ```
      -> Ticket.create(title: str, scope: str, parent: str, path: str)
        -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
        <- Session
      <- Ticket
      it should save that folder as the session's workpath
      ```
    that opens a ticket with no folder
      ```
      -> Ticket.create(title: str, scope: str, parent: str, path: str)
        -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
        <- Session
      <- Ticket
      it should leave the session working on the repository
      ```
    that opens a ticket split from another
      ```
      -> Ticket.create(title: str, scope: str, parent: str, path: str)
        -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
        <- Session
      <- Ticket
      it should name the ticket it was split from
      ```
    that adds a backlog item
      ```
      -> BacklogItem.create(title: str, text: str)
      <- BacklogItem
      it should show the item in the Backlog with its text
      ```
      ```
      -> BacklogItem.create(title: str, text: str)
      <- BacklogItem
      it should write the title and text to one markdown file
      ```
    that starts a backlog item
      ```
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      it should return the new ticket in Discovery
      ```
      ```
      -> BacklogItem.start(scope: str, path: str)
        -> Ticket.create(title: str, scope: str, parent: str, path: str)
          -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
          <- Session
        <- Ticket
      <- Ticket
      it should take the item off the Backlog
      ```
    that closes a ticket
      ```
      -> Ticket.close(leaving: list[str])
        -> Session.close()
        -> Session.move_to_closed()
        <- Session
      <- Ticket
      it should show the ticket in Complete
      ```
    that closes the active ticket
      ```
      -> Ticket.close(leaving: list[str])
        -> Session.close()
        -> Session.move_to_closed()
        <- Session
      <- Ticket
      -> Board.show()
      <- Board
      it should leave no ticket active
      ```
    that archives a ticket
      ```
      -> Ticket.archive()
        -> Session.close()
        -> Session.move_to_archive()
        <- Session
      <- Ticket
      -> Board.show()
      <- Board
      it should leave the ticket off the board
      ```
    that drags a ticket into a later stage's Done
      ```
      -> Ticket.move_to(stage: str, done: bool)
        -> BacklogItem.from_ticket(ticket: Ticket, board: Board)
        <- BacklogItem
      <- Ticket | BacklogItem
      it should show the ticket in that stage's Done
      ```
    that moves a ticket to the next column
      ```
      -> Ticket.move_next()
      <- Ticket
      it should show the ticket in the next stage
      ```
      ```
      -> Ticket.move_next()
      <- Ticket
      it should show the ticket in progress there
      ```
      with that stage's work not done
        ```
        -> Ticket.move_next()
        <- Ticket
        it should show the ticket in that stage's Done all the same
        ```
        and on to the column after
          and past Implementation
            ```
            -> Ticket.move_next()
            <- Ticket
            it should close the ticket
            ```
            ```
            -> Ticket.move_next()
            <- Ticket
            it should leave a ticket in Complete where it is on another move forward
            ```
            and back again
              ```
              -> Ticket.move_previous()
              <- Ticket | BacklogItem
              it should reopen the ticket in Implementation
              ```
        and back from Done
          ```
          -> Ticket.move_previous()
          <- Ticket | BacklogItem
          it should show the ticket in progress in that stage
          ```
      and back to the previous column
        ```
        -> Ticket.move_previous()
        <- Ticket | BacklogItem
        it should show the ticket in Discovery
        ```
        ```
        -> Ticket.move_previous()
        <- Ticket | BacklogItem
        it should show the ticket in Discovery's Done
        ```
    that turns a practice off for a ticket
      ```
      -> PracticeSessionOutput.enable(is_enabled: bool)
        -> PracticeSessionOutput.enabled
        <- bool
      <- PracticeSessionOutput
      it should show the practice off for that ticket
      ```
      ```
      -> PracticeSessionOutput.enable(is_enabled: bool)
        -> PracticeSessionOutput.enabled
        <- bool
      <- PracticeSessionOutput
      it should save the choice to the ticket's session.json
      ```
    that opens help on a fidelity
      ```
      -> Board.help(practice: str, fidelity: str)
      <- dict
      it should show the fidelity's rules
      ```
      ```
      -> Board.help(practice: str, fidelity: str)
      <- dict
      it should name the stage a fidelity belongs to
      ```
      ```
      -> Board.help(practice: str, fidelity: str)
      <- dict
      it should link to the fidelity's page on the forge
      ```
    that opens help on a practice
      ```
      -> Board.help(practice: str, fidelity: str)
      <- dict
      it should show the practice's shared rules
      ```
      ```
      -> Board.help(practice: str, fidelity: str)
      <- dict
      it should name no fidelity on a practice's help
      ```
    with a work folder outside the repository
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.files()
        -> FidelityGuidance.files()
          -> FidelitySessionOutput.output_paths()
            -> FidelityGuidance.outputs
            <- dict
          <- dict
          -> Branch.changed_files()
          <- list[str]
        <- dict
      <- dict[str, list[FileEntry]]
      it should list the files a pattern finds there
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.files()
        -> FidelityGuidance.files()
          -> FidelitySessionOutput.output_paths()
            -> FidelityGuidance.outputs
            <- dict
          <- dict
          -> Branch.changed_files()
          <- list[str]
        <- dict
      <- dict[str, list[FileEntry]]
      it should list the files a named part of the path finds there, in folders at any depth
      ```
    with a fidelity's markdown generated
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.files()
        -> FidelityGuidance.files()
          -> FidelitySessionOutput.output_paths()
            -> FidelityGuidance.outputs
            <- dict
          <- dict
          -> Branch.changed_files()
          <- list[str]
        <- dict
      <- dict[str, list[FileEntry]]
      it should list the file with whether it exists
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.files()
        -> FidelityGuidance.files()
          -> FidelitySessionOutput.output_paths()
            -> FidelityGuidance.outputs
            <- dict
          <- dict
          -> Branch.changed_files()
          <- list[str]
        <- dict
      <- dict[str, list[FileEntry]]
      it should list only the fidelities asked for
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      it should give the board the ticket's session.json
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Session.read_file(path: str)
      <- dict
      it should return the file's text
      ```
    with files in its session folder
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Session.folder_files()
      <- list[dict]
      it should list every file in the session folder
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Session.folder_files()
      <- list[dict]
      it should list the files from the project
      ```
  with a ticket in Discovery
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should name generate as the next action
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should allow only Generate before anything is generated
    ```
    that moves the ticket back out of Discovery
      ```
      -> Ticket.move_previous()
      <- Ticket | BacklogItem
      it should show an item in the Backlog with the ticket's title
      ```
      ```
      -> Ticket.move_previous()
      <- Ticket | BacklogItem
      it should give the item's path from the project
      ```
      ```
      -> Ticket.move_previous()
      <- Ticket | BacklogItem
      it should take the ticket off the board's stages
      ```
      that starts the item again
        ```
        -> BacklogItem.start(scope: str, path: str)
          -> Ticket.create(title: str, scope: str, parent: str, path: str)
            -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
            <- Session
          <- Ticket
        <- Ticket
        it should bring the ticket back with its work
        ```
  with a ticket whose story map has passed validate
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should name review as the next action
    ```
    with a report whose judgment fails rules the graph passed
      ```
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should name satisfy as the next action
      ```
      ```
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should count each finding of the judgment
      ```
    that a person has finished reviewing
      ```
      -> FidelityProgress.finish_review()
        -> SessionLog.record(line: str)
      <- FidelityProgress
      it should show the fidelity's review done
      ```
      ```
      -> FidelityProgress.finish_review()
        -> SessionLog.record(line: str)
      <- FidelityProgress
      it should write the review to the session log
      ```
    that a person names a fidelity the ticket does not have
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.finish_review()
        -> SessionLog.record(line: str)
      <- FidelityProgress
      it should refuse it, naming the fidelity
      ```
      among fidelities it does have
        ```
        -> FidelityProgress.finish_review()
          -> SessionLog.record(line: str)
        <- FidelityProgress
        it should write no review for the others named with it
        ```
  with a ticket whose next fidelity has violations
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should name satisfy as the next action
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should allow Validate and Review again on the same output
    ```
    with that fidelity's report saved with its graph
      ```
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should count the violations of the fidelity on its ticket
      ```
    with that fidelity's report saved without its graph
      ```
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should leave a fidelity with no saved graph uncounted
      ```
  with violations left on two fidelities
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    -> Ticket.violations()
    <- dict
    it should list the rules of every fidelity with violations
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    it should name the fidelity a rule was broken on
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    -> Ticket.violations()
    <- dict
    it should give the folder of the reports for every fidelity
    ```
  with violations left on a fidelity of a later stage
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    -> Ticket.violations()
    <- dict
    it should list only the rules of the fidelities in the ticket's stage
    ```
  with violations two fidelities of one practice share in their saved graphs
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    -> Ticket.violations()
    <- dict
    it should list a rule two fidelities share once
    ```
  with a scenarios report whose saved graph holds every stories rule's hits
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    it should list the scenarios rules and the story map rules
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> FidelityProgress.report()
      -> ReportFile.report()
      <- Report
    <- Report
    it should count the same rules on the ticket
    ```
    with a story map report newer than the scenarios report
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should leave the story map rules to the story map report
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.report()
        -> ReportFile.report()
        <- Report
      <- Report
      it should count only the rules the scenarios report answers for
      ```
  with a git repository and two tickets
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.branch()
    <- dict
    it should say a ticket has no branch yet
    ```
    that activates a ticket
      ```
      -> Ticket.activate(leaving: list[str], opening: list[str])
        -> Repo.switch_branch(name: str)
        <- str
        -> Repo.switch_worktree(name: str)
        <- str
        -> Sessions.switch(name: str)
      <- Ticket
      -> Board.show()
      <- Board
      it should make the chosen ticket the current session
      ```
    that activates a ticket with a new branch
      ```
      -> Ticket.activate(leaving: list[str], opening: list[str])
        -> Repo.switch_branch(name: str)
        <- str
        -> Repo.switch_worktree(name: str)
        <- str
        -> Sessions.switch(name: str)
      <- Ticket
      -> Ticket.branch()
      <- dict
      it should create the ticket's branch when a ticket that has none is activated
      ```
    with the active ticket on no branch of its own
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Ticket.branch()
      <- dict
      it should say the ticket being left has no branch yet
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Ticket.activate(leaving: list[str], opening: list[str])
        -> Repo.switch_branch(name: str)
        <- str
        -> Repo.switch_worktree(name: str)
        <- str
        -> Sessions.switch(name: str)
      <- Ticket
      it should commit nothing on a ticket that has no branch
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Ticket.close(leaving: list[str])
        -> Session.close()
        -> Session.move_to_closed()
        <- Session
      <- Ticket
      it should leave the branch checked out as it was
      ```
    with the active ticket on its own branch
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Ticket.branch()
      <- dict
      it should say the ticket being left is on its branch
      ```
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Ticket.activate(leaving: list[str], opening: list[str])
        -> Repo.switch_branch(name: str)
        <- str
        -> Repo.switch_worktree(name: str)
        <- str
        -> Sessions.switch(name: str)
      <- Ticket
      it should commit the branch the ticket being left is on
      ```
    with specs in the repository and one changed on the ticket's branch
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> FidelityProgress.files()
        -> FidelityGuidance.files()
          -> FidelitySessionOutput.output_paths()
            -> FidelityGuidance.outputs
            <- dict
          <- dict
          -> Branch.changed_files()
          <- list[str]
        <- dict
      <- dict[str, list[FileEntry]]
      it should list only the files the ticket's branch changed
      ```
    with the active ticket's branch not checked out
      ```
      -> Board.ticket(name: str)
      <- Ticket
      -> Ticket.activate(leaving: list[str], opening: list[str])
        -> Repo.switch_branch(name: str)
        <- str
        -> Repo.switch_worktree(name: str)
        <- str
        -> Sessions.switch(name: str)
      <- Ticket
      it should commit nothing on a branch that is not checked out
      ```
  with a session open in the project
    ```
    -> Board.show()
    <- Board
    -> TicketTools.create(title: str, scope: str, parent: str, path: str)
    -> Ticket.create(title: str, scope: str, parent: str, path: str)
      -> Sessions.create(name: str, workpath: Path, title: str, scope: str, parent: str)
      <- Session
    <- Ticket
    it should leave the board read out of the session log
    ```
  that are published through the cdd server
    ```
    // the graph holds no operation this observation calls
    it should name each tool after its object
    ```
    ```
    // the graph holds no operation this observation calls
    it should take the ticket's name on every ticket tool that acts on one
    ```
  whose JSON is compared with the shapes in data.py
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should return exactly the fields TicketData names
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    -> Ticket.branch()
    <- dict
    it should return exactly the fields BranchData names
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should return exactly the fields BacklogItemData names
    ```
    ```
    -> Board.ticket(name: str)
    <- Ticket
    it should return only the fields ColumnData names on a stage
    ```
  whose signatures are compared with the board app's shared behaviors
    ```
    // the graph holds no operation this observation calls
    it should state every shared behavior here under the same sentence
    ```


Open Board
  Open the board on a project
    ```
    // the graph holds no operation this observation calls
    it Then the header reads cdd-board-surface-fixture · 9 tickets · active: Checkout flow
    ```
    ```
    // the graph holds no operation this observation calls
    it And the session board reads the board again every two seconds
    ```


Say the cdd server is not connected
  ```
  // the graph holds no operation this observation calls
  it Then a band across the top of the page says The cdd server is not connected
  ```
  ```
  // the graph holds no operation this observation calls
  it And the header offers Update
  ```


Show a failing tool in a toast
  ```
  // the graph holds no operation this observation calls
  it Then a toast says cdd board.show failed: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
  ```
  ```
  // the graph holds no operation this observation calls
  it But no band says the cdd server is lost
  ```


Announce a ticket that moved
  ```
  // the graph holds no operation this observation calls
  it Then a toast says Move me moved to Discovery · Done
  ```


Announce a fidelity done
  ```
  // the graph holds no operation this observation calls
  it Then a toast says stories-story-map done on billing-report
  ```


Arrange Board And Details
  Give the board more height
    ```
    // the graph holds no operation this observation calls
    it Then the board region is 300 pixels high and the details take the rest
    ```
  Keep both regions open
    ```
    // the graph holds no operation this observation calls
    it Then the board region stays 160 pixels high
    ```
    the Person resizes the board to 5000 pixels
      ```
      // the graph holds no operation this observation calls
      it Then the board region stops at 650 pixels, so the details stay open
      ```
  Expand one region and show both again
    ```
    // the graph holds no operation this observation calls
    it Then the board takes the whole page
    ```
    the Person collapses the board
      ```
      // the graph holds no operation this observation calls
      it Then the board and the details share the page again
      ```


Display Ticket Card
  Draw the card's title, age, and fidelity segments
    ```
    // the graph holds no operation this observation calls
    it Then the card reads Checkout flow and 13 hours ago
    ```
    ```
    // the graph holds no operation this observation calls
    it And it shows one segment for each enabled Discovery fidelity, the story_map segment in the violations colour and the rest dim
    ```
    ```
    // the graph holds no operation this observation calls
    it And a violations link on the card opens the report
    ```
  Outline the active ticket
    ```
    // the graph holds no operation this observation calls
    it Then the checkout-flow card has a thick orange outline
    ```


Display Ticket Details
  Show the active ticket with no card pressed
    ```
    // the graph holds no operation this observation calls
    it Then the details show Checkout flow
    ```
  Show the ticket worked on last when none is active
    ```
    // the graph holds no operation this observation calls
    it Then the details show Billing report
    ```
  Say another session must be activated to act on a locked ticket
    ```
    // the graph holds no operation this observation calls
    it Then the details say Activate this session to run actions
    ```
  Expand one ticket's card at a time
    ```
    // the graph holds no operation this observation calls
    it Then billing-report's card is expanded with a tile for each enabled Discovery fidelity
    ```
    ```
    // the graph holds no operation this observation calls
    it And checkout-flow's card is closed
    ```
  Open a card on the fidelity of a pressed segment
    ```
    // the graph holds no operation this observation calls
    it Then billing-report's card is expanded with the story_map tile's action bar open
    ```


Set Stage WIP Limit
  Change nothing for a limit that is not a whole number
    ```
    -> BacklogDraftClient.type(field: 'title' | 'text', typed: string)
    it Then Discovery still shows the limit 3
    ```
    ```
    -> BacklogDraftClient.type(field: 'title' | 'text', typed: string)
    it But no limit is saved
    ```


Arrange Side Panel
  Set a panel's width
    ```
    // the graph holds no operation this observation calls
    it Then the files panel is 700 pixels wide
    ```
    the Person narrows the files panel to 10 pixels
      ```
      // the graph holds no operation this observation calls
      it Then the files panel stops at 360 pixels
      ```
  Expand one panel at a time
    ```
    // the graph holds no operation this observation calls
    it Then the files panel takes the board's width less the other open panels
    ```
    ```
    // the graph holds no operation this observation calls
    it And the report panel is no longer expanded
    ```
  Close a side panel
    ```
    // the graph holds no operation this observation calls
    it Then no side panel is open
    ```
  Keep the columns' width when a panel opens
    ```
    // the graph holds no operation this observation calls
    it Then the columns keep their width and scroll sideways beside the files panel
    ```


Restrict Actions To Active Session
  Lock tickets that are not the active session
    ```
    // the graph holds no operation this observation calls
    it Then billing-report's Run next, Run, practice switches, Split, and Handoff are off
    ```
    ```
    // the graph holds no operation this observation calls
    it And billing-report's Run next says Activate this session to run its next step
    ```
    ```
    // the graph holds no operation this observation calls
    it And checkout-flow's actions stay on
    ```
  Keep information and moves open on a locked ticket
    ```
    // the graph holds no operation this observation calls
    it Then the files panel lists billing-report's files
    ```
    the Person moves billing-report to Specification
      ```
      // the graph holds no operation this observation calls
      it Then billing-report moves to Specification
      ```
      ```
      // the graph holds no operation this observation calls
      it And Activate stays on for billing-report
      ```
  Unlock every ticket
    ```
    // the graph holds no operation this observation calls
    it Then billing-report's actions are on like the active ticket's
    ```


with no chat connected
  Add Backlog Item
    Add an idea to the Backlog
      ```
      -> ChatClient.fill(text: string)
      it Then Gift cards is selected and the form is closed
      ```
      ```
      -> ChatClient.fill(text: string)
      it And a toast says Gift cards added to Backlog
      ```
    Keep Add off with no title
      ```
      -> ChatClient.fill(text: string)
      it Then Add stays off
      ```
      ```
      -> ChatClient.fill(text: string)
      it And no backlog item is written
      ```
    Start a backlog item in a chosen folder
      ```
      // the graph holds no operation this observation calls
      it Then the roots dialog stays open on gift-cards so its practices' roots can be set
      ```
      ```
      // the graph holds no operation this observation calls
      it And a toast says Gift cards started in Discovery
      ```
  Open Ticket Session
    Keep + Ticket off with no chat
      ```
      // the graph holds no operation this observation calls
      it Then + Ticket is off
      ```
  Split Ticket Into Child Tickets
    Keep Split off where nothing can take the prompt
      ```
      // the graph holds no operation this observation calls
      it Then Split is off
      ```
  Write Ticket Handoff
    Keep Handoff off with no chat
      ```
      // the graph holds no operation this observation calls
      it Then Handoff is off
      ```
      ```
      // the graph holds no operation this observation calls
      it And the header says No chat connected: load the cdd-board mod in a chat to send commands
      ```
  Move Ticket
    Move a ticket into the Backlog with its work
      ```
      // the graph holds no operation this observation calls
      it Then the Backlog shows the backlog item Back to backlog and it is selected
      ```
      ```
      // the graph holds no operation this observation calls
      it And a toast says Back to backlog moved to Backlog
      ```
  Activate Ticket
    Switch to another ticket, committing, pushing, and merging the one left
      ```
      // the graph holds no operation this observation calls
      it Then a dialog headed Switch from Checkout flow to Billing report offers commit and push, chosen, and merge, not chosen
      ```
      ```
      // the graph holds no operation this observation calls
      it And it offers a branch for billing-report, chosen
      ```
    Cancel the switch
      ```
      // the graph holds no operation this observation calls
      it Then the dialog is closed
      ```
      ```
      // the graph holds no operation this observation calls
      it And checkout-flow is still the active ticket
      ```
  Close Active Session
    Complete the active ticket with its work committed
      ```
      // the graph holds no operation this observation calls
      it Then a dialog headed Close session Checkout flow offers commit and push, chosen
      ```


with a chat connected
  Open Ticket Session
    Ask a chat to open a ticket
      ```
      -> BoardReader.poll()
      it Then the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish
      ```
  Close Active Session
    Close the active session from its card
      ```
      -> BoardReader.poll()
      it Then the chat is sent /space:session:close-session
      ```
      ```
      -> BoardReader.poll()
      it And checkout-flow stays In progress in Discovery
      ```
  Split Ticket Into Child Tickets
    Ask the chat to split a ticket into child tickets
      ```
      -> BoardReader.poll()
      it Then the chat's prompt holds Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.create with parent checkout-flow for each story.
      ```
    Keep Split off on a closed ticket
      ```
      // the graph holds no operation this observation calls
      it Then Split is off
      ```
    Keep Split off on a locked ticket
      ```
      // the graph holds no operation this observation calls
      it Then Split is off
      ```
  Write Ticket Handoff
    Ask the chat to write a handoff
      ```
      -> BoardReader.poll()
      it Then the chat's prompt holds Write a handoff for ticket checkout-flow with /space-session-handoff-session.
      ```
      ```
      // the graph holds no operation this observation calls
      it And a toast says Queued for the prompt, for you to review
      ```
    Hold the handoff until the chat's turn ends
      ```
      // the graph holds no operation this observation calls
      it Then a toast says the fill goes in when this turn ends
      ```
      ```
      -> BoardReader.poll()
      it And the prompt receives the text once the turn has ended
      ```
