# TDD content inventory

## 1. Purpose and how to read it

This is the raw material for one common TDD practice or overlay. It gathers every piece of testing guidance in this repository (worktree `C:\dev\abd-cdd-tdd-practice`, branch `tdd-practice`) as it stands on 2026-11-14. It is an inventory, not a guideline: each entry quotes or closely paraphrases a source and cites `path:line`. Nothing here is a new rule. Where two sources disagree, section 4 says so and does not pick a winner.

Read section 2 to see which files hold testing advice and whether an agent ever sees them. Read section 3 theme by theme; each theme lists every source's version together. Section 4 lists the duplications, conflicts and broken pointers. Section 5 shows which fidelity consumes which piece.

"Delivered" means an agent receives the text. Every practice markdown file is delivered in full: each fidelity is an MCP tool (for example `bdd-development`, `clean-engineering-code`) and a skill (`practices-bdd-bdd-development`), and the tool returns the fidelity's schema, the practice Overview, Guidance and Shared rules, the fidelity's Overview, Guidance and Rules, and its template. So the procedures, RED-GREEN-REFACTOR and AAA do reach the agent (checked on 2026-11-15 by calling `bdd-development`). The `## Shared rules` and `#### Rules` sections are also installed under `.claude/rules/` by path. What is not delivered are files outside a practice markdown file: separate rule files under a practice's `rules/` folder (such as `testing-approach.md`) and the persona files under a practice's `agents/` folder.

## 2. Inventory

| Source file | Practice / fidelity | What it covers | Delivered? |
|---|---|---|---|
| `cdd_guidance/practices/clean_engineering/rules/testing-approach.md` | Clean Engineering (claims all code tests) | Test shape ladder: real conditions first, stub TDD at boundaries, e2e swap; `_spec` / `_e2e_spec` layout | **No.** Not part of a practice markdown file; front matter says `alwaysApply: true` (`:4`) but no installed rule, skill or MCP tool output contains "shape ladder" (`clean-engineering-code` and `bdd-development` output checked) |
| `cdd_guidance/practices/bdd/bdd.md` shared rules (`:100-119`) | BDD, all fidelities | Observable behaviour, usage order, describe naming, `that`/`with` not `when`, setup expresses state, coverage, rule-example pairs | Yes, `.claude/rules/practices/bdd.md` |
| `cdd_guidance/practices/bdd/bdd.md` behavior (`:123-177`) | BDD behavior | Confirm framework, `BDD: SIGNATURE` markers, no implementation | Yes, in full through its fidelity MCP tool and skill; Rules also in `.claude/rules/` |
| `cdd_guidance/practices/bdd/bdd.md` development (`:248-324`) | BDD development | Procedure (pointer to ladder), coverage check, RED-GREEN-REFACTOR, AAA, rules incl. `tier-by-speed` | Yes, in full through its fidelity MCP tool and skill; Rules also in `.claude/rules/` |
| `cdd_guidance/practices/bdd/bdd.md` Common mistakes (`:328-388`) | BDD | Nesting, setup labels, missing subject | Yes, part of the practice text the BDD tools return |
| `cdd_guidance/practices/bdd/templates/bdd.py`, `bdd.ts`, `bdd-sketch.md` | BDD | SIGNATURE → realization → AAA, one assertion per behaviour | Yes, the fidelity tool returns its template |
| `cdd_guidance/practices/bdd/agents/behavior-developer.md` | BDD agent persona | Red-green-refactor one signature at a time | **No** (`.claude/agents/` holds only context, discoverer, implementation, specification) |
| `cdd_guidance/practices/stories/stories.md` scenarios (`:127-155`) | Stories scenarios | Rules that also bind acceptance tests (explore surface, reconcile live, seed prior story as Given) | Yes, `rules/practices/stories/stories-scenarios.md` |
| `cdd_guidance/practices/stories/stories.md` acceptance_tests (`:172-238`) | Stories acceptance_tests | Pointer to ladder, develop one scenario at a time, failing test first, seed/stub/fixture rules, `story-tier-by-speed` | Yes, in full through its fidelity MCP tool and skill; Rules also in `.claude/rules/` |
| `cdd_guidance/practices/stories/templates/py/scenarios.py`, `ts/scenarios.ts`, `py/story_test.py`, `ts/story-test.ts` | Stories acceptance_tests | Lifecycle hooks, assertion helpers, `examples/` fixture layout, GWT step library | Yes, the fidelity tool returns its template |
| `cdd_guidance/practices/clean_engineering/clean_engineering.md` code (`:264-341`) | Clean Engineering code | No test procedure at all; "implement real behaviour", "update tests on rename" | Rules yes, `rules/practices/clean-engineering/clean-engineering-code.md` |
| `cdd_guidance/practices/clean_engineering/agents/engineer.md` | CE agent persona | "Always test-then-code-then-test", MUST follow the ladder | **No** |
| `cdd_guidance/practices/agent_bdd/agent_bdd.md` (+ `guide.md`) | Agent BDD | Harness rules, assert on artifacts, no mocking the harness, triage prompt vs code | Yes, `rules/practices/agent-bdd.md` (shared rules) |
| `cdd_guidance/practices/ux/ux.md`, `ux/guidance/front_end_code.md`, `ux/guidance/mockup.md` | UX mockup, front_end_code | Stub catalogue honesty; no fake backend as the only path | Rules yes, `rules/practices/ux/*.md` |
| `cdd_guidance/practices/ddd/ddd.md` tactics (`:287`, `:321`) | DDD tactics | One test approach per building block | Rules yes, `rules/practices/ddd/ddd-tactics.md` |
| `cdd_guidance/agents/implementation.md` | Implementation agent | TDD red-green-refactor, no stubs left, run tests after each slice | Yes, `.claude/agents/implementation.md` |
| `cdd_guidance/rules/test-timing.md` | Always-on | Which tier to run when | Yes, `.claude/rules/test-timing.md` |
| `cdd_guidance/rules/coding.mdc` | Always-on | Update tests in the same change as a renamed seam | Yes, `.claude/rules/coding.md` |
| `cdd_guidance/references/language-tools.md` | Reference (BDD, Stories, CE, agent BDD point here) | Runners, assertion libraries, story file shape, universal AAA / one assertion / example factories | Yes, `.claude/references/language-tools.md` |
| `AGENTS.md:38-55` | Project instructions | Setup, mamba command, tier table, Mamba spec style | Yes, loaded through `CLAUDE.md` (`@AGENTS.md`) |
| `scripts/test.ps1` | Runner | Tier selection, 100 ms budget, throwaway `CDD_HOME`, agent runs off outside e2e | Script, not guidance |
| `cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.md` | LERN overlay | Shared-story tiers, Playwright, BDD tiers with drivers, real server tier | Yes, `rules/patterns/lern-domain-driven.md` |
| `cdd_guidance/patterns/mern_domain_driven/mern_domain_driven.md` | MERN overlay | Tier/stub table, example factories, test scripts | Yes, `rules/patterns/mern-domain-driven.md` |
| `cdd_guidance/patterns/oss_portal_domain_driven/oss_portal_domain_driven.md` | OSS portal overlay | LERN tiers plus service, BFF, journey tests | Yes, `rules/patterns/oss-portal-domain-driven.md` |
| `cdd_guidance/patterns/cdd_claude_mod/cdd_claude_mod.md` | Claude mod overlay | Same signatures across languages, `claude plugin test`, surface heavy spec | Yes, `rules/patterns/cdd-claude-mod.md` |
| `cdd_guidance/patterns/cdd_web_domain_access/cdd_web_domain_access.md` | Web domain access overlay | Adapter tests against a real cdd server on a throwaway project | Yes, `rules/patterns/cdd-web-domain-access.md` |
| `.context/principles/context-as-code-strategy.md` | Principle (capture of existing apps) | Real seam, stub vs mock, one micro-increment, per-tier story files | No |
| `cdd_guidance/practices/stories/.context/stories-guidance-assessment.md:314-321` | Stories assessment | Brownfield observation vs greenfield TDD (open decision) | No |

