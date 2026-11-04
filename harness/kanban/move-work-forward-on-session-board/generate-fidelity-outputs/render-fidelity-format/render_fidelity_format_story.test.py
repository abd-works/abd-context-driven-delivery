from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----render-fidelity-format
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-realization.md

# Story: Render Fidelity Format
# Actor: Person
with story("Render Fidelity Format"):
    with scenario("Render existing output into another format"):
        # Evidence: observed: tile-client.spec 'Render Fidelity Format' — 'should turn existing output into the chosen format'.
        with given("billing-report's story map is tests/story-map.md, in markdown"):
            pass
        with and_("a chat is connected"):
            pass
        with when("the Person renders story_map into the diagram format"):
            # Board page -> Chat.send('command', '/actions-render stories-story-map format=drawio')
            pass
        with then("the chat receives the command /actions-render stories-story-map format=drawio"):
            pass
    with scenario("Keep render off with nothing to render"):
        # Evidence: observed: tile-client.spec 'should keep Run off on a render with nothing to render'.
        with given("billing-report's story map has no file"):
            pass
        with when("the Person chooses render on the story_map bar"):
            # Person -> TileActionsClient.chooseAction(story_map tile, 'render')
            pass
        with then("Run is off"):
            pass
