from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Review Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----browse-ticket-folder
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Browse Ticket Folder
# Actor: Person
with story("Browse Ticket Folder"):
    with scenario("Group a stage's files under their folders"):
        # Evidence: observed: side-panel-client.spec 'Browse Ticket Folder' — 'should group the files under their folders'; story-actions.spec 'should show the three modes of the files panel'.
        with given("checkout-flow's Discovery files are tests/a.md, tests/deep/b.md, and src/c.ts"):
            pass
        with when("the Person browses checkout-flow's Discovery files"):
            # Person -> Ticket.files(Discovery's enabled fidelities)
            pass
        with then("the files panel groups a.md and deep/b.md under tests/ and c.ts under src/"):
            pass
    with scenario("Browse the ticket's session folder"):
        # Evidence: observed: side-panel-client.spec 'Browse Ticket's Session Folder' — 'should list every file in the session folder', 'should show them as folders'; kanban_tools_spec 'with files in its session folder'.
        with given("checkout-flow's [session](../../../.context/kanban-model.md#session) folder holds its log and validation-reports/stories-story-map-20261101T100000.md"):
            pass
        with when("the Person browses checkout-flow's session folder"):
            # Person -> Ticket.session -> Session.folder_files()
            pass
        with then("the files panel lists .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md under its folder"):
            pass
