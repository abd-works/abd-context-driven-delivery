# pml-midtier Express Architecture Specification

## Where to Start -- What Does This Feature Touch?

Answer each question about the feature or story you are working on.

| Question                                                            | Read this                                                       |
| ------------------------------------------------------------------- | --------------------------------------------------------------- |
| Is there a new downstream system to integrate with?                 | [src/entities/](/src/entities/architecture-context.md)          |
| Does it involve customer support tickets?                           | [src/services/Zendesk/](/src/services/Zendesk/architecture-context.md) |

---

## Overview

pml-midtier is a Node.js/Express API gateway.

---

## Mechanisms

**System Entity Controllers** (`src/entities/`) -- request handlers. [src/entities/](/src/entities/architecture-context.md)

**Authentication** (`src/middlewares/Auth/`) -- JWT middleware. [src/middlewares/Auth/](/src/middlewares/Auth/architecture-context.md)

### Package Context

Every folder with significant logic has an `architecture-context.md` alongside its code.

**Mechanisms**

- **System Entity Controllers** -- request handlers. [src/entities/](/src/entities/architecture-context.md)
- **Authentication** -- JWT middleware. [src/middlewares/Auth/](/src/middlewares/Auth/architecture-context.md)

<!--
  FAILURE: src/services/Zendesk/architecture-context.md and
  tests/domain-helpers/architecture-context.md and src/helpers/architecture-context.md
  all exist on disk and are referenced from the Where to Start table / spec
  body, but no "Services" / "Utilities & Legacy" / "Testing" categories are
  listed below. The rule requires every documented folder to appear here.
-->

---

## Testing Architecture

Tests use a Sandbox pattern. See [tests/domain-helpers/](/tests/domain-helpers/architecture-context.md).

---

## References

- ADR-001 through ADR-007.
