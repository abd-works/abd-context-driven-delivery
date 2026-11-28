# widget-05 An idea started under a closed ticket is opened, and then shows twice: as its own card in Discovery and as a child inside the closed card in Complete

**Title** - `backlog-item.start_under` accepts a closed ticket as parent; the new open child is a card of its own in Discovery (`is_stacked: false`), while the closed parent in Complete still sends it in its `children`, so the board answer holds the same ticket in two columns.

**Charter** - theme 3, starting work from the Backlog and the board at once (drops on a card in any column, 020e7a512). **Tester** - Widget.

**Story** - Move work forward on session board / Organize Ticket Hierarchy; Move work forward from chat bar / Steer Sessions / Start Backlog Item From Session List. No scenario covers dropping an idea on a closed card; "Keep Split off on a closed ticket" keeps a closed card from taking a child through Split, but not through a drop or `start_under`.

**Module and class** - `space/kanban/backlog_item.py` `BacklogItem.start_under` (`self.start().reassign_parent(parent)`, no refusal of a closed parent); `space/kanban/ticket.py` `Ticket.children` (answers every child, open or not) beside `TicketTree.is_stacked` ("an open child ... of an open parent").

**Severity** - wrong result (one ticket in two columns; the closed parent's card claims an open child).

**Steps** (sandbox `C:\dev\_et\after-1-2-1\widget`, cdd server 8931, MCP with `X-CDD-Project` = `work\repo`)
1. `ticket.create {"title":"Order history"}`; `ticket.close {"ticket":"order-history","leaving":[]}`.
2. `backlog-item.create {"title":"Payment retry"}`.
3. `backlog-item.start_under {"backlog_item":"Payment retry","parent":"order-history"}` - succeeds.
4. `board.show`.

**Expected** - Either a closed ticket takes no new child (refused before the item starts, as Split is off on a closed card), or the child is shown once.

**Actual** - Discovery `in_progress` holds `payment-retry` (`is_stacked: false`, parent `order-history`), and Complete holds `order-history` with `children: ["payment-retry"]`, `is_closed: true`.

**Tier that should catch it** - unit (organize-ticket-hierarchy domain spec over a closed parent); the specs give children only to open parents.
