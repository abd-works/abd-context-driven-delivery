# Examples — abd-bdd-behavior

## Worked example: Voucher feature

**Inputs used:**
- `story-map.md` — sub-epic: `Redeem Voucher`
- `domain-language.md` — concepts: Voucher, Discount, Order, Customer
- `domain-model.md` — Voucher: validates eligibility, applies discount, tracks redemption state
- `acceptance-criteria.md` — AC for stories in the `Redeem Voucher` sub-epic

**Correct scaffold — `voucher-behavior.md`**

```
Redeem Voucher

  a Voucher
    it should not be redeemed
    with a 20 percent discount rule and no expiry
      it should be eligible for redemption
      it is applied to an Order with 3 eligible items
        the Order should show a 20 percent discount on each eligible item
        the Order should show the saving amount on the order summary
        the Order should show the original price alongside the discounted price
        the Voucher should be marked as redeemed
      it is applied to an Order with no eligible items
        the redemption should be refused because no eligible items are present
      it is applied to an Order by a Customer other than the one it was issued to
        the redemption should be refused because the Customer is not the intended recipient
    with a fixed-amount discount of ten
      it is applied to an Order
        the Order total should be reduced by ten
    with a past expiry date
      any redemption should be refused because the Voucher has expired
    that has already been redeemed
      any redemption should be refused because the Voucher was already used
    with a code that does not exist
      the redemption should be refused because the Voucher code is unknown
```

Why this is right:

- The top-level describe (`Redeem Voucher`) is the sub-epic from the story map.
- The subject (`a Voucher`) is a noun phrase, not a class name — it is an instance of the domain concept.
- Each nested describe either **elaborates the state** ("with a 20 percent discount rule and no expiry", "with a past expiry date") or introduces a **narrative event** ("it is applied to an Order with 3 eligible items"). Events read as present-tense narration — no `when/given/then` keywords.
- Every leaf is an **observation** of what is true in the state built by the containing describes. Leaves start with `it should` or `the X should`.
- The reader can walk the outline top-down and mentally construct the state at every point: a Voucher, with these rules, applied to an Order under these conditions, therefore the following is true.
- No code syntax, no method names, no implementation vocabulary.

## Counter-example 1 — implementation-oriented (old anti-pattern)

```
VoucherService
  applyVoucher
    calls calculateDiscount on DiscountCalculator
    throws VoucherExpiredException when TTL exceeded
```

Why this is wrong:

- `VoucherService` is an implementation class, not a subject or domain concept.
- `applyVoucher` is a method name, not a state or event.
- Leaf lines describe implementation detail, not observable behavior.
- No `should` prefix on any leaf.

## Counter-example 2 — operation-oriented (subtler anti-pattern)

```
Voucher
  should apply a percentage discount to eligible items
  should apply a fixed-amount discount to the order total
  should reject a voucher code that does not exist
  should reject a voucher past its expiry date
```

Why this is wrong even though every leaf starts with `should`:

- `Voucher` is a bare concept name, not a subject with state. The reader learns nothing about what Voucher this is.
- Each leaf collapses a state, an event, and a result into a single command-style sentence ("should apply a percentage discount"). There is no way to see what state the Voucher was in, what event was applied, and what became true as a result.
- There is no state buildup. Two tests could not share setup because there is no shared context above them.
- When the same behavior needs to be observed across many backends (Markdown, DrawIO, Miro, TypeScript), this shape forces duplication of the operation names in each backend's list. The state-oriented shape lets the shared story stay the same while only the observed artifacts differ per backend.

Rewritten correctly, this becomes the "with a 20 percent discount rule" branch in the correct scaffold above.
