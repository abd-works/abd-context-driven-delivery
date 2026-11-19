# Closing a ticket that has its own worktree commits the person's uncommitted edits in the main clone onto main, and pushes them, as "<ticket>: leave session"

- **Charter:** Round 1 second charter - backlog items, handoffs and closing a ticket when git disagrees, as two chats on two cdd servers sharing one repository
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Close Active Session - "Complete the active ticket with its work committed", "Offer to commit a branch open in its worktree". The commit offered is of the ticket's work; space/kanban module-context: "the repository's own folder stays on main ... its worktree's branch carries only the work".
- **Module and class:** `space/kanban/ticket_checkout.py` `TicketCheckout.save_work`: `free_worktree` has already removed the ticket's worktree, so `_checked_out_work_branch` is then the main clone's branch (main), and `_commit_and_push(branch, leaving)` commits and pushes whatever is uncommitted there.
- **Severity:** wrong result (work nobody chose to commit is published on origin's main)

## Steps
1. `ticket.create title="Dirty nine"`, `ticket.activate ticket="dirty-nine"`; in `..\repo-dirty-nine` append a line to `src/order.py` and add `src/nine.py`.
2. In the main clone `repo`, on main, append `# person editing on main, not committed` to `src/order.py`. Do not commit.
3. `ticket.close ticket="dirty-nine" leaving=["commit","push","merge","delete_branch","delete_worktree"]`
4. `git log -3 -- src/order.py`; `git show --stat 50fee38`; `git branch -a --contains 50fee38`

## Expected
The ticket's work is committed on its branch and merged. The person's uncommitted edit in the main clone stays uncommitted, or the close refuses because the main clone has changes of its own.

## Actual
```
50fee38 dirty-nine: leave session | parents e9b6faa
 src/order.py | 1 +
```
on `main` and `remotes/origin/main`: a commit on main holding only the person's line, named for the ticket, already pushed. The ticket's own commit is a different one (`3ff7703 dirty-nine: leave session` on `dirty-nine`). In this run the merge then conflicted with that line and the close failed as in gizmo-14 (worktree gone, ticket still open), so a failed close published the person's edit. Without the conflict the same commit is made and the close succeeds, so nobody is told.

## Tier that should catch it
Heavy (`ticket_work_heavy_spec.py`): real worktree plus a dirty main clone. Every close example there starts from a clean main clone.

## Also seen by
