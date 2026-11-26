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
  At modules, language is the first lines under each `# {path}` card.
  At model, each class's language is the first lines of its `## {ClassName}`
  card, above the typed block: its definition paragraph, then one `### term`
  per domain term it owns. Terms other modules own are not repeated here.
  Do not emit `## Language` or `## Modules` above the cards at any fidelity.
  At modules fidelity, stop after Purpose / Seam / Dependencies / Constraint.
  Do not emit ## {ClassName} typed compact blocks, *is a type of*,
  Child : Parent, Sources/context of this folder's own files, scan dumps,
  or runtime names nobody types (expand, invoke, install_to).
  Those wait for model, or they are internals — omit them.

  Write human-readable markdown only. Strip template markup (`<!-- Mu -->`,
  `<!-- Mv -->`, `<!-- L -->`, `<!-- Md -->`, `<!-- C -->`, and similar)
  before writing. At modules, sit the language immediately under `# {path}`,
  then the `- **Purpose:**` block.

  Subtypes use ## {ChildClass} : {ClassName} notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / ... when generating.
-->

# {module_path}                                                   <!-- Mu -->

<!-- Language has no section of its own (no ## Language, no ## Modules above the cards).
     At modules it is the first lines of this # {path} card: one ### concept per seam term.
     At model it moves onto each class: the first lines of its ## {ClassName} card, above the
     typed block, so a class's words and its members are read and changed together. -->

### {ClassName}                                                   <!-- L, Mu — modules only; at model this sits on the class card -->

- {why a caller uses this (the outcome), then the mechanic if needed, then how it relates to *another class*} <!-- L, Mu -->

Build order: `{first}` → `{second}` → `{third}`                   <!-- Mu -->

- **Purpose:** {the job a caller hires this module for — not how it is wired} <!-- Mu -->
- **Seam (terms):** {ClassName}, {ChildClass}, ...                <!-- Mu -->
- **Dependencies (one-way):** {other_module}, ...                 <!-- Mu -->

## Constraint                                                    <!-- Mu -->

{what callers must or must not do at this seam — the annotations they type, not runtime names they never write}

<!-- MODULES STOPS HERE. Do not copy the typed blocks below into module-context.md. -->

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

The *{ClassName}* is {what it is for, told from the class: the job a caller hires it for}. The {ClassName} {how it works at a high level, and which classes it works with: who does what to whom}. <!-- L -->

The {ClassName} {the states it moves through: what it is created from, its starting status, and each way it ends}. <!-- L -->

- **{Responsibility}.** The {ClassName} {does this; behaviour serving the same responsibility stays in this bullet; it asks the *{OtherClass}* to do its part, and stops there}. <!-- L — one bullet per responsibility, never per member -->
- **{Responsibility}.** The {ClassName} has a *{PartClass}*, calculated from {what}; {where a value it calculates goes once it is done}. <!-- L -->

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

## I{ChildClass}                                                  <!-- Md, optional -->

I{ChildClass}({param}: {Type})
------
----
{delta_operation}({param}: {Type}): {ReturnType}

## {ChildClass}                                                   <!-- Md -->

*{ChildClass}* *is a type of* *{ClassName}* that {what it does differently — the delta only}. <!-- L -->

+ {ChildClass}({param}: {Type})
------
+ {child_specific_property}: {Type}
	// {must / never / always / before / after about this property}
----
+ {delta_operation}({param}: {Type}): {ReturnType}

---

# {next_module_path}                                              <!-- Mu -->

- **Purpose:** {the job a caller hires this module for}
- **Seam (terms):** {ClassName}, ...
- **Dependencies (one-way):** *(none)*

## Constraint                                                    <!-- Mu -->

{what callers must or must not do}

<!-- MODULES STOPS HERE. -->

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
load_{example_key}(mode: {GenerationMode}): I{ClassName}

## {ClassName}ExampleFactory                                      <!-- Md -->

+ {ClassName}ExampleFactory()
------
----
+ load_{example_key}(mode: {GenerationMode}): I{ClassName}
	// examples[{example_key}] multi-type bundle
	// Fake: mock/stub framework + feed examples
	// Isolated: new {ClassName}(ctor-injected mocks/stubs)
	// Production: new {ClassName}(real collaborators)
