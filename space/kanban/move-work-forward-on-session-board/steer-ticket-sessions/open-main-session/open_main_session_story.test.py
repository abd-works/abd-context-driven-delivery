from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----open-main-session
# Model: ../../../.context/kanban-model.md

# Story: Open Main Session
# Actor: Person
with story("Open Main Session"):
    with scenario("Open main from a ticket on its own branch"):
        # Evidence: requested 2026-11-09: main is the default session; it is in the session list and opens in the repository's own folder.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), on its own branch pushed to origin"):
            pass
        with when("the Person opens main, committing checkout-flow"):
            # Person -> Board.open_main(leaving=['commit'])
            # Board -> Ticket.leave_for_another(['commit'])
            # Board -> Branch(main).check_out()
            # Board -> Sessions.switch('main')
            pass
        with then("no ticket is active"):
            pass
        with and_("the checkout is on main"):
            pass
        with and_("the checkout-flow branch is still there"):
            pass
    with scenario("Open main, deleting the ticket's branch"):
        # Evidence: requested 2026-11-09: deleting a session's branch closes the session.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), on its own branch pushed to origin"):
            pass
        with when("the Person opens main, deleting checkout-flow's branch"):
            # Person -> Board.open_main(leaving=['delete_branch'])
            # Board -> Ticket.leave_for_another(['delete_branch'])
            # Ticket -> Ticket.close(['delete_branch'])
            pass
        with then("no ticket is active"):
            pass
        with and_("the checkout-flow branch is gone"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
    with scenario("Open main from a ticket in its own worktree"):
        # Evidence: requested 2026-11-09: main goes to the repository's own folder.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its branch open in its own worktree"):
            pass
        with when("the Person opens main with nothing chosen"):
            # Person -> Board.open_main(leaving=[])
            pass
        with then("no ticket is active"):
            pass
        with and_("checkout-flow's worktree is still there"):
            pass
        with but_("checkout-flow is not closed"):
            pass
