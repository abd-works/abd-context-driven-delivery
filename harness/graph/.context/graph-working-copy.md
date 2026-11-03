# Graph working copy

The explorer graph is built from source on disk, not from a separate query database.

`Graph.load_working_copy(folder, practices, database?, overlays?)` stores the repo root on `graph._folder`, creates one `PracticeGraph` per practice key, and calls `fill_working_copy` in `harness/graph/working_copy.py`. That module walks folders and TypeScript files, runs the practice parsers (`TypeScriptCleanEngineeringModel`, `TypeScriptStoryModel`, `StoryModel`, DDD stereotypes, optional LERN overlay), and applies node and edge tuples with `PracticeGraph.apply_nodes` / `apply_edges`. `attach_rules` runs practice rule evaluators on the loaded graph. Each practice `root_node.populate()` builds the tree the app serializes.

The Vite app in `harness/graph/app` follows the CDD web domain access pattern. Its server holds one `CddConnection` and mounts the generated `graphRoutes`, so every call reaches `Graph.current()`, the one graph the cdd server holds. The page's `GraphClient` extends the generated `GraphClientGenerated` and calls `loadWorkingCopy` with every practice name mapped to the chosen folder root. It adds only the folder dialogs, which `choose_folder.py` opens on the server's machine.

Every graph operation answers a `TypedDict` from `harness/graph/data.py`. A load reports each practice, file, and rule through `report_progress`, and the page reads those steps from `/cdd/progress` while it waits. Every call finishes within ten minutes.
