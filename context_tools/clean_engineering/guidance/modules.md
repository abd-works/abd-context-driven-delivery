# Clean Engineering — Procedural Guidance (modules fidelity)

## How to identify modules

A module is a named structural boundary that groups closely related classes. Think of it as a folder with a clear purpose and a thin public surface:

1. **What concept does this module own?** It should be one domain concept or a coherent sub-system.
2. **What's its seam?** The public surface — the small set of types and operations that callers depend on. Everything else is hidden.
3. **What are its dependencies?** They must be one-way. If A depends on B, B must not depend on A. Cycles are a hard fail.

## Build order thinking

Dependencies define build order. Think of it like a compiler: what can be built first with no dependencies? That goes first. Then what depends only on the first thing? That goes second.

Write this as: `{first}` → `{second}` → `{third}`

If you can't find a linear build order, you have a cycle. Fix it by extracting a shared interface or restructuring the dependency.

## Nested module thinking

Nest modules only when they share real common mechanics:

- **Parent module** owns shared base types and the protocol children implement.
- **Child module** owns one independently implementable specialization.
- **Organizational folder** (no seam, no module-context.md) is NOT a module.

Children depend on the parent base, never on siblings. If children would duplicate mechanics, extract to the parent first.

## Module-context.md thinking

The context file is the **caller-facing contract** — only public seam information:
- Purpose, primary use case, rationale
- Seam (public type/class names)
- Dependencies (one-way module names)
- Optional: how to extend, mechanism notes

Never put internals here: no implementation details, no private helpers, no underscore-prefixed types, no test inventories, no scanner notes.

## Deep module ideal

The seam should be a short list of names with substantial functionality behind it. If internal helpers leak into the public surface, encapsulation becomes overhead without benefit. Heuristic: at most 40% of top-level symbols should be public (leading underscore for the rest).
