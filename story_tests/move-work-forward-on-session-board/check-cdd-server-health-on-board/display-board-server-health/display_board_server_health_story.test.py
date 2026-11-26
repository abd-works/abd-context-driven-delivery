from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Check CDD Server Health On Board
# Map: ../../../.context/story-map.md#s-board-app----display-board-server-health
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Display Board Server Health
# Actor: Board App
#
# Acceptance criteria:
# - Display Connected Status: with the cdd server not connected, a band across the page says so and how to reconnect, until the server answers again. Observed.
with story("Display Board Server Health"):
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
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card)s checkout-flow and billing-report are on the [board](../../../.context/kanban-model.md#board)"):
            pass
        with when("the Person adds a child titled Billing report to checkout-flow"):
            # Ticket card -> Ticket.add_child(title)
            # Ticket -> CardName
            # Ticket <- TicketNameTakenError
            pass
        with then("a toast says cdd ticket.add_child failed: TicketNameTakenError: a ticket named billing-report already exists; give 'Billing report' another title"):
            pass
        with but_("no band says the cdd server is lost"):
            pass
