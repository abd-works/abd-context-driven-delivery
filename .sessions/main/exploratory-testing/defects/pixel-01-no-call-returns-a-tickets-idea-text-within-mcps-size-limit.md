# pixel-01: No call returns one ticket's idea text within MCP's size limit; the promised `ticket.show` does not exist

**Charter:** theme 5, board answers for a big board. **Tester:** Pixel.

**Story:** Move Work Forward On Session Board / See Work On Session Board. No scenario covers how a robot reads one ticket's idea text; the promise is in the code (below).

**Module and class:** `space/kanban/ticket.py`, `OverviewTicket.text` and `Ticket.in_answer` (their docstrings send the reader to `ticket.show`); `space/kanban/board.py`, `Board.show`.

**Severity:** blocks work. A robot that moves, closes, archives, or activates a ticket, or reads the overview, gets `"text": ""` and has no call that returns that text inside the limit.

## Steps

1. Sandbox server: `python -m harness.mcp --port 8941` from the build, `CDD_HOME` a throwaway folder; MCP client with header `X-CDD-Project: <work/repo>`.
2. List the tools: there is `ticket.edit_text` but no `ticket.show`, and no `backlog-item.show`.
3. Create about 60 tickets with `ticket.create`, each with a 2,000-character idea through `ticket.edit_text`, 25 of them with one to three children (`ticket.add_child`).
4. Call `ticket.move_to` on one: its answer has `"text": ""`.
5. Call `board.show`, the only call left that sends the text.

## Expected

`OverviewTicket.text`: "`board.show` and `ticket.show` send it." `Ticket.in_answer`: "The board reads the board again after each of them, and `ticket.show` sends the text." The spec comment in `kanban_tools_spec.py` (line ~1392) says the same. So one call should return one ticket whole, text included, at the size of one ticket.

## Actual

- No `ticket.show` tool is published, and `git log -S"ticket.show"` shows it never existed: only the two size-fix commits mention it.
- `board.show` on that board (about 115 sessions): **4,114,441 characters in 7.45 seconds** (the Discovery column alone is 3,952,762), about 160 times past Claude Code's MCP answer limit (the debug note for #107 shows 74,106 characters already refused).
- So once the board has a few dozen tickets, an agent has no MCP call that returns a ticket's idea text; it can only read `.sessions/<name>/<name>.md` off disk, which an MCP-only robot cannot do and which is wrong in a ticket's worktree.

## Tier that should catch it

Unit (`kanban_tools_spec.py`): the size fixes assert the text is left out but never that another call returns it. A spec "a robot that moved a ticket reads its text with one call under 40,000 characters" would have shown the missing tool.

## Also seen by
