# ticket.create with a title that slugs to an existing ticket's name silently retitles that ticket, main included, instead of refusing

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Open Ticket Session - "Open a new ticket"; no scenario covers a title already taken.
- **Module and class:** `space/kanban/ticket.py` `Ticket.create` -> `CardPlacement.open_ticket` (`space/kanban/board.py`), and the session it opens (`space/session/sessions.py`).
- **Severity:** wrong result

## Steps
1. `ticket.create title="Gift wrap"`, `ticket.activate ticket="gift-wrap"`.
2. `ticket.create title="GIFT WRAP"` (a different piece of work, in the person's mind).
3. `ticket.create title="main"`.
4. `cat .sessions/gift-wrap/session.json .sessions/main/session.json`

## Expected
A second ticket, or a refusal that says a ticket named gift-wrap already exists. Main is never a ticket someone can create.

## Actual
Both calls answer success with the existing ticket: `{"title": "GIFT WRAP", "name": "gift-wrap", "last_activity": <the first ticket's>}`. The first ticket's title is overwritten ("Gift wrap" -> "GIFT WRAP"), and the caller is not told no ticket was made. `title="main"` answers `{"name": "main", "is_main": true}` and writes `.sessions/main/session.json` as `{"name": "main", "title": "main", "scope": "feature"}`, giving the main session a title and the scope of a feature. Titles differing only by case, or by punctuation, cannot be two tickets.

## Tier that should catch it
Unit (`kanban_tools_spec.py`): no git needed. The specs never create the same title twice.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). `ticket.create title="GIFT WRAP"` answers the existing `gift-wrap` with title `GIFT WRAP`; `title="main"` answers `is_main: true` and writes `.sessions/main/session.json` as `name main, title main, scope feature`. Also seen: the ticket's worktree copy of its `session.json` still says `Gift wrap`, so the two copies now disagree.
- Cause, if you found it: `CardPlacement.open_ticket` -> `Sessions.create` (`space/session/sessions.py`) opens the session of that name whether or not it exists, and writes the new title over it.
- Shares its cause with: gizmo-04, gizmo-06
