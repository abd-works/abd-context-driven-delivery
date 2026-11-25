# Selecting a package, a module or an aggregate in the graph view opens nothing and fails with NamedPathNotFoundError, because the node's folder is refused as a file that is gone

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App. No scenario selects a folder node; the promise is in `harness/files_app/.context/module-context.md` ("Selecting a node opens its file at its lines, or, for a node no file's lines hold such as a folder, each listed file below it") and in the docstring of `session.graph_node_ranges` ("a node read from no file's lines, such as a module that is a folder, answers each file the nodes below it come from").
- **Module and class:** `space/session/node_spans.py` `NodeSpans._refuse_gone` and `_named_file` (added with the pixel-08 fix, commit 13cc270cb); shown by `harness/files_app/app/files/files-graph.ts` `FilesGraph.select`. Not in the Files app files another chat was editing.
- **Severity:** blocks work (every folder node of Clean Engineering and DDD: 16 of 16 in the Bookshop)

## Steps

Sandbox `C:\dev\_et\round3\lens\work` (the combined Bookshop, session `main`), stack `C:\dev\_et\round3\lens\drv\stack.py` (cdd server 8915, Files server 8916), script `C:\dev\_et\round3\lens\drv\w6.py`.

1. Open `http://127.0.0.1:8916/?files=main&fidelity=<all fifteen>&project=C:\dev\_et\round3\lens\work`, press **All session files**, press **Graph**.
2. Open **clean_engineering** > **src** and select **Module catalogue**. Also: **ddd** > **Ordering** > select **Aggregate order**; select **Package src**.

The same call without the page (`C:\dev\_et\round3\lens\drv\a3.py`): `POST /api/session/.sessions%2Fmain%2Fsession.json/graph-node-ranges {"node_id": "clean_engineering:Module:src/catalogue", "paths": [...the 84 listed files...]}`.

## Expected

Each listed file below the folder opens, the first at the top and the others below it, at the lines of the folder's nodes (`catalogue`: `src/catalogue/book.py`, `book.ts`, `catalogue.py`).

## Actual

The call answers 500 and the page shows a toast; the file open before stays open with no line marked:

```
The Files app did not open catalogue: cdd session.graph_node_ranges failed: NamedPathNotFoundError: nothing at src/catalogue, read from C:\dev\_et\round3\lens\work; name paths from the project's root, or absolute
```

All 16 folder nodes of the walk fail the same way: the 4 aggregates (`ddd:Aggregate:catalogue/book`, `fulfilment/shipment`, `ordering/cart`, `ordering/order`), the 9 packages and the 3 modules. `_named_file` answers the folder's own path for a node whose source names a folder with a start line, and `_refuse_gone` then asks `is_file()` of it, which a folder never is. The folder is there; the message says nothing is.

Screenshots: `C:\dev\_et\round3\lens\shots\10-select-module-catalogue.png`, `10-select-aggregate-order.png`, `10-select-package-src.png`.

## Tier that should catch it

Unit (`space/session/session_graph_spec.py`): it asks the ranges of a class and of an unknown node, never of a module or package, so the refusal added for a moved file was never run against a folder. The e2e graph story test selects only classes and operations.

## Also seen by
