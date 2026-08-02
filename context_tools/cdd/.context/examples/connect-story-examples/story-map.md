---
fidelity: [discovery, specification]
artifact: [story-map]
format: md
section: body
---

<!-- Deliverable: extend clean_engineering + stories generators.
     Cart/Product appear only as pattern examples — not an app under construction. -->

# Story Map — Connect Story Examples

**Sources / context:** cdd-sketch.md, connected-context_tools.md, clean_engineering + stories generator packages

---

(E) Connect Story Examples
    (E) Generate Interface Extensions
        (S) Generator --> Generate Type Extending Interface
            // scenarios: Fake | Isolated | Production for any {Type}
            // owned by context_tools/clean_engineering instructions/templates
    (E) Generate Stories That Import Factories
        (S) Generator --> Generate Epic That Imports Factories
        (S) Generator --> Generate Sub-Epic That Imports Factories
        (S) Generator --> Generate Scenario Steps That Call Factory Methods
            // owned by context_tools/stories — factory links + objects used in scenarios
        (S) Generator --> Generate Story-Unique Imports
            // rare
    (E) Demonstrate Story Scenarios
        * approx 3-4 more stories (demo runner — later increment)

---

## Scope boundary

**In scope:** Extending `context_tools/clean_engineering` so generation builds Fake/Isolated/Production for `{Type}`; extending `context_tools/stories` so generation emits example-factory links and uses those objects in scenarios.
**Out of scope:** Building a pet-store/cart product; UX demo runner (later).

---

## Thin slices

### Increment 1: Generator extensions for factories + story imports

**Outcome:** CE generator can emit Fake/Isolated/Production; Stories generator can emit epic/sub-epic helpers and scenario steps that call factories (Fake at explore/spec).

**Stories:**
- Generate Type Extending Interface
- Generate Epic That Imports Factories
- Generate Sub-Epic That Imports Factories
- Generate Scenario Steps That Call Factory Methods
