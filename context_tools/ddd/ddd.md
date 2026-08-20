# Instructions

Apply **DDD** — bounded contexts, aggregates, building blocks — on top of **clean_engineering**.

**`clean_engineering`** owns OO structure (modules → model → specification → code; language is a companion). Do not restate class/module analysis here. DDD starts at **bounded_context**: context maps, aggregates, then stereotypes and tactics.

Each fidelity below is the whole story for that level. Call clean_engineering at the mapped fidelity. Do not fill details from a more detailed fidelity.

| Fidelity | clean_engineering |
|---|---|
| **bounded_context** | **modules** |
| **building_blocks** | **model** |
| **tactics** | **code** |

---
# Contexts



## bounded_context

**Default format:** markdown

**Goal:** Draw context boundaries, dependency arcs, and the aggregates that protect invariants — naming everything in the experts' vocabulary.

A **bounded context** is the boundary of **one model and one ubiquitous language** — owning team and codebase / deployable. Inside it, every term has one meaning. Across it, the same word may mean different things.

An **aggregate** is not a context. It is a **consistency** cluster *inside* a context: one root, a boundary, the invariants that boundary protects. Several aggregates that share the same language live in the **same** context (Catalog can hold Plan, Offer, …). Do **not** mint a bounded context per aggregate — that is a class with a fence around it, not a model boundary.

Failure modes: **duplicate concepts** (same real-world thing modeled twice); **false cognates** (same term, different meaning); **one-aggregate contexts** (every root wrapped as its own BC).

**Context map:** identify contexts → name them → describe contact points with translation.

**What gets tracked on a dependency:** direction (upstream/downstream/mutual, naming both sides); what crosses (concepts + translation); how they integrate — name the concrete mechanism and call site (e.g. synchronous call to `Catalog.Product.unit_price` at `add_item`, domain event `PriceChanged`, nightly batch extract). Categories like Events / Messaging / REST/API / Batch / Shared DB / File Transfer / Shared Kernel help, but "in-process" or "module seam" alone is not enough; relationship pattern from the catalogue below. Undecided items get owner + target date.

**Patterns:** Shared Kernel (shared subset, consult on change); Customer/Supplier (one-way, joint acceptance tests); Conformist (downstream adopts upstream); Anticorruption Layer (translate/isolate legacy); Open Host / Published Language (published protocol); Separate Ways (no integration). No ad hoc labels like "loose coupling."

**Boundary heuristics:** split a context when language, team, or model actually diverges — not when you add another aggregate. Size ~ten people upper bound; external systems usually Separate Ways / Conformist / ACL; formalize informal internal sharing; transform boundaries with clear current/end state.

An **Aggregate** is decided **inside** the context already named. Cluster for **one transaction / one invariant set**, not relatedness; keep aggregates small. Ask: what must be consistent in one transaction? what can tolerate lag? cost of brief inconsistency? who is the single access point (root)?

**Cross-aggregate:** when roots reference by ID — if A changes, does B need to know and how soon (immediate / eventual / snapshot)? copy or reference? what does the business do today? Outside the boundary, only through the root.

**Input traps:** hidden coupling; ownership ambiguity; false cognates; missing unnamed contexts; unclear direction; a new BC for each aggregate.

**Produce:** one `bounded-context-map.md` — inventory, dependencies, aggregates per context (root, members, invariants, cross-agg consistency); every inventoried context on an arc or declared standalone. Fill `templates/bounded-context-template.md`. Call clean_engineering at **modules**.

**Rules:**

- **`experts-words-preferred`** — Prefer the words domain experts use; do not invent technical synonyms when a domain word already exists.
- **`domain-concepts-not-technical-names`** — Every class/module names a domain concept (or honest boundary collaborator). Reject `Manager`, `Helper`, `Processor`, and similar layer names.
- **`one-meaning-per-context`** — Inside a context, one definition per term; false cognates across contexts are named and translated. The context is that language boundary. Aggregates are consistency clusters inside it — several per context is normal. Do not wrap each aggregate in its own bounded context.
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
| **Service** | Rare **doer** — only when the operation cannot sit cleanly on a single domain object. Not SOA / application `FooService`. |
| **Domain Event** | Significant past-tense moment — trigger and consumers as invariants; payload as properties. Facts, not commands. |
| **Specification** | Named, reusable true/false business rule (query / validate / construct)? |

