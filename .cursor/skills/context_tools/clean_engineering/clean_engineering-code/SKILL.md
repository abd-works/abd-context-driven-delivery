---
name: clean_engineering-code
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

# clean_engineering-code

Use clean_engineering guidance at `code` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@clean_engineering-model
@clean_engineering-modules

# Contexts

Deepen OO design from modules toward production code. Each fidelity **adds** artifacts — do not invent detail from a deeper level.

**Progression:** `partition` (action) → **modules** (scaffold → full map) → **model** → **code**.

| Fidelity | Default format | Produce |
|---|---|---|
| **modules** | markdown (+ drawio) | Independent modules, one-way deps, build order, thin seam terms |
| **model** | python | Empty public seam (on `Class` directly by default, or on a separate `I{Class}` contract **only when interfaces are explicitly requested**) + full module-context; stub example factories |
| **code** | python | Typed contracts (`Class(I{Class})` when an interface was requested, otherwise `Class` directly) → full production implementation |

**Interfaces (`I{Class}`) are optional, not automatic.** See `## model` § Interfaces for the trigger — ask for one, or a genuine multi-layer/multi-implementation seam.

---

## Language companion (not a fidelity)

**Language is not invocable** (`context.fidelity: language` is rejected). Natural-language identity is a **companion** that deepens at every stage through code.

- At each fidelity, refresh prose for terms/classes already named at that stage — definition, story bullets, invariants in plain English.
- Keep identity on the class (or `## ClassName` section); member bullets move onto members as model/code deepen.
- Do **not** invent types, method bodies, relationship kinds, or Public API ahead of the active fidelity.
- Prose lives under `{session}/{module}/` (markdown sections and/or class docstrings) and is updated in place — never a separate language-only generate run.

---

## code

**Default format:** Python

**Goal:** Two phases in one fidelity — first lock down the typed contracts (`Class(I{Class})` when an interface was requested at model, otherwise the `Class` stub already in place from model), then wire the full production implementation. When an `I{Class}` exists it stays as the stable seam throughout; when it does not, `Class` itself is the seam.

A vertical is not at **code** fidelity while it still depends on a mockup / Story Demo shell as the only UI, or on in-memory / fake factories as the only "backend." **Code** means real backend **and** real frontend (UX **code** fidelity) — not greybox + demo domain alone.

### Phase 1 — typed contracts

- **Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific recommendations for coding.
- **When an `I{Class}` interface was requested at model** (interfaces are optional — see `## model` § Interfaces): add `Class(I{Class})` (Java: `implements I{Class}`) in the **same file** as `I{Class}`. Do **not** fill out `I{Class}` or add private members to it.
- **When no interface was requested:** skip that step — the empty `Class` stub already exists from **model** fidelity in its own family file; continue directly onto it.
- On `Class`: implement public properties and operations; add private properties/operations as **empty interfaces** (`...` / `@abstractmethod`); add each relationship with its **kind** (composition / aggregation / association) and **cardinality** (e.g. `1..*`, `0..1`); invariants as **comments** (not methods) — formalizing any named at `## model` § Invariants, or newly introduced here.
- Interactions: `@interaction` abstract methods on `Class` (never on `I{Class}`, whether or not one exists) — formalizing any named at `## model` § Interactions, or newly introduced here.
- Complete `{Type}ExampleFactory` — fill in Fake, Isolated, and Production modes per the **Example factories** pattern in `## model`.
- Refresh `.context/module-context.md` still **public-seam-only**: ensure **Public API**, **Constraint**, and **Dependencies** match the implemented seam; add **Extend** / **Mechanism** only for public variation points. **Do not** add **Participants**, **Internal design**, **Domain separation**, or any other internals section — those stay in source and sketches, never in module-context.
- Edit the same `.context/module-context.md` — do not create parallel context files.
- Edit so remaining language-companion bullets sit on members; class-level docstring keeps only the opening definition.


State which side **navigates** to the other — direction is explicit.

### Phase 2 — production implementation

- Fill all remaining empty bodies on `Class` (no `...`, no `# TODO` on production ops/props).
- Wire **Production** collaborators — real persistence, services, and cross-module dependencies — not Fake-mode stubs as the shipping path.
- Drop `@interaction` methods — not needed once implemented.
- Keep invariants as **comments**.
- If an `I{Class}` exists, leave it in place for the public seam and for hand-written test fakes; if it does not, `Class` itself remains the seam.
- Add exceptions, named constants, private helpers as needed.
- Edit so language-companion prose stays as the class docstring — implementations sit beneath intent, they do not replace it.
- Edit so the implemented public surface matches the seam already designed — a short caller-facing API with real behaviour behind it, still living in the module folder.

