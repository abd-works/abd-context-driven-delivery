from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----choose-action-and-formats
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Choose Action And Formats
# Actor: Person
with story("Choose Action And Formats"):
    with scenario("Pick the fidelity's default format"):
        # Evidence: observed: tile-client.spec 'should give each fidelity its default format'; kanban_tools_spec 'should give each fidelity its default format'.
        with given("billing-report's story_map [fidelity](../../../.context/kanban-model.md#fidelityguidance) has no file generated"):
            pass
        with when("the Person opens the story_map tile"):
            # Board page -> Ticket.format_choices(['stories-story-map'])
            # Ticket <- markdown .context/story-map.md, not there
            pass
        with then("the generate action is chosen with the markdown chip picked"):
            pass
    with scenario("Leave a generated format unpicked"):
        # Evidence: observed: tile-client.spec 'should not pick a format already generated'; register.test 'a format already generated carries a check' in the map.
        with given("billing-report's story map is .context/story-map.md, already there"):
            pass
        with when("the Person opens the story_map tile"):
            # Person -> TileClient.toggle(billing-report, story_map tile)
            pass
        with then("the markdown chip is green and not picked"):
            pass
    with scenario("Stand one chip for a group of formats"):
        # Evidence: observed: tile-client.spec 'should let a chip stand for a group', 'should give each fidelity its default format from a chip', 'with a format generated on one fidelity of two'.
        with given("billing-report's story map is generated in markdown and its bounded context is not"):
            pass
        with when("the Person opens the Discovery stage head on story_map and bounded_context"):
            # Person -> TileClient.toggle(billing-report, Discovery stage head)
            pass
        with then("the bar shows a diagram chip and a markdown chip"):
            pass
        with and_("the markdown chip reads 1 of 2 with the hint markdown: 1 of 2 done"):
            pass
    with scenario("Keep Run off with no format picked"):
        # Evidence: observed: tile-client.spec 'should keep Run off until a format is chosen'.
        with given("billing-report's story map is already in markdown"):
            pass
        with but_("no format is picked"):
            pass
        with when("the session board draws the story_map bar"):
            # Board page -> TileActionsClient.barOf(billing-report, Discovery, story_map tile) <- runOff: true
            pass
        with then("Run is off"):
            pass
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