## 3. Themes

### 3.1 Test shape ladder / real conditions first

- **testing-approach.md** — "Test real conditions first — **no automated tests**; do it manually. Discover real shape, then test with stubs and lock fast regression tests, then extend with real conditions from the first pass. **Every error is an additional test.**" (`testing-approach.md:13`). Mandatory, "no stub-first shortcuts" (`:11`). Applies to unit BDD, agent BDD and story ATDD; `@bdd` and `@stories` "refer here instead of duplicating" (`:9`).
  1. Discover with real conditions: no stub or mock on the subject or integration path; AI utility = real sub-agents (`@agent_bdd`), never mock the harness; website = running app, reconcile live; backend = real or documented local endpoint; learn the real shape first; write only a test *signature* for every failure met (`:15-20`).
  2. Stub TDD (fast suite): only after step 1 and once code works; "two-pass tests" with stubs/mocks at architecture boundaries only; stubs MUST match observed real shape; run on every change (`:21`).
  3. E2E swap (on request): separate class or file, same signature and assertions, real collaborators; afterwards run only when the user asks (`:22`).
- **stories.md acceptance_tests** — "Use the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/`: start with the real application when it is available, use deterministic external-system stubs while developing, and replace them with end-to-end boundaries when requested." (`stories.md:202`)
- **bdd.md development** — "Follow the **Test shape ladder** in `@clean_engineering` `## code` § Procedure — real conditions first, then stub TDD, then e2e swap on request." (`bdd.md:266`) — target does not exist (see 4).
- **engineer.md** — "When writing or testing code you **MUST** follow the test shape ladder in `@clean_engineering` `## code` § Procedure (`code-procedure`)." (`engineer.md:8`) — same missing target.
- **agent_bdd.md** — `no-mocking-the-harness`: agent specs test the real agent end to end (`agent_bdd.md:35`, `:69`).
- **stories.md scenarios** — `explore-full-interaction-surface`: inspect every visible behaviour of the source or running product before generating acceptance tests (`stories.md:140`); `reconcile-live-immediately` in brownfield work (`:142`); `flagged-writes-intended-gwt` when evidence cannot exercise behaviour (`:143`).
- **context-as-code-strategy.md** — "Walk each scenario against the **real seam** of the layer you are proving, then lock that confirmation into a **runnable story**" (`:5`); "Do not stub the seam you are proving" (`:65`, `:94`).
- **stories-guidance-assessment.md** — asks for two declared evidence modes: brownfield capture (observed behaviour outranks sketches) and greenfield specification (tests begin RED) (`:314-321`). Not decided anywhere in the guidance.
- **Pattern real tiers** — LERN `server-tier-calls-the-real-thing` and `e2e-runs-the-whole-stack` (`lern_domain_driven.md:557-558`); OSS `service-tier-runs-a-real-database` (`oss_portal_domain_driven.md:530`); web access `test-the-adapter-against-real-cdd` (`cdd_web_domain_access.md:391`); Claude mod `prove-it-on-the-real-surface` (`cdd_claude_mod.md:343`).