### Rules

**Operations**

- **`keep-operations-small-focused`** — Under **20 lines**; extract named helpers.
- **`simplify-control-flow`** — Guard clauses; max nesting depth as enforced by scanners.
- **`maintain-abstraction-levels`** — One level at a time; no raw I/O mixed into orchestration names.

**Naming / context**

- **`provide-meaningful-context`** — Named constants for magic numbers and unexplained literals.

**Errors / comments**

- **`use-exceptions-properly`** — Domain exceptions that name the failure.
- **`never-swallow-exceptions`** — Log and re-raise or convert; never bare swallow.
- **`stop-writing-useless-comments`** — Comments explain **why**, not **what**.

## Sketching

When sketching, use the following sketch template. Do not use the produce templates below — stop reading this skill when sketching.

# clean_engineering sketch template — terse indent notation

Rough shape for sketching an clean_engineering analysis before generating the formal artifact. Use clean_engineering vocabulary directly (class, property, operation, subtype, composition, aggregation, association) rather than the generic `thing` fallback.

## Module nest (before class detail)

Sketch **nested modules** when children share a base seam. Paths are domain nouns (`powers/attack`).

```
powers/                              <-- parent sub-system (has shared seam)
  effect                             <-- parent-owned shared base module
  attack -> effect                   <-- child; depends on base, not on siblings
  control -> effect
  defense -> effect
  movement -> effect
  sensory -> effect
  general -> effect
  extras -> effect                   <-- modifiers nest with powers when they only apply to effects
  flaws -> effect

conflicts/
  turns                              <-- sequence; stub actions
  actions                            <-- maneuvers; stub turns
  conditions                         <-- damage/recovery; uses checks

gear/
  equipment
  headquarters
  vehicles

checks/                              <-- flat top-level OK when no shared parent seam
abilities/
```

**Hard rules:** nest only when there is a **shared base** or clear sub-system; children implement independently with siblings stubbed; shared mechanics live once under the parent (e.g. `powers/effect`), not copy-pasted.

## Notation

```
ClassName : BaseClass
  propertyName
  operationName param param
  otherPropertyOrOperationName
       nestedThing                      <-- a owned class
       nestedOperation param
  RelatedClass                          <-- association candidate

  ----
 SubtypeName : ClassName
      otherCollaborator                 <-- construction property (delta)
      operationName param
       -> otherCollaborator.operation   <-- real call on a held collaborator
       -> super.operation               <-- base operation when subtype extends it
       // invariant or sequencing note
      ----
 Collaborator
      property
      operation param
```

## Legend

| Symbol | clean_engineering meaning |
|---|---|
| `ClassName` | a class — earn a name once identity, state, behavior, or invariants justify it |
| `ClassName : BaseClass` | subtype of BaseClass; record only the delta |
| `propertyName` | something the class holds (noun phrase) |
| `operationName param` | something the class does (verb phrase); trailing tokens are parameters |
| indent | ownership / composition / subordination |
| `----` | separator between the primary class block and a peer class it relates to |
| `-> collaborator.operation` | interaction — a real operation on a property, peer, or `super` |
| `-> _private_helper` | rare — only when no public collaborator operation exists and the helper is essential to the story |
| `// …` | invariant or sequencing note (`ce-comments-are-for-invariants-and-sequencing-notes-only` — must/never/before/after only; not descriptive prose) |

## Interaction rules (read these)

- **Prefer real calls.** Write `-> opposingTrait.resolve`, `-> cart.add_item`, `-> super.resolve` — names that exist (or will exist) on the sketch.
- **Do not invent underscore placeholders** (`_opposing_roll`, `_private_helper_important_enough_to_show`) as a default. Those hide the design. If you cannot name a real receiver + operation, the collaboration is not understood yet — grill it or leave a `//` note.
- **`-> ClassName` alone is not an interaction.** Point at an operation (or a property read that matters), not the type.
- Show only interactions that clarify collaboration; suppress incidental helpers.

## Example factory pattern (generation pattern — not a framework Loader type)

When sketching types that stories will import for examples, document the **pattern with `{parameter}` placeholders first**, then a concrete **example**.

App per `{Type}`: production file `{Type}` (+ `{IType}` only when an interface is requested/needed — see § Interfaces in `clean_engineering.md`); **separate** `{type}_example_factory` file with `{Type}ExampleFactory` (plain class, no base). Fake / Isolated / Production are **modes**, not subclasses. Example **data** is not one property per type — a factory method may load **several** example classes (e.g. Cart + Product). Store bundles under `{example_key}`; each bundle holds the type payloads that method needs.

### PATTERN

