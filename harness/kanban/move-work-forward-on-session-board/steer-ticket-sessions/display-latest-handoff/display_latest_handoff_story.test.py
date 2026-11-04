from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-board-app----display-latest-handoff
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-realization.md

# Story: Display Latest Handoff
# Actor: Board App
with story("Display Latest Handoff"):
    with scenario("Show the latest handoff"):
        # Evidence: observed: kanban_tools_spec 'with handoffs written for the ticket' — 'should show the latest handoff'; side-panel-client.spec 'with its latest handoff opened' — 'should show the handoff in a tab', 'should read the handoff's text'.
        with given("checkout-flow's [session](../../../.context/kanban-model.md#session) folder holds handoff-20261101T120000.md and an earlier handoff"):
            pass
        with when("the Person selects checkout-flow"):
            # Board page -> Ticket.latest_handoff
            # Ticket <- .sessions/checkout-flow/handoff-20261101T120000.md
            pass
        with then("the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md"):
            pass
        with when("the Person opens the handoff"):
            # Person -> Ticket.read_file('.sessions/checkout-flow/handoff-20261101T120000.md')
            pass
        with then("the files panel shows the handoff in a tab with its text # Handoff"):
            pass
    with scenario("Say a ticket has no handoff"):
        # Evidence: observed: kanban_tools_spec 'should show no handoff for a ticket that has none'; details-view.tsx.
        with given("billing-report's [session](../../../.context/kanban-model.md#session) folder holds no handoff"):
            pass
        with when("the Person selects billing-report"):
            # Person -> TicketClient.select()
            # Board page -> Ticket.latest_handoff <- none
            pass
        with then("the details say No handoff yet"):
            pass
