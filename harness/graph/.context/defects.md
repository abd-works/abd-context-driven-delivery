# Defects

Historical fixes for the knowledge graph explorer under `harness/graph/app`. Tests live in `harness/graph/app/app.test.tsx`, `harness/graph/graph_spec.py`, and related specs.

- **Practices opened fully expanded.** The tree stays collapsed until a node is opened.
- **One invoke child hidden.** Both invoke children render under the operation.
- **Folder control would not accept a directory.** Choose folder writes the path and loads that working copy via `load_working_copy`.
- **Last folder forgotten on restart.** Stored in `cdd-graph-folder` and loaded on open.
- **Source canvas ate the mouse wheel.** Monaco scrollbar uses `handleMouseWheel: false` and `alwaysConsumeMouseWheel: false` in `app/source/SourceView.tsx`.
- **Class fold missing on a variable of a class type.** `variableTypes` in `app/source/call-expansion.ts` records the binding and folds that class under the line.
- **Violations switch ignored rule failures.** Turning it on sends `return_nodes` with `violations: true`.

## Not fixed

- **Scenario and step order.** Given, when, then, and and/but follow the source line; `populate` and `serialize` keep that order.
