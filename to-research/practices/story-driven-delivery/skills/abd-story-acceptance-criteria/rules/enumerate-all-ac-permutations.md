---
scanner: enumerate-ac-permutations
---

# Rule: Enumerate all AC permutations

**Scanner:** `scanners/enumerate-ac-permutations-scanner.py` — **`EnumerateACPermutationsScanner`** (policy; mechanical pass is currently a no-op)

Enumerate **all** important acceptance criteria permutations: validation paths, calculation branches, happy path, errors, boundaries.

## DO

- Cover validation paths explicitly.
- Include happy path, error path, and edge cases.
- Cover calculation branches where applicable.

## DON'T

- Skip permutations (e.g. only happy path).
- Assume a single path when multiple outcomes exist.
