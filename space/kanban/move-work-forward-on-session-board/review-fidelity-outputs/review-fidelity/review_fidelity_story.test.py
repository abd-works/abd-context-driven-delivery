from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Review Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----review-fidelity
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Review Fidelity
# Actor: Person
#
# Acceptance criteria:
# - Ignore Early Review: a review before a clean validate does not count. Observed.
# - Complete Stage Work: when every fidelity of a stage is reviewed, the ticket shows in that stage's Done part. Observed: `Ticket.is_done`.
with story("Review Fidelity"):
    with scenario("Review a fidelity after a clean validate"):
        # Evidence: observed: kanban_tools_spec 'with a ticket whose story map has passed validate' — 'should name review as the next action', 'that a person has finished reviewing' — 'should show the fidelity's review done', 'should write the review to the session log'; kanban_spec 'should show the fidelity done'.
        with given("billing-report's story map is generated and its latest validate passed with no graph-rule"):
            pass
        with when("the Person reviews story_map on billing-report"):
            # Person -> Ticket.finish_review(['stories-story-map'])
            # Ticket -> Ticket.record('review Stories story_map')
            # Board page -> Board.show()
            pass
        with then("billing-report's session log ends with review Stories story_map"):
            pass
        with and_("the story_map tile marks Review ✓ and the fidelity is done"):
            pass
        with and_("a toast says stories-story-map done on billing-report"):
            pass
    with scenario("Keep Review off until Validate is clean"):
        # Evidence: observed: tile-client.spec 'should not allow Review until Validate is clean'.
        with given("billing-report's story map has no file"):
            pass
        with but_("nothing is recorded on it"):
            pass
        with when("the session board draws the story_map bar"):
            # Board page -> TileActionsClient.barOf(billing-report, Discovery, story_map tile) <- reviewOff: true
            pass
        with then("review is off"):
            pass
    with scenario("Ignore a review recorded before a clean validate"):
        # Evidence: observed: kanban_spec 'that was reviewed before its validate passed' — 'should not count the review'.
        with given("pet-visits' session log has generate, then review, then validate Stories story_map"):
            pass
        with when("the session board reads pet-visits"):
            # FidelityProgress -> FidelityProgress.from_log(...) <- done: generate, validate
            pass
        with then("the story_map tile marks Review ○"):
            pass
    with scenario("Refuse a fidelity the ticket does not have"):
        # Evidence: observed: kanban_tools_spec 'that a person names a fidelity the ticket does not have' — 'should refuse it, naming the fidelity', 'among fidelities it does have' — 'should write no review for the others named with it'.
        with given("billing-report's story map passed validate"):
            pass
        with when("the Person reviews stories-no_such_fidelity"):
            # Person -> Ticket.finish_review(['stories-story-map', 'stories-no_such_fidelity']) <- FidelityNotFoundError
            pass
        with then("the board says no fidelity named stories-no_such_fidelity on ticket billing-report"):
            pass
        with but_("no review line is written for stories-story-map"):
            pass
    with scenario("Complete a stage's work"):
        # Evidence: observed: kanban_spec 'with every required fidelity in its stage done' — 'should be done, waiting in its stage's done part', 'should have no next'.
        with given("pet-visits has every Discovery fidelity generated, validated, and reviewed"):
            pass
        with when("the session board reads pet-visits"):
            # Stage -> Stage.done
            # Ticket -> Ticket.is_done <- true
            pass
        with then("pet-visits waits in Discovery's Done"):
            pass
        with and_("it has no next step"):
            pass
