# pml-midtier Express Architecture Specification

## Where to Start -- What Does This Feature Touch?

| Question                                              | Read this                                                |
| ----------------------------------------------------- | -------------------------------------------------------- |
| Is there a new downstream system to integrate with?   | [src/entities/](/src/entities/architecture-context.md)   |

---

## Overview

pml-midtier is a Node.js/Express API gateway.

---

## Mechanisms

**System Entity Controllers** (`src/entities/`) -- request handlers. [src/entities/](/src/entities/architecture-context.md)

---

## Testing Architecture

Tests use a Sandbox pattern.

### Principles

- **Stories instantiate tests.** Every story produces one test file per tier at the same folder path as the story in the hierarchy.
- **Same scenario vocabulary across tiers.** The base helper defines Given/When/Then method names from the story's acceptance criteria; every tier helper implements the same names.
- **Stub at the tier boundary only.** Tests stub `axios.request`, Cognito, Twilio, and Zoho at their respective boundaries; everything else runs for real.
- **Helpers own mechanics; test files own scenarios.** Test files contain only `it`/`test` declarations.

### Module Layout

| Story artifact | Test artifact |
|----------------|---------------|
| Epic | folder |
| Mid-level sub-epic | intermediate folder (only when it has children) |
| Lowest-level sub-epic | file (`<sub-epic>_<tier>.<ext>`) |
| Story | `describe` / test class inside the file |
| Scenario | `it` / `test` method inside the describe |

### Sandbox Example

```typescript
// Given
const customer = new Customer(app);

// When -- seeds axios.request queue and runs Supertest internally
const response = await customer.update({ withActiveSubscription: true });

// Then
expect(response.status).toBe(204);
```

### Spec Alignment

| Story | Test file | Status |
|-------|-----------|--------|
| Update customer | `customer/update_supertest.ts` | conforming |
| Cancel portability | `portability/cancel_supertest.ts` | drift |

<!--
  FAILURE: the Testing Architecture section in the main spec contains
  principles, module layout, sandbox example, and spec-alignment table
  inline. ALL of that material belongs in
  tests/domain-helpers/architecture-context.md, with the main spec
  reduced to a single pointer paragraph.
-->

---

## References

- ADR-001 through ADR-007.
