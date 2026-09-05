# Concepts — abd-bdd-development

For shared BDD theory (what BDD is, the three phases, observable behavior, domain practice alignment) see `../../../reference/bdd-concepts.md`.

This file covers concepts specific to the development phase.

---

## The RED-GREEN-REFACTOR cycle

BDD development follows the same discipline as TDD. The cycle has three positions:

**RED** — write the test body so it is specific enough to fail for the right reason. The production code either doesn't exist yet (import fails, class not found) or doesn't satisfy the assertion. A test that passes before production code exists is not a test — it is a false signal.

**GREEN** — write the minimum production code that makes the failing test pass. Not the elegant code. Not the future-proof code. The code that satisfies this specific assertion and no more.

**REFACTOR** — clean up now that the test is green and protected. Remove duplication, rename, extract. The test must stay green throughout. Refactoring after green is when you earn clean code; doing it during RED risks changing behavior while there is no safety net.

In BDD development with signature files, the cycle runs signature by signature:
1. Replace one `// BDD: SIGNATURE` with an Arrange-Act-Assert body → RED
2. Implement the production code until it is GREEN
3. Refactor if needed → still GREEN
4. Move to the next signature

Do not implement all test bodies before writing any production code. One test, one production change, one green.

---

## Arrange-Act-Assert

Every test body follows the same three-part structure:

```typescript
// Arrange — set up preconditions and inputs
const voucher = new Voucher({ code: 'SUMMER10', discount: 0.1 });
const order = new Order({ items: [{ price: 100 }] });

// Act — call the production code under test
const result = voucher.apply(order);

// Assert — check the observable outcome
expect(result.totalDiscount).toBe(10);
```

Each test has exactly one assertion — one observable outcome being verified. When you find yourself writing multiple expects, each checking a different thing, split the test.

---

## Mock boundaries

Mocks exist to replace a module boundary defined by the architecture — an external service, an infrastructure adapter, a framework integration point. They do not replace the domain classes you are testing.

**Mock:** the payment gateway adapter when testing the order service.
**Do not mock:** the `Order` class when your test IS for `Order`.

When you mock the object under test, you are testing the mock, not the production code. Nothing useful is verified.

**Where mock boundaries come from:** the architecture specification defines which layers exist and which boundaries separate them. Mock only at those defined boundaries, not at every interface or constructor you happen to pass.

---

## Testing layer selection

BDD development is one of two approaches for testing non-E2E layers. Decide per layer before writing any signatures, and never mix approaches in the same file.

| Layer | Recommended approach |
|---|---|
| **E2E / browser** | Spec-driven (ATDD) — test through the UI surface via `abd-story-acceptance-test` |
| **API / service / repository** | Choose: spec-driven (ATDD) or behavior-driven (BDD) |
| **Domain / unit** | Choose: spec-driven (ATDD) or behavior-driven (BDD) |
| **Component** | Choose: spec-driven (ATDD) or behavior-driven (BDD) |

**Decision guide:**
- Use **spec-driven (ATDD)** when test scenarios come from acceptance criteria and the team works outside-in.
- Use **behavior-driven (BDD)** when the team is doing discovery with a domain map and wants a scaffold-driven workflow through the three phases.

Include this guidance in any architecture specification that uses this skill family.

---

## Code minimalism in practice

The production code grows one failing test at a time. This is not a suggestion about design philosophy — it is a discipline that prevents drift between what is tested and what ships.

Any code path without a failing test behind it:
- Is not verified by the test suite
- Can change silently without a test breaking
- Represents scope that was not discussed or agreed

Concrete signs you are over-building:
- Adding a parameter the current test doesn't pass
- Handling an error path no test provokes
- Initializing a property no test reads
- Designing for a future requirement that has no story yet

If a behavior should exist, write a test for it first. Then implement it.
