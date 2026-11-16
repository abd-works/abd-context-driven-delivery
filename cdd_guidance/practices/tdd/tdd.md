---
always_apply: true
supplements:
  clean_engineering: code
  stories: acceptance_tests
  bdd: development
  ddd: tactics
---

## Overview

Test-driven development at implementation: every behavior is proven working for real before it is trusted, then kept proven by a test at the fastest tier that can prove it. TDD supplements the implementation fidelities of Clean Engineering (code), Stories (acceptance tests), BDD (development), and DDD (tactics); UX front-end code is not supplemented. Its guidance is the process; its rules check what the finished tests and code show. It has no rules for every fidelity it supplements: each section of rules names the fidelities it is for.

## Guidance

### Choose the flow first

The order of work depends on whether the story crosses an architectural boundary for the first time. An area is **known** when an e2e or heavy test already runs real code across every architectural boundary the story touches. If any boundary is new (a new module seam, a new external system, a new tier), use Flow A for that boundary.

**Flow A — a new feature or story that crosses an architectural boundary for the first time.** Run it for real first: the danger here is an AI that believes its own stubs.

1. **Run it end to end, directly.** Drive it through the real stack yourself (browser, server, store, agent), or ask the person to. Record every failure as it happens.
2. **Iterate until it works for real.** A person verifies the result. A human seeing the real thing work is the only way to rule out hallucination.
3. **Capture it in an e2e or heavy test.** Write the test that runs the same path end to end, and see it pass against the real stack, so the success cannot be hallucinated later.
4. **Then write the stubbed and mocked unit tests,** only where a stub or mock was actually used, each checked against the real seam you just ran. An AI tends to stub critical functionality, or to put the stub at the wrong seam and fake what should be real.

**Flow B — another story or feature on a known area.** The seams are proven, so the order reverses:

1. **Write the unit tests** on the seams that already exist, and see them fail for the right reason.
2. **Write the code and run only the tests for the change** — the specs of the files it touched — until they pass. Not the whole tier.
3. **Hand it to the person to try,** and while they test it, run the whole unit tier in a sub-task off the person's thread; report its result when it comes back.
4. **Write the heavy and/or e2e tests in a sub-task:** hand them to a background agent so the person is not kept waiting, and tell the person when they are done.

### Red, green, refactor

Inside Flow B, and for Flow A's unit tests once the real run works: see the test fail for the right reason, write the least production code that makes it pass, and refactor only while green. Take one signature or scenario to green before opening the next. It is not the opening move on a first boundary crossing.

### Arrange, act, assert

Lay out each test body as arrange, act, assert, and assert one outcome, so a failure names the behavior that broke.

### Test doubles and heavy coverage

Fake only what crosses the architecture boundary, never the subject under test, and build each fake from the real seam: the same operations and the same failure cases. **Every stub comes with heavy coverage:** stubbing a boundary makes the unit test fast but leaves the real boundary unproven, so whenever you stub, write a heavy (or e2e) example that runs the same `should` against the real boundary, or confirm one already exists. It runs the other way too: a heavy example keeps a stubbed twin in the unit spec beside it. Unit runs the stub after every pass; heavy checks, on its own cadence, that the stub still behaves like the real thing.

### Fixtures and example data

Keep example data in one home per concept and reuse it. Build a fixture that is slow to make and only read, such as a parsed graph or a loaded practice, once per file and share it. Extract shared setup once three sibling tests repeat it.

### Tiers by speed

A spec file's suffix names its tier, and the tier is about speed:

| Tier | Files | Holds |
|---|---|---|
| unit | `*_spec`, story tiers | Examples that run in microseconds to milliseconds, with a fake at every architecture boundary |
| heavy | `*_heavy_spec` | Examples that need a real resource: git, a server, a daemon, an installer, a worker process, a big load |
| e2e | `*_e2e_spec`, `*_agent_spec` | Examples that drive a real browser or a real agent |

### Make slow tests fast first

The first move for an example over budget is to find out why it is slow and make it fast. Measure where the time goes, then look, in order, for:

1. **A real boundary the unit test does not need** — a socket, a subprocess, git, the file system, a server. Put a fake at that boundary, and make sure a heavy test covers the real one. (On Windows a closed loopback port is not refused at once: a ping to it waits out its whole connect timeout.)
2. **A wait** — a sleep, a poll, a retry loop. Use a fake clock or an event.
3. **An expensive fixture rebuilt for every example.** Build it once per file.
4. **Work the example does not assert on.**

Only an example that is still slow, or that exists to prove the real resource, moves to the heavy spec under the same described subject, keeping its stubbed twin in unit.

### Cadence

Stay off the person's thread. In the foreground run only what proves the change just made; every larger run (the whole unit tier, heavy, e2e) goes to a sub-task or background process, and its result is reported when it comes back.

| Tier | When it runs | Who runs it |
|---|---|---|
| unit, for the change | After every change | The agent, in the foreground: only the specs of the files the change touched, so the answer comes in seconds |
| unit, whole tier | While the person tries the change, and before a push | A sub-task off the person's thread (about 20 s); nobody waits on it |
| heavy | Every hour, and once at the end of multi-pass work | A background process; push without waiting, report its result when it comes back |
| e2e | Every day, before every release, and at the end of work that touches a browser or an agent | The daily scheduled run and the release command |

Read the runner's slow list after every whole-tier unit run and fix each example in the same pass, optimizing first. Keep the runner's timings (`.pycache/spec-seconds.json`): they order the next run's batches, longest first.

