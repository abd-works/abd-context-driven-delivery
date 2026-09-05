---
name: ddd-tactics
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

# ddd-tactics

Use ddd guidance at `tactics` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@ddd-building_blocks
@ddd-bounded_context
@ddd-scaffold

# Contexts

## tactics

**Default format:** Python

**Goal:** Implement the domain and building-block seams (repos, events, factories, …) against a chosen architecture.

- Preserve names from the CE / building-blocks model.
- Implement repository persistence, event publication/handling, factories, services as decided upstream.
- **Architecture** — from project context (`.context/`, ADRs, stack). If none, **ask**. If none available, default: Node-shaped app + **JSON file persistence** (package TBD).
- Domain model free of UI/transport; persistence and messaging behind ports.
- **`load-with-identity-in-hand`** — When wrapping live, `load` takes the identity already in hand. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- Call clean_engineering at **code**.

---

## Templates

Call `load_template` directly with your active format and fidelity:

```python
from context_tools.ddd.ddd import Ddd
Ddd(fidelity="tactics").load_template(format="<your_format>", fidelity="tactics")
```

See examples in `context_tools/ddd/examples/` if needed.