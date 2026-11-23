# Question: activating a closed ticket opens its worktree but leaves it in Complete, its folder still in .sessions/_complete

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Move Ticket - "Reopen a ticket moved back out of Complete" says a reopened ticket's folder is back in `.sessions/<name>`; no scenario covers activate on a closed ticket.
- **Module and class:** `space/kanban/ticket.py` `Ticket.activate`; `space/kanban/ticket_checkout.py` `TicketCheckout.open`.
- **Severity:** question

## Steps
1. `ticket.create title="Loyalty points"`, `ticket.activate ticket="loyalty-points"`.
2. `ticket.close ticket="loyalty-points" leaving=["delete_worktree"]` - folder moves to `.sessions/_complete/loyalty-points`, worktree removed.
3. `ticket.activate ticket="loyalty-points"`.
4. `board.show`, `git worktree list`.

## Expected
Either activate refuses a closed ticket, or it reopens it (folder back in `.sessions/loyalty-points`, card back on a stage), as moving it back out of Complete does.

## Actual
Activate succeeds, makes `..\repo-loyalty-points` on branch `loyalty-points` again, and answers `session_file: .sessions/_complete/loyalty-points/session.json`. The board still shows the card in Complete while its worktree is open; a chat in that worktree gets a session kept under `_complete`.

Second run, ticket kid-two closed with `leaving=["commit","push","merge","delete_branch","delete_worktree"]` then activated: branch `kid-two` and `..epo-kid-two` are made again, and `sessions.current` from a chat in that worktree answers `{"name": "main", "branch": "main", "repo_name": "repo-kid-two"}`: the chat in the ticket's worktree is told it is on main, though git has `kid-two` checked out there (the scenario "Switching a chat in a ticket's worktree always opens that ticket's session" promises the ticket's session).

## Tier that should catch it
Heavy, once the intended behaviour is decided; today no spec activates a ticket after closing it.

## Also seen by
