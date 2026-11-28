# pixel-02: `ticket.tag` and `ticket.edit_text` on a parent answer 143,039 characters, twice MCP's limit, because they still send the ticket whole with each child whole

**Charter:** theme 5, board answers for a big board. **Tester:** Pixel.

**Story:** Move Work Forward On Session Board / Organize Ticket Hierarchy and See Work On Session Board. No scenario covers answer size; the promise is the size fix af30e8874.

**Module and class:** `space/kanban/ticket.py`: `Ticket.tag`, `Ticket.edit_text`, `Ticket.add_child`, `Ticket.pull_out`, `Ticket.reassign_parent`, `Ticket.create` return `Ticket` (whole), not `in_answer()`. `backlog_item.py`: `BacklogItem.start` and `start_under` do the same (see pixel-03 when measured).

**Severity:** blocks work. Claude Code refuses an MCP answer of this size (the #107 debug note shows 74,106 characters refused), so the agent that tagged or edited a parent never learns whether it worked.

## Steps

1. Sandbox server `python -m harness.mcp --port 8941`, throwaway `CDD_HOME`, client header `X-CDD-Project: <work/repo>`.
2. `ticket.create {"title": "Big board ticket 002"}`, `ticket.edit_text` with a 2,000-character idea, `ticket.add_child` three times.
3. With about 150 tickets on the board, call `ticket.tag {"ticket": "big-board-ticket-002", "word": "big"}`.
4. Call `ticket.edit_text` on the same parent with the same 2,000 characters.

## Expected

af30e8874 made moves, close, archive and activate answer "with the ticket as the overview sends it ... so a plan-sized ticket stays under MCP's answer size limit"; `OverviewTicket` sends children by name, because "sent whole, each child would carry its own progress, stage work, and children, so a ticket two levels of children deep would triple the answer". The other ticket tools should answer the same way, under the 40,000 characters the spec holds the overview to.

## Actual

| Call | Seconds | Characters |
|---|---:|---:|
| `ticket.tag` on a parent with 3 children | 3.68 | **143,039** |
| `ticket.edit_text` on that parent | 2.18 | **143,039** |
| `ticket.add_child` (answers the child) | 3.58 | 35,365 |
| `ticket.pull_out` (answers the child) | 2.47 | 35,407 |
| `ticket.create` / `ticket.edit_text` on a ticket with no children | ~1.2 | 34,000-36,000 |

Each child is sent whole, 35,340 characters each; the parent also sends its 2,000-character text and `parent_choices`, a list of every ticket on the board (148 names, 3,579 characters), so even a childless ticket's answer grows with the board. A parent with a 25,000-character plan and no children would also pass the limit through `edit_text`, since the text comes back in the answer.

## Tier that should catch it

Unit (`kanban_tools_spec.py`): the size specs cover only `board.overview`, `move_to`, and `move_next`. One example per published ticket tool on a parent with children would catch every tool that does not answer `in_answer()`.

## Also seen by
