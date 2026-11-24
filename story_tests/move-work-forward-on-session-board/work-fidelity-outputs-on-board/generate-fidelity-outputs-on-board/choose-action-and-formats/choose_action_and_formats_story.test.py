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
        with and_("the markdown chip reads 1 of 2 with the hint markdown: 1 of 2 done, selected"):
            pass
    with scenario("Keep the last format picked"):
        # Evidence: observed: practice_session_output_spec 'with one format chosen, left out'; generate-fidelity-outputs.story.ui.spec 'Keep the last format picked'.
        with given("billing-report's story map is already in markdown"):
            pass
        with and_("markdown is the only chip picked on the story_map bar"):
            pass
        with when("the Person unpicks the markdown chip"):
            # Person -> TileActionsClient.toggleFormat(story_map tile, 'markdown') -> Ticket.choose_formats -> FidelityFormats.choose_from -> FidelitySessionOutput.choose_formats -> LastFormatLeftOut
            pass
        with then("a toast says markdown is the only format chosen for story_map"):
            pass
        with and_("the markdown chip stays picked"):
            pass
    with scenario("Refuse a format for a practice turned off"):
        # Evidence: observed: practice_session_output_spec 'of a practice turned off'.
        with given("UX is turned off for billing-report's session"):
            pass
        with when("Claude Code chooses drawio for UX's ia"):
            # Claude Code -> FidelitySessionOutput.choose_format('drawio', True) -> PracticeTurnedOff
            pass
        with then("the choice is refused, saying ux is turned off for the session and to turn ux on first"):
            pass
        with and_("billing-report's session.json keeps no format for ia"):
            pass