### 3.2 Red-green-refactor and one test at a time

- **bdd.md development procedure** (`bdd.md:270-277`): confirm framework; scan and count `BDD: SIGNATURE` markers; extract shared setup at three siblings; pick **one** marker, use the realization call graph for Act, fill AAA from the template; run and "confirm RED for the right reason"; write the **minimum** production code to GREEN; refactor only while green; repeat until zero markers, then run validate.
- **bdd.md RGR section** — RED fail for the right reason before production code exists; GREEN least code; REFACTOR while green; "One test, one production change, one green — do not batch all bodies first." (`bdd.md:288-292`)
- **bdd.md rules** — `red-then-green` (`:316`), `minimum-green` / `code-minimalism` (`:317`), `one-signature-at-a-time` (`:318`), `hierarchy-preservation` 1:1 from sketch (`:315`).
- **bdd.md coverage check** — before RGR on an existing module, walk the tree for missing subjects/states/outcomes; not one `it` per public member (`bdd.md:279-286`); also `full-surface-coverage` (`:118`) and "scan production source for coverage gaps before filling signatures" (`:9`).
- **stories.md acceptance_tests** — "Take one Scenario at a time: write the failing acceptance test, invoke the Clean Engineering companion at `code` fidelity, implement the smallest production change that can pass, rerun the test, refactor when it is green, and then continue to the next behaviour. After two failed fix attempts, diagnose the failure before changing more code." (`stories.md:206`). Also "Develop the behaviour, not only the test" (same line).
- **behavior-developer.md** — "drive production code through red-green-refactor one signature at a time" (`:8`); development = replace each signature with AAA, minimum code to green, refactor while green, until zero signatures (`:13`).
- **engineer.md** — "You always follow test-then-code-then-test (BDD red-green-refactor) even when other guidance does not explicitly call for it." (`:8`)
- **implementation.md** — "Use test-driven development (red-green-refactor) and complete real integrations" (`:10`); `bdd-development` "one test signature at a time" (`:24`); completion needs "zero remaining test signatures in scope, passing test suites" (`:34`).
- **agent_bdd.md** — "The **`bdd`** generator supplies the underlying test discipline (RED-GREEN, AAA, mocks, minimalism, shared setup)." (`:7`)
- **Patterns** — "Specs first, small RED cycles" (`cdd_claude_mod.md:271`; `lern_domain_driven.md:485`; `oss_portal_domain_driven.md:448`); "Generate writes the acceptance tests first" (`lern_domain_driven.md:6`, `mern_domain_driven.md:6-7`, `oss_portal_domain_driven.md:7`); "Add any missing domain operation and its Mamba spec first" (`cdd_web_domain_access.md:343`).
- **context-as-code-strategy.md** — one micro-increment at a time (one story, one BDD describe, or one aggregate operation); "Run tests until green, repeat" (`:51`, `:61`).
- **testing-approach.md** — order is different: real manual run first, failures recorded as signatures only, stub tests written "once code works" (`:13`, `:20-21`).

### 3.3 Stubs, mocks and boundaries

