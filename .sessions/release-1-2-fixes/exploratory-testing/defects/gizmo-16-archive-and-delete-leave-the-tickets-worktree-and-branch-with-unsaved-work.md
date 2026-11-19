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

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz2.py`). `ticket.delete ticket="offline-two"` answers null and `ticket.archive ticket="conflict-one"` answers the ticket in `_archive`. Git still lists both worktrees and both branches; `unsaved2.py` and `unsaved.py` are uncommitted in them, and offline-two's local commit is on no remote. `ticket.activate ticket="conflict-one"` answers `TicketNotFoundError`. Also seen: the deleted ticket's worktree shows its own `session.json` and `session.log` as deleted.
- Cause, if you found it: `space/kanban/ticket.py` `Ticket.delete` and `Ticket.archive` close the session and move or remove its folder without asking the ticket's checkout whether it has a worktree, as `Ticket.close` does.
- Shares its cause with: none (gizmo-09's side note, a child left naming a deleted parent, is the same kind of leftover from `Ticket.delete`)
- Pixel, round 2, on the board's page: after `POST /api/ticket/alpha/archive` the Alpha card is gone from every column, while `git worktree list` still lists `repo-alpha [alpha]` and the branch `alpha` stays; nothing on the page leads to them.
