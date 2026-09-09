---
name: clean-engineering-modules
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

# clean_engineering-modules

Use clean_engineering guidance at `modules` fidelity only.

# Contexts

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Shared rules

- **`honor-every-rule-in-the-artifact`** — Honor every rule in the artifact you are writing. One-way dependencies, named seams, and localized behavior apply to language and markdown as well as to code. Do not create a dependency in prose that violates isolation. Treat prose with the same respect you treat the model and the code.
- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both. Keep `do-not-invent-parallel-object-models` on the model for wrappers and `*Model` / `*Entry` families.

---

## Language

When asked to express output using language, write the same names, definitions, and rules in a conversational format that we do in modules, model, and code. Shared rules `vocabulary-traces-to-source` and `do-not-invent-terms` apply here.

**Follow the object-oriented thinking in modules and model, then write it in English.** Use the same ideas: a **root** to group terms, then **concept**, **subtype**, **property**, **instance**, and **invariant**. Express them as short definitions, verb-led behaviour bullets, and italicized domain terms rather than typed class blocks. Keep identity on the concept and move member details onto the members as the model and code deepen. Update the existing prose under `{session}/{module}/` rather than creating a parallel description.

If the user asks for language while generating **modules** or **model**, use this Language section and stop before the fidelity Guidance and Rules.

---

## modules

**Default format:** markdown  
**Diagram format:** `drawio` (modules view with blue boxes, public-interface bullets, and one-way dependency arrows; template `templates/modules.drawio`). Programming-language channels are for **model** and later.

**Goal:** Partition a problem or solution space into independently understandable units. Each deep module has a narrow public interface and substantial implementation behind it. Name the units, their public interfaces, and their one-way dependencies. Identify only enough classes and terms to show independence; defer method bodies and relationship kinds until the boundaries settle.

Each **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

### Language

**When the user asks for language** rather than full generation at this fidelity, apply the top-level Language section. Do not use Guidance, Scaffold, or Module rules. **Stop reading this skill when writing language.**

### Guidance

**Create deep modules.** Group closely related classes around one domain concept. Give each module a narrow public interface with substantial implementation behind it so callers can understand the interface without reading the implementation. Avoid shallow modules that add another call without hiding a decision.

**Arrange dependencies one way.** Code that changes often may depend on code that changes rarely, but the stable module must not import its volatile caller. Break a cycle by moving the genuinely shared concept to a module both sides may depend on. Split a module that attracts unrelated callers along domain lines.

**Make every dependency explicit.** Use direct, visible references rather than globals, configuration magic, side effects, shared mutable state, or convention-based wiring. An implicit dependency is difficult to identify, replace in a test, or change safely.

Document only the **public seam** — how to use the module, how to extend it, and what it depends on. One name per concept on the seam (prefer the type name — `Ability`, not `Ability, Abilities`). Write language for the terms you name. Never document internals in module-context. The caller-facing contract is the only thing that should survive into documentation; implementation details live in source code and session notes. If someone needs to read the internals to use the module, the interface is too shallow.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut, not full generation at this fidelity), follow this subsection. Do not use Guidance or Module rules below.

Rough module index for a **partition** pass or first cut — module paths, chunk files, seam terms, and thin dependency notes only. Formal one-way graph and full `module-context.md` wait for **modules** generate.

Key rules: `one-way-deps` — dependencies flow one direction only; no cycles; `domain-nouns-only` — module names are domain nouns or paths, never action verbs or `*Model`/`*Runtime` suffixes. Use **abd-code-research** (not raw file scraping) when the corpus is code.

**Stop reading this skill when scaffolding.**

### Module rules

**Form the module**

- `domain-nouns-only` — Name modules after domain concepts or paths, never action verbs or generic `*Model` and `*Runtime` suffixes. A technical container name does not tell callers which business knowledge it owns.
- `named-seam-and-constraint` — Name the seam (public classes and operations) and the constraint (what callers must or must not do). A constraint you do not name is one callers find by breaking it at runtime.
- `high-cohesion` — Group classes that share one purpose and the same domain concept, or else unrelated work will keep landing in the same module and every feature ends up editing it.
- `single-boundary` — Do not let another module hold, mutate, or duplicate this module’s concept. The two modules will drift, and every rule change has to be found and made in both.

**Shape the seam**

- `deep-module` — Keep most top-level symbols private (at most **40%** public). Substantial work stays behind a short seam. Every public symbol is a signature you cannot change without editing every caller, so public parts are much harder to refactor than private ones.
- `abstraction-focus` — Name *what* the module does for callers, not internal steps or storage. A seam named after its implementation has to be renamed, with every caller updated, whenever the implementation changes.
- `public-seam-only` — Document only the public seam and dependencies on other modules. Do not document internals or tests. Documented internals are misunderstood as public promises, and callers start writing code against them.
- `use-typed-signatures` — Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.
- `general-purpose-surface` — Do not shape the seam for one caller’s UI or workflow. The second caller then either needs a near-duplicate operation or has to reshape its data to look like the first caller’s.
- `temporal-independence` — Leave the module valid after every public operation. Do not require a call order unless you document it, because an undocumented order fails on the first untested path.

