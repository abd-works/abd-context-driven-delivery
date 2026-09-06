# {SolutionName} — Platform Architecture Elements

> **Diagram:** `platform-architecture.drawio`
> **Last updated:** YYYY-MM-DD

---

## Client Applications

*Use when: a frontend surface runs on the client side. One entry per distinct client runtime.*

### {Name} (Client Application)
{Runtime and user-facing purpose.}

### {Name} (Client Application) *(if applicable)*
{Runtime and user-facing purpose.}

---

## Backend Services

*Use when: a server-side process handles requests or orchestrates logic. One entry per independently deployable service.*

### {Name} (Backend Service)
{Runtime, framework, and role.}

### {Name} (Backend Service) *(if applicable)*
{Runtime, framework, and role.}

---

## Data Stores

*Use when: a persistence or caching technology holds state. One entry per distinct store technology.*

### {Name} (Data Store)
{Technology and what kind of data lives here.}

### {Name} (Data Store) *(if applicable)*
{Technology and what kind of data lives here.}

---

## Background Workers

*Use when: an async process, queue consumer, or scheduled job runs independently of the request path.*

### {Name} (Background Worker) *(if applicable)*
{Runtime and responsibility.}

---

## CDN / Edge

*Use when: static assets or API traffic are served or proxied at the edge.*

### {Name} (CDN / Edge) *(if applicable)*
{Provider and what it caches or proxies.}

---

## Third-Party Integrations

*Use when: an external SaaS or API is a direct platform dependency. One entry per integration.*

### {Name} (Third-Party Integration)
{Provider and the capability it supplies.}

### {Name} (Third-Party Integration) *(if applicable)*
{Provider and the capability it supplies.}

---

## Technology Badges

| Element | Technology badge |
|---|---|
| {Element name} | {React / Node.js / PostgreSQL / etc.} |

---

## Legend

| Visual | Meaning |
|---|---|
| {Shape or colour} | {What it denotes} |

---

## Example

*Remove this section before committing.*

```markdown
## Client Applications

### Retail SPA (Client Application)
Browser-based React app; primary interface for browsing products, managing a cart, and
placing orders.

## Backend Services

### Orders API (Backend Service)
Node.js/Fastify REST API; validates requests, enforces authorisation, and orchestrates
order placement and fulfilment.

### Admin API (Backend Service)
Separate Fastify service for the Admin Console; exposes internal-only operations not
available to customers.

## Data Stores

### PostgreSQL (Data Store)
Primary relational database; source of truth for orders, products, and user records.

### Redis (Data Store)
In-memory cache for session state, rate-limit counters, and short-lived feature flags.

## Third-Party Integrations

### Auth0 (Third-Party Integration)
Identity provider; both APIs delegate authentication and token issuance to Auth0.

### Stripe (Third-Party Integration)
Payment gateway; the Orders API posts charges and receives synchronous and webhook responses.

## Technology Badges

| Element | Technology badge |
|---|---|
| Retail SPA | React 18 |
| Orders API | Node.js 20 / Fastify 4 |
| Admin API | Node.js 20 / Fastify 4 |
| PostgreSQL | PostgreSQL 15 |
| Redis | Redis 7 |
```
