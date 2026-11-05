from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../.context/story-map.md#s-person----set-stage-wip-limit
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Set Stage WIP Limit
# Actor: Person
with story("Set Stage WIP Limit"):
    with scenario("Set a stage's limit"):
        # Evidence: observed: board-client.spec 'Set Stage WIP Limit' — 'should save a whole number', 'should read the board again'; Board.set_wip_limit.
        with given("the Discovery [stage](../../../.context/kanban-model.md#stage--column) has the limit 3"):
            pass
        with when("the Person sets Discovery's limit to 4"):
            # Person -> Board.set_wip_limit('Discovery', 4)
            # Board -> .sessions/_board.json: {'wip_limits': {'Discovery': 4}}
            # Board page -> Board.show()
            pass
        with then("Discovery shows the limit 4"):
            pass
        with and_("the limit is still 4 when the board is read again"):
            pass
    with scenario("Give every stage a limit of 3 until a person sets one"):
        # Evidence: observed: kanban_tools_spec and wip_limits.spec.shared 'should give every stage a limit of 3 tickets until a person sets one'.
        with given("the [repository](../../../.context/kanban-model.md#repo) has no .sessions/_board.json"):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Stage -> Stage.wip_limit
            # Board -> Board.wip_limit(stage) <- 3
            pass
        with then("Discovery, Specification, and Implementation each show the limit 3"):
            pass
    with scenario("Show a stage over its limit"):
        # Evidence: observed: kanban_tools_spec 'that sets a stage's limit below the tickets it holds' — 'should show the stage over its limit'; Stage.is_over_limit.
        with given("the Discovery [stage](../../../.context/kanban-model.md#stage--column) holds the [tickets](../../../.context/kanban-model.md#ticket--card) billing-report, move-me, and back-to-backlog"):
            pass
        with when("the Person sets Discovery's limit to 2"):
            # Person -> Board.set_wip_limit('Discovery', 2)
            # Stage -> data_of(Stage) <- is_over_limit: true
            pass
        with then("Discovery's count shows in red, over its limit"):
            pass
    with scenario("Change nothing for a limit that is not a whole number"):
        # Evidence: observed: board-client.spec 'should change nothing for a limit that is not a number'; story-actions.spec 'should close the field on Escape without changing the limit'.
        with given("the Discovery [stage](../../../.context/kanban-model.md#stage--column) has the limit 3"):
            pass
        with when("the Person types many as Discovery's limit"):
            # Person -> BoardClient.submitWipLimit('Discovery', 'many') <- nothing, many is not a whole number
            pass
        with then("Discovery still shows the limit 3"):
            pass
        with but_("no limit is saved"):
            pass
