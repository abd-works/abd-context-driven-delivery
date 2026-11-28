# widget-04 Main, the default session, accepts child tickets, then follows its child across stages and refuses every move

**Title** - `backlog-item.start_under` with parent `main` (and every ticket's `parent_choices`, which lists main) makes main a parent; main then shows in its child's stage and its own moves are refused with `ParentMovesWithChildrenError`.

**Charter** - theme 3, starting work from the Backlog and the board at once. **Tester** - Widget.

**Story** - Move work forward on session board / Organize Ticket Hierarchy; no scenario covers main as a parent. `space/kanban/.context/module-context.md` treats main as "no one piece of work" (refusing its text, tags, close, archive, delete, Backlog).

**Module and class** - `space/kanban/ticket_tree.py` `TicketTree.parent_choices` (returns `[]` for main as a child, but never leaves main out as a parent); `space/session/session_hierarchy.py` `SessionHierarchy.can_take_parent`; `BacklogItem.start_under` -> `reassign_parent`.

**Severity** - question.

**Steps** (sandbox `C:\dev\_et\after-1-2-1\widget`, cdd server 8931, MCP with `X-CDD-Project` = `work\repo`)
1. `backlog-item.create {"title":"Search filters"}`.
2. `backlog-item.start_under {"backlog_item":"Search filters","parent":"main"}` - succeeds.
3. `ticket.move_to {"ticket":"search-filters","stage":"Implementation"}`.
4. `ticket.move_to {"ticket":"main","stage":"Hardening"}`; `board.show`.

**Expected** - Main, refused as a piece of work everywhere else, is refused as a parent too (or this is intended and a scenario says so).

**Actual** - Step 2 shows `main{search-filters}`; after step 3 the board shows `Implementation: main{search-filters} | admin-report` and Discovery has no main; step 4 answers `ParentMovesWithChildrenError: main has child tickets; a parent moves only with its children`.

**Tier that should catch it** - unit (organize-ticket-hierarchy domain spec), if main should be refused; no example names main as a parent.
