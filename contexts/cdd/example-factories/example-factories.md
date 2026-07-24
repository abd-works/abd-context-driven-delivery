<!-- @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only. -->
<!-- invoke-edit: action satisfy | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->

<!--
  clean_engineering model fidelity — Fake / Isolated / Production are factory modes, not subclasses.
  L = language companion (prose). Md = model (I{Type} seam). Production {Type} at specification+.
-->

# Example Factories                                                    <!-- L -->

---

## Language companion                                             <!-- L -->

The clean_engineering generator produces `{IType}`, production `{Type}`, and a pattern-generated `{Type}ExampleFactory` whose methods load multi-type example bundles. <!-- L -->
**Fake / Isolated / Production are modes** of how the factory builds `I{Type}` — not generated subclasses. <!-- L -->
There is no ExampleLoader framework type — load/fill is a generation pattern. <!-- L -->

### Module: example_factories                                      <!-- L -->

- Generates `{IType}` + `{Type}` in the production family file; `{Type}ExampleFactory` in a **sibling** `{type}_example_factory` file. <!-- L -->
- Does **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` classes. <!-- L -->
- Stories generator (separate) emits epics, scenarios, and steps that **import** these factories. <!-- L -->
- Seam: named factory methods return `I{Type}` filled from `examples[{example_key}]` bundles in a chosen mode. <!-- L -->
- **Constraint:** A bundle may include several types (e.g. cart and product), not one examples bag per type. Factories never sit in the production file. <!-- L -->

### IType                                                          <!-- L -->

- Public contract for a domain type. <!-- L -->
- Surface slots: constructor, public api, internals, dependencies. <!-- L -->

### Type (production)                                              <!-- L -->

- Production class implementing IType. <!-- L -->
- **Already works** — keep confirming; do not reinvent. <!-- L -->

### Modes (not types)                                              <!-- L -->

- **Fake** — mocking/stub framework creates `I{Type}`; feed `examples[{example_key}]`. <!-- L -->
- **Isolated** — `new {Type}(...ctor-injected mocks/stubs...)`. <!-- L -->
- **Production** — `new {Type}(...real collaborators...)`. <!-- L -->

### TypeExampleFactory                                             <!-- L -->

- Pattern-generated plain class (no base). <!-- L -->
- Methods load `examples[{example_key}]` and return `I{Type}` (+ peers) in fake / isolated / production mode. <!-- L -->

### CartExampleFactory                                             <!-- L -->

- Illustrative app factory (pattern example only — not a product deliverable). <!-- L -->
- **cart_with_items:** bundle ICart + IProduct; fake mode by default for stories. <!-- L -->

### ICart / Cart                                                   <!-- L -->

- Cart interface and production class; factory modes build ICart. <!-- L -->

### IProduct / Product                                             <!-- L -->

- Product interface and production class — often in the same example bundle as cart. <!-- L -->
