# DDD — Procedural Guidance (tactics fidelity)

## Architecture-first thinking

Before writing any code at tactics, resolve the architecture:

1. **Check project context** — `.context/`, ADRs, existing stack. What persistence? What messaging? What framework?
2. **If nothing exists, ask.** Don't assume. If no answer available, default to the simplest thing: JSON file persistence.
3. **Domain model stays clean** — no UI imports, no transport concerns, no framework annotations in domain classes. Domain objects speak domain language only.

## Repository implementation thinking

A repository is a collection-style seam. Think of it as a very simple collection API:

- `add(aggregate)` — store a new instance
- `find_by_{identity}(id)` — retrieve by business identity
- `update(aggregate)` — persist changes
- `remove(aggregate)` — retire

Behind this seam, the implementation talks to a database, file system, or whatever. But the domain code only sees the collection interface.

## Load with identity in hand

When implementing `load`, the caller already has the identity — a customer ID, an order number. Don't assume a browser session or a "current user" context. Pass the identity explicitly, load once, and reuse the variable.

A cart has no identity outside its prospect — you reach it through `prospect.cart`, not `cartRepository.current()`.

## Event implementation thinking

Domain events are facts about what happened, not commands about what to do:

- **Name** — past tense: `PaymentApproved`, not `ApprovePayment`
- **Trigger** — which operation publishes this event? Pin it as an invariant.
- **Consumers** — who reacts? List them. Each reaction is a separate concern.
- **Payload** — only the data needed for consumers to act. Not the entire aggregate.

## Ports and adapters

Keep persistence and messaging behind ports (interfaces). The domain declares what it needs; the infrastructure implements how. This is where you finally wire the repository implementations, event publishers, and external service clients.
