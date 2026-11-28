# widget-03 ticket.move_before answers CardNotInColumnError after it has already moved the ticket into another stage

**Title** - When either ticket is a stacked child, `ticket.move_before` across columns first moves the ticket into the other's stage (saved, committed and pushed), then refuses the ordering with `CardNotInColumnError`, so the caller is told the drop failed while the ticket has changed stage.

**Charter** - theme 3, starting work from the Backlog and the board at once (drops in any column). **Tester** - Widget.

**Story** - Move work forward on session board / Maintain tickets, the drop-above-a-card-in-any-column scenarios added in 020e7a512 (`maintain_tickets_story.test.md`). No scenario covers a stacked child as either card; the board page stops it (`TicketDrops.canDropAbove` refuses stacked cards), but an agent calling the tool, as the tool's own description invites, is not stopped.

**Module and class** - `space/kanban/ticket.py` `TicketMoveTools.move_before`: `beside = self.moves.move_beside(other)` places the ticket (`TicketMoves.move_beside` refuses only a parent), then `Card.move_before(beside, other)` -> `Column.place_before` raises `CardNotInColumnError` in `space/kanban/board.py`. Nothing checks both are cards of their own before the move.

**Severity** - wrong result (a move is made and kept while the answer is a failure).

**Steps** (sandbox `C:\dev\_et\after-1-2-1\widget`, cdd server 8931, MCP with `X-CDD-Project` = `work\repo`)
1. Backlog parent Checkout flow with children Address form, Card form, Gift wrap; `backlog-item.start {"backlog_item":"Checkout flow"}`. Ticket `admin-report` in Implementation, `order-history` in Discovery.
2. `ticket.move_before {"ticket":"card-form","other":"admin-report"}`.
3. `ticket.move_before {"ticket":"order-history","other":"card-form"}` (card-form is now a stacked child in Implementation).
4. `board.show`; read `.sessions/card-form/session.json`.

**Expected** - Either the move is refused before anything changes (as `ParentMovesWithChildrenError` is refused first), or it moves and answers success. The tool says "Where other is in another column ... ticket goes there first ... The column keeps that order"; the Constraint in `space/kanban/.context/module-context.md` keeps every move in session.json, so a refused call should leave none.

**Actual** - Step 2 answers `CardNotInColumnError: 'card-form' is not a card of its own in Implementation`, yet `card-form/session.json` holds `"stage": "Implementation"`, committed on main as `sessions: card-form stage Implementation ...`. Step 3 answers the same error, yet the board now shows `Implementation: admin-report | order-history` - order-history left Discovery.

**Tier that should catch it** - unit (kanban spec over `Ticket.move_before` with a stacked ticket on either side); `ticket-client.spec.ts` tests the page's guard, and the Python examples only drop cards of their own.
