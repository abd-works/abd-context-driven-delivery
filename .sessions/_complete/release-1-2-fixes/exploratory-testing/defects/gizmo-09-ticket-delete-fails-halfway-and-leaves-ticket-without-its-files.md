# ticket.delete can fail halfway with "WinError 5 Access is denied": the session's files are gone, its folder and card stay, and its title is lost

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Maintain Tickets / Delete Ticket - "Delete a ticket and its session folder".
- **Module and class:** `space/kanban/ticket.py` `Ticket.delete` (`self.session.close()` then the folder's removal with `shutil.rmtree`, per the traceback in `.sessions/main/session.err`); `space/session/session_folder.py`.
- **Severity:** wrong result

## Steps
1. `ticket.create title="Stock intake"` (first ticket of the repository), two more tickets, `ticket.add_child ticket="stock-intake" title="Scan barcodes"`.
2. Other tickets are activated, closed, moved; stock-intake itself is never activated. `ticket.move_next ticket="stock-intake"` (refused, parent), `ticket.reassign_parent ticket="stock-intake" parent="scan-barcodes"` (refused, loop).
3. `ticket.delete ticket="stock-intake"`; again a second time.

## Expected
The ticket and its session folder are removed, or nothing is and the call says why.

## Actual
Both calls: `PermissionError: [WinError 5] Access is denied: 'C:\dev\_et\gizmo\work\repo\.sessions\stock-intake'`. After the first, `session.json` and `session.log` are deleted (`git status`: ` D .sessions/stock-intake/session.json`, ` D .sessions/stock-intake/session.log`) while the empty folder stays, so the board still shows `stock-intake(scan-barcodes)`. A later `ticket.activate ticket="stock-intake"` succeeds and writes a new session.json whose title is "stock-intake": the title "Stock intake" and the session log are lost.

Not isolated: a second parent with a child (parent-two / kid-two) and two childless tickets deleted cleanly in the same server, so something held the stock-intake folder open in the server process (the empty folder could not be removed by `os.rmdir`). Whatever holds it, the delete is not all-or-nothing.

Also noticed on the clean delete: `ticket.delete` of a parent leaves its child with `"parent": "parent-two"` naming a ticket that no longer exists; the board then shows the child as a card of its own. No scenario says what happens to children.

## Tier that should catch it
Heavy on Windows (a folder held open cannot be removed there); the story's server tier deletes a ticket nothing else has touched.

## Also seen by
- Gizmo, second charter - cause confirmed and now repeatable: hold the ticket's session folder open with any process (`cd .sessions/escape && python -c "import time; time.sleep(30)" &`), then `ticket.delete ticket="escape"`. Answer: `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: '...\.sessions\escape'`. `session.json` and `session.log` are deleted (` D` in git status), the empty folder stays, and the card is still on the board. So a folder open in an editor, a shell or the Files app is enough.

## Confirmation (Sparky, round 2)
- Result: steps incomplete
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). I ran what the steps name: three tickets, `add_child`, another ticket activated and moved, the refused `move_next` and `reassign_parent`, then `ticket.delete ticket="stock-intake"`. The delete answered with no error and removed the folder; the second delete answered `TicketNotFoundError`. Step 2's "other tickets are activated, closed, moved" does not say which calls, and the report itself says something in the server process held the folder open without saying what. The side note is confirmed: the child `scan-barcodes` keeps `"parent": "stock-intake"` after its parent is deleted.
- Cause, if you found it: Not found for the `WinError 5`. What is missing from the report: the calls that leave the `stock-intake` folder held open in the server.
- Shares its cause with: none
