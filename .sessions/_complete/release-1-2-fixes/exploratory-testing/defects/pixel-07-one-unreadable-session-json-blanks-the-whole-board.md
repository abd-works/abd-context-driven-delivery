# One ticket's session.json that is not readable JSON blanks the whole board: no card, "0 tickets · active: none"

- **Charter:** Round 2 - explore the Kanban board's pages and the Files app's graph view in a real browser as a person whose tickets and files change under the page
- **Tester:** Pixel
- **Story:** Move Work Forward On Session Board > See Work On Session Board > Display Board. No scenario covers a session file that does not parse.
- **Module and class:** `space/kanban/board.py` `Board.show` (the cdd tool `board.show`), which raises `JsonFileUnreadable` for the first session file it cannot read; the page's `board-page.ts` then draws an empty board under the failure.
- **Severity:** blocks work (every other ticket, the backlog and the active session disappear from the board until the one file is repaired by hand; a file half-written by a crash, a merge conflict marker or a hand edit is enough)

## Steps

Sandbox: `C:\dev\_et\pixel\work\repo` with six tickets; board server on 8905 over a cdd server on 8901 (`C:\dev\_et\pixel\work\scripts\stack.py`); script `C:\dev\_et\pixel\work\scripts\b6.py`.

1. Open `http://127.0.0.1:8905/`, turn **Active session only** off: six cards.
2. Cut `.sessions/checkout-payment-retry-flow-one/session.json` in half (or replace it with `[1, 2]`).
3. Reload the page.

## Expected

The board keeps its other cards and says which ticket's session file is unreadable, on that card or in a notice, as the Files app keeps its list when one file does not open.

## Actual

The header reads `· 0 tickets · active: none`, no column holds a card, and every poll answers 502:

```
cdd board.show failed: JsonFileUnreadable: C:\dev\_et\pixel\work\repo\.sessions\checkout-payment-retry-flow-one\session.json is not a readable JSON object (Unterminated string starting at: line 5 column 3 (char 117))
```

The notice does name the file, which is good; the loss of every other card is the defect. With `[1, 2]` the same, "(expected an object, found list)". Screenshot: `C:\dev\_et\pixel\work\shots\b6-broken-session-json.png`.

## Tier that should catch it

unit (a spec of `Board.show` with one unreadable session file among readable ones), and one browser story test that the other cards stay. No spec seeds a session file that does not parse.

## Also seen by

## Confirmation (Rivet, round 2)
- Result: confirmed for the cdd tool; the board's page not run
- What I ran and saw: my own `sboard.py`: a real cdd server (`SpecServer`, port 8916) over a fresh repository with three tickets, `board.show` called as a chat. With three readable session files the answer names all three. With the first cut in half, and with `[1, 2]`, the whole call fails: `JsonFileUnreadable: ...\checkout-payment-retry-flow-one\session.json is not a readable JSON object (Expecting value: ...)` and `(expected an object, found list)`; no other ticket is answered. Repaired, all three come back.
- Which part I ran: step 2 and the tool the page asks. Not run: the page on a board server (steps 1 and 3), since the report gives no way to start one but the reporter's own script; the page's "0 tickets, active: none" and its 502 are therefore not seen by me.
- Cause, if you found it: `space/kanban/board.py` `Board.show`, as the report says: one session file's `JsonFileUnreadable` fails the whole answer.
- Shares its cause with: none. It is the opposite handling of the same event as sparky-03 and rivet-06, where an unreadable file is read as empty without a word; here it is said, and everything else is dropped.
