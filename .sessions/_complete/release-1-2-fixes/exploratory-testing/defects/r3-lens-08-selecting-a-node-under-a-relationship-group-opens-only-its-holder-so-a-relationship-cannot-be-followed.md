# Selecting a node under a relationship group (invokes, returns, accesses) opens only the node that holds the group: the related node's file never opens and nothing expands in place

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App > Follow Relationships Under Node In Files App, scenario "Selecting a related node opens its file beside the open one" (*Then* board.py opens beside ticket.py, at Board.reread; marked Intended). The code promises something else: `files-graph.ts` `select` says the holder opens "and the node expands in place under the line that uses it". Neither happens.
- **Module and class:** `harness/files_app/app/files/files-graph.ts` `FilesGraph.select` and `connectorHolderOf` (asks the ranges of the holder, puts the member in `expanded`); `harness/files_app/app/files/source-of-file.ts` `expandedLines`, which looks for the member among the file's `callouts` (`session.file`: a story test's steps and markdown links) and finds none for a class, an operation, a spec or a DDD root. `file-source-view.tsx`, which another chat was editing, calls `expandedLines`; the rule is not in it.
- **Severity:** wrong result (question for the supervisor: which of the two promises stands)

## Steps

Sandbox `C:\dev\_et\round3\lens\work`; script `C:\dev\_et\round3\lens\drv\w13.py`.

1. Graph view, **clean_engineering** > **src** > **ordering** > **Cart** (of `src/ordering/cart.py`) > **check_out** > open **invokes**: it holds `authorise` (in `src/ordering/payment.py`) and `place` (in `src/ordering/order.py`).
2. Select **authorise**, then **place**.
3. The same under **returns** (class Order), under an observation's **invokes** (bdd > order_spec > an order > ... > should be paid > invokes > pay), and under a repository's **accesses** (ddd > Ordering > order > OrderRepository > accesses > Order).

## Expected

By the scenario: the related node's file opens beside the open one, at its lines (`payment.py` at `authorise`). By the code's own words: `check_out` opens and `authorise` shows in place under line 38, `payment.authorise()`.

## Actual

Each selection sends `graph-node-ranges` for the holder (`clean_engineering:Operation:src/ordering/cart.py:check_out:Cart`), and the page shows `src/ordering/cart.py` with lines 34 to 41 marked, exactly as selecting `check_out` itself does. No other file opens, no lines show under the call (no view zone is drawn), and the selected row is the member. All four groups behave the same: the observation's `pay` shows the observation's two lines, the repository's `Order` shows the repository. The only way to reach a related node is to find it at its own home in the tree, by name, among same-named rows (the Bookshop has six classes named Order).

Screenshots: `C:\dev\_et\round3\lens\shots\41-invokes-member-selected.png`, `45-operation-invokes-place.png`, `45-observation-invokes.png`, `45-repository-accesses.png`.

## Tier that should catch it

e2e, the story's browser test: the scenario is marked Intended and no step of `explore-graph-in-files-app.story.ui_e2e_spec.py` selects a member of a group; the unit spec `files-graph.spec.ts` ("Open Connectors In Place") covers only a story test's step invoking an operation, where the step's callout exists; no example selects a member under an operation's, an observation's or a repository's group.

## Also seen by
