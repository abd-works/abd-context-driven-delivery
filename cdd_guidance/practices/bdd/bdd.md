## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage. At development fidelity, scan production source for coverage gaps before filling signatures.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe` — everything below inherits it, so the wrong subject at the top misplaces every behavior under it. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Nesting means each condition is set up once and everything inside adds to it — easier to follow, and no rebuilding the same state in every test. Select from these three layer types and arrange them to flow: 

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior — a nested block only makes sense if the parent state has to hold for the behavior to happen.
```
describe an account
  that is premium
    with a linked payment method
      [Behaviors for fully active premium users]
      that belongs a minor
      [Behaviors for minors linked premium users account]
```

**Share** when multiple channels or implementations produce the same observable behavior but each has a few unique behaviors of its own. Define the shared behaviors once, include them per channel, add only the deltas.
```
shared_examples "onboarding a new mobile customer"
  that selects a plan
    it should display the selected plan details
    it should show the monthly cost
  that provides identity verification
    it should validate the customer's ID
    it should create a pending account
  that completes payment
    it should activate the mobile line
    it should send a welcome confirmation

describe onboarding through the web
  it_behaves_like "onboarding a new mobile customer"
  that uploads a selfie for verification
    it should match the selfie against the ID photo

describe onboarding through voice
  it_behaves_like "onboarding a new mobile customer"
  that speaks the verification code
    it should confirm identity via voice match

describe onboarding through the retail store
  it_behaves_like "onboarding a new mobile customer"
  that scans the physical ID at the counter
    it should verify the document in real time
```

**Promote** when a condition repeated inside many areas is actually a core state that other behaviors sit inside. Pull it to the outermost boundary and nest everything under it.
```
before:                                     after:
describe a Payment                          describe a Payment
  that is submitted                           with an expired token       *promoted
    with an expired token  ←repeated            that is submitted
    with a valid token                            it should reject
  that is refunded                              that is refunded
    with an expired token  ←repeated              it should reject
    with a valid token                          that is disputed
  that is disputed                                it should reject
    with an expired token  ←repeated            that checks balance
    with a valid token                            it should reject
  that checks balance                           that generates statement
    with an expired token  ←repeated              it should reject
    with a valid token                        with a valid token
  that generates statement                      that is submitted
    with an expired token  ←repeated              it should process
    with a valid token                          that is refunded
                                                  it should process
                                                ...
```

Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **realization** | Same hierarchy; each `it should` carries the domain call graph (`->` / `<-`) for Act and observable side effects |
| **development** | Implemented tests + production code |

## Shared rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you write or reshape describe / that / with / it-should specs, or code that is supported by these specifications. Follow these rules.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`shared-describe-subject`** — Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

## Fidelities

### behavior

```yaml
default_format: python
stage: discovery
clean_engineering: model
```

#### Overview

Define BDD signatures — describe/it names for every observation, no test bodies.

#### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you name or re-nest describe/it signatures, change code that relies on those signatures, or change specifications that need this kind of rename. Follow these rules.

If this change will not stay here, follow `practices/bdd.mdc`.

- **`state-not-when`** — Nest by the state or condition that enables an observation, never by a `when` trigger.
- **`nest-by-enabling-events`** — Sub-groupings are conditions that unlock further behavior, not implementation steps.
- **`context-setup-expresses-state`** — Setup under a label must establish that label's state, not unrelated host boot.
- **`shared-describe-subject`** — Same rule as shared rules (above); at behavior fidelity, scan the spec file for repeated top-level `describe` prefixes before adding another subject line.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

### realization

```yaml
default_format: markdown
stage: specification
clean_engineering: model
```

#### Overview

Expand each agreed `it should` into the domain call graph that executes that observation — sketch fidelity only (signatures and collaborator calls, no bodies). Notation matches `@clean_engineering` **model** interactions (`->` outbound, `<-` return). This fidelity does not restate GWT scenarios; it traces the describe/`that`/`with` tree already fixed at **behavior**.

