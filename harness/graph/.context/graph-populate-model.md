# Graph populate model

The explorer graph lives in `harness/graph/`. `Graph` holds one practice graph per practice name. `fill_working_copy` in `working_copy.py` registers nodes and edges from parsers and story models, then `attach_rules` applies schema-backed rules.

There is no `.ql` loader channel. Extensions add Python in `working_copy` or practice `model/` parsers.

## Graph

+ practices: dict
	// practice name → PracticeGraph
+ folder: Path | None
	// repository root for this working copy
+ overlays: list[str]
	// pattern overlay roots merged into the load

## PracticeGraph

+ name: str
+ nodes: dict
	// semantic_type → list[Node]
+ edges: dict
	// kind → list[Edge]
+ root_node: Node
+ loaded: list[str]
	// e.g. nodes, edges, rules after fill

## fill_working_copy(graph)

Interaction:

	→ TypeScriptCleanEngineeringModel.parse for CE under src/
	→ DDD stereotypes from CE class facts
	→ story files for Stories practice
	→ story ↔ CE edges when both practices are present
	→ attach_rules on each practice

## Node / Edge

Same identifiers as the explorer UI: `node_id`, `semantic_type`, `source`, ordered `owns` and relationship kinds with `sequential_order` and `immediate` display hints.

Rule violations attach on nodes after populate; hooks and validate read those rule slugs.
