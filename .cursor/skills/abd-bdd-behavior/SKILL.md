---
name: abd-bdd-behavior
description: >-
  Deprecated entry point. Use the bdd skill instead.
disable-model-invocation: true
---

# Deprecated — use `bdd`

BDD now lives in the multi-fidelity **bdd** generator (`behavior` → `development`).
Hierarchy rules and fidelities live in `bdd.md` § Contexts; the plain-English hierarchy is a prerequisite, not a fidelity.

From the repo root, set `$env:PYTHONPATH = "$PWD;$PWD\primitives;$PWD\utilities;$PWD\concepts"`, then:

```
python -m tools manifest contexts.bdd.bdd:Bdd
```

Invoke with `context.fidelity behavior` (python format by default — empty test skeletons).
