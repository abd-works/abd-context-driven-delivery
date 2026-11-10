# Validation report — harness/codeQl_graph

Scope: `src/` against clean-engineering **model** rules in `practices/clean_engineering/clean_engineering.md`.

## clean_engineering / model

| Rule | Result | Evidence |
|---|---|---|
| `model-modules-follow-the-partition` | Pass | `src/` is the graph module the sketch names: `CodeQLKnowledgeGraph`, `CodeQLPracticeGraph`, `Node`, `Edge`, `EdgeType`, `Source`, `CallFold`. |
| `class-not-property-instance-or-subtype` | Pass | `CodeQLModule`, `CodeQLOOadClass`, and the other semantic types are subtypes of `Node`, selected by `semantic_type` in `Node.from_fact`. |
| `keep-classes-single-responsibility` | Pass | `Node` walks children, `CodeQLPracticeGraph` holds facts, `CodeQLKnowledgeGraph` runs populate then `buildGraph`. |
| `shape-classes-around-resources` | Pass | The graph owns practices, a practice owns nodes and edges, a node owns `children`. |
| `put-logic-on-the-owning-resource` | Fail | `serializeNode` walks `node.children` from outside `Node`. The node owns that tree. |
| `hide-inner-details` | Pass | `populated` is private. `children`, `source`, and the fact maps are the public model. |
| `use-property-not-accessor` | Fail | `Source.contents` is a property. `edgeCount()` and `edgeTypeKinds()` take no parameters and return derived state. |
| `prefer-class-operations` | Fail | `queryFiles`, `nodeFact`, `edgeFact`, `codeqlType`, `serializeNode`, `ensureDatabase`, `runQuery`, and `writeActual` are module functions beside the types that own that work. |
| `use-explicit-dependencies` | Fail | `CodeQLKnowledgeGraph.populate` builds the database path inside the method and calls `ensureDatabase` / `runQuery` as globals. Those collaborators are not constructor parameters. |
| `external-system-interface-is-one-way` | Pass | `graph.ts` imports `./codeql.ts`. The runner does not import the graph. |
| `keep-operations-single-responsibility` | Pass | `load_nodes`, `load_edges`, and `Node.populate` each do one job. |
| `limit-operation-parameters` | Pass | Domain operations take the path and the practice list, or a parent node. |
| `avoid-vague-parameter-names` | Pass | Fact fields are `node_id`, `semantic_type`, `parent_id`, `display`. |
| `errors-out-of-existence` | Fail | `runQuery` catches every CodeQL failure and returns `[]`. A broken query is not an ordinary empty result. |
| `state-change-returns-record-or-named-failure` | Fail | The same catch turns a failed query into an empty tuple list, so populate continues with a silent gap. |
| `domain-exception-carries-context` | Fail | There is no typed failure carrying the query path and the CodeQL stderr. |
| `limit-comments` | Pass | The source does not narrate lines the names already state. |
| `write-invariants` | Fail | `populated` stops a second walk in code. The classes do not name the rules they keep: both edge ends resolve, direct children share one list, a cycle is not walked again. |
| `write-interactions` | Pass | `Node.populate` asks `edge.child.populate`. `load_edges` asks `registered` for both ends. |
| `use-intention-revealing-names` | Fail | `CodeQLOOadClass` does not spell the OOAD type it constructs. |
| `use-consistent-naming` | Pass | Fact names follow the sketch: `node_id`, `semantic_type`, `load_nodes`, `load_edges`. |
| `eliminate-duplication` | Fail | The `grouped` and `relationship` branches in `Node.populate` are the same sequence: find or create a kind node, push it, populate the child under it. |
| `one-canonical-model-document` | Pass | The class model for this package is `.context/codeql-populate-model.md`. |
