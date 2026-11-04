from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../.context/story-map.md#s-person----restrict-actions-to-active-session
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Restrict Actions To Active Session
# Actor: Person
with story("Restrict Actions To Active Session"):
    with scenario("Lock tickets that are not the active session"):
        # Evidence: observed: ticket-client.spec 'should lock a ticket that is not the active session', 'should leave the active ticket open'; tile-client.spec 'should keep Run off on a locked ticket'; ticket-client.tsx runNextHint for a locked ticket; story-actions.spec 'should keep its practice switches off until Active session only is turned off'.
        with given("Active session only is on"):
            pass
        with and_("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the session board draws billing-report's card and tiles"):
            # Board page -> TicketClient.isLocked <- true
            pass
        with then("billing-report's Run next, Run, practice switches, Split, and Handoff are off"):
            pass
        with and_("billing-report's Run next says Activate this session to run its next step"):
            pass
        with and_("checkout-flow's actions stay on"):
            pass
    with scenario("Keep information and moves open on a locked ticket"):
        # Evidence: observed: story-actions.spec 'should let a ticket that is not active be dragged, activated, and its files opened'; ticket-card-view.tsx keeps every card draggable.
        with given("Active session only is on"):
            pass
        with and_("billing-report is not the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the Person opens billing-report's files"):
            # Person -> Ticket.files(['stories-story_map'])
            pass
        with then("the files panel lists billing-report's files"):
            pass
        with when("the Person moves billing-report to Specification"):
            # Person -> Ticket.move_to('Specification')
            pass
        with then("billing-report moves to Specification"):
            pass
        with and_("Activate stays on for billing-report"):
            pass
    with scenario("Unlock every ticket"):
        # Evidence: observed: ticket-client.spec 'should unlock every ticket with Active session only off'.
        with given("Active session only is on"):
            pass
        with when("the Person turns Active session only off"):
            # Person -> BoardLayoutClient.toggleOnlyActive()
            pass
        with then("billing-report's actions are on like the active ticket's"):
            pass
