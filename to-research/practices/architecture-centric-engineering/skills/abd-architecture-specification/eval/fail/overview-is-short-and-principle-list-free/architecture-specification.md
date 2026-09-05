# pml-midtier Express Architecture Specification

## Where to Start -- What Does This Feature Touch?

| Question                                              | Read this                                                |
| ----------------------------------------------------- | -------------------------------------------------------- |
| Is there a new downstream system to integrate with?   | [src/entities/](/src/entities/architecture-context.md)   |

---

## Overview

pml-midtier is a Node.js/Express API gateway that prioritizes:

1. **Modularity** -- each downstream system gets its own folder under `src/entities/` so new integrations follow the existing skeleton without modifying shared code.
2. **Testability** -- all outbound HTTP is stubbed at `axios.request`; controllers can be driven end-to-end through Supertest without any real network calls.
3. **Type safety** -- domain types live in `entities/{System}/types.ts`; midtier API objects are kept separate from external-system contracts so a downstream schema change is contained.
4. **Consistent error handling** -- every controller's catch block ends in `handleError(res, error)`; no inline status construction is permitted.
5. **Configuration discipline** -- secrets are resolved from AWS Secrets Manager before any module instantiates; runtime crashes on missing values rather than degrading silently.

The mechanisms are:

- **System Entity Controllers** -- request handlers, three-file skeleton, per-system folder.
- **Authentication** -- Cognito JWT validation as route-group middleware.
- **Error Handling** -- `Err`, `ErrorRequest`, `handleError`.
- **Configuration & Secrets** -- env loading + AWS Secrets Manager.

The system has been in production since 2024 and is the primary integration layer between the consumer apps and the BSS stack. The team's testing library of choice is Jest with Supertest; future direction includes migrating to a contract-test approach once the downstream Mavenir API stabilises.

<!--
  FAILURE: the Overview contains a numbered principle list, duplicates the
  mechanism list (which already lives under ## Mechanisms), and runs to
  six paragraphs with project history and "future direction" content.
  The rule requires at most two short paragraphs naming what the system
  is and the small set of concerns the architecture addresses.
-->

---

## Mechanisms

**System Entity Controllers** (`src/entities/`) -- request handlers. [src/entities/](/src/entities/architecture-context.md)

---

## Testing Architecture

Tests use a Sandbox pattern. See [tests/domain-helpers/](/tests/domain-helpers/architecture-context.md).

---

## References

- ADR-001 through ADR-007.
