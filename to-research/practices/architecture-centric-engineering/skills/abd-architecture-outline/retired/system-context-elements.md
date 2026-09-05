# {SolutionName} — System Context Elements

> **Diagram:** `system-context.drawio` · C4 Level 1
> **Last updated:** YYYY-MM-DD

---

## Systems in Scope

*Use when: the team owns this system. One entry per owned system.*

### {System A Name} (Software System)
{What it is and its primary job.}

**Major functions:**
- {Function or capability 1}
- {Function or capability 2}
- {Function or capability 3}
- {Function or capability 4}

**Platform technology:**
- **App stack:** {runtime · framework · key libraries}
- **Persistence:** {database technology and role}
- **Tools / infrastructure libs:** {build tool · logging · observability · etc.}

### {System B Name} (Software System)
{What it is and its primary job.}

**Major functions:**
- {Function or capability 1}
- {Function or capability 2}
- {Function or capability 3}
- {Function or capability 4}

**Platform technology:**
- **App stack:** {runtime · framework · key libraries}
- **Persistence:** {database technology and role}
- **Tools / infrastructure libs:** {build tool · logging · observability · etc.}

---

## Persons

*Use when: a human role interacts directly with an in-scope system. One entry per role.*

### {Role Name} (Person)
{What the role does and which system they interact with.}

### {Role Name} (Person)
{What the role does and which system they interact with.}

---

## External Systems

*Use when: a system outside the solution boundary connects to an in-scope system. One entry per external system.*

### {External System Name} (External System)
{What it is and what it provides.}

### {External System Name} (External System)
{What it is and what it provides.}

---

## Relationships

*Use when: an arrow appears in the diagram. One entry per arrow; state what crosses the boundary, the direction, and the protocol.*

### {Source} → {Target}: {Label} (Relationship)
**Protocol:** {HTTP/REST · gRPC · AMQP · WebSocket · HTTPS · etc.}
{What crosses the boundary, direction of data flow, and why.}

### {Source} → {Target}: {Label} (Relationship)
**Protocol:** {HTTP/REST · gRPC · AMQP · WebSocket · HTTPS · etc.}
{What crosses the boundary, direction of data flow, and why.}

---

## Legend

| Visual | Meaning |
|---|---|
| Blue / prominent box | Software system in scope |
| Grey box | External software system |
| Person icon | Human actor / role |
| Solid arrow | Synchronous interaction; label states what crosses the boundary |
| Dashed arrow | Async / event-driven interaction |

---

## Example

*Remove this section before committing.*

```markdown
## Systems in Scope

### Retail Platform (Software System)
Customer-facing web and mobile commerce platform — browse, cart, checkout, and order tracking.

**Major functions:**
- Product catalogue browsing and search
- Shopping cart and wishlist management
- Checkout and payment processing
- Order tracking and history
- Customer account and preferences
- Promotions and discount codes

**Platform technology:**
- **App stack:** Node.js 20 · Fastify 4 · React 18 · TanStack Query 5
- **Persistence:** PostgreSQL 15 (primary), Redis 7 (cache + ephemeral state)
- **Tools / infrastructure libs:** OpenTelemetry, Pino, Zod, TypeScript 5, GitHub Actions

### Admin Console (Software System)
Internal tool for back-office staff to manage listings, process refunds, and view dashboards.

**Major functions:**
- Product and inventory management
- Order management and refund processing
- Customer support lookup
- Operational dashboards and reporting

**Platform technology:**
- **App stack:** Node.js 20 · Fastify 4 · React 18
- **Persistence:** Shared PostgreSQL 15 instance (separate schema)
- **Tools / infrastructure libs:** Same observability stack as Retail Platform

## Persons

### Customer (Person)
Browses products, manages a cart, and places orders through the Retail Platform.

### Back-Office Operator (Person)
Manages product data and resolves order issues via the Admin Console.

## External Systems

### Auth0 (External System)
Identity provider; both in-scope systems delegate authentication and token issuance to Auth0.

### Stripe (External System)
Payment gateway; the Retail Platform sends card charges and receives synchronous results
plus webhook events for disputes.

### SendGrid (External System)
Transactional email service; the Retail Platform calls SendGrid to send order confirmations
and password resets.

## Relationships

### Customer → Retail Platform: Browse and submit orders (Relationship)
**Protocol:** HTTPS
Browser sends REST requests; platform validates stock, creates orders, and returns confirmation JSON.

### Back-Office Operator → Admin Console: Manage listings and process refunds (Relationship)
**Protocol:** HTTPS
Operator uses the Admin Console web UI; requests are forwarded to the shared API layer over REST.

### Retail Platform → Auth0: Authenticate users (Relationship)
**Protocol:** HTTPS / OAuth 2.0 + OIDC
Both systems redirect unauthenticated requests to Auth0 and verify JWTs on each API call.

### Retail Platform → Stripe: Process payments (Relationship)
**Protocol:** HTTPS / REST (Stripe API v1)
Platform posts a PaymentIntent; Stripe returns a synchronous result and sends webhook events for disputes.

### Retail Platform → SendGrid: Send transactional email (Relationship)
**Protocol:** HTTPS / REST (SendGrid Mail API v3)
Platform calls SendGrid after order state changes; failed deliveries are retried by SendGrid.
```