### When stuck

After two failed fixes for the same failure, stop and diagnose before a third: read the failure, reproduce it on its own, and find the cause.

## stories-acceptance-tests, bdd-development

The tests Stories acceptance tests and BDD development write share their tiers, their speed, their stubs and heavy coverage, and the cadence they run on.

### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*.spec.shared.ts,**/*Spec.java,**/*.story.*,**/*_story.test.*"
```

Whenever you create, alter, or delete acceptance tests or BDD specs. Follow these rules.

**Tiers**
- **`suffix-names-the-tier`** — `*_spec` is unit, `*_heavy_spec` is heavy, and `*_e2e_spec` / `*_agent_spec` is e2e; a story test's tier file follows the same suffixes. A suffix that names the wrong tier puts a slow test in the run that must stay fast.
- **`unit-tier-fakes-every-boundary`** — A unit spec reaches no real resource: a fake sits at every architecture boundary.
- **`heavy-tier-holds-a-real-resource`** — A heavy spec uses a real resource (git, a server, a daemon, an installer, a worker, a big load); without one it belongs in the unit tier.
- **`e2e-tier-drives-browser-or-agent`** — An e2e spec drives a real browser or a real agent, and no other tier does.
- **`slow-example-moves-not-the-file`** — An example over budget moves out alone, never the whole file: its stub stays in the unit spec and its real run goes to the heavy spec beside it, under the same described subject.
- **`no-skipped-or-empty-test`** — No test is skipped, commented out, or left without an assertion.

**Speed**
- **`unit-example-within-100-ms`** — Every unit example runs within 100 ms, its before-each and after-each included.
- **`unit-file-within-2-seconds`** — A unit spec file runs within 2 s.
- **`unit-tier-within-25-seconds`** — The whole unit tier finishes in under 25 s of wall clock on an idle machine, because it runs in a sub-task while the person tries each change, and a slow unit tier stops being run.
- **`specs-run-in-parallel`** — A spec can run beside any other: no fixed port, no shared temp folder, no shared `CDD_HOME`, no order between files.
- **`heavy-spec-owns-its-resources`** — A heavy spec makes its own throwaway resources (repository, server port, `CDD_HOME`), so heavy specs can run in parallel too.
- **`expensive-fixture-built-once`** — A read-only fixture that is slow to build is built once per file and shared, not once per example.
- **`no-wait-in-unit-test`** — A unit test never sleeps or polls; time, retries, and timeouts come from a fake clock.
- **`budget-never-raised`** — The 100 ms, 2 s, and 25 s budgets are never raised to make a slow test pass; the test gets fast or moves tier.

**Stubs and heavy coverage**
- **`stubbed-boundary-has-heavy-coverage`** — Every boundary a unit spec stubs is run for real by a heavy or e2e example with the same `should` sentence under the same subject. A stub with none is unchecked and drifts from the real thing.
- **`heavy-example-has-a-stubbed-twin`** — Every heavy example has a stubbed twin in the unit spec beside it, so a break is caught after every pass and not only on the heavy cadence.

**Cadence**
- **`heavy-run-within-the-hour`** — The newest heavy run on main is under an hour old and passed, or its failure is open on the board.
- **`e2e-run-within-the-day`** — The newest e2e run on main is under a day old and passed, or its failure is open on the board.
- **`release-follows-a-green-e2e`** — A release tag points at a commit whose e2e and heavy runs passed.

## clean-engineering-code

Follow the flow. Crossing a boundary for the first time (Flow A), write the code and run it end to end for real before any unit test; on a known area (Flow B), write the unit test that needs a new class or operation before the code.

### Rules

- **`operation-has-a-proving-test`** — Every public operation is invoked by at least one observation or step.
- **`class-demonstrated-by-a-test`** — Every public class is demonstrated through an example or observation.
- **`invariant-has-a-failing-case`** — Every invariant has a test that tries to break it and sees the named failure.
- **`every-branch-taken-by-a-test`** — Every branch in a public operation's body is taken by some test.

## stories-acceptance-tests

One scenario at a time, in the flow's order. Flow A: run the scenario for real end to end, have the person verify it, turn it into the heavy or e2e story test, then write the stubbed domain tier. Flow B: domain tier red on its Then, code to green, the person tries it, then the heavy and e2e tiers in a sub-task. Stories' own acceptance-test rules (seeding at the real owner, stubs at the system boundary, one interaction's outcomes in one Then) stay Stories'.

## bdd-development

One `BDD: SIGNATURE` at a time, in the flow's order, with arrange-act-assert taken from the realization's call graph. Flow A fills the heavy or e2e signature first, against a path already run for real; Flow B fills the unit signature red, then green.

### Rules

- **`act-follows-the-realization`** — The act calls what the observation invokes, in the realization's order.

## ddd-tactics

Settle how each building block is tested when you choose its pattern, and prove it through its aggregate root.

### Rules

- **`aggregate-tested-through-its-root`** — Tests reach entities and values only through the aggregate root's operations.
- **`invariant-guarded-by-a-test`** — Each aggregate invariant has a test where an operation refuses to break it.
- **`value-object-tested-by-equality`** — A value object's tests prove equality by value and immutability.
- **`repository-tested-on-a-real-store`** — A repository has unit tests on the in-memory one and a heavy test on the real store.
- **`domain-service-tested-with-fakes-at-boundary`** — A domain service's tests fake its collaborators outside the domain and use its domain collaborators for real.