```
# {family}.{ext}                    // production cohesive-file
({IType})                           // optional — only when requested/needed
  constructor
  public_api
  internals
  dependencies
{Type}                              // production; : {IType} only if one exists

# {type}_example_factory.{ext}      // ALWAYS separate
{Type}ExampleFactory
  {example_method}(mode)
    // loads examples[{example_key}] -> {Type} (or {IType} if one exists), {OtherType}, …
    // Fake | Isolated | Production are modes (not subclasses)
// examples[{example_key}] = multi-type bundle (not examples[{Type}][…])
// Fake:       mock/stub framework creates the instance (of I{Type} if one exists, else {Type} directly); feed examples
// Isolated:   new {Type}(...ctor-injected mocks/stubs...)
// Production: new {Type}(...real collaborators...)
```

### EXAMPLE

```
# cart.py / cart.js  (no interface requested — single implementation, no swap need)
Cart
Product

# cart_example_factory.py / cart_example_factory.js
CartExampleFactory
  cart_with_items(mode)
    // examples[cart_with_items] -> Cart, Product
    // Fake via mock framework (mocks Cart directly); Isolated/Production via Cart ctor
```

### Generation modes (no Fake/Isolated/Production types — same instance type, `{IType}` only if one exists)

| Mode | When used | How built |
|---|---|---|
| Fake | explore / spec default | Mocking framework creates the instance — `I{Type}` if one exists, else mocks `{Type}` directly; feed `examples[{example_key}]` |
| Isolated | story-test tier | `new {Type}(...mocks/stubs via constructor injection...)` |
| Production | story-test tier | `new {Type}(...real collaborators...)` |
| Demo (optional) | UI path | wraps playwright / UI invoker |

## Fidelity progression

- **Language companion** — prose identity refined at every stage (not a fidelity). Names and plain-English bullets only.
- **Modules fidelity** — independent modules, thin terms, **one-way deps**, **build order** (after partition). No types / relationship kinds.
- **Model fidelity** — typed properties and operation signatures, stubbed empty; relationship kind decided per pair. **`I{Class}` is opt-in, not automatic** — it replaces the direct `Class` stub only when explicitly requested or when the module genuinely has multiple layers/implementations to abstract apart (see `clean_engineering.md` § Interfaces). The rest of this file shows the `I{Class}` form since that is the richer case to document; default to the direct `Class` stub unless that trigger applies.
- **Code fidelity (Phase 1)** — full typed contracts (`Class(I{Class})` when an interface exists, otherwise `Class` directly), invariants, cardinality; example factories completed. The sketch is superseded once the formal artifact captures all of this.
- **Code fidelity (Phase 2)** — production implementation; all empty bodies filled; real collaborators wired.

> **Note:** `specification` was a prior fidelity name. It is retired — its work is now Phase 1 of `code`.

## Rules

- Nothing needs a formal name until the grill reveals it. `thing` is fine as a placeholder if the concept isn't stable yet.
- Indent = owned or subordinate. Never use indent for association — put associated classes as peers below `----`.
- One class family per file (`cohesive-file`): a class plus its subtypes and tightly connected peers (element + collection, small aggregate + part). Multiple unrelated families belong in separate sketches / separate code files. Example factories always go in a sibling `{type}_example_factory` file (`example-factory-separate-file`).
- **No `I{Type}` interface names in informal or modules-fidelity sketches.** Use concrete class names only. Interface types (`ICart`, `IRepository`, etc.) never appear before model fidelity, and even at model/code they are **opt-in** — only when requested or a genuine multi-layer/multi-implementation seam exists (see `clean_engineering.md` § Interfaces). Default sketches stay on the concrete class name throughout.

## Discovery precedence (context for the sketcher)

Session context wins. If the caller pasted their own template in chat, use that instead of this file. This file is the clean_engineering-flavoured convention layer, one step above the generic default at `sketch/sketch-template.md`.

## Templates

### markdown

