## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

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

When this BDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

## Shared rules

Use these rules when nesting describe / that / with / it should — subjects and states, never internals.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

#### Overview


**Default format:** Python
**Stage:** specification

**Goal:** Define BDD signatures — describe/it names for every observation, no test bodies.

#### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

#### Rules

Use these rules when defining BDD signatures — describe/it names only, no test bodies yet.

- **`state-not-when`** — Nest by the state or condition that enables an observation, never by a `when` trigger.
- **`nest-by-enabling-events`** — Sub-groupings are conditions that unlock further behavior, not implementation steps.
- **`context-setup-expresses-state`** — Setup under a label must establish that label's state, not unrelated host boot.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — Refer to [`practices/language-tools.md`](/practices/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

#### Template

"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to practices/language-tools.md for tool recommendations.
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
from practices.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')