#### Sketch

Ask which public operation on the subject under test each observation exercises, which collaborators participate, and what crosses an external-system boundary. Write the graph from a read of production code at those seams.

#### Guidance

- **Default on** after **behavior** signatures exist, unless the user says **no realizations**.
- Walk implementation from the outermost domain entry for the observation; strip pass-through helpers and language-native noise; stop at external systems with `[ExternalSystem]` at the boundary (same rules as `@practices/stories/story-realizations`).
- Keep Arrange surface lines (`-> subject = new …`, property sets) separate from the nested call graph under the Act that the observation proves.
- Store graphs on observations in the BDD model: fenced blocks in `templates/bdd-sketch.md`, round-tripped through `practices/bdd/model` (same call-graph conversion as stories and clean engineering).

Fill the **realization** section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`) — call-graph comments or structured `realization` data beside each `BDD: SIGNATURE` until **development** replaces them with real Arrange / Act / Assert.

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md,**/*-realization.md"
```

Whenever you add or change call graphs on BDD observations, or change production code those graphs describe. Follow these rules.

If this change will not stay here, follow `practices/bdd/bdd-behavior.mdc`.

- **`strip-helpers-to-domain-calls`** — Same rule as story realizations: show the domain call the helper delegates to.
- **`full-call-graph-per-observation`** — Follow every named domain or external-system collaborator from the entry operation through returns; do not stop at the first hop.
- **`external-systems-at-their-boundary`** — Label `[ExternalSystem]` at the seam; do not recurse inside vendor code.
- **`no-typescript-internals`** — Omit framework and language-native steps unless the observation is entirely infrastructure.
- **`sketch-fidelity`** — Signatures and interaction arrows only; no assertions, mocks, or production imports in the realization artifact.
- **`hierarchy-preservation`** — One graph per `it should`; do not add or remove observations when deepening to realization.

**Pass:** an `it` whose body is only call-graph comments (or `BDD: SIGNATURE` plus `# ->` lines) naming real domain operations.

**Fail:** assertions, mocks, or invented collaborators not traced to source.

---

### development

```yaml
default_format: python
stage: implementation
clean_engineering: code
```

#### Overview

Implement BDD tests with production code.

#### Guidance

**Procedure:** Follow the **Test shape ladder** in `@clean_engineering` `## code` § Procedure — real conditions first, then stub TDD, then e2e swap on request.

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Use the **realization** call graph for Act when present; otherwise derive Act from the observation label and domain model. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

#### Coverage check (existing module)

When generating or satisfying against a module that already exists, check the behavior tree before touching the spec:

1. Walk the describe/`that`/`with` tree for subjects, states, branches, or outcomes with no `it should`.
2. Compare against the usage story and observable behaviors the module is meant to support.
3. Add hierarchy and `it should` entries for missing behaviors — not one entry per public member on the class.
4. Then proceed with RED-GREEN-REFACTOR.

#### The RED-GREEN-REFACTOR cycle

**RED** — fail for the right reason before production code exists.  
**GREEN** — least production code that makes this assertion pass.  
**REFACTOR** — clean up while green. One test, one production change, one green — do not batch all bodies first.

#### Arrange-Act-Assert

Label Arrange / Act / Assert; one observable outcome per `it` (`observable-behavior` above). Split unrelated expects. Shared construction → `beforeEach` / factory at three sibling dupes.

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you create, alter, or delete production code supported by BDD specs, or the specs themselves. Follow these rules.

If this change will not stay here, follow `practices/bdd/bdd-behavior.mdc`.

