from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----generate-fidelity-output
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-realization.md

# Story: Generate Fidelity Output
# Actor: Person
#
# Acceptance criteria:
# - When a fidelity uses a different format from the one before it, the earlier fidelity is rendered into that format first. Observed: `Ticket.generate_commands`.
with story("Generate Fidelity Output"):
    with scenario("Send the generate command from a tile"):
        # Evidence: observed: tile-client.spec 'Generate Fidelity Output' — 'should send the commands the ticket names', 'should clear the picks'; story-actions.spec 'should send the generate commands from Run on an opened card'.
        with given("billing-report is the active [ticket](../../../.context/kanban-model.md#ticket--card) with nothing generated and a chat is connected"):
            pass
        with and_("its story_map bar has generate chosen and the markdown chip picked"):
            pass
        with when("the Person runs generate on story_map"):
            # Person -> Ticket.generate_commands(['stories-story_map'], ['markdown'])
            # Ticket <- ['/actions-generate stories-story-map format=markdown']
            # Board page -> Chat.send('command', '/actions-generate stories-story-map format=markdown')
            # chat mod -> Chat.check_in() <- the command
            # chat mod -> Claude Code command.run('actions-generate', 'stories-story-map format=markdown')  [External: Claude Code]
            pass
        with then("the chat runs /actions-generate stories-story-map format=markdown"):
            pass
        with and_("the bar's picks are cleared"):
            pass
        with and_("Claude Code goes on to Resolve Fidelity Output Paths for stories-story_map"):
            pass
    with scenario("Render the earlier fidelity into a new format first"):
        # Evidence: observed: kanban_tools_spec 'with a fidelity's markdown generated' — 'should render the earlier fidelity into the new format first'; Ticket.generate_commands.
        with given("pet-visits' story map is docs/story-map.md, generated in markdown only"):
            pass
        with when("the Person generates scenarios in drawio"):
            # Person -> Ticket.generate_commands(['stories-scenarios'], ['drawio'])
            # Ticket -> Session.fidelity_outputs(Stories story_map) <- markdown docs/story-map.md there, drawio not
            pass
        with then("the first command is /actions-render stories-story-map format=drawio source=markdown"):
            pass
        with and_("the last is /actions-generate stories-scenarios format=drawio"):
            pass
    with scenario("Count a generate line as Generate done"):
        # Evidence: observed: kanban_spec 'should show Generate done and Validate and Review remaining for that fidelity'.
        with given("the [session log](../../../.context/kanban-model.md#session) of pet-visits has no generate line for story_map"):
            pass
        with when("Claude Code finishes generating the story map"):
            # Generate -> GuidanceAction.run(...)
            # GuidanceAction -> Session.log_guidance_action('generate', [Stories story_map])
            pass
        with then("the session log ends with a generate line naming stories story_map markdown"):
            pass
        with and_("the story_map tile marks Generate ✓"):
            pass
