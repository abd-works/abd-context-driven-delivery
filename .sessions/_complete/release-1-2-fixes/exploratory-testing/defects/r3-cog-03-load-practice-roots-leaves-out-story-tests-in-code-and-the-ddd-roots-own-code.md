# graph.load_practice_roots on a session with all five practices leaves out every story test in code and the DDD root's own tactics code, makes DDD roots from classes under the Clean Engineering root, ignores the roots added to a fidelity, and names each node's file from its practice's root

- **Charter:** Round 3, second pass - the knowledge graph of the combined project, check 4
- **Tester:** Cog
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a session whose practices have different roots. `Graph.load_practice_roots` promises to "open each practice this graph holds on the folder its session names for it": "the Graph app's whole load".
- **Module and class:** `harness/graph/graph_reads.py` `GraphReads.practice_roots` (one folder per practice, `practice.session_root`), the Stories and DDD readings under `cdd_guidance/practices/stories/model/graph_reading.py` and `cdd_guidance/practices/ddd/model/graph_reading.py`.
- **Severity:** wrong result (the graph the Graph app shows for the session is a fraction of the project, with no word that anything was left out)
- **Related:** widget-22 (question, round 2: the map and folders outside a root, ids relative to the root). This is the round 3 build with roots chosen for every practice.

## Steps
Sandbox `C:\dev\_et\round3\cog\work` (a copy of the combined Bookshop), session `main`, throwaway cdd server: `sh C:/dev/_et/round3/cog/drv/go.sh a2.json`.

    practice-session-output.choose_root {"session":"main","practice":"stories","path":"story_tests"}
    practice-session-output.choose_root {"session":"main","practice":"clean_engineering","path":"src"}
    practice-session-output.choose_root {"session":"main","practice":"bdd","path":"src"}
    practice-session-output.choose_root {"session":"main","practice":"ux","path":"bookshop"}
    practice-session-output.choose_root {"session":"main","practice":"ddd","path":"ordering"}
    fidelity-session-output.add_root {"session":"main","practice":"ddd","fidelity":"tactics","path":"catalogue"}
    fidelity-session-output.add_root {"session":"main","practice":"ddd","fidelity":"tactics","path":"fulfilment"}
    fidelity-session-output.add_root {"session":"main","practice":"ux","fidelity":"mockup","path":"ux"}
    graph.load_practice_roots {}        -> "Loaded the working copies."
    graph.inventory {}
    graph.save_json {}                  (kept as C:\dev\_et\round3\cog\drv\roots.graph.json)

For comparison, `graph.load_files` on the same folders (`a3.json`, kept as `all.graph.json`).

## Expected
The same nodes `graph.load_files` gives for the files under the session's roots: 17 scenarios, the DDD code of `ordering/`, `catalogue/` and `fulfilment/`, and each node's file written from the project's root.

## Actual
| | load_files | load_practice_roots |
|---|---|---|
| Stories Scenario | 17 | 4, the markdown ones the map links to; none of the 13 scenarios of the Python and TypeScript story tests under `story_tests`, the root chosen for Stories |
| Stories `invokes` edges | 57 | 0 |
| DDD BoundedContext | 3 | 1 (Ordering; the roots added to tactics, `catalogue` and `fulfilment`, are not read) |
| DDD Aggregate | 4 (`ordering/cart`, `ordering/order`, ...) | 2, named `bookshop` and `ordering`: the folders `src/bookshop` and `src/ordering` of the Clean Engineering root |
| DDD EntityRoot | 8 | 4: `bookshop/order.py:Order`, `bookshop/order.ts:Order`, `ordering/order.py:Order`, `ordering/order.ts:Order`, which are the Clean Engineering classes `src/bookshop/order.*` and `src/ordering/order.*` |
| DDD ValueObject, Entity, DomainEvent, DomainService, Factory, Specification | 6, 2, 4, 2, 2, 2 | 0: nothing of `ordering/cart/` or `ordering/order/`, the code under the root chosen for DDD, is read |
| BDD Spec | 16 | 6 |

Each node's `file` is written from its own practice's root, so one path means different files: `ddd:EntityRoot:ordering/order.py:Order` and `bdd:Spec:ordering/order_spec.py` are `src/ordering/...`, `ddd:ContextMapping:.context/bounded-context.md:5` is `ordering/.context/bounded-context.md`, and the Stories files are `story-map.md` and `../story_tests/fill-cart/add-books/add_book_to_cart_story.test.md`. `ordering/order.py` is no file of the project, and `ordering/` is also the DDD root.

The only edges between practices are the 26 `invokes` from BDD observations to Clean Engineering.

## Tier that should catch it
Heavy (`graph_build_heavy_spec.py`): no example loads the practice roots of a session whose Stories, DDD and Clean Engineering roots are three different folders and compares the nodes with a load of the same files.

## Status: fixed (2026-11-23)
- Fixed before this pass (`edaba0a68`): a story test in code keeps its steps, `invokes` edges and examples when loaded with the map.
- Fixed now: `GraphReads.practice_roots` (`harness/graph/graph_reads.py`) reads every practice the graph holds from the files under the folders its session names for it, as `graph.load_files` reads the same files: every practice is opened on the session's project folder, so each node's file is named from the project's root (`ordering/order/order.py`, not a path from the practice's root that names another file), and the files read are those under every practice's roots, so DDD, which builds its building blocks from the classes Clean Engineering read, sees the tactics code under its own roots. `PracticeGuidance.session_roots` (was `session_root`) answers the practice's folder and every folder added to one of its fidelities, so the roots added to DDD's tactics are read. Nothing is saved by this load, since the graph then holds only the files under the roots; the answer is "Loaded N files under the practice roots."
- Covered by: `harness/graph/graph_build_heavy_spec.py`, "the Graph app's whole load of a session whose practices work in different folders": a copy of the Bookshop project with Stories at `story_tests`, DDD at `ordering` with `catalogue` added to its tactics, Clean Engineering at `src`, UX and BDD turned off, loaded through a real cdd server. Each practice holds the nodes `graph.load_files` gives for the same folders; the story tests in Python and TypeScript give their scenarios; DDD holds `ordering/order/order.py:Order` and `catalogue/book/book.py:Book`. The Graph app's scenarios (`integrate-practice-content-editor-apps-*.story.domain.spec.py`) read the roots a load named through `roots_loaded` (`space/kanban/knowledge_graph_examples.py`).
- Re-run on a copy of the tester's sandbox with its session's roots: `load_practice_roots` answers "Loaded 72 files under the practice roots." and holds 20 Stories scenarios, 3 DDD bounded contexts, 8 aggregates and 12 entity roots, the counts `load_files` gives for the same folders (before: 1 context, 2 aggregates named `bookshop` and `ordering`, no value objects or events).
