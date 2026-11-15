# TDD overlay — sketch (step 1)

Shell only: table of contents, rule names, one line each. It is practice guidance, not a stack pattern, so it lives with the practices. It overlays the way LERN and MERN do (`practices/<practice>/model/schema.yaml` + `rules.yaml` per decorated practice), but is switched on by a yaml setting instead of chosen per session. Source material: `tdd-content.md`.

## Where it lives and how it switches on

```
cdd_guidance/practices/tdd/
  tdd.md                       # Overview, Guidance, Shared rules, one section per decorated practice
  tdd.py                       # thin @agent_toolset PracticeGuidance, like stories.py
  rules/                       # the shared rules, checked on every decorated practice's nodes
    __init__.py                # RULES, BY_SLUG
    shared_tdd_rules.py        # one PracticeGraphRule per shared rule
    shared_tdd_rules_spec.py   # failing + repaired example per rule
  practices/                   # one folder per decorated practice, named like the practice
    clean_engineering/
      model/schema.yaml        # extends CE nodes with the facts the rules read (e.g. operation.provenBy)
      model/rules.yaml         # node type -> rule slugs
      rules/__init__.py        # RULES, BY_SLUG — loaded when the overlay is on
      rules/code_tdd_rules.py
      rules/code_tdd_rules_spec.py
      model/python/_examples/<rule>/{faulty,repaired}/
    stories/                   # guidance only for now: Stories already has every rule proposed
    bdd/
      model/{schema.yaml, rules.yaml}
      rules/{__init__.py, development_tdd_rules.py, development_tdd_rules_spec.py}
      model/python/_examples/<rule>/{faulty,repaired}/
    ddd/
      model/{schema.yaml, rules.yaml}
      rules/{__init__.py, tactics_tdd_rules.py, tactics_tdd_rules_spec.py}
      model/python/_examples/<rule>/{faulty,repaired}/
```

Rules are the core of the overlay, laid out like LERN's (`patterns/lern_domain_driven/practices/bdd/rules/shared_behavior_rules.py`):
- **One class per rule.** Each rule is a `PracticeGraphRule` subclass. It names its `slug` and the `node_types` it checks, and its `check(node, context)` returns one `file:line` message per violation.
- **Facts on the node.** A rule reads facts the overlay's `schema.yaml` adds to the practice's node, such as `operation.provenBy` or `observation.seenRed`. It never parses files itself.
- **Wiring.** `rules.yaml` maps each node type to the slugs that run on it, and the practice's `rules/__init__.py` exports `RULES` and `BY_SLUG`.
- **Proof.** Each rule has a `_spec.py` that checks a failing example and its repaired example with the decorated practice's rule examples: `assert_rule_pair` for CE, `assert_stories_example_pair` for Stories, `assert_bdd_source_pair` for BDD, and `assert_ddd_example_pair` for DDD.
- **Judged rules.** A rule the graph can't decide, such as `minimum-to-green`, has no class. It stays a named bullet in `tdd.md`, and validate judges it.

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

## Rules check the output, guidance steers the process

A rule names something you can see in the finished tests and code, so validate can check it after the fact. How the work got there (test first, red then green, one at a time, stop after two misses) is process: it lives in Guidance as steps, never as a rule, because nothing in the output proves or disproves it. Rechecked every rule against that test; the process ones moved to Guidance.

## Table of contents

1. **Overview** — what TDD adds at implementation: every behavior the code has is proven by a test at the fastest tier that can prove it.
2. **Guidance** (process, all decorated fidelities)
   1. The test shape ladder — real conditions first on brownfield, test-first on greenfield; one ladder, three tiers (absorbs `testing-approach.md`).
   2. Red, green, refactor — write the test, see it fail for the right reason, write the least code to green, refactor only while green.
   3. One at a time — one signature or scenario to green before the next.
   4. Arrange, act, assert — how to lay out a test body.
   5. Test doubles — where to put a fake and how to build it from the real seam.
   6. Fixtures and example data — where example data lives, when to extract shared setup.
   7. Tiers by speed — what each tier holds; when each runs.
   8. When stuck — two failed fix attempts, then diagnose.
