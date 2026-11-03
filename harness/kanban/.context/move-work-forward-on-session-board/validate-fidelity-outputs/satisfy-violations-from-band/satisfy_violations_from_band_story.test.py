from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../story-map.md#s-person----satisfy-violations-from-band
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Satisfy Violations From Band
# Actor: Person
with story("Satisfy Violations From Band"):
    with scenario("Show the active ticket's violations in a band"):
        # Evidence: observed: board-page-view.tsx ViolationsBandView; story-actions.spec 'should name the active ticket's violations across the page top and fill the prompt'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) with violations on stories-story_map"):
            pass
        with when("the session board reads the board"):
            # Board page -> Board.show()
            # Board <- active ticket checkout-flow with progress violations on stories-story_map
            pass
        with then("a band across the page top names checkout-flow's violations with Show and Satisfy"):
            pass
    with scenario("Fill the prompt with the fidelities that have violations"):
        # Evidence: observed: ticket-client.spec 'Satisfy Violations From Band' — 'should fill the prompt with the fidelities that have violations'.
        with given("the band names checkout-flow's violations on stories-story_map"):
            pass
        with and_("a chat is connected"):
            pass
        with when("the Person satisfies the violations from the band"):
            # Board page -> Chat.send('fill', '/actions-satisfy stories-story-map')
            pass
        with then("the chat's prompt holds /actions-satisfy stories-story-map"):
            pass
    with scenario("Keep Satisfy off with no chat"):
        # Evidence: observed: tests/board-surface.spec.ts 'with no chat connected' — 'should say to load the mod and turn off what sends to a chat'.
        with given("the band names checkout-flow's violations"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the Person looks at the band"):
            pass
        with then("Satisfy is off"):
            pass
    with scenario("Show no band when the active ticket is clean"):
        # Evidence: observed: board-page-view.tsx draws the band only when the active ticket has violated fidelities.
        with given("billing-report is the active [ticket](../../../kanban-model.md#ticket--card) with no violations"):
            pass
        with when("the session board reads the board"):
            pass
        with then("no violations band shows"):
            pass
