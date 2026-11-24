from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Show Tickets On Board
# Map: ../../../../.context/story-map.md#s-board-app----place-ticket-in-column
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Place Ticket In Column
# Actor: Board App
#
# Acceptance criteria:
# - Place Ticket In Column: a ticket shows in the stage of its latest move, or before any move in the earliest stage its session shows work in. Observed.
with story("Place Ticket In Column"):
    with scenario("Place a ticket in the stage of its latest move"):
        # Evidence: observed: kanban_tools_spec 'should show the ticket in the next stage'; Ticket.column in ticket.py; fixture-repo.ts second-spec.
        with given("the [session log](../../../../.context/kanban-model.md#session) of the [ticket](../../../../.context/kanban-model.md#ticket--card) second-spec ends with move Specification"):
            pass
        with when("the session board reads the [board](../../../../.context/kanban-model.md#board)"):
            # Board -> Ticket.column
            # Ticket <- the stage of its latest move line: Specification
            pass
        with then("second-spec shows In progress in the Specification [stage](../../../../.context/kanban-model.md#stage--column)"):
            pass
    with scenario("Place a ticket with no move in the earliest stage it has work in"):
        # Evidence: observed: kanban_spec 'with its first logged work on a Specification fidelity' — 'should be in Specification'; 'that has just been started' — 'should be in Discovery, in progress'.
        with given("the [session log](../../../../.context/kanban-model.md#session) of the [ticket](../../../../.context/kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux"):
            pass
        with but_("it has no move line"):
            pass
        with when("the session board reads the [board](../../../../.context/kanban-model.md#board)"):
            # Board -> Ticket.column
            # Ticket -> Ticket.progress
            # Ticket <- the first stage with work done: Specification
            pass
        with then("pet-visits shows in the Specification [stage](../../../../.context/kanban-model.md#stage--column)"):
            pass