- **`hierarchy-preservation`** — 1:1 from sketch nesting to code. Nothing added, removed, or flattened. Same depth, same `it` count. Changing the tree during implementation drops behaviors that were agreed on, or adds ones nobody specified.
- **`red-then-green`** — Fix code by writing the test first, then watching it fail, then making production code changes.
- **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass. Refactor only while green.
- **`one-signature-at-a-time`** — Implement and test one `BDD: SIGNATURE` at a time — get it passing before moving to the next. Do not fill in every test body first and try to make them all pass together.
- **`one-assertion-per-test`** — One outcome per `it` — two outcomes in one test and a failure does not tell you which behavior broke.
- **`layer-isolation`** — Mock only at architecture boundaries; never the subject under test. Mocking the subject tests the mock, not your code.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes. Repeated setup in every test hides what actually differs between them.
- **`context-setup-expresses-state`** — Same rule as behavior (above). At development fidelity, `before.each` is Arrange: it must express the parent context's named state, not smuggle host boot under a domain classification branch.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept. Tests that assemble state through getters or pass setup bags couple to how you built it, not what it does.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.

---

## Common mistakes still being made

Scratch pad — mistakes people still make against this practice. Each entry: the mistake, an example, what should have happened instead. (Disposition TBD.)

### Not nesting contexts properly

**Mistake:** Repeating the same top-level `describe` subject with only a trailing qualifier, or nesting `that` / `with` layers that do not read as one enabling sentence (setup grouped for file convenience instead of state).

**Example:** Two top-level describes in one spec file: `a bare agentic toolset registered for deploy` and `a bare agentic toolset with mcp-published operations registered for deploy`, each with its own install `before.each`. Or a configuration branch *outside* install while a sibling repeats the same `that has been deployed to Cursor` wrapper.

**What should have happened:** One outer `describe` for the shared subject (`an agent toolset registered for deploy`). Branch with sibling contexts (`that has been installed … from operations not marked mcp` vs `… marked mcp`). Shared subject promotion is also what **`shared-describe-subject`** flags.

### Treating results of install as install configuration

**Mistake:** Naming an **outcome on the tree** (assembled artifacts, deployed skill files, MCP enrollment) in a `with` context that sits **above** the context whose `before.each` runs install — so the label sounds like a precondition or fixture choice instead of something true **after** install.

**Example:**

```python
with context("with fidelity artifacts assembled in one install pass"):
    with context("that has been deployed to Cursor"):
        with before.each:
            Installer(ide="Cursor", path=self.tree).install([SamplePracticeWithFidelities()])
```

**What should have happened:** Install state first; outcome contexts nested under it:

```python
with context("that has been installed to Cursor from practice guidance with fidelity markdown sections"):
    with before.each:
        Installer(ide="Cursor", path=self.tree).install([SamplePracticeWithFidelities()])
    with context("with fidelity artifacts assembled in one install pass"):
        with it("should emit the practice skill, practice rules, fidelity skills, and fidelity rules in one pass"):
            ...
```

Read the parent label and `before.each` together: **`context-setup-expresses-state`** — the setup must establish the state the label names; observables on the install tree belong under `that has been installed …`, not as a peer that implies a second way to “configure” the same subject.

### Missing the core subject under test

**Mistake:** Naming the actor, the mechanism, or one part as the subject. The tree then hangs contexts off the installer, the annotation, or the path, and you never see the thing the examples are actually about.

**Example:** Installer specs kept opening `an installer deploying to an IDE path`, and a Guidance context that listed skill, MCP, and rules annotations. The subject under test is the installed CDD toolset. Guidance is one part of that toolset. Instructions and rules are parts of Guidance. Installed, and to a path, are states of the toolset.

**What should have happened:** Name the core subject first. Then name its subcomponents. From each subcomponent, derive the nested contexts (what it is made of), the events (what has already happened to it), and the expectations (what you can observe).

```
an agent toolset                          ← subject
  with operations annotated for installation   ← subcomponent
    that are annotated as skills and commands
      it should write a skill file for each of them
  that is a Guidance toolset              ← subcomponent
    with instructions
    with rules
  that has been installed                 ← event on the subject
    to a path                             ← where that event landed
      that has been cleansed
        it should remove the published skill
```

Do not open a new describe for the installer, the path, or the annotation when those are a state or a part of the same subject.

---
