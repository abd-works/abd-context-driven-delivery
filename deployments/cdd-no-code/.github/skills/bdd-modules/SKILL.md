---
name: bdd-modules
description: "Provide guidance for creating behavior skeletons and development tests."
disable-model-invocation: true
---

# bdd-modules

Use bdd guidance at `modules` fidelity only.

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

### Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage.

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

**Shared Rules:**

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
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

## Sketching

When sketching, use the sketch template at `bdd/templates/bdd-sketch.md`. Do not use the produce templates below — stop reading this skill when sketching.

## Templates

### markdown

"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to context_tools/language-tools.md for tool recommendations.
# =============================================================================
# BEHAVIOR (SIGNATURE) — `signature-markers`
# Every `it` body is exactly `# BDD: SIGNATURE` — nothing else.
#
# with description('{DomainEntity}'):
#     with context('that has been created'):
#         with it('should have {initial property} assigned'):
#             # BDD: SIGNATURE
# =============================================================================
# DEVELOPMENT — `no-remaining-signatures`
# Replace each `# BDD: SIGNATURE` with Arrange / Act / Assert. Zero markers when done.
# Instructions:
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Use Arrange / Act / Assert comments in test bodies.
#   3. One assertion per behavior.
# =============================================================================
"""
from mamba import description, context, it, before
from expects import equal, expect
from {domain_module} import {DomainEntity}

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_data())
            # Assert
            expect(entity.property).to(equal(expected_value))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            # Act
            self.entity.{action}({input})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))

        with it('should {second behavior}'):
            # Arrange
            {local_setup} = {value}
            # Act
            self.entity.{action}({local_setup})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from context_tools.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')

See examples in `context_tools/bdd/examples/` if needed.