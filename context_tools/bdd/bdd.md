# Contexts

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Hierarchy shape (required)

```
describe {subject — domain thing, state, or observable condition}
  that {event or condition that sets the subject up}
    with {narrower condition}
      it should {observable outcome}
```

| Line | Names | Never names |
| --- | --- | --- |
| **describe** | Subject under observation in plain English (thing, state, condition) | Manager / hub / runner / service / internal class; decorator symbol (`@log`); marker name |
| **that …** | Past or present event/condition on that subject (`that has been logged`, `that is invoked`) | `when …` |
| **with …** | Narrower standing condition (`with no session name given`, `with verbose off`) | `when …`; implementation knobs phrased as API flags |
| **it should …** | One stakeholder-visible outcome | Internals, private fields, call counts on mocks of the subject |

**Fail:**
```
@log marker                          ← mechanism / symbol, not a subject
ToolsetRunner                        ← manager / internal
a logged tool                        ← splits the same subject; use one action story
when no session name is given        ← never "when" for state — use "with …"
```

### Mental model

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe`. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Select from these three layer types and arrange them to flow:

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. `"during a flash sale, that has been submitted, with items in the cart"` does not. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior.
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

**Shared Rules:**

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …).
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`full-surface-coverage`** — When generating or satisfying tests for a module that already exists, scan the production source for every public method, property, class, and constant. Each must have at least one `it should` covering its observable behavior. Any gap is a violation. Private and underscore-prefixed members are excluded unless they are part of a documented public contract.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

---

This skill operates at **multiple levels of fidelity**. Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity. Least detail → most detail below.

| Fidelity | Output |
|---|---|
| **modules** | Thin subject index — top-level `describe`s with candidate `that`/`with` + TODOs (partition pass) |
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **development** | Implemented tests + production code |

## modules

**Default format:** markdown

**Goal:** Name the BDD subject tree before behavior signatures — delegates module structure to Clean Engineering at the same depth.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ## behavior / ## development below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

Rough subject index for a **partition** pass or first cut — domain things, states, or observable conditions (top-level `describe`s); subject + candidate `that`/`with` + TODOs. Not full `it should` suites.

Key rules: `state-not-when` — nest by the state or condition that enables an observation, never by a `when` trigger; `nest-by-enabling-events` — sub-groupings are conditions that unlock further behavior, not implementation steps.

## behavior

**Default format:** Python

**Goal:** map observation to a real test before implementation. Lock the sketched hierarchy as framework `describe` / `it` nesting. Every `it` body is exactly one `BDD: SIGNATURE` marker — nothing else.

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed 
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

### Rules

- **`hierarchy-preservation`** — 1:1 from sketch nesting to code. Nothing added, removed, or flattened. Same depth, same `it` count.
- **`signature-markers`** — Every `it` body is exactly `// BDD: SIGNATURE` or `# BDD: SIGNATURE`.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

## development

**Default format:** Python

**Goal:** Replace `BDD: SIGNATURE` markers one at a time with it shgould /expect bodies, then minimum production code until green. Inherit the framework from the **behavior** artifactif already completed.

**Procedure:** Follow the **Test shape ladder** in `@clean_engineering` `## code` § Procedure — real conditions first, then stub TDD, then e2e swap on request.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

### Coverage scan (existing code)

When generating or satisfying against a module that already exists, read the production source before touching the spec:

1. List every public method, property, class, and constant (exclude `_`-prefixed members unless publicly documented).
2. Compare against the existing spec to find members with no `it should` entry.
3. Add `it should` entries (at behavior fidelity) or full test bodies (at development fidelity) for every gap — do not skip any public member.
4. Only then proceed with RED-GREEN-REFACTOR for the new or updated tests.

### The RED-GREEN-REFACTOR cycle

**RED** — fail for the right reason before production code exists.  
**GREEN** — least production code that makes this assertion pass.  
**REFACTOR** — clean up while green. One test, one production change, one green — do not batch all bodies first.

### Arrange-Act-Assert

Label Arrange / Act / Assert; one observable outcome per `it` (`observable-behavior` above). Split unrelated expects. Shared construction → `beforeEach` / factory at three sibling dupes.

### Rules

- **`red-then-green`** — Fail for the right reason before production code changes.
- **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass.
- **`refactor-only-when-green`** — Refactor only while green.
- **`one-signature-at-a-time`** — One marker → green → next. Do not batch all bodies first.
- **`one-assertion-per-test`** —  one outcome per `it`. tighly connects `expects`
- **`layer-isolation`** — Mock only at architecture boundaries; never the subject under test.
- **`no-remaining-signatures`** — Zero `BDD: SIGNATURE` markers when done.
- **`full-surface-coverage`** — Before generating or satisfying, scan the production source for all public members. Add `it should` entries for every uncovered public method, property, or class. Complete coverage is required; no public surface may be left untested.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.
- **`roundtrip-parity-is-required`** — Adapter parse/render seams assert `counts(parse(render(canonical))) == counts(canonical)`.
- **`code-source-of-truth-guard`** — Tests reject unsafe regeneration when generation can overwrite hand-edited code.
- **`impl-must-carry-bdd-manifest`** — Impl paired with `*_spec.py` carries `# @toolset-manifest … context_tools.bdd.bdd:Bdd`.
- **`observable-behavior`** — Assert public outcomes only.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

---

## Story acceptance (Python)

Story files import **`story_test.py`** — it extends **Mamba** with **`with given`**, **`with when`**, **`with then`**, **`with and_`**, and **`with background.all` / `with background.each`** (like **`with before.all` / `with before.each`**). Run with **`python -m story_test`**. Unit BDD specs keep plain `description` / `context` / `it`.