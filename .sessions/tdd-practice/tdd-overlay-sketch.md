# TDD overlay — sketch (step 1)

Shell only: table of contents, rule names, one line each. It is practice guidance, not a stack pattern, so it lives with the practices. It overlays the way LERN and MERN do (`practices/<practice>/model/schema.yaml` + `rules.yaml` per decorated practice), but is switched on by a yaml setting instead of chosen per session. Source material: `tdd-content.md`.

## Where it lives and how it switches on

```
cdd_guidance/practices/tdd/
  tdd.md                       # Overview, Guidance, Shared rules, one section per decorated practice
  tdd.py                       # thin @agent_toolset PracticeGuidance, like stories.py
  practices/
    clean_engineering/model/{schema.yaml, rules.yaml}
    stories/model/{schema.yaml, rules.yaml}
    bdd/model/{schema.yaml, rules.yaml}
    ddd/model/{schema.yaml, rules.yaml}
  _examples/<rule>/{faulty,repaired}/
```

`tdd.md` front matter (new setting). Today only `PatternOverlays` reads `practices/<practice>/model` overlays, and only from `cdd_guidance/patterns/`; a practice that decorates other practices needs that reading to come from the guidance side too:

```yaml
always_apply: true          # in every session, no overlays= word needed
decorates:                  # the fidelities it adds guidance and rules to
  clean_engineering: code
  stories: acceptance_tests
  bdd: development
  ddd: tactics
# ux: none — UX front_end_code is not decorated
```

Rules apply to the domain: each rule in `rules.yaml` is keyed to the practice's knowledge-graph node at that fidelity, the way LERN keys `server-tier-calls-the-real-thing` to `behaviorServer`. The graph checks it on the node; validate judges the rest.

## Table of contents

1. **Overview** — what TDD adds at implementation: a failing test drives every production change, at the fastest tier that can prove it.
2. **Guidance** (general, all decorated fidelities)
   1. The test shape ladder — real conditions first on brownfield, test-first on greenfield; one ladder, three tiers (absorbs `testing-approach.md`).
   2. Red, green, refactor — one signature or scenario at a time.
   3. Arrange, act, assert — one outcome per test.
   4. Test doubles — fakes at the architecture boundary only; a stub mirrors the real seam.
   5. Fixtures and example data — one home for example data, shared setup at three siblings.
   6. Tiers by speed — unit, heavy, e2e; what each holds; when each runs.
   7. When stuck — two failed fix attempts, then diagnose.
3. **Shared rules** (every decorated fidelity)
4. **Clean Engineering · code**
5. **Stories · acceptance_tests**
6. **BDD · development**
7. **DDD · tactics**

## Shared rules

| Rule | One line |
|---|---|
| `test-before-code` | No production change without a test that failed for the right reason first. |
| `minimum-to-green` | Write the least production code that turns the failing test green; refactor only while green. |
| `one-at-a-time` | Take one failing test to green before opening the next. |
| `one-outcome-per-test` | A test proves one outcome, so a failure names the behavior that broke. |
| `double-only-at-boundaries` | Replace only what crosses the architecture boundary; never the subject under test. |
| `double-honours-real-seam` | A fake has the real seam's operations and failure cases, and a heavy test runs the real one. |
| `tier-by-speed` | The file suffix names the tier and the tier is about speed (moved here from BDD and Stories). |
| `diagnose-after-two-misses` | After two failed fixes for the same failure, stop and diagnose before a third. |

## Clean Engineering · code

General: production code is written only to turn a test green; a new class or operation arrives with the test that needed it.

| Rule | Graph node | One line |
|---|---|---|
| `operation-has-a-proving-test` | `operation` | Every public operation is invoked by at least one observation or step (`invokedBy`). |
| `class-demonstrated-by-a-test` | `class` | Every public class is demonstrated through an example or observation (`demonstratedThrough`). |
| `invariant-has-a-failing-case` | `invariant` | Every invariant has a test that tries to break it and sees the named failure. |
| `no-untested-branch-added` | `operation` | A new branch in an operation body arrives with the test that takes it. |

## Stories · acceptance_tests

General: one scenario at a time — scenario test red, production code green, then the next scenario.

| Rule | Graph node | One line |
|---|---|---|
| `scenario-runs-red-first` | `scenario` | A scenario's test is seen failing on its Then before its production code exists. |
| `given-seeds-state-only` | `given` | A Given builds state through repositories or fixtures; it never asserts and never calls the When. |
| `when-calls-the-domain-operation` | `when` | A When calls the operation it `invokes`, through the public seam, nothing else. |
| `then-observes-one-outcome` | `then` | A Then checks the example it `observes`; an And adds an outcome of the same interaction only. |
| `example-data-from-one-home` | `example` | Example rows come from the story's examples file, never typed inline in a step. |

## BDD · development

General: one `BDD: SIGNATURE` at a time, arrange-act-assert from the realization call graph.

| Rule | Graph node | One line |
|---|---|---|
| `signature-goes-red-first` | `observation` | Each signature is filled and seen failing before production code is written for it. |
| `act-follows-the-realization` | `observation` | The act calls what the observation `invokes`, in the realization's order. |
| `setup-builds-the-named-state` | `context` | A `that`/`with` setup arranges exactly the state its label names (pairs with BDD's `context-setup-expresses-state`). |
| `no-signature-left` | `spec` | A development spec is done only when no `BDD: SIGNATURE` marker remains. |

## DDD · tactics

General: each building block is proven the way its kind demands, through its aggregate root.

| Rule | Graph node | One line |
|---|---|---|
| `aggregate-tested-through-its-root` | `aggregate` | Tests reach entities and values only through the aggregate root's operations. |
| `invariant-guarded-by-a-test` | `entityRoot` | Each aggregate invariant has a test where an operation refuses to break it. |
| `value-object-tested-by-equality` | `valueObject` | A value object's tests prove equality by value and immutability. |
| `repository-tested-on-a-real-store` | `repository` | A repository's unit tests run on the in-memory one; a heavy test runs the real store. |
| `domain-service-tested-with-fakes-at-boundary` | `domainService` | A domain service's collaborators outside the domain are fakes; its domain collaborators are real. |

## Open decisions for step 2

1. **Order on brownfield.** The ladder says run real conditions first, with no automated tests. Every other source says write the test first. The sketch keeps both: greenfield goes test first, brownfield runs real conditions first. Is that right?
2. **Moving rules.** `tier-by-speed`, `story-tier-by-speed`, `layer-isolation` and `red-then-green` would move out of BDD and Stories into this overlay. Or should they stay where they are, with the overlay only pointing to them?
3. **The `always_apply` setting.** Should it go in `tdd.md` front matter, or in the project's yaml so a project can turn it off?
4. **Overlay reading.** Teach the practice catalogue that a practice may decorate others (its `decorates:` list and `practices/` folder), and have `PatternOverlays` read stack patterns only? Or one overlay reader for both?
5. **Agent BDD.** Agent BDD isn't decorated in this sketch. Should it be?
