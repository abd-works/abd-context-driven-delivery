# Defects

Historical fixes for the knowledge graph explorer under `harness/graph/app`. Tests live in `harness/graph/app/app.test.tsx`, `harness/graph/graph_spec.py`, and related specs.

- **Practices opened fully expanded.** The tree stays collapsed until a node is opened.
- **One invoke child hidden.** Both invoke children render under the operation.
- **Folder control would not accept a directory.** Choose folder writes the path and loads that working copy via `load_working_copy`.
- **Last folder forgotten on restart.** Stored in `cdd-graph-folder` and loaded on open.
- **Source canvas ate the mouse wheel.** Monaco scrollbar uses `handleMouseWheel: false` and `alwaysConsumeMouseWheel: false` in `app/source/SourceView.tsx`.
- **Class fold missing on a variable of a class type.** `variableTypes` in `app/source/call-expansion.ts` records each variable's class and folds that class under the line.
- **Violations switch ignored rule failures.** Turning it on sends `return_nodes` with `violations: true`.
- **Scenario and step order.** Stories, backgrounds, scenarios, and steps (given, when, then, and and/but) follow their source lines: `Node.populate` sorts them by line, and `serialize` keeps that order. `graph_spec.py` checks it ("should list the steps in source order").
