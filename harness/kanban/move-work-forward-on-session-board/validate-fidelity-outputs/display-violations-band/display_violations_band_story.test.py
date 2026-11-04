from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-board-app----display-violations-band
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-realization.md

# Story: Display Violations Band
# Actor: Board App
#
# Acceptance criteria:
# - Show Violations Band: the band shows the active ticket's violations, and only when it has some. Observed: `ViolationsBandView` in `board-page-view.tsx`.
with story("Display Violations Band"):
    with scenario("Show the active ticket's violations in a band"):
        # Evidence: observed: board-page-view.tsx ViolationsBandView; story-actions.spec 'should name the active ticket's violations across the page top'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card) with violations on stories-story_map"):
            pass
        with when("the session board reads the board"):
            # Board page -> Board.show()
            # Board <- active ticket checkout-flow with progress violations on stories-story_map
            pass
        with then("a band across the page top names checkout-flow's violations"):
            pass
    with scenario("Show no band when the active ticket is clean"):
        # Evidence: observed: board-page-view.tsx draws the band only when the active ticket has violated fidelities.
        with given("billing-report is the active [ticket](../../../.context/kanban-model.md#ticket--card) with no violations"):
            pass
        with when("the session board reads the board"):
            # Board page -> Board.show()
            # Board <- active ticket billing-report with no violated fidelity
            pass
        with then("no violations band shows"):
            pass
