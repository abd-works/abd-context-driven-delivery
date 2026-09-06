# Thin Slicing — Example Output Shape

## Example: retail inventory

```text
Increment 1: Manual inventory update — staff marks stock changes on paper; customer sees in-store signage.
  Stories: Update inventory by hand, Display paper signage, Record sale manually

Increment 2: Partial automation — barcode scanner updates inventory file; signage updates printed daily.
  Stories: Scan item to update inventory file, Generate print signage from file, Semi-automated sale logging

Increment 3: Full automation — purchase updates inventory and digital display in real time.
  Stories: Process sale in POS system, Decrement inventory automatically, Update digital signage live
```

Each increment shows an end-to-end slice: input → processing → persistence → visible outcome. The journey becomes more automated and robust with each increment.

## Weak patterns to avoid

- Phase numbers with no outcome: "Sprint 1", "Sprint 2"
- "All UI then all API" — horizontal layering
- Three auth methods as spine steps 2–4 when one suffices for the first increment
