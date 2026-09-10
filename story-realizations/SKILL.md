# Story Realizations Skill

**Purpose:** Turn a set of story scenarios into scenario realization documents — one Markdown file per scope — that trace each Given/When/Then step down through the domain model's call graph and back, showing how objects and external systems collaborate to produce observable outcomes.

**Format references:**
- Scenario structure: `@context_tools/stories/stories.md` — the GWT step vocabulary and rules.
- Interaction notation: `@context_tools/clean_engineering/clean_engineering.md` — the `write-interactions` rule and model fidelity guidance.

---

## What a scenario realization is

A scenario realization is a hybrid artifact. It keeps the Given/When/Then skeleton of a scenario so readers can follow the business story, but inside each step it unfolds the call graph so readers can see how the domain model actually executes that step.

It sits at **sketch fidelity**: method signatures, collaborator calls, and system boundaries — no bodies, no implementation detail, no framework plumbing.

**What it shows:**
- Every domain object and named external system that participates in the step.
- The chain of calls across those participants — the full call graph for each step, not just the entry point.
- Return values that matter to the caller above.
- The direction of each call and its response.

**What it does not show:**
- TypeScript or language-native code (array methods, string formatting, type guards, etc.).
- Private helper functions whose only job is readability or code organization — strip these and show the underlying domain call they delegate to.
- Framework machinery (routing, serialization, middleware, dependency injection wiring).
- Internal state assignments that have no collaborator on the other side.

---

## Call graph notation

Each step expands into an indented call graph. Indent one level per call depth. Use arrows to show direction:

```
objectName.operation(args)
  → collaborator.operation(args)
      → deeperCollaborator.operation(args)
      ← result
  ← result
← result
```

- `→` outbound call to a collaborator or external system.
- `←` return value flowing back to the caller above.
- Named arguments when they name a domain concept worth tracing. Omit when the name adds nothing over the type.
- External systems (anything outside the domain model) are labelled at the call site: `[ExternalSystem] operation(args)`.

When a step is a pure state assertion (a Given precondition or a Then outcome), describe the state using domain terms rather than expanding a call graph — the graph applies to interactions, not to preconditions that already exist.

---

## Output format

Produce one Markdown file per scope (story, sub-epic, or explicit grouping the user names). Name it after the scope using kebab-case.

```markdown
# Scenario Realizations: {Scope Name}

Source: {story file path or scenario file path}

---

## {Story Name}

### Scenario: {Scenario Name}

**Given** {precondition in plain domain terms}
  — {additional state if needed, root-first per `given-names-complex-state-root-first`}

**When** {actor performs domain intent}

{callGraph}

**Then** {observable outcome in domain terms}
  — {additional observable outcome}

---
```

For the call graph block, use the notation above. Begin with the outermost method the story step maps to — the entry point on the public seam. Strip wrapper and adapter calls that exist only to simplify code; follow the chain until you reach either a leaf domain operation or a named external system boundary.

When a Then step itself triggers observable downstream behaviour (a system call, a persisted state change, a domain event), expand that too, because `behavioral-and-system-observable-outcomes` requires you to name what a person or another system can observe.

---

## Procedure

1. **Identify the scope.** Accept a story name, sub-epic, folder path, or spec file as the scope. When the user names a folder, include every story file inside it.

2. **Read source material in full.** For each story in scope:
   - Read the scenario file (`.md` or spec file).
   - Read the production code files the scenarios call — at minimum the entry point class and every domain class it touches across the call graph.
   - Read the relevant domain model files when they exist alongside the code.
   - Do not skim. A step that looks simple at the scenario level often fans out across several domain objects. You cannot draw the call graph from headings alone.

3. **Identify the outermost call for each When step.** In acceptance test specs, the When step is typically a call on a domain aggregate, service, or story entry-point class. That is the root of the call graph. If the spec uses a helper to set up the call, strip the helper and start from the real domain operation.

4. **Walk the call graph.** From the outermost call, follow every collaborator call the implementation makes:
   - Strip language-native calls (`.map`, `.filter`, `JSON.parse`, TypeScript utilities).
   - Strip private helpers that exist only to break up code; if a private helper calls a real domain operation, show the domain operation in place of the helper.
   - Stop at external system boundaries (repositories, gateways, external APIs). Name the boundary and the operation it exposes; do not recurse into external system internals.
   - Stop at TypeScript or framework library calls. Name the library operation at the boundary if it is semantically significant (e.g. an HTTP call, a database write), then stop.

5. **Write the realization.** For each scenario:
   - Copy the Given and Then text in plain domain language.
   - Expand the When step using the call graph notation.
   - Expand any Then step that itself produces an observable collaborator call or system side effect.

6. **Name everything from the domain model.** Every object name, operation name, and system name must trace to the source code or domain model. Do not invent synonyms. Follow `vocabulary-traces-to-source`.

7. **Write the output file.** Place it alongside the source scenarios unless the user specifies otherwise, or write it to the location the user names. One file per scope. Name it `{scope-kebab-case}-realization.md`.

---

## Rules

- **`strip-helpers-to-domain-calls`** — Remove any function whose body is a single domain call or a delegation. Show the domain call directly at the parent's indent level. A helper that exists only to shorten the call site adds a level of indentation without adding a participant.
- **`full-call-graph-per-step`** — Follow the call graph from the outermost operation to every named domain or external-system collaborator it reaches. Do not stop at the first level. The reader must be able to trace the entire step without reading source code.
- **`external-systems-at-their-boundary`** — Show an external system at the call the domain model makes to it. Do not show what the external system does internally. Label it `[ExternalSystem]` so the boundary is visible.
- **`no-typescript-internals`** — Do not show TypeScript-native operations (array iteration, string methods, type guards, promises) unless the step has no domain collaborator. If the step is entirely infrastructure, name the infrastructure boundary and stop.
- **`gwt-steps-trace-to-domain-operations`** — Every When and Then traces to a named domain operation or property on the domain model. Use the same vocabulary the code uses. Follow `gwt-steps-trace-to-domain-operations` from stories.md.
- **`sketch-fidelity`** — Signatures only. No bodies, no implementation detail, no framework annotations. The reader should be able to see the call graph structure in one pass without drowning in detail.
- **`one-file-per-scope`** — Write one output file per scope. When a scope contains many stories, group them in the same file under separate `## {Story Name}` headings.
