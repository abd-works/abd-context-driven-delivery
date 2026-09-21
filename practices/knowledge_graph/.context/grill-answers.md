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

**A:** `Class.externalClasses` lists every class dependency whose home module is another module. `Module.externalClasses` is the deduped rollup from owned classes. Same-module refs stay on `relationships`. CodeQL populates both from imports, types, and call graph.

## Practice graph, not parallel guidelines

**A:** One `PracticeGraph`; every node is a `GraphNode` (graph membership + `usedBy`) and a practice instance (`practice = clean_engineering | ddd | stories | bdd`). Cross-practice edges (`Step.invokes → Operation`, `Example.expresses → Class`, etc.) are first-class fields, not prose.

Grounded in `practices/ddd/guidance/building_blocks.md`, `practices/ddd/templates/ddd-sketch.md`, `domain/bounded-context-map.md` (`Customer` BC holds Customer, Cart, …; `Inventory` holds Porting).

## Story and BDD depth

**Correction:** The graph includes the Stories tree below Story: **Scenario**, **Background**, **Step** (existing `Clause`), **Example**. BDD has its own tree: **Description** (`describe`), **Context** (`that` / `with`), **Observation** (`it should`). The important work is the edges that join Stories, CE, DDD, and BDD — not four disconnected trees.

Grounded in `practices/stories/model/scenario.py`, `practices/bdd/bdd.md`, `gwt-steps-trace-to-domain-operations`.
