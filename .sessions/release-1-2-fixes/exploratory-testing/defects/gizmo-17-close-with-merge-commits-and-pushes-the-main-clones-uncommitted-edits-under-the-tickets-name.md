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

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz2.py`). As reported: with the ticket's line and the person's line both appended to `src/order.py`, the close fails on the merge conflict, and main and origin/main hold a commit `dirty-nine: leave session` whose only change is the person's line (`src/order.py | 1 +`). The case the report did not run, a close with merge that succeeds cleanly (the ticket adds only `src/nine.py`; the main clone has the uncommitted line in `src/order.py`): `ticket.close leaving=[commit, push, merge, delete_branch, delete_worktree]` answers the closed ticket with no word about the main clone. Main's log reads `dirty-nine: leave session` (the ticket's commit), `dirty-nine: leave session` (a second commit, holding only the person's line), `merge dirty-nine into main`, `sessions: close dirty-nine`. `git show origin/main:src/order.py` holds the person's line and the main clone's status is clean. So the uncommitted edit is committed and pushed, under the ticket's name, on a close that reports success.
- Cause, if you found it: `space/kanban/ticket_checkout.py` `TicketCheckout.save_work`: by the time it runs, `Ticket.close` has freed the ticket's worktree, so `_checked_out_work_branch` answers the branch the main clone has checked out, and `_commit_and_push` commits and pushes whatever is uncommitted there.
- Shares its cause with: gizmo-14 (the same order in `Ticket.close`)

## Status: fixed (2026-11-23)
- Fixed before this pass (`5e8029f31`): `Ticket.close` saves and merges the ticket's work while its worktree is still there, so the commit is made in the worktree, never from the main clone. An uncommitted edit in the main clone to a file the ticket did not change stays uncommitted and off origin (`ticket_work_heavy_spec.py`, "that a ticket is closed with its branch merged while the clone's own folder holds an edit nobody committed").
- Fixed now, the case the report ran (the ticket and the person both changed one file): the close is refused before anything changes (`TicketCheckout.refuse_edits_merge_would_overwrite`, `EditsInTheWayOfMergeError`): "dirty-nine is not closed: the repository's own folder holds uncommitted changes to src/order.py, which merging dirty-nine into main would run over; commit them or set them aside in <folder>, then close dirty-nine again". Nothing is committed on main or on the ticket's branch, the person's edit stays uncommitted, and the ticket keeps its worktree and stays open. Refusing was chosen over committing around it because the merge cannot run over the edit without either publishing it or losing it.
- Covered by: `space/kanban/ticket_work_heavy_spec.py`, "that a ticket is closed with its branch merged while the clone's own folder holds an uncommitted edit to a file the ticket changed" (real git in temporary folders, a real worktree and a dirty main clone): refuses naming the file, the edit stays uncommitted, nothing is committed on main, the edit stays off origin's main, nothing of the ticket's work is committed, its worktree is kept, it stays open.
