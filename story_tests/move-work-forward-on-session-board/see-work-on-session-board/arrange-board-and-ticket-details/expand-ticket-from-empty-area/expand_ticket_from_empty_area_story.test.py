from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Arrange Board And Ticket Details
# Map: ../../../../.context/story-map.md#s-person----expand-ticket-from-empty-area
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Expand Ticket From Empty Area
# Actor: Person
with story("Expand Ticket From Empty Area"):
    with scenario("Expand one ticket's card at a time"):
        # Evidence: observed: tile-client.spec 'Expand Ticket' — 'should open with its tiles only, each opening its own action bar', 'should expand only one card at a time'; story-actions.spec 'should expand only one card at a time'.
        with given("the card of the [ticket](../../../../.context/kanban-model.md#ticket--card) checkout-flow is expanded over the board"):
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
        with given("billing-report's card shows a segment for the story_map [fidelity](../../../../.context/kanban-model.md#fidelityguidance)"):
            pass
        with when("the Person opens billing-report's story_map segment"):
            # Person -> OpenCardClient.openSegment(billing-report, Discovery, 'stories-story-map')
            pass
        with then("billing-report's card is expanded with the story_map tile's action bar open"):
            pass
