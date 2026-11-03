from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../story-map.md#s-person----choose-action-and-formats
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Choose Action And Formats
# Actor: Person
with story("Choose Action And Formats"):
    with scenario("Pick the fidelity's default format"):
        # Evidence: observed: tile-client.spec 'should give each fidelity its default format'; kanban_tools_spec 'should give each fidelity its default format'.
        with given("billing-report's story_map [fidelity](../../../kanban-model.md#fidelityguidance) has no file generated"):
            pass
        with when("the Person opens the story_map tile"):
            # Board page -> Ticket.files(['stories-story_map'])
            # Ticket <- markdown tests/story-map.md, not there
            pass
        with then("the generate action is chosen with the markdown chip picked"):
            pass
    with scenario("Leave a generated format unpicked"):
        # Evidence: observed: tile-client.spec 'should not pick a format already generated'; register.test 'a format already generated carries a check' in the map.
        with given("billing-report's story map is tests/story-map.md, already there"):
            pass
        with when("the Person opens the story_map tile"):
            pass
        with then("the markdown chip is green and not picked"):
            pass
    with scenario("Stand one chip for a group of formats"):
        # Evidence: observed: tile-client.spec 'should let a chip stand for a group', 'should give each fidelity its default format from a chip', 'with a format generated on one fidelity of two'.
        with given("billing-report's story map is generated in markdown and its bounded context is not"):
            pass
        with when("the Person opens the Discovery stage head on story_map and bounded_context"):
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
        with when("the Person looks at the story_map bar"):
            pass
        with then("Run is off"):
            pass
    with scenario("Keep Run off on a render with nothing to render"):
        # Evidence: observed: tile-client.spec 'should keep Run off on a render with nothing to render'.
        with given("billing-report's story map has no file"):
            pass
        with when("the Person chooses render on the story_map bar"):
            pass
        with then("Run is off"):
            pass
    with scenario("Keep Run off with no chat or on a locked ticket"):
        # Evidence: observed: tile-client.spec 'should keep Run off with no chat connected', 'should keep Run off on a locked ticket'.
        with given("the story_map bar has the markdown chip picked"):
            pass
        with but_("no chat is connected, or the ticket is not the active session with Active session only on"):
            pass
        with when("the Person looks at the story_map bar"):
            pass
        with then("Run is off"):
            pass
