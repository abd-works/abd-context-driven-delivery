# pml-midtier Express Architecture Specification

## Where to Start -- What Does This Feature Touch?

Answer each question about the feature or story you are working on. Each "yes" points to a context file with the details you need.

| Question                                                                              | Read this                                                       |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Does it add a new route?                                                              | [src/entities/](/src/entities/architecture-context.md)          |
| Does it need a new environment variable?                                              | [src/configs/](/src/configs/architecture-context.md)            |
| Does it add a new Joi validation schema?                                              | [src/helpers/](/src/helpers/architecture-context.md)            |
| Does it touch the Auth middleware?                                                    | [src/middlewares/Auth/](/src/middlewares/Auth/architecture-context.md) |
| Does it return a new `Err` subclass or 4xx status code?                               | [src/helpers/error/](/src/helpers/error/architecture-context.md) |
| Does it import the `Twilio` SDK?                                                      | [src/services/Twilio/](/src/services/Twilio/architecture-context.md) |
| Does it add a new payload-builder method to the `Zendesk` service?                    | [src/services/Zendesk/](/src/services/Zendesk/architecture-context.md) |

---

## Overview

pml-midtier is a Node.js/Express API gateway.

---

## Mechanisms

**System Entity Controllers** (`src/entities/`) -- one folder per downstream system. [src/entities/](/src/entities/architecture-context.md)

---

## Testing Architecture

Tests use a Sandbox pattern. See [tests/domain-helpers/](/tests/domain-helpers/architecture-context.md).

---

## References

- ADR-001 through ADR-007.
