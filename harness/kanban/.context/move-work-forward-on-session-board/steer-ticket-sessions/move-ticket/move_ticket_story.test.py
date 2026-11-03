from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../story-map.md#s-person----move-ticket
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Move Ticket
# Actor: Person
with story("Move Ticket"):
    with scenario("Move a ticket on to the next column"):
        # Evidence: observed: kanban_tools_spec 'that moves a ticket to the next column' — 'should show the ticket in the next stage', 'should show the ticket in progress there'; kanban_spec 'should write the stage it entered to its session log'; ticket-client.spec 'should read the board again and select the ticket where it landed'.
        with given("the [ticket](../../../kanban-model.md#ticket--card) ready-to-move is in Discovery's Done"):
            pass
        with when("the Person moves ready-to-move on"):
            # Person -> Ticket.move_next()
            # Ticket -> Stage.next_stage <- Specification
            # Ticket -> Ticket.record('move Specification')
            # Board page -> Board.show()
            pass
        with then("ready-to-move is In progress in Specification and selected"):
            pass
        with and_("its session log ends with move Specification"):
            pass
    with scenario("Drag a ticket into a stage's Done whatever its work"):
        # Evidence: observed: kanban_tools_spec 'that drags a ticket into a later stage's Done' — 'should show the ticket in that stage's Done'; kanban_spec 'that a person has dragged into a later stage's done part'; ticket-client.spec 'should select a dragged ticket in the stage it was dropped on'.
        with given("the [ticket](../../../kanban-model.md#ticket--card) move-me is In progress in Discovery with nothing done"):
            pass
        with when("the Person moves move-me into Implementation's Done"):
            # Person -> Ticket.move_to('Implementation', done=True)
            # Ticket -> Ticket.record('move Implementation')
            # Ticket -> Ticket.record('done Implementation')
            pass
        with then("move-me shows in Implementation's Done and is selected"):
            pass
    with scenario("Move a ticket back to the previous column"):
        # Evidence: observed: kanban_tools_spec 'and back to the previous column' — 'should show the ticket in Discovery', 'should show the ticket in Discovery's Done'.
        with given("the [ticket](../../../kanban-model.md#ticket--card) second-spec is In progress in Specification"):
            pass
        with when("the Person moves second-spec back"):
            # Person -> Ticket.move_previous()
            # Ticket -> Stage.previous_stage <- Discovery
            # Ticket -> Ticket.record('move Discovery')
            # Ticket -> Ticket.record('done Discovery')
            pass
        with then("second-spec shows in Discovery's Done"):
            pass
    with scenario("Move a ticket into the Backlog with its work"):
        # Evidence: observed: kanban_tools_spec 'that moves the ticket back out of Discovery' — 'should show an item in the Backlog with the ticket's title', 'should take the ticket off the board's stages'; ticket-client.spec 'that a person has moved to the Backlog', 'should let a ticket in any column be dropped on the Backlog'; board-client.spec 'should say a ticket moved to the Backlog'.
        with given("the [ticket](../../../kanban-model.md#ticket--card) back-to-backlog is In progress in Discovery with its story map generated"):
            pass
        with when("the Person moves back-to-backlog into the Backlog"):
            # Person -> Ticket.move_to('Backlog')
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_backlog()
            # Ticket -> BacklogItem.holding(ticket, board)
            # BacklogItem -> .sessions/_backlog/back-to-backlog/back-to-backlog.md: # Back to backlog
            # Ticket <- BacklogItem Back to backlog
            pass
        with then("the Backlog shows the [backlog item](../../../kanban-model.md#backlogitem--card) Back to backlog and it is selected"):
            pass
        with and_("a toast says Back to backlog moved to Backlog"):
            pass
        with but_("no stage shows back-to-backlog"):
            pass
    with scenario("Close a ticket moved on past Implementation"):
        # Evidence: observed: kanban_tools_spec 'and past Implementation' — 'should close the ticket', 'should leave a ticket in Complete where it is on another move forward'; ticket-client.spec 'should let only the active ticket, or one done in Implementation, be dropped on Complete'.
        with given("the [ticket](../../../kanban-model.md#ticket--card) almost-shipped is in Implementation's Done"):
            pass
        with and_("almost-shipped is not the active ticket"):
            pass
        with when("the Person moves almost-shipped on into Complete"):
            # Person -> Ticket.move_next()
            # Ticket -> Stage.next_stage <- none
            # Ticket -> Ticket.close()
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_closed()
            pass
        with then("almost-shipped shows in Complete"):
            pass
        with and_("its folder is in .sessions/closed/almost-shipped"):
            pass
    with scenario("Reopen a ticket moved back out of Complete"):
        # Evidence: observed: kanban_tools_spec 'and back again' — 'should reopen the ticket in Implementation'; kanban_spec 'that a person has dragged out of Complete' — 'should be open again, in progress in that stage'.
        with given("the closed [ticket](../../../kanban-model.md#ticket--card) shipped-work is in Complete"):
            pass
        with when("the Person moves shipped-work back"):
            # Person -> Ticket.move_previous()
            # Ticket -> Session.reopen()
            # Ticket -> Ticket.record('move Implementation')
            # Ticket -> Ticket.record('done Implementation')
            pass
        with then("shipped-work shows in Implementation's Done"):
            pass
        with and_("its folder is back in .sessions/shipped-work"):
            pass
    with scenario("Refuse a move into a column that is not a stage"):
        # Evidence: observed: NotAStageError in Ticket.move_to; ticket-client.tsx canDropOn accepts Complete only for the active ticket or one done in Implementation. No spec moves a ticket into Complete through move_to.
        with given("the [ticket](../../../kanban-model.md#ticket--card) billing-report is In progress in Discovery"):
            pass
        with and_("billing-report is not the active ticket"):
            pass
        with when("the Person tries to move billing-report into Complete"):
            # Person -> TicketClient.canDropOn('Complete') <- false
            pass
        with then("Complete does not take billing-report"):
            pass
        with and_("billing-report stays In progress in Discovery"):
            pass
