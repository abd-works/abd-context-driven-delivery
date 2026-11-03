from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../story-map.md#s-person----run-action-across-practices
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Run Action Across Practices
# Actor: Person
with story("Run Action Across Practices"):
    with scenario("Sketch every fidelity of a stage in one command"):
        # Evidence: observed: tile-client.spec 'Run Action Across Practices' — 'should name every fidelity of the stage in one command'.
        with given("billing-report is the active [ticket](../../../kanban-model.md#ticket--card) in Discovery and a chat is connected"):
            pass
        with and_("the Discovery stage head's action bar is open"):
            pass
        with when("the Person runs sketch from the Discovery stage head"):
            # Board page -> Chat.send('command', '/actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior')
            pass
        with then("the chat receives the command /actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior"):
            pass
    with scenario("Keep two stage heads open at once"):
        # Evidence: observed: tile-client.spec 'with two stage heads pressed' — 'should keep both stage bars open'.
        with given("billing-report's Discovery stage head is pressed open"):
            pass
        with when("the Person presses the Specification stage head"):
            pass
        with then("both stage bars are open"):
            pass
