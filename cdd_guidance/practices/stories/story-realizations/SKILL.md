# Story Realizations Skill

**Purpose:** Turn a set of story scenarios into scenario realization documents — one Markdown file per scope — that write, after each Given group and each When group, the code-like statements the code runs for those steps, showing how objects and external systems collaborate to produce observable outcomes.

**Format references:**
- Scenario structure and fidelity: `@practices/stories/stories.md` `#scenarios` — GWT plus **Scenario realizations (default on)** unless the user says **no realizations**.
- Acceptance tests: `@practices/stories/stories.md` `#acceptance_tests` — implement through the realized call graph.
- BDD: `@practices/bdd/bdd.md` `#realization` — the same notation on each `it should` of the spec files, in its own `{scope}-bdd-realization.md`. A scenario realization follows the story map's Scenarios; a BDD realization follows the spec files' observations. Keep them in separate files, because a reader has to know which one a graph realizes.
- Interaction notation: `@practices/clean_engineering/clean_engineering.md` — `write-interactions`; arrows round-trip via `practices/source_code/call_graph.py` and the stories/BDD model channels.

---

## What a scenario realization is

A scenario realization is a hybrid artifact. It keeps the Given/When/Then skeleton of a scenario so readers can follow the business story, and after each Given group and each When group it writes, as code-like statements, what the code does for those steps: the Givens' block builds the state they describe, and the When's block runs the operation under test.

It sits at **sketch fidelity**: method signatures, collaborator calls, and system boundaries — no bodies, no implementation detail, no framework plumbing.

**What it shows:**
- The statements of the flow: each object named once with a variable, each constructor with the parameters the code's constructor takes, and each repository call as a statement of its own.
- Every domain object and named external system that participates in the step.
- The chain of calls across those participants — the full call graph for each step, not just the entry point.
- Return values that matter to the caller above.
- The direction of each call and its response.

**What it does not show:**
- TypeScript or language-native code (array methods, string formatting, type guards, etc.).
- Private helper functions whose only job is readability or code organization — strip these and show the underlying domain call they delegate to.
- Framework machinery (routing, serialization, middleware, dependency injection wiring).
- Internal state assignments that have no collaborator on the other side.
- Sentences about state (`<- an empty cart: no lines`, `<- nothing stored`): a realization is statements, and a Given that sets up nothing has no block.
- Test helpers (`seedPlanCatalog`): name the repository or aggregate operation the seed reaches (`CartRepository.create(cart)`).

---

## Statement notation

Each block is the flow the step group runs, one statement per line, in the order the code runs them:

```
// the Customer has an empty Cart
cart = new Cart(customerProfile)
CartRepository.create(cart)
```

```
cart = CartRepository.load(cartId)
plan = PlanRepository.loadByName(Atlas)
line = cart.addLine(plan)
  -> plan.priceFor(customerProfile)
CartRepository.update(cart)
```

- **Name each object once with a variable** (`cart = new Cart(customerProfile)`) and use the variable afterwards, so the reader follows one object from statement to statement.
- **Spell out constructors and factories with the parameters the code's constructor takes**, because those set up the object's dependencies.
- **Only the flow calls repositories**, each as a statement of its own at the top level: load the aggregate, call the domain operation, store the aggregate back. A domain object never calls a repository, its own or another aggregate's; one aggregate holds another by its id and is handed that aggregate's root (`cart.addLine(plan)`). The rule `repositories-called-only-by-the-flow` reports a repository call written under a domain operation.
- **Indent under a statement what a domain operation calls in turn**, one level per call depth, with `->`. External systems are labelled at the call site: `-> [ExternalSystem] operation(args)`.
- **Use `<- ` only for a returned value the next statements use** that no variable already names; never for a sentence about state.
- **Put `// <the Given line's words>` before each Given line's statements**, so a reader can tell which statements build which Given.
- **Name the repository or aggregate operation a seed reaches**, never a test helper.

## Output format

Produce one Markdown file per scope (story, sub-epic, or explicit grouping the user names): `.context/{scope-kebab-case}-scenario-realization.md`.

```markdown
# Scenario Realizations: {Scope Name}

Source: {story file path or scenario file path}

---

## {Story Name}

### Scenario: {Scenario Name}

**Given** {precondition in plain domain terms}
  — {additional state if needed, root-first per `given-names-complex-state-root-first`}

{givenStatements}

**When** {actor performs domain intent}

{whenStatements}

**Then** {observable outcome in domain terms}
  — {additional observable outcome}

---
```

