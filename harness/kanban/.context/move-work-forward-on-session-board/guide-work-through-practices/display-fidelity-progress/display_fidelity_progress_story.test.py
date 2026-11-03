from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../story-map.md#s-board-app----display-fidelity-progress
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Display Fidelity Progress
# Actor: Board App
with story("Display Fidelity Progress"):
    with scenario("Show Generate done"):
        # Evidence: observed: kanban_spec 'with a fidelity generated' — 'should show Generate done and Validate and Review remaining for that fidelity', 'should still find the practice and fidelity by name'.
        with given("pet-visits' [session log](../../../kanban-model.md#session) has generate /work, /work/docs stories story_map markdown stories"):
            pass
        with when("the session board reads pet-visits"):
            # Ticket -> Ticket.progress
            # Ticket -> FidelityProgress.from_log(story_map, Discovery, lines)
            # FidelityProgress <- done: generate
            pass
        with then("the story_map tile marks Generate ✓ and Validate and Review ○"):
            pass
    with scenario("Show violations held on Validate"):
        # Evidence: observed: kanban_spec 'that has a validate naming graph-rule violations' — 'should still need Validate for that fidelity'; FidelityProgress.action_states marks validate in_progress.
        with given("pet-visits' story_map is generated"):
            pass
        with and_("its latest validate line is validate Stories story_map graph-rule actor-named-in-step map.md:12"):
            pass
        with when("the session board reads pet-visits"):
            # FidelityProgress -> FidelityProgress.from_log(...) <- has_violations: true
            # FidelityProgress -> FidelityProgress.action_states <- validate: in_progress
            pass
        with then("the story_map tile marks Validate as violations and its block shows in the violations colour"):
            pass
        with and_("Review stays to do"):
            pass
    with scenario("Show Validate done after a clean validate"):
        # Evidence: observed: kanban_spec 'that has a validate with no violations' — 'should show Validate done for that fidelity', 'should match the practice's class name in the validate line to its folder name'.
        with given("pet-visits' story_map is generated"):
            pass
        with and_("its latest validate line is validate Stories story_map with no graph-rule"):
            pass
        with when("the session board reads pet-visits"):
            # FidelityProgress -> FidelityProgress.from_log(...) <- done: generate, validate
            pass
        with then("the story_map tile marks Generate ✓, Validate ✓, and Review ○"):
            pass
    with scenario("Show each fidelity of the stage on the ticket"):
        # Evidence: observed: kanban_tools_spec 'should show each fidelity's Generate, Validate, and Review'; ticket-client.tsx standingOf for a stage head.
        with given("billing-report has nothing recorded in its [session log](../../../kanban-model.md#session)"):
            pass
        with when("the session board reads billing-report"):
            # Ticket -> Ticket.to_json() <- actions: each fidelity's generate, validate, review as to_do
            pass
        with then("each Discovery tile marks Generate, Validate, and Review ○, its block dim"):
            pass
