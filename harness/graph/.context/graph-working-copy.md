# Graph working copy

The explorer graph is built from source on disk, not from a separate query database.

`Graph.load_working_copy(folder, practices, database?, overlays?)` stores the repo root on `graph._folder`, creates one `PracticeGraph` per practice key, and calls `fill_working_copy` in `harness/graph/working_copy.py`. That module walks folders and TypeScript files, runs the practice parsers (`TypeScriptCleanEngineeringModel`, `TypeScriptStoryModel`, `StoryModel`, DDD stereotypes, optional LERN overlay), and applies node and edge tuples with `PracticeGraph.apply_nodes` / `apply_edges`.

Each node holds the object its parser built as `Node.model`: the `Operation`, `OoadClass`, `Parameter`, `Module`, BDD spec node, DDD building block, or Story/Scenario/Step. Rules read measurements through `node.get_fact`, which asks the model first, so every measurement has one copy and rules check exactly the object the explorer shows. Each model class lists its saved attributes in `graph_facts`; `graph.json` stores those with the node, so a graph reloaded without parsing still answers `get_fact` from `data`. The node's `data` keeps only what the loader alone knows, such as a class's folder or the interactions a model document adds.

`attach_rules` runs practice rule evaluators on the loaded graph. Each practice `root_node.populate()` builds the tree the app serializes.

The Vite app in `harness/graph/app` follows the CDD web domain access pattern. Its server holds one `CddConnection` and mounts the generated `graphRoutes`, so every call reaches `Graph.current()`, the one graph the cdd server holds. The page's `GraphClient` extends the generated `GraphClientGenerated` and calls `loadWorkingCopy` with every practice name mapped to the chosen folder root. It adds only the folder dialogs, which `choose_folder.py` opens on the server's machine.

Every graph operation answers an object that marks its data with `@data_field`: the graph's own `PracticeGraph` and `Filter`, the `Inventory` of practices, or an object from `harness/graph/explorer.py`, such as an explorer tree entry or a node's source, which holds the node it describes and reads its data from it.

`EDGE_ORDER` in `graph.py` says where each edge kind's group sits under a node in the explorer tree. The loader, the model objects, and the schema edges all read it through `edge_order`, and `graph.json` saves the number on each edge. Every `schema.yaml` and overlay `rules.yaml` is read by one `Schema` class in `harness/guidance/schema.py`, so the schema edges, the rule lists, and the fidelity map see the same types and fields. The source view's folds and the inlining of called operations are built in TypeScript (`app/source/call-expansion.ts`); Python sends only the source text with each call marked. A load reports each practice, file, and rule through `report_progress`, and the page reads those steps from `/cdd/progress` while it waits. Every call finishes within ten minutes.
