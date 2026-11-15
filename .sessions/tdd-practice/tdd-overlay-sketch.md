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
- **Facts on the node.** A rule reads facts the overlay's `schema.yaml` adds to the practice's node, such as `operation.provenBy` or `spec.tier`. It never parses files itself.
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

A rule names something you can see in the finished tests and code, so validate can check it after the fact. How the work got there (which flow, real run or test first, red then green, one at a time, stop after two misses) is process: it lives in Guidance as steps, never as a rule, because nothing in the output proves or disproves it. Rechecked every rule against that test; the process ones moved to Guidance.

## Table of contents

1. **Overview** — what TDD adds at implementation: every behavior is proven working for real before it is trusted, then kept proven by a test at the fastest tier that can prove it.
2. **Guidance** (process, all decorated fidelities)
   1. **Choose the flow** — first crossing of an architectural boundary runs end to end first; a story on a known area tests first (see below; replaces the test shape ladder in `testing-approach.md`).
   2. Red, green, refactor — inside Flow B, and for Flow A's unit tests once the real run works: see the test fail for the right reason, write the least code to green, refactor only while green. Not the opening move on a first boundary crossing.
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

## Guidance emphasis: two flows, picked by how known the area is

The Guidance opens with this choice, because the rest of the steps depend on it.

### Flow A — a new feature or story that crosses an architectural boundary for the first time

Run it for real first, because the danger here is an AI that believes its own stubs.

1. **Run it end to end, directly.** The AI drives it through the real stack itself (browser, server, store, agent) or asks the person to run it. Record every failure as it happens.
2. **Iterate until it works for real.** A person verifies the result. Only a human seeing the real thing work rules out hallucination.
3. **Capture it in an e2e or heavy test.** Write the test that runs the same path end to end, and see it pass against the real stack, so the success can't be hallucinated later.
4. **Then write the stubbed and mocked unit tests.** Write them only where a stub or mock was actually used, and check each one against the real seam you just ran. AI tends to stub critical functionality, or to put the stub at the wrong seam, faking what should be real.

### Flow B — another story or feature on an area already known

Here the seams are proven, so it runs the other way round:

1. **Unit tests first.** Write them on the seams that already exist (red).
2. **Write the code and run the tests** until they are green.
3. **Hand it to the person to try.**
4. **Write the heavy and/or e2e tests in a sub-task.** Hand them to a background agent so the person isn't kept waiting, and tell the person when they are done.

### How the choice is made

The area is "known" when an e2e or heavy test already runs real code across every architectural boundary this story touches. If any boundary is crossed for the first time (a new module seam, a new external system, a new tier), use Flow A for that boundary.

## Shared rules

File: `rules/shared_tdd_rules.py`. What BDD development and Stories acceptance_tests have in common is the test tiers: unit, heavy and e2e. These rules replace BDD `tier-by-speed` and Stories `story-tier-by-speed`; both practices drop theirs and get the overlay's. Each rule is checked on a spec file node; validate judges what the graph cannot see.

| Rule | Checked on | One line |
|---|---|---|
| `suffix-names-the-tier` | spec file | `*_spec` is unit, `*_heavy_spec` is heavy, `*_e2e_spec` / `*_agent_spec` is e2e; a story test's tier file follows the same suffixes. |
| `unit-tier-fakes-every-boundary` | spec file | A unit spec reaches no real resource: a fake sits at every architecture boundary. |
| `heavy-tier-holds-a-real-resource` | spec file | A heavy spec uses a real resource (git, a server, a daemon, an installer, a worker, a big load); without one it belongs in the unit tier. |
| `e2e-tier-drives-browser-or-agent` | spec file | An e2e spec drives a real browser or a real agent, and nothing else does. |
| `slow-example-moves-not-the-file` | spec file | An example over budget moves out alone, never the whole file: it gets a stub in the unit spec, and its real run goes to the heavy spec beside it, under the same described subject. The budget is never raised. |
| `stubbed-boundary-has-heavy-coverage` | unit spec file | Every boundary a unit spec stubs (socket, subprocess, git, file system, server, external system) is run for real by a heavy or e2e example with the same `should` sentence under the same subject. A stub without one is unchecked, and the stub can drift from the real thing. |
| `heavy-example-has-a-stubbed-twin` | heavy spec file | Every heavy example has a stubbed twin in the unit spec beside it, so the break is caught after every pass and not only at the end. |
| `no-skipped-or-empty-test` | observation, scenario | No test is skipped, commented out, or left without an assertion. |

