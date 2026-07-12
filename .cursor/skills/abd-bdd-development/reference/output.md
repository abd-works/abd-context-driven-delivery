# Output — abd-bdd-development

- **Test file:** `{domain-name}.test.ts` (Jest/TypeScript) or `{domain-name}_spec.py` (Mamba/Python) — existing file with signatures replaced.
- **Helper file (when needed):** `{domain-name}-helper.ts` / `{domain-name}_helper.py` — shared factory functions and `beforeEach` setup when used by more than one test.
- **Production code:** `{domain-name}.ts` / `{domain-name}.py` — minimal module implementing the behavior under test.

**Resolution:** production code goes in the layer's conventional module location. Follow the project's established convention (e.g. `src/features/{name}/`).
