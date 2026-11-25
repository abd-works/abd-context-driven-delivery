# A long ticket title fails with a raw "WinError 206 The filename or extension is too long" instead of a refusal that says the title is too long

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Open Ticket Session - "Open a new ticket"; no scenario covers a long title.
- **Module and class:** `space/kanban/ticket.py` `Ticket.create`; the session folder is named with the whole slug of the title, with no length limit (`space/session/session_folder.py`).
- **Severity:** misleading message

## Steps
`ticket.create title="A very long title that goes on and on and on about the bookshop and its many many needs for stock and orders and customers and refunds and loyalty and everything else under the sun until the path limit is surely near"` (215 characters) on Windows.

## Expected
The ticket is made under a shortened name with the full title kept in session.json, or the call refuses in the product's words.

## Actual
`FileNotFoundError: [WinError 206] The filename or extension is too long: 'C:\dev\_et\gizmo\work\repo\.sessions\a-very-long-title-that-goes-on-...'`. Nothing is left behind. Shorter long titles pass create but then name a branch and a session folder of the same length, which the path limit can meet later, inside a worktree.

## Tier that should catch it
Unit for a name limit once one is decided; heavy on Windows for the real path limit.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). The 215-character title fails with a raw `FileNotFoundError`, but here it is `[WinError 3] The system cannot find the path specified`, not `WinError 206`, for the same `.sessions\a-very-long-title-...` folder. Nothing was left behind.
- Cause, if you found it: `Ticket.create` -> `Sessions.create`: the session folder takes the whole slug of the title, with no limit on its length.
- Shares its cause with: gizmo-04, gizmo-05
- Pixel, round 2, on the board's page: a backlog title of 5,000 letters typed into the Backlog's + field answers 502 and the notice `cdd backlog-item.create failed: FileNotFoundError: [Errno 2] No such file or directory: '...\.sessions\_backlog	ttt...'`, the same raw failure for a backlog item; the notice then stays on the page beside the next item's "added to Backlog".
