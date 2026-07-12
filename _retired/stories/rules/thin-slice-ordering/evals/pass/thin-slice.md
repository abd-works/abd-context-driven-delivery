# Thin slicing — `Cash Management` incremental backlog

## Product / context

**Product:** cash-management payment initiation and settlement

## Increments

### Increment 1: `Customer submits happy-path payment`

**Outcome:** a Treasurer can submit a same-day transfer and see a confirmation number

**Decision prompt:** does the payment gateway respond within 500 ms under realistic load?

**Stories in this increment:**

- `Submit same-day transfer`
- `Return confirmation number`
