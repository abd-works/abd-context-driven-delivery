# DDD — Procedural Guidance (shared)

## Think in language boundaries, not feature buckets

The most common mistake is carving bounded contexts by UI feature or page: "Onboarding context," "Dashboard context," "Settings context." These aren't language boundaries — they're screen labels. The same `Customer` concept appears in all of them with the same meaning.

Instead, ask: **where does the same word mean a different thing?** That's a context boundary. "Account" in billing means payment instrument; "Account" in identity means login credentials. Two contexts.

## How to discover contexts

1. **Listen for vocabulary friction** — when the same word causes confusion ("which account?", "what kind of order?"), you've found a boundary.
2. **Track lifecycle speed** — things that change at different rates belong in different contexts. Customer identity changes rarely; their subscription changes often; their catalog browsing changes constantly.
3. **Watch for ownership patterns** — who decides the rules? If billing rules and identity rules come from different stakeholders or teams, that's two contexts even if the data looks related.

## Aggregates are consistency clusters, not feature groups

An aggregate is **not** "all the things related to X." It's the smallest cluster where a business invariant must hold atomically. Ask:

- **What must be true together?** An order and its line items must add up correctly — that's one aggregate.
- **What can change independently?** A customer's address can change without affecting their orders — different aggregates.
- **What's the transaction boundary?** Everything that must succeed or fail together is one aggregate.

Keep aggregates small. If you're grouping more than 5-7 concepts into one aggregate, you're probably bundling things that don't share invariants.

## External systems are not your bounded contexts

When modeling a system that integrates with vendors (Mavenir, AWS, Stripe), the vendor is a **downstream external system**, not a bounded context of your product. Your product's contexts come first; vendor integrations are arcs from your contexts to theirs.
