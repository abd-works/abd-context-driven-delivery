---
fidelity: [discovery, specification]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Connect Story Examples

## Product / context

**Product:** CDD generators — `clean_engineering` + `stories` (not a retail/cart app)

**Slicing intent:** Ship generator instructions/templates that emit Fake/Isolated/Production and story artifacts that link factories into scenarios. Pattern examples (Cart/Product) illustrate only.

**Spine vs optional:** CE Fake/Isolated/Production emission + Stories factory links/scenario use on the spine. Demo runner later.

## Increments

### Increment 1: Extend CE + Stories generators

**Outcome:** clean_engineering builds Fake/Isolated/Production for any `{Type}`; stories generates epic/sub-epic helpers and scenario steps that import factories and use returned objects (Fake at explore/spec; Isolated/Production per test tier).

**Stories in this increment:**

- *Generate Type Extending Interface*
- *Generate Epic That Imports Factories*
- *Generate Sub-Epic That Imports Factories*
- *Generate Scenario Steps That Call Factory Methods*

### Increment 2: Demonstrate story scenarios (later)

**Stories in this increment:**

- *approx 3-4 demo runner stories*