- **bdd.md** `layer-isolation` — "Mock only at architecture boundaries; never the subject under test. Mocking the subject tests the mock, not your code." (`bdd.md:320`)
- **testing-approach.md** — stubs/mocks at architecture boundaries only, never the subject; stubs MUST match the observed real shape (`:21`); step 1 has no stub on the subject or integration path (`:15`).
- **stories.md** `system-stubs-domain-real` — inspect the real integration contract again; the stub reproduces that boundary's operations, structures, identifiers, state changes and failures; no simpler test API; keep aggregates, repositories, validation, mapping and transitions real (`stories.md:232`). `separate-test-controls-from-production-contracts` — seed/reset/inspect operations live on a test adapter or stub, not the production contract (`:231`). `story-tier-by-speed` — "stubs at external systems, the domain real and in memory" (`:238`).
- **agent_bdd.md** `no-mocking-the-harness` (`:35`, `:69`); "Do not: ... mock the harness or the agent" (`:88`).
- **context-as-code-strategy.md** — definitions: a mock "proves what went out", a stub is "a canned neighbor response" (`:22`); frontend: stub the next layer and mock the call; backend: real HTTP in, stub downstream (`:24`); write the minimum stubs at the outermost boundary; take non-core stubs from the owning aggregate's folder, never invent one inside a story test (`:65`).
- **AGENTS.md** — unit tier: "Use fakes (`MockGit`) and shared fixtures." (`AGENTS.md:49`)
- **bdd.md** `tier-by-speed` — make a slow example fast "with a fake at the architecture boundary or a fixture built once and shared" (`bdd.md:324`).
- **Production stubs (not test doubles)** — CE code: "Fill every empty body — a stub ships as a silent no-op" (`clean_engineering.md:289`); implementation.md: no "stubs, fake persistence, demo-only UI" left (`:10`); UX front_end_code: replace mockup stubs, "not Fake factory or in-browser demo domain alone" (`ux.md:211-212`, `front_end_code.md:7-8,14-18`), `real-backend-wired` (`ux.md:234`); UX mockup: list every faked behaviour (`ux.md:161`, `:187`; `mockup.md:29-31`); LERN/MERN `implement-full-interfaces`, no stub no-ops (`lern_domain_driven.md:537`, `mern_domain_driven.md:147`).
- **Testability through design** — CE modules: an implicit dependency is hard to "replace in a test" (`clean_engineering.md:91`); CE model: a dependency not in the constructor "cannot be swapped for a test double" (`:197`).
- **Pattern stub policies** — MERN table: server tier stubs nothing; client tier stubs the HTTP client via `vi.mock`; e2e stubs nothing (`mern_domain_driven.md:98-103`); `{Type}ExampleFactory` `Isolated` = ctor-injected mocks, `Production` = real collaborators (`:108-110`). LERN server tier: no `vi.mock`, `vi.fn` or spy (`lern_domain_driven.md:557`); Playwright tier: the page "with the API answered from examples" (`:413`); e2e: no stub, no intercepted request (`:558`); lowdb `Memory` in tests (`:190`), in-memory repository proves the entity (`:326-327`). OSS: BFF spec with "the gateway answered from examples" (`oss_portal_domain_driven.md:392`). Claude mod: `claude plugin test` with stubbed MCP (`cdd_claude_mod.md:252`, `:344`); the stubbed kit cannot see layout or a stale stub, hence the surface heavy spec (`:343`). Web access: "a stubbed tool would still pass after the Python changed" (`cdd_web_domain_access.md:336`, `:391`).
- **language-tools.md** — Java mocking: Mockito (`:31`).

### 3.4 Fixtures and seed state

- **bdd.md** `context-sharing` — shared construction in `beforeEach` / factory "at three sibling dupes" (`bdd.md:321`; also procedure step 3, `:272`, and AAA, `:296`). `context-setup-expresses-state` — setup under a `that`/`with` must establish that label's state; host boot goes in a parent context labelled as started (`:117`; worked mistakes `:340-364`). `oo-api-design` — tests that assemble state through getters or setup bags couple to construction (`:322`).
- **stories.md acceptance_tests** — "Represent each named scenario example as one code fixture, and do not invent fixture values the scenario does not name." (`:206`). Rules: `examples-declare-seed-vs-interaction` (`:228`), `shared-example-fixtures` shaped from the owning system (`:229`), `seed-state-at-its-real-owner` (`:230`), `assert-domain-behavior-not-seeded-state` (`:233`), `infrastructure-in-lifecycle-hooks` — load an aggregate once at the highest Given (`:234`), `domain-operations-inline-in-steps` — shared prior state seeded with a `seed…` fixture (`:236`).
- **stories.md scenarios** `seed-prior-story-as-given` — seed later Stories from prior Stories' examples, do not replay their When (`:154`).
- **scenarios.py template** — fixtures under `examples/` at the lowest shared folder (epic, sub-epic, story), one file per domain concept, never repeat literals (`templates/py/scenarios.py:43-52`); same in `ts/scenarios.ts`.
- **language-tools.md** — "Example Factories: Isolate test data generation into sibling `*_example_factory` files." (`:47`)
- **context-as-code-strategy.md** — fixtures and `givens.ts` "sit at the lowest folder that actually shares them"; do not hoist (`:187`); folder tree `:168-180`.
- **Patterns** — LERN `examples/<concept>.examples.ts`: "exports data, not a repository" (`lern_domain_driven.md:357`); `reset-every-repository` before each story (`:551`); `tier-bound-repository-accessor` (`:548`). MERN `{Type}ExampleFactory` over hand-rolled fixtures (`mern_domain_driven.md:107-110`); `use-thorough-e2e-tests`: no blanket deletes between tests (`:152`). Claude mod: "Seed what an earlier version stored" (`cdd_claude_mod.md:344`).
- **test.ps1 / AGENTS.md** — "shared fixtures" in the unit tier (`AGENTS.md:49`); specs get a throwaway `CDD_HOME` per run and per batch (`scripts/test.ps1:54-56`, `:199`).

### 3.5 Test structure

