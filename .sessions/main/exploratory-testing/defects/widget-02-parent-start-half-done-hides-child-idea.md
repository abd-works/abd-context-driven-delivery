# widget-02 Starting a parent whose child cannot start answers a failure but leaves the parent and the other children started, and the failed child's idea vanishes from the board

**Title** - `backlog-item.start` on a parent refuses with `TicketNameTakenError` for one child, yet the parent and every child before it are already opened, committed and pushed; the failed child's file is left alone in `_backlog/<parent>/` with no parent file, so the board no longer shows it and no tool can find, start or delete it.

**Charter** - theme 3, starting work from the Backlog and the board at once. **Tester** - Widget.

**Story** - Move work forward from chat bar / Steer Sessions / Start Backlog Item From Session List, "Start a parent with its child items" and "Show why a Backlog item did not start" ("no ticket is opened"). No scenario covers a child that fails to start.

**Module and class** - `space/kanban/backlog_item.py` `BacklogItem.start`: the parent's ticket is opened and its file kept first, then `for child in children: child.start("story", path).reassign_parent(ticket)`; nothing checks the children's names before the parent opens, and nothing undoes on a child's failure. `space/kanban/backlog_folder.py` `BacklogFolder.idea_files` lists a folder's markdown files only when the folder's own `<name>.md` is there, so the orphan is unlisted.

**Severity** - wrong result (the idea's only copy becomes unreachable; the board is half-moved).

**Steps** (sandbox `C:\dev\_et\after-1-2-1\widget`, cdd server on 8931, MCP with `X-CDD-Project` = `work\repo`)
1. `ticket.create {"title":"Order history"}` (an open ticket).
2. `backlog-item.create` Checkout flow, Address form, Card form, Gift wrap, and `backlog-item.create {"title":"Order history"}` (accepted, though a ticket has the name); `backlog-item.nest_under` each of the four under Checkout flow.
3. `backlog-item.start {"backlog_item":"Checkout flow"}`.
4. `board.show`; `backlog-item.start`, `backlog-item.delete {"backlog_item":"Order history"}`; `backlog-item.create {"title":"Checkout flow"}`.

**Expected** - The start is refused before anything moves, naming the child whose name is taken ("a name already taken is refused ... before any folder, file, or branch is made", `space/kanban/.context/module-context.md`, Constraint; "Never delete a backlog item's file: it is the only copy of the idea"). Or, at least, the failed child stays visible in the Backlog.

**Actual** - Step 3 answers `TicketNameTakenError: a ticket named order-history already exists; give 'Order history' another title`, but the board then shows `Discovery: checkout-flow{address-form,card-form,gift-wrap}` and the Backlog holds only Payment retry and Search filters; commit `016cfaa` on main (pushed) opened all four tickets. `.sessions/_backlog/checkout-flow/order-history.md` is still on disk, but step 4 answers `BacklogItemNotFoundError: no backlog item titled 'Order history' on the board` for start and delete, and `backlog-item.create Checkout flow` is refused with `BacklogItemTakenError: the Backlog already keeps an idea in .sessions/_backlog/checkout-flow.md` - a name blocked by a folder the board does not show.

Also: `backlog-item.create` and `nest_under` accept an item whose name an open ticket already has, so the clash only surfaces at start.

**Tier that should catch it** - unit (`backlog_folder_spec.py` / kanban spec with a session already named as a child); the specs start parents whose children all have free names.

## Also seen by

- Widget, second route, no name clash in the data: a person starts Checkout flow on the board while a chat starts its child Card form at the same moment (`backlog-item.start {"backlog_item":"Card form"}` from one MCP connection, `{"backlog_item":"Checkout flow"}` from another). Card form's start wins, opening card-form as a ticket with no parent; the parent's start then fails with `TicketNameTakenError: a ticket named card-form already exists`, after checkout-flow and address-form were opened, and `_backlog/checkout-flow/gift-wrap.md` is left orphaned and unlisted, exactly as above. So the half-move needs no bad data, only two people acting at once.
