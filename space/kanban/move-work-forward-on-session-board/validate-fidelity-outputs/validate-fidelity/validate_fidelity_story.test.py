from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----validate-fidelity
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Validate Fidelity
# Actor: Person
with story("Validate Fidelity"):
    with scenario("Send the fidelity to validate"):
        # Evidence: observed: tile-client.spec 'Validate Fidelity' — 'should send the fidelity to validate', 'should allow Validate on files already there, with nothing recorded yet'.
        with given("billing-report is the active [ticket](../../../.context/kanban-model.md#ticket--card) and a chat is connected"):
            pass
        with and_("its story map .context/story-map.md is there"):
            pass
        with when("the Person validates story_map"):
            # Board page -> Chat.send('command', '/actions-validate stories-story-map')
            pass
        with then("the chat receives the command /actions-validate stories-story-map"):
            pass
        with and_("Claude Code goes on to Save Validation Report for stories-story-map"):
            pass
    with scenario("Count Validate done only with no graph-rule violations"):
        # Evidence: observed: kanban_spec 'that has a validate with no violations' — 'should show Validate done for that fidelity'; 'that has a validate naming graph-rule violations' — 'should still need Validate for that fidelity'.
        with given("pet-visits' story map is generated"):
            pass
        with when("Claude Code validates the story map and finds no graph-rule violation"):
            # Validate -> Graph.load_files(...)
            # Validate -> ChatLog.validation(FidelitySessionOutput(Stories story_map), [])
            pass
        with then("the session log ends with validate Stories story_map"):
            pass
        with and_("the story_map tile marks Validate ✓"):
            pass
        with when("Claude Code validates it again and finds actor-named-in-step on map.md line 12"):
            # Validate -> ChatLog.validation(FidelitySessionOutput(Stories story_map), ['actor-named-in-step map.md:12'])
            pass
        with then("the session log ends with validate Stories story_map graph-rule actor-named-in-step map.md:12"):
            pass
        with and_("the story_map tile marks Validate as violations again"):
            pass
    with scenario("Keep Validate off with nothing to check"):
        # Evidence: observed: tile-client.spec 'should keep Validate off with no files and nothing recorded', 'should stay off until the ticket allows it'; kanban_tools_spec 'should allow only Generate before anything is generated'.
        with given("billing-report's story map has no file"):
            pass
        with but_("nothing is recorded on it"):
            pass
        with when("the session board draws the story_map bar"):
            # Board page -> TileActionsClient.barOf(billing-report, Discovery, story_map tile) <- validateOff: true
            pass
        with then("validate is off"):
            pass
    with scenario("Allow Validate again on the same output"):
        # Evidence: observed: kanban_tools_spec 'should allow Validate and Review again on the same output'.
        with given("checkout-flow's story map has violations"):
            pass
        with when("the session board reads checkout-flow"):
            # Ticket -> data_of(Ticket) <- allowed_actions: generate, validate, review
            pass
        with then("validate is on for story_map"):
            pass
