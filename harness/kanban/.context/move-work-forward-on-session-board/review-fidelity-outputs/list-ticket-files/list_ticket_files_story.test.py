from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Review Fidelity Outputs
# Map: ../../../story-map.md#s-person----list-ticket-files
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: List Ticket Files
# Actor: Person
with story("List Ticket Files"):
    with scenario("List a fidelity's files with whether each exists"):
        # Evidence: observed: kanban_tools_spec 'with a fidelity's markdown generated' — 'should list the file with whether it exists', 'should list only the fidelities asked for'; side-panel-client.spec 'should list the files that exist'.
        with given("checkout-flow's story map tests/story-map.md is there and tests/story-map.drawio is not"):
            pass
        with when("the Person lists checkout-flow's story_map files"):
            # Person -> Ticket.files(['stories-story_map'])
            # Ticket -> Session.fidelity_outputs(Stories story_map)
            # Ticket <- markdown tests/story-map.md exists, drawio tests/story-map.drawio missing
            pass
        with then("the files panel lists tests/story-map.md as there"):
            pass
        with but_("no file of another fidelity is listed"):
            pass
    with scenario("List only what the ticket's branch changed"):
        # Evidence: observed: kanban_tools_spec 'with specs in the repository and one changed on the ticket's branch' — 'should list only the files the ticket's branch changed'.
        with given("the [ticket](../../../kanban-model.md#ticket--card) pet-visits works on the whole [repository](../../../kanban-model.md#repo) on its own branch pet-visits"):
            pass
        with and_("the repository holds src/theirs_spec.py and its branch added src/mine_spec.py"):
            pass
        with when("the Person lists pet-visits' bdd behavior files"):
            # Person -> Ticket.files(['bdd-behavior'])
            # Ticket -> Repo.files_changed_on('pet-visits')
            pass
        with then("the files panel lists src/mine_spec.py"):
            pass
        with but_("src/theirs_spec.py is not listed"):
            pass
    with scenario("Say in a toast when the list cannot be read"):
        # Evidence: observed: side-panel-client.spec 'with a list that cannot be read' — 'should say so in a toast', 'should open no panel'.
        with given("the board shows no ticket named no-such-ticket"):
            pass
        with when("the Person lists no-such-ticket's story_map files"):
            # Person -> Ticket.load('no-such-ticket') <- TicketNotFoundError
            pass
        with then("a toast says cdd ticket.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board"):
            pass
        with but_("no panel opens"):
            pass
