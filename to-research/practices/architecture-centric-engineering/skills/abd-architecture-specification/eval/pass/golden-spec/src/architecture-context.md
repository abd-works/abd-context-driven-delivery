# pml-midtier Express Architecture Specification

> **Status:** Draft -- Exploration fidelity (document mode; describes what exists)
> **Date:** 2026-06-27
> **Mode:** document (Exploration -- describe; do not prescribe)

---

## Where to Start -- What Does This Feature Touch?

Answer each question about the feature or story you are working on. Each "yes" points to a context file with the details you need. Read only those files -- you don't need the rest of this document.

If every answer is "no", the feature is either infrastructure-only or out of scope for this spec; if you are unsure, read the Overview and Source Layout below to orient yourself and follow the relevant context files from there.


| Question                                                                                   | Read this                                                               |
| ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Is there a new downstream system to integrate with, or a new operation on an existing one? | [System Entity Controllers](/src/entities/architecture-context.md) |
| Does it require a new third-party credential or a new environment-specific value?          | [Configuration & Secrets](/src/configs/architecture-context.md)    |
| Should access to this operation be restricted to authenticated or specific users?          | [Authentication](/src/middlewares/Auth/architecture-context.md)    |
| Are there specific failure conditions the caller needs to distinguish and handle?          | [Error Handling](/src/helpers/error/architecture-context.md)       |
| Does it involve number portability or SMS-based verification?                              | [Twilio](/src/services/Twilio/architecture-context.md)             |
| Does it need to raise or look up a customer support ticket?                                | [Zendesk](/src/services/Zendesk/architecture-context.md)           |


---



## Overview

pml-midtier is a Node.js/Express API gateway sitting between the Paradise Mobile consumer apps and the downstream systems that fulfil their requests. It does not own domain state -- it validates, proxies, and maps. Every request enters through a protected HTTP surface, passes identity verification, reaches the controller responsible for that downstream system, and comes back out as a normalised response or a typed error.

The architecture has four concerns: loading configuration and secrets before anything else starts; authenticating every inbound request before it reaches a controller; routing each request to the right entity controller which calls the downstream system and maps the result; and translating all failures -- validation, network, or business -- into consistent HTTP error responses.

> **Sources:** `docs/architecture/blueprint/architecture-blueprint.md` (reverse-engineered 2026-06-26) -- ADRs 001-007 in `docs/architecture/decisions/`

---



## Mechanisms

**Configuration & Secrets** (`src/configs/`) -- loads `.env` and optional AWS Secrets Manager values once before any module runs; exports typed config objects. [src/configs/architecture-context.md](/src/configs/architecture-context.md)

**Authentication** (`src/middlewares/Auth/`) -- applies Cognito JWT validation as a route-group prefix in `app.ts`; writes decoded credentials onto the request so controllers never touch tokens directly. [src/middlewares/Auth/architecture-context.md](/src/middlewares/Auth/architecture-context.md)

**System Entity Controllers** (`src/entities/`) -- one folder per downstream system; each follows an index/routes/controller skeleton and calls the downstream system directly via [AxiosFactory](/src/services/Axios/architecture-context.md). [src/entities/architecture-context.md](/src/entities/architecture-context.md)

**Error Handling** (`src/helpers/error/`) -- `validatePayload` throws typed `Err` objects; `AxiosFactory` throws `AxiosServiceError`; all failures converge at `handleError` which is the sole translator to HTTP. [src/helpers/error/architecture-context.md](/src/helpers/error/architecture-context.md)

### Package Context

Every folder with significant logic has an `architecture-context.md` alongside its code.

**Mechanisms**

- **Configuration & Secrets** -- env loading and AWS Secrets Manager [src/configs/](/src/configs/architecture-context.md)
- **Authentication** -- Cognito JWT validation, Zoho OAuth, and the CognitoService that does the actual token work [src/middlewares/Auth/](/src/middlewares/Auth/architecture-context.md)
- **System Entity Controllers** -- the full controller pattern, file skeleton, and per-entity mapping table [src/entities/](/src/entities/architecture-context.md)
- **Error Handling** -- `handleError`, `Err`, `validatePayload` [src/helpers/error/](/src/helpers/error/architecture-context.md)

