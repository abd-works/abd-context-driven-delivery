---
name: clean_engineering-model
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

# clean_engineering-model

Use clean_engineering guidance at `model` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@clean_engineering-modules

# Contexts

Deepen OO design from modules toward production code. Each fidelity **adds** artifacts — do not invent detail from a deeper level.

---

## Language 
- At each fidelity, refresh prose for terms/classes already named at that stage — definition, story bullets, invariants in plain English.
- Keep identity on the class (or `## ClassName` section); member bullets move onto members as model/code deepen.
- Prose lives under `{session}/{module}/` (markdown sections and/or class docstrings) and is updated in place

---

## model

**Default format:** Python

**Goal:** Analyze modules and design its object model — the classes, what they remember and do, and how they relate. Stub empty properties and operations. No production behavior yet.

### Guidelines

Analyze the source context to identify the concepts and operations the domain already names — do not invent terminology. Group concepts that have their own identity, state, and behavior into **classes**. Model them **behaviors first and data second** — **properties** (what they remember — noun phrases) and **operations** (what they do — verb phrases). An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to do what the object itself should do.

**Localize behavior to the object that owns the state.** Each object accesses its own state and enforces its own invariants — do not write objects that manipulate another object's internal state. When deciding where an operation belongs, ask: which object has the data this operation needs? That is where the operation lives. `cart.checkout()`, not `customer.checkoutCart()` and not `CheckoutManager.processCheckout(cart)`. 

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with, this will reveal a hidden concept. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals. Inside an operation, name **interactions** with other classes — specifically in other modules (`-> {collaborator}.{operation}`). Use exsisting public seam named in those modules or create new ones that respect module boundaries. Add **invariants** thins that must stay true (`// remaining budget never goes negative`) when the operation runs.

**Get typing right.** Write a **property** when variation is data — a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations — put that shared behavior in one place. Write a **subtype** when a variant changes what the thing *does*; record only the delta. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations sit behind one seam.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part  — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language companion for new or uodated terms now on the public API. Do not document internal design, private participants, or implementation notes.


### Rules

- `class-not-property-instance-or-subtype` — Before promoting a term to its own class, check whether it fits as a property, an instance, or a subtype. Only when none of those three fit does it deserve its own class.
- `use-property-not-accessor` — Use `@property` (or the language equivalent) for read-only computed values; do not use `get_` / `set_` method prefixes.
- `keep-operations-single-responsibility` — Each operation has one reason to change — pure calculation or orchestration, not both. An operation doing two things reveals either a missing operation or a missing class.
- `separate-concerns` — Pure calculation separate from I/O and mutation.
- `use-clear-operation-parameters` — Prefer 0–2 parameters. When more configuration is needed, the extra parameters reveal a missing value object — promote them to a new class and pass that instead.
- `interactions-are-operation-calls` — Nest `-> {collaborator}.{operation}` under the calling operation. `-> ClassName` alone is not an interaction. Do not invent `- **Interaction:**` bullets.
- `invariants-are-class-level-notes` — Class-level invariants sit as `//` on the class, not under one operation. They do not become methods.
- `keep-classes-single-responsibility` — Each class has **one reason to change**.
- `hide-inner-details` — Expose **behavior** through named methods; callers see what the class does, not how it stores or arranges its information.
- `eliminate-duplication` — Repeated logic gets one canonical function.
- `prefer-class-operations` — Factory and lifecycle operations are **static methods on the class**, not module-level exported functions (`ParadiseMobile.initialize(config)`, not `export async function open()`). Private helpers used from one class belong on that class.
- `use-explicit-dependencies` — Pass every collaborator through the **constructor**; never reach for a global or construct a collaborator inside construction.
- `use-intention-revealing-names` — Every name — class, property, operation, parameter — answers "why does this exist?" No abbreviations, no single-letter identifiers outside trivial loop indices.
- `use-consistent-naming` — One word per concept across the model. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).
- `reuse-existing-not-invent-parallel` — When a class wraps or renders an existing type, name it after that type (`CatalogContextTool` wraps `BaseContextTool`; `CatalogAction` wraps `Action`). Do not invent a parallel domain noun for the same concept — especially not a retired synonym the project has already replaced (Foundry **Practice** → CDD **context tool**). Explicit old→new mapping rows (and overview lines that *state* the replacement) are allowed; live class names, constructor args, and row/registry/toolset labels are not.
- `reuse-established-notation-not-a-parallel-one` — Interactions/invariants at sketch and `## model` reuse `->` / `//`; never invent a bold-bullet parallel (`- **Interaction:**` / `- **Invariant:**` as collaboration markers). Language companion `- **Invariant:** <!-- L -->` and Spec indented labels are different surfaces.
- `ce-comments-are-for-invariants-and-sequencing-notes-only` — `//` comments are must/never/always/before/after notes only. Not narrative, not “transient value object”, not cross-references between atoms.
- `do-not-invent-parallel-object-models` — Do not invent a parallel object model when existing objects already carry the data a new requirement needs. Wrap or extend the live hierarchy instead; do not scrape the same information into a second `*Model` / `*Entry` (or similar) family.

## Sketching

When sketching, use the sketch template at `clean_engineering/templates/clean_engineering-sketch.md`. Do not use the produce templates below — stop reading this skill when sketching.

## Templates

### markdown

---
format: markdown
fidelity: all
---
<!--
  clean_engineering markdown template — unified across all fidelities.

  I{ClassName} is not the default. When generated, it lives in the same file /
  same module H1 as {ClassName} — public members only on I{ClassName}; private
  members stay on {ClassName}. Omit ## I{ClassName} unless the user asked or
  multiple implementations sit behind one seam.

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

  One file per cohesive set — the primary class, its subtypes, and peers
  that only make sense together. Do not default to one class per file.

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

# FILE: {module}/.context/module-context.md

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
# One file per cohesive set — the primary class, its subtypes, and peers
# that only make sense together. Do not default to one class per file.
# Default: Class is the seam. I{ClassName} is not the default — add it in
# this same file when multiple implementations sit behind one seam, or when
# the user asks. Public members only on I{ClassName}; private members stay
# on {ClassName}. Example factories are ALWAYS in a separate sibling file.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
# Optional — omit unless generating an interface:
class I{ClassName}(ABC):
    @property
    @abstractmethod
    def {property}(self) -> {Type}:
        ...

    @abstractmethod
    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

class {ClassName}:  # or class {ClassName}(I{ClassName}):
    """*{ClassName}* unique role."""

    @property
    def {property}(self) -> {Type}:
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

    def _{private_helper}(self, {param}: {Type}) -> {Type}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...

See examples in `context_tools/clean_engineering/examples/` if needed.