## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code. Honour every rule in the artifact you are writing — prose, diagrams, and source.

## Shared rules

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`honor-every-rule-in-the-artifact`** — Honor every rule in the artifact you are writing. One-way dependencies, named seams, and localized behavior apply to language and markdown as well as to code. Do not create a dependency in prose that violates isolation. Treat prose with the same respect you treat the model and the code.
- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both. Keep `do-not-invent-parallel-object-models` on the model for wrappers and `*Model` / `*Entry` families.

---

#### Overview


**Default format:** Python
**Stage:** specification

**Other formats:** markdown for a language model and `drawio` through `class_model/drawio` for a class diagram. The same classes, operations, and relationships must appear in every selected representation.

**Goal:** Design the object model — the classes, what they remember and do, and how they relate.

#### Guidance

Analyze the source context to identify the concepts and operations the domain already names. Group concepts with their own identity, state, and behavior into **classes**. Model them **behaviors first and data second**: **properties** are noun phrases describing what an object remembers or derives from the state it already owns, and **operations** are verb phrases describing what it does. A derived property recalculates internally when read but still looks like a field to its caller; it takes no owner or state parameters. An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to perform behavior owned by another object. A Service or Gateway that names a real external system is different: it represents that system's operations rather than holding displaced domain logic.

**Localize behavior to the object that owns the invariant.** Each object accesses its own state and enforces its own rules; do not write objects that manipulate another object's internal state. A route name, the actor in a Story, or the object named in Given does not determine ownership. Ask which object has the state and rule needed to complete the behavior. A customer route may still call `cart.checkout()` when Cart owns checkout; moving that operation to Customer or a `CheckoutManager` separates the rule from its state.

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with; that split surfaces the concept you had not named yet. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches. A class that does everything is a class that changes for every feature, and a long seam forces every caller to pick from methods that were not written for their job.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals — parameters that duplicate state mean callers assemble what the object should already know, and returns that expose internals let callers depend on how you store things. Inside an operation, name **interactions** with other classes — specifically in other modules. Use the existing public seam named in those modules or create new ones that respect module boundaries. Add **invariants** — things that must stay true when the operation runs; an invariant you do not name here is a bug you only find once the body is written. 

**Get typing right.** Write a **property** when variation is data: a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations. Write a **subtype** when a variant changes what the thing does, and record only the difference. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations share one public contract or when a domain object must describe an external dependency without importing its implementation.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global. A dependency you cannot see in the constructor cannot be swapped for a test double, and a global hides what the class actually needs to run.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part and the part has no identity outside it — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members, but members keep their own identity — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane. The kind you pick here becomes the lifecycle in code — composition deletes the part with the owner, association does not — so the wrong kind means rewriting constructors, delete paths, and every caller that assumed the wrong ownership.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language for new or updated terms now on the public API. Do not document internal design, private participants, or implementation notes — documented internals read as promises, and callers write against them.

#### Rules

Use these rules when deciding which classes exist, what they remember and do, and how they relate — stubs only, no production bodies.

**Shape classes**
- `model-modules-follow-the-partition` — Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.
- `class-not-property-instance-or-subtype` — Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.
- `keep-classes-single-responsibility` — Give each class one reason to change.
- `put-logic-on-the-owning-resource` — Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.
- `use-property-not-accessor` — Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work.
- `use-explicit-dependencies` — Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.
- `external-system-interface-is-one-way` — Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.


**Define operations**
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `limit-operation-parameters` — Have callers pass intent, not setup. Prefer 0-2 parameters for domain operations; when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract.
- `avoid-vague-parameter-names` — Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.
- `state-change-returns-record-or-named-failure` — When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.
- `domain-exception-carries-context` — Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely.
- `catalog-has-an-evaluation-operation` — Let a catalog hold named rules and give the catalog or owning aggregate an operation that evaluates them and returns the unmet rules. Rule data without an evaluation operation leaves every caller to interpret it independently.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Invariants, interactions, and comments**

- `write-invariants` — Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.
- `write-interactions` — Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

**Names and reuse**

- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `do-not-invent-parallel-object-models` — Wrap or extend the live objects and name a wrapper after the type it represents. The domain wrapper may know the external type; the external type must not import the wrapper, expose domain types, or hold a reverse reference. Do not scrape the same data into a second `*Model` or `*Entry` family, because parallel representations require conversion code and drift apart. Do not split the same job into a second type either — working state for a parse, walk, or expand belongs on the object that owns that operation unless the model names the second type on the public seam.
- `one-canonical-model-document` — Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

#### Template

"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to practices/language-tools.md for tool recommendations.
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