---
format: markdown
fidelity: all
---
<!--
  clean_engineering markdown template — unified across all fidelities.

  INTERFACES ARE OPTIONAL (see clean_engineering.md § Interfaces). This template shows
  the `I{ClassName}` form because it is the richer case to document. Default to
  skipping `## I{ClassName}` entirely and starting straight at `## {ClassName}` (empty,
  untagged Md members at model) unless the user asked for an interface, or the module
  genuinely has multiple layers/implementations behind one seam.

  Fidelity tags on section headings (as HTML comments — informational only):
    L  = language companion (prose identity; refined at every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order; no I{Class} yet)
    Md = model          (I{ClassName} — typed compact block — ONLY when an interface is
                         requested; otherwise model is the empty `## {ClassName}` block)
    C  = code           (fill {ClassName}; public filled, privates filled; drop interactions)

  Class member format (model):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — code fidelity only

  Document structure: H1 = module, H2 = class within that module.
  Interface (I{ClassName}) and implementation ({ClassName}) both sit under the
  same module H1 — interface first, then implementation. No fidelity section
  headers (## Model fidelity / ## Code fidelity) in the output.
  Language companion and modules overview go as prose BEFORE the first H1.

  Subtypes use ## {ChildClass} : {ClassName} notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / ... when generating.
-->

**Sources / context:** {source_files}                             <!-- L -->

## Language companion                                             <!-- L -->

*{ClassName}* is {intent — what role it plays, what it holds, what it does.
This paragraph IS the class definition. Identity only.}           <!-- L -->

### {class_name_as_a_concept}                                     <!-- L -->

- {bullet: what it holds, what it does, how it relates to *another class*} <!-- L -->
- {as many bullets as the concept warrants}                       <!-- L -->
- **Invariant:** {rule that must always hold — only when one exists} <!-- L -->

### {ChildClass} *is a type of* {ClassName}                       <!-- L -->

- {delta behavior only — what this subtype adds or overrides}     <!-- L -->

## Modules                                                        <!-- Mu -->

Build order: `{first}` → `{second}` → `{third}`

---

# {module_path}                                                   <!-- Mu -->

- **Purpose:** {one paragraph}                                    <!-- Mu -->
- **Seam (terms):** {ClassName}, {ChildClass}, ...                <!-- Mu -->
- **Dependencies (one-way):** {other_module}, ...                 <!-- Mu -->

## I{ClassName}                                                   <!-- Md, optional -->
<!-- Omit this section entirely by default — see note at top of file.
     Include it only when an interface was requested, or the module has
     multiple layers/implementations that need abstracting apart. -->

I{ClassName}({param}: {Type})
------
{owned_property}: {Type}
{plain_property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}
{another_operation}(): {ReturnType}

## {ClassName}                                                    <!-- Md -->

+ {ClassName}({param}: {Type})
------
+ << composition >> {owned_property}: {Type}
	Invariant: {constraint sentence.}
+ << aggregation >> {collected_property}: list[{Type}]
+ << association >> {referenced_property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}
	Invariant: {constraint sentence applicable to this operation.}
	Interaction:
		{variable}: {Type} = {other}.{call}({args})
		return {variable}
- _{private_helper}({param}: {Type}): {Type}

## I{ChildClass}                                                  <!-- Md, optional -->

I{ChildClass}({param}: {Type})
------
----
{delta_operation}({param}: {Type}): {ReturnType}

## {ChildClass}                                                   <!-- Md -->

+ {ChildClass}({param}: {Type})
------
+ {child_specific_property}: {Type}
	Invariant: {constraint sentence.}
----
+ {delta_operation}({param}: {Type}): {ReturnType}

---

# {next_module_path}                                              <!-- Mu -->

- **Purpose:** {one paragraph}
- **Seam (terms):** {ClassName}, ...
- **Dependencies (one-way):** *(none)*

## I{NextClassName}                                               <!-- Md, optional -->

I{NextClassName}({param}: {Type})
------
{property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}

## {NextClassName}                                                <!-- Md -->

+ {NextClassName}({param}: {Type})
------
+ {property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}

---

### Example factory (when Stories-bound) — separate file           <!-- Md -->

Write factories in `{type_slug}_example_factory.md` (or code sibling), **not** in the production family file.
Do not sketch Fake{ClassName} / Isolated{ClassName} / Production{ClassName} types.

## I{ClassName}ExampleFactory                                     <!-- Md, optional — same opt-in rule -->

I{ClassName}ExampleFactory()
------
----
load_{example_key}(mode): I{ClassName}

## {ClassName}ExampleFactory                                      <!-- Md -->

+ {ClassName}ExampleFactory()
------
----
+ load_{example_key}(mode): I{ClassName}
	// examples[{example_key}] multi-type bundle
	// Fake: mock/stub framework + feed examples
	// Isolated: new {ClassName}(ctor-injected mocks/stubs)
	// Production: new {ClassName}(real collaborators)

### python

"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to context_tools/language-tools.md for tool recommendations.
# =============================================================================
# A production file holds the public seam (I{Class} when one exists), the 
# production Class, subtypes, and tightly connected peers. 
# Example factories are ALWAYS in a separate sibling file.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
class {ClassName}:
    """*{ClassName}* unique role."""
    
    @property
    def {property}(self) -> {Type}:
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...

See examples in `context_tools/clean_engineering/examples/` if needed.