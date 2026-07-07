# Thin slicing — `Treasury Same-Day Transfers` incremental backlog

## Product / context

**Product:** Corporate treasury same-day USD transfers

**Slicing intent:** deliver the smallest end-to-end transfer capability first, then layer approvals and fraud review

**Spine vs optional:** compose → submit → route → track is the spine. Dual-control and fraud outcomes are additive layers.

## Increments

### Increment 1: `Compose and route a single-control transfer`

**Outcome:** a Treasurer can compose a transfer under the dual-control threshold and see it route within the same-day window

**Decision prompt:** ship without dual-control if fewer than 20% of transfers exceed the threshold in production data

**Stories in this increment:**

- *`Draft transfer details`*
- *`Validate destination account`*
- *`Review composed transfer`*
- *`Submit transfer for approval`*
- *`Approve single-control transfer`*
- *`Route transfer before cutoff`*
- *`View pending transfers`*
- *`View settled transfers`*

### Increment 2: `Add dual-control and cancellation`

**Outcome:** high-value transfers require a second approver and Treasurers can cancel while pending

**Decision prompt:** enable dual-control before onboarding any customer whose ADV exceeds the threshold

**Stories in this increment:**

- *`Approve dual-control transfer`*
- *`Cancel pending transfer`*
- *`Attach memo to transfer`*
- *`Route transfer after cutoff`*
- *`View rejected transfers`*

### Increment 3: `Add fraud review outcomes`

**Outcome:** flagged transfers are held for Fraud Analyst adjudication and Treasurers see the outcome

**Decision prompt:** wire fraud review before enabling third-party destinations

**Stories in this increment:**

- *`Release flagged transfer`*
- *`Block flagged transfer`*
- *`View blocked transfers`*
- *`View rejected transfers`*
