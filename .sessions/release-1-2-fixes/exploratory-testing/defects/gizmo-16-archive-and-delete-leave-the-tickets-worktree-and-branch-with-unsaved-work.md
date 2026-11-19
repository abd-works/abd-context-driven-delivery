# ticket.delete and ticket.archive take the card and session folder away but leave the ticket's worktree and branch, with its unsaved work, where no card reaches them

- **Charter:** Round 1 second charter - backlog items, handoffs and closing a ticket when git disagrees, as two chats on two cdd servers sharing one repository
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Maintain Tickets / Delete Ticket - "Delete a ticket and its session folder"; Archive Ticket - "Archive a ticket off the board". Neither scenario has a ticket with a worktree.
- **Module and class:** `space/kanban/ticket.py` `Ticket.delete` and `Ticket.archive` (both call `self.session.close()` and move or remove the folder; neither asks `self.checkout` about a worktree, as `Ticket.close` does).
- **Severity:** wrong result (board, session and git disagree; no work is destroyed)

## Steps
1. `ticket.create title="Offline two"`, `ticket.activate ticket="offline-two"`; in `..\repo-offline-two` commit nothing, add `src/unsaved2.py` (it also held one local commit never pushed).
2. `ticket.delete ticket="offline-two"`
3. Same with conflict-one (worktree `..\repo-conflict-one`, new file `src/unsaved.py`): `ticket.archive ticket="conflict-one"`, then `ticket.activate ticket="conflict-one"`.
4. `git worktree list`, `git branch`, `board.show`.

## Expected
Delete and archive either refuse while the ticket has a worktree with work in it, or offer what close offers (commit, push, delete_worktree), so nothing is left that the board cannot show.

## Actual
Both answer success. The cards are gone (`.sessions/offline-two` removed, `.sessions/_archive/conflict-one` made), and git still has
```
C:/dev/_et/gizmo/work/repo-conflict-one  465ef0e [conflict-one]
C:/dev/_et/gizmo/work/repo-offline-two   367963d [offline-two]
```
with `unsaved.py` and `unsaved2.py` uncommitted in them, and offline-two's commit 367963d on no remote. `ticket.activate ticket="conflict-one"` answers `TicketNotFoundError: no ticket named 'conflict-one' on the board`, so the archived ticket's worktree cannot be opened, closed or removed through the product. A chat started in either folder would work on a branch no ticket owns. The folders also stand in the way of any later ticket of the same name.

## Tier that should catch it
Heavy (`ticket_work_heavy_spec.py`): real worktrees. The delete and archive examples use tickets never activated.

## Also seen by
