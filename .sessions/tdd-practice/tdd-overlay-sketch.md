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
3. **Shared rules** (output, every decorated fidelity)
4. **Clean Engineering · code** — guidance + rules
5. **Stories · acceptance_tests** — guidance + rules
6. **BDD · development** — guidance + rules
7. **DDD · tactics** — guidance + rules

## Shared rules

File: `rules/shared_tdd_rules.py`. The overlay supplies only rules no practice has yet. Each is checked on the output; a rule the graph cannot decide is a bullet in `tdd.md` that validate judges.

| Rule | Checked on | One line |
|---|---|---|
| `no-skipped-or-empty-test` | graph: observation, scenario | No test is skipped, commented out, or left without an assertion. |

Not supplied, because a practice already has the rule (open decision 2 asks whether these move here):

| Proposed | Already exists as |
|---|---|
| `one-outcome-per-test` | BDD `one-assertion-per-test` |
| `double-only-at-boundaries` | BDD `layer-isolation` |
| `double-honours-real-seam` | Stories `system-stubs-domain-real` |
| `tier-by-speed` | BDD `tier-by-speed`, Stories `story-tier-by-speed` |

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
2. **Moving rules.** `tier-by-speed`, `story-tier-by-speed` and `layer-isolation` would move out of BDD and Stories into this overlay, and BDD's `red-then-green`, `minimum-green` and `one-signature-at-a-time` are process, so they would leave BDD's rules for this overlay's Guidance. Or should they stay where they are, with the overlay only pointing to them?
3. **The `always_apply` setting.** Should it go in `tdd.md` front matter, or in the project's yaml so a project can turn it off?
4. **Overlay reading.** Teach the practice catalogue that a practice may decorate others (its `decorates:` list and `practices/` folder), and have `PatternOverlays` read stack patterns only? Or one overlay reader for both?
5. **Agent BDD.** Agent BDD isn't decorated in this sketch. Should it be?
