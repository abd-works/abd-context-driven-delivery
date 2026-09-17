# DDD — Procedural Guidance (bounded_context fidelity)

## How to draw the context map

Start from what your users do, not from the technology:

1. **Name the system you're building** — the consumer app, the product. This goes first/upstream on the map.
2. **Identify the language clusters** — group concepts by shared vocabulary and shared rules. Each cluster that uses the same terms with the same meaning is one bounded context.
3. **Name each context** — use the domain experts' words. Not `PaymentService`, not `BillingModule`. Use `Billing`, `Catalog`, `Fulfillment`.
4. **Place aggregates inside contexts** — each aggregate is a consistency boundary within the context. Several aggregates sharing the same language is normal — don't wrap each one in its own context.
5. **Draw the arcs** — for each dependency between contexts, state: direction, what crosses, how they integrate, and the relationship pattern.

## Traps to catch during mapping

- **One-aggregate contexts** — if every context has exactly one aggregate, you're drawing class boundaries, not language boundaries. Merge contexts that share vocabulary.
- **UI-theme contexts** — "Selfcare" and "Onboarding" that both contain `Customer`, `Subscription`, and `Plan` are the same context viewed from different screens. Don't split by UI.
- **Copy-paste contexts** — if the same concept (`Customer`) appears in three contexts with the same definition, those aren't separate contexts — they're one context being accessed from different angles.
- **Missing unnamed contexts** — look for integration points that nobody named. The authentication system, the notification system, the reporting pipeline — these are contexts even if nobody called them that.

## Dependency thinking

For every arrow on the map, answer all four questions:

1. **Direction** — who depends on whom? Name both sides (upstream/downstream or mutual).
2. **What crosses** — which concepts flow across the boundary? How do they translate?
3. **How they integrate** — name the mechanism: synchronous call to `X.Y.operation()`, domain event `ThingHappened`, batch extract, shared database. "Loose coupling" alone is not an answer.
4. **Relationship pattern** — Shared Kernel, Customer/Supplier, Conformist, ACL, Open Host, Separate Ways. Pick from the catalogue, don't invent.

## The vendor label

Every context carries a vendor label after `|`: `custom` (you build it), `bespoke` (you customize it), or the vendor name (Mavenir, Stripe, AWS). Never put team names or technology stacks here.
