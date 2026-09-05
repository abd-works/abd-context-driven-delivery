# Output — abd-bdd-specification

**Deliverables folder:** alongside the feature's `*-behavior.md` file, or in `test/` / `src/` following the project convention.

**File name:** `{domain-name}.test.ts` (Jest/TypeScript) or `{domain-name}_spec.py` (Mamba/Python).

**Resolution:**

1. User names the file explicitly → use that.
2. A `{stem}-behavior.md` exists → derive `{stem}.test.ts` or `{stem}_spec.py` in the same directory.
3. A test file already exists → add signatures to it; do not create a duplicate.
