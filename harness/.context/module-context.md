# Primitives — Integrated Guide

Four decorators turn a plain Python class into a fully agentic toolset. This file shows how they fit together and where to find the per-primitive docs.

## The four decorators

| Decorator | Lives in | What it does |
|---|---|---|
| `@toolset` | `harness/agent_tools` | Mixes `Toolset` into the class; publishes the manifest the AI reads |
| `@agent_tool` | `harness/agent_tools` | Marks a method as directly callable by the AI |
| `@resource` | `harness/agent_tools` | Marks a `@property` as observable state the AI can read |
| `@markdown` | `harness/markdown` | Extracts co-located markdown (folder, file, or section) |
| `@agent_instructions` | `harness/agent_tools` | Marks a method as an AI-orchestrated recipe; body is parsed as instructions, not executed |

---

## Integrated example

`harness/examples/reporter.py` — `Reporter` uses the decorators with `@markdown` extract. Companion files `reporter.md` and `house-guidelines.md` sit beside it in the same folder.

---

## Per-primitive documentation

| Primitive | Module context |
|---|---|
| `@toolset` / `@agent_tool` / `@resource` | `harness/agent_tools/.context/module-context.md` |
| `@agent_instructions` | `harness/agent_tools/.context/module-context.md` |
| `@markdown` | `harness/markdown/.context/module-context.md` |

---

## Dependency direction

```
actions  →  harness/markdown
tools    →  harness/markdown
```

Never import `tools` or `actions` from inside `harness`.



## Rules 
- maximize use of templated variables to keep utility specific markdown as reusable and generic as possible 