**Define dependencies**

- `one-way-deps` — Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.
- `low-coupling` — Depend only through other modules’ seams. Keep sibling imports few. Reaching past a seam freezes that module’s internals — it can no longer change them without breaking you.
- `layer-separation` — keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.
- `nesting` — Nest a child only when it shares mechanics or is a sub-system; keep independent modules flat. Put shared behavior on the parent. A child may depend on the parent, not on siblings.

---

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
    L  = language (prose identity; refined at every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order; no I{Class} yet)
    Md = model          (I{ClassName} — typed compact block — ONLY when an interface is
                         requested; otherwise model is the empty `## {ClassName}` block)
    C  = code           (fill {ClassName}; public filled, privates filled; drop interactions)

  Class member format (model):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — code fidelity only

  Invariants, interactions, comments (model):
    Write each invariant as `//` on the class (or under the property / operation
    it constrains): a must / never / always / before / after that stays true
    when the object acts.
    Write each interaction as `-> {collaborator}.{operation}` nested under the
    calling operation. `-> ClassName` alone is not an interaction.
    State an invariant or a sequence with `//`. Leave every other line
    uncommented.

  Put a class family in one file: the primary type, its subtypes, and
  tightly connected peers that only make sense together (element +
  collection, small aggregate + its part). Name the file after the family
  concept (`abilities.py` for Ability + Abilities). Split into another
  file only when a type is independently reused across families or the
  file becomes a grab-bag of unrelated types. Do not default to one class
  per file. Put `{Type}ExampleFactory` (and its examples data, plus
  `I{Type}ExampleFactory` when one was requested) in a sibling file —
  never in the production family file.

  Give each module its own folder. Put class files, markdown, and other
  module-level artifacts in that folder — not beside it, not in a flat
  dump. Not every folder is a module: treat a folder as a module only
  when it owns `.context/module-context.md`. Do not stop at an arbitrary
  depth — every folder that is a cohesive functional unit owns
  `module-context.md`. Absorb implementation-only folders (`assets/`,
  thin `config/`) into the parent description. Never put
  `module-context.md` under `.context/sessions/`.

  Document structure: H1 = module, H2 = class within that module.
  Interface (I{ClassName}) and implementation ({ClassName}) both sit under the
  same module H1 — interface first, then implementation. No fidelity section
  headers (## Model fidelity / ## Code fidelity) in the output.
  Language and modules overview go as prose BEFORE the first H1.

  Write human-readable markdown only. Strip template markup (`<!-- Mu -->`,
  `<!-- Mv -->`, `<!-- L -->`, `<!-- Md -->`, `<!-- C -->`, and similar)
  before writing. Sit a module heading immediately above its
  `- **Purpose:**` block — no blank line between them.

  Subtypes use ## {ChildClass} : {ClassName} notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / ... when generating.
-->

**Sources / context:** {source_files}                             <!-- L -->

## Language                                                       <!-- L -->

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


+ {ClassName}({param}: {Type})
	// {must / never / always / before / after that stays true of the object}
------
+ << composition >> {owned_property}: {Type}
	// {must / never / always / before / after about this property}
+ << aggregation >> {collected_property}: list[{Type}]
+ << association >> {referenced_property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}
	// {must / never / always / before / after when this operation runs}
	-> {collaborator}.{operation}
- _{private_helper}({param}: {Type}): {Type}


I{ChildClass}({param}: {Type})
------
----
{delta_operation}({param}: {Type}): {ReturnType}


+ {ChildClass}({param}: {Type})
------
+ {child_specific_property}: {Type}
	// {must / never / always / before / after about this property}
----
+ {delta_operation}({param}: {Type}): {ReturnType}

---

# {next_module_path}                                              <!-- Mu -->

- **Purpose:** {one paragraph}
- **Seam (terms):** {ClassName}, ...
- **Dependencies (one-way):** *(none)*


I{NextClassName}({param}: {Type})
------
{property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}


+ {NextClassName}({param}: {Type})
------
+ {property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}

---


Write factories in `{type_slug}_example_factory.md` (or code sibling), **not** in the production family file.
Do not sketch Fake{ClassName} / Isolated{ClassName} / Production{ClassName} types.

## I{ClassName}ExampleFactory                                     <!-- Md, optional — same opt-in rule -->

I{ClassName}ExampleFactory()
------
----
load_{example_key}(mode): I{ClassName}


+ {ClassName}ExampleFactory()
------
----
+ load_{example_key}(mode): I{ClassName}
	// examples[{example_key}] multi-type bundle
	// Fake: mock/stub framework + feed examples
	// Isolated: new {ClassName}(ctor-injected mocks/stubs)
	// Production: new {ClassName}(real collaborators)

See examples in `context_tools/clean_engineering/examples/` if needed.