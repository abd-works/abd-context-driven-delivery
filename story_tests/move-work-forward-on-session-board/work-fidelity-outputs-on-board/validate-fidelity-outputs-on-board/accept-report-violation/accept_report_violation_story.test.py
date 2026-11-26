from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----accept-report-violation
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Accept Report Violation
# Actor: Person
with story("Accept Report Violation"):
    with scenario("Accept a violation as it is"):
        # Evidence: observed: validate-fidelity-outputs.story.shared.py (domain and server tiers) and validate-fidelity-outputs.story.ui.spec.ts 'Accept a violation as it is'; side-panel-client.spec 'with Accept pressed on one violation'.
        with given("checkout-flow's story_map report lists verb-noun-format at .context/story-map.md line 6, on the story node-1, saying Name the story with a verb"):
            pass
        with when("the Person accepts that violation"):
            # Board page -> FidelityProgress.accept_violation(rule, message, location, line, node_id)
            # FidelityProgress -> ReportFile.accept(the violation as the report showed it)
            # ReportFile -> AcceptedViolations.accept(the violation as the saved graph names it)
            pass
        with then(".context/violations-accepted.json keeps verb-noun-format on node-1 with the message Name the story with a verb"):
            pass
        with and_("the story_map report lists no rules and says it leaves out 1 accepted violation"):
            # FidelityProgress.report() -> ReportFile.report() -> AcceptedViolations.accepted_among(the report's violations)
            pass
        with and_("the story_map tile marks Validate ✓ with no violations"):
            # Ticket.load() -> FidelityProgress.from_log() -> FidelityProgress._with_accepted_left_out()
            pass
    with scenario("Leave an accepted violation out of the next validation"):
        # Evidence: observed: validate-fidelity-outputs.story.shared.py (domain tier); checked_graph_spec 'that checks a graph one of whose violations a person accepted'; validation_report_spec 'should say how many accepted violations it leaves out and the file that keeps them'.
        with given("the session checkout-flow has an entity root with a private-method-naming violation"):
            pass
        with and_("Claude Code validated ddd-tactics on that file"):
            pass
        with and_("the Person accepted every private-method-naming violation of the ddd-tactics report"):
            pass
        with when("Claude Code validates ddd-tactics on that file again"):
            # Validate.validate() -> CheckedGraph.violations() -> AcceptedViolations.open_among(the graph's violations)
            # ReportText -> CheckedGraph.accepted()
            pass
        with then("the validation report names no private-method-naming violation"):
            pass
        with and_("it says how many accepted violations it leaves out, kept in .context/violations-accepted.json"):
            pass
        with and_("the session log's validate line names no private-method-naming violation"):
            pass
    with scenario("Show an accepted violation again once its finding changes"):
        # Evidence: observed: validate-fidelity-outputs.story.shared.py (domain tier) and validate-fidelity-outputs.story.ui.spec.ts; accepted_violations_spec 'should show it again when the finding's message changes', 'should show it again when the node's id changes'.
        with given("the Person accepted verb-noun-format on node-1 saying Name the story with a verb"):
            pass
        with when("Claude Code validates the story map again and finds verb-noun-format on node-1 saying Name the story with a verb and a noun"):
            pass
        with then("the story_map report lists verb-noun-format with one violation again"):
            pass
        with and_("the story_map tile marks Validate as violations"):
            pass
    with scenario("Accept a judged finding on a line of a file"):
        # Evidence: observed: validate-fidelity-outputs.story.shared.py (domain tier); accepted_violations_spec 'with a judged finding on a line of a file accepted'.
        with given("checkout-flow's story_map report's judgment fails do-not-invent-requirements at story-map.md line 7, which reads - Confirm Order"):
            pass
        with when("the Person accepts that finding"):
            pass
        with then(".context/violations-accepted.json keeps do-not-invent-requirements on .context/story-map.md with the judged content - Confirm Order and no line number"):
            pass
        with and_("the story_map report lists no rules"):
            pass
    with scenario("Take an acceptance back"):
        # Evidence: observed: validate-fidelity-outputs.story.shared.py (domain and server tiers) and validate-fidelity-outputs.story.ui.spec.ts 'Take an acceptance back'.
        with given("the Person accepted verb-noun-format on node-1 saying Name the story with a verb"):
            pass
        with and_("the story_map report lists that violation among the accepted ones"):
            pass
        with when("the Person takes that acceptance back"):
            # Board page -> FidelityProgress.reopen_violation(rule, message, location, line, node_id)
            # FidelityProgress -> ReportFile.reopen() -> AcceptedViolations.reopen()
            pass
        with then("the story_map report lists verb-noun-format with one violation again"):
            pass
        with and_(".context/violations-accepted.json keeps no acceptance"):
            pass
    with scenario("Refuse accepted violations that are not readable JSON"):
        # Evidence: observed: validate-fidelity-outputs.story.shared.py (domain tier); accepted_violations_spec 'whose file is not readable JSON'.
        with given("checkout-flow's story map has violations"):
            pass
        with and_(".context/violations-accepted.json is not readable JSON"):
            pass
        with when("the Person opens checkout-flow's story_map report"):
            pass
        with then("the report is refused, naming .context/violations-accepted.json and how to repair it"):
            # AcceptedViolations -> AcceptedViolationsUnreadable(the file, what is wrong in it)
            pass
        with and_("the file is left as it was"):
            pass