- **Arrange-Act-Assert** — bdd.md: "Label Arrange / Act / Assert; one observable outcome per `it`" (`:294-296`); procedure step 4 (`:273`); template `bdd.py:22-27` ("Use Arrange / Act / Assert comments... One assertion per behavior"), `bdd.ts:7`; language-tools "Every test behavior should clearly separate these three phases" (`:45`); bdd-sketch: development turns realization graphs into AAA (`bdd-sketch.md:16`); realization: keep Arrange surface lines separate from the Act call graph (`bdd.md:213`).
- **One outcome per test** — bdd.md `one-assertion-per-test` (`:319`), `observable-behavior` (`:109`); language-tools "One Assertion per Behavior" (`:46`), "Behavioral Outcomes" (`:48`); AGENTS.md "one outcome per `it`" (`:55`).
- **Given / When / Then** — stories.md `inline-simple-gwt-bodies` (`:235`), `domain-operations-inline-in-steps` (`:236`), `extract-assertion-helper` after more than twice (`:237`); `when-holds-the-operation` (`:148`); `and-chaining` — one interaction's results in one Then/And block (`:151`); templates: `then` then `and_`, lifecycle hooks in `before.all` / `after.all`, not `given()` (`scenarios.py:30-41`, `:67-86`); LERN/OSS `no-expect-in-given` (`lern_domain_driven.md:549`, `oss_portal_domain_driven.md:532`), `outline-entries-loop-over-examples` (`lern:550`, `oss:533`).
- **describe / that / with** — bdd.md tree guidance (`:9-90`) and shared rules `usage-order-behaviors`, `describe-is-subject-not-internal`, `describe-is-plain-english`, `shared-describe-subject`, `state-not-when`, `nest-by-enabling-events` (`:111-116`); AGENTS.md "`describe` a domain subject, nest `with` / `that` states (never `when`), one outcome per `it`, ordered as a usage story" (`:55`). Behavior fidelity `no-implementation` and `framework-syntax` with `BDD: SIGNATURE` (`bdd.md:165-166`).
- **Agent BDD** — `act-assert-inline`: act → assert → act → assert in one `it`, no `before.all` (`agent_bdd.md:26`, `:63`, `:82`).
- **Same sentence across languages** — Claude mod `identical-signatures-across-languages` (`cdd_claude_mod.md:341`); LERN `same-signature-across-languages` (`lern_domain_driven.md:560`); web access (`cdd_web_domain_access.md:336`).
- **Mechanical rule specs** — `scan-fixture-pair`: use the practice's `rules/rule_examples.py` pair asserter (`bdd.md:119`; template `bdd.py:61-68`).

### 3.6 Tiers and speed

- **bdd.md** `tier-by-speed` (`bdd.md:324`): suffix names the tier; unit `*_spec` examples run in microseconds to milliseconds with before/after each; runner fails over budget (100 ms); heavy `*_heavy_spec` needs a real resource (git, server, daemon, installer, worker, big load); e2e `*_e2e_spec`, `*_agent_spec` drive a real browser or agent; a slow example gets fast or moves to the heavy spec under the same described subject; only slow examples move; never raise the budget.
- **stories.md** `story-tier-by-speed` — domain tier `.story.domain.spec` within the unit budget; a tier that starts a real server, app or install is `..._heavy_spec`; one that drives a browser or agent is `..._e2e_spec` (`stories.md:238`).
- **AGENTS.md** tier table (`:47-53`): unit = `*_spec.py`, `*_story.test.py`, story tiers, 100 ms `-ExampleBudgetMs`; heavy = `*_heavy_spec.py`, one file at a time; e2e = `*_e2e_spec.py`, `*_agent_spec.py`, the only tier that may start an agent. Points to `tier-by-speed` (`:53`).
- **scripts/test.ps1** — header restates tiers (`:5-11`); `-ExampleBudgetMs 100` includes before/after each (`:15-16`); unit tier collects `*_spec.py` and `*.story.*.spec.py` minus heavy/e2e/agent (`:294-298`); files over budget in parallel rerun alone, still-slow ones fail with "make them fast, or move them to a *_heavy_spec.py" (`:309-334`); heavy runs one process at a time (`:337-342`); `CDD_AGENT_RUNS_OFF` outside e2e (`:276-277`).
- **testing-approach.md** — two files only: `{module}_spec.py` always, `{module}_e2e_spec.py` on explicit e2e request (`:24-29`); no heavy tier.
- **Pattern tiers** — LERN story tiers `.story.shared.ts` / `.story.domain.spec.ts` / `.story.server.spec.ts` / `.story.playwright.ts` (`lern_domain_driven.md:351-357`) and BDD tiers shared / domain / server / Playwright / e2e with a driver (`:405-423`), `domain-tier-only-for-domain-logic` (`:559`); MERN domain unit / server / client / e2e (`mern_domain_driven.md:98-103`); OSS shared / domain / service / BFF / Playwright / journey e2e (`oss_portal_domain_driven.md:387-394`), `journey-test-per-release` (`:531`); Claude mod Mamba domain, tool spec, `claude plugin test`, `claude plugin validate`, `tsc -p` (`cdd_claude_mod.md:254-260`) plus `*_surface_heavy_spec.py` (`:343`).

### 3.7 When to run which tier

