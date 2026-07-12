# Thin slicing — `Cash Management` incremental backlog

## Product / context

**Product:** `Same-day and next-day domestic transfers for corporate treasurers`
**Slicing intent:** `Ship value in the smallest end-to-end vertical slice`

## Increments

### Increment 1: `Move money same-day for one treasurer`

**Outcome:** `A treasurer can submit and see settlement of a same-day transfer`
**Slicing notes:** `Manual approver step; single currency (USD only)`

### Increment 2: `Same-day transfers for the full team`

**Outcome:** `Multiple treasurers can operate independently`
**Slicing notes:** `Adds per-treasurer authorization`
**Stories in this increment:**
- *`Submit same-day transfer`*
- *`Approve pending transfer`*
- *`Cancel pending transfer`*
