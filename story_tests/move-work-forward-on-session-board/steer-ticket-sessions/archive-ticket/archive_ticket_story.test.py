from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----archive-ticket
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Archive Ticket
# Actor: Person
with story("Archive Ticket"):
    with scenario("Archive a ticket off the board"):
        # Evidence: observed: kanban_spec 'that has been archived' — 'should be off the board', 'should have its folder in the archive'; kanban_tools_spec 'that archives a ticket' — 'should leave the ticket off the board'. Called as the ticket.archive tool; the board app has no Archive button.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery with its story map generated"):
            pass
        with when("the Person archives pet-visits"):
            # Person -> Ticket.archive()
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_archive()
            pass
        with then("no [column](../../../.context/kanban-model.md#column) shows pet-visits"):
            pass
        with and_("its folder is in .sessions/_archive/pet-visits"):
            pass
    with scenario("Refuse to archive a ticket the board does not have"):
        # Evidence: inferred: Ticket.load raises TicketNotFoundError in space/kanban/ticket.py, and ticket.archive loads its ticket by name; no spec archives an unknown ticket.
        with given("the [board](../../../.context/kanban-model.md#board) shows no [ticket](../../../.context/kanban-model.md#ticket--card) named no-such-ticket"):
            pass
        with when("the Person archives no-such-ticket"):
            # Person -> Ticket.load('no-such-ticket') <- TicketNotFoundError
            pass
        with then("the board says no ticket named 'no-such-ticket' on the board"):
            pass
        with but_("nothing is moved to .sessions/_archive"):
            pass
