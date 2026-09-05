# pml-midtier Express Architecture Specification

## Where to Start -- What Does This Feature Touch?

| Question                                              | Read this                                                                    |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| Is there a new downstream system to integrate with?   | [src/entities/](../../../src/entities/architecture-context.md)               |
| Does it involve customer support tickets?             | [src/services/Zendesk/](../../../src/services/Zendesk/architecture-context.md) |

---

## Overview

pml-midtier is a Node.js/Express API gateway.

---

## Mechanisms

**System Entity Controllers** (`src/entities/`) -- request handlers. [src/entities/](../../../src/entities/architecture-context.md)

**Authentication** (`src/middlewares/Auth/`) -- JWT middleware. [src/middlewares/Auth/](src/middlewares/Auth/architecture-context.md)

### Package Context

**Mechanisms**

- **System Entity Controllers** -- request handlers. [src/entities/](../../../src/entities/architecture-context.md)
- **Authentication** -- JWT middleware. [src/middlewares/Auth/](src/middlewares/Auth/architecture-context.md)

<!--
  FAILURE: links use `../../../` relative-up traversal and bare relative
  paths like `src/middlewares/...` instead of workspace-root `/src/...`.
  When the spec file moves, every link breaks silently.
-->

---

## Testing Architecture

Tests use a Sandbox pattern. See [tests/domain-helpers/](../../../tests/domain-helpers/architecture-context.md).

---

## References

- ADR-001 through ADR-007.
