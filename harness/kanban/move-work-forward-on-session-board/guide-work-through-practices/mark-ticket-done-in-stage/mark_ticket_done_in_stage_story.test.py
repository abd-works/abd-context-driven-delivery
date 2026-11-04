from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-person----mark-ticket-done-in-stage
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Mark Ticket Done In Stage
# Actor: Person
with story("Mark Ticket Done In Stage"):
    with scenario("Mark a ticket done in its stage"):
        # Evidence: observed: kanban_spec 'with its stage not done' / 'that a person has moved on' — 'should be done in its stage, in the same column', 'should have no next'; move_ticket.behavior.e2e 'should say in a toast that it is done in its stage'.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery with only its story map generated"):
            pass
        with when("the Person marks pet-visits done in Discovery"):
            # Person -> Ticket.move_next()
            # Ticket -> Ticket.is_done <- false
            # Ticket -> Ticket.record('done Discovery')
            pass
        with then("pet-visits shows in Discovery's Done"):
            pass
        with and_("it has no next step"):
            pass
        with and_("a toast says Pet visits moved to Discovery · Done"):
            pass
    with scenario("Mark a ticket back in progress"):
        # Evidence: observed: kanban_tools_spec 'and back from Done' — 'should show the ticket in progress in that stage'; kanban_spec 'that a person has dragged back into its own stage's in progress part'.
        with given("the ticket ready-to-move is in Discovery's Done"):
            pass
        with when("the Person moves ready-to-move back into Discovery's In progress"):
            # Person -> Ticket.move_to('Discovery')
            # Ticket -> Ticket.record('in-progress Discovery')
            pass
        with then("ready-to-move shows In progress in Discovery"):
            pass
