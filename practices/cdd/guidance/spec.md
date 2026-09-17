# CDD — Procedural Guidance (spec fidelity)

## How to run spec

Spec narrows to a concrete sub-epic. Everything gets locked down:

1. **Scope is narrow** — a sub-epic within the solution or increment. Not the whole thing.
2. **Deepen each active lens to precision:**
   - Stories → exploration (locked scenarios, possibly acceptance_tests starting)
   - DDD → tactics (architecture resolved, implementation decisions made)
   - UX → mockup (controls finalized, interactions wired)
   - Clean Engineering → code (Phase 1: typed contracts)
   - BDD → development (SIGNATURE markers being filled with real tests)

## Locking decisions

At spec, decisions stop being tentative. When you lock something:

- The scenario list is final for this scope
- The domain model classifications are committed
- The screen controls and interactions are decided
- The public API surface is typed

Changes after locking require explicit re-opening, not silent drift.

## The spec-engineer transition

Spec and engineer share the same child fidelities for most lenses (both use tactics, code, development). The difference is intent: spec is about locking the design; engineer is about making it work. If tests are green and the code runs, you're in engineer territory.
