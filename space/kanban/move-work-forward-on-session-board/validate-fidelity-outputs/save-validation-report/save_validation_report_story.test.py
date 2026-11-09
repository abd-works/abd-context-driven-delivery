from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-claude-code----save-validation-report
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Save Validation Report
# Actor: Claude Code
with story("Save Validation Report"):
    with scenario("Save the report and the graph it checked"):
        # Evidence: observed: cdd_guidance/actions/validate/validate_spec.py 'should save the report in the session's reports folder, named after the fidelity and date', 'should save the graph it checked beside the report, under the same name', 'should keep the rule hits on the nodes of the saved graph', 'should say where the report is saved'.
        with given("the [session](../../../.context/kanban-model.md#session) checkout-flow has an entity root with a private-method-naming violation"):
            pass
        with when("Claude Code validates ddd-tactics on that file"):
            # Validate -> Graph.load_files(folder, ['ddd'], [file], [])
            # Graph -> Ddd.reading.in_graph.check()
            # Validate -> Graph.saved(files) written to <report>.json
            # Validate -> ChatLog.validation(FidelitySessionOutput(Ddd tactics), ['private-method-naming ...'])
            pass
        with then("the validation report is saved as validation-reports/ddd-tactics-20261101T100000.md naming private-method-naming"):
            pass
        with and_("the graph it checked is saved beside it as ddd-tactics-20261101T100000.json, with the rule hits on its nodes"):
            pass
        with and_("Claude Code's reply says where the report is saved"):
            pass
    with scenario("Save one report for each listed guidance"):
        # Evidence: observed: validate_spec.py 'should save a report for each listed guidance'.
        with given("the session checkout-flow has edited files for ddd-tactics and stories-scenarios"):
            pass
        with when("Claude Code validates ddd-tactics and stories-scenarios together"):
            # Agent -> Validate.validate(['ddd-tactics', 'stories-scenarios'])
            pass
        with then("validation-reports holds one stories-scenarios report and one ddd-tactics report"):
            pass
    with scenario("Leave an earlier report's graph as it was"):
        # Evidence: observed: validate_spec.py 'should leave an earlier report's saved graph as it was'.
        with given("validation-reports holds ddd-tactics-20200101T000000.json"):
            pass
        with when("Claude Code validates ddd-tactics again"):
            # Agent -> Validate.validate(['ddd-tactics'])
            pass
        with then("ddd-tactics-20200101T000000.json is unchanged"):
            pass