- **test-timing.md** (always-on): unit after each pass (seconds to a minute; fails over-budget examples); heavy once at the end, fix and rerun; e2e when the work touches a browser capture or an agent, also once at the end; push after unit passes and say which tiers remain; a single change runs unit then the heavy specs of touched modules (`test-timing.md:8-17`).
- **testing-approach.md** — fast suite "run on every change"; e2e "only when the user asks for e2e / integration / full stack" (`:21-22`).
- **implementation.md** — "Execute relevant automated tests and validation commands after each small behavior slice and across the completed scope" (`:34`).
- **bdd.md** — run validate after zero markers remain (`:277`); `tier-by-speed`: "A unit tier that takes minutes stops being run after each change, and then it catches nothing." (`:324`); stories `story-tier-by-speed`: domain tier runs after every change (`stories.md:238`).
- **Patterns** — Claude mod: run `claude plugin validate`, `tsc -p`, `claude plugin test` and Mamba (`cdd_claude_mod.md:276`); surface heavy spec only on a surface that reloaded the current mod and server (`:343`); web access: type-check, tests, validate (`cdd_web_domain_access.md:347`); MERN/LERN/OSS `scaffold-test-scripts` keep Vitest and Playwright separate (`mern:151`, `lern:546`, `oss:534`); MERN e2e needs the real frontend served (`mern:152`).

### 3.8 Language tools

- **language-tools.md** — TS: Vitest (or Jest), `expect`, `expect.poll` (`:11-12`); copy `story-test.ts` once per tests tree, LERN puts it in `test-utils/story-test/` (`:13`); one `{story_snake}_story.test.ts` per story, "Do not emit front-end / back-end / e2e files, and do not use `.spec.`" (`:14`). Python: Mamba for BDD specs, Mamba via `story_test.py` for stories, Expects assertions (`:19-21`); one `{story_snake}_story.test.py` per story, not `_spec.py`; boot/teardown in `before.all` / `after.all` (`:23`); run with `python -m story_test` (`:24`). Java: JUnit 5, AssertJ, `@Nested` for describe, Mockito, `{Story}StoryTest.java` (`:28-35`). Universal concepts (`:43-49`).
- **bdd.md** behavior — "Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those." (`:142`); `framework-syntax`: one framework, no mixing (`:166`).
- **AGENTS.md** — `.venv/bin/mamba --format documentation path/to/thing_spec.py` (`:40-43`).
- **Pointers** — bdd.md `:5`, `:166`, `:268`; stories.md `:208`; clean_engineering.md `:285`; agent_bdd.md `:5`; templates `bdd.py:3`, `bdd.ts:3`, `scenarios.py:7`.

### 3.9 Agent BDD specifics

- Harness: `same-harness-interface`, `steps-on-the-block` (`agent_bdd.md:15-16`).
- `instruct-for-setup`, `instruct-run-for-toolset`, `fenced-yaml-contract` (local YAML replay fallback) (`:20-22`).
- `act-assert-inline`, `session-file-per-scenario` (`:26-27`).
- `assert-on-response-fields` (cheap, deterministic, does not prove work finished), `assert-on-run-artifacts` (file on disk, not chat claims), `judge-qualitative-outcomes` (`ai_judge` on artifact text; `generate_and_judge` for pass fixtures), `instruction-expansion-ok-to-judge-prose`, `no-mocking-the-harness` (`:31-35`).
- `timeout-per-instruct` 300 s default, 300–600 s for long actions (`:39`).
- Failures: `triage-prompt-vs-code`; `code-failure-needs-vanilla-bdd` — fix code and add the vanilla mamba BDD that would have caught it; `prompt-failure-stays-on-agent-bdd` (`:43-45`).
- Shared rules repeat all of the above in one line each (`:58-73`); "# Generate" steps and "Do not" list (`:76-88`) are repeated verbatim in `practices/agent_bdd/guide.md:1-11`.
- Tier: `*_agent_spec.py` is e2e; only e2e may start an agent (`AGENTS.md:51`, `scripts/test.ps1:10-11`, `:88-92`, `:276-277`). Ladder step 1 names agent BDD for AI utilities (`testing-approach.md:16`).

### 3.10 Pattern (stack) specific rules

| Pattern | Testing rules and sections |
|---|---|
| LERN | Testing architecture (`lern_domain_driven.md:344-376`), Testing with BDD (`:378-423`), Generate step 3 (`:479-485`); rules `reduce-story-overlap`, `scaffold-test-scripts`, `playwright-tests-browser-interaction`, `tier-bound-repository-accessor`, `no-expect-in-given`, `outline-entries-loop-over-examples`, `reset-every-repository` (`:545-551`); `shared-behavior-stays-tier-free`, `tier-runs-shared-behavior`, `server-tier-calls-the-real-thing`, `e2e-runs-the-whole-stack`, `domain-tier-only-for-domain-logic`, `same-signature-across-languages` (`:555-560`) |
| MERN | Testing architecture (`mern_domain_driven.md:91-113`); `test-story-driven`, `scaffold-test-scripts`, `use-thorough-e2e-tests` (`:150-152`) |
| OSS portal | Testing architecture (`oss_portal_domain_driven.md:379-394`); `reduce-story-overlap`, `service-tier-runs-a-real-database`, `journey-test-per-release`, `no-expect-in-given`, `outline-entries-loop-over-examples`, `scaffold-test-scripts` (`:529-534`) |
| Claude mod | Testing architecture (`cdd_claude_mod.md:250-260`); `identical-signatures-across-languages`, `spec-the-tool-boundary`, `prove-it-on-the-real-surface`, `test-the-mod-through-the-engine` (`:341-344`) |
| Web domain access | Testing (`cdd_web_domain_access.md:334-336`); `test-the-adapter-against-real-cdd`, `act-on-a-throwaway-project` (`:391-392`) |

