---
description: "Whenever you create, alter, or delete bounded contexts, aggregates, or the language between them, or change a model or code that forces a language-boundary change. Follow these rules."
paths:
  - "**/*bounded-context*"
  - "**/*-sketch.md"
---

#### Rules



Whenever you create, alter, or delete bounded contexts, aggregates, or the language between them, or change a model or code that forces a language-boundary change. Follow these rules.

- **`experts-words-preferred`** — Use the words domain experts use. An invented synonym becomes a second term every reader must translate.
- **`domain-concepts-not-technical-names`** — Name contexts, aggregates, and concepts — not `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, or `*Request`. Do not invent a type for fields that already belong on a concept. A technical name carries no meaning the business would recognize, so rules parked on it cannot be found where the concept lives and get re-implemented elsewhere.
- **`bc-by-lifecycle-not-ui-themes`** — Partition by ubiquitous language and how fast the model changes, not by UI themes or journey stages. Do not mint journey-themed contexts that duplicate core domain contexts. Screens and journeys are redrawn while language boundaries hold; a boundary cut along the UI has to move with every redesign and drags the model with it.
- **`one-meaning-per-context`** — Inside a context, one definition per term; name and translate false cognates across contexts. Several aggregates per context is normal. Do not wrap each aggregate in its own bounded context. Two meanings under one word become contradictory code that both looks consistent; a context per aggregate walls one language off from itself and charges integration cost for nothing.
- **`bc-above-aggregate`** — A bounded context names a business area, department, or system collection with its own ubiquitous language — not a single aggregate. If the only candidate context is one aggregate, nest it under a broader context or record it as an **Integrations:** arc; omit the `###` heading. No real language boundary is better than a heading that merely duplicates an aggregate name.
- **`one-module-per-context-when-small`** — A consolidated custom context with only a handful of collaborating types is one clean-engineering module, not one package per aggregate or per class. Several entities under one `#### {module}/` is normal; four modules for four classes in the same context is the packaging version of `bc-above-aggregate`.
- **`aggregate-clusters-entities`** — An aggregate is a consistency cluster with a chosen root and the entities inside it — not one `####` heading per entity class. Several `#####` entities under one aggregate is normal; five aggregates for five account types that share one customer file is the same mistake at a finer grain.
- **`integrations-cross-context-only`** — **Integrations:** arcs cross a bounded-context boundary only. Another entity or aggregate in the same context is a property on the type that uses it — not an integration.
- **`dependency-fields-tracked`** — Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc that names only a neighbor context does not tell anyone what to build.
- **`no-orphan-contexts`** — Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.
- **`vendor-not-implementation`** — The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere, because they can change while the domain meaning remains stable.
- **`context-tree-bc-aggregate-concept`** — Three levels on the bounded_context card only: BC → Aggregate → concept. Classes, stereotypes, and repositories wait for **model**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.
- **`bounded-context-file-marks-the-folder`** — In code, a bounded context is the folder that contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and each aggregate folder under it. A folder of classes with no such file is a module or a package, so the map and the tree disagree about where the language boundary is.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.
- **`user-facing-system-first`** — The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

---