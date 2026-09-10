---
name: clean-engineering-model
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

# clean_engineering-model

Use clean_engineering guidance at `model` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@clean_engineering-modules

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

## model

**Default format:** Python

**Other formats:** markdown for a language model and `drawio` through `class_model/drawio` for a class diagram. The same classes, operations, and relationships must appear in every selected representation.

**Goal:** Analyze modules and design its object model — the classes, what they remember and do, and how they relate. Stub empty properties and operations. No production behavior yet. A model is the whole design in one place — who owns what, what they do, how they connect — so a human or an agent can read it, challenge it, and refactor before any body or call site exists. Those are the decisions that are cheap here and expensive in code: once behavior is written, moving an operation means rewriting the body and every caller.

### Language

**When the user asks for language** rather than full generation at this fidelity, apply the top-level Language section. Do not use Guidance or Rules. **Stop reading this skill when writing language.**

### Guidance

Analyze the source context to identify the concepts and operations the domain already names. Group concepts with their own identity, state, and behavior into **classes**. Model them **behaviors first and data second**: **properties** are noun phrases describing what they remember, and **operations** are verb phrases describing what they do. An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to perform behavior owned by another object. A Service or Gateway that names a real external system is different: it represents that system's operations rather than holding displaced domain logic.

**Localize behavior to the object that owns the invariant.** Each object accesses its own state and enforces its own rules; do not write objects that manipulate another object's internal state. A route name, the actor in a Story, or the object named in Given does not determine ownership. Ask which object has the state and rule needed to complete the behavior. A customer route may still call `cart.checkout()` when Cart owns checkout; moving that operation to Customer or a `CheckoutManager` separates the rule from its state.

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with; that split surfaces the concept you had not named yet. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches. A class that does everything is a class that changes for every feature, and a long seam forces every caller to pick from methods that were not written for their job.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals — parameters that duplicate state mean callers assemble what the object should already know, and returns that expose internals let callers depend on how you store things. Inside an operation, name **interactions** with other classes — specifically in other modules. Use the existing public seam named in those modules or create new ones that respect module boundaries. Add **invariants** — things that must stay true when the operation runs; an invariant you do not name here is a bug you only find once the body is written. 

**Get typing right.** Write a **property** when variation is data: a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations. Write a **subtype** when a variant changes what the thing does, and record only the difference. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations share one public contract or when a domain object must describe an external dependency without importing its implementation.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global. A dependency you cannot see in the constructor cannot be swapped for a test double, and a global hides what the class actually needs to run.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part and the part has no identity outside it — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members, but members keep their own identity — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane. The kind you pick here becomes the lifecycle in code — composition deletes the part with the owner, association does not — so the wrong kind means rewriting constructors, delete paths, and every caller that assumed the wrong ownership.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language for new or updated terms now on the public API. Do not document internal design, private participants, or implementation notes — documented internals read as promises, and callers write against them.

### Interfaces

Use an interface when the model requires more than one implementation, when a caller must depend on a stable contract owned by another module, or when the domain describes access to an external system. Default to the concrete class when none of these conditions exists. A domain wrapper may name and represent the external type it wraps, but the external-system type must not import the domain wrapper or expose domain types; knowledge points from the domain toward the external contract, not back into the domain.


### Rules

**Shape classes**
- `model-modules-follow-the-partition` — Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.
- `class-not-property-instance-or-subtype` — Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.
- `keep-classes-single-responsibility` — Give each class one reason to change.
- `put-logic-on-the-owning-resource` — Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change.
- `use-property-not-accessor` — Use a named property for state and for a change whose validation and invariants can remain inside that property. Use an operation only when the behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as one property assignment. Callers should not need `getX`, `setX`, or storage knowledge.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work.
- `use-explicit-dependencies` — Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.
- `external-system-interface-is-one-way` — Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.


**Define operations**
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `limit-operation-parameters` — Have callers pass intent, not setup. Prefer 0-2 parameters for domain operations; when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract.
- `avoid-vague-parameter-names` — Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.
- `state-change-returns-record-or-named-failure` — When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.
- `catalog-has-an-evaluation-operation` — Let a catalog hold named rules and give the catalog or owning aggregate an operation that evaluates them and returns the unmet rules. Rule data without an evaluation operation leaves every caller to interpret it independently.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Invariants, interactions, and comments**

- `write-invariants` — Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.
- `write-interactions` — Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

**Names and reuse**

- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `do-not-invent-parallel-object-models` — Wrap or extend the live objects and name a wrapper after the type it represents. The domain wrapper may know the external type; the external type must not import the wrapper, expose domain types, or hold a reverse reference. Do not scrape the same data into a second `*Model` or `*Entry` family, because parallel representations require conversion code and drift apart.
- `one-canonical-model-document` — Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

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
# Put a class family in one file: the primary type, its subtypes, and
# tightly connected peers that only make sense together (element +
# collection, small aggregate + its part). Name the file after the family
# concept (`abilities.py` for Ability + Abilities). Split into another
# file only when a type is independently reused across families or the
# file becomes a grab-bag. Do not default to one class per file.
# Default: Class is the seam. I{ClassName} is not the default — add it in
# this same file when multiple implementations sit behind one seam, or when
# the user asks. Public members only on I{ClassName}; private members stay
# on {ClassName}. Put `{Type}ExampleFactory` in a sibling file — never in
# the production family file. Write each file under the module folder
# (`{module}/{family_slug}.py`), not beside the module.
# Invariants, interactions, comments (model):
#   Write each invariant as `#` on the class (or above the property /
#   operation it constrains): a must / never / always / before / after
#   that stays true when the object acts.
#   Write each interaction as `-> {collaborator}.{operation}` nested
#   under the calling operation. `-> ClassName` alone is not an interaction.
#   State an invariant or a sequence with `#`. Leave every other line
#   uncommented.
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
    # {must / never / always / before / after that stays true of the object}

    @property
    def {property}(self) -> {Type}:
        # {must / never / always / before / after about this property}
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        # {must / never / always / before / after when this operation runs}
        # -> {collaborator}.{operation}
        ...

    def _{private_helper}(self, {param}: {Type}) -> {Type}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...

See examples in `context_tools/clean_engineering/examples/` if needed.