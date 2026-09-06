---
scanner: atomic-ac
---

# Rule: Atomic acceptance criteria

**Scanner:** `scanners/atomic-ac-scanner.py` — **`AtomicACScanner`**

Write atomic acceptance criteria. Avoid repeating common WHEN/THEN/AND blocks across multiple AC. State the general case once; additional AC should only state what differs.

## DO

- State general behavior once in the first acceptance criteria.
- Variations only state what differs from the general case.
- Edge cases state only the edge behavior.
- Use "see previous" only when unavoidable (should be rare).

## DON'T

- Repeat the same base logic across multiple acceptance criteria.
- Make variations repeat the full acceptance criteria text.