3. **Shared rules** — the test tiers: unit, heavy, e2e (BDD development and Stories acceptance_tests)
4. **Clean Engineering · code** — guidance + rules
5. **Stories · acceptance_tests** — guidance + rules
6. **BDD · development** — guidance + rules
7. **DDD · tactics** — guidance + rules

## Shared rules

File: `rules/shared_tdd_rules.py`. What BDD development and Stories acceptance_tests have in common is the test tiers: unit, heavy and e2e. These rules replace BDD `tier-by-speed` and Stories `story-tier-by-speed`; both practices drop theirs and get the overlay's. Each rule is checked on a spec file node; validate judges what the graph cannot see.

| Rule | Checked on | One line |
|---|---|---|
| `suffix-names-the-tier` | spec file | `*_spec` is unit, `*_heavy_spec` is heavy, `*_e2e_spec` / `*_agent_spec` is e2e; a story test's tier file follows the same suffixes. |
| `unit-tier-within-budget` | spec file | A unit example, with its before-each and after-each, runs within the budget (100 ms); a fake sits at every architecture boundary. |
| `heavy-tier-holds-a-real-resource` | spec file | A heavy spec uses a real resource (git, a server, a daemon, an installer, a worker, a big load); without one it belongs in the unit tier. |
| `e2e-tier-drives-browser-or-agent` | spec file | An e2e spec drives a real browser or a real agent, and nothing else does. |
| `slow-example-moves-not-the-file` | spec file | An example over budget moves to the heavy spec beside its unit spec, under the same described subject; the rest of the file stays unit, and the budget is never raised. |
| `no-skipped-or-empty-test` | observation, scenario | No test is skipped, commented out, or left without an assertion. |

Guidance (not rules): which tier runs when, from `cdd_guidance/rules/test-timing.md` — unit after every change, heavy once at the end of the work, e2e when the work touches a browser or an agent.

Also shared, because they overlay both BDD development and Stories acceptance_tests (each moves here from the practice that has it now):

| Rule | Checked on | One line | Moves from |
|---|---|---|---|
| `one-outcome-per-test` | BDD observation, Stories then | A test asserts one outcome; a Stories And may add an outcome of the same interaction only. | BDD `one-assertion-per-test` |
| `double-only-at-boundaries` | BDD observation, Stories step | A test fakes only what crosses the architecture boundary, never the subject under test. | BDD `layer-isolation` |
| `double-honours-real-seam` | BDD observation, Stories given | A fake has the real seam's operations and failure cases, and a heavy test runs the real one. | Stories `system-stubs-domain-real` |

### New code: one rule shared across practices

A classic overlay can't do this. `GraphOverlay.rules_for` (`harness/graph/pattern_overlays.py:76`) reads only `<overlay>.practices.<practice>.rules`, so a rule lives under exactly one practice, and LERN would have to copy a rule into each practice that needs it. TDD needs one rule checked on several practices' nodes. The new pieces:

- **A shared rule names a node type per practice.** It is a `PracticeGraphRule` whose `node_types` is a map, such as `{"bdd": ("Observation",), "stories": ("Then",)}`, instead of a flat tuple. `check(node, context)` reads the same fact on each node, for example `asserted_outcomes`, `fakes` or `tier_reaches`, so each practice's graph reading has to record that fact on its own node.
- **The overlay loads shared rules for each practice it decorates.** `GraphOverlay.rules_for(practice)` also reads `<overlay>.rules` and keeps the shared rules whose `node_types` name `practice.key`, merged with that practice's own `practices/<practice>/rules`.
- **The rule lives in one place.** Each decorated practice's `model/rules.yaml` lists the shared slug against its own node type, so the graph runs it there. The rule class, its spec and its faulty/repaired examples live once, in `tdd/rules/`, with one example pair per practice it checks.
- **Always on.** `always_apply` makes `PatternOverlays.checks_of` include this overlay for every practice listed in `decorates`, whatever overlays the session chose.

Moved to Guidance as process: `test-before-code`, `minimum-to-green`, `one-at-a-time`, `diagnose-after-two-misses`.

## Clean Engineering · code

File: `practices/clean_engineering/rules/code_tdd_rules.py`

