# Question: load_practice_roots leaves the story map and every folder outside a practice's root out of the graph, and the DDD nodes do not match the files

- **Charter:** Round 2 - the knowledge graph and the formats of the other practices, as an agent whose files move, rename and stop parsing between two calls
- **Tester:** Widget
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers this.
- **Module and class:** `harness/graph/graph.py` `Graph.load_practice_roots`, `graph_reads.py`, `saved_graph.py`; the DDD reading under `cdd_guidance/practices/ddd/model`.
- **Severity:** question

## Steps
Sandbox `repo` (`C:\dev\_et\widget\work\repo`), session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`, calls in `drv\d2.json`, `drv\d5.json`, `drv\d6.json`). The project holds `.context/story-map.md`, scenarios under `story_tests/`, a package `shop/`, `src/order.py`, `.context/bounded-context-map.md` (contexts Ordering and Catalog) and `.context/domain-model.md`. The session's roots are the defaults (stories: `tests`, which does not exist; clean-engineering: `src`).

    graph.load_practice_roots {}
    graph.inventory {}
    graph.load_files {"folder": "C:/dev/_et/widget/work/repo", "practices": ["stories","ddd","clean_engineering","bdd"], "files": [every folder]}
    graph.return_nodes {"filter": {"practice": "ddd"}}
    graph.save_json {}

## Expected
Not known. Four things to settle:

1. After load_practice_roots the inventory has no stories practice at all, though the story map sits where the story_map fidelity writes it (`.context/story-map.md`). Is the map meant to be in the session's graph only when it sits under the Stories root?
2. Classes read under the Clean Engineering root get ids from that root (`.context/src-model.md:Order`), while load_files gives the same file `src/.context/src-model.md:...`. Are the two meant to differ?
3. With every DDD file loaded, the only BoundedContext node is one named "bounded context" at `.`; Ordering and Catalog are not nodes. Aggregates Order and Book are there; Book is also an EntityRoot, Order is not, though both are written `<<Aggregate Root>> <<Entity>>`.
4. `graph.save_json` followed by a new server's `load_practice_roots` answered "Loaded the working copies", not "Loaded the saved graph" (it said the latter once, in an earlier run). A graph.json that is truncated, an empty object, or a list is passed over the same way without a word. When is the saved graph read?

## Actual
As listed. Also seen in the same runs:

- `graph.load_files` with `"folder": "."` ran past 10 seconds and left every practice empty, where the absolute folder loaded the same files in half a second.
- A truncated graph.json given to validate's `graph` fails with a raw `JSONDecodeError: Unterminated string starting at ...`; an empty object gets the clear `SavedGraphOutdated: ... is in shape None, not 5; load the working copy again`.
- `graph.refresh` reads exactly the paths given, as its description says: after `shop/catalog.py` moved to `shop/books/catalog.py`, a refresh of `shop/books` alone left the node `shop/catalog.py:Catalog` and its `missing-module-context` violation in the graph. `validate` with `paths: ["shop/books"]` did drop the node of the file that was gone.

## Tier that should catch it
Once answered, heavy (`graph_build_heavy_spec.py`).
