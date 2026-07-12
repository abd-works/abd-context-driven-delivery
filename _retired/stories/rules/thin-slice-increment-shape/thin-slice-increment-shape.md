---
fidelity: [discovery]
artifact: [thin-slice]
scanner: increment-shape
kind: shape

---

# Rule: Thin-slice increment shape

Every increment in the thin slice must be three things at once:

1. **Vertical** — cuts through every layer that a real user interaction touches (UI or entry-point + business rule + persistence or side-effect)
2. **Marketable** — delivers observable value to a real user or stakeholder, describable without engineering jargon
3. **Minimal** — the smallest cut of scope that is still vertical and marketable — no gold-plating

A single-layer slab (UI only, service only, schema only) is not an increment. A "phase 1 platform" is not an increment. Neither is a full feature.

## DO

- Make each increment ship the shortest end-to-end path for its stories
- Trade off quality attributes explicitly — the first increment often skips retries, edge-case UI, i18n, observability polish (see `thin-slice-ordering.md` for the reasoning)
- Name each increment with the user-visible outcome it delivers ("Customer submits happy-path payment", not "Payment service v1")
- Keep each increment shippable *on its own* — the story map should stay coherent if delivery stops after any increment

## DON'T

- Slice by layer ("Increment 1: schema; Increment 2: service; Increment 3: UI") — that's horizontal, not thin
- Package a full feature as "increment 1" — if it's not minimal, it's not thin
- Add polish stories to increment 1 (retry logic, exhaustive validation, admin screens) that don't move the marketable outcome
- Hide risk behind "we'll add that in increment 3" — architectural risk goes *early*, see `thin-slice-ordering.md`

## Vertical

An increment is vertical when a **specific end-to-end user interaction** works. Concretely:

- The **entry point** (UI screen, API endpoint, CLI command, event) exists and is reachable
- The **business rule** for the happy path executes
- The **persistent effect** (record written, event emitted, response returned) is observable

If any of those three is missing, the increment is a slab, not a slice.

## Marketable

An increment is marketable if you can complete this sentence without engineering vocabulary:

> "After this increment, a **{actor}** can **{observable outcome}**."

Passing examples:

- "After this increment, a **Customer** can **submit a payment from their savings account and see the confirmation number**."
- "After this increment, a **Support Agent** can **look up a payment by confirmation number and see its status**."

Failing examples:

- "After this increment, the payment service exposes a POST endpoint."
- "After this increment, the database has a payments table."

## Minimal

Minimal means: what is the smallest thing you can ship that is still vertical AND marketable?

Legitimate minimal-slice tradeoffs (spell them out on the increment):

- **Happy path only** — errors deferred to a later increment
- **One channel only** — web first, mobile and partner API deferred
- **One entity variant** — one account type first, others deferred
- **Manual for the rest** — reconciliation manual for now
- **No polish** — no retries, no i18n, no analytics

Illegitimate cuts:

- Skipping persistence ("we'll write the DB in increment 2")
- Skipping the actual business rule ("increment 1 accepts any input")
- Skipping the response ("increment 1 fires and forgets")

## Format

```markdown
### Increment 1 — Customer submits happy-path payment
_Marketable outcome: a Customer can submit a valid payment from web and see a confirmation number._

**Stories in this increment:**
- Customer submits payment from web (happy path only)
- System returns confirmation number

**Deferred to later increments (explicit tradeoffs):**
- Payment from partner API (increment 2)
- Rejection when limit exceeded (increment 3)
- Retry on transient service failure (increment 4)
- Mobile channel (increment 5)
```

## Cross-references

- `thin-slice-ordering.md` — how to *order* increments once each one is shape-correct
- `four-to-nine-children.md` — each increment holds 4–9 stories; a 12-story increment is too fat, a 1-story increment is probably a slab
- `right-size-story-nodes.md` — stories inside an increment obey the same right-sizing rule