Honour aggregate boundaries from bounded_context; do not redraw by relatedness. Same class shape as clean_engineering — stereotypes layered on. Every source concept classified (or Unresolved) with supporting model content.

**Input traps:** identity by habit; aggregate redrawn by relatedness; VO as Entity; `*Service` as a verb bag (SOA); silent consistency.

**Produce:** Update `bounded-context-map.md` — CE compact blocks + stereotypes under each owning context (`templates/bounded-context-template.md`). Call clean_engineering at **specification**. No tables, brokers, frameworks, or REST endpoints here — infrastructure at **tactics**.

**Rules:**

- **`identity-test-entity-vs-vo`** — Entity vs VO by identity that transcends attributes; prefer Value Object.
- **`every-concept-classified`** — Every source concept classified with supporting model content (or Unresolved); multiple stereotypes per concept are fine.
- **`service-is-homeless`** — DDD Service = a **doer**, and they are **rare**. Use one only when the operation cannot sit cleanly on a single domain object. Not SOA: do not invent `FooService` to park verbs. If `Customer` signs in, that is `Customer.signIn`.
- **`domain-events-past-tense`** — Past-tense domain name; trigger and consumers as invariants; not commands or infra names.
- **`no-premature-infrastructure`** — Design intent only: no tables, brokers, framework annotations, or endpoints.
- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class name at building_blocks carries a tactical tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, `<<Repository>>`, `<<Factory>>`, `<<Service>>`, `<<Domain Event>>`, `<<Specification>>`). Bare names are incomplete.
- **`flaccid-data-object-no-behavior`** — A type is not a field bag. Give it the operations that are **its** work. Select / port / checkout live on the aggregate that does them, not on a repository. Do not hang someone else’s verbs on a value so it “has behavior” (credentials does not grow `signIn`).
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screen drivers are not domain objects. The user action is an operation on the aggregate that owns it.
- **`private-method-naming`** — Public operations use `+` and no leading `_`. Private helpers use `-` and a `_` prefix (e.g. `- _deriveOnboardingStep`). `derive*` helpers are private.
- **`no-orphaned-objects`** — Every domain object has at least one relationship (dependency, composition, or association). Unconnected Credentials/Session-style boxes are incomplete.

---

## tactics

**Default format:** Python

**Goal:** Implement the domain and building-block seams (repos, events, factories, …) against a chosen architecture.

- Preserve names from the CE / building-blocks model.
- Implement repository persistence, event publication/handling, factories, services as decided upstream.
- **Architecture** — from project context (`.context/`, ADRs, stack). If none, **ask**. If none available, default: Node-shaped app + **JSON file persistence** (package TBD).
- Domain model free of UI/transport; persistence and messaging behind ports.
- Call clean_engineering at **code**.

---

# Scaffold

**Produce:** thin bounded context index — **names only**: context name + candidate aggregates + short ubiquitous-language note (`DomainMap` → `BoundedContext` → `Aggregate`). No BuildingBlock at scaffold.

Key rules: `language-is-context-scoped` — a term’s meaning is only valid inside the context that defines it; the same word in two contexts is two different concepts.

---

# Default folder

`default_workspace_folder` is `src/` for **generate**. `/document` calls `apply_document_workspace_default`: working area becomes `domain/` unless `path` was passed or `default_workspace_folder` was already overwritten. Clean Engineering does not choose this folder; `ce()` follows DDD's working path.

---

# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

When documenting an existing system, tactical wraps live under the DDD working area (`domain/` by default, overridable via `path` or `default_workspace_folder`) as `{bounded-context}/{aggregate}/` (`{class}.ts` + `{class}.{tier}.ts` + `stubs/{system}/`). Leave production `src/` alone. Generate / greenfield work may still use `src/`.

---

# Generate

1. Confirm fidelity (`bounded_context` → `building_blocks` → `tactics`) and format.
2. Read the active fidelity section above (including its Rules). Do not re-author CE OO theory.
3. Use peer actions when useful (`grill`, `sketch`, `iterate`; `templates/ddd-sketch.md`).
4. Fill / deepen `bounded-context-map.md`; at **tactics**, resolve architecture first.
5. Call clean_engineering at the mapped fidelity (`generate_output`).
6. Run **validate**.
