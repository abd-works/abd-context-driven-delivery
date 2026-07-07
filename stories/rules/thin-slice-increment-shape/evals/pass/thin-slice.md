# Thin slicing — `Cash Management` incremental backlog

## Product / context

**Product:** cash-management payment initiation and settlement

**Slicing intent:** ship the shortest end-to-end path first, defer error and alternate channels

## Increments

### Increment 1: `Customer submits happy-path payment`

**Outcome:** a Treasurer can submit a same-day transfer and see a confirmation number

**Stories in this increment:**

- `Submit same-day transfer`
- `Return confirmation number`

### Increment 2: `Payment is rejected on breach`

**Outcome:** an over-limit transfer is rejected with a clear reason

**Stories in this increment:**

- `Reject over-limit transfer`
