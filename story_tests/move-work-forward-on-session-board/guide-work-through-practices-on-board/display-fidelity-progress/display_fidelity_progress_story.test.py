from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-board-app----display-fidelity-progress
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Display Fidelity Progress
# Actor: Board App
#
# Acceptance criteria:
# - Each fidelity shows Generate and Validate as to do, in progress, or done; a fidelity whose latest validate passes is done. Observed.
with story("Display Fidelity Progress"):
    with scenario("Show Generate done"):
        # Evidence: observed: kanban_spec 'with a fidelity generated' — 'should show Generate done and Validate remaining for that fidelity', 'should still find the practice and fidelity by name'.
        with given("pet-visits' [session log](../../../.context/kanban-model.md#session) has generate /work, /work/docs stories story_map markdown stories"):
            pass
        with when("the session board reads pet-visits"):
            # Ticket -> Ticket.progress
            # Ticket -> FidelityProgress.from_log(story_map, Discovery, lines)
            # FidelityProgress <- done: generate
            pass
        with then("the story_map tile marks Generate ✓ and Validate ○"):
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
        with then("the story_map tile marks Validate as violations and its segment shows in the violations colour"):
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
        with then("the story_map tile marks Generate ✓ and Validate ✓, and the fidelity is done"):
            pass
    with scenario("Complete a stage's work"):
        # Evidence: observed: kanban_spec 'with every required fidelity in its stage done' — 'should have no next'.
        with given("pet-visits has every Discovery fidelity generated and validated with no violations"):
            pass
        with when("the session board reads pet-visits"):
            pass
        with then("pet-visits waits in Discovery's Done"):
            pass
        with and_("it has no next step"):
            pass
    with scenario("Show each fidelity of the stage on the ticket"):
        # Evidence: observed: kanban_tools_spec 'should show each fidelity's Generate and Validate'; Ticket.stage_work for a stage head.
        with given("billing-report has nothing recorded in its [session log](../../../.context/kanban-model.md#session)"):
            pass
        with when("the session board reads billing-report"):
            # Ticket -> data_of(Ticket) <- actions: each fidelity's generate and validate as to_do
            pass
        with then("each Discovery tile marks Generate and Validate ○, its segment dim"):
            pass
