---
name: stories-scenarios
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-scenarios

Use stories guidance at `scenarios` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@stories-story_map
@stories-scaffold

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | typescript | Main-flow scenarios per story (single or multiple); optional variations; `examples/` + `givens.ts`. Pass `format markdown` when the strategy asks for a markdown view. |
| **acceptance_tests** | typescript | `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam (`front-end`, `back-end`, or another system name). No story folder. Fixtures: `examples/` + `givens.ts`. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.ts` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## scenarios

**Default format:** typescript

**Goal:** Main-flow scenarios per story (single or multiple) with optional variations.

**Produce:** Same `{story}.{tier}.ts` tree as acceptance_tests. Pass `format markdown` only when the strategy command names it.

### Rules

- **`behavioral-observable-outcomes`** — Name and Then in domain-observable terms; never internals.
- **`explore-full-interaction-surface`** — Scenarios are not complete when only the main-flow GWT from the sketch is written. Before locking scenarios (and again before acceptance_tests), walk the real UI and model **every distinct user-visible behavior**: inline rule checklists and how they change while typing, field-level validation errors clearing as input conforms, cross-field rules (confirm password, paste mismatch), submit-button gating, and server-side error surfaces. A story that only codifies the happy path when the screen has rich client-side validation is a **defect** — branch into additional scenarios (or scenario outlines with examples) per mechanical variation, not one paragraph that mentions "validation" in passing.
- **`gwt-steps-trace-to-domain-operations`** — Every Given / When / Then maps to a named domain operation or property. If a step cannot be traced, that is a modelling gap — add the operation or property; do not gloss over it. A hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
- **`reconcile-live-immediately`** — The running app wins. When a walk-through disagrees with the sketch, fix the sketch in that increment before locking the test.
- **`explain-deep-link-arrival`** — A scenario that navigates to a parameterized route (`/sign-up/:planId`) must say how a user actually arrives: in-app navigation, marketing/external deep-link, or a wizard step with no URL change. Do not write `When they navigate to X` as if it were a button.
- **`given-only-what-the-system-checks`** — Given states conditions the **running system actually uses** for the behaviour under test. Do not Given a field the code never reads for that decision (`metadata.verified` when routing actually keys off `customer.billing.id`).
- **`when-holds-the-operation`** — When holds the domain operation being exercised. An empty When with a comment, or the operation called inside Then, is a defect. Then only asserts on what When already produced — no I/O in Then.
- **`then-and-chaining`** — The first outcome uses `then()`; every later outcome on the same interaction chains `.and()`. Repeated `then()` calls break the Gherkin narrative. Markdown `And` stays `And`.
- **`extract-assertion-helper`** — The same assertion shape more than twice becomes a named helper that takes a data bag. Call sites pass only the concrete values.
- **`infrastructure-in-lifecycle-hooks`** — Browser boot, app wiring, and `initialize` live in `beforeAll` / `afterAll`. `given(` is domain state only.
- **`load-with-identity-in-hand`** — `load` takes the identity already in hand. Do not assume a browser session. Load once at the highest Given that needs the aggregate and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- **`seed-prior-story-as-given`** — A later story's Given is seeded from prior-story fixtures (`givens.ts` / `examples/`), not a replay of that story's When.
- **`reuse-owning-aggregate-stubs`** — For a non-core aggregate, take stubs from **that aggregate's folder / source repository** (`domain/{bounded-context}/{aggregate}/stubs/{system}/`). Do not invent a test-local stub. Do not stub the seam you are proving.

---

## Templates

Call `load_template` directly with your active format and fidelity:

```python
from context_tools.stories.stories import Stories
Stories(fidelity="scenarios").load_template(format="<your_format>", fidelity="scenarios")
```

See examples in `context_tools/stories/examples/` if needed.