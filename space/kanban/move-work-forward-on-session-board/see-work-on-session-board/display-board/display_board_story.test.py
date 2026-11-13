from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../.context/story-map.md#s-board-app----display-board
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Display Board
# Actor: Board App
#
# Acceptance criteria:
# - Display Connected Status: with the cdd server not connected, a band across the page says so and how to reconnect, until the server answers again. Observed.
# - Draw Board Columns: Backlog, Discovery, Specification, Implementation, and Complete, in that order, with In progress and Done inside each stage. Observed: `board-columns-view.tsx`.
# - Refresh Board After Tool Calls: after a cdd tool call finishes, the board, an open tile, and an open Files panel or report show the state they are in then. Observed.
# - Announce Ticket Changes: a toast shows when a ticket moves, including from In progress to Done and to the Backlog, or a fidelity is done. Observed.
with story("Display Board"):
    with scenario("Draw the columns of the board"):
        # Evidence: observed: kanban_spec 'should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order', 'should have story_map, bounded_context, and ia as Discovery's work required', 'should give every stage Generate and Validate, in that order'.
        with given("a [board](../../../.context/kanban-model.md#board) with the Stories, DDD, and UX [practices](../../../.context/kanban-model.md#practiceguidance) chosen"):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Board page -> Board.show()
            # Board -> Board.columns
            # Board <- Backlog, Stage Discovery, Stage Specification, Stage Implementation, Column Complete
            # Stage -> Stage.work_required
            # Stage <- every chosen practice's fidelities of that stage
            pass
        with then("the [columns](../../../.context/kanban-model.md#column) read Backlog, Discovery, Specification, Implementation, and Complete, in that order"):
            pass
        with and_("each [stage](../../../.context/kanban-model.md#stage--column) shows an In progress list and a Done list"):
            pass
        with and_("the Discovery [stage](../../../.context/kanban-model.md#stage--column) requires story_map, bounded_context, and ia, each through Generate and Validate"):
            pass
    with scenario("Say the cdd server is not connected"):
        # Evidence: observed: board-client.spec 'should show a band when the board read answers that cdd is not connected', 'should show the band when the server itself does not answer' (the band then says not answering); board-header-view.tsx names the button Connect.
        with given("the cdd server behind the session board is not connected"):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Board page -> Board.show()
            # Board page <- the cdd server is not connected
            pass
        with then("a band across the top of the page says The cdd server is not connected"):
            pass
        with and_("the header offers Update"):
            pass
    with scenario("Show a failing tool in a toast"):
        # Evidence: observed: board-client.spec 'with a tool failing' — 'should show no band', 'should show a toast'.
        with given("the [session](../../../.context/kanban-model.md#session) folder .sessions/broken holds a session.json that is not JSON"):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Board page -> Board.show()
            # Board -> Board.tickets
            # Board <- JsonFileUnreadable
            pass
        with then("a toast says cdd board.show failed: JsonFileUnreadable: .sessions/broken/session.json is not a readable JSON object (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))"):
            pass
        with but_("no band says the cdd server is lost"):
            pass
    with scenario("Install the board again"):
        # Evidence: observed: board-client.spec 'that a person has pressed Update'; board-page.ts update posts App.install of the Kanban app through its generated client (editor-app-client.ts kanban).
        with given("the board is open"):
            pass
        with when("the Person presses Update"):
            # Board page -> App: install (app.install, the Kanban app)
            # App -> npm install  [External: npm]
            # App -> npm run build  [External: npm]
            pass
        with then("the Kanban app is installed again through App.install, which installs its packages and rebuilds its page"):
            pass
        with and_("the page loads again from the new build"):
            pass
    with scenario("Say why the board's install failed"):
        # Evidence: observed: board-client.spec 'with an install that fails'; app.py AppNotStarted.
        with given("npm cannot install the Kanban app"):
            pass
        with when("the Person presses Update"):
            # Board page -> App: install
            # App <- AppNotStarted
            pass
        with then("a toast says the Kanban install failed, with the reason and the fix"):
            pass
        with and_("the page keeps running as it was"):
            pass
    with scenario("Keep the newer board when an older read answers late"):
        # Evidence: observed: board-client.spec 'Refresh Board After Tool Calls' — 'should keep the newer board when an older read answers late'; board-reader.ts refresh.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) move-me is In progress in the Discovery [stage](../../../.context/kanban-model.md#stage--column)"):
            pass
        with and_("a read of the [board](../../../.context/kanban-model.md#board) is still waiting for its answer"):
            pass
        with and_("another chat has moved move-me into Discovery's Done"):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board) again"):
            # Board page -> Board.show()
            # Board <- move-me done in Discovery
            pass
        with then("the session board shows move-me in Discovery's Done even though the older read answered last"):
            pass
    with scenario("Announce a ticket that moved"):
        # Evidence: observed: board-client.spec 'Announce Ticket Changes' — 'should name the new column of a ticket that moves', 'should raise nothing on the first read', 'should raise nothing on each read of a session open and closed under one name'.
        with given("the session board shows the [ticket](../../../.context/kanban-model.md#ticket--card) move-me In progress in Discovery"):
            pass
        with when("another chat moves move-me into Discovery's Done"):
            # Agent -> Ticket.move_to('Discovery', done=True)
            # Ticket -> TicketWork.record('done Discovery')
            # Board page -> Board.show()
            # Board page -> BoardClient.announcementsSince(earlier read)
            pass
        with then("a toast says Move me moved to Discovery · Done"):
            pass
    with scenario("Announce a fidelity done"):
        # Evidence: observed: board-client.spec 'should name a fidelity that is done'.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) billing-report has the story_map [fidelity](../../../.context/kanban-model.md#fidelityguidance) generated and validated with no violations"):
            pass
        with when("a clean validate of stories-story-map is written to billing-report's [session log](../../../.context/kanban-model.md#session)"):
            # Agent -> validate.validate(stories-story-map) writes a clean validate line
            # Board page -> Board.show()
            # Board <- stories-story-map done on billing-report
            pass
        with then("a toast says stories-story-map done on billing-report"):
            pass
