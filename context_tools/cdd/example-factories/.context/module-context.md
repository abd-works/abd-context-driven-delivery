# Module: example_factories

**Purpose:** Expose `{IType}`, production `{Type}`, and `{Type}ExampleFactory` seams so stories helpers can call factories. Fake / Isolated / Production are factory **modes**, not subclasses.

**Primary use case:** Explore/spec — scenario steps call a helper; helper calls `ICartExampleFactory.cart_with_items()`; factory returns fake `ICart` + `IProduct` (mock/stub framework + `examples[cart_with_items]`). Story-test tiers choose isolated (`Cart` + ctor-injected mocks) or production (`Cart` + real collaborators).

**Rationale:** Example data is keyed by `{example_key}` as a multi-type bundle (not `examples[{Type}][…]`). Factories are pattern-generated plain classes (no ExampleLoader base). Do not generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` classes.

## Seam

The seam is `IType` / `ICart` / `IProduct` / `ICartExampleFactory` — callers import factories and load named example methods; they do not invent domain objects in helpers.

Constraint: do not emit Fake/Isolated/Production subclasses of `I{Type}`. Build `I{Type}` via factory mode (fake = mock framework + examples; isolated = `{Type}` + ctor-injected mocks; production = `{Type}` + real collaborators). Bundles are multi-type by `{example_key}`.

## Public API

- `IType`
- `ICart`
- `IProduct`
- `ICartExampleFactory.cart_with_items(mode="fake") -> (ICart, IProduct)`

**Layout:** Pattern docs in this module; generated app code uses two files per type — `{family}.{ext}` (production) and `{type}_example_factory.{ext}` (factory + examples).

## Dependencies

None at modules fidelity (example data arrives with the generation pattern).

**Mechanism stereotype:** `{Type}ExampleFactory.{example_method}(mode)` → `examples[{example_key}]` → fake | isolated | production `I{Type}`
