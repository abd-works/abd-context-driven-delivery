# Thin slicing — Treasury Same-Day Transfers incremental backlog

## Product / context

**Product:** Corporate treasury same-day USD transfers

**Slicing intent:** deliver the basic happy-path transfer first, then rejection and cutoff outcomes, then fraud review adjudication

**Spine vs optional:** compose → submit → approve → route before cutoff → track settled is the spine. Cancellation, after-cutoff routing, dual-control, memos, and fraud outcomes are layered in later increments.

## Increments

### Increment 1: Submit and settle a same-day transfer on the happy path

**Outcome:** a Treasurer can compose a transfer below the dual-control threshold, obtain single approval, route it before the 15:00 ET cutoff, and see it pending then settled

**Decision prompt:** does the end-to-end same-day path complete within the cutoff window under realistic load?

**Stories in this increment** *(order reflects flow within the slice):*

- *Draft transfer details*
- *Validate destination account*
- *Review composed transfer*
- *Submit transfer for approval*
- *Approve single-control transfer*
- *Route transfer before cutoff*
- *View pending transfers*
- *View settled transfers*

### Increment 2: Handle rejection and cutoff outcomes

**Outcome:** a Treasurer can cancel a pending transfer, see a transfer roll to next-day after cutoff, and view rejected transfer outcomes; high-value transfers require dual approval

**Decision prompt:** do cancellation, cutoff roll-forward, and dual-control paths produce clear, actionable outcomes for Treasurers?

**Stories in this increment:**

- *Cancel pending transfer*
- *Route transfer after cutoff*
- *View rejected transfers*
- *Approve dual-control transfer*
- *Attach memo to transfer*

### Increment 3: Adjudicate fraud-flagged transfers

**Outcome:** a Fraud Analyst can release or block flagged transfers and Treasurers can see blocked transfer outcomes

**Decision prompt:** wire fraud review before enabling third-party destinations

**Stories in this increment:**

- *Release flagged transfer*
- *Block flagged transfer*
- *View blocked transfers*
