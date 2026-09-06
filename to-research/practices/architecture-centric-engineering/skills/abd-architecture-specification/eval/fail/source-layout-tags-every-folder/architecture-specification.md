# pml-midtier Express Architecture Specification

## Where to Start -- What Does This Feature Touch?

| Question                                                | Read this                                                |
| ------------------------------------------------------- | -------------------------------------------------------- |
| Is there a new downstream system to integrate with?     | [src/entities/](/src/entities/architecture-context.md)   |

---

## Overview

pml-midtier is a Node.js/Express API gateway.

---

## Mechanisms

**System Entity Controllers** (`src/entities/`) -- request handlers. [src/entities/](/src/entities/architecture-context.md)

### Package Context

**Mechanisms**

- **System Entity Controllers** -- request handlers. [src/entities/](/src/entities/architecture-context.md)

### Source Layout

```
src/
+-- server.ts
+-- app.ts
+-- configs/
+-- middlewares/
+-- helpers/
+-- services/
|   +-- Axios/
|   +-- Logger/
|   +-- Twilio/
|   +-- Zendesk/
+-- entities/
+-- types/
+-- old-payments/
```

<!--
  FAILURE: every line is a bare folder name. No arrow descriptions, no
  mechanism tags, and old-payments/ is not flagged [dead code]. Reader
  cannot tell which folder belongs to which mechanism, or which folders
  are inactive.
-->

---

## Testing Architecture

Tests use a Sandbox pattern. See [tests/domain-helpers/](/tests/domain-helpers/architecture-context.md).

---

## References

- ADR-001 through ADR-007.
