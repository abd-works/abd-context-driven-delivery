---
always_apply: true
supplements:
  clean_engineering: code
  stories: [acceptance_tests, hardening]
  bdd: [development, hardening]
  ddd: tactics
---

## Overview

Test-driven development at implementation: every behavior is proven working for real before it is trusted, then kept proven by a test at the fastest tier that can prove it. TDD supplements the implementation fidelities of Clean Engineering (code), Stories (acceptance tests), BDD (development), and DDD (tactics); UX front-end code is not supplemented. It also supplements the hardening fidelities of Stories and BDD, where the whole release is made ready for production by exploratory testing and a regression run of every story, in its own section below. Its guidance is the process; its rules check what the finished tests and code show. It has no rules for every fidelity it supplements: each section of rules names the fidelities it is for. The graph checks `unit-tier-fakes-every-boundary` on BDD specs and on Stories acceptance tests, and `declared-exception-raised-by-a-test` on the classes of the code, and it lists candidates for `stubbed-boundary-has-heavy-coverage` on BDD specs and for `operation-has-a-proving-test` on the code's operations. Its overlay records what those rules read: each test file's tier, the real resources a unit test imports and the boundaries it stubs, whether a heavy or e2e spec has one of a unit spec's examples, and whether a test reaches each public operation and names each declared exception. Validate judges the rest. The tiers each module uses are recorded in the session's `session.json` as generate and render write its tests (Set up the tiers of a module, below).

## Guidance

### Choose the flow first

The order of work depends on whether the story crosses an architectural boundary for the first time. An area is **known** when an e2e or heavy test already runs real code across every architectural boundary the story touches. If any boundary is new (a new module seam, a new external system, a new tier), use Flow A for that boundary. Use Flow A too for a feature built for the first time, even inside a known area, and for a change the person has already corrected once and you are making again, such as a layout tweak that keeps coming out wrong: in both the risk is the same, a result nobody has seen work.

**Flow A — a new feature, a story that crosses an architectural boundary for the first time, or a change the person keeps correcting.** Run it for real first: the danger here is an AI that believes its own stubs.

1. **Run it end to end, directly.** Drive it through the real stack yourself (browser, server, store, agent), or ask the person to. Record every failure as it happens. On a screen, screenshot each Given, When and Then as you go, keyed story › scenario › step.
2. **Iterate until it works for real.** Judge each step's screenshot against its step text, as Stories acceptance tests says: the Given's state is visible, the When took effect, the Then shows the right values, labels and messages. Fix and walk again until every step meets it, then write the walk report (`harness/e2e_review/report/report.ts`). A person verifies the result by reviewing that report; accepting it makes the walk the reference. A human seeing the real thing work is the only way to rule out hallucination.
3. **Capture it in an e2e or heavy test.** Write the test that runs the same path end to end, and see it pass against the real stack, so the success cannot be hallucinated later. An e2e test records the same step screenshots; compare each with the accepted walk. Where they differ, fix the test or the code; when it is unclear which is right, walk that step again. When they all match, this run is the first baseline.
4. **Then write the stubbed and mocked unit tests,** only where a stub or mock was actually used, each checked against the real seam you just ran. An AI tends to stub critical functionality, or to put the stub at the wrong seam and fake what should be real.

The real run includes the error conditions, not only the main path. Run for real each edge and error case that applies to the new boundary, the ones `edge-and-error-cases-have-scenarios` (Stories scenarios) asks a story's scenarios to cover: input that is missing, malformed or past a limit; the same action twice; a second actor at the same moment; the action stopped partway; a dependency absent, slow or wrong; the thing changed or gone since it was last seen; an actor not allowed. The heavy or e2e test that captures the run holds those cases, because a stubbed test written afterwards can only fake the failures somebody has seen happen.

**Flow B — another story or feature on a known area.** The seams are proven, so the order reverses:

1. **Write the unit tests** on the seams that already exist, and see them fail for the right reason.
2. **Write the code and run only the tests for the change** — the specs of the files it touched — until they pass. Not the whole tier.
3. **Hand it to the person to try,** and while they test it, run the whole unit tier in a sub-task off the person's thread; report its result when it comes back.
4. **Write the heavy and/or e2e tests in a sub-task:** hand them to a background agent so the person is not kept waiting, and tell the person when they are done. An e2e run ends with a review of its screens against the baseline (Reviewing e2e screens, below).

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
| e2e | `*_e2e_spec`, `*_agent_spec`, `*.story.ui.spec.ts` and the other Playwright specs | Examples that drive a real browser or a real agent |

### Set up the tiers of a module

A module's tests use the unit tier, and a module that is an app uses more: the **server** tier when it publishes operations through the cdd server or another server, and the **web** tier when it shows a page. Which tiers a module uses, and the test tool of each, is recorded in the session's `session.json`, so the next story of that module is tested at every tier the module needs and not only at the one its author thought of:

```json
"test_tiers": {"space/kanban": {"unit": "mamba", "server": "mamba", "web": "playwright"}}
```

Nobody fills the record by hand when a session is set up. A generate or a render at Stories acceptance tests or BDD development fills it as it writes tests: the unit tier for each module the fidelity writes under, and the server or web tier of a module once a test file of that tier is there (`*.story.server.spec.*` is server, `*.story.ui.spec.*` is web). Where it cannot tell, such as a story test that sits under `story_tests/` and names no module, or a module with no server or web test yet, its reply asks you to decide and to record the answer with `session.record_test_tier` (the session, the module's folder, the tier, the test tool). Decide from the module's code, never from the story's wording: a class the module publishes as a tool of a server means the server tier, and a page the module serves or draws means the web tier.

Set up each tier a module uses before its first test at that tier:

1. **Unit:** the test tool of the module's language (Mamba for Python), with a fake at every architecture boundary. A story test's shared and domain tier files run here.
2. **Server:** a story test's server tier file (`{sub_epic_slug}.story.server.spec.*`) starts the real server, sends each operation the arguments its published schema names, and reads the answer the server sends back, because a test that calls the Python operation directly never meets the arguments a caller really sends.
3. **Web:** a browser story test (`{sub_epic_slug}.story.ui.spec.ts`, Playwright) opens the page against the real server and records a screenshot for each step, because a page can be wrong where no assertion looks.

The server tier runs with the heavy specs and the web tier with the e2e specs, on their cadence.

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
| e2e | Every day, before every release, and at the end of work that touches a browser or an agent; its screens are reviewed against the last accepted run before its result counts | The daily scheduled run and the release command |
| exploratory testing | Before every release, during hardening, once the release's stories pass their own tests and before the regression run, on the areas the release changed and the areas those changes could affect; and on the person's word after a change to an area that has produced defects no tier runs for real | The exploratory-testing supervisor, with tester robots on the prompt queue, each in its own sandbox; the person confirms the themes first, defects are reported as they are found, and defect-fixing robots, one for each isolated area of the code base, fix them with a commit for each fix |

Exploratory testing is not a tier of specs: it runs the product for real to find the defects no test was written for, and every defect it confirms gets a test at the tier that owns the behaviour (stories-hardening, bdd-hardening, below).

Read the runner's slow list after every whole-tier unit run and fix each example in the same pass, optimizing first. Keep the runner's timings (`.pycache/spec-seconds.json`): they order the next run's batches, longest first.

### Reviewing e2e screens

Passing e2e tests prove only the assertions someone wrote; a screen can break where no assertion looks (a field missing, a label changed, a layout collapsed, a notice no longer shown). So every e2e run, by ticket, by hand or scheduled, is reviewed screen by screen against the last run the person accepted. Each step of a browser story test records its screenshot and result in the run's `results.json` (Stories acceptance tests, `every-step-captured`); the review is `harness/e2e_review/report/review.ts`.

1. **Run the e2e tests.** Each step records its screenshot and result under `.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>/`.
2. **Compare each step with the last accepted run, by pixels.** A pair changed when more than 1% of its 8px blocks moved; only changed pairs go on.
3. **Give each changed pair a verdict and a reason:**
   - **intended:** cites the story or code change behind it (this ticket's changes, or for a scheduled run the commits on main since the baseline).
   - **regression caught:** a test already fails for it, named; fix the code.
   - **missed by the tests:** the screen is wrong and nothing failed; go to step 4.
   - **noise:** timing, animation, or a value the system mints; make the harness deterministic and rerun.
4. **For each miss, write the failing test at the layer that owns it** (Stories acceptance tests says which), see it fail, fix the code, and rerun.
5. **Repeat until every changed pair is intended.** The person reviews the compare report; accepting it makes the run the new baseline.

### When stuck

After two failed fixes for the same failure, stop and diagnose before a third: read the failure, reproduce it on its own, and find the cause.

## Shared rules

```yaml
alwaysApply: true
```

Whenever you are about to write production code or a test for it. Follow these rules.

- **`flow-chosen-before-code`** — Before writing production code or a test, say which flow each boundary the change touches is in, and work in that flow's order. **Flow A** is a boundary crossed for the first time, such as a new module seam, a new external system, a new process, or a new tier; a feature built for the first time; or a change the person has already corrected and you are making again: run it for real end to end, the error conditions of `edge-and-error-cases-have-scenarios` that apply as well as the main path, have the person verify it, capture it in a heavy or e2e test that holds those cases, and only then write the stubbed unit tests. On a screen, the person verifies it by the walk report's screen for each step, and the e2e test is compared with that walk. **Flow B** is a known area, where a heavy or e2e test already runs every boundary the change touches: write the unit test, see it fail for the right reason, then write the code. Tests written after the code, which pass on their first run, prove nothing they were not shaped to pass, and stubs written before a real run fake the very boundary nobody has seen work.

## stories-acceptance-tests, bdd-development

The tests Stories acceptance tests and BDD development write share their tiers, their speed, their stubs and heavy coverage, and the cadence they run on.

### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*.spec.shared.ts,**/*spec.js,**/*.spec.shared.js,**/*.story.*,**/*_story.test.*"
```

Whenever you create, alter, or delete acceptance tests or BDD specs. Follow these rules.

**Tiers**
- **`suffix-names-the-tier`** — `*_spec` is unit, `*_heavy_spec` is heavy, and `*_e2e_spec` / `*_agent_spec` / `*.story.ui.spec.ts` is e2e; a story test's tier file follows the same suffixes. A suffix that names the wrong tier puts a slow test in the run that must stay fast.
- **`unit-tier-fakes-every-boundary`** — A unit spec reaches no real resource: a fake sits at every architecture boundary. {{decided.unit_tier_fakes_every_boundary}}
- **`heavy-tier-holds-a-real-resource`** — A heavy spec uses a real resource (git, a server, a daemon, an installer, a worker, a big load); without one it belongs in the unit tier.
- **`e2e-tier-drives-browser-or-agent`** — An e2e spec drives a real browser or a real agent, and no other tier does.
- **`slow-example-moves-not-the-file`** — An example over budget moves out alone, never the whole file: its stub stays in the unit spec and its real run goes to the heavy spec beside it, under the same described subject.
- **`no-skipped-or-empty-test`** — No test is skipped, commented out, or left without an assertion.
- **`module-tiers-recorded`** — Before a test is written for a module, the session's `session.json` names the tiers the module uses and the test tool of each (`test_tiers`): unit for every module, server for one that publishes operations through a server, web for one that shows a page. Generate and render record what the test files show; record the rest with `session.record_test_tier`. A module with no record is tested at whichever tier its author thinks of first.
- **`story-tested-at-each-recorded-tier`** — A story of a module whose record names the server tier has a server tier test, and one whose record names the web tier has a browser test, each running that story's scenarios. Judged by validate: read the session's `test_tiers`, then the story's test files on the graph and the tier of each, because a story proven only at the unit tier has never met the arguments a server sends or the page a person sees.

**Speed**
- **`unit-example-within-100-ms`** — Every unit example runs within 100 ms, its before-each and after-each included.
- **`unit-file-within-2-seconds`** — A unit spec file runs within 2 s.
- **`unit-tier-within-25-seconds`** — The whole unit tier finishes in under 25 s of wall clock on an idle machine, because it runs in a sub-task while the person tries each change, and a slow unit tier stops being run.
- **`specs-run-in-parallel`** — A spec can run beside any other: no fixed port, no shared temp folder, no shared `CDD_HOME`, no order between files.
- **`heavy-spec-owns-its-resources`** — A heavy spec makes its own throwaway resources (repository, server port, `CDD_HOME`), so heavy specs can run in parallel too.
- **`expensive-fixture-built-once`** — A read-only fixture that is slow to build is built once per file and shared, not once per example.
- **`no-wait-in-unit-test`** — A unit test never sleeps or polls; time, retries, and timeouts come from a fake clock.
- **`noise-is-fixed-in-the-harness`** — A screen that changes between e2e runs only by timing, animation, or a value the system mints is made deterministic in the harness (a fixed clock, a fixed value, a settled page), never accepted as noise, because accepted noise hides the next real change behind it.
- **`budget-never-raised`** — The 100 ms, 2 s, and 25 s budgets are never raised to make a slow test pass; the test gets fast or moves tier.

**Stubs and heavy coverage**
- **`stubbed-boundary-has-heavy-coverage`** — Every boundary a unit spec stubs is run for real by a heavy or e2e example with the same `should` sentence under the same subject. A stub with none is unchecked and drifts from the real thing. The graph lists a unit spec that puts a stand-in somewhere (a mock, a patch, a spy, or a class named as a fake, a stub or a mock) while no heavy or e2e spec has any of its `should` sentences under its subject. Read each: the graph cannot tell whether the stand-in sits at an architecture boundary, and a heavy example worded another way covers it unseen. {{decided.stubbed_boundary_has_heavy_coverage}}
- **`heavy-example-has-a-stubbed-twin`** — Every heavy example has a stubbed twin in the unit spec beside it, so a break is caught after every pass and not only on the heavy cadence.

**Cadence**
- **`heavy-run-within-the-hour`** — The newest heavy run on main is under an hour old and passed, or its failure is open on the board.
- **`e2e-run-within-the-day`** — The newest e2e run on main is under a day old and passed, or its failure is open on the board.
- **`every-run-reviewed`** — Every e2e run, by ticket, by hand or scheduled, is compared screen by screen with the last accepted run, and every changed pair has a verdict with its reason, before the run's result counts; an intended change cites the story or code change behind it. A passing run nobody looked at can still show a broken screen.
- **`missed-change-adds-a-test-first`** — A screen change no test caught gets a failing test at the layer that owns the behaviour before the code is fixed, so the same break is caught by a test next time and not only by a screenshot.
- **`release-follows-a-green-e2e`** — A release tag points at a commit whose e2e and heavy runs passed.
- **`person-accepts-the-baseline`** — Only the person's acceptance makes a walk by hand the reference or an e2e run the baseline, and only once every changed pair is judged intended, because a baseline the agent moves on its own accepts whatever the agent got wrong.

## clean-engineering-code

Follow the flow. Crossing a boundary for the first time (Flow A), write the code and run it end to end for real before any unit test; on a known area (Flow B), write the unit test that needs a new class or operation before the code.

### Rules

- **`operation-has-a-proving-test`** — Every public operation is invoked by at least one observation or step. The graph lists each public operation with a body that no test it read reaches: no observation or step invokes it, no test code calls it, none of the ways the project reaches code besides calls and imports reaches it, and no operation a test reaches goes on to invoke it. The project names those ways in its `.context/config.json`, under `code_reach`: the decorators that publish an operation for a framework to call by name, the registries a class is registered with, the base classes a framework finds subclasses by, whose overrides it calls, the entry points its configuration starts, the naming conventions a framework finds code by, the files generated adapters call, and the operations an instruction file, such as a practice's recipe, tells an agent to call. A project that names none reaches code only by calls and imports, so every operation no test reaches is listed. A listed operation may still be tested through a call the graph cannot follow, such as a name the code builds or a call from another language, so read each before adding a test. It asks how the tests use the code across files, so validate runs it over the whole working copy, whatever paths it is given. {{decided.operation_has_a_proving_test}}
- **`class-demonstrated-by-a-test`** — Every public class is demonstrated through an example or observation.
- **`invariant-has-a-failing-case`** — Every invariant has a test that tries to break it and sees the named failure.
- **`declared-exception-raised-by-a-test`** — Every exception class the code declares is named by a test, the one that breaks its invariant and expects it. An exception no test names is a failure nobody has seen happen, so its message and what it carries are unchecked. It asks how the tests use the code across files, so validate runs it over the whole working copy, whatever paths it is given. {{decided.declared_exception_raised_by_a_test}}
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

## stories-hardening, bdd-hardening

Hardening makes the whole release ready for production. Implementation proved each story on its own; hardening looks at the release as one product, for the defects no story's tests were written to find and for the screens a change broke somewhere else. It has two parts, done in this order, and a release is ready when both are finished: first exploratory testing, which finds what the tests miss, and then, once its defects are fixed, a regression run, which shows that nothing already accepted has changed without a reason.

### Exploratory testing

An exploratory-testing supervisor hands out the testing, and tester robots do it (the `exploratory-testing-supervisor` and `exploratory-testing-tester` agents, `.claude/agents/`). The session's `exploratory-testing/` folder keeps the record: the themes, the charters, one file per defect, and the final report.

The scope is the areas the release changed, and the areas those changes could affect, such as the callers of a changed module or a screen that shows a changed value. It is not the entire system, unless the person says otherwise. Testing spread over the whole product finds only shallow defects, and the regression run that follows covers every story's screens.

1. **Analyse the changed areas and propose test themes.** Find what the release changed (its tickets and commits since the last release) and what depends on it. Within that scope, read the story map, the scenario files and story tests under `story_tests/`, and the defects already known (fix commits, the backlog, handoffs). For each sub-epic count its scenarios and its tests at each tier, and set the known defects beside the counts. A theme is a kind of behaviour that produced defects and that no tier runs for real, such as two callers changing one file at the same time, or an install stopped partway. Write each with its evidence to `exploratory-testing/coverage-themes.md`, because a theme without evidence sends a robot to an area the tests already cover.
2. **Take the themes from the person.** Show the proposed themes and let the person confirm, drop, or add to them before any robot starts. The person knows where the product hurts in ways the code and the tests do not show, and a robot sent to a theme nobody agreed to spends the session on the wrong risk.
3. **Write one charter for each theme.** A charter is a short mission, `Explore <area> as <persona> with <data> to discover <risk>`, with its sandbox folder, its own throwaway `CDD_HOME`, its test data, and what is out of bounds. Keep them in `exploratory-testing/charters.md`. Giving each robot its own sandbox and data keeps two robots from changing one another's results or the person's real sessions.
4. **Run several queue robots at once, each on its own theme.** Put each charter on the prompt queue as its own card (`prompt-queue.add`), give it to a named robot (`prompt-queue.assign`), and start one sub-agent for each robot from the tester agent, handing it its card's words exactly. Robots working at once cover the release in the time one robot takes for a single theme, and the queue shows the person which robot holds which theme.
5. **Report each defect to the shared defect area as it is found.** Each robot writes one file per defect to `exploratory-testing/defects/` (the steps, what was expected, what was seen, and the tier that should have caught it) and queues a `[defect]` card at once, not at the end of its run. One shared folder lets a robot see that a defect is already reported, and a defect reported as it is found can be fixed while testing goes on.
6. **Give each defect card to a dedicated defect-fixing robot.** Run one or more defect-fixing robots beside the testers, one for each isolated area of the code base, such as a module whose files no other fixing robot changes, and assign each `[defect]` card to the robot that owns the area where the failure shows (`prompt-queue.assign`). A tester never fixes: it keeps testing while the fix is made. One fixing robot for each area lets fixes go on at once without two robots changing the same files.
7. **Fix each defect test first, and commit after each fix.** The fixing robot reproduces the defect from the report alone, and marks it confirmed, not reproduced, or works as intended, with its severity. Every confirmed defect gets a scenario and a test, seen failing first, at the tier that owns the behaviour (Flow A when the boundary has never been run for real), then the fix. The robot commits that one defect's test and fix by themselves, naming the defect's file, before it takes its next card, because a commit that holds several fixes cannot be reverted or traced to one defect when a fix breaks something else.
8. **Report and close.** Each tester writes its report: what it tested, what it found, and what it thinks is still at risk. The final report sets the defects out by story and by module, each with the commit that fixed it, because a defect fixed with no test comes back in the next release.

### Regression

Regression runs after exploratory testing is done: every defect it found is fixed and committed, and its final report is written. Then run the e2e tier for every story of the release, on the commit that holds those fixes, and review every screen against the last official release. A regression run made while defects are still being fixed judges screens that the next fix changes, so it has to be run again. Implementation reviews a ticket's e2e run against the last run the person accepted (Reviewing e2e screens, above); hardening does the same for the whole release against the last release's accepted run, because a change made for one story can break the screen of another story that no ticket touched.

1. **Run every story's e2e tests** (`e2e-review.run` for each sub-epic, or the release's e2e run), so each step records its screenshot and result.
2. **Have an AI judge compare each step with the last official release's accepted run.** Only the pairs whose pixels changed go to the judge (`e2e-review.changed_pairs`, then `e2e-review.judge_step`).
3. **Give every changed pair a verdict with its reason** (`e2e-review.record_verdict`): intended, citing the story or commit behind it; regression caught; missed by the tests; or noise, as `every-run-reviewed` asks. A missed change gets its failing test first (`missed-change-adds-a-test-first`).
4. **The person accepts the run** (`e2e-review.accept`), as `person-accepts-the-baseline` asks, and it becomes the baseline the next release is compared with.

### Rules

```yaml
alwaysApply: false
globs: "**/exploratory-testing/**,**/e2e-test-results/**"
```

Whenever you harden a release for production, by exploratory testing or a regression run. Follow these rules.

**Exploratory testing**
- **`themes-confirmed-by-the-person`** — Every theme in `exploratory-testing/coverage-themes.md` carries its evidence and was confirmed or added by the person before any robot started, because robots sent to themes nobody agreed to test the wrong risks.
- **`scope-is-what-the-release-changed`** — Every theme lies in an area the release changed or an area those changes could affect, and names the change behind it; a theme outside that scope is there because the person asked for it. Robots spread over the entire system test each area thinly and miss the defects the changes made.
- **`one-robot-per-theme`** — Every theme has a charter on the prompt queue, assigned to its own named robot with its own sandbox and `CDD_HOME`, because two robots on one theme or one sandbox report each other's changes as defects.
- **`every-theme-has-a-robot-report`** — Every theme has its robot's report: what it tested, the defects it found, and what it thinks is still at risk. A theme without a report was never tested, and the release looks covered where it is not.
- **`defects-reported-as-found`** — Every defect is one file in the shared defect area, `exploratory-testing/defects/`, with its steps, what was expected and seen, and the tier that should have caught it, and has a `[defect]` card on the queue, because a defect kept until the end of a robot's run cannot be fixed or matched against other reports while testing goes on.
- **`defects-fixed-by-a-robot-per-code-area`** — Every `[defect]` card is assigned to a dedicated defect-fixing robot that owns the area of the code base where the failure shows, and no two fixing robots change the same files, because a tester that stops to fix leaves its theme untested and two robots fixing in one area overwrite each other's work.
- **`every-defect-triaged`** — Every defect is marked confirmed, not reproduced, or works as intended by someone other than its reporter, with its severity, and every confirmed defect has a scenario and a test seen failing first, so the next release's tests catch it.
- **`one-commit-per-defect-fix`** — Every fixed defect has a commit of its own, made as soon as its test passes and holding only that defect's test and fix, because a fix committed together with others cannot be reverted or traced to its defect.

**Regression**
- **`regression-after-exploratory-testing`** — The regression run is made after exploratory testing has finished, on a commit that holds every defect fix, because a run made before the last fix accepts screens that fix then changes.
- **`every-story-run-at-e2e`** — Every story of the release has an e2e run made on the release's commit, because a story left out of the run is a screen nobody checked before production.
- **`every-story-judged-against-the-last-release`** — Every story's e2e screens are compared with the last official release's accepted run, and every changed pair has a verdict with its reason (`every-run-reviewed`); the release is ready only when every changed pair is intended and the person has accepted the run (`person-accepts-the-baseline`). A run judged against anything newer than the last release can hide a break made since it.
