---
fidelity: [discovery]
artifact: [thin-slice]
scanner: thin-slice-ordering
kind: shape

---

# Rule: Thin-slice ordering

Increments are ordered by **risk retirement**, not by feature completeness or by story-map left-to-right position. Three ordering forces apply, in this priority:

1. **Architectural risk first** — the unknown that could break the design gets validated in increment 1
2. **Spine before optional paths** — the sequential happy path across the whole flow ships before any variation, error path, or side channel
3. **Marketable value early** — of the remaining candidates, the one that delivers the largest observable outcome ships next

Every increment should also carry an explicit **decision prompt** — the question the increment answers, so the team can see whether shipping it changed the plan.

## DO

- Put whatever is architecturally uncertain into increment 1 (a new integration, a new persistence strategy, a new UI framework, a hard latency budget)
- Map the **spine** — the shortest end-to-end sequence of stories that a real user walks through — and order the spine first
- Push optional paths, error paths, alternate channels, and admin flows *after* the spine is delivered
- Name a **decision prompt** for each increment: "does the payment gateway hit our latency SLO?", "does the fraud model reject cleanly?"

## DON'T

- Order by story-map left-to-right — the map organises for understanding, not for delivery order
- Defer risk to "later, once the easy stuff is done" — that guarantees late surprises
- Deliver only spine and ignore optional paths — every optional path deferred must appear in a later increment, not vanish
- Ship an increment without knowing what question it answers

## Architectural risk first

Architectural risk means: something in the design that we're **not sure will work**. Signals include:

- A new external system with unclear SLAs (payment gateway, KYC provider, notification vendor)
- A new persistence pattern (event sourcing, sharded write path, cross-region replication)
- A non-functional target that constrains the whole design (sub-500ms end-to-end, six-nines durability)
- A regulatory constraint whose interpretation is still open (PCI segmentation, GDPR erasure)

Increment 1 must exercise at least one architectural risk. If it doesn't, the ordering is wrong.

## Spine vs. optional paths

The **spine** is the sequential list of stories a single user walks through on the happy path from first touch to observable outcome. Draw it as a straight line across the story map, top row.

Optional paths, error paths, alternate channels, and admin/back-office stories live *off* the spine. They are always **later** than the spine.

```
Spine (increment 1, in this order):
  Customer opens payment form
  → Customer enters recipient and amount
  → Customer confirms payment
  → System returns confirmation number

Off-spine (increment 2+):
  - Payment rejected: over daily limit
  - Payment rejected: recipient blocked
  - Payment initiated via partner API
  - Payment initiated via mobile
  - Support Agent looks up payment
```

## Decision prompts

Each increment carries a **decision prompt**: the single question shipping this increment answers. When the increment ships, the team compares actual behaviour to the prompt and decides whether to proceed as planned, adjust, or stop.

Format:

```markdown
### Increment 1 — Customer submits happy-path payment
**Decision prompt:** Does the payment gateway respond within our 500 ms latency budget under a realistic load pattern?

**If yes:** proceed to increment 2 (over-limit rejection path).
**If no:** insert a caching / retry increment before proceeding, or renegotiate the SLO.
```

Legitimate decision prompts:

- "Does {external system} meet our latency / reliability target?"
- "Does the domain model cover {edge case} without a special case?"
- "Does the fraud model reject cleanly enough to ship without human review?"
- "Do users understand the {new interaction} without hand-holding?"

Illegitimate decision prompts (too generic to be useful):

- "Is the code good?"
- "Are tests passing?"
- "Do users like it?"

## Format

```markdown
## Thin slice

### Increment 1 — Customer submits happy-path payment
**Decision prompt:** Does the payment gateway respond within 500 ms under realistic load?
**Architectural risk retired:** payment-gateway integration and latency budget.

Stories: … (see thin-slice-increment-shape.md)

### Increment 2 — Rejection paths
**Decision prompt:** Does the domain model produce clear, actionable rejection reasons?
**Architectural risk retired:** none (business rules only).

Stories: …
```

## Cross-references

- `thin-slice-increment-shape.md` — what each increment *is* (this rule is about their order)
- `four-to-nine-children.md` — 4–9 increments in the thin slice is the target
- `document-observed-quirks.md` — decisions surfaced by an increment often update quirks or close gaps on downstream artifacts
