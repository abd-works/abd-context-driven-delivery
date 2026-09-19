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
**Stage:** implementation

**Goal:** Write working production code — real persistence, services, and UI behind the public seams.

#### Guidance

Follow the idioms in [`../language-tools.md`](../language-tools.md).

Start by **Implementing the public surface.** Where the model asked for an interface, the class implements it in the same file and the interface stays public-only. Where it did not, continue to implement the class. Implement public properties and operations first; write out private members next — the seam the model named is the contract, and privates follow from what those operations need, not the other way around. Relationships keep the kind and cardinality already named. 

Make sure to **Implement real behavior.** Fill every empty body — a stub ships as a silent no-op and hides that the seam was never finished. Wire real persistence, services, and other-module seams — not stand-ins as the shipping path. Add helpers, named constants, and domain exceptions only when the implementation needs them; speculative helpers become APIs nobody asked for. Keep an existing interface as the seam; otherwise treat the class as the seam. 

When writing out code take care to **Fill out all interactions with real code.** Turn `-> collaborator.operation` notes into actual calls — have the object ask its collaborators to do the work; do not reach into their internals. A placeholder left in place means the module boundary was never exercised; reaching past the seam couples you to another module's internals. Drop the placeholder once the call is real.

**Honor invariants in the implementation.** Turn `// remaining budget never goes negative` comments into methods where you can; replace comments with explicit code. A comment-only invariant runs only if someone read it — explicit code runs on every path.

**Keep the code clean.** Give each operation one thing to do; keep it short and at one level of abstraction — do not mix orchestration with raw I/O, or a storage change drags through business logic. Name things so they say why they exist. Handle the failing or empty cases first and return — then write the main path flat. Do not bury the real work inside nested ifs. Name exceptions after the failure; never swallow them. Give magic numbers names. Keep the public surface the seam already designed: short, caller-facing, with substantial implementation behind it, still in the module folder.

**Skip the model only for a very small change** — fill a body, rename, extract a helper, honor an invariant already named. The language is already there; keep it current. When you start needing to model — a new class, a new responsibility, a new relationship, a new public seam, or a new concept — stop and go to **model**. See `@clean_engineering-model`. Then return to code and implement what the model now names. Do not grow a shadow model only in the implementation — code-only design drifts from the language and module-context, and the next reader cannot find what you decided.

**Refresh the language and the seam.** Keep class identity in the docstring; put member bullets on the members. Edit the same public-seam module-context — how to use it, what callers must honor, what it depends on. Never internals. Never a parallel file — two documents drift, and documented internals read as promises callers build against.

#### Rules

Use these rules when filling production method bodies, constructors, and call sites — real persistence and real collaborators, not a demo shell.

**Implement the model**
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `keep-operations-small-focused` — Keep each operation short enough to read as one thought — under 20 lines. When it grows, extract a private helper whose name says why that slice exists.
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `simplify-control-flow` — Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Names and reuse**
- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `provide-meaningful-context` — Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `no-legacy-api-after-refactor` — When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

**Errors / comments**
- `use-exceptions-properly` — Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.
- `never-swallow-exceptions` — Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

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
