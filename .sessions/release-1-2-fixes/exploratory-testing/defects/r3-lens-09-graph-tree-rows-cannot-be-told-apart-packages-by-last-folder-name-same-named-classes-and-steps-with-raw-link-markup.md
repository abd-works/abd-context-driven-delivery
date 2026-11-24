# Rows of the graph tree cannot be told apart: packages show only their last folder name (two top rows named src), the Python and TypeScript twins of a class have one name and one tooltip, and a step's name is its raw link markup cut off after a few words

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App > Expand Practice Tree In Files App ("nested as the Graph app nests them"). No scenario covers two nodes of one name, or a project with code outside one root.
- **Module and class:** `harness/files_app/app/files/files-graph-view.tsx` `GraphRowView` (the row's `title` is the kind and the name only; the file a node comes from is nowhere on the row) and the explorer entries it draws (`harness/graph/explorer.py`), where a package whose parent folder holds no code of its own is placed at the practice's root under its last folder name. `files-graph-view.tsx` is not among the files another chat was editing.
- **Severity:** cosmetic (misleading where two rows share a name)

## Steps

Sandbox `C:\dev\_et\round3\lens\work`; scripts `C:\dev\_et\round3\lens\drv\a1.py` (the tree through the API) and `w14.py`.

1. Graph view, open **clean_engineering**.
2. Open **ddd** > **Ordering** > **order**; open **clean_engineering** > **src** > **ordering**.
3. Open **stories** > **Check Out** > **Place Order** > **Submit Order** > **Submit a cart with one book**, and hover its Given step.

## Expected

A person can tell from a row, or its tooltip, which folder or file it stands for; a step reads as its sentence.

## Actual

- The clean_engineering tree's top rows are `src`, `story_tests`, `src`, `book`, `shipment`, `cart`, `order`. The first `src` is `src/`; the second is `bookshop/src`; `book` is `catalogue/book`, `shipment` is `fulfilment/shipment`, `cart` and `order` are `ordering/cart` and `ordering/order`. Their parents (`bookshop`, `catalogue`, `fulfilment`, `ordering`) are not shown, and both tooltips read `Package src`. Under `story_tests` the row `confirm-order` is `story_tests/check-out/confirm-order`, with `check-out` left out, while under `src` the folders nest as they are on disk.
- Every DDD building block and every class the project has in both languages shows as two rows with one name and one tooltip, in no fixed order: under the aggregate `order`, `Order, Order, Checkout, Checkout, OrderRepository, Payment, OrderRepository, Payment, OrderFactory, OrderFactory, OrderPaid, OrderPaid`; under the module `ordering`, `Cart, CartLine, Cart, CartLine, ..., Order, ..., Order`. Which is Python and which TypeScript shows only after selecting each. The six `_module` rows under `bookshop/src` (one per view file) are the same.
- A step of a story test in code is named by its text with the markdown link left in: the row's tooltip is `Given given the Customer has [Cart](../../../../.context/domain-model.md#cart-aggregate-root-entity) cart with Tiny Tales` (the kind, then the keyword again), and the row shows `given the Customer h...` (148 of 713 pixels), so the steps `given the Customer has [Cart]... cart with Tiny Tales` and `... empty cart` read alike. A markdown step keeps its `++Cart++` marks.

Screenshots: `C:\dev\_et\round3\lens\shots\32-ce-off.png` (the seven package rows), `20-d-root-order-ts.png`, `50-step-names-and-packages.png`.

## Tier that should catch it

Unit, in the page's spec (`harness/files_app/app/files/files-graph.spec.ts`) and the explorer's: their example project has one root, one language and no two nodes of a name.

## Also seen by

## Status

Fixed on release-1-2-fixes (2026-11-23). Python decides what each row shows, once, where the node is known: every explorer entry now sends a `label` beside its `name`, which `PlaceLabels` (`harness/graph/explorer.py`) decides for all the entries of one place together.

- A package or module (Clean Engineering's `folder_types`) reads as its path from the folder it sits under, or its whole path at the practice's root: `src` and `bookshop/src`, `catalogue/book`, and `check-out/confirm-order` under `story_tests`.
- Entries of one label read with their file after them, `Order (order.py)` and `Order (order.ts)`, or the file's path when two files share a name, `_module (catalogue/views.py)`.
- A link in a name reads as its words (`link_words`, `harness/markdown/markdown.py`, which `heading_anchor` now uses too), so the step reads `given the Customer has Cart cart with Tiny Tales`. The `++Cart++` marks of a markdown step are left as they are: the defect's brief asked only for link markup.

The Graph app (`app/graph/GraphView.tsx`) and the Files app (`files-graph-view.tsx`) show the label in the row, its tooltip and its open button (`labelOf`, `harness/graph/app/graph/explorer-trees.ts`).

Specs: `harness/graph/explorer_tree_spec.py` (packages at the root and under a package, a branch read on its own, two classes of one name, two files of one name, a step with a link), `harness/graph/app/graph/explorer-trees.test.ts` (the label of a tree item), `harness/files_app/app/files/files-graph.spec.ts` (Ticket shown and titled by its label).

The generated TypeScript type `ExplorerEntryData` declares `label` once the language adapters are installed again (`python scripts/install.py --ide Claude`); both apps compile and show the label before that, since `labelOf` reads it whether the type declares it or not.
