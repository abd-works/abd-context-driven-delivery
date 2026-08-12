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
| `// …` | invariant or sequencing note |

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
