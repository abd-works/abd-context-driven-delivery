# PracticeGraph

**Purpose:** Hold one graph for a working area: nodes, relationships, and rule hits. Stories, Clean Engineering, DDD, and BDD each add their own node types and CodeQL populate; this package does not name those types.

**Primary use case:** `PracticeGraph(root)`, register and relate nodes, then `evaluate_rules` so `node.rules.violations` can be read.

**Rationale:** The graph is the registry. Practice guidance stays on Stories, Clean Engineering, DDD, BDD, UX. This is not a practice and not a second graph type beside PracticeGraph.

## Seam

`PracticeGraph` is the seam. `Node` is mixed into practice types. `CodeQL` runs queries. `RuleRegistry` evaluates graphQuery files that live on each practice.

Constraint: populate from CodeQL facts, not from markdown. A *GraphRule* that is not graph-evaluated stays in the registry and is not run. This package does not import practice node classes — those extensions import `Node` from here.

## Public API

- `PracticeGraph(root, rule_registry=None)`
- `register(node)` / `relate(edge)`
- `evaluate_rules(slugs=None, skip=None, *, codeql_results=None)`
- `CodeQL.run_queries(queries)` / `CodeQL.populate` is called from a practice, not from this type's inheritance
- `RuleRegistry.load()` / `RuleRegistry.evaluate(graph)`
- `node.rules.violations`

## Dependencies

None on practice packages. Practices depend on this module (`Node`, `PracticeGraph`, `CodeQL`).