Also DDD tactics: settle "how it is tested" per building block (`ddd.md:287`), `one-pattern-per-building-block` (`:321`).

## 4. Duplications, conflicts and gaps

**Broken pointers**
1. `bdd.md:266` and `engineer.md:8` send the reader to "`@clean_engineering` `## code` § Procedure" (`code-procedure`). `clean_engineering.md` code fidelity (`:264-341`) has Overview, Sketch, Guidance, Scaffold, Rules; no Procedure, and no testing guidance at all. The ladder lives only in `clean_engineering/rules/testing-approach.md`.
2. `testing-approach.md` says it is always-on (`:4`) and that `@bdd` and `@stories` "refer here" (`:9`), but it is never delivered: it sits outside the practice markdown, no file under `.claude/` and no fidelity tool output contains "shape ladder", and no `.py` file names `testing-approach`. Only `stories.md:202` points at it by its real location.
3. `bdd.md:146`, `:216`, `:273` name `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`) with "DEVELOPMENT TESTS" and "PRODUCTION CODE" sections. The files are `templates/bdd.py` and `templates/bdd.ts` (no Java); `bdd.py` has a "DEVELOPMENT" block (`:22-27`) and no production-code section.
4. `agent_bdd.md:11`, `:80` name `templates/agent_bdd-templates.py`; the file is `templates/agent_bdd.py`.

**Conflicts**
5. Order of test and code. BDD (`bdd.md:274-276`, `:316`), Stories (`stories.md:206`), the agents and the patterns ("Specs first, small RED cycles") write a failing test before production code. The ladder says first run real conditions with "no automated tests" (`testing-approach.md:13`), record failures as signatures only (`:20`), and write stub tests "once code works" (`:21`). The Stories assessment (`stories-guidance-assessment.md:314-321`) names the same tension (brownfield vs greenfield) as an open decision.
6. Tiers. `tier-by-speed`, AGENTS.md and test.ps1 have three tiers (unit, heavy, e2e). The ladder has two files (`_spec`, `_e2e_spec`) and no heavy tier (`testing-approach.md:24-29`).
7. When e2e runs. Ladder: only when the user asks (`testing-approach.md:22`). test-timing: whenever the work touches a browser capture or an agent, once at the end (`test-timing.md:14`).
8. Story test file names. Stories acceptance_tests outputs are `{sub_epic_slug}.story.shared|domain.spec|server.spec.{py,ts}` (`stories.md:179-186`, `:198`). language-tools says one `{story_snake}_story.test.{ts,py}` per story, no `.spec.`, and no front-end/back-end/e2e files (`language-tools.md:14`, `:23`); the scenarios templates say the same (`scenarios.py:17-18`, `scenarios.ts:12-13`). context-as-code-strategy uses `{story-name}.front-end.ts` / `.back-end.ts` per tier (`:96-105`).
9. Server story tier speed. `story-tier-by-speed` says a tier that starts a real server is a `..._heavy_spec` (`stories.md:238`), but the acceptance_tests outputs name it `.story.server.spec.*` (`:182`, `:186`), and test.ps1 puts every `*.story.*.spec.py` into the unit tier (`scripts/test.ps1:294-295`). LERN's server tier calls a real store or MCP tool (`lern_domain_driven.md:557`) under `.server.spec.ts`.
10. Example data location and name. language-tools: sibling `*_example_factory` files (`:47`). scenarios templates: `examples/` folders, one `*.examples.py` per concept (`scenarios.py:43-52`). LERN: `examples/<concept>.examples.ts` exporting data (`lern_domain_driven.md:357`). MERN: `{Type}ExampleFactory` with Isolated/Production modes (`mern_domain_driven.md:107-110`). context-as-code: `examples/` plus `givens.ts` (`:168-180`).
11. One assertion per test vs. chained outcomes. BDD and language-tools require one outcome per `it` (`bdd.md:319`, `language-tools.md:46`). Stories keeps all of one interaction's results in one Then/And block (`stories.md:151`; `scenarios.py:30-33`). Agent BDD runs act → assert → act → assert in one `it` (`agent_bdd.md:26`).
12. Shared setup. BDD extracts shared setup to `beforeEach` at three siblings (`bdd.md:272`, `:321`). Agent BDD forbids `before.all` and `self.*` accumulation (`agent_bdd.md:26`, `:82`). Stories wants simple GWT bodies inline (`stories.md:235`).