Guidance: production code is written only to turn a test green; when a new class or operation is needed, write the test that needs it first.

| Rule | Graph node | One line |
|---|---|---|
| `operation-has-a-proving-test` | `operation` | Every public operation is invoked by at least one observation or step (`invokedBy`). |
| `class-demonstrated-by-a-test` | `class` | Every public class is demonstrated through an example or observation (`demonstratedThrough`). |
| `invariant-has-a-failing-case` | `invariant` | Every invariant has a test that tries to break it and sees the named failure. |
| `every-branch-taken-by-a-test` | `operation` | Every branch in a public operation's body is taken by some test (was `no-untested-branch-added`, which described the process). |

## Stories · acceptance_tests

Guidance: one scenario at a time — scenario test red on its Then, production code to green, then the next scenario.

No new rules: Stories acceptance_tests and scenarios already cover each one proposed.

| Proposed | Already exists as |
|---|---|
| `given-seeds-state-only` | `seed-state-at-its-real-owner`, `infrastructure-in-lifecycle-hooks`, `given-only-what-the-system-checks` |
| `when-calls-the-domain-operation` | `when-holds-the-operation`, `domain-operations-inline-in-steps`, `gwt-steps-trace-to-domain-operations` |
| `then-observes-one-outcome` | `when-holds-the-operation`, `behavioral-and-system-observable-outcomes`, `and-chaining` |
| `example-data-from-one-home` | `shared-example-fixtures`, `examples-declare-seed-vs-interaction` |

So `practices/stories/` holds Guidance only until a gap shows; no `rules/` folder yet.

Moved to Guidance as process: `scenario-runs-red-first`.

## BDD · development

File: `practices/bdd/rules/development_tdd_rules.py`

Guidance: one `BDD: SIGNATURE` at a time — fill it, see it fail, write the least code to green; arrange-act-assert from the realization call graph.

| Rule | Graph node | One line |
|---|---|---|
| `act-follows-the-realization` | `observation` | The act calls what the observation `invokes`, in the realization's order. |

Not supplied, because BDD already has them: `setup-builds-the-named-state` (BDD `context-setup-expresses-state`), `no-signature-left` (BDD template `no-remaining-signatures`, with `hierarchy-preservation`).

Moved to Guidance as process: `signature-goes-red-first`.

## DDD · tactics

File: `practices/ddd/rules/tactics_tdd_rules.py`

Guidance: settle how each building block is tested when you choose its pattern; prove it through its aggregate root.

| Rule | Graph node | One line |
|---|---|---|
| `aggregate-tested-through-its-root` | `aggregate` | Tests reach entities and values only through the aggregate root's operations. |
| `invariant-guarded-by-a-test` | `entityRoot` | Each aggregate invariant has a test where an operation refuses to break it. |
| `value-object-tested-by-equality` | `valueObject` | A value object's tests prove equality by value and immutability. |
| `repository-tested-on-a-real-store` | `repository` | A repository has unit tests on the in-memory one and a heavy test on the real store. |
| `domain-service-tested-with-fakes-at-boundary` | `domainService` | A domain service's tests fake its collaborators outside the domain and use its domain collaborators for real. |

## Open decisions for step 2

1. **Order on brownfield.** The ladder says run real conditions first, with no automated tests. Every other source says write the test first. The sketch keeps both: greenfield goes test first, brownfield runs real conditions first. Is that right?
2. **Moving rules.** Decided: the tier rules move here, and BDD `tier-by-speed` and Stories `story-tier-by-speed` are removed. Also decided: `one-assertion-per-test`, `layer-isolation` and `system-stubs-domain-real` move here as shared rules. Still open: BDD's `red-then-green`, `minimum-green` and `one-signature-at-a-time` are process — move them out of BDD's rules into this overlay's Guidance?
3. **The `always_apply` setting.** Should it go in `tdd.md` front matter, or in the project's yaml so a project can turn it off?
4. **Overlay reading.** Teach the practice catalogue that a practice may decorate others (its `decorates:` list and `practices/` folder), and have `PatternOverlays` read stack patterns only? Or one overlay reader for both?
5. **Agent BDD.** Agent BDD isn't decorated in this sketch. Should it be?
