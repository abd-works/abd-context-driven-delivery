from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../.context/story-map.md#s-board-app----display-ticket-details
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-realization.md

# Story: Display Ticket Details
# Actor: Board App
#
# Acceptance criteria:
# - A press anywhere on a card shows that ticket in the details region below the board, and with no card pressed the details show the active ticket. Observed.
# - The details show the ticket's practices with their fidelity progress and its latest validation reports. Observed.
# - Expand Ticket: the expanded card shows the same tiles as the details, and only one is expanded at a time. Observed.
with story("Display Ticket Details"):
    with scenario("Show the ticket of a card pressed anywhere"):
        # Evidence: observed: story-actions.spec 'should show the ticket of a card pressed anywhere'; ticket-client.spec 'should name the ticket's stage and how far it has got there', 'should say what runs next'.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) billing-report is In progress in Discovery with nothing recorded"):
            pass
        with when("the Person selects billing-report's card"):
            # Person -> TicketClient.select()
            # Board page -> Ticket.to_json()
            pass
        with then("the details show Billing report, root whole repository, and Discovery · in progress"):
            pass
        with and_("the details say No handoff yet and Next: stories-story_map, generate"):
            pass
        with and_("the details show a tile for each enabled [fidelity](../../../.context/kanban-model.md#fidelityguidance) with its [fidelity progress](../../../.context/kanban-model.md#fidelityprogress)"):
            pass
    with scenario("Show the active ticket with no card pressed"):
        # Evidence: observed: board-client.spec 'should show the active ticket with no card pressed'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with but_("no card is pressed"):
            pass
        with when("the session board draws the details"):
            # Board page -> BoardClient.selectedTicket
            # Board <- active ticket checkout-flow
            pass
        with then("the details show Checkout flow"):
            pass
    with scenario("Show the ticket worked on last when none is active"):
        # Evidence: observed: board-client.spec 'should show the ticket worked on last with none active'.
        with given("no [ticket](../../../.context/kanban-model.md#ticket--card) is active"):
            pass
        with and_("billing-report has the latest line in its session log, at 2026-11-02T10:00:00Z"):
            pass
        with when("the session board draws the details"):
            # Board page -> BoardClient.selectedTicket
            # Board <- the ticket with the latest last_activity: billing-report
            pass
        with then("the details show Billing report"):
            pass
    with scenario("Name a split ticket by the ticket it came from"):
        # Evidence: observed: ticket-client.spec 'should name a split ticket by its parent'.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) child has scope story and parent epic in its session.json"):
            pass
        with when("the Person selects child's card"):
            # Board page -> Ticket.to_json(): scope, parent
            pass
        with then("the details read child · story of epic"):
            pass
    with scenario("Say another session must be activated to act on a locked ticket"):
        # Evidence: observed: ticket-client.spec 'should say another session must be activated to run it'.
        with given("Active session only is on"):
            pass
        with and_("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the Person selects billing-report's card"):
            # Person -> TicketClient.select()
            pass
        with then("the details say Activate this session to run actions"):
            pass
    with scenario("Expand one ticket's card at a time"):
        # Evidence: observed: tile-client.spec 'Expand Ticket' — 'should open with its tiles only, each opening its own action bar', 'should expand only one card at a time'; story-actions.spec 'should expand only one card at a time'.
        with given("the card of the [ticket](../../../.context/kanban-model.md#ticket--card) checkout-flow is expanded over the board"):
            pass
        with when("the Person expands billing-report's card"):
            # Person -> OpenCardClient.toggle(billing-report)
            pass
        with then("billing-report's card is expanded with a tile for each enabled Discovery fidelity"):
            pass
        with and_("checkout-flow's card is closed"):
            pass
    with scenario("Open a card on the fidelity of a pressed segment"):
        # Evidence: observed: tile-client.spec 'with a segment pressed' — 'should open the card', 'should open the tile of that fidelity'; story-actions.spec 'should open a card on the fidelity of a pressed segment'.
        with given("billing-report's card shows a segment for the story_map [fidelity](../../../.context/kanban-model.md#fidelityguidance)"):
            pass
        with when("the Person opens billing-report's story_map segment"):
            # Person -> OpenCardClient.openSegment(billing-report, Discovery, 'stories-story_map')
            pass
        with then("billing-report's card is expanded with the story_map tile's action bar open"):
            pass