**Duplications (same idea, different words)**
13. Mock only at boundaries: `bdd.md:320`, `testing-approach.md:21`, `stories.md:232`, `stories.md:238`, `context-as-code-strategy.md:22-24`.
14. RED-GREEN-REFACTOR, one at a time: `bdd.md:270-277`, `:288-292`, `:316-318`; `stories.md:206`; `behavior-developer.md:8,13`; `engineer.md:8`; `implementation.md:10,24`; `agent_bdd.md:7`; pattern "Specs first, small RED cycles" (3 files).
15. Tier rules: `bdd.md:324` (`tier-by-speed`), `stories.md:238` (`story-tier-by-speed`), `AGENTS.md:47-53`, `scripts/test.ps1:5-11`, `test-timing.md:8`.
16. AAA and one outcome: `bdd.md:294-296`, `:319`; `language-tools.md:45-48`; `bdd.py:22-27`; `AGENTS.md:55`.
17. Shared-setup threshold "three": `bdd.md:272`, `:296`, `:321`; Stories `extract-assertion-helper` "more than twice" (`stories.md:237`).
18. Same `should` sentence across languages: `cdd_claude_mod.md:341`, `lern_domain_driven.md:560`, `cdd_web_domain_access.md:336`.
19. Real tier, no stubs: LERN `server-tier-calls-the-real-thing` (`:557`), OSS `service-tier-runs-a-real-database` (`:530`, labelled as LERN's), web access `test-the-adapter-against-real-cdd` (`:391`).
20. LERN rules copied into OSS with "*(LERN)*" tags (`oss_portal_domain_driven.md:529`, `:532-534`).
21. Agent BDD content three times: Guidance (`agent_bdd.md:13-45`), Shared rules (`:58-73`), Generate (`:76-88`) = `agent_bdd/guide.md:1-11`.
22. Production "no stubs left" (not a test rule but often read as one): `clean_engineering.md:289`, `implementation.md:10`, `ux.md:211-212,234`, `front_end_code.md:7-8,14-18`, LERN/MERN `implement-full-interfaces`.

**Gaps**
23. Clean Engineering `code` — the fidelity that writes production code — holds no test procedure, no test rule, and no pointer to the ladder; only the persona `engineer.md` (not delivered) says to follow one.
24. UX `front_end_code` says nothing about how the front end is tested; only the patterns (LERN Playwright, MERN client tier, Claude mod `claude plugin test`) do.
25. The procedural pieces (BDD procedure, RGR, AAA, coverage check; Stories "one Scenario at a time", "two failed fix attempts") are Guidance. They reach the agent through the fidelity MCP tools and skills, but not as path rules under `.claude/rules/`, so an agent editing a spec without calling the fidelity tool sees only the Rules.
26. "Two-pass tests" (`testing-approach.md:21`) is not defined anywhere.
27. The "two failed fix attempts then diagnose" stop rule exists only in Stories (`stories.md:206`).
28. Agent personas `engineer.md` and `behavior-developer.md`, which carry the strongest test-first wording, are not delivered: not installed as agents and not part of any practice markdown a tool returns.

## 5. Which fidelities consume which pieces

Legend: **O** = the fidelity's own text states it; **P** = it points to it; **I** = an always-on installed rule applies to it; blank = nothing found.

| Piece | CE `code` | Stories `acceptance_tests` | BDD `development` | Agent BDD | UX `front_end_code` |
|---|---|---|---|---|---|
| Test shape ladder (`testing-approach.md`) | (persona `engineer.md:8` P, broken) | P (`stories.md:202`) | P, broken (`bdd.md:266`) | ladder names it (`testing-approach.md:16`) | |
| Red-green-refactor, one at a time | | O (`stories.md:206`) | O (`bdd.md:270-292`, `:316-318`) | P to bdd (`agent_bdd.md:7`) | |
| Coverage check before RGR | | O (`stories.md:140`, scenarios rule) | O (`bdd.md:279-286`) | | |
| Mock only at boundaries / stubs match real | | O (`stories.md:231-232`) | O (`bdd.md:320`) | O, no mocking harness (`agent_bdd.md:35`) | |
| No stubs in shipped code | O (`clean_engineering.md:289`) | | | | O (`ux.md:211-212`, `:234`) |
| Fixtures and seed state | | O (`stories.md:206`, `:228-236`) | O (`bdd.md:117`, `:321`) | session file per scenario (`:27`) | |
| AAA / one outcome per test | | GWT + and-chaining (`stories.md:151`, `:235-237`) | O (`bdd.md:294-296`, `:319`) | act-assert-inline (`:26`) | |
| describe / that / with | | | O (shared rules `bdd.md:109-119`) | via bdd (`:11`) | |
| Tier by speed | | O (`stories.md:238`) | O (`bdd.md:324`) | e2e tier (`AGENTS.md:51`) | |
| When to run each tier (`test-timing.md`) | I | I | I (points back to `tier-by-speed`) | I | I |
| Language tools reference | P (`clean_engineering.md:285`) | P (`stories.md:208`) | P (`bdd.md:268`) | P (`agent_bdd.md:5`) | |
| Update tests on renamed seam | O (`clean_engineering.md:335`), I (`coding.mdc:11-15`) | I | I | I | I |
| Pattern overlays (LERN, MERN, OSS, Claude mod, web access) | pattern rules name CE code as fallback (`lern:501`, `mern:133`, `oss:469`) | patterns pin Stories `acceptance_tests` / typescript (`lern:6`, `mern:6-13`, `oss:7,15`) | LERN Testing with BDD (`lern:378-423`, `:555-560`) | | patterns only (LERN Playwright, MERN client tier, Claude mod pane tests) |
| Implementation agent (`implementation.md`) | loads `clean-engineering-code` (`:23`) | loads `stories-acceptance-tests` (`:20`) | loads `bdd-development` (`:24`) | | loads `ux-front-end-code` (`:22`) |
