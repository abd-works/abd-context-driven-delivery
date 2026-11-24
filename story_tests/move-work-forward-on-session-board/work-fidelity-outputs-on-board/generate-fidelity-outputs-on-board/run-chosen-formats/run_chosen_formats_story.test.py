from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----run-chosen-formats
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Run Chosen Formats
# Actor: Person
with story("Run Chosen Formats"):
    with scenario("Keep Run off on a render with nothing to render"):
        # Evidence: observed: tile-client.spec 'should keep Run off on a render with nothing to render'.
        with given("billing-report's story map has no file"):
            pass
        with when("the Person chooses render on the story_map bar"):
            # Person -> TileActionsClient.chooseAction(story_map tile, 'render')
            pass
        with then("Run is off"):
            pass
    with scenario("Keep Run off with no chat"):
        # Evidence: observed: tile-client.spec 'should keep Run off with no chat connected', 'should keep Run off on a locked ticket'.
        with given("the story_map bar has the markdown chip picked"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the session board draws the story_map bar"):
            # Board page -> ChatClient.canSend <- false
            # Board page -> TileActionsClient.barOf(billing-report, Discovery, story_map tile) <- runOff: true
            pass
        with then("Run is off"):
            pass
    with scenario("Keep Run off on a locked ticket"):
        # Evidence: observed: tile-client.spec 'should keep Run off with no chat connected', 'should keep Run off on a locked ticket'.
        with given("Active session only is on"):
            pass
        with and_("billing-report is not the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with and_("billing-report's story_map bar has the markdown chip picked"):
            pass
        with when("the session board draws billing-report's story_map bar"):
            # Board page -> TileActionsClient.barOf(billing-report, Discovery, story_map tile) <- isLocked: true, runOff: true
            pass
        with then("Run is off"):
            pass