### Test speed rules

These are checked on what a test run leaves behind, the way `scripts/test.ps1` checks today. The runner's guard logs every example over budget, and `.pycache/spec-seconds.json` keeps each file's seconds from the last run. The graph reads both onto the spec file node (new facts `example_ms`, `file_seconds` and `run_seconds`), so validate can check speed without running the suite again.

| Rule | Checked on | One line |
|---|---|---|
| `unit-example-within-100-ms` | spec file (`example_ms`) | Every unit example runs within 100 ms, its before-each and after-each included. Today: `-ExampleBudgetMs 100`, and an example over it fails its file. |
| `unit-file-within-2-seconds` | spec file (`file_seconds`) | A unit spec file runs within 2 s. Today the slowest is about 1 s; the runner's 20 s (`$soloSeconds`) is only where it gives a file a batch of its own. |
| `unit-tier-within-25-seconds` | the run (`run_seconds`) | The whole unit tier finishes in under 25 s of wall clock (today 20 s on an idle machine). Unit runs after every pass, and a slow unit tier stops being run. |
| `specs-run-in-parallel` | spec file | A spec can run beside any other: no fixed port, no shared temp folder, no shared `CDD_HOME`, no order between files. The runner splits files into `ProcessorCount - 2` parallel batches, longest first. |
| `heavy-spec-owns-its-resources` | heavy spec file | A heavy spec makes its own throwaway resources (repo, server port, `CDD_HOME`), so heavy specs can run in parallel too. Today they run one file at a time. |
| `expensive-fixture-built-once` | spec file | A read-only fixture that is slow to build, such as a parsed graph or a loaded practice, is built once per file and shared, not once per example. |
| `no-wait-in-unit-test` | unit spec file | A unit test never sleeps or polls. Time, retries and timeouts come from a fake clock. |
| `budget-never-raised` | runner settings | The 100 ms, 2 s and 25 s budgets are never raised to make a slow test pass. The slow test gets fast or moves tier. |

Measured on 2026-11-15, `scripts/test.ps1 -Suite unit` in this worktree on a 24-core machine with nothing else running (an earlier run beside a game took 29 s):
- **Whole run:** 20 s of wall clock, for 312 files and 5,340 examples.
- **Parallel pass:** 7 batches. It ends with its slowest batch, `cdd_guidance/actions .. clean_engineering` (75 files), at 15.2 s. The two `space/kanban` batches take 14.2 s and 11.3 s.
- **Re-run alone:** 2 files went over budget in parallel and ran again alone, taking 1.6 s.
- **Per file:** the slowest file takes about 1 s (`.pycache/spec-seconds.json`), and 292 of the 312 take under 1 s.
- **Over budget:** one file, `harness/mcp/mcp_daemon_spec.py`, has 2 examples at about 515 ms each, so the run fails. That spec arrived with the merge from main.

Guidance (process, not rules):
- **Unit after every pass.** Run it after each change or pass. The run is fast enough that the next pass starts from known-good code.
- **Heavy once, at the end, in the background.** Don't wait on it. Commit and push after unit passes, and report the heavy result when it comes back.
- **E2E only when the work touches a browser or an agent,** also once at the end.
- **A slow test: optimize first.** The first step for any example over budget is to find out why it is slow and make it fast. Measure where the time goes, then look for these, in order:
  1. **A real boundary the unit test doesn't need.** A socket, a subprocess, git, the file system or a server. Put a fake at that boundary. An example: `mcp_daemon_spec`'s two examples pinged a closed port, and Windows waits out the full 0.5 s connect timeout instead of refusing straight away. A fake ping makes them about 1 ms.
  2. **A wait.** A sleep, a poll or a retry loop. Use a fake clock or an event.
  3. **An expensive fixture rebuilt for every example.** Build it once per file and share it.
  4. **Work the example doesn't assert on.** For example, loading every practice to check one.
- **Every stub comes with heavy coverage.** Stubbing a boundary makes the unit test fast, but leaves the real boundary unproven. So whenever you stub, write a heavy (or e2e) example that runs the same `should` against the real boundary, or confirm one already exists. It works the other way too: a heavy example keeps a stubbed twin in unit. Unit runs the stub after every pass, and heavy checks once at the end that the stub still behaves like the real thing. For `mcp_daemon_spec`, the fake ping goes in the unit spec, and a heavy spec pings a real closed port and a real hung server.
- **Read the slow list after every unit run.** The runner lists each example over budget. Fix each one in the same pass, optimizing first.
- **Keep the timings.** `spec-seconds.json` orders the next run's batches, longest first, so the run ends when its slowest batch does and no later.

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

