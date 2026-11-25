# graph.refresh of Stories files nobody changed leaves a different graph each time: the map alone detaches every story test in code from its story, one story test doubles its story and epic, and the story_tests folder drops every markdown scenario

- **Charter:** Round 3, second pass - the knowledge graph of the combined project, check 4
- **Tester:** Cog
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a refresh of part of the Stories files. `Graph.refresh` promises: "drop every node read from them, read them as they are now, link them to the other practices' nodes ... Every other node stays as it was". Validate with `paths` refreshes the session's graph the same way, so this is what a validate of the story map or of one story test leaves behind.
- **Module and class:** `harness/graph/graph_reads.py` `GraphReads.refresh`, with `cdd_guidance/practices/stories/stories.py` `Stories.read_files` (`_take_story_test`, which puts a story test's scenarios on the map's Story only when the map is read in the same call).
- **Severity:** wrong result
- **Related:** r3-sparky-08 (a load with the map and a load without it differ). Here no file changes and one loaded graph is refreshed.

## Steps
Sandbox `C:\dev\_et\round3\cog\work` (a copy of the combined Bookshop), session `main`, throwaway cdd server on the build under test: `sh C:/dev/_et/round3/cog/drv/go.sh r2.json`.

    graph.load_files {"folder": "C:/dev/_et/round3/cog/work", "practices": ["stories","ddd","ux","clean_engineering","bdd"], "files": [".context","story_tests","src","catalogue","ordering","fulfilment","bookshop","ux"]}
    graph.save_json {}                                                   (A: Story 16, Scenario 17, 17 scenarios edges)
    graph.refresh {"paths": [".context/story-map.md"]}                    -> "Refreshed 1 files."   save (B)
    graph.refresh {"paths": ["story_tests/fulfil-order/pack-order/pack_order_story.test.py"]}       save (C)
    graph.refresh {"paths": ["story_tests"]}                              -> "Refreshed 20 files."  save (D)

No file is edited between the calls. Saved graphs: `all`, `r2a`, `r2b`, `r2c` `.graph.json` in `C:\dev\_et\round3\cog\drv`; compare two with `python df.py all.graph.json r2a.graph.json`.

## Expected
A, B, C and D are the same graph, since the files are the same.

## Actual
- **B, the map refreshed:** 13 `scenarios` edges are gone, each from a story to a scenario of a story test in Python or TypeScript (Authorize Payment, Cancel Order, Mark Order Shipped, Pack Order, Search Books, Submit Order, View Order Confirmation). The 13 Scenario nodes stay, held by no story; only the four markdown scenarios keep their story.
- **C, one story test refreshed:** 5 nodes added: a second `Story:story_tests/fulfil-order/pack-order/pack_order_story.test.py:Pack Order` beside the map's Pack Order, `Epic:story_tests/fulfil-order:Fulfil Order` beside the map's epic, a SubEpic also named Fulfil Order, and two Examples. 156 edges added, most of them `invokes` to every `create` and `load` in the project (r3-sparky-09).
- **D, the folder refreshed:** against A, 46 nodes gone and 31 added. Gone: all four markdown scenarios with their steps, all 8 Examples, and the scenarios of Submit Order and Authorize Payment. Added: Epics `story_tests/browse-books:Browse Books`, `story_tests/check-out:Check Out` and `story_tests:Fulfil Order`, seven Story nodes named for files (two Cancel Order, two View Order Confirmation), and SubEpics named after their epic. 95 edges gone, 415 added.

A full `graph.load_files` afterwards brings A back. Every answer says only "Refreshed n files". No edge points at a missing node in any of the four graphs.

The same order dependence shows in DDD (added to r3-bolt-05): `graph.refresh {"paths": ["ordering/order/order.py"]}` moves the Python OrderRepository's `accesses` edge from the TypeScript root to the Python root and gives the TypeScript repository a second one, and a later refresh of `src/ordering/order_spec.py`, a file of another practice, adds the first one back.

## Tier that should catch it
Heavy (`graph_build_heavy_spec.py`): no example refreshes the story map, or one story test, of a graph that holds both and compares the graph with the one before.
