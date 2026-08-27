# Primitives — Integrated Guide

Four decorators turn a plain Python class into a fully agentic toolset. This file shows how they fit together and where to find the per-primitive docs.

## The four decorators

| Decorator | Lives in | What it does |
|---|---|---|
| `@toolset` | `primitives/tools` | Mixes `Toolset` into the class; publishes the manifest the AI reads |
| `@agent_tool` | `primitives/tools` | Marks a method as directly callable by the AI |
| `@resource` | `primitives/tools` | Marks a `@property` as observable state the AI can read |
| `@instruction` | `primitives/instructions` | Marks a method as a content-resolution slot (file / folder / section) |
| `@agent_instructions` | `primitives/actions` | Marks a method as an AI-orchestrated recipe; body is parsed as instructions, not executed |

---

## Integrated example

`primitives/examples/reporter.py` — `Reporter` uses every decorator and all three instruction forms. Companion files `reporter.md` and `house-guidelines.md` sit beside it in the same folder.

---

## Per-primitive documentation

| Primitive | Module context |
|---|---|
| `@toolset` / `@agent_tool` / `@resource` | `primitives/tools/.context/module-context.md` |
| `@agent_instructions` | `primitives/actions/.context/module-context.md` |
| `@instruction` | `primitives/instructions/.context/module-context.md` |

---

## Dependency direction

```
actions  →  primitives/instructions  →  primitives/assets
tools    →  primitives/instructions
```

Never import `tools` or `actions` from inside `primitives`. Peers self-register through `ToolsetExtensions`.



## Rules 
- maximize use of templated variables to keep utility specific markdown as reusable and generic as possible 
