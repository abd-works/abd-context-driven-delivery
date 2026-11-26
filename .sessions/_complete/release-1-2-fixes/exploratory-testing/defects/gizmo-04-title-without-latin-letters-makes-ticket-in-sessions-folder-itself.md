# A title with no Latin letter or digit (empty, spaces, 日本語) makes a ticket named ".sessions" whose session files are written into .sessions itself

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Open Ticket Session - "Open a new ticket"; Maintain Tickets "Keep Add off with no title" promises the page keeps Add off, but the tool takes it.
- **Module and class:** `space/kanban/ticket.py` `Ticket.create` -> `CardPlacement.open_ticket`; the name comes from the title's slug (`harness/annotations/name.py` `Name`), which is empty here, so the session folder is `.sessions/` + "".
- **Severity:** wrong result

## Steps
1. `ticket.create title=""`  2. `ticket.create title="   "`  3. `ticket.create title="日本語"`
4. `ls .sessions`; `cat .sessions/session.json`; `board.show`; `ticket.activate ticket=".sessions"`

## Expected
An empty title is refused; a title in another script gets a name of its own (or is refused saying why).

## Actual
All three calls answer a ticket `{"name": ".sessions", "session_file": ".sessions/session.json", "branch": ".sessions"}`. `.sessions/session.json`, `.sessions/session.log` and `.sessions/progress-cache.json` are written beside the session folders, and each call overwrites the last one's title (file ends as `{"name": ".sessions", "scope": "feature", "title": "\u65e5\u672c\u8a9e"}`). The board does not show the ticket, and `ticket.activate ticket=".sessions"` answers `TicketNotFoundError: no ticket named '.sessions' on the board`, so the work a person titled in Japanese is nowhere. `.sessions/session.json` is then committed on main by the next save. Also: accented letters are dropped rather than folded: "Refunds / returns: café ünïcode ✓" became `refunds-returns-caf-n-code`.

## Tier that should catch it
Unit (`space/kanban/kanban_tools_spec.py`, MockGit): it is name handling. No spec creates a ticket with an empty or non-Latin title through the tool.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). `""`, `"   "` and `"日本語"` each answer a ticket named `.sessions` with `session_file` `.sessions/session.json`; the file ends with title `\u65e5\u672c\u8a9e`; the board does not hold it; `ticket.activate ticket=".sessions"` answers `TicketNotFoundError`. The accented title became `refunds-returns-caf-n-code`. I saw `session.json` and `session.log` in `.sessions`; `progress-cache.json` was not there.
- Cause, if you found it: `space/kanban/ticket.py` `Ticket.create` and `space/kanban/board.py` `CardPlacement.open_ticket` pass the title to `board.sessions.create` with no check of the name its slug gives.
- Shares its cause with: gizmo-05, gizmo-06 (the name made from the title is never checked: empty, already taken, or too long)
- Pixel, round 2, on the board's page: the ticket titled 日本語 (name `.sessions`, files in `.sessions/session.json`) has no card in any column, with Active session only off; the header's ticket count does not include it.
