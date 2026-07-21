## Specification Fidelity — Generate

Produce **fully typed class contracts**: annotated properties, complete operation signatures (public and private), relationship cardinality, invariants. Bodies remain `...`.

At this fidelity the module's *internals* become explicit alongside its seam. The modules-fidelity artifact captured the public face; specification fidelity spells out the full participant list — public classes AND internal ones — so the next engineer can modify the module safely. Fleshing out internals is part of the job here: hiding them would leave the module a black box that only its original author can extend.

Default output is code (Python). Keep editing files inside the existing module folder (`physical-folder`) — do not relocate class files outside it.

---

### Modules

Extend `.context/module-context.md` (the single shared context file seeded at modules fidelity) with the following sections:

```markdown
## Participants

[Every class in the module, labelled public vs internal. One bold entry per
class:
- **`PublicClass`** *(public)* — one-sentence role, and its position in the seam.
- **`_InternalHelper`** *(internal)* — one-sentence role, and which public class(es)
  use it. Reader must know what this exists for and what breaks if it changes.
This is where module internals get spelt out. Skipping internal participants
leaves the module opaque to anyone modifying it later.]

## Public API (specification)

[Extend the modules-fidelity Public API description with typed operation
signatures. One bold entry per public operation on each public class:
- **`ClassName.operation_name(params) -> ReturnType`** — [what it does; the
  intent already given at modules fidelity is inherited, not repeated].
Group operations under their owning public class. Internal operations are NOT
listed here — they appear in the Participants section on their owning class.]

## Internal design

[How the module works internally. Cover:
- **State ownership** — which internal class holds what state and why.
- **Lifecycle** — how instances are constructed, wired, and torn down; any
  initialisation-order constraints.
- **Failure translation** — how upstream failures (from dependencies) become
  the module's own failure shapes at the seam.
- **Any non-obvious internal contract** — e.g. "the signer must be constructed
  before the client; the config secret is loaded once at module init".
This section is the manual for changing the module. Public API is the contract;
Internal design is how the contract is honoured.]

## Domain separation

[Note any business invariants the caller must enforce that are NOT the module's
job to police. For each, link to where they are specified: "The [rule] invariant
is enforced by the caller — see [domain spec location]."]

## Mechanism (optional — extends modules-fidelity stereotype if present)

**Variation points** — [the classes or parameters that change per instance of this mechanism].
**Fixed parts** — [the classes, constraints, or structural rules that hold across all instances].
**How to build another instance** — [1–3 sentences: what a developer must provide and what the mechanism handles for them].
```

The domain separation section ensures business rules do not migrate into the module context file. Rationale that doesn't belong in code — design decisions, known constraints, trade-offs — continues to live here rather than in comments.

#### Module rules

- **`information-hiding`** — Volatile implementation choices — algorithms, storage formats, internal data structures — must not appear in public signatures or return types. If a public operation exposes an internal representation (e.g. returns a `Dict[str, Any]` shaped like a database row), wrap it in a domain type owned by the module. Changing the internal representation must not ripple to callers.
- **`temporal-independence`** — Every public operation must leave the module in a valid state. Flag any operation that requires callers to invoke it in a specific order relative to other public operations, and either merge the sequence into a single atomic operation or document the constraint explicitly in the module context file.

---

### Classes

At specification fidelity every class — public and internal — gets its full contract. Private operations, internal state, and invariants are all made explicit so the module's internals are as spelt out as its seam. For each class:

1. **Class docstring** — the opening definition paragraph from the language artifact, carried forward. By specification fidelity all language bullets are fully distributed: each property and operation has its own docstring **above** the member. No language content remains stranded in the class-level docstring.
2. **Properties** — `self._name: Type` in `__init__`, with `Optional`, `List`, etc. as needed.
3. **Public operations** — full typed signature. Body is `...`. This is the contract.
4. **Private operations** — `def _name(self, ...) -> Type: ...`. Signals internal design without implementing. Do not skip these — they are how the module's internals become explicit.
5. **Interactions** — for each public operation or property, list what it calls: **other** (external class, e.g. `pricing.compute_quote()`) or **internal** (private operation, e.g. `self._validate()`).
6. **Relationships** — target class, kind (**composition** / **aggregation** / **association**), cardinality (`1`, `*`, `0..1`), navigating end. Cardinality carried by the type (`List[Order]`, `Optional[Cart]`).
7. **Inheritance** — base class + delta. Subtype must be Liskov-substitutable for the base.
8. **Invariants** — constraints as docstring assertions or `__init__` comments.
