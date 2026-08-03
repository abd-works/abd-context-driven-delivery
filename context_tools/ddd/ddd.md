# Instructions

Apply **DDD** — bounded contexts, aggregates, building blocks — on top of **clean_engineering**.

**`clean_engineering`** owns OO structure (modules → model → specification → code; language is a companion). Do not restate class/module analysis here. DDD starts at **bounded_context**: context maps, aggregates, then stereotypes and code.

Each fidelity below is the whole story for that level. Call clean_engineering at the mapped fidelity. Do not fill details from a more detailed fidelity.

| Fidelity | clean_engineering |
|---|---|
| **bounded_context** | **modules** |
| **building_blocks** | **model** |
| **code** | **code** |

---
# Contexts



## bounded_context

**Default format:** markdown

**Goal:** Draw context boundaries, dependency arcs, and the aggregates that protect invariants — naming everything in the experts' vocabulary.

A **bounded context** is an explicitly set boundary in which a model applies and is managed to be uniform — organizational (owning team) and implementation (codebase / deployable). Within it, every term has one meaning. Across boundaries, the same word may mean different things.

Failure modes: **duplicate concepts** (same real-world thing modeled twice) and **false cognates** (same term, different meaning).

**Context map:** identify contexts → name them → describe contact points with translation.

**What gets tracked on a dependency:** direction (upstream/downstream/mutual, naming both sides); what crosses (concepts + translation); how they integrate — name the concrete mechanism and call site (e.g. synchronous call to `Catalog.Product.unit_price` at `add_item`, domain event `PriceChanged`, nightly batch extract). Categories like Events / Messaging / REST/API / Batch / Shared DB / File Transfer / Shared Kernel help, but "in-process" or "module seam" alone is not enough; relationship pattern from the catalogue below. Undecided items get owner + target date.

**Patterns:** Shared Kernel (shared subset, consult on change); Customer/Supplier (one-way, joint acceptance tests); Conformist (downstream adopts upstream); Anticorruption Layer (translate/isolate legacy); Open Host / Published Language (published protocol); Separate Ways (no integration). No ad hoc labels like "loose coupling."

**Boundary heuristics:** larger vs smaller (~ten people upper bound); external systems usually Separate Ways / Conformist / ACL; formalize informal internal sharing; transform boundaries with clear current/end state.

An **Aggregate** is a cluster treated as a single unit for data changes — one **root** Entity, a **boundary**, and the invariants that boundary protects. Decide aggregates here, with context_tools. Boundaries exist for invariant protection, not relatedness; keep aggregates small.

Ask: what must be consistent in one transaction? what can tolerate lag? cost of brief inconsistency? who is the single access point (root)?

**Cross-aggregate:** when roots reference by ID — if A changes, does B need to know and how soon (immediate / eventual / snapshot)? copy or reference? what does the business do today? Outside the boundary, only through the root.

**Input traps:** hidden coupling; ownership ambiguity; false cognates; missing unnamed contexts; unclear direction.

**Produce:** one `bounded-context-map.md` — inventory, dependencies, aggregates per context (root, members, invariants, cross-agg consistency); every inventoried context on an arc or declared standalone. Fill `templates/bounded-context-template.md`. Call clean_engineering at **modules**.

**Rules:**

- **`experts-words-preferred`** — Prefer the words domain experts use; do not invent technical synonyms when a domain word already exists.
- **`domain-concepts-not-technical-names`** — Every class/module names a domain concept (or honest boundary collaborator). Reject `Manager`, `Helper`, `Processor`, and similar layer names.
- **`one-meaning-per-context`** — Inside a context, one definition per term; false cognates across contexts are named and translated.
- **`dependency-fields-tracked`** — Every arc states direction (named sides or mutual), what crosses, how they integrate (concrete mechanism), and catalogue relationship pattern — or a dated follow-up with owner.
- **`no-orphan-contexts`** — Every inventoried context appears in a dependency arc or is declared standalone with rationale.
- **`aggregate-protects-invariants`** — Name root, members, and the business invariants that require the boundary; do not cluster by relatedness alone.
- **`invariants-from-business-logic`** — Invariants come from domain rules and expert statements, not convenient code shape.

---

## building_blocks

**Default format:** markdown

**Goal:** Deepen the same context map — under each owning context, add CE compact class detail with DDD stereotypes. Not a separate BB document; added detail on the aggregates already placed in the BC.

| Stereotype | Business question |
|---|---|
| **Entity** | Can we tell them apart over time when attributes change? Identity transcends attributes — not "importance." |
| **Value Object** | Fully described by values — interchangeable, replaceable, immutable? Prefer VO unless tracked identity is required. |
| **Repository** | How does the business find, store, and retire this aggregate? Collection-style seam only here. |
| **Factory** | Complex birth / invariants at creation / subtype choice? |
| **Service** | Homeless operation — placing it on a concept would distort that concept? Stateless, domain-named. |
| **Domain Event** | Significant past-tense moment — trigger and consumers as invariants; payload as properties. Facts, not commands. |
| **Specification** | Named, reusable true/false business rule (query / validate / construct)? |

Honour aggregate boundaries from bounded_context; do not redraw by relatedness. Same class shape as clean_engineering — stereotypes layered on. Every source concept classified (or Unresolved) with supporting model content.

**Input traps:** identity by habit; aggregate redrawn by relatedness; VO as Entity; Service as dump; silent consistency.

**Produce:** Update `bounded-context-map.md` — CE compact blocks + stereotypes under each owning context (`templates/bounded-context-template.md`). Call clean_engineering at **specification**. No tables, brokers, frameworks, or REST endpoints here — infrastructure at **code**.

**Rules:**

- **`identity-test-entity-vs-vo`** — Entity vs VO by identity that transcends attributes; prefer Value Object.
- **`every-concept-classified`** — Every source concept classified with supporting model content (or Unresolved); multiple stereotypes per concept are fine.
- **`service-is-homeless`** — Service only when no concept can own the operation without distortion; domain-named, typically stateless.
- **`domain-events-past-tense`** — Past-tense domain name; trigger and consumers as invariants; not commands or infra names.
- **`no-premature-infrastructure`** — Design intent only: no tables, brokers, framework annotations, or endpoints.

---

## code

**Default format:** Python

**Goal:** Implement the domain and building-block seams (repos, events, factories, …) against a chosen architecture.

- Preserve names from the CE / building-blocks model.
- Implement repository persistence, event publication/handling, factories, services as decided upstream.
- **Architecture** — from project context (`.context/`, ADRs, stack). If none, **ask**. If none available, default: Node-shaped app + **JSON file persistence** (package TBD).
- Domain model free of UI/transport; persistence and messaging behind ports.
- Call clean_engineering at **code**.

---

# Scaffold

**Produce:** thin bounded context index — context name + candidate aggregates + short ubiquitous-language note (`DomainMap` → `BoundedContext` → `Aggregate` → `BuildingBlock`).

Key rules: `language-is-context-scoped` — a term’s meaning is only valid inside the context that defines it; the same word in two contexts is two different concepts.

---


# Generate

1. Confirm fidelity (`bounded_context` → `building_blocks` → `code`) and format.
2. Read the active fidelity section above (including its Rules). Do not re-author CE OO theory.
3. Use peer actions when useful (`grill`, `sketch`, `iterate`; `templates/ddd-sketch.md`).
4. Fill / deepen `bounded-context-map.md`; at **code**, resolve architecture first.
5. Call clean_engineering at the mapped fidelity (`generate_output`).
6. Run **validate**.
