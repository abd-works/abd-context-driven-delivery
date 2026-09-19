## Overview

Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.

**`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`building_blocks`** classifies concepts with stereotypes; **`clean_engineering-code`** implements the seams when **`tactics`** wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and what each concept actually is.

---

When this DDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

## Shared rules

Use these rules when defining domain logic in code, a model, or language.

- **`ubiquitous-language-everywhere`** — One term per concept, taken from the business, used identically on the map, in the model, in the code, and in the tests. A technical synonym makes every reader keep a translation in their head, and the two names drift until they mean different things.
- **`model-the-domain-not-the-implementation`** — Model what the business does, not what the current database, screens, or vendor API expose. A model shaped by an existing implementation locks in decisions nobody chose on purpose.
- **`vocabulary-traces-to-domain-source`** — Trace every term back to domain experts or an upstream artifact. Invent a word and each layer keeps its own glossary.
- **`read-all-source-context-in-full`** — Before locking a context boundary or aggregate, read every referenced segment, sketch, grill-answer, and handoff in full. Titles and indexes show words, not mechanics; a boundary drawn from headings alone misses coupling that shows up only in the prose.
- **`do-not-invent-concepts`** — Only model contexts, aggregates, and types the source describes or the user explicitly asks for. Invented contexts and DTO-shaped nouns become code nobody asked for and integrations nobody planned.

---

#### Overview


**Default format:** Python
**Stage:** implementation

**Goal:** Decide one implementation pattern for each building block the model uses, then implement the domain against it — preserving every name and boundary from upstream.

**Produce:** Implementation under the project layout; call clean_engineering at **code**.

#### Guidance

**Read the project's architecture before deciding anything.** Check project context (`.context/`, ADRs, stack). If none exists, ask. If nothing is available, default to a Node-shaped app with JSON file persistence (package TBD).

**Decide one implementation pattern per building block, then apply it everywhere that block appears.** Work through the blocks the model actually uses — not every solution uses all of them — and settle for each: what technology backs it, how you extend or wrap that technology, and how it is tested. With the pattern fixed, going from model to implementation is a mechanical translation — the model says `<<Repository>>` and the pattern says exactly what that becomes. Without it, every instance is a fresh design problem invented from scratch, and nothing about the model tells you what the code should look like.

**Settle the architectural granularity in the same pass.** Decide whether a bounded context is an in-process module, a deployed container, or a service, and decide whether an aggregate and Repository are in-process objects or sit behind a service and its own store. For example, a Repository backed by MongoDB and service calls has different runtime and test costs from an in-memory collection. Make the choice explicitly before implementation sets it by accident.

**Preserve names and boundaries from the map and model.** Tactics is where repositories persist, events publish, and factories run — not where you rename concepts to match a framework tutorial.

**Keep the domain free of UI and transport.** Persistence and messaging sit behind ports; the domain types do not import screens or HTTP clients.

**Load with the identity already in hand** when wrapping live code. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.

#### Rules

Use these rules when choosing how a repository, event, or factory is stored, published, and tested, then writing that implementation.

- **`one-pattern-per-building-block`** — Each building block in play gets one named implementation pattern — technology, extension mechanism, test approach — used by every instance of that block. Divergent implementations of the same block make the solution unreadable and untestable as a whole.
- **`architectural-granularity-decided`** — State what a bounded context, an aggregate, and a repository are at runtime (in-process module, container, service with its own store). Left undecided, the first adapter written silently sets it for everything after.
- **`preserve-upstream-names`** — Public API names match the building_blocks model. Renaming here breaks traceability back to the map and the stories.
- **`load-with-identity-in-hand`** — A live `load` takes the identity already in hand. Do not assume ambient session state. Reach owned aggregates through their owner.
- **`ports-behind-adapters`** — Persistence, messaging, and external systems integrate through ports — not direct imports from the domain core.