Moved to Guidance as process: `minimum-to-green`, `one-at-a-time`, `diagnose-after-two-misses`. Dropped: `test-before-code`, because test first is Flow B only; Flow A runs it for real first.

## Clean Engineering · code

File: `practices/clean_engineering/rules/code_tdd_rules.py`

Guidance: follow the flow. Crossing a boundary for the first time (Flow A), write the code and run it end to end for real before any unit test; on a known area (Flow B), write the unit test that needs a new class or operation before the code.

| Rule | Graph node | One line |
|---|---|---|
| `operation-has-a-proving-test` | `operation` | Every public operation is invoked by at least one observation or step (`invokedBy`). |
| `class-demonstrated-by-a-test` | `class` | Every public class is demonstrated through an example or observation (`demonstratedThrough`). |
| `invariant-has-a-failing-case` | `invariant` | Every invariant has a test that tries to break it and sees the named failure. |
| `every-branch-taken-by-a-test` | `operation` | Every branch in a public operation's body is taken by some test (was `no-untested-branch-added`, which described the process). |

## Stories · acceptance_tests

Guidance: one scenario at a time, in the flow's order. Flow A: run the scenario for real end to end, have the person verify it, then turn it into the heavy or e2e story test, then the stubbed domain tier. Flow B: domain tier red on its Then, code to green, person tries it, heavy/e2e tier in a sub-task.

No new rules: Stories acceptance_tests and scenarios already cover each one proposed.

| Proposed | Already exists as |
|---|---|
| `given-seeds-state-only` | `seed-state-at-its-real-owner`, `infrastructure-in-lifecycle-hooks`, `given-only-what-the-system-checks` |
| `when-calls-the-domain-operation` | `when-holds-the-operation`, `domain-operations-inline-in-steps`, `gwt-steps-trace-to-domain-operations` |
| `then-observes-one-outcome` | `when-holds-the-operation`, `behavioral-and-system-observable-outcomes`, `and-chaining` |
| `example-data-from-one-home` | `shared-example-fixtures`, `examples-declare-seed-vs-interaction` |

So `practices/stories/` holds Guidance only until a gap shows; no `rules/` folder yet.

Dropped `scenario-runs-red-first`: red first is Flow B only.

## BDD · development

File: `practices/bdd/rules/development_tdd_rules.py`

Guidance: one `BDD: SIGNATURE` at a time, in the flow's order; arrange-act-assert from the realization call graph. Flow A fills the heavy or e2e signature first, against a path already run for real; Flow B fills the unit signature red, then green.

| Rule | Graph node | One line |
|---|---|---|
| `act-follows-the-realization` | `observation` | The act calls what the observation `invokes`, in the realization's order. |

Not supplied, because BDD already has them: `setup-builds-the-named-state` (BDD `context-setup-expresses-state`), `no-signature-left` (BDD template `no-remaining-signatures`, with `hierarchy-preservation`).

Dropped `signature-goes-red-first`: red first is Flow B only.

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

1. **Order.** Decided: chosen by whether this crosses an architectural boundary for the first time (Flow A: real end to end first) or works on a known area (Flow B: unit tests first). See Guidance emphasis.
2. **Moving rules.** Decided: the tier rules move here, and BDD `tier-by-speed` and Stories `story-tier-by-speed` are removed. Also decided: `one-assertion-per-test`, `layer-isolation` and `system-stubs-domain-real` move here as shared rules. BDD's process rules (`red-then-green`, `minimum-green`, `one-signature-at-a-time`) stay in BDD for now; moving them is in the backlog (`.sessions/_backlog/maybe-later.md`).
3. **The `always_apply` setting.** Should it go in `tdd.md` front matter, or in the project's yaml so a project can turn it off?
4. **Speed budgets.** Today, on an idle machine, the unit tier takes 20 s and its slowest file about 1 s. The proposed budgets are 25 s for the tier and 2 s per file. The run time depends on how busy the machine is, so should the tier budget be checked only on an idle run? And should heavy specs run in parallel once `heavy-spec-owns-its-resources` holds?
5. **Overlay reading.** Teach the practice catalogue that a practice may decorate others (its `decorates:` list and `practices/` folder), and have `PatternOverlays` read stack patterns only? Or one overlay reader for both?
6. **Agent BDD.** Agent BDD isn't decorated in this sketch. Should it be?
