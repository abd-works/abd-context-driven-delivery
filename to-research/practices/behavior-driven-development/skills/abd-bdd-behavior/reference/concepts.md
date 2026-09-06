# Concepts — abd-bdd-behavior

For shared BDD theory (what BDD is, the three phases, observable behavior, domain practice alignment) see `../../../reference/bdd-concepts.md`.

This file covers concepts specific to the behavior-discovery phase.

---

## The behavior hierarchy

The behavior hierarchy is a plain-English indented outline. It is **state-oriented**: describe blocks build up state, leaves observe what is true of that state. This is the object-oriented BDD shape — `RSpec` / `Mocha` idiomatic — without the `describe(...)` / `it(...)` syntax at this fidelity.

Four kinds of line appear in the outline:

1. **Sub-epic** (top-level describe) — one block per sub-epic in scope from the story map. Name taken verbatim.
2. **Subject** (nested describe) — a noun phrase introducing an instance of a domain concept: `a Voucher`, `a Story Map`, `a DrawIO diagram`. Not a bare class name.
3. **State elaboration or narrative event** (nested describe) — either narrows the current state (`with 4 Epics`, `with a past expiry date`) or applies a change to it (`an Epic is appended to the Story Map`, `the diagram is edited — a SubEpic is deleted`). Events are present-tense narration; no `Given / When / Then` keywords.
4. **Observation** (leaf) — starts with `it should` or `the X should`. Describes what is true at that point in the built-up state. **Never** restates the operation that produced the state — that role belongs to the event describe above.

```
Redeem Voucher                                                 ← sub-epic (from story-map.md)
  a Voucher                                                    ← subject
    it should not be redeemed                                  ← observation of initial state
    with a 20 percent discount rule and no expiry              ← state elaboration
      it should be eligible for redemption                     ← observation of narrowed state
      it is applied to an Order with 3 eligible items          ← narrative event
        the Order should show a 20 percent discount on each    ← observation of resulting state
        the Voucher should be marked as redeemed
    with a past expiry date                                    ← alternative state
      any redemption should be refused                         ← observation
```

Depth is not fixed. Follow the structure the domain gives you. Every leaf must be readable in the context of every describe above it.

---

## Reading domain artifacts

The behavior hierarchy is derived, not invented. For each domain artifact, here is what to extract:

| Artifact | What to extract |
|---|---|
| `story-map.md` | Sub-epic names — these become top-level describe blocks |
| `domain-language.md` | Concept names — these become nested describe blocks |
| `domain-model.md` | States, transitions, operation groups — these become inner describe groupings |
| `acceptance-criteria.md` | Observable behaviors per story — these become `should` leaf statements |

If a concept is referenced in acceptance criteria but not present in domain-language or domain-model, flag it — do not add it silently to the hierarchy.

---

## Naming rules

- **Sub-epic names:** copied verbatim from the story map. No paraphrasing.
- **Subjects:** noun phrases naming an instance of a domain concept — `a Voucher`, `a Story Map`. Never a bare class name like `Voucher` or `StoryMap`.
- **State elaborations:** narrow the subject with `with ...`, or introduce sub-state with `the first X has N Y`.
- **Narrative events:** present-tense sentences describing a change — `an Epic is appended to the Story Map`, `the first Voucher is redeemed`. No `Given / When / Then` keywords.
- **Observations:** start with `it should` or `the X should`. Describe what is true at that point in the state. Do not restate the event above.

**Pass:** `an Epic is appended to the Story Map > it should hold 5 Epics`
**Fail (operation-oriented):** `StoryMap > should add an Epic to a StoryMap`
**Fail (implementation-oriented):** `should call applyDiscount() on VoucherService`

---

## What this phase does not produce

- No code syntax of any kind
- No Gherkin (`Given / When / Then`)
- No test file structure (`describe()`, `it()`, `beforeEach()`)
- No assertions
- No mocks

Those belong in abd-bdd-specification (structure) and abd-bdd-development (implementation).
