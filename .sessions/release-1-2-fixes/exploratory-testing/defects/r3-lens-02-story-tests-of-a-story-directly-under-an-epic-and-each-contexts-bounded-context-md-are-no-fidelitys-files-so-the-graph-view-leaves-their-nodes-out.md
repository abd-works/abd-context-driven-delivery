# The story tests of a story that sits directly under an epic, and each context's bounded-context.md, are no fidelity's files, so the file bar leaves them out while a practice is on and the graph view shows those stories with no scenario and no context mapping at all

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App > Expand Practice Tree In Files App ("the practice trees of the session's graph, holding only the nodes of the files the file list would show"). No scenario covers a story with no sub-epic.
- **Module and class:** `space/kanban/ticket_choices.py` `root_files` (`each.holds(repo / entry.path)` answers no fidelity for these files) and the declared outputs it matches against: `cdd_guidance/practices/stories/stories.md` (`story_tests/{epic}/{sub-epic}/{story}/...` only) and `cdd_guidance/practices/ddd/ddd.md` (tactics says "write `.context/bounded-context.md` in each context folder" but declares only `{bounded_context}/{aggregate}/`). The page then drops them in `harness/files_app/app/files/files-page.ts` `rootFilesShown` (a file no fidelity declares shows only while no practice is selected), which is as written. Not in the Files app files another chat was editing.
- **Severity:** wrong result (3 of the Bookshop's 9 stories with tests lose every scenario in the tree, and the 3 ContextMapping nodes the graph holds are never shown)

## Steps

Sandbox `C:\dev\_et\round3\lens\work`, session `main` with all five practices on; stack `C:\dev\_et\round3\lens\drv\stack.py`.

1. Open the Files app on the session with every fidelity, press **All session files**, show the list: 97 entries. `ticket/main/root-files` answers 104 files; these answer `"fidelities": []` and are not listed:
   - `story_tests/browse-books/search-books/search_books_story.test.ts` (Search Books, a story directly under the epic Browse Books)
   - `story_tests/fulfil-order/pack-order/pack_order_story.test.py`, `story_tests/fulfil-order/fulfil-order.story.shared.py`, `.story.domain.spec.py`, `.story.server.spec.py`, `story_tests/fulfil-order/examples/order_examples.py` (Pack Order and Mark Order Shipped, directly under the epic Fulfil Order)
   - `story_tests/check-out/confirm-order/examples/order.examples.ts`
   - `catalogue/.context/bounded-context.md`, `fulfilment/.context/bounded-context.md`, `ordering/.context/bounded-context.md`
   - (the UX view files `bookshop/src/api.ts`, `App.tsx`, `bookshop/buy-a-book.drawio`, `ux-map.json`, `ux/ux.json` are r3-gizmo-05's)
2. Press **Graph**, open **stories** > **Browse Books** and **Fulfil Order**; open **ddd**.
3. For comparison ask the graph with those files added to the paths: `C:\dev\_et\round3\lens\drv\a2.py` (`graph-trees` and `graph-branch` with the 84 listed files plus the 10 above).

## Expected

Files the practices write where their fidelities say (a story's folder under its epic when the map gives it no sub-epic; the context's own `bounded-context.md`) are that fidelity's files, are listed with Stories or DDD on, and their nodes are in the tree: Search Books, Pack Order and Mark Order Shipped each with two scenarios, and the ContextMapping nodes under their contexts.

## Actual

- **Search Books**, **Pack Order**, **Mark Order Shipped** show as leaves, with no twist; selecting Pack Order opens only `.context/story-map.md` at line 55. With the files added to the paths (step 3) the same graph answers `Find a book by a word of its title`, `Find nothing for an unknown word`, `Pack a paid order`, `Refuse to pack an unpaid order`, `Mark a packed order shipped`, `Keep an order that is not packed as it is`. Pack Order's `when` is the Bookshop's one step that invokes production code (`Order.pack`), so the link from Stories to Clean Engineering cannot be followed in the Files app at all.
- `graph.inventory` counts 3 `ContextMapping` nodes for DDD (`ddd:ContextMapping:fulfilment/.context/bounded-context.md:5`, `ordering/...:5`, `ordering/...:6`); the tree shows none, on any branch, since their file is not among the files listed. Yet selecting **BoundedContext Ordering** opens that same unlisted `ordering/.context/bounded-context.md`.
- Tree counts: DDD 41 nodes shown of 44 in the graph; Stories 83 of 83 for the listed files, 6 scenarios and their steps short of what the project holds.

Screenshots: `C:\dev\_et\round3\lens\shots\20-s-story-pack-order.png`, `20-d-context-ordering.png`, `02-all-session-files-list.png`.

## Tier that should catch it

Heavy (`space/kanban/kanban_tools_spec.py`, the `root_files` examples): its files sit under an epic and a sub-epic, and it has no context folder with a `bounded-context.md`. The Bookshop is the first project of the round with an epic that holds stories directly.

## Also seen by