Write each block in the statement notation above. A Given block builds the state its Givens describe through the constructors and repository operations the code uses. A When block begins with the flow's loads, then the outermost method the story step maps to — the entry point on the public seam — then the stores. Strip wrapper and adapter calls that exist only to simplify code; follow the chain until you reach either a leaf domain operation or a named external system boundary.

When a Then step itself triggers observable downstream behaviour (a system call, a persisted state change, a domain event), expand that too, because `behavioral-and-system-observable-outcomes` requires you to name what a person or another system can observe.

---

## Procedure

1. **Identify the scope.** Accept a story name, sub-epic, folder path, or spec file as the scope. When the user names a folder, include every story file inside it.

2. **Read the scenarios and the Clean Engineering model in full.** For each story in scope, read its scenario file. Read the Clean Engineering model the scenarios' domain terms link to (`{module}/.context/*-model.md`): every operation, its signature, and the `->` interactions under it. The model is where each operation's collaborators are written down, so the call graph comes from it rather than from re-reading the code.

3. **Find the operation each Given and When starts from.** Load the knowledge graph for the scope (`graph.load_files` with `stories` and `clean_engineering`). Each step's `invokes` edges name the operations its acceptance test calls, matched to the code's classes. The first operation a When invokes is the root of its call graph; a Given's statements are the constructors and the repository operations its seed reaches. When that operation is a test helper, start from the domain operation the helper calls, because the helper only sets up the call.

4. **Walk the call graph through the model.** Under the root, write each `->` interaction the model lists for that operation, then each of those operations' interactions in turn. Name a returned value with a variable (`line = cart.addLine(plan)`) when the next statements use it, and leave it out otherwise. A repository interaction the model lists under a domain operation belongs to the flow: write it as a statement of its own above or below the operation, and add a note to fix the model, because a domain object that calls a repository breaks `repositories-called-only-by-the-flow`:
   - Stop at an operation the model gives no interactions; it finishes its job from its own state.
   - Stop at an external system: label the call `[ExternalSystem]` and do not recurse into it.
   - When the model leaves out an interaction the code makes, the model is incomplete. Add the interaction to the model first, then draw it, because a realization that disagrees with the model leaves two descriptions of one design.

5. **Write the realization.** For each scenario:
   - Copy the Given, When and Then text in plain domain language.
   - After each Given group, a Background's Givens included, write the statements that build its state, each Given line's statements after a `//` comment of its words. A Given that sets up nothing has no block.
   - After each When group, write the statements of the flow that runs it.
   - Expand any Then step that itself produces an observable collaborator call or system side effect.

6. **Name everything from the domain model.** Every object name, operation name, and system name must trace to the source code or domain model. Do not invent synonyms. Follow `vocabulary-traces-to-source`.

7. **Write the output file.** Write `.context/{scope-kebab-case}-scenario-realization.md` in the module the scenarios belong to, or the location the user names. One file per scope.

---

## Rules

- **`strip-helpers-to-domain-calls`** — Remove any function whose body is a single domain call or a delegation. Show the domain call directly at the parent's indent level. A helper that exists only to shorten the call site adds a level of indentation without adding a participant.
- **`full-call-graph-per-step`** — Follow the call graph from the outermost operation to every named domain or external-system collaborator it reaches. Do not stop at the first level. The reader must be able to trace the entire step without reading source code.
- **`external-systems-at-their-boundary`** — Show an external system at the call the domain model makes to it. Do not show what the external system does internally. Label it `[ExternalSystem]` so the boundary is visible.
- **`no-typescript-internals`** — Do not show TypeScript-native operations (array iteration, string methods, type guards, promises) unless the step has no domain collaborator. If the step is entirely infrastructure, name the infrastructure boundary and stop.
- **`repositories-called-only-by-the-flow`** — Call each repository from the flow, as a statement of its own at the top of the block; never under a domain operation. Hand the operation the aggregate root the flow loaded.
- **`gwt-steps-trace-to-domain-operations`** — Every Given, When and Then traces to a named domain operation or property on the domain model. Use the same vocabulary the code uses. Follow `gwt-steps-trace-to-domain-operations` from stories.md.
- **`sketch-fidelity`** — Signatures only. No bodies, no implementation detail, no framework annotations. The reader should be able to see the call graph structure in one pass without drowning in detail.
- **`one-file-per-scope`** — Write one output file per scope. When a scope contains many stories, group them in the same file under separate `## {Story Name}` headings.
