from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----open-validation-report
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Open Validation Report
# Actor: Person
with story("Open Validation Report"):
    with scenario("Open a fidelity's latest report"):
        # Evidence: observed: kanban_tools_spec 'with validation reports saved for a fidelity' — 'should show that fidelity's latest report', 'should list each rule the report names with its violations', 'should give a violation the line it failed on', 'should show the source lines around a violation'; side-panel-client.spec 'Open Validation Report'; story-actions.spec 'should show the rules with the failing line marked'.
        with given("checkout-flow's story map has the validation report stories-story-map-20261101T100000.md with its saved graph"):
            pass
        with and_("the graph names verb-noun-format on .context/story-map.md line 6"):
            pass
        with when("the Person opens checkout-flow's story_map report"):
            # Person -> Ticket.report('stories-story-map')
            # Ticket -> Ticket.reports <- .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md
            # Ticket <- path, text, rules from the saved graph, has_saved_graph: true
            pass
        with then("the report panel shows .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md"):
            pass
        with and_("it lists verb-noun-format with one violation at .context/story-map.md line 6 and the source lines around it"):
            pass
    with scenario("Show every fidelity's violations at once"):
        # Evidence: observed: side-panel-client.spec 'should show every fidelity's violations with no fidelity named'; kanban_tools_spec 'with violations left on two fidelities', 'should list a rule two fidelities share once'.
        with given("checkout-flow has violations"):
            pass
        with when("the Person opens checkout-flow's violations from its card"):
            # Person -> Ticket.violations()
            # Ticket -> Ticket.report(each fidelity with violations)
            pass
        with then("the report panel shows .sessions/checkout-flow/validation-reports with every rule broken, each naming its fidelity"):
            pass
    with scenario("Say a report has no saved graph"):
        # Evidence: observed: kanban_tools_spec 'with a validation report saved without its graph' — 'should say a report has no saved graph', 'should still return the report's text'.
        with given("the ticket's latest story_map report has no graph saved beside it"):
            pass
        with when("the Person opens the story_map report"):
            # Person -> Ticket.report('stories-story-map') <- rules: [], has_saved_graph: false
            pass
        with then("the report panel shows the report's text"):
            pass
        with and_("it says the report has no saved graph in place of saying it has no violations"):
            pass
    with scenario("Open a violation's file at its line"):
        # Evidence: observed: story-actions.spec 'should open a violation's file at its line in the Files panel'; side-panel-client.spec 'with a violation in a file its fidelity does not declare'.
        with given("checkout-flow's story_map report is open"):
            pass
        with when("the Person opens the verb-noun-format violation"):
            # Person -> Ticket.read_file('.context/story-map.md')
            pass
        with then("the files panel shows .context/story-map.md with line 6 marked"):
            pass
    with scenario("Say there is no report"):
        # Evidence: observed: kanban_tools_spec 'should show no report for a fidelity that has none'.
        with given("billing-report has no validation report"):
            pass
        with when("the session board reads billing-report"):
            # Ticket -> Ticket.reports <- none
            pass
        with then("the story_map bar shows no report link"):
            pass
