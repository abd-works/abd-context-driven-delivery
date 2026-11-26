# backlog-item.create with a title already in the Backlog overwrites the first idea's text; an empty or non-Latin title writes `_backlog/.md`

- **Charter:** Round 1 second charter - backlog items, handoffs and closing a ticket when git disagrees, as two chats on two cdd servers sharing one repository
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Maintain Tickets / Add Backlog Item - "Add an idea to the Backlog", "Keep Add off with no title". space/kanban module-context, Constraint: "Never delete a backlog item's file: it is the only copy of the idea".
- **Module and class:** `space/kanban/backlog_item.py` `BacklogItem.create` (writes `_backlog/<slug>.md` without asking whether it is there); `BacklogItem.start` for the second half.
- **Severity:** wrong result (an idea is lost)

## Steps
1. `backlog-item.create title="Gift cards" text="Sell gift cards."`
2. `backlog-item.create title="Gift cards" text="A second idea with the same title."`
3. `cat .sessions/_backlog/gift-cards.md`
4. `backlog-item.create title=""`, then `backlog-item.create title="日本語" text="idea"`; `ls -a .sessions/_backlog`
5. With a ticket stock-intake open: `backlog-item.create title="Stock intake" text="Same name as an open ticket."`, `backlog-item.start backlog_item="Stock intake"`.
6. `backlog-item.start backlog_item="日本語"`

## Expected
The second create is refused, or kept as a second item; the first idea's text stays. An empty title is refused. Starting an item whose name an open ticket has says so.

## Actual
- Step 2 answers success; the file holds only "A second idea with the same title." - "Sell gift cards." is gone, with no copy (it was not yet committed).
- Step 4: both write the one file `.sessions/_backlog/.md`; the empty one answers `"title": ".md"`, the second replaces it.
- Step 5: start answers the existing ticket stock-intake (its child scan-barcodes still under it) with the item's text as its text; the idea file is moved into that ticket's folder as `stock-intake.md`, where it would replace a text file the ticket already had (not tried with one present). The caller is not told no new ticket was made.
- Step 6: answers a ticket named `.sessions` with `"text": ""` (gizmo-04's ticket), and the item's file is moved to `.sessions/.sessions.md`, off the board.

## Tier that should catch it
Unit (`space/kanban/kanban_tools_spec.py`): file naming only. The specs create each title once.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz2.py`). The second `backlog-item.create title="Gift cards"` answers success and `gift-cards.md` holds only `A second idea with the same title.` An empty title and `日本語` both write `_backlog/.md`, the first answering `"title": ".md"`. Starting `Stock intake` answers the open ticket stock-intake with the item's text and moves the file to `.sessions/stock-intake/stock-intake.md`. Starting `日本語` answers a ticket named `.sessions`; here the idea file ended as `.sessions/.md`, where the report says `.sessions/.sessions.md`.
- Cause, if you found it: `space/kanban/backlog_item.py` `BacklogItem.create` writes `_backlog/{Name(title).title_slug}.md` without checking that the slug is not empty or that the file is not there; `BacklogItem.start` opens the session of that name whether or not a ticket has it.
- Shares its cause with: gizmo-04, gizmo-05 (a name made from a title is never checked: empty, or already taken)
- Pixel, round 2, on the board's page: after a second `backlog-item.create` titled Idea one the Backlog shows one Idea one card holding the second text; the first text is gone.
