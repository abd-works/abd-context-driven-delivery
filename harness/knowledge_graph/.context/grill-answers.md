# Knowledge graph — grill answers

## Package location

**Q:** Where should the navigable graph types live, given harness must not import practices?

**A:** Put `knowledge_graph` under `practices/` so it can subclass the existing Clean Engineering and Stories nodes (`OoadNode`, `Module`, `OoadClass`, `Epic`, `SubEpic`, `Story`) directly. Not under `harness/`.

Grounded in `practices/clean_engineering/model/base_class_model.py`, `practices/stories/model/nodes.py`, `harness/.context/module-context.md`.

## First increment scope

**Q:** What populates increment 1 so Paradise navigation tests can be real?

**A:** A subset of My Paradise onboard: **Create Customer** and **Get Number**, plus the supporting Clean Engineering / DDD types those stories use. Later, a complete semantic model we can test against.

Not the full onboard epic (11 child epics on `stories/story-map.md`). Increment 1 child epics are `create-customer` and `get-number` only.

Grounded in `stories/onboard-a-customer/create-customer/`, `stories/onboard-a-customer/get-number/`, `domain/customer/Customer.ts` (`CustomerRepository.create` / `load`).

## Module is not a repository owner

**Correction:** `Module` does not have a `repository`. DDD adds two **Module** subtypes: **Bounded Context** (language boundary) and **Aggregate** (consistency cluster). An Aggregate must have a known **root** Entity. **Repository** is a **Class** that lives in the Aggregate when that root has an independent collection lifecycle — not a field on Module.

**Class subtypes:** Entity (identity that outlives attributes), Entity Root (Entity that is the Aggregate’s only entry — same identity rule; `aggregate` link is the only difference), Value Object, Repository, Domain Event, Domain Service.

## Cross-module class dependencies

**A:** `Property — hasType — Class`, `Parameter — hasType — Class`, `Operation — returns — Class`, and `Operation — invokes — Operation` are first-class edges. Emit `Class — dependsOn — Class` when any of those reach a Class in another Module; roll up to Module. Same-module refs use `Class — associates — Class`. CodeQL populates types, params, returns, and call graph.

## Practice graph, not parallel guidelines

**A:** One `PracticeGraph`; every node is a `GraphNode` and a practice instance. Every edge is a `GraphRelationship` with explicit **from**, **kind**, and **to** — e.g. `Step — invokes — Operation`, not a one-sided field on Step alone. `usedBy` is the reverse index on `GraphNode`.

Grounded in `practices/ddd/guidance/building_blocks.md`, `practices/ddd/templates/ddd-sketch.md`, `domain/bounded-context-map.md` (`Customer` BC holds Customer, Cart, …; `Inventory` holds Porting).

## Story and BDD depth

**Correction:** The graph includes the Stories tree below Story: **Scenario**, **Background**, **Step** (existing `Clause`), **Example**. BDD has its own tree: **Description** (`describe`), **Context** (`that` / `with`), **Observation** (`it should`). The important work is the edges that join Stories, CE, DDD, and BDD — not four disconnected trees.

Grounded in `practices/stories/model/scenario.py`, `practices/bdd/bdd.md`, `gwt-steps-trace-to-domain-operations`.

## Guidance rules on graph nodes

**Q:** How do practice guidance rules attach to the unified graph?

**A:** Every node is subject to rules **directly** (rule `applies_to` matches the node type at a fidelity) or **through a parent** (inherited scope). Each practice has **shared rules** plus **fidelity-specific rules**; fidelity narrows which node types are in scope — e.g. `scenarios` → Scenario/Step/Example; `acceptance_tests` → Step with `Step — invokes — Operation`; `building_blocks` → Repository/Entity with DDD edges.

**Query surface (sketch):** `node.rules.violations` (all applicable); `node.rules.direct.violations` (closest practice+fidelity match); `node.rules.practice(p).fidelity(f).violations` (filtered).

**Evaluation:** Rules are graph/CodeQL predicates over the loaded practice graph — not per-file scanner re-parses. CodeQL supplies calls/mutations; the graph supplies practice identity and cross-practice edges. See `knowledge-graph-sketch.md` § Guidance rules on nodes.
