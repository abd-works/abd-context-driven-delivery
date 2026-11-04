from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../story-map.md#s-person----archive-ticket
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Archive Ticket
# Actor: Person
with story("Archive Ticket"):
    with scenario("Archive a ticket off the board"):
        # Evidence: observed: kanban_spec 'that has been archived' — 'should be off the board', 'should have its folder in the archive'; kanban_tools_spec 'that archives a ticket' — 'should leave the ticket off the board'. Called as the ticket.archive tool; the board app has no Archive button.
        with given("the [ticket](../../../kanban-model.md#ticket--card) pet-visits is In progress in Discovery with its story map generated"):
            pass
        with when("the Person archives pet-visits"):
            # Person -> Ticket.archive()
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_archive()
            pass
        with then("no [column](../../../kanban-model.md#column) shows pet-visits"):
            pass
        with and_("its folder is in .sessions/_archive/pet-visits"):
            pass
