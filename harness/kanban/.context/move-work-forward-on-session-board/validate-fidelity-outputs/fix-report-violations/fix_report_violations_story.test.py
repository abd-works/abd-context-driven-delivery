from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Validate Fidelity Outputs
# Map: ../../../story-map.md#s-person----fix-report-violations
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

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
            # Board page -> Chat.send('command', '/actions-satisfy stories-story-map tests/story-map.md:6 rule verb-noun-format')
            pass
        with then("the chat receives the command /actions-satisfy stories-story-map tests/story-map.md:6 rule verb-noun-format"):
            pass
    with scenario("Fix every violation of a rule"):
        # Evidence: observed: side-panel-client.spec 'should send Fix all for every violation of a rule'.
        with given("checkout-flow's story_map report lists verb-noun-format"):
            pass
        with when("the Person fixes every violation of verb-noun-format"):
            # Board page -> Chat.send('command', '/actions-satisfy stories-story-map rule verb-noun-format')
            pass
        with then("the chat receives the command /actions-satisfy stories-story-map rule verb-noun-format"):
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
