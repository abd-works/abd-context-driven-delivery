---
scanner: reaction-chaining
---

# Rule: Use AND for multiple reactions

**Scanner:** `scanners/reaction-chaining-scanner.py` — **`ReactionChainingScanner`**

Chain sequential **system** reactions with **AND** under the same trigger. Avoid separate **WHEN** for each micro-step when the trigger is the same. Limit **AND** chains to a reasonable length (scanner warns when excessive).

## DO

- Chain related system outcomes with AND.

## DON'T

- Use separate WHEN/THEN pairs for sequential system-only actions that belong to one reaction chain.
