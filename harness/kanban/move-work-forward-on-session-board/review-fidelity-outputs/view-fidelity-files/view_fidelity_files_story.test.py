from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Review Fidelity Outputs
# Map: ../../../.context/story-map.md#s-person----view-fidelity-files
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: View Fidelity Files
# Actor: Person
with story("View Fidelity Files"):
    with scenario("Open one tab per format, generated or not"):
        # Evidence: observed: side-panel-client.spec 'View Fidelity Files' — 'should open one tab per format, generated or not', 'should read the text of the file a tab shows'; story-actions.spec 'should offer a tab for a format not generated yet and say so'; kanban_tools_spec 'should return the file's text'.
        with given("checkout-flow's story map is tests/story-map.md and tests/story-map.drawio is not there"):
            pass
        with when("the Person views checkout-flow's story_map files"):
            # Person -> Ticket.files(['stories-story_map'])
            # Person -> Ticket.read_file('tests/story-map.md')
            pass
        with then("the files panel shows the tabs tests/story-map.md and tests/story-map.drawio"):
            pass
        with and_("the tests/story-map.md tab shows # Check Out Order"):
            pass
        with and_("the drawio tab says it is not generated yet"):
            pass
    with scenario("Go back to the list when the last tab closes"):
        # Evidence: observed: side-panel-client.spec 'should go back to the list when the last tab closes', 'should keep a tab a person closed closed'.
        with given("the tabs tests/story-map.md and tests/story-map.drawio are open"):
            pass
        with when("the Person closes both tabs"):
            # Person -> FilesPanelClient.closeTab('tests/story-map.md')
            # Person -> FilesPanelClient.closeTab('tests/story-map.drawio')
            pass
        with then("the files panel shows the list"):
            pass
    with scenario("Refuse a file outside the repository"):
        # Evidence: observed: kanban_tools_spec 'should refuse a file outside the repository, naming the path and the ticket'.
        with given("checkout-flow's repository is the project folder"):
            pass
        with when("a file outside the repository is asked for"):
            # Person -> Ticket.read_file('../secrets.txt') <- FileOutsideRepositoryError
            pass
        with then("the board says ../secrets.txt is not a file in this repository"):
            pass
