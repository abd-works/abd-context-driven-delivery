from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-person----open-help
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Open Help
# Actor: Person
#
# Acceptance criteria:
# - Fidelity help shows its overview, guidance, and rules. Observed.
# - Practice help shows its overview, guidance, and shared rules. Observed.
# - The Forge link opens the fidelity's or practice's page, as the catalog generator names it; a fidelity the catalog has no page for links to its practice's page. Observed: `Help.href` reads `CatalogPractice`; kanban_spec 'with help open on a fidelity the catalog has no page for'.
with story("Open Help"):
    with scenario("Open a fidelity's help"):
        # Evidence: observed: kanban_tools_spec 'that opens help on a fidelity' — 'should show the fidelity's rules', 'should name the stage a fidelity belongs to', 'should link to the fidelity's page on the forge'; story-actions.spec 'should show a fidelity's overview, guidance, rules, and Forge link'.
        with given("billing-report's story_map tile is shown"):
            pass
        with when("the Person opens help on the story_map fidelity"):
            # Person -> FidelityProgress.help()
            # FidelityProgress <- Help(practice, fidelity, stage Discovery): overview, guidance, rules, href
            pass
        with then("a side panel shows story_map's overview, guidance, and rules such as verb-noun-format"):
            pass
        with and_("it names the stage Discovery"):
            pass
        with and_("its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html"):
            pass
    with scenario("Open a practice's help"):
        # Evidence: observed: kanban_tools_spec 'that opens help on a practice' — 'should show the practice's shared rules', 'should name no fidelity on a practice's help'; story-actions.spec 'should head a practice's rules SHARED RULES and say Practice overview'.
        with given("billing-report's [practices](../../../.context/kanban-model.md#practiceguidance) are shown in the details"):
            pass
        with when("the Person opens help on the Stories practice"):
            # Person -> Board.help('stories')
            pass
        with then("a side panel shows Practice overview and SHARED RULES such as do-not-invent-requirements"):
            pass
        with and_("it names no fidelity"):
            pass
        with and_("its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/context-tools/stories.html"):
            pass
    with scenario("Link the ddd model fidelity to its own page"):
        # Evidence: observed: the catalog generator writes cdd_guidance/catalog/fidelities/ddd-model.html; guide-work-through-practices.story.shared.py.
        with given("the catalog has a page for the ddd model fidelity"):
            pass
        with when("the Person opens help on the ddd model fidelity"):
            # Person -> FidelityProgress.help()
            pass
        with then("its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/ddd-model.html"):
            pass
