# CS violations

Ticket maintain-tickets-on-board, validate run of 2026-11-11 17:57 with the overlay `cdd_web_domain_access`.

## `same-verb-across-layers`
- `space/kanban/ticket.py` `choose_parent`: the tool is `ticket.choose_parent`, but it calls the domain operation `Ticket.reassign_parent`.
- `space/kanban/ticket.py` `place_before`: the tool is `ticket.place_before`, but it calls the domain operation `Card.move_before`.

## `one-line-to-the-domain`
- `space/kanban/ticket.py` `place_before`: the tool commits the new order on main after `move_before`, so calling `move_before` directly keeps the order but doesn't commit it.
- `space/kanban/backlog_item.py` `place_before`: the same, for a backlog item.
