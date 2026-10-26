---
description: "Whenever you add or change call graphs on BDD observations, or change production code those graphs describe. Follow these rules."
paths:
  - "**/*spec.py"
  - "**/*_spec.py"
  - "**/*spec.ts"
  - "**/*Spec.java"
  - "**/*-sketch.md"
  - "**/*-realization.md"
---

#### Rules



Whenever you add or change call graphs on BDD observations, or change production code those graphs describe. Follow these rules.

If this change will not stay here, follow `practices/bdd/behavior.mdc`.

- **`strip-helpers-to-domain-calls`** — Same rule as story realizations: show the domain call the helper delegates to.
- **`full-call-graph-per-observation`** — Follow every named domain or external-system collaborator from the entry operation through returns; do not stop at the first hop.
- **`external-systems-at-their-boundary`** — Label `[ExternalSystem]` at the seam; do not recurse inside vendor code.
- **`no-typescript-internals`** — Omit framework and language-native steps unless the observation is entirely infrastructure.
- **`sketch-fidelity`** — Signatures and interaction arrows only; no assertions, mocks, or production imports in the realization artifact.
- **`hierarchy-preservation`** — One graph per `it should`; do not add or remove observations when deepening to realization.

**Pass:** an `it` whose body is only call-graph comments (or `BDD: SIGNATURE` plus `# ->` lines) naming real domain operations.

**Fail:** assertions, mocks, or invented collaborators not traced to source.

---