**Services**

- **AxiosFactory** -- singleton outbound HTTP client used by every controller [src/services/Axios/](/src/services/Axios/architecture-context.md)
- **CognitoService** -- JWT fetch, verify, and decode; part of the Authentication mechanism [src/services/Cognito/](/src/services/Cognito/architecture-context.md)
- **LoggerFactory** -- cross-cutting logging singleton [src/services/Logger/](/src/services/Logger/architecture-context.md)
- **Twilio** -- Verify SDK wrapper for SMS portability verification; used by Mavenir only [src/services/Twilio/](/src/services/Twilio/architecture-context.md)
- **Zendesk** -- ticket client with payload builders for customer lifecycle events; used by Mavenir only [src/services/Zendesk/](/src/services/Zendesk/architecture-context.md)

**Utilities & Legacy**

- **Helpers** -- grab-bag of utilities: validation, JWT/Customer helpers, and legacy response-building code [src/helpers/](/src/helpers/architecture-context.md)
- **Types** -- legacy type folder; mostly dead code from a previous Contentful/Cloudinary integration [src/types/](/src/types/architecture-context.md)

**Testing**

- **Domain Test Objects** -- centralized domain classes + fixtures + spec-alignment table [tests/domain-helpers/](/tests/domain-helpers/architecture-context.md)



### Source Layout

```
src/
+-- server.ts              <- bootstrap                          [Configuration & Secrets]
+-- app.ts                 <- composition root
+-- configs/               <- env + secrets loading              [Configuration & Secrets]
+-- middlewares/Auth/      <- JWT + Zoho OAuth                   [Authentication]
+-- helpers/               <- misc utilities + legacy
|   +-- error/             <- error handling                     [Error Handling]
+-- services/
|   +-- Axios/             <- HTTP client
|   +-- Cognito/           <- JWT validation                     [Authentication]
|   +-- Logger/            <- logging
|   +-- Twilio/            <- SMS verification
|   +-- Zendesk/           <- support tickets
+-- entities/              <- one folder per downstream system   [System Entity Controllers]
+-- types/                 <- legacy type definitions            [dead code]
```



### Instantiating the Domain

> **Entity implementation patterns vary significantly.** Folders are named after the external system, not domain concepts (ADR-001). Mavenir is the only entity with an explicit domain model; the others accumulated organically:
>
> - **Mavenir** -- midtier API objects live in `types/CustomerResponse.ts`; external system objects live in `types/Customer.ts`; `utils/buildCustomer/` translates between them.
> - **Zoho** -- midtier API objects are produced by `inventory.mapper.ts`; external system objects live in `types/zohoItem.ts` and siblings.
> - **Voucher** -- midtier API objects live in `types.ts`; external system objects are defined inline in the controller.
> - **My** -- no midtier API objects defined; reuses `CustomerResponse` from Mavenir.
> - **MdeAdmin** -- no midtier API objects defined; request shapes are inline types in the controller.
> - **Cognito, Persona, Fygaro, Apple, Webflow** -- no API objects defined.

---



## Testing Architecture

Tests use a **Sandbox** pattern: domain test objects drive the full Express app via Jest + Supertest; all back-office dependencies (`axios.request`, Cognito, Twilio, Zoho) are stubbed at the boundary. See [`tests/domain-helpers/architecture-context.md`](/tests/domain-helpers/architecture-context.md) for principles, file layout, epic/sub-epic map, and spec-alignment table.

---



## References

- **Architecture source of truth:** `docs/architecture/blueprint/architecture-blueprint.md` (reverse-engineered 2026-06-26)
- **Decision records:** `docs/architecture/decisions/ADR-001` through `ADR-007`
- **Domain model:** `docs/domain/model/domain-model.md` + `docs/domain/model/modules/` (12 bounded context files)
- **Acceptance criteria:** `docs/stories/acceptance-criteria/acceptance-criteria.md` (31 stories)
- **Coding standard:** `abd-clean-code`
- **Testing standard:** `abd-story-acceptance-test`
- **Domain specification:** `docs/domain/specification/domain-specification.md` (domain class names drive domain test object names)

