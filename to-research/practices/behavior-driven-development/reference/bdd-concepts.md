# BDD Concepts (shared)

Shared reference for all BDD skills. Each skill owns its own notation, format, and phase-specific rules; this file owns the shared theory.

---

## What BDD is

Behavior-driven development is a practice that bridges domain understanding and working tests. It starts with human-readable descriptions of what the system should do — anchored to the domain vocabulary and story structure — and progresses through three phases until those descriptions become passing, executable tests.

The three phases are distinct. Each has a different output and a different audience:

| Phase | Skill | Output | Audience |
|---|---|---|---|
| **Behavior discovery** | `abd-bdd-behavior` | Plain-English hierarchy (`*-behavior.md`) | Business stakeholders + team |
| **Signature** | `abd-bdd-specification` | Empty test skeleton with markers | Developers reviewing structure |
| **Development** | `abd-bdd-development` | Implemented tests + production code | Engineering |

Do not skip phases or merge them. The hierarchy must be agreed before signatures are written; signatures must exist before implementation begins.

---

## The describe / it / should hierarchy

Every BDD test file is an indented hierarchy:

- **describe** — a concept, state, or grouping. Describes *what is being characterized*, not a test.
- **it** — a single observable behavior of that concept in that state. Starts with `should` in plain English during behavior discovery; becomes a test slot during signature; gains a body during development.

The hierarchy is derived from domain artifacts, not invented by the developer. Every describe block must correspond to a sub-epic, a domain concept, or a named state from the domain model. This is what makes BDD tests readable by non-engineers.

---

## Observable behavior

An observable behavior is something the system does that a stakeholder can verify without looking at the code — a value returned, a state that changed, an effect produced through the public API.

Tests prove observable behavior. They do not describe how the system achieves the behavior internally, which fields it uses, or which private methods it calls. Any test that checks internals breaks when you refactor, not when behavior breaks — which is the wrong signal.

---

## Domain practice alignment

BDD in this family is domain-map-driven. The behavior hierarchy is not invented from scratch; it is derived from:

- **Story map** — sub-epics anchor the top-level describe blocks
- **Domain language** — concept names anchor nested describe blocks
- **Domain model** — states and transitions supply grouping structure
- **Acceptance criteria** — observable behaviors supply the leaf `should` statements

If a concept or sub-epic is missing from those artifacts, surface it there first. Do not add names to the BDD hierarchy that don't exist in the domain sources.
