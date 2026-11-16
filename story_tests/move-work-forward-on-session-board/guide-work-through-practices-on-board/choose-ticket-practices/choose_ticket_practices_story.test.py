from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-person----choose-ticket-practices
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Choose Ticket Practices
# Actor: Person
with story("Choose Ticket Practices"):
    with scenario("Turn a practice off for a ticket"):
        # Evidence: observed: kanban_tools_spec 'that turns a practice off for a ticket' — 'should show the practice off for that ticket', 'should save the choice to the ticket's session.json'; ticket-client.spec 'Choose Ticket Practices'; story-actions.spec 'should turn a practice off, say where it was saved, and fade its tile'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card) working on every [practice](../../../.context/kanban-model.md#practiceguidance)"):
            pass
        with and_("its bounded_context tile is open"):
            pass
        with when("the Person turns DDD off for checkout-flow"):
            # Person -> Ticket.enable_practice('ddd', False)
            # Ticket -> Session.enable_practice('ddd', False)
            # PracticeSessionOutput -> .sessions/checkout-flow/session.json practices
            pass
        with then("a toast says DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json"):
            pass
        with and_("the bounded_context tile closes and fades"):
            pass
        with and_("the card shows no DDD segment"):
            pass
    with scenario("Finish a stage on the practices left on"):
        # Evidence: observed: kanban_spec 'with every practice but Stories turned off' — 'should be done with the one practice it works on'.
        with given("pet-visits has generated and validated the story_map [fidelity](../../../.context/kanban-model.md#fidelityguidance)"):
            pass
        with and_("every practice but Stories is turned off for pet-visits"):
            pass
        with when("the session board reads pet-visits"):
            # Ticket -> Ticket.is_done
            # Ticket <- every enabled fidelity of Discovery is done
            pass
        with then("pet-visits shows in Discovery's Done"):
            pass
    with scenario("Keep practice switches off on a locked ticket"):
        # Evidence: observed: story-actions.spec 'should keep its practice switches off until Active session only is turned off'; practice-grid-view.tsx.
        with given("Active session only is on"):
            pass
        with and_("billing-report is not the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the session board draws billing-report's practices"):
            # Board page -> TicketClient.isLocked <- true
            pass
        with then("each practice switch is off until Active session only is turned off"):
            pass
