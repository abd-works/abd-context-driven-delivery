from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-person----open-practice-tile
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Open Practice Tile
# Actor: Person
with story("Open Practice Tile"):
    with scenario("Open a tile on a short hover"):
        # Evidence: observed: tile-client.spec 'should open a tile after a short hover', 'should close it on leaving'.
        with given("billing-report's card is expanded"):
            pass
        with when("the Person rests the pointer on the story_map tile for half a second"):
            # Person -> TileClient.open(spot, false)
            # Board page -> Ticket.files(['stories-story-map'])
            pass
        with then("the story_map tile's action bar opens above the grid, at full width"):
            pass
        with when("the Person moves the pointer away"):
            # Person -> TileClient.hoverOut(billing-report, story_map tile)
            pass
        with then("the action bar closes"):
            pass
    with scenario("Keep a pressed tile open"):
        # Evidence: observed: tile-client.spec 'should keep a tile a person pressed open after the pointer leaves', 'should close on a second press'; story-actions.spec 'should keep a pressed tile open after the pointer leaves'.
        with given("billing-report is selected"):
            pass
        with when("the Person presses the story_map tile"):
            # Person -> TileClient.open(spot, true)
            pass
        with then("the story_map action bar stays open after the pointer leaves"):
            pass
        with when("the Person presses the story_map tile again"):
            # Person -> TileClient.toggle(billing-report, story_map tile)
            pass
        with then("the story_map action bar closes"):
            pass
    with scenario("Keep two pressed tiles open at once"):
        # Evidence: observed: tile-client.spec 'with two tiles pressed' — 'should keep both bars open', 'should close only the bar pressed again', 'should change only that bar's action'; story-actions.spec 'should keep two pressed tiles open at once'.
        with given("billing-report's story_map tile is pressed open"):
            pass
        with when("the Person presses the bounded_context tile"):
            # Person -> TileClient.toggle(billing-report, bounded_context tile)
            pass
        with then("both action bars are open"):
            pass
        with when("the Person chooses sketch on the bounded_context bar"):
            # Person -> TileActionsClient.chooseAction(bounded_context tile, 'sketch')
            pass
        with then("only the bounded_context bar's action is sketch"):
            pass
    with scenario("Open a hovered tile beside a pressed one"):
        # Evidence: observed: tile-client.spec 'with a pressed bar and a bar a hover opened' — 'should open the hovered bar beside the pressed one', 'should replace the hovered bar with the next one a hover opens, and keep the pressed one', 'should close the hovered bar on leaving, and keep the pressed one'.
        with given("billing-report's card is expanded with the story_map tile pressed open"):
            pass
        with when("the Person hovers on the ia tile"):
            # Person -> TileClient.hoverIn(billing-report, ia tile)
            pass
        with then("the ia bar opens beside the story_map bar"):
            pass
        with when("the Person moves the pointer away from the ia tile"):
            # Person -> TileClient.hoverOut(billing-report, ia tile)
            pass
        with then("the ia bar closes and the story_map bar stays open"):
            pass
    with scenario("Leave a tile in the details closed under a resting pointer"):
        # Evidence: observed: story-actions.spec 'should leave a tile in the details closed while the pointer only rests on it'.
        with given("billing-report is shown in the details"):
            pass
        with when("the Person rests the pointer on the story_map tile in the details"):
            # Person -> nothing: a tile in the details opens on TileClient.toggle, not on a resting pointer
            pass
        with then("the story_map action bar stays closed"):
            pass
