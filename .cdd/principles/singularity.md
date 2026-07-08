Keep capabilities extremely focused — one concept, one job. Build larger capabilities by extending focused ones, not by bloating a single capability.

A capability should do exactly one thing well. When a capability starts doing two things, split it.

**DO** — one concept per capability, composed via `extends:` frontmatter:

```
agentic-tdd/     ← builds and runs agent tests
rules/           ← validates and generates rule-compliant artifacts
capability/      ← deploys and manages capabilities
```

`agentic-tdd` extends `capability` and inherits Deploy and Clean at deploy time rather than reimplementing them.

**DON'T** — accumulate unrelated concerns in one capability:

```
tools/           ← tests, validation, deployment, scanning, and more
```

When a capability needs behaviour from another capability, set `extends:` on the target and list local actions in `overrides:`. Deploy wires the rest as `read @{parent} § {action}`. Extend `_BaseCli` in the API surface for deterministic actions. Let each capability own its domain; let the extend chain wire them together.
