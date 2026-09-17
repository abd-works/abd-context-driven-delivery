# Primitives — Integrated Guide

Four decorators turn a plain Python class into a fully agentic toolset. This file shows how they fit together and where to find the per-primitive docs.

## The four decorators

| Decorator | Lives in | What it does |
|---|---|---|
| `@toolset` | `primitives/agent_tools` | Mixes `Toolset` into the class; publishes the manifest the AI reads |
| `@agent_tool` | `primitives/agent_tools` | Marks a method as directly callable by the AI |
| `@resource` | `primitives/agent_tools` | Marks a `@property` as observable state the AI can read |
| `@markdown` | `primitives/markdown` | Extracts co-located markdown (folder, file, or section) |
| `@agent_instructions` | `primitives/agent_tools` | Marks a method as an AI-orchestrated recipe; body is parsed as instructions, not executed |

---

## Integrated example

`primitives/examples/reporter.py` — `Reporter` uses the decorators with `@markdown` extract. Companion files `reporter.md` and `house-guidelines.md` sit beside it in the same folder.

---

## Per-primitive documentation

| Primitive | Module context |
|---|---|
| `@toolset` / `@agent_tool` / `@resource` | `primitives/agent_tools/.context/module-context.md` |
| `@agent_instructions` | `primitives/agent_tools/.context/module-context.md` |
| `@markdown` | `primitives/markdown/.context/module-context.md` |

---

## Dependency direction

```
actions  →  primitives/markdown
tools    →  primitives/markdown
```

Never import `tools` or `actions` from inside `primitives`.



## Rules 
- maximize use of templated variables to keep utility specific markdown as reusable and generic as possible 
