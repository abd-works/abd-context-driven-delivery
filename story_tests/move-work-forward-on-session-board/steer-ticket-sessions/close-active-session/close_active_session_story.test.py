from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----close-active-session
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Close Active Session
# Actor: Person
with story("Close Active Session"):
    with scenario("Close the active session from its card"):
        # Evidence: observed: ticket-client.spec 'Close Active Session' — 'should send the close session command to the chat', 'should leave the ticket in its column'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), In progress in Discovery, with a chat connected"):
            pass
        with when("the Person closes checkout-flow's session from its card"):
            # Person -> Chat.command('/space:session:close-session')
            # Chat -> Session.close()
            pass
        with then("the chat is sent /space:session:close-session"):
            pass
        with and_("checkout-flow stays In progress in Discovery"):
            pass
    with scenario("Complete the active ticket with its work committed"):
        # Evidence: observed: activation-client.spec 'Close Active Session' — 'should ask what to do with its work', 'should send what to do with its work', 'should select the ticket in Complete'; ticket-client.tsx dropOn opens the Close dialog for the active ticket; kanban_tools_spec 'should leave no ticket active'.
        with given("checkout-flow is open in its own worktree"):
            pass
        with when("the Person moves checkout-flow into Complete"):
            # Person -> Ticket.close_choices()
            pass
        with then("a dialog headed Close session Checkout flow offers commit and push, none chosen"):
            pass
        with when("the Person confirms"):
            # Person -> Ticket.close(['commit', 'push'])
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # Ticket -> Session.close()
            # Ticket -> SessionFolder.move_to_closed()
            # Board page -> Board.show()
            pass
        with then("checkout-flow shows in Complete and is selected"):
            pass
        with and_("a toast says Checkout flow: committed, pushed · Session Checkout flow closed"):
            pass
        with and_("main is the active ticket"):
            pass
    with scenario("Commit the closed session's folder and return to main"):
        # Evidence: observed: e2e-report B4 — the close commit was made before the session folder moved to .sessions/_complete/, so the move stayed uncommitted, and the closed ticket's branch stayed checked out.
        with given("checkout-flow is open in its own worktree"):
            pass
        with when("the Person closes checkout-flow, committing and pushing"):
            # Person -> Ticket.close(['commit', 'push'])
            # Ticket -> Session.close()
            # Ticket -> SessionFolder.move_to_closed()
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # Ticket -> Branch(main).check_out()
            pass
        with then("nothing is left uncommitted"):
            pass
        with and_("the checkout is back on main"):
            pass
    with scenario("Return to main whatever is chosen"):
        # Evidence: requested 2026-11-09: closing a session goes to main, the default session in the repository's own folder.
        with given("checkout-flow is open in its own worktree"):
            pass
        with when("the Person closes checkout-flow with nothing chosen"):
            # Person -> Ticket.close([])
            # Ticket -> TicketCheckout.return_to_default_branch()
            pass
        with then("the checkout is back on main"):
            pass
        with and_("main is the active ticket"):
            pass
    with scenario("Offer to commit a branch open in its worktree"):
        # Evidence: observed: e2e-report B3 — the close dialog said "branch none yet" for a ticket whose branch exists in a worktree, and labelled the choices with the ticket title.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its branch open in its own worktree"):
            pass
        with when("the Person closes checkout-flow"):
            # Person -> Ticket.close_choices() <- branch: checkout-flow, choices: handoff, commit, push
            pass
        with then("the close dialog offers a handoff, and to commit and push checkout-flow"):
            pass
    with scenario("Close a session whose work is on main"):
        # Evidence: observed: chat-ui-defects backlog item — closing a session on main should commit and push main, as switching a branch does, and not try to delete a worktree; main has no worktree to delete.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its work on main"):
            pass
        with when("the Person closes checkout-flow"):
            # Person -> Ticket.leave_choices()
            # Ticket <- Branch main, is_checked_out: true
            pass
        with then("the close dialog offers to commit and push main"):
            pass
        with when("the Person confirms"):
            # Person -> Ticket.close(['commit', 'push'])
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # Ticket -> Session.close()
            # Ticket -> SessionFolder.move_to_closed()
            pass
        with then("main on origin holds the commit checkout-flow: leave session"):
            pass
        with and_("the checkout is still on main"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
    with scenario("Write a handoff for the session being closed"):
        # Evidence: observed: chat-ui-defects backlog item — the close and switch dialogs need a Create handoff checkbox, on by default; when it is on, closing or switching writes a handoff for the session being left.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its story map held on violations"):
            pass
        with when("the Person closes checkout-flow with Create handoff chosen"):
            # Person -> Ticket.close(['handoff'])
            # Ticket -> Handoffs.write(LeavingHandoff(ticket).document)
            # Ticket -> Session.close()
            # Ticket -> SessionFolder.move_to_closed()
            pass
        with then("checkout-flow's folder in .sessions/_complete holds a handoff"):
            pass
        with and_("the handoff names stories-story-map as what comes next"):
            pass
    with scenario("Complete a ticket that has no branch of its own"):
        # Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'should commit nothing on a ticket that has no branch'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with but_("it has no branch of its own"):
            pass
        with when("the Person moves checkout-flow into Complete and confirms"):
            # Person -> Ticket.close([])
            # Ticket -> Session.close()
            # Ticket -> SessionFolder.move_to_closed()
            pass
        with then("checkout-flow shows in Complete"):
            pass
        with and_("its folder is in .sessions/_complete/checkout-flow"):
            pass
        with but_("checkout-flow's work is not committed"):
            pass
    with scenario("Leave what the repository's own folder holds uncommitted out of the close"):
        # Evidence: tested by heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with its branch merged while the clone's own folder holds an edit nobody committed'.
        with given("checkout-flow is open in its own worktree, with work in it"):
            pass
        with and_("the repository's own folder holds an edit to README.md that nobody committed"):
            pass
        with when("the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree"):
            # Person -> Ticket.close(['commit', 'push', 'merge', 'delete_branch', 'delete_worktree'])
            # Ticket -> TicketCheckout.save_work(leaving)
            # Ticket -> TicketCheckout.leave_branch(leaving)
            pass
        with then("main on origin holds checkout-flow's work"):
            pass
        with but_("main on origin does not hold the edit to README.md"):
            pass
        with and_("that edit is still uncommitted in the repository's own folder"):
            pass
    with scenario("Keep the ticket open when its branch does not merge into main"):
        # Evidence: tested by heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with its branch merged into a main it conflicts with'.
        with given("checkout-flow is open in its own worktree"):
            pass
        with and_("its branch and main on origin each changed the same line"):
            pass
        with when("the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree"):
            # Person -> Ticket.close(['commit', 'push', 'merge', 'delete_branch', 'delete_worktree'])
            # Ticket -> TicketCheckout.save_work(leaving)
            # Ticket -> TicketCheckout.leave_branch(leaving)
            pass
        with then("the board says checkout-flow does not merge into main"):
            pass
        with and_("main has no merge half done"):
            pass
        with and_("checkout-flow still has its worktree"):
            pass
        with and_("checkout-flow stays In progress in Discovery"):
            pass
    with scenario("Refuse to call a ticket closed while a program holds its worktree open"):
        # Evidence: tested by heavy, Windows: space/repo/worktree_heavy_spec.py 'whose folder a running program holds open'.
        with given("checkout-flow is open in its own worktree"):
            pass
        with and_("a running program works in that worktree's folder"):
            pass
        with when("the Person closes checkout-flow, deleting its worktree"):
            # Person -> Ticket.close(['delete_worktree'])
            # TicketCheckout -> Worktrees.remove(worktree) <- WorktreeNotRemovedError
            pass
        with then("the board says the worktree could not be removed, naming its folder"):
            pass
        with and_("checkout-flow's work is committed on its branch on origin"):
            pass
        with when("that program has ended and the Person activates checkout-flow"):
            # Person -> Ticket.activate()
            # Worktrees -> Worktrees.add(folder, branch)
            pass
        with then("checkout-flow has its own worktree again"):
            pass
