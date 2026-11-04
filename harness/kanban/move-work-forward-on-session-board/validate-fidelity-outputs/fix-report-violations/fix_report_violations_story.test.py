from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----fix-report-violations
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Fix Report Violations
# Actor: Person
with story("Fix Report Violations"):
    with scenario("Fix one violation at its line"):
        # Evidence: observed: side-panel-client.spec 'Fix Report Violations' — 'should send Fix for one violation at its line'; story-actions.spec 'should send Fix and Fix all to the chat'.
        with given("checkout-flow's story_map report lists verb-noun-format at tests/story-map.md line 6"):
            pass
        with and_("a chat is connected"):
            pass
        with when("the Person fixes that violation"):
            # Board page -> Chat.send('command', fix message: the verb-noun-format rule, the error at tests/story-map.md:6, and the content that failed)
            pass
        with then("the chat receives one message naming the verb-noun-format rule, the error at tests/story-map.md:6, and the content that failed, with instructions to fix it"):
            pass
    with scenario("Fix every violation of a rule"):
        # Evidence: observed: side-panel-client.spec 'should send Fix all for every violation of a rule'.
        with given("checkout-flow's story_map report lists verb-noun-format"):
            pass
        with when("the Person fixes every violation of verb-noun-format"):
            # Board page -> Chat.send('command', fix message: the verb-noun-format rule and every violation of it, each with its content)
            pass
        with then("the chat receives one message with every verb-noun-format violation, each at its file and line with the content that failed, and instructions to fix them"):
            pass
    with scenario("Fix every violation in the report"):
        # Evidence: observed: side-panel-client.spec 'with Fix all pressed on the whole report' — 'should send one message to the chat', 'should name every rule the report breaks', 'should give every violation of every rule'.
        with given("checkout-flow's report lists violations of verb-noun-format and do-not-invent-requirements"):
            pass
        with and_("a chat is connected"):
            pass
        with when("the Person fixes every violation in the report"):
            # Person -> BoardPage.fixReport('checkout-flow', every rule in the report)
            # Board page -> Chat.send('command', fix message: each rule with every violation of it, each with its content)
            pass
        with then("the chat receives one message naming each rule with every violation of it, each at its file and line with the content that failed, and instructions to fix them all"):
            pass
    with scenario("Read an open report again after the fix"):
        # Evidence: observed: side-panel-client.spec 'with a report and files open as the board changes' — 'should read the report again'.
        with given("checkout-flow's story_map report is open with verb-noun-format listed"):
            pass
        with when("Claude Code validates the story map again with no violations"):
            # Validate -> Session.log_validation(Stories story_map, [])
            # Board page -> Board.show()
            # Board page -> Ticket.report('stories-story_map')
            pass
        with then("the open report lists no rules"):
            pass
